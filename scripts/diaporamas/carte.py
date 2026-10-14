"""Fonds de carte des épisodes (spec 12, « Lectures d'époque et épisodes »).

Usage :
    python3 scripts/diaporamas/carte.py            # (re)fait src/data/diaporamas/fonds/*.json
    python3 scripts/diaporamas/carte.py --fond monde   # ce fond seulement (ni plans ni autres fonds)

Les cartes animées des épisodes sont dessinées en SVG par le lecteur, sur un fond simplifié
tiré de Natural Earth (domaine public, https://www.naturalearthdata.com/) : terres émergées,
contour de la France (frontières actuelles : elles diffèrent peu de celles de 1793, Savoie et
Nice comprises), grands fleuves. Les données sont projetées (équirectangulaire, échelle des
longitudes corrigée à la latitude moyenne), découpées au cadre et simplifiées
(Douglas-Peucker), puis écrites avec la projection pour que le lecteur place villes, flèches
et zones données en [longitude, latitude].

Fichiers téléchargés une fois dans .cache/diaporamas/natural-earth/ (1:50 000 000).

Cartes de lieu (spec 12, « Cartes de lieu et citations en surimpression ») : le médaillon du
lecteur reprend ces fonds avec un cadre adapté au lieu (`fond` d'un lieu) : `france` (France
seule, aussi utilisé par les épisodes), `voisins` (France et pays voisins : Fleurus, Mayence,
Turin, Arcole, Campo-Formio), `europe` (Europe et Méditerranée, France repérée : Égypte,
Moscou, Algérie), `monde` (Amériques et Afrique de l'Ouest comprises : Saint-Domingue, Gorée,
Guyane, Sainte-Hélène). La France est toujours dessinée en plus soutenu : on voit où est le lieu par rapport
à elle.

Plans de Paris d'époque (`--plans`, ou sans argument : tout) : pour un lieu de Paris
(`fond: paris`), le médaillon montre un plan du domaine public de la période (`PLANS`), en
gris, zoomé sur le lieu. Le plan est téléchargé depuis Commons (licence contrôlée), recadré
sur la ville, réduit (2 000 px de large), désaturé, papier blanchi (niveaux), puis écrit en
WebP dans public/diaporamas/fonds/<nom>.webp ; ses métadonnées et son calage vont dans
src/data/diaporamas/plans/<nom>.json.

Calage (géoréférencement) : quelques monuments sont repérés à la main sur l'original (pixels,
mesurés sur des agrandissements quadrillés) et associés à leurs coordonnées (Wikidata, P625 ;
pour l'Observatoire, l'intersection de la méridienne de Paris, 2°20′14″ E, et de sa
perpendiculaire, 48°50′11″ N, tracées sur le plan). Une transformation affine
(lon, lat) → (x, y) est ajustée par moindres carrés sur ces points ; les écarts résiduels
sont affichés et notés dans le JSON. Plan de Verniquet (1790) : 9 points, échelle ~1,47 m par
pixel de l'original, écart quadratique moyen ~14 m, 30 m au plus (Observatoire).
"""
import json, math, sys, time
from pathlib import Path

import commun as c

SOURCE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
FICHIERS = {'terres': 'ne_50m_land.geojson', 'pays': 'ne_50m_admin_0_countries.geojson',
            'fleuves': 'ne_50m_rivers_lake_centerlines.geojson'}
