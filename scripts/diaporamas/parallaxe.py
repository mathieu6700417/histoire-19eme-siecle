"""Parallaxe 2,5D : plans d'un tableau séparés par estimation de profondeur (spec 12,
« Enrichissements visuels », point 6 — banc d'essai du 2026-10-08).

Usage :
    python3 scripts/diaporamas/parallaxe.py revolution --n 47                # 3 plans, amplitude 1,5 %
    python3 scripts/diaporamas/parallaxe.py revolution --n 6 47 56 81 --plans 2 --amplitude 0.012
    python3 scripts/diaporamas/parallaxe.py revolution --n 47 --planche      # planche seule (rien écrit)
    python3 scripts/diaporamas/parallaxe.py revolution --n 47 --retirer      # retire le champ

Dépendances (hors bibliothèque standard), dans un venv qui voit le torch du système :
    python3 -m venv --system-site-packages .cache/venv-parallaxe
    .cache/venv-parallaxe/bin/pip install "opencv-python-headless<4.11" "numpy==2.0.2"
    .cache/venv-parallaxe/bin/pip install --ignore-installed scikit-learn pyarrow scipy "numpy==2.0.2"
(la seconde ligne isole le venv d'un scikit-learn système compilé pour numpy 1, que transformers
importe). Le script se relance de lui-même dans ce venv. Modèle : Depth Anything V2 Small
(`depth-anything/Depth-Anything-V2-Small-hf`, Apache 2.0, ~100 Mo, téléchargé au premier usage dans
~/.cache/huggingface), calculé en local (MPS si disponible, sinon CPU).

Méthode, pour l'image servie (`public/diaporamas/<slug>/NNN.webp`, mêmes pixels que le lecteur) :
1. profondeur relative (inverse : grand = proche), lissée en préservant les bords (filtre bilatéral
   joint guidé par l'image), normalisée sur la zone utile (centiles 2 à 98) ;
2. seuils entre plans par la méthode d'Otsu (multi-niveaux) sur l'histogramme de la zone utile ;
3. alpha de chaque plan proche = rampe dans l'espace des profondeurs (largeur `RAMPE`) : nette sur une
   arête d'occlusion (la profondeur y saute), large sur une surface continue (sol, ciel) où le plan
   se fond sans couture ; petites îles retirées, petits trous bouchés ;
4. comblement : sous chaque plan proche, le plan de derrière est comblé (OpenCV `inpaint`, Telea)
   dans le cœur du masque (alpha > 0,5) élargi de quelques pixels ; seule une bande de la largeur du
   déplacement (1 à 2 % de la scène) sera jamais découverte ;
5. sortie : `public/diaporamas/<slug>/parallaxe/NNN-0.webp` (fond, opaque), `NNN-1.webp`,
   `NNN-2.webp` (plans proches, transparents, nuls hors de la zone utile), et dans la diapositive
   `image.parallaxe: { plans: [...], amplitude }` ; planche de contrôle dans
   `.cache/diaporamas/parallaxe/NNN.jpg` (image, profondeur, plans sur damier, fond comblé, et un
   décalage exagéré ×3 pour juger les découvertes).
"""
import argparse, os, sys, time
from pathlib import Path

VENV = Path(__file__).resolve().parents[2] / '.cache' / 'venv-parallaxe' / 'bin' / 'python'
try:
    import cv2  # noqa: F401
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError:
    if VENV.exists() and Path(sys.prefix).resolve() != VENV.parents[1].resolve():
        os.execv(str(VENV), [str(VENV), *sys.argv])
    raise SystemExit('OpenCV manquant : voir l\'en-tête de parallaxe.py pour créer .cache/venv-parallaxe')

import commun as c

MODELE = 'depth-anything/Depth-Anything-V2-Small-hf'
RAMPE = 0.06          # largeur de la rampe d'alpha, en profondeur normalisée (0 → 1)
ELARGI = 4            # px : élargissement du cœur comblé (couvre les pixels de bord mêlés)
ILE_MIN = 0.002       # part de l'image : îles plus petites retirées d'un plan, trous plus petits bouchés
QUALITE = 82
AMPLITUDE = 0.015     # déplacement final du premier plan, en fraction de la largeur de la scène


