"""Contrôle d'une période du « Siècle en images » (spec 12).

Usage :
    python3 scripts/diaporamas/verifier.py revolution
    python3 scripts/diaporamas/verifier.py --tous

Vérifie : nombre de diapositives (110 à 130 depuis la révision « Arts et techniques ») et d'actes (6 à 10), numérotation continue,
actes cohérents (débuts croissants, titre et dates du carton d'acte : « 1787-1789 »,
« juillet-octobre 1789 »), chaque image et chaque audio présents dans public/diaporamas/<slug>/,
licences libres (relevées par images.py depuis l'API Commons), métadonnées complètes
(titre, auteur, date, technique, conservation), une même œuvre deux fois au plus,
durées (14 à 24 s par diapositive en principe, ~18 s en moyenne), phrases horodatées
(`audio.phrases`), caméra (`image.camera` : 1 à 3 étapes, cadres valides et assez grands,
passages `quand` exacts et dans l'ordre ; plus de champ `cadrage`), contrôle de fidélité
passé pour le texte actuel (empreinte de voix.py), narrations de 2 à 3 phrases et ~40 à
55 mots, phrases de 25 mots au plus, sans parenthèses ni abréviations courantes.
Frise du temps : `date` (et `date_fin` facultatif) au format AAAA, AAAA-MM ou AAAA-MM-JJ, date
réelle, `date_fin` postérieure à `date`, dans la période de la frise (de la première année du
premier acte à la dernière année du dernier acte), date de la diapositive 1 obligatoire (une
diapositive sans date reprend celle de la précédente). Les retours en arrière sont listés en
avertissement (pour relecture) ; le nombre de surimpressions de la frise est affiché.
Musique (si le champ `musique` existe ; voir musique.py) : chaque fichier présent, licence relevée
par musique.py pour la source actuelle et admise (domaine public, CC0, CC BY, CC BY-SA ; jamais
NC ni ND), crédits complets (titre, compositeur ou auteur, date, interprète, licence, source),
1 à 3 pistes de fond par acte, 3 à 6 intermèdes chantés (et 1 ou 2 intermèdes musicaux,
`instrumental`, sans paroles) de 15 à 25 s, chacun après une
diapositive existante dont la narration annonce le chant (son titre y figure), paroles
horodatées dans l'ordre et dans la durée de l'extrait. Uniquement de vrais enregistrements
(source `commons` ou `archive`) : une piste issue d'un MIDI ou sans enregistrement réel est
refusée, de même qu'un fichier orphelin dans musique/. La durée totale compte les intermèdes.
Lectures et épisodes (spec 12, « Lectures d'époque et épisodes ») : champs complets, `apres`
désignant une diapositive sans autre segment (intermède, lecture, épisode), audio présent et à
jour (empreinte de voix.py, voix de lecture comprise), fidélité, phrases horodatées, durées
(lectures 20 à 40 s, épisodes 45 s à 1 min 30), nombres (4 à 6 lectures, 3 à 5 épisodes).
Lectures : chaque paragraphe vérifié MOT POUR MOT sur la page Wikisource (`source.page`),
téléchargée à neuf (comme `npm run verifier:ecrivains`) ; coupures « […] » seules sur leur ligne ;
portrait sous licence libre (relevé par images.py) ou image d'une diapositive. Épisodes : règles
de la narration (phrases de 25 mots au plus, ni parenthèses ni abréviations), passages `quand`
exacts, sources des chiffres, graphiques et cartes, fond de carte et sa licence, fac-similé sous
licence libre, cadres valides et citations du document (relevées sur le fac-similé).
`--hors-ligne` : textes des lectures comparés au cache de scripts/ecrivains (sans réseau).
Code de sortie 1 en cas d'erreur ; les avertissements n'en sont pas.
"""
import argparse, calendar, datetime, json, re, sys, unicodedata
from collections import Counter

import commun as c
from voix import VOIX, VOIX_LECTURE, empreinte

sys.path.insert(1, str(c.RACINE / 'scripts' / 'ecrivains'))
HORS_LIGNE = False


def _ecrivains():
    """scripts/ecrivains/verifier.py (homonyme de ce fichier : chargé par son chemin)."""
    import importlib.util
    if 'verifier_ecrivains' not in sys.modules:
        spec = importlib.util.spec_from_file_location('verifier_ecrivains', c.RACINE / 'scripts' / 'ecrivains' / 'verifier.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        sys.modules['verifier_ecrivains'] = m
    return sys.modules['verifier_ecrivains']

CAMERA_RATIO = 1.6
PAUSE = 0.6     # pause entre deux diapositives (s) ; mêmes valeurs que src/utils/diaporamas.ts
CARTON = 2.0    # carton de changement d'acte (s), compté dans la durée totale
CHAMPS = ('titre', 'auteur', 'date', 'technique', 'conservation')
SAUT_JOURS = 92  # frise : saut notable vers l'avant au-delà de 3 mois (même valeur que diaporamas.ts)
MOIS = ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre',
        'octobre', 'novembre', 'décembre')


