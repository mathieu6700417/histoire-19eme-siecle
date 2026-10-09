"""Appel Gemini commun aux scripts de la chaîne (camera, utile, portraits, voix, paroles, banc_gemini).

Rassemble ce qui coûtait cher faute d'être réglé (journal du 2026-10-09 : ~6,3 $ pour une passe
caméra, la réflexion faisant ~85 % du coût) :

- **Modèle par tâche** : `modele('camera')` lit DIAPORAMAS_MODELE_CAMERA, puis l'ancienne variable
  de la tâche (DIAPORAMAS_MODELE_VISION, DIAPORAMAS_MODELE_TRANSCRIPTION…), puis le défaut ;
  l'option `--modele` des scripts passe avant tout.
- **Réflexion réglée** : `thinkingConfig.thinkingBudget` ajouté à tout appel de texte ou de vision
  (pas à la synthèse vocale) ; défaut REFLEXION_DEFAUT (bas), réglable par DIAPORAMAS_REFLEXION,
  DIAPORAMAS_REFLEXION_<TACHE> ou `--reflexion` (0 = sans réflexion, -1 = dynamique, laissée au modèle).
- **Plafond de dépense par lancement** : `--budget 0.50` ($). Le coût est estimé sur les jetons
  réellement renvoyés (`usageMetadata`) avec la table TARIFS ; une fois le plafond atteint, tout
  nouvel appel lève BudgetAtteint : les scripts s'arrêtent proprement et écrivent ce qui est fait.
  Les appels déjà partis (parallèles) se terminent : le dépassement est d'au plus quelques appels.

TARIFS est **indicatif** (hypothèse, $ par million de jetons, réflexion comptée en sortie) : le
vérifier sur la page de tarifs de Google avant de s'y fier ; un modèle absent prend le tarif
DEFAUT_TARIF.
"""
import json, os, threading, time, urllib.error, urllib.request

URL = 'https://generativelanguage.googleapis.com/v1beta/models'

# Tarifs INDICATIFS ($ / million de jetons : entrée, sortie y compris réflexion). Hypothèses à
# vérifier ; seules les proportions servent (estimation du plafond, comparaison du banc d'essai).
TARIFS = {
    'gemini-3.8-flash': (0.30, 2.50),
    'gemini-3.5-flash-lite': (0.10, 0.40),
    'gemini-3.1-flash-lite': (0.10, 0.40),
    'gemini-3.5-transcribe': (0.30, 1.00),
    'gemini-3.8-flash-tts': (0.50, 18.00),   # ~25 jetons audio par seconde : ~0,027 $ la minute
}
DEFAUT_TARIF = (0.30, 2.50)

REFLEXION_DEFAUT = 0        # sans réflexion : meilleur rapport qualité/prix au banc du 2026-10-09 (camera, utile, transcription ; gemini-3.8-flash)

# Modèle par défaut de chaque tâche, et ancienne variable d'environnement encore lue.
TACHES = {
    'camera': ('gemini-3.8-flash', 'DIAPORAMAS_MODELE_VISION'),
    'visages': ('gemini-3.8-flash', 'DIAPORAMAS_MODELE_VISION'),
    'utile': ('gemini-3.8-flash', 'DIAPORAMAS_MODELE_VISION'),
    'portraits': ('gemini-3.8-flash', 'DIAPORAMAS_MODELE_VISION'),
    'transcription': ('gemini-3.8-flash', 'DIAPORAMAS_MODELE_TRANSCRIPTION'),
    'paroles': ('gemini-3.8-flash', 'DIAPORAMAS_MODELE_TRANSCRIPTION'),
    'voix': ('gemini-3.8-flash-tts', 'DIAPORAMAS_MODELE_VOIX'),
}

_verrou = threading.Lock()
_choix: dict[str, str] = {}             # tâche -> modèle imposé par --modele
_reflexion: dict[str, int] = {}         # tâche -> budget imposé par --reflexion
plafond: float | None = None            # $ ; None = sans plafond
depense = {'appels': 0, 'entree': 0, 'sortie': 0, 'reflexion': 0, 'dollars': 0.0}


class ErreurGemini(Exception):
    pass


class BudgetAtteint(ErreurGemini):
    pass


def modele(tache: str) -> str:
    if tache in _choix:
        return _choix[tache]
    defaut, ancienne = TACHES.get(tache, ('gemini-3.8-flash', None))
    return (os.environ.get(f'DIAPORAMAS_MODELE_{tache.upper()}')
            or (os.environ.get(ancienne) if ancienne else None) or defaut)


def reflexion(tache: str) -> int:
    if tache in _reflexion:
        return _reflexion[tache]
    v = os.environ.get(f'DIAPORAMAS_REFLEXION_{tache.upper()}') or os.environ.get('DIAPORAMAS_REFLEXION')
    return int(v) if v not in (None, '') else REFLEXION_DEFAUT


