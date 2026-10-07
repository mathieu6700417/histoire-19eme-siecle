"""Fonds de carte des épisodes (spec 12, « Lectures d'époque et épisodes »).

Usage :
    python3 scripts/diaporamas/carte.py            # (re)fait src/data/diaporamas/fonds/*.json

Les cartes animées des épisodes sont dessinées en SVG par le lecteur, sur un fond simplifié
tiré de Natural Earth (domaine public, https://www.naturalearthdata.com/) : terres émergées,
contour de la France (frontières actuelles : elles diffèrent peu de celles de 1793, Savoie et
Nice comprises), grands fleuves. Les données sont projetées (équirectangulaire, échelle des
longitudes corrigée à la latitude moyenne), découpées au cadre et simplifiées
(Douglas-Peucker), puis écrites avec la projection pour que le lecteur place villes, flèches
et zones données en [longitude, latitude].

Fichiers téléchargés une fois dans .cache/diaporamas/natural-earth/ (1:50 000 000).
"""
import json, math, sys
from pathlib import Path

import commun as c

SOURCE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
FICHIERS = {'terres': 'ne_50m_land.geojson', 'pays': 'ne_50m_admin_0_countries.geojson',
            'fleuves': 'ne_50m_rivers_lake_centerlines.geojson'}
FONDS = {
    # Cadre [lon0, lat0, lon1, lat1] ; échelle : unités SVG par degré de latitude.
    'france': {'cadre': [-5.6, 41.2, 10.2, 51.6], 'echelle': 100, 'tolerance': 1.1,
               'fleuves': ['Loire', 'Rhône', 'Seine', 'Garonne', 'Rhine']},
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


def chemin(pts, ferme=True):
    if len(pts) < 2:
        return ''
    s = 'M' + ' '.join(f'{p[0]:.0f},{p[1]:.0f}' for p in pts)
    return s + ('Z' if ferme else '')


def fabriquer(nom: str, fond: dict) -> dict:
    proj, largeur, hauteur, cx = projeter_fn(fond)
    tol = fond['tolerance']
    cadre = fond['cadre']

    def polygones(geoms):
        sortie = []
        for g in geoms:
            for r in anneaux(g):
                pts = decouper(r, cadre)
                if len(pts) < 3:
                    continue
                pts = simplifier([proj(p) for p in pts] + [proj(pts[0])], tol)
                # Îlots minuscules ignorés.
                aire = abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))) / 2
                if len(pts) >= 4 and aire > 40:
                    sortie.append(chemin(pts[:-1]))
        return ''.join(sortie)

    terres = polygones([f['geometry'] for f in charger('terres')['features']])
    pays = charger('pays')['features']
    france = polygones([f['geometry'] for f in pays if f['properties'].get('ADM0_A3') == 'FRA'])
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


def main() -> int:
    dossier = c.DONNEES / 'fonds'
    dossier.mkdir(parents=True, exist_ok=True)
    for nom, fond in FONDS.items():
        d = fabriquer(nom, fond)
        f = dossier / f'{nom}.json'
        f.write_text(json.dumps(d, ensure_ascii=False) + '\n')
        print(f'{f.relative_to(c.RACINE)} : {d["largeur"]}×{d["hauteur"]}, {f.stat().st_size // 1024} Ko')
    return 0


if __name__ == '__main__':
    sys.exit(main())
