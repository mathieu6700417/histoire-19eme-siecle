#!/usr/bin/env python3
"""Vignettes dessinées (spec 17, essai 5) : du dessin généré au « trait qui se trace ».
Repris de l'essai (.cache/diaporamas/essais-colab/vignettes/tracer.py). Tourne dans le venv
`.cache/venv-vignettes` (OpenCV, scikit-image) ; appelé par `vignettes.py tracer`.

    .cache/venv-vignettes/bin/python scripts/diaporamas/vignettes_trace.py SOURCE.png SORTIE_SANS_EXTENSION [--plein]

`--plein` (dessin traversant, révision du 2026-10-14) : ni recadrage ni fondu des bords (le dessin
reste calé sur l'écran : le lecteur le pose centré sous l'image), tracés à `TRACE_PLEIN` px de large
(chaque marge n'en fait qu'un sixième environ). Sans lui : vignette d'une marge (pilote, essai 5).

Pour un dessin (PNG du modèle) :
  1. encre : niveaux de gris aplanis (papier retiré par fermeture morphologique), petites taches et
     filets de cadre résiduels effacés, bords fondus, recadrage sur l'encre ; sortie
     `<sortie>-encre.webp` à la résolution du dessin : RVB noir, alpha = encre (avec son
     anticrénelage). Le lecteur la teinte : le rendu final EST le dessin généré, aucun trait redessiné ;
  2. tracés : l'encre ramenée à `TRACE` px de large, binarisée, squelettisée, découpée en polylignes
     « de plume » (on traverse les carrefours), chacune avec son épaisseur (transformée de distance) ;
     longs contours d'abord (chaînés au plus proche en partant du haut), hachures courtes ensuite
     (bandes de haut en bas), trois « plumes » jouées ensemble dans chaque groupe ;
  3. `<sortie>.json`, compact : {"l", "h" (px des tracés), "d" (durée, s), "t": [[épaisseur × 10,
     début (cs), fin (cs), contour (1) ou hachure (0), x0, y0, dx1, dy1, …], …]} (points entiers,
     en écarts au précédent). Le lecteur découvre l'encre en peignant ces tracés dans un masque.
Sortie standard : une ligne JSON {encre: [l, h], traces: [l, h], n, contours, hachures, octets}.
"""
import json, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize

DUREE = 4.2            # s : durée totale du tracé (constante VIGNETTE_DUREE du lecteur, à titre indicatif)
PART_CONTOURS = 0.58   # part de la durée pour les longs contours
TRACE = 360            # px : largeur des tracés (le masque est peint à cette échelle, puis agrandi)
TRACE_PLEIN = 1000     # px : de même pour un dessin traversant
LONG = 38 * TRACE / 640  # px : au-delà, un tracé est un contour (38 px à 640 px de large dans l'essai)
FONDU = 0.06           # part du bord du dessin recadré où l'encre s'éteint
PLUMES = 3