def profondeur(img: 'np.ndarray') -> 'np.ndarray':
    import torch
    # pandas (importé en option par scikit-learn, lui-même importé par transformers) traîne des
    # extensions système compilées pour numpy 1 : on l'écarte, il ne sert pas ici.
    sys.modules.setdefault('pandas', None)
    import transformers
    transformers.logging.set_verbosity_error()
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    dev = 'mps' if torch.backends.mps.is_available() else 'cpu'
    proc = AutoImageProcessor.from_pretrained(MODELE)
    mod = AutoModelForDepthEstimation.from_pretrained(MODELE).to(dev).eval()
    with torch.no_grad():
        ent = proc(images=Image.fromarray(img), return_tensors='pt').to(dev)
        d = mod(**ent).predicted_depth[None]
        d = torch.nn.functional.interpolate(d, size=img.shape[:2], mode='bicubic', align_corners=False)
    return d[0, 0].float().cpu().numpy()


def otsu(v: 'np.ndarray', n: int) -> list[float]:
    """Seuils d'Otsu à n − 1 niveaux (recherche exhaustive sur 64 classes)."""
    h, b = np.histogram(v, bins=64, range=(0, 1))
    p = h / h.sum(); m = (b[:-1] + b[1:]) / 2
    def var(a, z):
        w = p[a:z].sum()
        return 0 if w == 0 else w * ((p[a:z] * m[a:z]).sum() / w) ** 2
    best, seuils = -1, []
    if n == 2:
        for i in range(4, 60):
            s = var(0, i) + var(i, 64)
            if s > best: best, seuils = s, [m[i]]
    else:
        for i in range(4, 56):
            for j in range(i + 4, 60):
                s = var(0, i) + var(i, j) + var(j, 64)
                if s > best: best, seuils = s, [m[i], m[j]]
    return [float(x) for x in seuils]


def nettoyer(alpha: 'np.ndarray') -> 'np.ndarray':
    """Retire les îles et bouche les trous de moins de ILE_MIN de l'image (sur le cœur alpha > 0,5)."""
    import cv2
    aire = ILE_MIN * alpha.size
    coeur = (alpha > 0.5).astype(np.uint8)
    garde = np.zeros_like(coeur)
    k, lab, st, _ = cv2.connectedComponentsWithStats(coeur, 8)
    for j in range(1, k):
        if st[j, cv2.CC_STAT_AREA] >= aire: garde[lab == j] = 1
    trous = 1 - garde
    k, lab, st, _ = cv2.connectedComponentsWithStats(trous, 8)
    bouche = np.zeros_like(garde)
    for j in range(1, k):
        if st[j, cv2.CC_STAT_AREA] < aire: bouche[lab == j] = 1
    a = alpha.copy()
    a[(coeur == 1) & (garde == 0)] = 0   # îles retirées
    a[bouche == 1] = 1                   # trous bouchés
    # Les retouches binaires sont adoucies (bords de 2 px), le reste de la rampe est gardé.
    flou = cv2.GaussianBlur(a, (0, 0), 1.2)
    retouche = cv2.dilate(((coeur == 1) & (garde == 0) | (bouche == 1)).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    a[retouche] = flou[retouche]
    return np.clip(a, 0, 1)


def zone_comblee(alpha: 'np.ndarray') -> 'np.ndarray':
    """Part comblée (0 → 1) sous un plan : son cœur (alpha > 0,5) élargi de ELARGI px, à bord adouci
    sur 3 px (1 sur tout le cœur)."""
    import cv2
    m = cv2.dilate((alpha > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ELARGI + 1,) * 2))
    return np.clip(cv2.distanceTransform(m, cv2.DIST_L2, 3) / 3, 0, 1).astype(np.float32)


def combler(img: 'np.ndarray', part: 'np.ndarray') -> 'np.ndarray':
    """L'image comblée (Telea) là où `part` > 0, fondue avec l'originale sur le bord adouci."""
    import cv2
    rempli = cv2.inpaint(img, (part > 0).astype(np.uint8) * 255, 6, cv2.INPAINT_TELEA).astype(np.float32)
    p = part[..., None]
    return rempli * p + img.astype(np.float32) * (1 - p)