def bornes_date(texte) -> tuple[datetime.date, datetime.date] | None:
    """Premier et dernier jour d'une date ISO partielle (AAAA, AAAA-MM, AAAA-MM-JJ), ou None."""
    if not isinstance(texte, str):
        return None
    m = re.fullmatch(r'(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?', texte)
    if not m:
        return None
    a, mo, j = int(m[1]), m[2] and int(m[2]), m[3] and int(m[3])
    try:
        if j:
            d = datetime.date(a, mo, j)
            return d, d
        if mo:
            return datetime.date(a, mo, 1), datetime.date(a, mo, calendar.monthrange(a, mo)[1])
        return datetime.date(a, 1, 1), datetime.date(a, 12, 31)
    except ValueError:
        return None


def libelle_date(texte: str) -> str:
    """« 1789 », « juillet 1789 », « 14 juillet 1789 » (1er pour le premier du mois)."""
    p = [int(v) for v in texte.split('-')]
    if len(p) == 1:
        return str(p[0])
    if len(p) == 2:
        return f'{MOIS[p[1] - 1]} {p[0]}'
    return f"{'1er' if p[2] == 1 else p[2]} {MOIS[p[1] - 1]} {p[0]}"


def controler_dates(d: dict) -> tuple[list[str], list[str], list[int]]:
    """Dates de la frise : erreurs, avertissements (retours en arrière) et numéros des
    diapositives où la frise s'affiche en surimpression (saut notable hors carton d'acte)."""
    erreurs, avert, surimpressions = [], [], []
    annees = [int(a) for acte in d['actes'] for a in re.findall(r'\b1[789]\d\d\b', acte.get('dates') or '')]
    premier = re.findall(r'\b1[789]\d\d\b', d['actes'][0].get('dates') or '') if d['actes'] else []
    dernier = re.findall(r'\b1[789]\d\d\b', d['actes'][-1].get('dates') or '') if d['actes'] else []
    if not (premier and dernier):
        return erreurs, avert, surimpressions  # dates des actes déjà signalées
    debut, fin = datetime.date(int(min(premier)), 1, 1), datetime.date(int(max(dernier)), 12, 31)
    debuts_actes = {a['debut'] for a in d['actes']}
    prec = None  # (n, premier jour, dernier jour, libellé) de la diapositive précédente
    for x in d['diapositives']:
        p = f"{x['n']:3d}"
        if 'date' not in x:
            if 'date_fin' in x:
                erreurs.append(f'{p} : « date_fin » sans « date »')
            if prec is None:
                erreurs.append(f'{p} : date manquante (la première diapositive doit être datée)')
            continue
        b = bornes_date(x['date'])
        if not b:
            erreurs.append(f"{p} : date invalide ({x['date']!r} ; AAAA, AAAA-MM ou AAAA-MM-JJ)")
            continue
        lib = libelle_date(x['date'])
        if 'date_fin' in x:
            bf = bornes_date(x['date_fin'])
            if not bf:
                erreurs.append(f"{p} : date_fin invalide ({x['date_fin']!r})")
                continue
            if bf[1] <= b[1]:
                erreurs.append(f"{p} : date_fin ({x['date_fin']}) pas postérieure à date ({x['date']})")
                continue
            b = (b[0], bf[1])
            lib += f" → {libelle_date(x['date_fin'])}"
        if b[0] < debut or b[1] > fin:
            erreurs.append(f'{p} : date {lib} hors de la période de la frise ({debut.year}-{fin.year})')
            continue
        if prec:
            if b[1] < prec[1]:
                avert.append(f'{p} : retour en arrière ({prec[3]}, diapositive {prec[0]} → {lib})')
            if x['n'] not in debuts_actes and (b[1] < prec[1] or (b[0] - prec[2]).days > SAUT_JOURS):
                surimpressions.append(x['n'])
        prec = (x['n'], b[0], b[1], lib)
    return erreurs, avert, surimpressions