FONDS = {
    # Cadre [lon0, lat0, lon1, lat1] ; échelle : unités SVG par degré de latitude.
    'france': {'cadre': [-5.6, 41.2, 10.2, 51.6], 'echelle': 100, 'tolerance': 1.1,
               'fleuves': ['Loire', 'Rhône', 'Seine', 'Garonne', 'Rhine']},
    # Médaillons des cartes de lieu (le cadre `france` sert aussi).
    'voisins': {'cadre': [-6.5, 40.4, 17.5, 55.4], 'echelle': 44, 'tolerance': 1.0,
                'fleuves': ['Rhine', 'Rhône', 'Seine', 'Loire', 'Po']},
    'europe': {'cadre': [-12.0, 26.0, 42.0, 60.5], 'echelle': 20, 'tolerance': 1.0, 'fleuves': []},
    # Sud à -20° (2026-10-09) : Sainte-Hélène (-15,9°), qui revient après 1815 (retour des Cendres, 1840).
    'monde': {'cadre': [-100.0, -20.0, 50.0, 64.0], 'echelle': 6, 'tolerance': 0.9, 'fleuves': []},
    # Carte de l'empire colonial (spec 12, « Les colonies au fil du récit », 2026-10-12) : le monde de
    # Tahiti à la Nouvelle-Calédonie, commun à toutes les périodes ; chaque carte y prend son `cadre`.
    # Largeur ~2 000 unités (libellés du lecteur à ~3 % de la largeur d'une vue) ; coordonnées au dixième
    # (`decimales`), une tolérance fine et les petites îles gardées (`aire_min`) pour les zooms.
    # `metropole` : le contour « france » se limite à l'Europe (sans les départements d'outre-mer actuels).
    'empire': {'cadre': [-160.0, -48.0, 180.0, 66.0], 'echelle': 6, 'tolerance': 0.8, 'fleuves': [],
               'decimales': 1, 'aire_min': 2, 'metropole': True},
}

# Plans de Paris d'époque (domaine public, Commons) et leur calage : points
# (nom, x, y en pixels de l'original, latitude, longitude). `slugs` : périodes qui les emploient.
PLANS = {
    'paris-1790': {
        'commons': 'File:1790 Plan de Verniquet.jpg',
        'titre': 'Plan de la ville de Paris avec sa nouvelle enceinte',
        'auteur': 'Edme Verniquet',
        'date': '1790 (levé de 1785-1791 ; fac-similé)',
        'credit': 'Plan de Verniquet, 1790',
        'slugs': ['prologue', 'revolution', 'consulat-empire', 'restauration'],
        # Partie gardée (pixels de l'original : la ville, sans les tables ni le titre) et largeur servie.
        'recadrage': [100, 1050, 5800, 4450], 'largeur': 2000, 'qualite': 55,
        # Pixels relevés sur l'original (6 179 × 4 849), plan orienté sur la méridienne de Paris.
        'points': [
            ('Observatoire (méridienne × perpendiculaire)', 2700, 4018, 48.836389, 2.337229),
            ('Notre-Dame (milieu de l’édifice)', 3372, 2756, 48.85300, 2.34980),
            ('Dôme des Invalides', 1503, 2606, 48.85500, 2.31250),
            ('Place Vendôme (statue)', 2346, 1670, 48.86750, 2.32944),
            ('Place des Victoires (statue)', 2932, 1798, 48.86583, 2.34111),
            ('Place Royale, auj. des Vosges (statue)', 4145, 2558, 48.85556, 2.36556),
            ('Sainte-Geneviève, auj. Panthéon', 3182, 3270, 48.84620, 2.34611),
            ('Saint-Sulpice', 2622, 2914, 48.85100, 2.33492),
            ('Chapelle de la Salpêtrière', 4070, 3815, 48.83888, 2.36413),
        ],
    },
    # Monarchie de Juillet et Deuxième République (ajout du 2026-10-11). La Restauration, déjà publiée,
    # reste sur Verniquet. Plan orienté au nord, ~1,21 m par pixel de l'original (8 250 × 6 266).
    'paris-1838': {
        'commons': 'File:Ambroise Tardieu, Plan de Paris en 1838 avec le tracé de ses anciennes enceintes, 1838 - Gallica.jpg',
        'titre': 'Plan de Paris en 1838 avec le tracé de ses anciennes enceintes',
        'auteur': 'Ambroise Tardieu',
        'date': '1838',
        'credit': 'Plan de Tardieu, 1838',
        'slugs': ['monarchie-de-juillet', 'deuxieme-republique', 'second-empire'],
        # La ville dans le mur des Fermiers généraux, de Passy à la barrière du Trône (le titre, en
        # haut à droite, et un bout des renvois, en bas à gauche, restent hors les murs).
        'recadrage': [450, 485, 7830, 5350], 'largeur': 2000, 'qualite': 55,
        'points': [
            ('Observatoire (milieu de l’édifice)', 3755, 4973, 48.836389, 2.337229),
            ('Notre-Dame (milieu de l’édifice)', 4550, 3452, 48.85300, 2.34980),
            ('Dôme des Invalides', 2300, 3275, 48.85500, 2.31250),
            ('Colonne Vendôme', 3314, 2131, 48.86747, 2.32941),
            ('Place des Victoires (centre)', 4020, 2286, 48.86583, 2.34111),
            ('Place Royale, auj. des Vosges (statue)', 5489, 3206, 48.85556, 2.36556),
            ('Chapelle de la Salpêtrière', 5410, 4743, 48.83888, 2.36413),
            ('Rotonde de la Villette', 5733, 666, 48.88333, 2.36944),
            ('Place du Trône, auj. de la Nation (centre)', 7316, 3877, 48.84833, 2.39583),
            ('Rotonde de Chartres (parc Monceau)', 2091, 951, 48.88025, 2.30908),
        ],
    },
}


