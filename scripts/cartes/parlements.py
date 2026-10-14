"""Fond de la carte des parlements et conseils souverains en 1789 (spec 21).

Usage (depuis la racine du projet) :
    python3 scripts/cartes/parlements.py

Dépendance : shapely (`pip install shapely`), pour fusionner les départements et découper.

Source : Natural Earth, 1:10 000 000 (domaine public, https://www.naturalearthdata.com/) :
départements français (admin 1), pays (admin 0), grands fleuves. Fichiers téléchargés une fois
dans .cache/cartes/.

Méthode (approximation assumée, signalée sur la carte) :
- chaque ressort de parlement ou de conseil souverain est reconstitué en réunissant des
  départements actuels (`RESSORTS`) ; les vrais ressorts ne suivaient pas ces limites
  (Mâconnais, Barrois, Sedan, Angoumois… sont rangés avec leurs voisins) ;
- le contour de la France est le contour actuel ; la Savoie (Savoie, Haute-Savoie) et le comté
  de Nice (Alpes-Maritimes à l'est du Var, coupées ici au méridien 7,19° E) sont marqués hors du
  royaume ; Avignon et le Comtat Venaissin (pontificaux), Mulhouse et Montbéliard, trop petits,
  sont seulement signalés par un point dans la carte (données de src/data/xixe/parlements.ts) ;
- projection équirectangulaire, longitudes corrigées à la latitude moyenne, simplification
  Douglas-Peucker. La projection est écrite dans le JSON : le composant CarteFrance y place
  les villes d'après leurs coordonnées réelles.

Sortie : src/data/xixe/cartes/parlements-1789.json
"""
import json
import math
import urllib.request
from pathlib import Path

from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union

RACINE = Path(__file__).resolve().parents[2]
CACHE = RACINE / '.cache' / 'cartes'
SORTIE = RACINE / 'src' / 'data' / 'xixe' / 'cartes' / 'parlements-1789.json'
SOURCE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
FICHIERS = {
    'departements': 'ne_10m_admin_1_states_provinces.geojson',
    'pays': 'ne_10m_admin_0_countries.geojson',
    'fleuves': 'ne_10m_rivers_lake_centerlines.geojson',
}

# Cadre [lon0, lat0, lon1, lat1] et échelle (unités SVG par degré de latitude).
CADRE = (-5.4, 41.25, 9.9, 51.25)
ECHELLE = 58
TOLERANCE = 0.55  # en unités SVG (1 unité ≈ 1,9 km)
FLEUVES = ['Seine', 'Loire', 'Rhône', 'Garonne', 'Rhine', 'Dordogne']
VAR = 7.19  # méridien de l'embouchure du Var (limite approximative du comté de Nice)

# Ressorts approximés par départements actuels (codes INSEE).
RESSORTS = {
    'paris': ['75', '77', '78', '91', '92', '93', '94', '95', '02', '60', '80', '62', '08', '51', '10',
              '52', '89', '58', '45', '41', '28', '18', '36', '37', '72', '53', '49', '85', '79', '86',
              '16', '23', '03', '63', '15', '42', '69'],
    'rouen': ['76', '27', '14', '50', '61'],
    'rennes': ['35', '22', '29', '56', '44'],
    'bordeaux': ['33', '24', '47', '40', '17', '87', '19'],
    'toulouse': ['31', '09', '11', '34', '30', '48', '07', '43', '12', '46', '81', '82', '32', '65'],
    'pau': ['64'],
    'aix': ['13', '83', '04', '84', '06-ouest'],
    'grenoble': ['38', '26', '05'],
    'dijon': ['21', '71', '01'],
    'besancon': ['25', '39', '70'],
    'metz': ['57'],
    'nancy': ['54', '88', '55'],
    'douai': ['59'],
    'colmar': ['67', '68', '90'],
    'perpignan': ['66'],
    'bastia': ['2A', '2B'],
    'hors': ['73', '74', '06-est'],
}


def charger(cle: str) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    chemin = CACHE / FICHIERS[cle]
    if not chemin.exists():
        print('téléchargement', FICHIERS[cle])
        urllib.request.urlretrieve(SOURCE + FICHIERS[cle], chemin)
    return json.loads(chemin.read_text())


CX = math.cos(math.radians((CADRE[1] + CADRE[3]) / 2))
LARGEUR = round((CADRE[2] - CADRE[0]) * ECHELLE * CX)
HAUTEUR = round((CADRE[3] - CADRE[1]) * ECHELLE)


def proj(lon, lat):
    return ((lon - CADRE[0]) * ECHELLE * CX, (CADRE[3] - lat) * ECHELLE)