def controler_camera(x: dict) -> list[str]:
    """Étapes `image.camera` : 1 à 3, cadres dans [0, 1] et assez grands, la première sans
    `quand`, les suivantes avec un passage exact de la narration, dans l'ordre."""
    etapes = x['image'].get('camera')
    if not etapes:
        return ['caméra absente (camera.py)']
    if not isinstance(etapes, list) or not 1 <= len(etapes) <= 3:
        return [f'caméra : {len(etapes)} étape(s) (1 à 3)']
    erreurs, apres = [], 0
    L, H = x['image'].get('largeur') or 1600, x['image'].get('hauteur') or 1200
    for k, e in enumerate(etapes, 1):
        r = e.get('cadre')
        if not (isinstance(r, list) and len(r) == 4 and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
            erreurs.append(f'caméra, étape {k} : cadre invalide ({r})')
            continue
        # Taille minimale (~30 % : voir camera.ajuster), avec une tolérance pour les corrections à la main.
        if max((r[2] - r[0]) * L, (r[3] - r[1]) * H * CAMERA_RATIO) < 0.25 * max(L, H):
            erreurs.append(f'caméra, étape {k} : cadre trop serré ({r}), image floue')
        q = e.get('quand')
        if k == 1:
            if q:
                erreurs.append('caméra : la première étape ne doit pas avoir de « quand »')
            continue
        pos = x['narration'].find(q, apres) if q else -1
        if pos < 0:
            erreurs.append(f'caméra, étape {k} : « {q} » absent de la narration (ou hors de l’ordre)')
        else:
            apres = pos + len(q)
    return erreurs


def _sans_accents(t: str) -> str:
    t = unicodedata.normalize('NFKD', t.lower().replace('’', "'"))
    return ' '.join(re.findall(r"[a-z0-9']+", ''.join(ch for ch in t if not unicodedata.combining(ch))))


def controler_musique(d: dict, dossier) -> tuple[list[str], list[str], float]:
    """Musique : erreurs, avertissements et durée ajoutée par les intermèdes (avec leurs pauses)."""
    from musique import REFUS, licence_admise
    m = d.get('musique')
    if not m:
        return [], ['pas de musique (champ « musique » absent)'], 0.0
    erreurs, avert = [], []
    etat_f = c.CACHE / d['slug'] / 'musique.json'
    etat = json.loads(etat_f.read_text()) if etat_f.exists() else {}
    actes = {a['id'] for a in d['actes']}
    narrations = {x['n']: x['narration'] for x in d['diapositives']}
    ids = set()
    for p, chant in [(p, False) for p in m.get('fond', [])] + [(p, True) for p in m.get('intermedes', [])]:
        pid = p.get('id', '?')
        q = f'musique {pid}'
        if pid in ids:
            erreurs.append(f'{q} : identifiant en double')
        ids.add(pid)
        champs = ('titre', 'auteur' if chant else 'compositeur', 'date', 'interprete', 'licence', 'fichier')
        manquants = [k for k in champs if not str(p.get(k) or '').strip()]
        if chant and not str(p.get('enregistrement') or '').strip():
            manquants.append('enregistrement')
        if manquants:
            erreurs.append(f"{q} : crédits incomplets ({', '.join(manquants)})")
        src = p.get('source') or {}
        if src.get('type') == 'midi' or src.get('commons') or str(src.get('fichier') or src.get('url') or '').lower().endswith(('.mid', '.midi', '.mxl', '.musicxml')):
            erreurs.append(f'{q} : rendu MIDI refusé, il faut un vrai enregistrement libre ({src})')
        elif src.get('type') not in ('commons', 'archive'):
            erreurs.append(f'{q} : source invalide, ni Commons ni Internet Archive ({src})')
        if re.search(r'\b(midi|rendu)\b', _sans_accents(p.get('interprete') or '')):
            erreurs.append(f"{q} : interprète « {p.get('interprete')} » : rendu MIDI refusé")
        if (etat.get(pid) or {}).get('moteur'):
            erreurs.append(f'{q} : fichier produit par un rendu MIDI (relancer musique.py --force)')
        if REFUS.search(p.get('licence') or ''):
            erreurs.append(f"{q} : licence NC ou ND refusée ({p.get('licence')})")
        e = etat.get(pid)
        if not e or e.get('source') != src:
            erreurs.append(f'{q} : licence non relevée pour cette source (relancer musique.py)')
        elif not e.get('libre') or not licence_admise(e.get('licence_relevee') or ''):
            erreurs.append(f"{q} : licence refusée ({e.get('licence_relevee')})")
        if not (dossier / (p.get('fichier') or '')).is_file():
            erreurs.append(f"{q} : fichier absent ({p.get('fichier')})")
        duree = p.get('duree') or 0
        if duree <= 0:
            erreurs.append(f'{q} : durée absente (relancer musique.py)')
        if not chant:
            if p.get('acte') not in actes:
                erreurs.append(f"{q} : acte inconnu ({p.get('acte')})")
            v = p.get('volume', 1)
            if not (isinstance(v, (int, float)) and 0 < v <= 2):
                erreurs.append(f'{q} : volume relatif invalide ({v})')
            continue
        if not 15 <= duree <= 26:
            avert.append(f'{q} : intermède de {duree:.1f} s (visé : 15 à 25 s)')
        n = p.get('apres')
        if n not in narrations:
            erreurs.append(f'{q} : « apres » ne désigne pas une diapositive ({n})')
        else:
            titre = re.sub(r"^(le|la|les|l')\s*", '', _sans_accents(p.get('titre') or ''))
            if titre and titre not in _sans_accents(narrations[n]):
                avert.append(f'{q} : la narration de la diapositive {n} n’annonce pas « {p.get("titre")} »')
        par = p.get('paroles') or []
        if p.get('instrumental'):
            # Intermède musical (œuvre instrumentale, spec 12, « Arts et techniques ») : pas de
            # paroles, le lecteur masque le sous-titre.
            if par:
                erreurs.append(f'{q} : intermède instrumental avec des paroles')
        elif not par:
            erreurs.append(f'{q} : paroles absentes')
        elif any(not (isinstance(x, list) and len(x) == 2 and isinstance(x[0], (int, float)) and str(x[1]).strip()) for x in par) \
                or [x[0] for x in par] != sorted(x[0] for x in par) or par[0][0] < 0 or par[-1][0] >= duree:
            erreurs.append(f'{q} : paroles mal horodatées ({par})')
    for a in d['actes']:
        k = sum(1 for p in m.get('fond', []) if p.get('acte') == a['id'])
        if not 1 <= k <= 3:
            erreurs.append(f"musique : acte « {a['titre']} » : {k} piste(s) de fond (1 à 3)")
    inter = m.get('intermedes', [])
    chantes = [p for p in inter if not p.get('instrumental')]
    if not 3 <= len(chantes) <= 6:
        avert.append(f'musique : {len(chantes)} intermède(s) chanté(s) (3 à 6 visés)')
    if len(inter) - len(chantes) > 2:
        avert.append(f'musique : {len(inter) - len(chantes)} intermèdes musicaux (1 ou 2 au plus)')
    if len({p.get('apres') for p in inter}) != len(inter):
        erreurs.append('musique : deux intermèdes après la même diapositive')
    if 'moteur' in m:
        erreurs.append('musique : champ « moteur » (rendu MIDI) à retirer')
    attendus = {p.get('fichier') for p in m.get('fond', []) + inter}
    if (dossier / 'musique').is_dir():
        for f in sorted((dossier / 'musique').iterdir()):
            if f.is_file() and f'musique/{f.name}' not in attendus:
                erreurs.append(f'musique : fichier orphelin {f.name} (à supprimer)')
    return erreurs, avert, sum((p.get('duree') or 0) + PAUSE for p in inter)


def _texte_wikisource(page: str) -> tuple[str, str]:
    """Texte normalisé d'une page Wikisource : (statut, texte). Téléchargée à neuf, à l'URL
    publique, comme scripts/ecrivains/verifier.py ; `--hors-ligne` : cache de wikisource.py."""
    import wikisource as ws
    norm, page_publique = _ecrivains().norm, _ecrivains().page
    if HORS_LIGNE:
        return 'cache', norm(' '.join(ws.paragraphes(page)) + ' ' + ' '.join(ws.paragraphes(page, vers=True)))
    code, p1, p2 = page_publique(ws.url_page(page))
    return (str(code), f'{p1}\n{p2}') if code == 200 else (str(code), '')


def _instants_ok(texte: str, quands: list[str]) -> list[str]:
    return [q for q in quands if q and q not in texte]


def controler_segments(d: dict, dossier, voix_etat: dict, img_etat: dict, lexique: dict) -> tuple[list[str], list[str], float]:
    """Lectures d'époque et épisodes : erreurs, avertissements, durée ajoutée (pauses comprises)."""
    erreurs, avert = [], []
    narrations = {x['n']: x for x in d['diapositives']}
    occupes = Counter([i.get('apres') for i in (d.get('musique') or {}).get('intermedes', [])]
                      + [l.get('apres') for l in d.get('lectures', [])] + [e.get('apres') for e in d.get('episodes', [])])
    duree = 0.0

    def audio(q: str, obj: dict, texte: str, voix: str, bornes: tuple[float, float]):
        nonlocal duree
        a = obj.get('audio') or {}
        if not a.get('fichier') or not (dossier / a['fichier']).is_file():
            erreurs.append(f'{q} : audio absent (voix.py)')
            return
        v = voix_etat.get(obj['_cle'], {})
        if v.get('empreinte') != empreinte(c.appliquer_lexique(texte, lexique), voix):
            erreurs.append(f'{q} : audio périmé (texte ou voix changés : relancer voix.py)')
        elif v.get('fidelite', 0) < 0.9:
            erreurs.append(f"{q} : fidélité insuffisante ({v.get('fidelite')})")
        du = a.get('duree') or 0
        duree += du + PAUSE
        ph = a.get('phrases')
        if not ph or len(ph) != len(c.phrases(texte)):
            erreurs.append(f'{q} : phrases non horodatées ou incohérentes (voix.py --horodater)')
        if q.startswith('lecture'):
            controler_mots(q, a, texte, du)
        if not bornes[0] <= du <= bornes[1]:
            avert.append(f'{q} : durée {du:.1f} s (visé : {bornes[0]:.0f} à {bornes[1]:.0f} s)')

    def controler_mots(q: str, a: dict, texte: str, du: float):
        """Minutage mot par mot (voix.py --mots) : un couple [début, fin] par mot lu, dans
        l'ordre, dans la durée de l'audio. Absent : le lecteur se replie au prorata (avertissement)."""
        mots = a.get('mots')
        attendus = len(c.mots_lus(texte))
        if mots is None:
            avert.append(f'{q} : mots non minutés, repli au prorata des caractères (voix.py --mots)')
            return
        if len(mots) != attendus:
            erreurs.append(f'{q} : {len(mots)} mots minutés pour {attendus} mots lus (texte changé ? voix.py --mots)')
            return
        avant = 0.0
        for k, m in enumerate(mots):
            if not (isinstance(m, list) and len(m) == 2 and all(isinstance(v, (int, float)) for v in m)):
                erreurs.append(f'{q} : mot {k + 1} mal minuté ({m})')
                return
            d, f = m
            if not (0 <= d <= f <= du + 0.05):
                erreurs.append(f'{q} : mot {k + 1} hors de l\'audio ou à l\'envers ({m}, durée {du:.2f} s)')
                return
            if d < avant - 0.01:
                erreurs.append(f'{q} : mot {k + 1} avant le précédent ({d:.2f} s < {avant:.2f} s)')
                return
            avant = d

    def apres(q: str, n):
        if n not in narrations:
            erreurs.append(f'{q} : « apres » ne désigne pas une diapositive ({n})')
        elif occupes[n] > 1:
            erreurs.append(f'{q} : un autre segment suit déjà la diapositive {n}')

    lectures = d.get('lectures', [])
    if lectures and not 4 <= len(lectures) <= 6:
        avert.append(f'{len(lectures)} lecture(s) (4 à 6 visées)')
    pages: dict[str, tuple[str, str]] = {}
    for l in lectures:
        q = f"lecture {l.get('id')}"
        l['_cle'] = f"lecture:{l.get('id')}"
        manquants = [k for k in ('id', 'apres', 'nature', 'oeuvre', 'annee', 'texte') if not l.get(k)]
        au = l.get('auteur') or {}
        manquants += [f'auteur.{k}' for k in ('nom', 'dates', 'voix') if not au.get(k)]
        if not (l.get('source') or {}).get('page'):
            manquants.append('source.page')
        if manquants:
            erreurs.append(f"{q} : champs manquants ({', '.join(manquants)})")
            continue
        apres(q, l['apres'])
        if au['voix'] not in ('homme', 'femme'):
            erreurs.append(f"{q} : voix « {au['voix']} » inconnue (homme ou femme)")
            continue
        if l.get('date') and not bornes_date(l['date']):
            erreurs.append(f"{q} : date invalide ({l['date']!r})")
        blocs = l['texte']
        if blocs[0].strip() == '[…]' or blocs[-1].strip() == '[…]' or any('[…]' in b and b.strip() != '[…]' for b in blocs):
            erreurs.append(f'{q} : coupure « […] » mal placée (seule sur sa ligne, ni au début ni à la fin)')
        page = l['source']['page']
        if page not in pages:
            try:
                pages[page] = _texte_wikisource(page)
            except Exception as e:  # noqa: BLE001
                pages[page] = ('erreur', str(e))
        statut, source = pages[page]
        if statut not in ('200', 'cache'):
            erreurs.append(f'{q} : page Wikisource injoignable ({statut}) : {page}')
        else:
            norm = _ecrivains().norm
            for b in blocs:
                if b.strip() == '[…]':
                    continue
                for morceau in b.split('\n'):
                    if norm(morceau).strip() not in source:
                        erreurs.append(f'{q} : introuvable mot pour mot sur Wikisource : « {morceau[:80]}… »')
        po = l.get('portrait') or {}
        if po.get('diapositive'):
            if po['diapositive'] not in narrations:
                erreurs.append(f"{q} : portrait : diapositive {po['diapositive']} inexistante")
        elif po.get('commons'):
            e = img_etat.get(l['_cle'])
            if not e or e.get('commons') != po['commons'] or not e.get('libre'):
                erreurs.append(f'{q} : portrait : licence non relevée ou refusée (images.py)')
            elif not (dossier / (po.get('fichier') or '')).is_file():
                erreurs.append(f'{q} : portrait absent ({po.get("fichier")})')
        else:
            avert.append(f'{q} : pas de portrait (initiale affichée)')
        r = po.get('cadre')
        if r is not None and not (len(r) == 4 and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
            erreurs.append(f'{q} : cadre du portrait invalide ({r})')
        audio(q, l, c.texte_lu(l), VOIX_LECTURE, (20, 40))

    episodes = d.get('episodes', [])
    if episodes and not 3 <= len(episodes) <= 5:
        avert.append(f'{len(episodes)} épisode(s) (3 à 5 visés)')
    fonds_dir = c.DONNEES / 'fonds'
    for e in episodes:
        q = f"épisode {e.get('id')}"
        e['_cle'] = f"episode:{e.get('id')}"
        manquants = [k for k in ('id', 'apres', 'titre', 'narration', 'visuels', 'sources') if not e.get(k)]
        if manquants:
            erreurs.append(f"{q} : champs manquants ({', '.join(manquants)})")
            continue
        apres(q, e['apres'])
        if e.get('date') and not bornes_date(e['date']):
            erreurs.append(f"{q} : date invalide ({e['date']!r})")
        t = e['narration']
        for ph in c.phrases(t):
            if c.nb_mots(ph) > 25:
                erreurs.append(f'{q} : phrase de {c.nb_mots(ph)} mots (25 au plus) : « {ph[:60]}… »')
        if re.search(r'[()\[\]]', t):
            erreurs.append(f'{q} : parenthèses dans la narration')
        if re.search(r'\b(etc|av|apr|J\.-C|M|Mme|St|Ste|cf|env)\.', t):
            erreurs.append(f'{q} : abréviation dans la narration')
        quands = []
        for k, v in enumerate(e['visuels']):
            tv = v.get('type')
            qv = f'{q}, visuel {k + 1} ({tv})'
            if k == 0 and v.get('quand'):
                erreurs.append(f'{qv} : le premier visuel ne prend pas de « quand »')
            if k > 0 and not v.get('quand'):
                erreurs.append(f'{qv} : « quand » manquant')
            quands.append(v.get('quand'))
            if tv == 'carton':
                if not v.get('texte'):
                    erreurs.append(f'{qv} : texte manquant')
            elif tv in ('chiffres', 'barres', 'courbe'):
                if not str(v.get('source') or '').strip():
                    erreurs.append(f'{qv} : source des chiffres manquante')
                items = v.get('items') or v.get('barres') or v.get('reperes') or []
                quands += [x.get('quand') for x in items]
                if tv == 'barres' and any(not (0 <= x.get('valeur', -1) <= v.get('max', 0)) for x in v.get('barres', [])):
                    erreurs.append(f'{qv} : valeur hors de l’échelle (0 à max)')
                if tv == 'courbe':
                    pts = v.get('points') or []
                    if any(not bornes_date(x[0]) for x in pts) or [x[0] for x in pts] != sorted(x[0] for x in pts):
                        erreurs.append(f'{qv} : points mal datés ou désordonnés')
                    if any(not 0 <= x[1] <= v.get('ymax', 0) for x in pts):
                        erreurs.append(f'{qv} : point hors de l’échelle')
                    dates = {x[0] for x in pts}
                    if any(r.get('date') not in dates for r in v.get('reperes', [])):
                        erreurs.append(f'{qv} : repère sans point correspondant')
            elif tv == 'carte':
                f = fonds_dir / f"{v.get('fond')}.json"
                if not f.is_file():
                    erreurs.append(f"{qv} : fond de carte absent ({v.get('fond')} : carte.py)")
                elif not json.loads(f.read_text()).get('licence'):
                    erreurs.append(f'{qv} : licence du fond de carte non notée')
                if not str(v.get('source') or '').strip():
                    erreurs.append(f'{qv} : source de la carte manquante')
                quands += [x.get('quand') for x in v.get('elements', [])]
            elif tv == 'document':
                im = v.get('image') or {}
                cle = f"{e['_cle']}:{k}"
                ei = img_etat.get(cle)
                if not ei or ei.get('commons') != im.get('commons') or not ei.get('libre'):
                    erreurs.append(f'{qv} : fac-similé : licence non relevée ou refusée (images.py)')
                if not (dossier / (im.get('fichier') or '')).is_file():
                    erreurs.append(f"{qv} : fac-similé absent ({im.get('fichier')})")
                for x in v.get('lignes', []):
                    r = x.get('cadre') or []
                    if not (len(r) == 4 and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
                        erreurs.append(f'{qv} : cadre de ligne invalide ({r})')
                    if not x.get('texte') or not x.get('quand'):
                        erreurs.append(f'{qv} : ligne sans texte ou sans « quand »')
                    quands.append(x.get('quand'))
                if not str(v.get('source') or '').strip():
                    erreurs.append(f'{qv} : source du document manquante')
            else:
                erreurs.append(f'{qv} : type inconnu')
        for qa in _instants_ok(t, quands):
            erreurs.append(f'{q} : « {qa} » absent de la narration')
        audio(q, e, t, VOIX, (45, 90))
    for x in lectures + episodes:
        x.pop('_cle', None)
    return erreurs, avert, duree


def verifier(slug: str) -> bool:
    f, d = c.lire(slug)
    dossier = c.PUBLIC / d['slug']
    etat_img = c.CACHE / d['slug'] / 'images.json'
    etat_voix = c.CACHE / d['slug'] / 'voix.json'
    img = json.loads(etat_img.read_text()) if etat_img.exists() else {}
    voix = json.loads(etat_voix.read_text()) if etat_voix.exists() else {}
    lexique = c.charger_lexique()
    erreurs, avert = [], []
    diapos = d['diapositives']

    if not 110 <= len(diapos) <= 130:
        erreurs.append(f'{len(diapos)} diapositives (attendu : 110 à 130)')
    if not 6 <= len(d['actes']) <= 10:
        erreurs.append(f"{len(d['actes'])} actes (attendu : 6 à 10)")
    if [x['n'] for x in diapos] != list(range(1, len(diapos) + 1)):
        erreurs.append('numérotation des diapositives non continue (1, 2, 3…)')
    debuts = [a['debut'] for a in d['actes']]
    if debuts != sorted(debuts) or (debuts and debuts[0] != 1) or len(set(debuts)) != len(debuts):
        erreurs.append(f'débuts des actes incohérents : {debuts}')
    for a in d['actes']:
        nom_acte = a.get('titre') or a.get('id') or '?'
        if not (a.get('titre') or '').strip():
            erreurs.append(f"acte {a.get('id')} : titre manquant")
        dates = a.get('dates')
        if not isinstance(dates, str) or not dates.strip():
            erreurs.append(f'acte « {nom_acte} » : dates manquantes (champ « dates », ex. « 1787-1789 »)')
        elif not re.search(r'\b1[789]\d\d\b', dates):
            erreurs.append(f'acte « {nom_acte} » : dates sans année ({dates})')
        elif re.search(r'\s[-–]\s|\s[-–]|[-–]\s|\s{2}|^\s|\s$', dates):
            erreurs.append(f'acte « {nom_acte} » : dates mal composées ({dates!r} ; écrire « 1787-1789 »)')
    for k in ('slug', 'numero', 'titre', 'periode', 'resume'):
        if not d.get(k) and d.get(k) != 0:
            erreurs.append(f'champ « {k} » manquant')

    oeuvres = Counter(x['image']['commons'] for x in diapos)
    for oeuvre, n in oeuvres.items():
        if n > 2:
            erreurs.append(f'{oeuvre} utilisée {n} fois (2 au plus)')

    durees = []
    for x in diapos:
        n, i = x['n'], x['image']
        p = f'{n:3d}'
        if not (dossier / i.get('fichier', '')).is_file():
            erreurs.append(f"{p} : image absente ({i.get('fichier')})")
        e = img.get(str(n))
        if not e or e.get('commons') != i['commons']:
            erreurs.append(f'{p} : licence non relevée pour ce fichier (relancer images.py)')
        elif not e.get('libre'):
            erreurs.append(f"{p} : licence refusée ({e.get('licence')})")
        elif (e.get('largeur') or 0) < 1000:
            avert.append(f"{p} : original étroit ({e.get('largeur')} px)")
        if i.get('licence') != 'Domaine public':
            erreurs.append(f'{p} : licence affichée absente')
        manquants = [k for k in CHAMPS if not (i.get(k) or '').strip()]
        if manquants:
            erreurs.append(f"{p} : métadonnées manquantes ({', '.join(manquants)})")
        r = i.get('recadrage')
        if r is not None and not (isinstance(r, list) and len(r) == 4 and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
            erreurs.append(f'{p} : recadrage invalide ({r})')
        if 'cadrage' in i:
            erreurs.append(f'{p} : champ « cadrage » supprimé (remplacé par « camera »)')
        erreurs += [f'{p} : {e}' for e in controler_camera(x)]

        a = x.get('audio') or {}
        if not a.get('fichier') or not (dossier / a['fichier']).is_file():
            erreurs.append(f'{p} : audio absent')
        else:
            v = voix.get(str(n), {})
            if v.get('empreinte') != empreinte(c.appliquer_lexique(x['narration'], lexique)):
                erreurs.append(f'{p} : audio périmé (la narration a changé : relancer voix.py)')
            elif v.get('fidelite', 0) < 0.9:
                erreurs.append(f"{p} : fidélité insuffisante ({v.get('fidelite')})")
            duree = a.get('duree') or 0
            durees.append(duree)
            ph = a.get('phrases')
            if not ph:
                erreurs.append(f'{p} : phrases non horodatées (voix.py --horodater)')
            elif (len(ph) != len(c.phrases(x['narration']))
                  or any(not (0 <= d0 <= f0 <= duree + 0.05) for d0, f0 in ph)
                  or any(ph[k][1] > ph[k + 1][0] + 0.01 for k in range(len(ph) - 1))):
                erreurs.append(f'{p} : horodatage des phrases incohérent ({ph})')
            if not 14 <= duree <= 24:
                avert.append(f'{p} : durée {duree:.1f} s (visé : 14 à 24 s)')

        t = x['narration']
        for ph in c.phrases(t):
            if c.nb_mots(ph) > 25:
                erreurs.append(f'{p} : phrase de {c.nb_mots(ph)} mots (25 au plus) : « {ph[:60]}… »')
        if not 2 <= len(c.phrases(t)) <= 3:
            avert.append(f'{p} : {len(c.phrases(t))} phrases (2 à 3 visées)')
        if not 40 <= c.nb_mots(t) <= 55:
            avert.append(f'{p} : {c.nb_mots(t)} mots (40 à 55 visés)')
        if re.search(r'[()\[\]]', t):
            erreurs.append(f'{p} : parenthèses dans la narration')
        if re.search(r'\b(etc|av|apr|J\.-C|M|Mme|St|Ste|cf|env)\.', t):
            erreurs.append(f'{p} : abréviation dans la narration')

    e_dates, a_dates, surimp = controler_dates(d)
    erreurs += e_dates
    avert += a_dates
    e_mus, a_mus, duree_chants = controler_musique(d, dossier)
    erreurs += e_mus
    avert += a_mus
    e_seg, a_seg, duree_segments = controler_segments(d, dossier, voix, img, lexique)
    erreurs += e_seg
    avert += a_seg

    total = sum(durees) + PAUSE * len(diapos) + CARTON * len(d['actes']) + duree_chants + duree_segments
    print(f"{d['titre']} ({d['periode']}) : {len(diapos)} diapositives, {len(d['actes'])} actes, "
          f"{len(oeuvres)} œuvres différentes.")
    if durees:
        print(f'Durée totale (pauses, cartons d’acte et intermèdes compris) : {total / 60:.1f} min ; moyenne {sum(durees) / len(durees):.1f} s par diapositive '
              f'(de {min(durees):.1f} à {max(durees):.1f} s ; visé : ~18 s).')
    m = d.get('musique') or {}
    if m:
        poids = sum(f.stat().st_size for f in (dossier / 'musique').glob('*.m4a')) if (dossier / 'musique').is_dir() else 0
        n_instr = sum(1 for p in m.get('intermedes', []) if p.get('instrumental'))
        print(f"Musique : {len(m.get('fond', []))} pistes de fond, {len(m.get('intermedes', [])) - n_instr} intermède(s) chanté(s), "
              f"{n_instr} intermède(s) musical(aux) "
              f"({duree_chants:.0f} s, pauses comprises), {poids / 1e6:.1f} Mo.")
    if d.get('lectures') or d.get('episodes'):
        print(f"Lectures et épisodes : {len(d.get('lectures', []))} lecture(s), {len(d.get('episodes', []))} épisode(s) "
              f"({duree_segments / 60:.1f} min, pauses comprises).")
    datees = sum(1 for x in diapos if 'date' in x)
    print(f'Frise : {datees} diapositives datées sur {len(diapos)} ; {len(surimp)} surimpression(s) '
          f"hors cartons d'acte{' (diapositives ' + ', '.join(map(str, surimp)) + ')' if surimp else ''}.")
    for a in avert:
        print(f'  avertissement {a}')
    for e in erreurs:
        print(f'  ERREUR {e}')
    print('OK' if not erreurs else f'{len(erreurs)} erreur(s).')
    return not erreurs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug', nargs='?')
    p.add_argument('--tous', action='store_true')
    p.add_argument('--hors-ligne', action='store_true', help='lectures comparées au cache Wikisource')
    a = p.parse_args()
    global HORS_LIGNE
    HORS_LIGNE = a.hors_ligne
    if a.tous:
        slugs = [f.stem for f in sorted(c.DONNEES.glob('*.json'))]
    elif a.slug:
        slugs = [a.slug]
    else:
        p.error('indiquer une période ou --tous')
    ok = True
    for s in slugs:
        ok = verifier(s) and ok
        print()
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