def charger(nom: str) -> dict:
    dossier = c.CACHE / 'natural-earth'
    f = dossier / FICHIERS[nom]
    if not f.exists():
        dossier.mkdir(parents=True, exist_ok=True)
        f.write_bytes(c.http_get(SOURCE + FICHIERS[nom]))
    return json.loads(f.read_text())


def anneaux(geom: dict) -> list[list[list[float]]]:
    if geom['type'] == 'Polygon':
        return geom['coordinates']
    if geom['type'] == 'MultiPolygon':
        return [r for p in geom['coordinates'] for r in p]
    return []


def lignes(geom: dict) -> list[list[list[float]]]:
    if geom['type'] == 'LineString':
        return [geom['coordinates']]
    if geom['type'] == 'MultiLineString':
        return geom['coordinates']
    return []


def decouper(anneau, cadre):
    """Sutherland-Hodgman : l'anneau (lon, lat) découpé au rectangle du cadre."""
    x0, y0, x1, y1 = cadre
    bords = [(lambda p: p[0] >= x0, lambda a, b: inter_x(a, b, x0)),
             (lambda p: p[0] <= x1, lambda a, b: inter_x(a, b, x1)),
             (lambda p: p[1] >= y0, lambda a, b: inter_y(a, b, y0)),
             (lambda p: p[1] <= y1, lambda a, b: inter_y(a, b, y1))]
    pts = anneau
    for dedans, inter in bords:
        if not pts:
            break
        sortie = []
        for k, p in enumerate(pts):
            q = pts[k - 1]
            if dedans(p):
                if not dedans(q):
                    sortie.append(inter(q, p))
                sortie.append(p)
            elif dedans(q):
                sortie.append(inter(q, p))
        pts = sortie
    return pts


def inter_x(a, b, x):
    t = (x - a[0]) / (b[0] - a[0])
    return [x, a[1] + t * (b[1] - a[1])]


def inter_y(a, b, y):
    t = (y - a[1]) / (b[1] - a[1])
    return [a[0] + t * (b[0] - a[0]), y]


def simplifier(pts, tol):
    """Douglas-Peucker (points déjà projetés)."""
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1e-9
    pire, k = 0.0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        dist = abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / n if n > 1e-9 else math.hypot(p[0] - a[0], p[1] - a[1])
        if dist > pire:
            pire, k = dist, i
    if pire <= tol:
        return [a, b]
    return simplifier(pts[:k + 1], tol)[:-1] + simplifier(pts[k:], tol)


def projeter_fn(fond):
    lon0, lat0, lon1, lat1 = fond['cadre']
    k = fond['echelle']
    cx = math.cos(math.radians((lat0 + lat1) / 2))
    return (lambda p: [(p[0] - lon0) * cx * k, (lat1 - p[1]) * k]), round((lon1 - lon0) * cx * k), round((lat1 - lat0) * k), cx