def preparer(slug: str, x: dict, plans: int, amplitude: float, planche_seule: bool) -> dict | None:
    import cv2
    n = x['n']
    src = c.PUBLIC / slug / x['image']['fichier']
    img = np.array(Image.open(src).convert('RGB'))
    H, W = img.shape[:2]
    u = x['image'].get('utile', [0, 0, 1, 1])
    ux0, uy0, ux1, uy1 = int(u[0] * W), int(u[1] * H), int(round(u[2] * W)), int(round(u[3] * H))
    t0 = time.time()
    d = profondeur(img)
    t_modele = time.time() - t0
    # Lissage qui suit les bords de l'image (pas de halo de profondeur autour des figures).
    d = cv2.ximgproc.jointBilateralFilter(img, d.astype(np.float32), 9, 0.05 * (d.max() - d.min()), 5) \
        if hasattr(cv2, 'ximgproc') else cv2.bilateralFilter(d.astype(np.float32), 9, float(0.05 * (d.max() - d.min())), 5)
    zone = d[uy0:uy1, ux0:ux1]
    lo, hi = np.percentile(zone, 2), np.percentile(zone, 98)
    d = np.clip((d - lo) / max(1e-6, hi - lo), 0, 1)
    seuils = otsu(d[uy0:uy1, ux0:ux1].ravel(), plans)
    utile = np.zeros((H, W), np.float32); utile[uy0:uy1, ux0:ux1] = 1
    alphas = []
    for s in seuils:
        v = np.clip((d - s) / RAMPE + 0.5, 0, 1)
        a = nettoyer((v * v * (3 - 2 * v)).astype(np.float32)) * utile
        alphas.append(a)
    # Chaque plan proche emporte la zone comblée sous lui (son bord élargi) : alpha ≥ part comblée,
    # sinon la composition au repos montrerait du comblé hors du plan. Alpha quantifié comme dans le
    # webp : le démêlage en tient compte.
    parts = [zone_comblee(a) * utile for a in alphas]
    alphas = [np.round(np.maximum(a, p) * 255) / 255 for a, p in zip(alphas, parts)]
    # Plans du fond vers l'avant : chacun est l'image comblée sous les plans plus proches.
    # Couleurs des bords « démêlées » : la couleur d'un plan sur sa rampe est choisie pour que la
    # composition à décalage nul redonne exactement l'image (pas de halo au repos), et qu'un bord
    # découvert garde la couleur de la figure plutôt qu'un mélange avec le fond d'origine.
    couches, dessous = [], None
    for k in range(plans):
        cible = (combler(img, np.maximum.reduce(parts[k:])) if k + 1 < plans else img).astype(np.float32)
        if k == 0:
            couches.append((cible.round().astype(np.uint8), np.ones((H, W), np.float32)))
            dessous = cible
            continue
        a = alphas[k - 1]
        a3 = a[..., None]
        rgb = np.where(a3 > 0.02, (cible - (1 - a3) * dessous) / np.maximum(a3, 0.02), cible).clip(0, 255)
        couches.append((rgb.round().astype(np.uint8), a))
        dessous = rgb * a3 + dessous * (1 - a3)
    dossier = c.PUBLIC / slug / 'parallaxe'
    noms = [f'parallaxe/{n:03d}-{k}.webp' for k in range(plans)]
    poids = []
    if not planche_seule:
        dossier.mkdir(parents=True, exist_ok=True)
        for (rgb, a), nm in zip(couches, noms):
            f = c.PUBLIC / slug / nm
            if nm.endswith('-0.webp'):
                Image.fromarray(rgb).save(f, 'WEBP', quality=QUALITE, method=6)
            else:
                rgba = np.dstack([rgb * (a[..., None] > 0.004), (a * 255).round().astype(np.uint8)]).astype(np.uint8)
                Image.fromarray(rgba, 'RGBA').save(f, 'WEBP', quality=QUALITE, alpha_quality=90, method=6)
            poids.append(f.stat().st_size)
    planche(n, img, d, seuils, couches, amplitude)
    aires = [float(a[uy0:uy1, ux0:ux1].mean()) for a in alphas]
    print(f'{n:3d}  {plans} plans  seuils {", ".join(f"{s:.2f}" for s in seuils)}  '
          f'aire des plans proches {", ".join(f"{p:.0%}" for p in aires)}  modèle {t_modele:.1f} s  '
          + (f'poids {" + ".join(f"{p // 1024} Ko" for p in poids)} (image {src.stat().st_size // 1024} Ko)' if poids else ''))
    return None if planche_seule else {'plans': noms, 'amplitude': amplitude}


