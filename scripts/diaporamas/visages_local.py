"""Détection locale et gratuite des visages (remplace l'appel Gemini de camera.py --visages).

Lancé par camera.py dans le venv `.cache/venv-visages` (OpenCV ; le système n'a pas OpenCV) :

    python3 -m venv .cache/venv-visages && .cache/venv-visages/bin/pip install opencv-python-headless numpy
    curl -L -o .cache/modeles-visages/yunet.onnx \\
      https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx

Entrée (stdin) : liste JSON de chemins d'images. Sortie (stdout) : liste JSON, une liste de
rectangles [gauche, haut, droite, bas] (fractions de l'image) par chemin, au format du cache
`visages.json` : du haut du crâne au menton, d'une oreille à l'autre (la boîte de YuNet, front-menton,
est élargie en conséquence ; étalonnage sur le relevé Gemini, 2026-10-09).

Détecteur : YuNet (OpenCV DNN), passé sur l'image entière et sur des tuiles qui se chevauchent
(têtes plus petites), en couleur et en niveaux de gris égalisés (gravures, estampes), puis fusion
par suppression des non-maxima.

Mode portrait (2026-10-09, règle « chaque vue d'un portrait montre le visage entier ») : entrée
`{"portrait": true, "chemins": [...]}` ; pour chaque chemin, le visage le plus probable seul (liste
d'un rectangle, ou vide), cherché avec un seuil bas (SEUIL_PORTRAIT) et sans le filtre des grandes
boîtes : camera.py s'en sert quand le titre ou le registre dit « portrait » et que la passe normale
n'a rien trouvé (gravure pâle, profil).
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

MODELE = Path(__file__).resolve().parents[2] / '.cache' / 'modeles-visages' / 'yunet.onnx'
COTE = 1280            # plus grand côté de l'image entière analysée
SEUIL = 0.45           # score minimal de YuNet
TUILES = 2             # tuiles par côté (avec chevauchement) en plus de l'image entière
HAUT, BAS, LARGE = 0.25, 0.05, 0.25   # élargissement de la boîte YuNet (fractions de sa taille)
H_MIN = 0.02           # hauteur minimale rendue (fraction de l'image), comme la consigne Gemini
SEUIL_PORTRAIT = 0.2    # mode portrait : score minimal du meilleur visage
GRAND, SEUIL_GRAND = 0.10, 0.70   # boîte de plus de 10 % de la hauteur : score exigé plus haut
                                  # (fausses alertes larges sur les drapés, les ciels, les foules)


def _detecteur(L: int, H: int, seuil: float = SEUIL):
    return cv2.FaceDetectorYN.create(str(MODELE), '', (L, H), seuil, 0.3, 5000)


def _passer(img: np.ndarray, seuil: float = SEUIL) -> list[tuple[float, float, float, float, float]]:
    H, L = img.shape[:2]
    det = _detecteur(L, H, seuil)
    _, faces = det.detect(img)
    if faces is None:
        return []
    return [(float(f[0]), float(f[1]), float(f[0] + f[2]), float(f[1] + f[3]), float(f[14])) for f in faces]


def _variantes(img: np.ndarray) -> list[np.ndarray]:
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    egal = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gris)
    return [img, cv2.cvtColor(egal, cv2.COLOR_GRAY2BGR)]


def _nms(boites: list, seuil: float = 0.3) -> list:
    boites = sorted(boites, key=lambda b: -b[4])
    gardees = []
    for b in boites:
        ok = True
        for g in gardees:
            ix = max(0, min(b[2], g[2]) - max(b[0], g[0]))
            iy = max(0, min(b[3], g[3]) - max(b[1], g[1]))
            i = ix * iy
            a = min((b[2] - b[0]) * (b[3] - b[1]), (g[2] - g[0]) * (g[3] - g[1]))
            if a > 0 and i / a > seuil:
                ok = False
                break
        if ok:
            gardees.append(b)
    return gardees


def detecter(chemin: str) -> list[list[float]]:
    img = cv2.imread(chemin, cv2.IMREAD_COLOR)
    if img is None:
        return []
    H0, L0 = img.shape[:2]
    k = COTE / max(H0, L0)
    base = cv2.resize(img, (round(L0 * k), round(H0 * k)), interpolation=cv2.INTER_AREA) if k < 1 else img
    H, L = base.shape[:2]
    boites = []
    for v in _variantes(base):
        boites += _passer(v)
    # Tuiles agrandies (×TUILES) : les têtes de 2-4 % de l'image deviennent lisibles pour YuNet.
    if TUILES > 1:
        grand = cv2.resize(img, (L * TUILES, H * TUILES), interpolation=cv2.INTER_AREA if k * TUILES < 1 else cv2.INTER_CUBIC)
        tl, th = L, H
        pas_x, pas_y = (grand.shape[1] - tl) // max(1, TUILES - 1) or tl, (grand.shape[0] - th) // max(1, TUILES - 1) or th
        for ty in range(TUILES):
            for tx in range(TUILES):
                x0, y0 = min(tx * pas_x, grand.shape[1] - tl), min(ty * pas_y, grand.shape[0] - th)
                tuile = grand[y0:y0 + th, x0:x0 + tl]
                for v in _variantes(tuile):
                    for b in _passer(v):
                        if (b[3] - b[1]) / TUILES / H > GRAND:
                            continue        # les grandes têtes viennent de l'image entière
                        boites.append(((b[0] + x0) / TUILES, (b[1] + y0) / TUILES,
                                       (b[2] + x0) / TUILES, (b[3] + y0) / TUILES, b[4]))
    sortie = []
    for x0, y0, x1, y1, score in _nms(boites):
        w, h = x1 - x0, y1 - y0
        if h / H > GRAND and score < SEUIL_GRAND:
            continue
        r = _elargir((x0, y0, x1, y1), L, H)
        if r[3] - r[1] >= H_MIN and r[2] > r[0]:
            sortie.append(r)
    return sorted(sortie)


def _elargir(b, L: int, H: int) -> list[float]:
    x0, y0, x1, y1 = b[:4]
    w, h = x1 - x0, y1 - y0
    r = [(x0 - LARGE * w) / L, (y0 - HAUT * h) / H, (x1 + LARGE * w) / L, (y1 + BAS * h) / H]
    return [round(min(1.0, max(0.0, v)), 3) for v in r]


def detecter_portrait(chemin: str) -> list[list[float]]:
    """Le visage le plus probable d'un portrait (seuil bas, image entière, couleur et gris égalisé)."""
    img = cv2.imread(chemin, cv2.IMREAD_COLOR)
    if img is None:
        return []
    H0, L0 = img.shape[:2]
    k = COTE / max(H0, L0)
    base = cv2.resize(img, (round(L0 * k), round(H0 * k)), interpolation=cv2.INTER_AREA) if k < 1 else img
    H, L = base.shape[:2]
    boites = [b for v in _variantes(base) for b in _passer(v, SEUIL_PORTRAIT)]
    boites = [b for b in boites if (b[3] - b[1]) / H >= H_MIN]
    if not boites:
        return []
    # Le plus probable, à score voisin le plus grand (le sujet d'un portrait domine l'image).
    b = max(boites, key=lambda b: b[4] + 2 * (b[3] - b[1]) / H)
    return [_elargir(b, L, H)]


def main() -> None:
    entree = json.loads(sys.stdin.read())
    if isinstance(entree, dict) and entree.get('portrait'):
        json.dump([detecter_portrait(p) for p in entree['chemins']], sys.stdout)
        return
    json.dump([detecter(p) for p in entree], sys.stdout)


if __name__ == '__main__':
    main()