def encre(chemin: Path) -> np.ndarray:
    """Alpha de l'encre (0 papier … 1 encre pleine), recadré, à la résolution du dessin."""
    g = cv2.imread(str(chemin), cv2.IMREAD_GRAYSCALE).astype(np.float32)
    # Papier : fermeture morphologique (efface le trait) puis flou ; on divise pour l'aplanir.
    k = max(15, round(21 * g.shape[1] / 640)) | 1
    papier = cv2.morphologyEx(g, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    papier = cv2.GaussianBlur(papier, (0, 0), 9)
    n = np.clip(g / np.maximum(papier, 1) * 255, 0, 255)
    a = np.clip((232 - n) / (232 - 70), 0, 1)
    binaire = (a > 0.38).astype(np.uint8)
    # Taches : composantes de moins de 10 px retirées (et leur encre avec).
    nb, lab, st, _ = cv2.connectedComponentsWithStats(binaire, connectivity=8)
    garde = np.zeros(nb, bool); garde[1:] = st[1:, cv2.CC_STAT_AREA] >= 10
    binaire = garde[lab].astype(np.uint8)
    a = a * cv2.dilate(binaire, np.ones((3, 3), np.uint8))
    # Cadre résiduel : une rangée ou une colonne des 15 % extérieurs presque toute encrée est un filet
    # de cadre (la consigne dit « sans bordure ») ; effacée, avec deux pixels de part et d'autre.
    hh, ww = binaire.shape
    for axe, taille in ((1, hh), (0, ww)):
        part = binaire.mean(axis=axe)
        for i in np.nonzero(part > 0.45)[0]:
            if i < 0.15 * taille or i > 0.85 * taille:
                sl = slice(max(0, i - 2), i + 3)
                if axe == 1:
                    binaire[sl, :] = 0; a[sl, :] = 0
                else:
                    binaire[:, sl] = 0; a[:, sl] = 0
    # Bords fondus : l'encre s'éteint dans les 7 % extérieurs (pas de bord rectangulaire).
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.minimum.reduce([xx / W, (W - 1 - xx) / W, yy / H, (H - 1 - yy) / H])
    a = a * np.clip(d / 0.07, 0, 1) ** 1.2
    # Recadrage sur l'encre (marge de 3 %) : la vignette occupe toute sa place dans la marge.
    ys, xs = np.nonzero(a > 0.2)
    if len(xs):
        m = round(0.03 * W)
        a = a[max(0, ys.min() - m):min(H, ys.max() + m + 1), max(0, xs.min() - m):min(W, xs.max() + m + 1)]
    # Fondu des bords du dessin recadré : une composition à bord carré s'éteint au lieu de former
    # un rectangle dans la marge.
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum.reduce([xx / w, (w - 1 - xx) / w, yy / h, (h - 1 - yy) / h])
    return np.ascontiguousarray(a * np.clip(d / FONDU, 0, 1) ** 0.8)


def encre_pleine(chemin: Path) -> np.ndarray:
    """Alpha de l'encre d'un dessin traversant : papier aplani, taches retirées, sans recadrage ni
    fondu des bords (la position du dessin sur l'écran en dépend)."""
    g = cv2.imread(str(chemin), cv2.IMREAD_GRAYSCALE).astype(np.float32)
    k = max(15, round(21 * g.shape[1] / 640)) | 1
    papier = cv2.GaussianBlur(cv2.morphologyEx(g, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))), (0, 0), 9)
    n = np.clip(g / np.maximum(papier, 1) * 255, 0, 255)
    a = np.clip((232 - n) / (232 - 70), 0, 1)
    b = (a > 0.38).astype(np.uint8)
    nb, lab, st, _ = cv2.connectedComponentsWithStats(b, connectivity=8)
    garde = np.zeros(nb, bool); garde[1:] = st[1:, cv2.CC_STAT_AREA] >= 10
    return np.ascontiguousarray(a * cv2.dilate(garde[lab].astype(np.uint8), np.ones((3, 3), np.uint8)))


VOISINS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def polylignes(sq: np.ndarray):
    """Squelette → polylignes « de plume » : on va toujours au voisin libre le plus dans l'axe (on
    traverse les carrefours) ; bloqué, on lève la plume et on repart d'une branche laissée."""
    pts = set(zip(*np.nonzero(sq)))

    def vois(p):
        return [(p[0] + dy, p[1] + dx) for dy, dx in VOISINS if (p[0] + dy, p[1] + dx) in pts]
    deg = {p: len(vois(p)) for p in pts}
    libre = set(pts)
    lignes = []
    for d0 in sorted(pts, key=lambda p: (deg[p] != 1, p[0], p[1])):   # extrémités d'abord, de haut en bas
        if d0 not in libre:
            continue
        pile = [d0]; libre.discard(d0)
        while pile:
            a = pile.pop()
            ligne = [a]; prec = None
            while True:
                cands = [q for q in vois(ligne[-1]) if q in libre]
                if not cands:
                    break
                if prec is not None:
                    vy, vx = ligne[-1][0] - prec[0], ligne[-1][1] - prec[1]
                    cands.sort(key=lambda q: -((q[0] - ligne[-1][0]) * vy + (q[1] - ligne[-1][1]) * vx))
                pile.extend(ligne[-1] for _ in cands[1:])   # branches à reprendre plus tard
                q = cands[0]
                libre.discard(q); prec = ligne[-1]; ligne.append(q)
            if len(ligne) > 1:
                lignes.append(ligne)
            elif deg[a] == 0:
                lignes.append([a, a])
    return lignes


def simplifier(ligne, tol=0.8):
    c = np.array([[x, y] for y, x in ligne], np.float32).reshape(-1, 1, 2)
    return cv2.approxPolyDP(c, tol, False).reshape(-1, 2)