def chemin(pts, ferme=True, dec=0):
    if len(pts) < 2:
        return ''
    s = 'M' + ' '.join(f'{p[0]:.{dec}f},{p[1]:.{dec}f}' for p in pts)
    return s + ('Z' if ferme else '')


def fabriquer(nom: str, fond: dict) -> dict:
    proj, largeur, hauteur, cx = projeter_fn(fond)
    tol = fond['tolerance']
    cadre = fond['cadre']
    dec, aire_min = fond.get('decimales', 0), fond.get('aire_min', 40)

    def polygones(geoms, europe=False):
        sortie = []
        for g in geoms:
            for r in anneaux(g):
                if europe and not (-6 < r[0][0] < 10 and 41 < r[0][1] < 52):
                    continue
                pts = decouper(r, cadre)
                if len(pts) < 3:
                    continue
                pts = simplifier([proj(p) for p in pts] + [proj(pts[0])], tol)
                # Îlots minuscules ignorés.
                aire = abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))) / 2
                if len(pts) >= 4 and aire > aire_min:
                    sortie.append(chemin(pts[:-1], dec=dec))
        return ''.join(sortie)

    terres = polygones([f['geometry'] for f in charger('terres')['features']])
    pays = charger('pays')['features']
    france = polygones([f['geometry'] for f in pays if f['properties'].get('ADM0_A3') == 'FRA'],
                       europe=fond.get('metropole', False))
    fleuves = []
    for f in charger('fleuves')['features']:
        if f['properties'].get('name') in fond['fleuves']:
            for l in lignes(f['geometry']):
                pts = [proj(p) for p in l if cadre[0] <= p[0] <= cadre[2] and cadre[1] <= p[1] <= cadre[3]]
                if len(pts) >= 2:
                    fleuves.append(chemin(simplifier(pts, tol), ferme=False))
    return {
        'nom': nom,
        'licence': 'Domaine public (Natural Earth)',
        'source': 'Natural Earth, 1:50 000 000 (terres, pays, fleuves), https://www.naturalearthdata.com/',
        'note': 'Contour actuel de la France, simplifié ; il diffère peu de celui de 1793.',
        'projection': {'cadre': cadre, 'echelle': fond['echelle'], 'cx': round(cx, 6)},
        'largeur': largeur, 'hauteur': hauteur,
        'terres': terres, 'france': france, 'fleuves': fleuves,
    }


