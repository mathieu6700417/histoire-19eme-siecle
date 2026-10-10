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

- **Solde des crédits prépayés** (spec 13, outil 2) : l'API ne le donne pas, on le tient soi-même.
  Chaque appel est ajouté à `.cache/diaporamas/gemini-depenses.jsonl` (`ts`, script, tâche, modèle,
  jetons, dollars estimés ; écriture en ajout, sous verrou). L'utilisateur déclare son crédit après
  une recharge (`gemini.py --crediter 10` : le solde lu sur la console Google à cet instant), écrit
  dans `.cache/diaporamas/gemini-credit.json` ; solde estimé = crédit − dépenses depuis.
- **Sonde** : un appel minimal (un jeton de sortie) qui dit si les crédits répondent. Elle part
  toute seule au premier appel d'un lancement (une fois, pas par appel) ; crédits épuisés, ou
  `--budget` supérieur au solde estimé : CreditsEpuises, une BudgetAtteint, donc le même arrêt
  propre. `--sans-sonde` saute la sonde et ce contrôle. Un 402 en cours de route lève la même erreur.
- **Essai sans dépense** : `DIAPORAMAS_GEMINI_SIMULER=402` fait répondre « 402, crédits épuisés »
  à tout appel (sonde comprise), sans réseau.

Usage :
    python3 scripts/diaporamas/gemini.py --solde         # solde estimé, dépense de 7 jours par script, sonde
    python3 scripts/diaporamas/gemini.py --crediter 10   # après une recharge : 10 $ disponibles maintenant

`--solde` rend 0 (crédits disponibles), 2 (crédits épuisés) ou 1 (sonde sans réponse : clé, réseau).

TARIFS est **indicatif** (hypothèse, $ par million de jetons, réflexion comptée en sortie) : le
vérifier sur la page de tarifs de Google avant de s'y fier ; un modèle absent prend le tarif
DEFAUT_TARIF.
"""
import datetime, io, json, os, re, sys, threading, time, urllib.error, urllib.request
from pathlib import Path

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

CACHE = Path(__file__).resolve().parents[2] / '.cache' / 'diaporamas'
DEPENSES = CACHE / 'gemini-depenses.jsonl'   # un appel par ligne
CREDIT = CACHE / 'gemini-credit.json'        # { "credit": 10.0, "depuis": "<ts>" }
MODELE_SONDE = os.environ.get('DIAPORAMAS_MODELE_SONDE') or 'gemini-3.8-flash'
RECHARGER = 'recharger le compte Gemini, puis : python3 scripts/diaporamas/gemini.py --crediter <dollars>'

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
sans_sonde = False                      # --sans-sonde : ni sonde ni comparaison du budget au solde
_verrou_sonde = threading.Lock()
_sonde_faite = False                    # la sonde part une fois par lancement
_epuise: str | None = None              # message, une fois les crédits constatés épuisés


class ErreurGemini(Exception):
    pass


class BudgetAtteint(ErreurGemini):
    pass


class CreditsEpuises(BudgetAtteint):
    """Crédits prépayés épuisés (sonde, 402 en cours de route) ou --budget au-dessus du solde estimé."""


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
    p.add_argument('--sans-sonde', action='store_true',
                   help='ne pas sonder les crédits Gemini ni comparer --budget au solde estimé avant le premier appel')


def appliquer(a, taches: list[str]) -> None:
    global plafond, sans_sonde
    if getattr(a, 'budget', None) is not None:
        plafond = a.budget
    sans_sonde = bool(getattr(a, 'sans_sonde', False))
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
    if _epuise:
        raise CreditsEpuises(_epuise)
    if plafond is not None and depense['dollars'] >= plafond:
        raise BudgetAtteint(f"plafond de {plafond:.2f} $ atteint (~{depense['dollars']:.3f} $ dépensés) : arrêt")


def _maintenant() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def _noter(nom: str, tache: str | None, e: int, s: int, r: int, dol: float) -> None:
    """Ajoute l'appel au registre des dépenses (une ligne, sous verrou : appels et scripts parallèles)."""
    import fcntl
    ligne = {'ts': _maintenant(), 'script': Path(sys.argv[0]).stem or '?', 'tache': tache or '?', 'modele': nom,
             'entree': e, 'sortie': s, 'reflexion': r, 'dollars': round(dol, 6)}
    try:
        DEPENSES.parent.mkdir(parents=True, exist_ok=True)
        with DEPENSES.open('a', encoding='utf-8') as h:
            fcntl.flock(h, fcntl.LOCK_EX)
            h.write(json.dumps(ligne, ensure_ascii=False) + '\n')
    except OSError:
        pass    # le registre est une aide : ne jamais faire échouer un appel payé