def tarif(nom: str) -> tuple[float, float]:
    return TARIFS.get(nom, DEFAUT_TARIF)


def options(p, taches: list[str]) -> None:
    """Ajoute --budget, --reflexion et --modele à un argparse."""
    p.add_argument('--budget', type=float, metavar='DOLLARS',
                   help='plafond de dépense Gemini de ce lancement (estimé sur les jetons renvoyés, '
                        'tarifs indicatifs de gemini.py) : arrêt propre une fois atteint')
    p.add_argument('--reflexion', type=int, metavar='JETONS',
                   help=f'budget de réflexion par appel (défaut {REFLEXION_DEFAUT} ou DIAPORAMAS_REFLEXION ; '
                        '0 = aucune, -1 = dynamique)')
    p.add_argument('--modele', metavar='NOM',
                   help=f"modèle Gemini pour {', '.join(taches)} (sinon DIAPORAMAS_MODELE_<TACHE>)")


def appliquer(a, taches: list[str]) -> None:
    global plafond
    if getattr(a, 'budget', None) is not None:
        plafond = a.budget
    for t in taches:
        if getattr(a, 'reflexion', None) is not None:
            _reflexion[t] = a.reflexion
        if getattr(a, 'modele', None):
            _choix[t] = a.modele


def bilan() -> str:
    d = depense
    p = f' ; plafond {plafond:.2f} $' if plafond is not None else ''
    return (f"Gemini : {d['appels']} appel(s), {d['entree']} jetons en entrée, {d['sortie']} en sortie "
            f"(dont {d['reflexion']} de réflexion) ; ~{d['dollars']:.3f} $ (tarifs indicatifs){p}.")


def verifier_budget() -> None:
    if plafond is not None and depense['dollars'] >= plafond:
        raise BudgetAtteint(f"plafond de {plafond:.2f} $ atteint (~{depense['dollars']:.3f} $ dépensés) : arrêt")


def compter(nom: str, u: dict) -> dict:
    """Ajoute l'usage d'une réponse à la dépense ; rend {'entree', 'sortie', 'reflexion', 'dollars'}."""
    e = int(u.get('promptTokenCount') or 0)
    r = int(u.get('thoughtsTokenCount') or 0)
    s = int(u.get('candidatesTokenCount') or 0) + r
    pe, ps = tarif(nom)
    dol = e / 1e6 * pe + s / 1e6 * ps
    with _verrou:
        depense['appels'] += 1
        depense['entree'] += e
        depense['sortie'] += s
        depense['reflexion'] += r
        depense['dollars'] += dol
    return {'entree': e, 'sortie': s, 'reflexion': r, 'dollars': dol}


def generer(tache: str, corps: dict, nom: str | None = None, delai: int = 180,
            erreur: type = ErreurGemini) -> dict:
    """Réponse brute de generateContent pour `tache` (modèle, réflexion, plafond appliqués).

    `erreur` : classe d'exception levée (chaque script garde la sienne). `nom` : modèle explicite.
    La réponse porte en plus `_usage` (jetons et coût estimé de cet appel)."""
    verifier_budget()
    cle = os.environ.get('GEMINI_API_KEY', '')
    if not cle:
        raise erreur('GEMINI_API_KEY absente de .env')
    nom = nom or modele(tache)
    corps = dict(corps)
    g = dict(corps.get('generationConfig') or {})
    if 'tts' not in nom and 'responseModalities' not in g and 'thinkingConfig' not in g:
        g['thinkingConfig'] = {'thinkingBudget': reflexion(tache)}
    corps['generationConfig'] = g
    for essai in range(6):
        req = urllib.request.Request(f'{URL}/{nom}:generateContent', data=json.dumps(corps).encode(),
                                     headers={'x-goog-api-key': cle, 'Content-Type': 'application/json'})
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=delai).read())
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:300]
            if e.code in (429, 500, 502, 503, 504) and essai < 5:
                time.sleep(8 * (essai + 1))
                continue
            raise erreur(f'Gemini {e.code} : {msg}') from None
        except (urllib.error.URLError, TimeoutError) as e:
            if essai < 5:
                time.sleep(8 * (essai + 1))
                continue
            raise erreur(f'Gemini injoignable : {e}') from None
    else:
        raise erreur('Gemini : trop de tentatives')
    d['_usage'] = compter(nom, d.get('usageMetadata') or {})
    return d


def json_de(d: dict, erreur: type = ErreurGemini):
    try:
        return json.loads(''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts']))
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise erreur(f'réponse illisible : {str(d)[:300]}') from e