def resoudre3(m, v):
    """Système 3 × 3 (Cramer)."""
    det = lambda a: (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                     + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    d = det(m)
    return [det([[v[i] if j == k else m[i][j] for j in range(3)] for i in range(3)]) / d for k in range(3)]


def caler(points):
    """Affine (lon, lat, 1) → x et → y par moindres carrés (équations normales)."""
    A = [[p[4], p[3], 1.0] for p in points]
    ata = [[sum(a[i] * a[j] for a in A) for j in range(3)] for i in range(3)]
    cx = resoudre3(ata, [sum(a[i] * p[1] for a, p in zip(A, points)) for i in range(3)])
    cy = resoudre3(ata, [sum(a[i] * p[2] for a, p in zip(A, points)) for i in range(3)])
    return cx, cy


def plan(nom: str, p: dict) -> dict:
    """Plan d'époque : téléchargement (licence contrôlée), calage, WebP gris, métadonnées."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    info = c.infos_fichiers([p['commons']])[p['commons']]
    if info.get('manquant'):
        raise SystemExit(f"{p['commons']} : introuvable sur Commons")
    libre, licence = c.licence_libre(info)
    if not libre:
        raise SystemExit(f"{p['commons']} : licence refusée ({licence})")
    dossier = c.CACHE / 'plans'
    dossier.mkdir(parents=True, exist_ok=True)
    original = dossier / f'{nom}{Path(info["url"]).suffix.lower()}'
    if not original.exists():
        original.write_bytes(c.http_get(info['url']))
        time.sleep(1)
    im = Image.open(original).convert('L')
    cx, cy = caler(p['points'])
    m_x = 111320 * math.cos(math.radians(48.85)) / math.hypot(cx[0], cy[0])  # mètres par pixel
    m_y = 111200 / math.hypot(cx[1], cy[1])
    residus = []
    for q in p['points']:
        ex = cx[0] * q[4] + cx[1] * q[3] + cx[2] - q[1]
        ey = cy[0] * q[4] + cy[1] * q[3] + cy[2] - q[2]
        residus.append((q[0], round(math.hypot(ex * m_x, ey * m_y))))
    rms = math.sqrt(sum(r * r for _, r in residus) / len(residus))
    x0, y0, x1, y1 = p['recadrage']
    W = p['largeur']
    H = round((y1 - y0) * W / (x1 - x0))
    r = im.crop((x0, y0, x1, y1)).resize((W, H), Image.LANCZOS)
    # Niveaux : le papier (gris ~205) devient blanc cassé, l'encre est un peu soutenue.
    lut = [246 if v >= 198 else round(160 + (v - 178) * 86 / 20) if v >= 178 else round(v * 160 / 178) for v in range(256)]
    sortie = c.PUBLIC / 'fonds' / f'{nom}.webp'
    sortie.parent.mkdir(parents=True, exist_ok=True)
    r.point(lut).save(sortie, 'WEBP', quality=p['qualite'], method=6)
    # (lon, lat) → fractions (u, v) de l'image servie.
    su, sv = 1 / (x1 - x0), 1 / (y1 - y0)
    return {
        'nom': nom, 'fichier': f'fonds/{nom}.webp', 'largeur': W, 'hauteur': H,
        'titre': p['titre'], 'auteur': p['auteur'], 'date': p['date'], 'credit': p['credit'],
        'commons': info['titre_fichier'], 'licence': 'Domaine public', 'licence_relevee': licence,
        'slugs': p['slugs'],
        'calage': {
            'u': [cx[0] * su, cx[1] * su, (cx[2] - x0) * su], 'v': [cy[0] * sv, cy[1] * sv, (cy[2] - y0) * sv],
            'metres_par_pixel': round(W and (m_x + m_y) / 2 * (x1 - x0) / W, 2),
            'ecart_moyen_m': round(rms), 'points': [[q[0], q[1], q[2], q[3], q[4], e] for q, (_, e) in zip(p['points'], residus)],
        },
    }


def main() -> int:
    dossier = c.DONNEES / 'fonds'
    dossier.mkdir(parents=True, exist_ok=True)
    seulement_plans = '--plans' in sys.argv
    # --fond NOM… : ces fonds seulement (ni plans ni autres fonds refaits).
    fonds = sys.argv[sys.argv.index('--fond') + 1:] if '--fond' in sys.argv else None
    for nom, p in ({} if fonds else PLANS).items():
        d = plan(nom, p)
        f = c.DONNEES / 'plans' / f'{nom}.json'
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
        w = c.PUBLIC / d['fichier']
        print(f"{w.relative_to(c.RACINE)} : {d['largeur']}×{d['hauteur']}, {w.stat().st_size // 1024} Ko ; "
              f"calage : écart moyen {d['calage']['ecart_moyen_m']} m, "
              f"au plus {max(q[5] for q in d['calage']['points'])} m ({len(p['points'])} points)")
    if seulement_plans:
        return 0
    for nom, fond in FONDS.items():
        if fonds and nom not in fonds:
            continue
        d = fabriquer(nom, fond)
        f = dossier / f'{nom}.json'
        f.write_text(json.dumps(d, ensure_ascii=False) + '\n')
        print(f'{f.relative_to(c.RACINE)} : {d["largeur"]}×{d["hauteur"]}, {f.stat().st_size // 1024} Ko')
    return 0


if __name__ == '__main__':
    sys.exit(main())