def depenses(depuis: str | None = None) -> list[dict]:
    """Lignes du registre des dépenses, à partir de l'instant `depuis` (ISO, UTC)."""
    if not DEPENSES.exists():
        return []
    lignes = []
    for l in DEPENSES.read_text(encoding='utf-8').splitlines():
        try:
            x = json.loads(l)
        except json.JSONDecodeError:
            continue
        if not depuis or x.get('ts', '') >= depuis:
            lignes.append(x)
    return lignes


def credit() -> dict | None:
    try:
        x = json.loads(CREDIT.read_text())
        return x if isinstance(x.get('credit'), (int, float)) else None
    except (OSError, json.JSONDecodeError, AttributeError):
        return None


def solde() -> float | None:
    """Solde estimé ($) : crédit déclaré − dépenses estimées depuis ; None sans crédit déclaré."""
    cr = credit()
    if not cr:
        return None
    return cr['credit'] - sum(x.get('dollars') or 0 for x in depenses(cr.get('depuis')))


def crediter(dollars: float) -> None:
    CREDIT.parent.mkdir(parents=True, exist_ok=True)
    tmp = CREDIT.with_suffix('.tmp')
    tmp.write_text(json.dumps({'credit': dollars, 'depuis': _maintenant()}, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(CREDIT)


def _epuises(code: int, msg: str, large: bool = False) -> bool:
    """La réponse dit-elle « crédits épuisés » ? 402 toujours ; RESOURCE_EXHAUSTED s'il parle de crédits
    (un 429 de simple débit se retente) ; `large` (sonde) : tout RESOURCE_EXHAUSTED."""
    if code == 402:
        return True
    return 'RESOURCE_EXHAUSTED' in msg and (large or bool(re.search(r'prepay|credit|billing', msg, re.I)))


def _poster(nom: str, corps: dict, cle: str, delai: int) -> dict:
    """Un appel generateContent. DIAPORAMAS_GEMINI_SIMULER=402 : réponse 402 simulée, sans réseau."""
    url = f'{URL}/{nom}:generateContent'
    if os.environ.get('DIAPORAMAS_GEMINI_SIMULER') == '402':
        raise urllib.error.HTTPError(url, 402, 'Payment Required', None, io.BytesIO(
            b'{"error": {"code": 402, "status": "RESOURCE_EXHAUSTED", "message": "simulation : prepayment credits depleted"}}'))
    req = urllib.request.Request(url, data=json.dumps(corps).encode(),
                                 headers={'x-goog-api-key': cle, 'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=delai).read())


def sonder() -> tuple[str, str]:
    """Sonde des crédits : un appel minimal au modèle flash. Rend ('ok' | 'epuise' | 'inconnu', détail).
    Son coût (quelques jetons) va au registre des dépenses, pas au plafond du lancement."""
    simule = os.environ.get('DIAPORAMAS_GEMINI_SIMULER') == '402'
    cle = os.environ.get('GEMINI_API_KEY', '')
    if not cle and not simule:
        return 'inconnu', 'GEMINI_API_KEY absente de .env'
    corps = {'contents': [{'parts': [{'text': 'ok'}]}],
             'generationConfig': {'maxOutputTokens': 1, 'thinkingConfig': {'thinkingBudget': 0}}}
    try:
        d = _poster(MODELE_SONDE, corps, cle, 30)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors='replace')[:300]
        if _epuises(e.code, msg, large=True):
            return 'epuise', f'{e.code} : {" ".join(msg.split())[:160]}'
        return 'inconnu', f'Gemini {e.code} : {" ".join(msg.split())[:160]}'
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return 'inconnu', f'Gemini injoignable : {e}'
    u = d.get('usageMetadata') or {}
    e_, r_ = int(u.get('promptTokenCount') or 0), int(u.get('thoughtsTokenCount') or 0)
    s_ = int(u.get('candidatesTokenCount') or 0) + r_
    pe, ps = tarif(MODELE_SONDE)
    _noter(MODELE_SONDE, 'sonde', e_, s_, r_, e_ / 1e6 * pe + s_ / 1e6 * ps)
    return 'ok', f'{e_ + s_} jetons'


def avant_premier_appel() -> None:
    """Une fois par lancement, avant le premier appel payant : sonde des crédits et --budget comparé
    au solde estimé. Lève CreditsEpuises (et tout appel suivant aussi) ; rien avec --sans-sonde."""
    global _sonde_faite, _epuise
    with _verrou_sonde:
        if _sonde_faite or sans_sonde:
            return
        _sonde_faite = True
        s = solde()
        if s is not None and plafond is not None and plafond > s:
            _epuise = (f'--budget {plafond:.2f} $ dépasse le solde estimé (~{max(s, 0):.2f} $, tarifs indicatifs) : '
                       f'baisser --budget ou {RECHARGER} (ou --sans-sonde)')
        else:
            etat, detail = sonder()
            if etat == 'epuise':
                _epuise = f'crédits Gemini épuisés (sonde : {detail}) : {RECHARGER}'
            elif etat == 'inconnu':
                print(f'Sonde Gemini sans réponse ({detail}) : on continue.', file=sys.stderr)
    if _epuise:
        raise CreditsEpuises(_epuise)


def compter(nom: str, u: dict, tache: str | None = None) -> dict:
    """Ajoute l'usage d'une réponse à la dépense du lancement et au registre des dépenses ;
    rend {'entree', 'sortie', 'reflexion', 'dollars'}."""
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
    _noter(nom, tache, e, s, r, dol)
    return {'entree': e, 'sortie': s, 'reflexion': r, 'dollars': dol}


def generer(tache: str, corps: dict, nom: str | None = None, delai: int = 180,
            erreur: type = ErreurGemini) -> dict:
    """Réponse brute de generateContent pour `tache` (modèle, réflexion, plafond appliqués).

    `erreur` : classe d'exception levée (chaque script garde la sienne). `nom` : modèle explicite.
    La réponse porte en plus `_usage` (jetons et coût estimé de cet appel)."""
    global _epuise
    verifier_budget()
    cle = os.environ.get('GEMINI_API_KEY', '')
    if not cle and os.environ.get('DIAPORAMAS_GEMINI_SIMULER') != '402':
        raise erreur('GEMINI_API_KEY absente de .env')
    avant_premier_appel()
    nom = nom or modele(tache)
    corps = dict(corps)
    g = dict(corps.get('generationConfig') or {})
    if 'tts' not in nom and 'responseModalities' not in g and 'thinkingConfig' not in g:
        g['thinkingConfig'] = {'thinkingBudget': reflexion(tache)}
    corps['generationConfig'] = g
    for essai in range(6):
        try:
            d = _poster(nom, corps, cle, delai)
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:300]
            if _epuises(e.code, msg):
                _epuise = f'crédits Gemini épuisés en cours de route ({e.code}) : {RECHARGER}'
                raise CreditsEpuises(_epuise) from None
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
    d['_usage'] = compter(nom, d.get('usageMetadata') or {}, tache)
    return d


def json_de(d: dict, erreur: type = ErreurGemini):
    try:
        return json.loads(''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts']))
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise erreur(f'réponse illisible : {str(d)[:300]}') from e


def afficher_solde() -> int:
    """`--solde` : solde estimé, dépense des 7 derniers jours par script, sonde. Code 2 : crédits épuisés."""
    cr, s = credit(), solde()
    if cr:
        dep = cr['credit'] - s
        print(f"Crédit déclaré : {cr['credit']:.2f} $ le {str(cr.get('depuis', '?'))[:10]} ; dépensé depuis : ~{dep:.3f} $ ; "
              f'solde estimé : ~{s:.2f} $ (estimation, tarifs indicatifs).')
    else:
        print('Pas de crédit déclaré (après une recharge : gemini.py --crediter <dollars>) : dépenses et sonde seulement.')
    il_y_a_7j = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).isoformat(timespec='seconds')
    lignes = depenses(il_y_a_7j)
    print(f"Dépense des 7 derniers jours : ~{sum(x.get('dollars') or 0 for x in lignes):.3f} $ en {len(lignes)} appel(s)"
          f"{' (registre vide : tenu depuis la spec 13)' if not lignes else ''}.")
    par: dict[str, list[float]] = {}
    for x in lignes:
        par.setdefault(x.get('script', '?'), []).append(x.get('dollars') or 0)
    for script, v in sorted(par.items(), key=lambda kv: -sum(kv[1])):
        print(f'  {script} : ~{sum(v):.3f} $ ({len(v)} appel(s))')
    etat, detail = sonder()
    if etat == 'epuise':
        print(f'Sonde ({MODELE_SONDE}) : crédits épuisés ({detail}) ; {RECHARGER}')
        return 2
    if etat == 'inconnu':
        print(f'Sonde ({MODELE_SONDE}) : pas de réponse ({detail}).')
        return 1
    print(f'Sonde ({MODELE_SONDE}) : crédits disponibles ({detail}).')
    return 0


def main() -> int:
    import argparse
    import commun
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--solde', action='store_true', help='solde estimé, dépense de 7 jours par script et sonde')
    p.add_argument('--crediter', type=float, metavar='DOLLARS',
                   help='déclare le crédit disponible maintenant (après une recharge)')
    a = p.parse_args()
    commun.charger_env()
    if a.crediter is not None:
        crediter(a.crediter)
        print(f'Crédit déclaré : {a.crediter:.2f} $ à compter de maintenant ({CREDIT.relative_to(CACHE.parents[1])}).')
        return 0 if not a.solde else afficher_solde()
    if a.solde:
        return afficher_solde()
    p.error('--solde ou --crediter DOLLARS')


if __name__ == '__main__':
    sys.exit(main())