def composer(couches, decalages, W, H):
    """Composition des plans, chacun décalé de `decalages[k]` px vers la droite."""
    import cv2
    out = np.zeros((H, W, 3), np.float32)
    for (rgb, a), dx in zip(couches, decalages):
        M = np.float32([[1, 0, dx], [0, 1, 0]])
        r = cv2.warpAffine(rgb.astype(np.float32), M, (W, H), borderMode=cv2.BORDER_REPLICATE)
        al = cv2.warpAffine(a, M, (W, H), borderMode=cv2.BORDER_REPLICATE)[..., None]
        out = r * al + out * (1 - al)
    return out.clip(0, 255).astype(np.uint8)


def planche(n, img, d, seuils, couches, amplitude):
    import cv2
    H, W = img.shape[:2]
    L = 520; h = int(H * L / W)
    def vign(a, titre):
        im = Image.fromarray(a).resize((L, h))
        ImageDraw.Draw(im).text((6, 4), titre, fill=(255, 0, 0))
        return im
    def damier(rgb, a):
        y, x = np.mgrid[:H, :W]
        g = np.where(((x // 24 + y // 24) % 2)[..., None] == 0, 200, 140).astype(np.float32)
        return (rgb * a[..., None] + g * (1 - a[..., None])).astype(np.uint8)
    carte = cv2.applyColorMap((d * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)[..., ::-1]
    for s in seuils:
        carte[np.abs(d - s) < 0.004] = (0, 255, 255)
    v = [vign(img, f'{n} image'), vign(carte, 'profondeur (clair = proche), seuils en cyan')]
    for k, (rgb, a) in enumerate(couches):
        v.append(vign(rgb if k == 0 else damier(rgb, a), 'fond comblé' if k == 0 else f'plan {k}'))
    dmax = 3 * amplitude * W  # décalage exagéré ×3 pour voir les découvertes
    nb = len(couches)
    v.append(vign(composer(couches, [dmax * k / (nb - 1) for k in range(nb)], W, H), f'décalage ×3 ({3 * amplitude:.1%})'))
    z = np.abs(composer(couches, [0] * nb, W, H).astype(int) - img.astype(int)).sum(2).clip(0, 255).astype(np.uint8)
    v.append(vign(np.dstack([z * 4] * 3).clip(0, 255).astype(np.uint8), 'écart composition / image ×4'))
    print(f'     écart au repos (somme RVB) : moyen {z.mean():.2f}, > 24 sur {(z > 24).mean():.3%} des pixels, max {z.max()}')
    cols = 3; lignes = (len(v) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * L, lignes * h), 'white')
    for k, im in enumerate(v): sheet.paste(im, ((k % cols) * L, (k // cols) * h))
    (c.CACHE / 'parallaxe').mkdir(parents=True, exist_ok=True)
    sheet.save(c.CACHE / 'parallaxe' / f'{n:03d}.jpg', quality=85)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('slug')
    ap.add_argument('--n', type=int, nargs='+', required=True)
    ap.add_argument('--plans', type=int, default=3, choices=(2, 3))
    ap.add_argument('--amplitude', type=float, default=AMPLITUDE)
    ap.add_argument('--planche', action='store_true', help='planche de contrôle seule, rien n\'est écrit')
    ap.add_argument('--retirer', action='store_true', help='retire image.parallaxe (les fichiers restent)')
    a = ap.parse_args()
    if not 0.005 <= a.amplitude <= 0.02:
        raise SystemExit('amplitude hors de 0,005 à 0,02 (1 à 2 % de la scène voulus)')
    f, D = c.lire(a.slug)
    slug = D['slug']
    par_n = {x['n']: x for x in D['diapositives']}
    for n in a.n:
        x = par_n.get(n)
        if not x: raise SystemExit(f'diapositive {n} introuvable')
        if a.retirer:
            x['image'].pop('parallaxe', None); continue
        if x['image'].get('apres') or x.get('mosaique'):
            raise SystemExit(f'{n} : pas de parallaxe sur un avant / après ou une mosaïque')
        r = preparer(slug, x, a.plans, a.amplitude, a.planche)
        if r: x['image']['parallaxe'] = r
    if not a.planche: c.ecrire(f, D)
    print(f'planches : {(c.CACHE / "parallaxe").relative_to(c.RACINE)}/')


if __name__ == '__main__':
    main()