def simplifier(pts, tol):
    """Douglas-Peucker (points projetés)."""
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1e-9
    dmax, k = 0.0, 0
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / n if math.hypot(dx, dy) else math.hypot(x0 - x1, y0 - y1)
        if d > dmax:
            dmax, k = d, i
    if dmax <= tol:
        return [pts[0], pts[-1]]
    return simplifier(pts[:k + 1], tol)[:-1] + simplifier(pts[k:], tol)


def anneaux(geom):
    """Anneaux extérieurs et intérieurs d'un (Multi)Polygon shapely."""
    polys = [geom] if geom.geom_type == 'Polygon' else list(getattr(geom, 'geoms', []))
    for p in polys:
        if p.geom_type != 'Polygon' or p.is_empty:
            continue
        yield list(p.exterior.coords)
        for i in p.interiors:
            yield list(i.coords)


def chemin_poly(geom, aire_min=4.0) -> str:
    morceaux = []
    for anneau in anneaux(geom):
        pts = simplifier([proj(x, y) for x, y in anneau], TOLERANCE)
        if len(pts) < 4:
            continue
        aire = abs(sum(pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1] for i in range(len(pts) - 1))) / 2
        if aire < aire_min:
            continue
        morceaux.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts[:-1]) + 'Z')
    return ''.join(morceaux)


def chemin_ligne(geom) -> str:
    lignes = [geom] if geom.geom_type == 'LineString' else list(getattr(geom, 'geoms', []))
    morceaux = []
    for l in lignes:
        if l.geom_type != 'LineString' or l.is_empty:
            continue
        pts = simplifier([proj(x, y) for x, y in l.coords], TOLERANCE)
        if len(pts) >= 2:
            morceaux.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts))
    return ''.join(morceaux)


def main() -> int:
    cadre = box(*CADRE)
    deps = {}
    for f in charger('departements')['features']:
        p = f['properties']
        if p.get('adm0_a3') != 'FRA' or p.get('type') != 'Metropolitan département':
            continue
        code = (p.get('iso_3166_2') or '').removeprefix('FR-')
        deps[code] = shape(f['geometry']).buffer(0)
    am = deps.pop('06')
    deps['06-ouest'] = am.intersection(box(0, 40, VAR, 50))
    deps['06-est'] = am.intersection(box(VAR, 40, 12, 50))

    vus = [c for codes in RESSORTS.values() for c in codes]
    manquants = sorted(set(deps) - set(vus))
    inconnus = sorted(set(vus) - set(deps))
    if manquants or inconnus:
        raise SystemExit(f'départements non rangés : {manquants} ; inconnus : {inconnus}')

    zones = {}
    for nom, codes in RESSORTS.items():
        # Petit tampon aller-retour : referme les interstices entre départements voisins.
        union = unary_union([deps[c] for c in codes]).buffer(0.002).buffer(-0.002)
        zones[nom] = chemin_poly(union.intersection(cadre))

    france = unary_union(list(deps.values())).buffer(0.002).buffer(-0.002)
    voisins = []
    for f in charger('pays')['features']:
        if f['properties'].get('ADM0_A3') == 'FRA':
            continue
        g = shape(f['geometry']).buffer(0)
        if g.intersects(cadre):
            voisins.append(g.intersection(cadre))
    terres_voisines = unary_union(voisins).difference(france)

    fleuves = []
    for f in charger('fleuves')['features']:
        nom = f['properties'].get('name') or ''
        if nom in FLEUVES and f['geometry']:
            g = shape(f['geometry'])
            if g.intersects(cadre):
                fleuves.append(chemin_ligne(g.intersection(cadre)))

    donnees = {
        'nom': 'parlements-1789',
        'licence': 'Domaine public (Natural Earth)',
        'source': 'Natural Earth, 1:10 000 000 (départements, pays, fleuves), https://www.naturalearthdata.com/',
        'note': ("Ressorts reconstitués par regroupement de départements actuels : approximation. "
                 "Contour actuel de la France ; Savoie et comté de Nice (coupé au Var) hors du royaume en 1789."),
        'projection': {'cadre': list(CADRE), 'echelle': ECHELLE, 'cx': round(CX, 6)},
        'largeur': LARGEUR,
        'hauteur': HAUTEUR,
        'voisins': chemin_poly(terres_voisines, aire_min=8),
        'france': chemin_poly(france),
        'fleuves': ''.join(fleuves),
        'zones': zones,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(donnees, ensure_ascii=False) + '\n')
    print(f'{SORTIE.relative_to(RACINE)} : {SORTIE.stat().st_size // 1024} Ko, {LARGEUR} × {HAUTEUR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