def longueur(p):
    return float(np.sum(np.hypot(*np.diff(p, axis=0).T))) if len(p) > 1 else 1.0


def chainer(traits, depart):
    """Ordre « de plume » : le trait suivant est le plus proche de la fin du précédent (retourné s'il
    est plus proche par sa fin)."""
    if not traits:
        return []
    pos = np.array(depart, np.float32)
    debuts = np.array([t['p'][0] for t in traits], np.float32); fins = np.array([t['p'][-1] for t in traits], np.float32)
    libre = np.ones(len(traits), bool); ordre = []
    while libre.any():
        idx = np.nonzero(libre)[0]
        d1 = np.hypot(*(debuts[idx] - pos).T); d2 = np.hypot(*(fins[idx] - pos).T)
        j1, j2 = d1.argmin(), d2.argmin()
        i, inverse = (idx[j1], False) if d1[j1] <= d2[j2] else (idx[j2], True)
        t = traits[i]
        if inverse:
            t['p'] = t['p'][::-1]
        ordre.append(t); libre[i] = False; pos = np.array(t['p'][-1], np.float32)
    return ordre


def traiter(src: Path, sortie: Path) -> dict:
    a = encre(src)
    H, W = a.shape
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., 3] = np.round(a * 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(f'{sortie}-encre.webp', 'WEBP', quality=82, alpha_quality=60, method=6)   # alpha 60 : 35 % plus léger, écart moyen < 1/255
    # Tracés à TRACE px de large : moins de points, même dessin.
    h = round(H * TRACE / W)
    p = cv2.resize(a, (TRACE, h), interpolation=cv2.INTER_AREA)
    binaire = (p > 0.3).astype(np.uint8)
    sq = skeletonize(binaire > 0)
    dist = cv2.distanceTransform(binaire, cv2.DIST_L2, 3)
    traits = []
    for l in polylignes(sq):
        r = float(np.percentile([dist[y, x] for y, x in l], 90))
        q = simplifier(l)
        if len(q) < 2:
            q = np.array([[l[0][1], l[0][0]], [l[-1][1], l[-1][0]]], np.float32)
        traits.append(dict(p=q.astype(np.float32), r=r, L=longueur(q)))
    longs = chainer([t for t in traits if t['L'] >= LONG], (TRACE / 2, 0))
    courts = [t for t in traits if t['L'] < LONG]
    bandes = [[] for _ in range(8)]
    for t in courts:
        bandes[min(7, int(float(np.mean(t['p'][:, 1])) / h * 8))].append(t)
    hach = []
    for i, b in enumerate(bandes):
        hach += chainer(b, (0 if i % 2 == 0 else TRACE, (i + .5) * h / 8))
    sortie_t = []
    for groupe, debut, duree in ((longs, 0.0, DUREE * PART_CONTOURS),
                                 (hach, DUREE * PART_CONTOURS * 0.88, DUREE * (1 - PART_CONTOURS * 0.88))):
        total = sum(t['L'] for t in groupe) or 1
        cible = total / PLUMES; t0 = debut; acc = 0.0; k = 0
        for t in groupe:
            d = duree * t['L'] / cible
            if acc + t['L'] > cible * (k + 1) and k < PLUMES - 1:
                k += 1; t0 = debut
            pts = np.round(t['p']).astype(int)
            plat = [int(pts[0][0]), int(pts[0][1])]
            for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
                if (x1, y1) != (x0, y0):
                    plat += [int(x1 - x0), int(y1 - y0)]
            if len(plat) == 2:
                plat += [0, 0]
            sortie_t.append([round(10 * max(2.2, 2 * t['r'] + 1.6)), round(100 * t0), round(100 * (t0 + d)), int(groupe is longs)] + plat)
            t0 += d; acc += t['L']
    texte = json.dumps(dict(l=TRACE, h=h, d=DUREE, t=sortie_t), separators=(',', ':'))
    Path(f'{sortie}.json').write_text(texte)
    return dict(encre=[W, H], traces=[TRACE, h], n=len(sortie_t), contours=len(longs), hachures=len(hach), octets=len(texte))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--plein']
    if len(args) != 2:
        raise SystemExit(__doc__)
    if '--plein' in sys.argv:
        encre, TRACE, LONG = encre_pleine, TRACE_PLEIN, 38 * TRACE_PLEIN / 640
    print(json.dumps(traiter(Path(args[0]), Path(args[1]))))
