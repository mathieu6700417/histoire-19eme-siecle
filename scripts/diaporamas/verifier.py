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
(`audio.phrases`), caméra (`image.camera` : 1 à 4 étapes, cadres valides et assez grands,
passages `quand` exacts et dans l'ordre ; plus de champ `cadrage` ; `image.ouverture`, détail
zoomé découvert à la sortie du carton d'acte : cadre valide, seulement sur la première diapositive
d'un acte, avertissement s'il est trop serré ou à peine plus serré que le premier cadre), zone utile
(`image.utile`, spec 12 « Sans bordures » : présente, valide, 25 % de l'image au moins ; cadres de la
caméra, ouverture et cadre d'intermède dans la zone, ou la recouvrant à 50 % au moins), titre court du cartouche
(`image.titre_court`, 60 caractères au plus) et cartouche rédigé de chaque piste de musique
(`cartouche` : oeuvre, compositeur), contrôle de fidélité
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
horodatées dans l'ordre et dans la durée de l'extrait ; calées au mot (`calage: "mot"`, paroles.py),
chaque mot de chaque vers horodaté, dans l'ordre, dans l'extrait. Uniquement de vrais enregistrements
(source `commons` ou `archive`) : une piste issue d'un MIDI ou sans enregistrement réel est
refusée, de même qu'un fichier orphelin dans musique/. La durée totale compte les intermèdes.
Avertissement quand un acte dure plus que ses pistes de fond enchaînées (elles boucleraient).
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
Cartes de lieu et citations en surimpression (spec 12, 2026-10-07) : un médaillon au plus par
diapositive, avec 1 à 5 lieux (révision du 2026-10-08 : passages dans l'ordre de la narration,
instants croissants, fond cohérent, points dans le cadre calculé et assez écartés) ; `lieux` : nom, `quand` (passage exact), lon/lat dans le cadre du fond (`france`,
`voisins`, `europe`, `monde` : fonds de carte.py ; `paris` : sur le plan d'époque de la période,
plans/<nom>.json) ; `citations` : `texte` sous-chaîne exacte de la narration, entre « », 25 mots
au plus, auteur ; instants (`instant`, `mots`) présents, dans l'audio et à jour (empreinte de
surimpressions.py), sinon avertissement (le lecteur se replie au prorata).
Portraits des personnes nommées (spec 12, 2026-10-08) : registre `portraits.json` (nom, dates,
fichier présent, page Commons, auteur, date de l'œuvre, licence domaine public ou CC0, cadre du
visage ; sans portrait : une note) ; dans chaque diapositive, `personnes` et `personnes_vues` :
personne au registre, `quand` exacts et dans l'ordre, instants présents, croissants, dans l'audio
et à jour, 4 portraits au plus, personne montrée absente de l'image (jamais aussi dans
`personnes_vues` ; désaccord avec le contrôle de vision en cache : avertissement), personne
citée (`citations[].personne`) accompagnée de son portrait.
Objets de musée et manuscrits (spec 12, « Enrichissements visuels », 2026-10-08) : registre
`objets.json` (type, nom, date, musée, fichier présent, page Commons, licence domaine public, CC0,
CC BY ou CC BY-SA, auteur de la photo pour une licence CC BY ; manuscrit : halo valide et passage
transcrit) ; dans chaque diapositive, un objet et un manuscrit au plus, au registre et du bon type,
`quand` exact, côté valide, instant présent, dans l'audio et à jour ; objet omis ou raccourci par
l'arbitrage : avertissement. Deux surimpressions au plus à la fois (citation, manuscrit, médaillon
de lieu, portraits, objet ; fenêtres recalculées comme dans le lecteur), jamais l'objet avec la
surimpression de son coin ni le manuscrit avec la citation.
Chiffres clés et dates républicaines (spec 12, « Enrichissements visuels », point 4, 2026-10-08) : un
chiffre et une date au plus par diapositive ; chiffre : `quand` exact, nombre dit dans le `quand` égal à
`valeur` (chiffres ou toutes lettres), prudence dite (« plus de », « près de »…) reprise dans `prefixe`,
unité courte, source notée ; date : `quand` exact, `republicain` valide, `gregorien` recalculé (tables
officielles : 1er vendémiaire de chaque an, années sextiles III, VII, XI ; calcul contrôlé sur une table
de concordance et des dates connues), date confirmée par la narration ou par la date de la diapositive
(sinon avertissement) ; instants présents, à jour, dans l'audio ; fenêtres recalculées comme dans le
lecteur (`chiffresDe`) et comptées dans la règle des deux surimpressions ; jamais le chiffre ni la date
avec la citation ; chiffre ou date omis ou raccourcis : avertissement.
Code de sortie 1 en cas d'erreur ; les avertissements n'en sont pas.
"""
import argparse, calendar, datetime, json, math, re, sys, unicodedata
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
CARTON = 12.0   # carton de changement d'acte (s), compté dans la durée totale
APRES_CITATION = 2.0  # la citation en surimpression reste ~2 s après son dernier mot


def pause_apres(x: dict) -> float:
    """Pause après la voix : PAUSE, allongée quand la narration finit par une citation en
    surimpression (max(PAUSE, fin du dernier mot + 2 s − durée de la voix)) ; même calcul que
    `pauseApres` dans src/utils/diaporamas.ts (ici d'après `mots` ; sans eux, au prorata)."""
    ci = (x.get('citations') or [None])[0]
    du = (x.get('audio') or {}).get('duree') or 6
    if not ci or ci.get('texte', '') not in x['narration']:
        return PAUSE
    if ci.get('mots') and len(ci['mots']) == len(c.mots_lus(ci['texte'])):
        fin = ci['mots'][-1][1]
    else:  # prorata des caractères sur la phrase horodatée (comme le lecteur)
        t, pos = x['narration'], x['narration'].index(ci['texte']) + len(ci['texte'])
        ph = (x.get('audio') or {}).get('phrases') or []
        debuts = [0]
        for q in c.phrases(t)[:-1]:
            debuts.append(t.index(q, debuts[-1]) + len(q))
        if len(ph) != len(debuts):
            fin = pos / max(1, len(t)) * du
        else:
            j = max(k for k, v in enumerate(debuts) if v <= pos)
            f_car = debuts[j + 1] if j + 1 < len(debuts) else len(t)
            fin = ph[j][0] + (pos - debuts[j]) / max(1, f_car - debuts[j]) * (ph[j][1] - ph[j][0])
    return max(PAUSE, round(fin + APRES_CITATION - du, 2))


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
    """Étapes `image.camera` : 1 à 4, cadres dans [0, 1] et assez grands, la première sans
    `quand`, les suivantes avec un passage exact de la narration, dans l'ordre."""
    etapes = x['image'].get('camera')
    if not etapes:
        return ['caméra absente (camera.py)']
    if not isinstance(etapes, list) or not 1 <= len(etapes) <= 4:
        return [f'caméra : {len(etapes)} étape(s) (1 à 4)']
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


def controler_ouverture(x: dict, debut_acte: bool) -> tuple[list[str], list[str]]:
    """`image.ouverture` (spec 12, « Sortie du carton d'acte en deux volets ») : cadre
    [x0, y0, x1, y1] dans [0, 1], seulement sur la première diapositive d'un acte. Avertissement
    s'il est trop serré (image floue : moins de ~400 px de l'original) ou s'il ne zoome pas au moins
    ×1,6 par rapport au premier cadre de la caméra."""
    i = x['image']
    if 'ouverture' not in i:
        return [], []
    r = i['ouverture']
    if not (isinstance(r, list) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r)
            and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
        return [f'ouverture : cadre invalide ({r}) : [x0, y0, x1, y1] entre 0 et 1, x0 < x1 et y0 < y1'], []
    if not debut_acte:
        return ['ouverture : seulement sur la première diapositive d\'un acte'], []
    L, H = i.get('largeur') or 1600, i.get('hauteur') or 1200
    avert = []
    taille = lambda c: max((c[2] - c[0]) * L, (c[3] - c[1]) * H * CAMERA_RATIO)
    if taille(r) < 400:
        avert.append(f'ouverture : cadre très serré ({r}, {taille(r):.0f} px), image floue')
    cam = i.get('camera') or []
    c0 = cam[0].get('cadre') if cam else [0, 0, 1, 1]
    if isinstance(c0, list) and len(c0) == 4 and taille(c0) < 1.6 * taille(r):
        avert.append(f'ouverture : zoom faible (×{taille(c0) / taille(r):.1f} par rapport au premier cadre ; ×2 visé)')
    return [], avert


UTILE_AIRE_MIN = 0.25     # zone utile plus petite : erreur (moins de 50 % : avertissement, sauf saisie à la main)
UTILE_RECOUVRE = 0.5      # part d'un cadre (caméra, ouverture, intermède) dans la zone utile : en deçà, erreur
UTILE_RECOUVRE_AVERT = 0.75


def controler_utile(x: dict, cadre_inter: list | None = None) -> tuple[list[str], list[str]]:
    """`image.utile` (spec 12, « Sans bordures ») : présente, valide, pas absurde ; les cadres de
    la caméra, l'ouverture et le cadre d'un intermède contenus dans la zone, ou au moins la
    recouvrant largement (le lecteur les y ramène)."""
    i = x['image']
    u = i.get('utile')
    if u is None:
        return ['zone utile absente (utile.py)'], []
    if not (isinstance(u, list) and len(u) == 4 and all(isinstance(v, (int, float)) for v in u)
            and 0 <= u[0] < u[2] <= 1 and 0 <= u[1] < u[3] <= 1):
        return [f'zone utile invalide ({u}) : [x0, y0, x1, y1] entre 0 et 1, x0 < x1 et y0 < y1'], []
    erreurs, avert = [], []
    aire = (u[2] - u[0]) * (u[3] - u[1])
    if aire < UTILE_AIRE_MIN:
        erreurs.append(f'zone utile absurde ({u} : {aire * 100:.0f} % de l\'image)')
    elif aire < 0.5 and not i.get('utile_manuel'):
        avert.append(f'zone utile petite ({u} : {aire * 100:.0f} % de l\'image) : à relire, puis « utile_manuel »')
    cadres = [(f'caméra, étape {k}', e.get('cadre')) for k, e in enumerate(i.get('camera') or [], 1)]
    if i.get('ouverture'):
        cadres.append(('ouverture', i['ouverture']))
    if cadre_inter:
        cadres.append(('cadre de l\'intermède', cadre_inter))
    for nom, r in cadres:
        if not (isinstance(r, list) and len(r) == 4) or list(r) == [0, 0, 1, 1]:
            continue  # déjà signalé par les contrôles de la caméra ; ou vue d'ensemble (toute la zone)
        a = max(1e-9, (r[2] - r[0]) * (r[3] - r[1]))
        dedans = max(0, min(r[2], u[2]) - max(r[0], u[0])) * max(0, min(r[3], u[3]) - max(r[1], u[1])) / a
        if dedans < UTILE_RECOUVRE:
            erreurs.append(f'{nom} : cadre {r} à {dedans * 100:.0f} % dans la zone utile {u}')
        elif dedans < UTILE_RECOUVRE_AVERT:
            avert.append(f'{nom} : cadre {r} à {dedans * 100:.0f} % dans la zone utile (ramené dedans par le lecteur)')
    return erreurs, avert


FONDS_LIEU = ('paris', 'france', 'voisins', 'europe', 'monde')


def plan_paris(slug: str) -> dict | None:
    """Plan de Paris d'époque de la période (src/data/diaporamas/plans/*.json, carte.py)."""
    for f in sorted((c.DONNEES / 'plans').glob('*.json')):
        p = json.loads(f.read_text())
        if slug in p.get('slugs', []):
            return p
    return None


_FRANCE = None


def en_france(lon: float, lat: float) -> bool:
    """Le point est-il en France métropolitaine (contour Natural Earth du cache de carte.py) ?"""
    global _FRANCE
    if _FRANCE is None:
        f = c.CACHE / 'natural-earth' / 'ne_50m_admin_0_countries.geojson'
        _FRANCE = []
        if f.exists():
            for ft in json.loads(f.read_text())['features']:
                if ft['properties'].get('ADM0_A3') == 'FRA':
                    g = ft['geometry']
                    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
                    _FRANCE = [p[0] for p in polys if -6 <= p[0][0][0] <= 10 and 41 <= p[0][0][1] <= 52]
    dedans = False
    for anneau in _FRANCE:
        for (x0, y0), (x1, y1) in zip(anneau, anneau[1:] + anneau[:1]):
            if (y0 > lat) != (y1 > lat) and lon < x0 + (lat - y0) * (x1 - x0) / (y1 - y0):
                dedans = not dedans
    return dedans


MAX_LIEUX = 5            # lieux d'un médaillon (MAX_LIEUX de src/utils/diaporamas.ts)
ORDRE_FONDS = FONDS_LIEU  # du plus étroit au plus large
RATIO_MULTI, EMPRISE_POINTS, LARGEUR_MIN_FOND = 4 / 3, 0.6, 0.45  # mêmes valeurs que diaporamas.ts
VUE_PARIS_M = 2000
ECART_MIN = 0.045        # fraction de la largeur du cadre : deux points plus proches se touchent


def cadre_multiple(lieux: list[dict], plan: dict | None) -> tuple[str, list[tuple[str, float, float]], list[str]] | None:
    """Médaillon à plusieurs lieux, calculé comme `medaillonMultiple` (diaporamas.ts) : fond retenu,
    points (nom, x, y en fractions du cadre) et remarques (fond élargi, lieux de Paris fondus)."""
    notes = []
    if all(li.get('fond') == 'paris' for li in lieux):
        if not plan:
            return None
        u, v = plan['calage']['u'], plan['calage']['v']
        px = [((u[0] * li['lon'] + u[1] * li['lat'] + u[2]) * plan['largeur'],
               (v[0] * li['lon'] + v[1] * li['lat'] + v[2]) * plan['hauteur']) for li in lieux]
        L, H, w_min, noms, fond = plan['largeur'], plan['hauteur'], VUE_PARIS_M / plan['calage']['metres_par_pixel'], [li['nom'] for li in lieux], 'paris'
    else:
        k = max(1, *[ORDRE_FONDS.index(li['fond']) for li in lieux if li.get('fond') in ORDRE_FONDS])
        demande = ORDRE_FONDS[k]

        def charge(nom):
            f = c.DONNEES / 'fonds' / f'{nom}.json'
            return json.loads(f.read_text()) if f.is_file() else None

        def dedans(f):
            x0, y0, x1, y1 = f['projection']['cadre']
            mx, my = (x1 - x0) * 0.03, (y1 - y0) * 0.03
            return all(x0 + mx <= li['lon'] <= x1 - mx and y0 + my <= li['lat'] <= y1 - my for li in lieux)
        f = charge(ORDRE_FONDS[k])
        while k < len(ORDRE_FONDS) - 1 and (not f or not dedans(f)):
            k += 1
            f = charge(ORDRE_FONDS[k])
        if not f:
            return None
        fond = ORDRE_FONDS[k]
        if fond != demande:
            notes.append(f'fond élargi de « {demande} » à « {fond} » pour englober tous les lieux')
        retenus, vus = [], set()
        for li in lieux:
            nom = 'Paris' if li['fond'] == 'paris' else li['nom']
            if nom in vus:
                notes.append(f'deux lieux de Paris sur la carte « {fond} » : ils se confondent (un seul point « Paris »)')
                continue
            vus.add(nom)
            retenus.append((nom, li))
        cx0, _, _, cy1 = f['projection']['cadre']
        e, cx = f['projection']['echelle'], f['projection']['cx']
        px = [((li['lon'] - cx0) * cx * e, (cy1 - li['lat']) * e) for _, li in retenus]
        L, H, w_min, noms = f['largeur'], f['hauteur'], f['largeur'] * LARGEUR_MIN_FOND, [n for n, _ in retenus]
    xs, ys = [p[0] for p in px], [p[1] for p in px]
    w = max(w_min, (max(xs) - min(xs)) / EMPRISE_POINTS, (max(ys) - min(ys)) / EMPRISE_POINTS * RATIO_MULTI)
    w = min(w, L, H * RATIO_MULTI)
    h = w / RATIO_MULTI
    x0 = min(L - w, max(0, (min(xs) + max(xs)) / 2 - w / 2))
    y0 = min(H - h, max(0, (min(ys) + max(ys)) / 2 - h / 2))
    return fond, [(n, (x - x0) / w, (y - y0) / h) for n, (x, y) in zip(noms, px)], notes


def controler_medaillon_multiple(p: str, t: str, lieux: list[dict], plan: dict | None) -> tuple[list[str], list[str]]:
    """Plusieurs lieux sur une diapositive (spec 12, révision du 2026-10-08) : passages dans l'ordre
    de la narration, instants croissants, fond cohérent (Paris seul ou fonds SVG ; un seul lieu de
    Paris sur une carte plus large), points tous dans le cadre et assez écartés."""
    erreurs, avert = [], []
    depuis = 0
    for li in lieux:
        pos = t.find(li.get('quand') or '\0', depuis)
        if pos < 0:
            erreurs.append(f"{p} : lieu « {li.get('nom')} » : passage « {li.get('quand')} » absent après le lieu précédent "
                           f"(les lieux suivent l'ordre de la narration)")
            return erreurs, avert
        depuis = pos + 1
    inst = [li.get('instant') for li in lieux]
    if all(isinstance(v, (int, float)) for v in inst) and any(inst[k] >= inst[k + 1] for k in range(len(inst) - 1)):
        erreurs.append(f'{p} : instants des lieux non croissants ({", ".join(f"{v:.2f}" for v in inst)})')
    if any(li.get('fond') not in FONDS_LIEU or not isinstance(li.get('lon'), (int, float)) or not isinstance(li.get('lat'), (int, float)) for li in lieux):
        return erreurs, avert  # signalé lieu par lieu
    m = cadre_multiple(lieux, plan)
    if not m:
        erreurs.append(f'{p} : médaillon à plusieurs lieux sans fond (plan de Paris ou carte.py)')
        return erreurs, avert
    fond, pts, notes = m
    for n in notes:
        (erreurs if 'confondent' in n else avert).append(f'{p} : {n}')
    for nom, x, y in pts:
        if not (0.02 <= x <= 0.98 and 0.02 <= y <= 0.98):
            erreurs.append(f'{p} : « {nom} » hors du cadre calculé ({fond})')
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if math.hypot(pts[i][1] - pts[j][1], (pts[i][2] - pts[j][2]) / RATIO_MULTI) < ECART_MIN:
                avert.append(f'{p} : « {pts[i][0]} » et « {pts[j][0]} » presque confondus sur la carte « {fond} »')
    return erreurs, avert


def controler_surimpressions(d: dict) -> tuple[list[str], list[str], int, int]:
    """Cartes de lieu et citations : erreurs, avertissements, nombres de lieux et de citations."""
    erreurs, avert = [], []
    plan = plan_paris(d['slug'])
    cache_f = c.CACHE / d['slug'] / 'surimpressions.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    nl = nc = 0
    from surimpressions import empreinte_audio
    for x in d['diapositives']:
        p, t = f"{x['n']:3d}", x['narration']
        lieux, citations = x.get('lieux') or [], x.get('citations') or []
        if not lieux and not citations:
            continue
        a = x.get('audio') or {}
        du = a.get('duree') or 0
        fa = c.PUBLIC / d['slug'] / a.get('fichier', '')
        a_jour = fa.is_file() and cache.get(str(x['n']), {}).get('empreinte') == empreinte_audio(fa, t)
        if len(lieux) > MAX_LIEUX:
            erreurs.append(f'{p} : {len(lieux)} lieux ({MAX_LIEUX} au plus dans le médaillon)')
        if len(lieux) > 1:
            e_m, a_m = controler_medaillon_multiple(p, t, lieux, plan)
            erreurs += e_m
            avert += a_m
        for li in lieux:
            nl += 1
            q = f"{p} : lieu « {li.get('nom')} »"
            if not str(li.get('nom') or '').strip():
                erreurs.append(f'{q} : nom manquant')
            if not li.get('quand') or li['quand'] not in t:
                erreurs.append(f"{q} : passage « {li.get('quand')} » absent de la narration")
            lon, lat, fond = li.get('lon'), li.get('lat'), li.get('fond')
            if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
                erreurs.append(f'{q} : coordonnées manquantes')
                continue
            if fond not in FONDS_LIEU:
                erreurs.append(f'{q} : fond inconnu ({fond} ; {", ".join(FONDS_LIEU)})')
            elif fond == 'paris':
                if not plan:
                    erreurs.append(f'{q} : aucun plan de Paris pour cette période (carte.py, PLANS)')
                else:
                    u, v = plan['calage']['u'], plan['calage']['v']
                    fu, fv = u[0] * lon + u[1] * lat + u[2], v[0] * lon + v[1] * lat + v[2]
                    if not (0.02 <= fu <= 0.98 and 0.02 <= fv <= 0.98):
                        erreurs.append(f'{q} : hors du plan de Paris ({lat}, {lon})')
            else:
                ff = c.DONNEES / 'fonds' / f'{fond}.json'
                if not ff.is_file():
                    erreurs.append(f'{q} : fond {fond} absent (carte.py)')
                else:
                    x0, y0, x1, y1 = json.loads(ff.read_text())['projection']['cadre']
                    mx, my = (x1 - x0) * 0.03, (y1 - y0) * 0.03
                    if not (x0 + mx <= lon <= x1 - mx and y0 + my <= lat <= y1 - my):
                        erreurs.append(f'{q} : coordonnées hors du cadre « {fond} » ({lat}, {lon})')
                    elif fond != 'france' and en_france(lon, lat):
                        avert.append(f'{q} : lieu en France sur le fond « {fond} » (« france » suffit ?)')
            if 'instant' not in li:
                avert.append(f'{q} : instant non calé, repli au prorata (surimpressions.py)')
            elif not a_jour:
                erreurs.append(f'{q} : instant périmé (voix ou texte changés : surimpressions.py)')
            elif not 0 <= li['instant'] <= du:
                erreurs.append(f"{q} : instant hors de l'audio ({li['instant']})")
        for ci in citations:
            nc += 1
            texte = ci.get('texte') or ''
            q = f"{p} : citation « {texte[:30]}… »"
            pos = t.find(texte) if texte else -1
            if pos < 0:
                erreurs.append(f'{q} : texte absent de la narration (sous-chaîne exacte)')
                continue
            avant = t[:pos]
            if avant.rfind('«') <= avant.rfind('»') or '»' not in t[pos + len(texte):]:
                erreurs.append(f'{q} : texte hors des guillemets « »')
            if c.nb_mots(texte) > 25:
                erreurs.append(f'{q} : {c.nb_mots(texte)} mots (citation courte : 20 environ, 25 au plus)')
            if not str(ci.get('auteur') or '').strip():
                erreurs.append(f'{q} : auteur manquant')
            if 'prudence' in ci and not isinstance(ci['prudence'], bool):
                erreurs.append(f'{q} : « prudence » doit valoir true ou false')
            mots = ci.get('mots')
            if not mots:
                avert.append(f'{q} : mots non minutés, repli au prorata (surimpressions.py)')
                continue
            if len(mots) != len(c.mots_lus(texte)):
                erreurs.append(f'{q} : {len(mots)} mots minutés pour {len(c.mots_lus(texte))} (surimpressions.py)')
            elif not a_jour:
                erreurs.append(f'{q} : instants périmés (voix ou texte changés : surimpressions.py)')
            elif any(not (0 <= m[0] <= m[1] <= du + 0.05) for m in mots) or any(mots[k][0] > mots[k + 1][0] for k in range(len(mots) - 1)):
                erreurs.append(f'{q} : instants des mots incohérents')
    return erreurs, avert, nl, nc


MAX_PORTRAITS = 4  # ovales de la rangée (MAX_PORTRAITS de src/utils/diaporamas.ts)


def controler_portraits(d: dict) -> tuple[list[str], list[str], int, int]:
    """Portraits des personnes nommées : erreurs, avertissements, nombres de mentions montrées et de
    personnes différentes montrées."""
    erreurs, avert = [], []
    reg_f = c.DONNEES / 'portraits.json'
    if not reg_f.exists():
        if any(x.get('personnes') or x.get('personnes_vues') for x in d['diapositives']):
            erreurs.append('portraits.json absent (portraits.py --registre)')
        return erreurs, avert, 0, 0
    registre = json.loads(reg_f.read_text())
    par_id: dict[str, dict] = {}
    for p in registre:
        q = f"portrait « {p.get('id')} »"
        if not p.get('id') or p['id'] in par_id:
            erreurs.append(f'{q} : identifiant manquant ou en double')
            continue
        par_id[p['id']] = p
        if not str(p.get('nom') or '').strip():
            erreurs.append(f'{q} : nom manquant')
        m = re.fullmatch(r'(\d{3,4})-(\d{4})', p.get('dates') or '')
        if not m:
            erreurs.append(f"{q} : dates « {p.get('dates')} » (attendu « 1759-1794 »)")
        if not p.get('fichier'):
            if not str(p.get('note') or '').strip():
                erreurs.append(f'{q} : ni portrait ni note expliquant son absence')
            continue
        for cle in ('commons', 'page', 'auteur', 'date', 'licence'):
            if not str(p.get(cle) or '').strip():
                erreurs.append(f'{q} : « {cle} » manquant')
        if not (c.PUBLIC / p['fichier']).is_file():
            erreurs.append(f"{q} : fichier {p['fichier']} absent (portraits.py --registre)")
        lic = p.get('licence') or ''
        if not c.LICENCE_PD.match(lic) or re.search(r'\bcc[- ]by\b|by-sa|\bnc\b|\bnd\b|gfdl', lic, re.I):
            erreurs.append(f'{q} : licence non admise ({lic} ; domaine public ou CC0)')
        cv = p.get('cadre_visage')
        if not (isinstance(cv, list) and len(cv) == 4 and 0 <= cv[0] < cv[2] <= 1 and 0 <= cv[1] < cv[3] <= 1):
            erreurs.append(f'{q} : cadre du visage invalide ({cv})')
        # Œuvre faite du vivant de la personne ou peu après : l'année de l'œuvre (premier nombre de
        # quatre chiffres) ne dépasse pas la mort de plus de 5 ans, sinon avertissement à relire.
        an = re.search(r'\b(1[5-9]\d\d)\b', p.get('date') or '')
        if m and an and int(an.group(1)) > int(m.group(2)) + 5:
            avert.append(f"{q} : œuvre datée {an.group(1)}, {int(an.group(1)) - int(m.group(2))} ans après la mort (copie d'un portrait d'après nature ? à relire)")
    cache_f = c.CACHE / d['slug'] / 'surimpressions.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    vision_f = c.CACHE / d['slug'] / 'personnes.json'
    vision = json.loads(vision_f.read_text()) if vision_f.exists() else {}
    from surimpressions import empreinte_audio
    n_montres, montres = 0, set()
    for x in d['diapositives']:
        gens, vues = x.get('personnes') or [], x.get('personnes_vues') or []
        if not gens and not vues:
            continue
        p, t = f"{x['n']:3d}", x['narration']
        a = x.get('audio') or {}
        du = a.get('duree') or 0
        fa = c.PUBLIC / d['slug'] / a.get('fichier', '')
        a_jour = fa.is_file() and cache.get(str(x['n']), {}).get('empreinte') == empreinte_audio(fa, t)
        for liste, nom_l in ((gens, 'personnes'), (vues, 'personnes_vues')):
            depuis = 0
            for pe in liste:
                q = f"{p} : {nom_l} « {pe.get('id')} »"
                if pe.get('id') not in par_id and nom_l == 'personnes':
                    erreurs.append(f'{q} : absente du registre portraits.json')
                pos = t.find(pe.get('quand') or '\0', depuis)
                if not pe.get('quand') or pos < 0:
                    erreurs.append(f"{q} : nom « {pe.get('quand')} » absent de la narration (ou hors de l'ordre)")
                    continue
                depuis = pos + 1
        ids_vues = {pe.get('id') for pe in vues}
        for pe in gens:
            if pe.get('id') in ids_vues:
                erreurs.append(f"{p} : « {pe['id']} » à la fois visible sur l'image et montrée en portrait")
        rep_v = {r.get('id'): r for r in vision.get(str(x['n']), {}).get('reponse', [])}
        for pe in {pe.get('id'): pe for pe in gens}.values():
            r = rep_v.get(pe.get('id'))
            if r and r.get('visible'):
                avert.append(f"{p} : « {pe['id']} » montrée en portrait alors que le contrôle de vision la voit sur l'image "
                             f"(relu à la main ? « {str(r.get('raison', ''))[:70]} »)")
        for pe in {pe.get('id'): pe for pe in vues}.values():
            r = rep_v.get(pe.get('id'))
            if r and not r.get('visible'):
                avert.append(f"{p} : « {pe['id']} » notée visible alors que le contrôle de vision ne la voit pas")
        inst = [pe.get('instant') for pe in gens]
        if gens and any(v is None for v in inst):
            avert.append(f'{p} : instants des personnes non calés, repli au prorata (surimpressions.py)')
        elif gens:
            if not a_jour:
                erreurs.append(f'{p} : instants des personnes périmés (voix ou texte changés : surimpressions.py)')
            if any(not 0 <= v <= du for v in inst):
                erreurs.append(f"{p} : instant d'une personne hors de l'audio")
            if any(inst[k] > inst[k + 1] for k in range(len(inst) - 1)):
                erreurs.append(f'{p} : instants des personnes non croissants ({", ".join(f"{v:.2f}" for v in inst)})')
        avec = list(dict.fromkeys(pe['id'] for pe in gens if par_id.get(pe.get('id'), {}).get('fichier')))
        if len(avec) > MAX_PORTRAITS:
            erreurs.append(f'{p} : {len(avec)} portraits ({MAX_PORTRAITS} au plus dans la rangée)')
        n_montres += sum(1 for pe in gens if pe.get('id') in avec[:MAX_PORTRAITS])
        montres |= set(avec[:MAX_PORTRAITS])
        for ci in x.get('citations') or []:
            qui = ci.get('personne')
            if not qui or qui in ids_vues:
                continue
            if qui not in {pe.get('id') for pe in gens}:
                erreurs.append(f"{p} : la citation de « {qui} » n'est pas accompagnée de son portrait (absent de personnes)")
            elif not par_id.get(qui, {}).get('fichier'):
                avert.append(f"{p} : citation de « {qui} », sans portrait fiable au registre")
    for x in d['diapositives']:
        for ci in x.get('citations') or []:
            if ci.get('personne') and not (x.get('personnes') or x.get('personnes_vues')):
                erreurs.append(f"{x['n']:3d} : citation de « {ci['personne']} » sans relevé des personnes")
    return erreurs, avert, n_montres, len(montres)


# --- Objets de musée et manuscrits ; deux surimpressions au plus (spec 12, 2026-10-08) -------------
# Fenêtres d'affichage recalculées comme dans src/utils/diaporamas.ts (surimpressionsDe, portraitsDe,
# medaillonMultiple, objetsDe) : mêmes constantes, mêmes arbitrages.
DUREE_LIEU, APRES_LIEUX = 5.0, 3.0
DUREE_PORTRAITS, APRES_PORTRAITS = 5.0, 3.0
DUREE_OBJET, MIN_OBJET = 5.0, 3.5
DUREE_MANUSCRIT, MIN_MANUSCRIT = 8.0, 5.0
DUREE_CHIFFRE, MIN_CHIFFRE = 4.0, 3.0
DUREE_DATE, MIN_DATE = 5.0, 3.0
ECART_SURIMPRESSION = 0.5
LICENCE_OBJET = re.compile(r'^(Domaine public|CC0|CC BY(-SA)? \d\.\d( [a-z]{2})?)$')


def instant_caractere(x: dict, pos: int) -> float:
    """Instant où la voix prononce le caractère `pos` (prorata dans sa phrase horodatée), comme
    `instantCaractere` du lecteur."""
    t = x['narration']
    a = x.get('audio') or {}
    du, ph = a.get('duree') or 6, a.get('phrases') or []
    debuts = [0]
    for q in c.phrases(t)[:-1]:
        debuts.append(t.index(q, debuts[-1]) + len(q))
    if len(ph) != len(debuts):
        return pos / max(1, len(t)) * du
    j = max(k for k, v in enumerate(debuts) if v <= pos)
    f_car = debuts[j + 1] if j + 1 < len(debuts) else len(t)
    return round(ph[j][0] + (pos - debuts[j]) / max(1, f_car - debuts[j]) * (ph[j][1] - ph[j][0]), 2)


def instants_suivis(x: dict, liste: list[dict]) -> list[float | None]:
    """Instants de mentions cherchées chacune après le début de la précédente (lieux, personnes)."""
    depuis, sortie = 0, []
    for m in liste:
        pos = x['narration'].find(m.get('quand') or '\0', depuis)
        if pos >= 0:
            depuis = pos + 1
        sortie.append(m['instant'] if 'instant' in m else (None if pos < 0 else instant_caractere(x, pos)))
    return sortie


def placer(a0: float, duree: float, mini: float, fin: float, bloques: list[tuple[float, float]]):
    """Même calcul que `placer` de src/utils/diaporamas.ts."""
    B = sorted((f for f in bloques if f[1] > f[0]), key=lambda f: f[0])
    a = a0
    for _ in range(12):
        if a + mini > fin:
            return None
        dedans = next((f for f in B if f[0] <= a < f[1]), None)
        if dedans:
            a = dedans[1]
            continue
        suivant = next((f for f in B if f[0] > a), None)
        b = min(a + duree, suivant[0] if suivant else math.inf)
        if b - a >= mini:
            return (round(a, 2), round(b, 2))
        if not suivant:
            return None
        a = suivant[1]
    return None


def fenetres_surimpressions(x: dict, portraits_reg: dict, objets_reg: dict) -> dict:
    """Fenêtres [a, b) (s de l'audio) de la citation, du médaillon de lieu, de la rangée de portraits,
    du manuscrit et de l'objet d'une diapositive, arbitrées comme dans le lecteur."""
    du = (x.get('audio') or {}).get('duree') or 6
    fin = du + pause_apres(x)
    t = x['narration']
    F: dict[str, tuple[float, float] | None] = {'citation': None, 'lieu': None, 'portraits': None, 'manuscrit': None, 'objet': None, 'chiffre': None, 'date': None}
    ci = (x.get('citations') or [None])[0]
    if ci and ci.get('texte') and ci['texte'] in t:
        pos = t.index(ci['texte'])
        mots = c.mots_lus(ci['texte'])
        if ci.get('mots') and len(ci['mots']) == len(mots):
            d0, dernier = ci['mots'][0][0], ci['mots'][-1][1]
        else:
            d0, dernier = instant_caractere(x, pos + mots[0][0]), instant_caractere(x, pos + len(ci['texte']))
        F['citation'] = (max(0, d0 - 0.15), dernier + APRES_CITATION)
    C = F['citation']
    lieux = [v for v in instants_suivis(x, x.get('lieux') or []) if v is not None][:MAX_LIEUX]
    if lieux:
        a = max(0, min(lieux[0] - 0.1, fin - 4))
        b = max(lieux[-1] + APRES_LIEUX, a + DUREE_LIEU) if len(x.get('lieux') or []) > 1 else a + DUREE_LIEU
        if C and a < C[1] + 0.3 and b > C[0] - 0.5:
            if C[1] + 0.3 + 3 <= fin:
                a = C[1] + 0.3
                b = a + DUREE_LIEU
            elif C[0] - 0.5 - a >= 2.5 and (len(lieux) == 1 or any(v < C[0] - 1.5 for v in lieux)):
                b = C[0] - 0.5
            else:
                a = b = None
        if a is not None:
            F['lieu'] = (round(a, 2), round(b, 2))
    gens, dernier = [], -1.0
    for m, v in zip(x.get('personnes') or [], instants_suivis(x, x.get('personnes') or [])):
        if v is None or not portraits_reg.get(m.get('id'), {}).get('fichier'):
            continue
        if m['id'] in [g for g, _ in gens]:
            dernier = max(dernier, v)
            continue
        if len(gens) >= MAX_PORTRAITS:
            continue
        gens.append((m['id'], v))
        dernier = max(dernier, v)
    if gens:
        a = max(0, min(gens[0][1] - 0.1, fin - 4))
        b = max(dernier + APRES_PORTRAITS, a + DUREE_PORTRAITS)
        if C and ci.get('personne') in [g for g, _ in gens]:
            b = max(b, C[1])
        F['portraits'] = (round(a, 2), round(b, 2))

    def elargir(f):
        return [(f[0] - ECART_SURIMPRESSION, f[1] + ECART_SURIMPRESSION)] if f else []

    def ensemble(p, q):
        return [(max(p[0], q[0]) - ECART_SURIMPRESSION, min(p[1], q[1]) + ECART_SURIMPRESSION)] if p and q and min(p[1], q[1]) > max(p[0], q[0]) else []

    def instant_de(m):
        return m['instant'] if 'instant' in m else (instant_caractere(x, t.index(m['quand'])) if m.get('quand') in t else None)
    mm = (x.get('manuscrits') or [None])[0]
    if mm and objets_reg.get(mm.get('id'), {}).get('fichier') and instant_de(mm) is not None:
        a0 = max(0.3, min(instant_de(mm) - 0.1, fin - 6))
        F['manuscrit'] = placer(a0, DUREE_MANUSCRIT, MIN_MANUSCRIT, fin, elargir(C) + ensemble(F['lieu'], F['portraits']))
    mo = (x.get('objets') or [None])[0]
    if mo and objets_reg.get(mo.get('id'), {}).get('fichier') and instant_de(mo) is not None:
        coin = F['lieu'] if mo.get('cote', 'droite') == 'droite' else F['portraits']
        a0 = max(0.3, min(instant_de(mo) - 0.1, fin - 4))
        L, P, M = F['lieu'], F['portraits'], F['manuscrit']
        F['objet'] = placer(a0, DUREE_OBJET, MIN_OBJET, fin, elargir(C) + elargir(M) + elargir(coin)
                            + ensemble(L, P) + ensemble(L, M) + ensemble(P, M))

    # Chiffre clé puis date républicaine (chiffresDe) : ils cèdent à la citation et à tout instant où
    # deux autres surimpressions sont déjà là.
    def paires(fs):
        return [b for k, p in enumerate(fs) for q in fs[k + 1:] for b in ensemble(p, q)]
    mc = (x.get('chiffres') or [None])[0]
    if mc and instant_de(mc) is not None:
        a0 = max(0.3, min(instant_de(mc) - 0.1, fin - 3.5))
        F['chiffre'] = placer(a0, DUREE_CHIFFRE, MIN_CHIFFRE, fin, elargir(C) + paires([F['lieu'], F['portraits'], F['objet'], F['manuscrit']]))
    md = (x.get('dates_republicaines') or [None])[0]
    if md and md.get('gregorien') and instant_de(md) is not None:
        a0 = max(0.3, min(instant_de(md) - 0.1, fin - 3.5))
        F['date'] = placer(a0, DUREE_DATE, MIN_DATE, fin, elargir(C) + paires([F['lieu'], F['portraits'], F['objet'], F['manuscrit'], F['chiffre']]))
    return F


def controler_objets(d: dict) -> tuple[list[str], list[str], int, int, int]:
    """Objets de musée et manuscrits (registre objets.json, mentions des diapositives) et règle des
    deux surimpressions au plus : erreurs, avertissements, nombres d'objets, de manuscrits montrés
    et de diapositives où deux surimpressions se montrent ensemble."""
    erreurs, avert = [], []
    reg_f = c.DONNEES / 'objets.json'
    registre = json.loads(reg_f.read_text()) if reg_f.exists() else []
    if not registre and any(x.get('objets') or x.get('manuscrits') for x in d['diapositives']):
        erreurs.append('objets.json absent (objets.py --registre)')
    par_id: dict[str, dict] = {}
    for o in registre:
        q = f"objet « {o.get('id')} »"
        if not o.get('id') or o['id'] in par_id:
            erreurs.append(f'{q} : identifiant manquant ou en double')
            continue
        par_id[o['id']] = o
        if o.get('type') not in ('objet', 'manuscrit'):
            erreurs.append(f"{q} : type « {o.get('type')} » (objet ou manuscrit)")
        for cle in ('nom', 'date', 'musee', 'commons', 'page', 'licence', 'fichier'):
            if not str(o.get(cle) or '').strip():
                erreurs.append(f'{q} : « {cle} » manquant (objets.py --registre)')
        if len(o.get('nom') or '') > 64:
            avert.append(f'{q} : légende longue ({len(o["nom"])} caractères ; 60 environ)')
        if o.get('fichier') and not (c.PUBLIC / o['fichier']).is_file():
            erreurs.append(f"{q} : fichier {o['fichier']} absent (objets.py --registre)")
        lic = o.get('licence') or ''
        if not LICENCE_OBJET.match(lic) or re.search(r'\bnc\b|\bnd\b', lic, re.I):
            erreurs.append(f'{q} : licence non admise ({lic} ; domaine public, CC0, CC BY ou CC BY-SA)')
        elif lic.startswith('CC BY') and not str(o.get('auteur_photo') or '').strip():
            erreurs.append(f'{q} : licence {lic} sans auteur de la photo (crédit obligatoire)')
        if o.get('type') == 'manuscrit':
            h = o.get('halo')
            if not (isinstance(h, list) and len(h) == 4 and 0 <= h[0] < h[2] <= 1 and 0 <= h[1] < h[3] <= 1):
                erreurs.append(f'{q} : halo invalide ({h})')
            if not str(o.get('passage') or '').strip():
                erreurs.append(f'{q} : passage éclairé non transcrit')
    portraits_reg = {p['id']: p for p in (json.loads((c.DONNEES / 'portraits.json').read_text()) if (c.DONNEES / 'portraits.json').exists() else []) if p.get('id')}
    cache_f = c.CACHE / d['slug'] / 'surimpressions.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    from surimpressions import empreinte_audio
    n_obj = n_man = n_deux = 0
    for x in d['diapositives']:
        p, t = f"{x['n']:3d}", x['narration']
        a = x.get('audio') or {}
        du = a.get('duree') or 0
        fa = c.PUBLIC / d['slug'] / a.get('fichier', '')
        for cle, genre in (('objets', 'objet'), ('manuscrits', 'manuscrit')):
            liste = x.get(cle) or []
            if len(liste) > 1:
                erreurs.append(f'{p} : {len(liste)} {cle} (un au plus par diapositive)')
            for m in liste:
                q = f"{p} : {genre} « {m.get('id')} »"
                o = par_id.get(m.get('id'))
                if not o:
                    erreurs.append(f'{q} : absent du registre objets.json')
                elif o.get('type') != genre:
                    erreurs.append(f"{q} : de type « {o.get('type')} » dans le registre")
                if not m.get('quand') or m['quand'] not in t:
                    erreurs.append(f"{q} : passage « {m.get('quand')} » absent de la narration")
                    continue
                if m.get('cote', 'droite') not in ('droite', 'gauche'):
                    erreurs.append(f"{q} : côté « {m.get('cote')} » (droite ou gauche)")
                if 'instant' not in m:
                    avert.append(f'{q} : instant non calé, repli au prorata (surimpressions.py)')
                elif not (fa.is_file() and cache.get(str(x['n']), {}).get('empreinte') == empreinte_audio(fa, t)):
                    erreurs.append(f'{q} : instant périmé (voix ou texte changés : surimpressions.py)')
                elif not 0 <= m['instant'] <= du:
                    erreurs.append(f"{q} : instant hors de l'audio ({m['instant']})")
                else:
                    # Instant aligné : proche du prorata des phrases (sinon alignement à relire).
                    pro = instant_caractere(x, t.index(m['quand']))
                    if abs(pro - m['instant']) > 2.5:
                        avert.append(f"{q} : instant {m['instant']:.2f} s loin du prorata ({pro:.2f} s) : alignement à relire")
        if not any(x.get(k) for k in ('citations', 'lieux', 'personnes', 'objets', 'manuscrits', 'chiffres', 'dates_republicaines')):
            continue
        F = fenetres_surimpressions(x, portraits_reg, par_id)
        if x.get('objets'):
            if F['objet']:
                n_obj += 1
                if F['objet'][1] - F['objet'][0] < DUREE_OBJET - 0.01:
                    avert.append(f"{p} : objet raccourci à {F['objet'][1] - F['objet'][0]:.1f} s (il cède la place)")
            else:
                avert.append(f'{p} : objet omis faute de place (autres surimpressions)')
        if x.get('manuscrits'):
            if F['manuscrit']:
                n_man += 1
                if F['manuscrit'][1] - F['manuscrit'][0] < DUREE_MANUSCRIT - 0.01:
                    avert.append(f"{p} : manuscrit raccourci à {F['manuscrit'][1] - F['manuscrit'][0]:.1f} s")
            else:
                avert.append(f'{p} : manuscrit omis faute de place (citation)')
        # Deux surimpressions au plus à la fois (la frise du temps, éphémère, cède à l'exécution).
        fins = (a.get('duree') or 6) + pause_apres(x)
        actives = {k: v for k, v in F.items() if v}
        pire, quand_pire = 0, 0.0
        for k in range(int(fins / 0.05) + 1):
            ti = k * 0.05
            n = sum(1 for v in actives.values() if v[0] <= ti < v[1])
            if n > pire:
                pire, quand_pire = n, ti
        if pire > 2:
            erreurs.append(f"{p} : {pire} surimpressions à la fois vers {quand_pire:.1f} s ({', '.join(f'{k} {v[0]:.1f}-{v[1]:.1f}' for k, v in actives.items())})")
        elif pire == 2:
            n_deux += 1
        o = F['objet']
        coin = F['lieu'] if ((x.get('objets') or [{}])[0].get('cote', 'droite') == 'droite') else F['portraits']
        if o and coin and min(o[1], coin[1]) > max(o[0], coin[0]) - ECART_SURIMPRESSION:
            erreurs.append(f'{p} : objet et surimpression du même coin ensemble ({o} / {coin})')
        if F['manuscrit'] and chevauchent(F['manuscrit'], F['citation']):
            erreurs.append(f'{p} : manuscrit et citation ensemble')
        for k, cle, duree in (('chiffre', 'chiffres', DUREE_CHIFFRE), ('date', 'dates_republicaines', DUREE_DATE)):
            if F[k] and chevauchent(F[k], F['citation']):
                erreurs.append(f'{p} : {k} et citation ensemble')
            if x.get(cle):
                if not F[k]:
                    avert.append(f"{p} : {k} {'omis' if k == 'chiffre' else 'omise'} faute de place (autres surimpressions)")
                elif F[k][1] - F[k][0] < duree - 0.01:
                    avert.append(f"{p} : {k} {'raccourci' if k == 'chiffre' else 'raccourcie'} à {F[k][1] - F[k][0]:.1f} s (cède la place)")
    return erreurs, avert, n_obj, n_man, n_deux


# --- Chiffres clés et dates républicaines (spec 12, « Enrichissements visuels », point 4) ---------
# Table de concordance officielle : 1er vendémiaire de chaque an (an I à XIV), indépendante du calcul
# de commun.premier_vendemiaire (qui ajoute la durée des années, sextiles III, VII et XI).
PREMIER_VENDEMIAIRE = {1: '1792-09-22', 2: '1793-09-22', 3: '1794-09-22', 4: '1795-09-23', 5: '1796-09-22',
                       6: '1797-09-22', 7: '1798-09-22', 8: '1799-09-23', 9: '1800-09-23', 10: '1801-09-23',
                       11: '1802-09-23', 12: '1803-09-24', 13: '1804-09-23', 14: '1805-09-23'}
# Dates connues (journées et lois célèbres, fin du calendrier).
DATES_CONNUES = {'1er vendémiaire an I': '22 septembre 1792', '22 prairial an II': '10 juin 1794',
                 '9 thermidor an II': '27 juillet 1794', '1er prairial an III': '20 mai 1795',
                 '13 vendémiaire an IV': '5 octobre 1795', '18 fructidor an V': '4 septembre 1797',
                 '18 brumaire an VIII': '9 novembre 1799', '10 nivôse an XIV': '31 décembre 1805'}
PRUDENCES = ('plus de', 'près de', 'environ', 'moins de', 'quelque', 'presque')


def _iso(texte: str) -> str:
    """« 27 juillet 1794 » → « 1794-07-27 »."""
    j, mo, an = texte.split(' ')
    return f"{an}-{MOIS.index(mo) + 1:02d}-{1 if j == '1er' else int(j):02d}"


def controler_chiffres(d: dict) -> tuple[list[str], list[str], int, int, int]:
    """Chiffres clés et dates républicaines : erreurs, avertissements, nombre de chiffres, de dates et
    de dates confirmées par la narration ou la date de la diapositive."""
    erreurs, avert = [], []
    for an, iso in PREMIER_VENDEMIAIRE.items():
        if c.premier_vendemiaire(an).isoformat() != iso:
            erreurs.append(f'calendrier républicain : 1er vendémiaire an {an} calculé {c.premier_vendemiaire(an)} (table : {iso})')
    for rep, greg in DATES_CONNUES.items():
        if (c.date_republicaine(rep) or ('', ''))[1] != greg:
            erreurs.append(f'calendrier républicain : {rep} calculé {c.date_republicaine(rep)} (attendu : {greg})')
    cache_f = c.CACHE / d['slug'] / 'surimpressions.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    from surimpressions import empreinte_audio
    n_ch = n_da = n_conf = 0
    for x in d['diapositives']:
        p, t = f"{x['n']:3d}", x['narration']
        a = x.get('audio') or {}
        fa = c.PUBLIC / d['slug'] / a.get('fichier', '')
        for cle, genre in (('chiffres', 'chiffre'), ('dates_republicaines', 'date')):
            liste = x.get(cle) or []
            if len(liste) > 1:
                erreurs.append(f'{p} : {len(liste)} {cle} (un au plus par diapositive)')
            for m in liste:
                q = f"{p} : {genre} « {m.get('quand')} »"
                if not m.get('quand') or m['quand'] not in t:
                    erreurs.append(f'{q} : passage absent de la narration')
                    continue
                if 'instant' not in m:
                    avert.append(f'{q} : instant non calé, repli au prorata (surimpressions.py)')
                elif not (fa.is_file() and cache.get(str(x['n']), {}).get('empreinte') == empreinte_audio(fa, t)):
                    erreurs.append(f'{q} : instant périmé (voix ou texte changés : surimpressions.py)')
                elif not 0 <= m['instant'] <= (a.get('duree') or 0):
                    erreurs.append(f"{q} : instant hors de l'audio ({m['instant']})")
                elif abs(instant_caractere(x, t.index(m['quand'])) - m['instant']) > 2.5:
                    avert.append(f"{q} : instant {m['instant']:.2f} s loin du prorata : alignement à relire")
                if genre == 'chiffre':
                    n_ch += 1
                    dit = c.nombre_dit(m['quand'])
                    if dit is None or dit != m.get('valeur'):
                        erreurs.append(f"{q} : nombre dit {dit} ≠ valeur {m.get('valeur')}")
                    prud = next((w for w in PRUDENCES if re.search(rf'\b{w}\b', m['quand'].lower())), '')
                    if prud != (m.get('prefixe') or '').lower():
                        erreurs.append(f"{q} : prudence « {prud} » dite, préfixe « {m.get('prefixe') or ''} »")
                    if not str(m.get('unite') or '').strip() or len(m['unite']) > 45:
                        erreurs.append(f'{q} : unité manquante ou trop longue (45 caractères au plus)')
                    if not str(m.get('source') or '').strip():
                        erreurs.append(f'{q} : source non notée')
                    continue
                n_da += 1
                rep = m.get('republicain') or ''
                # Le passage dit est le début de la date affichée (« 22 prairial » → « 22 prairial an II »).
                if not rep.startswith(re.sub(r"^l'", '', m['quand'])):
                    avert.append(f'{q} : date affichée « {rep} » éloignée du passage dit')
                conv = c.date_republicaine(rep)
                if not conv:
                    erreurs.append(f'{q} : date républicaine « {rep} » illisible (« 9 thermidor an II », « an III »)')
                elif conv[1] != m.get('gregorien'):
                    erreurs.append(f"{q} : correspondance « {m.get('gregorien')} », recalculée « {conv[1]} »")
                elif ' – ' in conv[1]:
                    # Année seule : la date de la diapositive doit y tomber.
                    d0, d1 = (_iso(v) for v in conv[1].split(' – '))
                    if x.get('date') and not d0[:len(x['date'])] <= x['date'] <= d1:
                        erreurs.append(f"{q} : date de la diapositive {x['date']} hors de {rep} ({conv[1]})")
                    else:
                        n_conf += 1
                elif conv[1] in re.sub(r'[  ]', ' ', t) or x.get('date') == _iso(conv[1]) or str(m.get('relu') or '').strip():
                    # Confirmée par la voix, par la date de la diapositive, ou relue (`relu` : pourquoi).
                    n_conf += 1
                else:
                    avert.append(f'{q} : {conv[1]} ni dit par la narration ni date de la diapositive (à relire)')
    return erreurs, avert, n_ch, n_da, n_conf


def chevauchent(p, q) -> bool:
    """Deux fenêtres [a, b) se recouvrent-elles ?"""
    return bool(p and q and min(p[1], q[1]) > max(p[0], q[0]))


def _sans_accents(t: str) -> str:
    t = unicodedata.normalize('NFKD', t.lower().replace('’', "'"))
    return ' '.join(re.findall(r"[a-z0-9']+", ''.join(ch for ch in t if not unicodedata.combining(ch))))


FONDU_PISTE = 3.0  # s : chevauchement de deux pistes de fond d'un acte (FONDU_PISTE de Diaporama.astro)


def controler_boucles(d: dict) -> list[str]:
    """Musique de fond (spec 12, retours du 2026-10-07) : avertit quand un acte dure plus que ses
    pistes enchaînées (le lecteur les ferait boucler). Durée de l'acte : carton, diapositives et
    tout ce qui suit l'une d'elles (intermèdes, lectures, épisodes), pauses comprises."""
    m = d.get('musique') or {}
    apres: dict[int, float] = {}
    for s in m.get('intermedes', []):
        apres[s.get('apres')] = apres.get(s.get('apres'), 0) + (s.get('duree') or 0) + PAUSE
    for s in d.get('lectures', []) + d.get('episodes', []):
        apres[s.get('apres')] = apres.get(s.get('apres'), 0) + ((s.get('audio') or {}).get('duree') or 0) + PAUSE
    avert, actes = [], d['actes']
    for k, a in enumerate(actes):
        fin = actes[k + 1]['debut'] if k + 1 < len(actes) else float('inf')
        duree = CARTON + sum((x.get('audio') or {}).get('duree', 0) + pause_apres(x) + apres.get(x['n'], 0)
                             for x in d['diapositives'] if a['debut'] <= x['n'] < fin)
        pistes = [p.get('duree') or 0 for p in m.get('fond', []) if p.get('acte') == a['id']]
        if not pistes:
            continue
        musique = sum(pistes) - FONDU_PISTE * (len(pistes) - 1)
        if duree > musique:
            avert.append(f"musique : l'acte {a['id']} dure {duree:.0f} s, ses pistes de fond {musique:.0f} s "
                         f"(fondus déduits) : elles boucleraient ; allonger une piste (« fin ») ou en ajouter une")
    return avert


def _paroles_au_mot(q: str, p: dict, par: list, duree: float) -> list[str]:
    """Paroles calées au mot (spec 12, « Paroles des chants façon clip », paroles.py) : chaque vers
    porte [début, fin] de chacun de ses mots (`commun.mots_lus`), dans l'ordre (débuts strictement
    croissants d'un bout à l'autre du chant), dans la durée de l'extrait, le vers commençant à son
    premier mot ; `calage` dit « mot » (tous les vers calés) ou « vers » (repli, aucun)."""
    err = []
    cales = [x for x in par if len(x) == 3]
    calage = p.get('calage')
    if calage not in (None, 'mot', 'vers'):
        err.append(f'{q} : calage « {calage} » inconnu (« mot » ou « vers »)')
    if calage == 'mot' and len(cales) != len(par):
        err.append(f'{q} : calage « mot » mais {len(par) - len(cales)} vers sans mots horodatés')
    if calage in (None, 'vers') and cales:
        err.append(f'{q} : mots horodatés sans « calage: mot »')
    prec = -1.0
    for k, x in enumerate(cales):
        vers, mots = x[1], x[2]
        noms = [m for _, _, m in c.mots_lus(vers)]
        if not (isinstance(mots, list) and len(mots) == len(noms)
                and all(isinstance(m, list) and len(m) == 2 and all(isinstance(v, (int, float)) for v in m) for m in mots)):
            err.append(f'{q} : vers « {vers} » : {len(mots) if isinstance(mots, list) else 0} mots horodatés pour {len(noms)}')
            continue
        if abs(mots[0][0] - x[0]) > 0.05:
            err.append(f'{q} : vers « {vers} » : commence à {x[0]} s, son premier mot à {mots[0][0]} s')
        for nom, (d, fi) in zip(noms, mots):
            if d <= prec:
                err.append(f'{q} : « {nom} » ({vers}) : {d} s, pas après le mot précédent ({prec} s)')
            if fi < d or d < 0 or fi > duree + 0.01:
                err.append(f'{q} : « {nom} » ({vers}) : [{d}, {fi}] hors de l\'extrait (0 à {duree} s) ou à l\'envers')
            prec = d
    for cle in ('calage_fenetres', 'calage_retouches'):
        if cle in p and not (isinstance(p[cle], list) and all(v is None or isinstance(v, list) for v in p[cle])):
            err.append(f'{q} : {cle} invalide')
    return err


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
        # Cartouche du lecteur rédigé à la main : deux lignes, sans troncature (spec 12).
        k = p.get('cartouche') or {}
        if not (str(k.get('oeuvre') or '').strip() and str(k.get('compositeur') or '').strip()):
            erreurs.append(f'{q} : cartouche (oeuvre, compositeur) manquant')
        elif max(len(k['oeuvre']), len(k['compositeur'])) > 60:
            erreurs.append(f'{q} : cartouche trop long (60 caractères par ligne au plus)')
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
        elif any(not (isinstance(x, list) and len(x) in (2, 3) and isinstance(x[0], (int, float)) and str(x[1]).strip()) for x in par) \
                or [x[0] for x in par] != sorted(x[0] for x in par) or par[0][0] < 0 or par[-1][0] >= duree:
            erreurs.append(f'{q} : paroles mal horodatées ({[x[:2] for x in par]})')
        else:
            erreurs += _paroles_au_mot(q, p, par, duree)
        # Cadre facultatif de la caméra pendant l'intermède (spec 12, « Caméra calme et lente ») :
        # rectangle normalisé de l'image de la diapositive `apres`.
        if 'cadre' in p:
            r = p['cadre']
            if not (isinstance(r, list) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r)
                    and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
                erreurs.append(f'{q} : cadre invalide ({r}) : [x0, y0, x1, y1] entre 0 et 1, x0 < x1 et y0 < y1')
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
                    # Graphiques des épisodes : le dernier point a son étiquette ; valeurs en clair.
                    if pts and pts[-1][0] not in {r.get('date') for r in v.get('reperes', [])}:
                        erreurs.append(f'{qv} : le dernier point n’a pas de repère (étiquette)')
                    if any(re.search(r'\d\s*[lsd]\.', r.get('libelle') or '') for r in v.get('reperes', [])):
                        erreurs.append(f'{qv} : étiquette en notation d’époque (l. s. d.) : écrire la valeur en clair')
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



# --- Avant / après et mosaïques (spec 12, « Enrichissements visuels », points 3 et 5) ------------
VOLET = 3.5   # durée du volet (s) ; mêmes valeurs que src/utils/diaporamas.ts
MOSAIQUE = {'apparition': 0.3, 'pas': 0.5, 'fondu': 0.8, 'tenue': 1.0}
PLONGEE_MIN = 3.0  # durée minimale de la plongée (s) : le lecteur l'allonge selon l'ampleur (~5 s pour une grille de 2 lignes)


def debut_plongee(n: int) -> float:
    return MOSAIQUE['apparition'] + (n - 1) * MOSAIQUE['pas'] + MOSAIQUE['fondu'] + MOSAIQUE['tenue']


def controler_avant_apres_mosaiques(d: dict, img_etat: dict, dossier) -> tuple[list[str], list[str], int, int]:
    """Avant / après (`image.apres`) et mosaïques (`mosaique`) : fichiers, licences relevées par
    images.py, métadonnées, zone utile, cadres, passages exacts et dans l'ordre, place du volet dans
    la voix ; vignettes présentes (4 à 6), `principale` valide (l'image de la diapositive), pas sur
    une diapositive d'ouverture d'acte, grille et plongée tenues dans la voix. Dosage : 3 à 4
    avant/après et 2 mosaïques par période (avertissement sinon)."""
    erreurs, avert = [], []
    debuts = {a['debut'] for a in d['actes']}
    inter = {i['apres'] for i in (d.get('musique') or {}).get('intermedes', []) if i.get('cadre')}
    n_ap = n_mos = 0

    def licence(q: str, cle: str, i: dict):
        e = img_etat.get(cle)
        if not e or e.get('commons') != i.get('commons'):
            erreurs.append(f'{q} : licence non relevée pour ce fichier (relancer images.py)')
        elif not e.get('libre'):
            erreurs.append(f"{q} : licence refusée ({e.get('licence')})")
        elif (e.get('largeur') or 0) < 1000:
            avert.append(f"{q} : original étroit ({e.get('largeur')} px)")
        if i.get('licence') != 'Domaine public':
            erreurs.append(f'{q} : licence affichée absente')
        if not i.get('fichier') or not (dossier / i['fichier']).is_file():
            erreurs.append(f"{q} : image absente ({i.get('fichier')})")

    for x in d['diapositives']:
        n, t = x['n'], x['narration']
        ap = x['image'].get('apres')
        if ap is not None:
            n_ap += 1
            q = f'{n:3d} : avant/après'
            licence(q, f"apres:{ap.get('commons')}", ap)
            manquants = [k for k in CHAMPS if not (ap.get(k) or '').strip()]
            if manquants:
                erreurs.append(f"{q} : métadonnées manquantes de l'image après ({', '.join(manquants)})")
            tc = (ap.get('titre_court') or '').strip()
            if not tc or len(tc) > 60:
                erreurs.append(f"{q} : titre court de l'image après manquant ou trop long")
            if ap.get('commons') == x['image'].get('commons'):
                erreurs.append(f'{q} : image après identique à l’image avant')
            r = ap.get('cadre')
            if not (isinstance(r, list) and len(r) == 4 and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
                erreurs.append(f'{q} : cadre de raccord invalide ({r})')
            pseudo = {'narration': t, 'image': {**ap, 'camera': [{'cadre': r}] + list(ap.get('camera') or [])}}
            e_ut, a_ut = controler_utile(pseudo)
            erreurs += [f'{q} (image après) : {e}' for e in e_ut]
            avert += [f'{q} (image après) : {e}' for e in a_ut]
            quand = ap.get('quand') or ''
            pos = t.find(quand) if quand else -1
            if pos < 0:
                erreurs.append(f'{q} : passage du volet « {quand} » absent de la narration')
                continue
            # Les étapes de l'image avant précèdent le volet ; celles de l'image après le suivent.
            for e in (x['image'].get('camera') or [])[1:]:
                if e.get('quand') and t.find(e['quand']) >= pos:
                    erreurs.append(f"{q} : étape « {e['quand']} » de l'image avant après le passage du volet")
            apres = pos + len(quand)
            for e in ap.get('camera') or []:
                k = t.find(e.get('quand') or '\0', apres)
                if not e.get('quand') or k < 0:
                    erreurs.append(f"{q} : étape « {e.get('quand')} » de l'image après absente de la narration ou avant le volet")
                else:
                    apres = k + len(e['quand'])
                rr = e.get('cadre')
                if not (isinstance(rr, list) and len(rr) == 4 and 0 <= rr[0] < rr[2] <= 1 and 0 <= rr[1] < rr[3] <= 1):
                    erreurs.append(f"{q} : cadre invalide sur l'image après ({rr})")
            if len((x['image'].get('camera') or [])) + 1 + len(ap.get('camera') or []) > 5:
                avert.append(f'{q} : beaucoup d’étapes de caméra pour une diapositive')
            ti = instant_caractere(x, pos)
            du = (x.get('audio') or {}).get('duree') or 0
            if ti < 2:
                avert.append(f"{q} : volet à {ti:.1f} s, l'image avant à peine vue")
            if du and ti + VOLET > du - 1:
                erreurs.append(f'{q} : volet ({ti:.1f} s + {VOLET} s) trop près de la fin de la voix ({du:.1f} s)')
            if n in inter:
                erreurs.append(f'{q} : avant/après et intermède cadré sur la même diapositive (non pris en charge)')
        mo = x.get('mosaique')
        if mo is not None:
            n_mos += 1
            q = f'{n:3d} : mosaïque'
            V = mo.get('vignettes') or []
            k = mo.get('principale')
            if not 4 <= len(V) <= 6:
                erreurs.append(f'{q} : {len(V)} vignettes (4 à 6)')
            if not isinstance(k, int) or not 0 <= k < len(V):
                erreurs.append(f'{q} : « principale » invalide ({k})')
            elif V[k].get('commons') != x['image'].get('commons'):
                erreurs.append(f"{q} : la vignette principale ({k}) n'est pas l'image de la diapositive")
            leg = (mo.get('legende') or '').strip()
            if not leg or len(leg) > 60:
                erreurs.append(f'{q} : ligne du cartouche (« legende ») manquante ou trop longue')
            if len({v.get('commons') for v in V}) != len(V):
                erreurs.append(f'{q} : vignettes en double')
            if x['image'].get('ouverture') or n in debuts:
                erreurs.append(f"{q} : pas de mosaïque sur la première diapositive d'un acte (ouverture du carton)")
            if x['image'].get('apres'):
                erreurs.append(f'{q} : mosaïque et avant/après sur la même diapositive')
            for j, v in enumerate(V):
                if j == k:
                    continue
                qv = f'{q}, vignette {j}'
                licence(qv, f"vignette:{v.get('commons')}", v)
                manquants = [c_ for c_ in ('titre', 'auteur', 'date') if not (v.get(c_) or '').strip()]
                if manquants:
                    erreurs.append(f"{qv} : métadonnées manquantes ({', '.join(manquants)})")
                u = v.get('utile')
                if not (isinstance(u, list) and len(u) == 4 and 0 <= u[0] < u[2] <= 1 and 0 <= u[1] < u[3] <= 1):
                    erreurs.append(f'{qv} : zone utile absente ou invalide (utile.py)')
                elif (u[2] - u[0]) * (u[3] - u[1]) < UTILE_AIRE_MIN:
                    erreurs.append(f'{qv} : zone utile absurde ({u})')
            du = (x.get('audio') or {}).get('duree') or 0
            if du and debut_plongee(len(V)) + PLONGEE_MIN + 3 > du:
                erreurs.append(f'{q} : voix trop courte ({du:.1f} s) pour la grille et la plongée')
    if n_ap and not 3 <= n_ap <= 4:
        avert.append(f'{n_ap} avant/après (3 à 4 visés par période)')
    if n_mos and n_mos != 2:
        avert.append(f'{n_mos} mosaïque(s) (2 visées par période)')
    return erreurs, avert, n_ap, n_mos


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

    # Une même œuvre deux fois au plus, images après et vignettes de mosaïque comprises.
    oeuvres = Counter(x['image']['commons'] for x in diapos)
    for x in diapos:
        if x['image'].get('apres'):
            oeuvres[x['image']['apres'].get('commons')] += 1
        mo = x.get('mosaique') or {}
        for j, v in enumerate(mo.get('vignettes', [])):
            if j != mo.get('principale'):
                oeuvres[v.get('commons')] += 1
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
        tc = (i.get('titre_court') or '').strip()
        if not tc:
            erreurs.append(f'{p} : titre court (titre_court) manquant pour le cartouche')
        elif len(tc) > 60:
            erreurs.append(f'{p} : titre court trop long ({len(tc)} caractères, 60 au plus)')
        if 'cadrage' in i:
            erreurs.append(f'{p} : champ « cadrage » supprimé (remplacé par « camera »)')
        erreurs += [f'{p} : {e}' for e in controler_camera(x)]
        e_ouv, a_ouv = controler_ouverture(x, n in debuts)
        erreurs += [f'{p} : {e}' for e in e_ouv]
        avert += [f'{p} : {e}' for e in a_ouv]
        cadre_inter = next((s.get('cadre') for s in (d.get('musique') or {}).get('intermedes', []) if s.get('apres') == n), None)
        e_ut, a_ut = controler_utile(x, cadre_inter)
        erreurs += [f'{p} : {e}' for e in e_ut]
        avert += [f'{p} : {e}' for e in a_ut]

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
    avert += controler_boucles(d)
    e_sur, a_sur, n_lieux, n_cit = controler_surimpressions(d)
    erreurs += e_sur
    avert += a_sur
    e_por, a_por, n_portraits, n_gens = controler_portraits(d)
    erreurs += e_por
    avert += a_por
    e_obj, a_obj, n_objets, n_manuscrits, n_deux = controler_objets(d)
    erreurs += e_obj
    avert += a_obj
    e_ch, a_ch, n_chiffres, n_dates, n_conf = controler_chiffres(d)
    erreurs += e_ch
    avert += a_ch
    e_am, a_am, n_ap, n_mos = controler_avant_apres_mosaiques(d, img, dossier)
    erreurs += e_am
    avert += a_am

    pauses = [pause_apres(x) for x in diapos]
    longues = [(x['n'], q) for x, q in zip(diapos, pauses) if q > PAUSE]
    total = sum(durees) + sum(pauses) + CARTON * len(d['actes']) + duree_chants + duree_segments
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
    if n_lieux or n_cit:
        print(f'Surimpressions : {n_lieux} lieu(x) dans {sum(1 for x in d["diapositives"] if x.get("lieux"))} médaillon(s) de carte, {n_cit} citation(s) ; pause allongée après la voix '
              f"(citation finale) : {', '.join(f'{n} ({q:.2f} s)' for n, q in longues) or 'aucune'}.")
    if n_portraits:
        n_ment = sum(len(x.get('personnes') or []) + len(x.get('personnes_vues') or []) for x in diapos)
        n_vues = sum(len(x.get('personnes_vues') or []) for x in diapos)
        print(f'Portraits : {n_ment} mention(s) de personnes, dont {n_vues} visibles sur l’image ; '
              f'{n_portraits} mention(s) avec portrait, {n_gens} personne(s) différente(s) montrée(s).')
    if n_objets or n_manuscrits:
        print(f'Objets et manuscrits : {n_objets} objet(s) de musée, {n_manuscrits} manuscrit(s) montrés (visés : ~10 et 3 à 4) ; '
              f'deux surimpressions ensemble sur {n_deux} diapositive(s), jamais plus.')
        if not 6 <= n_objets <= 14:
            avert.append(f'{n_objets} objet(s) de musée (~10 visés par période)')
        if not 3 <= n_manuscrits <= 4:
            avert.append(f'{n_manuscrits} manuscrit(s) (3 à 4 visés par période)')
    if n_chiffres or n_dates:
        print(f'Chiffres clés et dates : {n_chiffres} chiffre(s) (~8 visés), {n_dates} date(s) républicaine(s), '
              f'correspondances recalculées ({n_conf} confirmée(s) par la narration ou la date de la diapositive).')
    if n_ap or n_mos:
        print(f"Avant/après et mosaïques : {n_ap} avant/après (diapositives {', '.join(str(x['n']) for x in diapos if x['image'].get('apres'))}), "
              f"{n_mos} mosaïque(s) (diapositives {', '.join(str(x['n']) for x in diapos if x.get('mosaique'))}).")
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
        slugs = [f.stem for f in sorted(c.DONNEES.glob('*.json')) if re.match(r'\d+-', f.stem)]  # pas portraits.json
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
