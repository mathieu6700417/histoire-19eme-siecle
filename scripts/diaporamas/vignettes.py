#!/usr/bin/env python3
"""Dessins traversants sous les images entières (spec 17, essai 5 : « Verdict et règles
d'intégration », puis « Révision après visionnage du pilote : dessins traversants, simples, sans
personnage », 2026-10-14 ; pilote sur la période 06).

Sous une image montrée en entier (`image.entier`), un seul dessin à la plume au format de l'écran,
**généré par IA** (Z-Image-Turbo, Apache 2.0, sur Colab) d'après ce que dit la voix : une esquisse
simple, sans personnage, dont on ne voit que les deux bords, dans les marges ; le centre, caché par
l'image, est laissé vide. Les deux bords se tracent ensemble en 8 s (une plume par bord, contours
d'abord), chacun sur une simple éclaircie du fond prolongé (src/scripts/diaporama/vignette.ts) ; le
cartouche le signale. Mode d'emploi complet : README, « Dessins traversants (spec 17, essai 5) ».

    python3 scripts/diaporamas/vignettes.py preparer <slug>            # lot → manifeste, consignes, fenêtres
    python3 scripts/diaporamas/vignettes.py lancer <slug> [--graines 1,2,3] [--seulement 031,034-b]
                                               [--gpu L4] [--session NOM] [--reprendre] [--garder] [--sans-suivi]
    python3 scripts/diaporamas/vignettes.py rapatrier <slug> | arreter <slug>    # session laissée ouverte
    python3 scripts/diaporamas/vignettes.py tracer <slug> [--seulement …]    # encre + tracés de chaque tirage
    python3 scripts/diaporamas/vignettes.py planche <slug>             # relecture : montages et planche.html
    python3 scripts/diaporamas/vignettes.py publier <slug> [--seulement 31,34b] [--sauf …] [--essai]
    python3 scripts/diaporamas/vignettes.py retirer <slug> 31 34b …    # ou --tout
    python3 scripts/diaporamas/vignettes.py encres <slug> [--essai]   # encre claire sur fond sombre
    python3 scripts/diaporamas/vignettes.py lister <slug>

**Lot** (écrit à la main) : src/data/diaporamas/generation/<slug>-vignettes.json, qui sert aussi de
recette : `style` (consigne commune, anglaise : esquisse simple, aucun personnage), `modele`, et
`vignettes`, une entrée par image :
    { "n": "31" ou "34b" (numéro ACTUEL ; `renumeroter.py` le tient à jour), "commons" (facultatif,
      vérifié), "gauche", "droite" : ce qui est dessiné sur chaque bord (anglais, lieux et objets
      seulement), "quand" : passage exact de la narration qui déclenche le trait (absent : peu après
      l'apparition de l'image), "graine" ou "reprise" (« essai-simple:031-C-zimage » : tirages de
      l'essai repris tels quels), puis à la relecture "tirage", "jugement" ("bon" | "ecarte"), "raison" }

**Format et place.** Le dessin est demandé au format de la scène la plus large du lecteur
(`GEN` : 1792 × 768, 2,33:1, ordinateur fenêtré) ; le lecteur le pose à la hauteur de l'image entière
au repos, sur son bas, centré sur elle ; sur une scène plus étroite que lui (plein écran 16:9 ou 16:10,
grand écran fenêtré), il le réduit à la largeur de la scène. La consigne écrit donc, d'après la place réelle de
l'image (rapport de la zone utile × `entier_zoom`, son rapprochement final), la part du centre à
laisser vide et la bande de chaque côté où poser l'objet : entre le bord de l'image et le bord de la
scène la plus étroite (`SCENE_ETROITE` hauteurs d'image de large) ; au-delà, seulement le sol et le ciel.

**Cache** : .cache/diaporamas/vignettes/<slug>/ : manifeste.json (kit envoyé sur Colab), bruts/
(<nom>-g<k>.png ; les reprises de l'essai y sont copiées), trace/ (<nom>-g<k>-encre.webp et
<nom>-g<k>.json, par `tracer`, mode « plein » de vignettes_trace.py, dans le venv .cache/venv-vignettes :
`python3 -m venv .cache/venv-vignettes && .cache/venv-vignettes/bin/pip install opencv-python-headless
scikit-image numpy pillow`), releve/ (montages des trois tirages) et planche.html (maquettes animées).
Le premier pilote (vignettes d'une marge) est dans l'historique de ce fichier et dans pilote-1/.

`publier` copie l'encre et les tracés du tirage retenu des entrées jugées « bon » dans
public/diaporamas/<slug>/ (031-vignette.webp, 031-vignette.json ; 034-b-vignette.…) et écrit
`image.vignette` { fichier, traces, centre: [x0, x1] (part de la largeur du dessin cachée par l'image
à son rapprochement final, d'après laquelle il a été composé), quand?, largeur, hauteur, modele,
genere_le } ; refuse une image qui n'est pas montrée en entier, une surimpression de coin (portraits,
médaillon de lieu, objet, manuscrit : elles couvrent une marge) ou une citation à l'écran pendant le
dessin, et plus de `PLAFOND` dessins. Idempotent. `renumeroter.py` suit les deux fichiers ;
`verifier.py` contrôle la famille « vignettes (essai 5) ».
"""
from __future__ import annotations

import argparse, datetime, html, json, re, shutil, subprocess, sys, time, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import commun as c
import fond   # colab(), arreter(), images entières

MODELE = 'Tongyi-MAI/Z-Image-Turbo'
PLAFOND = 35               # dessins par période, au plus (verdict du 2026-10-14 : une trentaine)
GEN = (1792, 768)          # px demandés au modèle : la scène la plus large du lecteur (2,33:1, multiples de 16)
SCENE_ETROITE = 1.6        # largeur de la scène la plus étroite, en hauteurs d'image au repos (16:10 fenêtré)
MARGE_MIN = 0.16           # marge (hauteurs d'image) en deçà de laquelle le bord serait trop étroit
ATTENTE = 2.0              # s : départ par défaut du tracé après l'apparition de l'image (VIGNETTE_ATTENTE du lecteur)
ATTENTE_PLAN = 1.2         # s : de même après l'instant d'un plan (VIGNETTE_ATTENTE_PLAN)
DUREE = 8.0                # s : durée du tracé (VIGNETTE_DUREE du lecteur)
FENETRE_CHIFFRE = 5.0      # s : chiffre clé ou date républicaine à l'écran (4 à 5 s, diaporamas.ts), marge comprise
SUFFIXE = '-vignette'
ENCRE_SEUIL = 0.4          # luminance moyenne des marges du fond prolongé (0-1, avant FOND_LUMIERE) sous
                           # laquelle le dessin est tracé à l'encre claire, sans éclaircie (annotations du 2026-10-14)
REMOTE = '/content/vignettes'
ESSAI = c.CACHE / 'vignettes'
VENV = c.RACINE / '.cache' / 'venv-vignettes' / 'bin' / 'python'


def dossier(slug: str) -> Path:
    d = c.CACHE / 'vignettes' / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def lot_f(slug: str) -> Path:
    return c.DONNEES / 'generation' / f'{slug}-vignettes.json'


def lire_lot(slug: str) -> dict:
    f = lot_f(slug)
    if not f.exists():
        raise SystemExit(f'Lot absent : {f.relative_to(c.RACINE)} (à écrire à la main, voir le README)')
    return json.loads(f.read_text(encoding='utf-8'))


def cle(texte: str) -> str:
    """« 34-b », « 034b » → « 34b »."""
    m = re.fullmatch(r'0*(\d+)-?([a-z]?)', str(texte).strip().lower())
    if not m:
        raise SystemExit(f'cible « {texte} » : attendu un numéro de diapositive (86) ou de plan (34b)')
    return m[1] + m[2]


def images(d: dict) -> list[dict]:
    """Image de chaque diapositive et de chacun de ses plans : {'cle' (31, 34b), 'nom' (031, 034-b),
    'image', 'x', 'k' (0 : image de la diapositive ; 1, 2 : plans)}."""
    sortie = []
    for x in d['diapositives']:
        serie = [(str(x['n']), x['image'], 0)]
        for k, p in enumerate(x.get('plans') or []):
            lettre = c.LETTRES_PLANS[k] if k < len(c.LETTRES_PLANS) else chr(ord('b') + k)
            serie.append((f"{x['n']}{lettre}", p.get('image') if isinstance(p, dict) else None, k + 1))
        for k_, im, k in serie:
            if isinstance(im, dict) and im.get('fichier'):
                sortie.append({'cle': k_, 'nom': Path(im['fichier']).stem, 'image': im, 'x': x, 'k': k})
    return sortie


# --- Géométrie, fenêtres, surimpressions (partagées avec verifier.py) ----------------------------

def aspect(im: dict) -> float:
    u = im.get('utile') or [0, 0, 1, 1]
    return (im.get('largeur') or 1600) * (u[2] - u[0]) / ((im.get('hauteur') or 1200) * (u[3] - u[1]))


def largeur_finale(im: dict) -> float:
    """Largeur de l'image entière à son rapprochement final, en hauteurs d'image au repos."""
    return aspect(im) * min(2.0, max(1.0, im.get('entier_zoom') or 1.3))


def marge(im: dict) -> float:
    """Marge de chaque côté sur la scène la plus étroite, au rapprochement final, en hauteurs
    d'image : tant que l'image agrandie reste plus étroite que la scène, la vue est centrée sur elle
    en largeur (camera.ts, `vueZoom`), les deux marges sont égales."""
    return max(0.0, (SCENE_ETROITE - largeur_finale(im)) / 2)


def centre(im: dict, r: float | None = None) -> list[float]:
    """Part de la largeur du dessin (rapport `r`, par défaut le format `GEN`) cachée par l'image au
    rapprochement final (le dessin est posé à la hauteur de l'image au repos, centré sur elle)."""
    r = r or GEN[0] / GEN[1]
    w = min(1.0, largeur_finale(im) / r)
    return [round(0.5 - w / 2, 4), round(0.5 + w / 2, 4)]


def consigne(lot: dict, v: dict, im: dict) -> str:
    """Consigne d'un dessin traversant : style commun, puis composition calculée d'après la place
    réelle de l'image (centre vide, bande de chaque côté où poser l'objet, bords extérieurs nus)."""
    r = GEN[0] / GEN[1]
    x0 = centre(im)[0]
    dedans = max(0.0, x0 - 0.015)                           # depuis le bord : jusqu'où dessiner l'objet
    dehors = max(0.0, 0.5 - SCENE_ETROITE / 2 / r)          # au-delà (vers le bord), rogné sur la scène étroite
    pc = lambda f: round(100 * f)
    return (f"{lot['style']} A wide panoramic sketch whose interest is only on its two sides. The whole middle "
            f"{100 - 2 * pc(dedans)} percent of the width is completely empty white paper with nothing drawn in it, "
            f"except perhaps a faint ground line near the bottom. On the left side, standing between about {pc(dehors)} and "
            f"{pc(dedans)} percent of the width from the left edge: {v['gauche']}. On the right side, standing between about "
            f"{pc(dehors)} and {pc(dedans)} percent of the width from the right edge: {v['droite']}. The outer {pc(dehors)} "
            f"percent of each side holds only a faint ground line and sky. Both sides stand on the same ground line, near the "
            f"bottom of the picture, and rise to about two thirds of its height.")


def instant_car(x: dict, pos: int) -> float:
    """Instant (s) où la voix dit le caractère `pos` (prorata dans sa phrase horodatée)."""
    for d0, f0, t0, t1 in c._phrases_horodatees(x):
        if d0 <= pos < max(f0, d0 + 1):
            return t0 + (pos - d0) / max(1, f0 - d0) * (t1 - t0)
    duree = (x.get('audio') or {}).get('duree') or 6
    return pos / max(1, len(x['narration'])) * duree


def fenetre(x: dict, k: int) -> dict:
    """Fenêtre de l'image k (0 : image de la diapositive) : {'t': (début, fin) s de la voix,
    'car': caractères de la narration dite pendant ce temps}."""
    F = c.fenetres_plans(x)
    fen = F[k]
    t0, t1 = fen['t']
    if t0 is None:
        t0 = max(0.0, instant_car(x, fen['car'][0]) - c.AVANCE_PLAN)
    if t1 is None:
        t1 = max(t0, instant_car(x, F[k + 1]['car'][0]) - c.AVANCE_PLAN)
    return {'t': (float(t0), float(t1)), 'car': fen['car']}


def depart(x: dict, k: int, v: dict) -> tuple[float, str | None]:
    """Instant prévu du début du tracé (même règle que vignette.ts, à l'entrée en scène près) et
    problème éventuel du `quand`."""
    f = fenetre(x, k)
    a = f['t'][0] + (ATTENTE if k == 0 else ATTENTE_PLAN)
    q = v.get('quand')
    if not q:
        return a, None
    c0, c1 = f['car']
    pos = x['narration'].find(q, c0)
    if pos < 0 or pos >= max(c1, c0 + 1):
        return a, f'passage « {q} » absent de la narration dite pendant l\'image'
    return max(a, instant_car(x, pos) - 0.2), None


def fenetre_vignette(x: dict, k: int, v: dict) -> tuple[float, float]:
    """Temps (s de la voix) où le dessin est à l'écran : du début du tracé à la fin de l'image (fondu
    du plan suivant compris ; dernière image : fin de la voix et un peu de sa pause)."""
    t, _ = depart(x, k, v)
    return t, fenetre(x, k)['t'][1] + c.FONDU_PLAN + 0.5


_REGISTRES: tuple[dict, dict] | None = None


def surimpressions(x: dict, fen: tuple[float, float]) -> tuple[list[str], list[str]]:
    """Surimpressions à l'écran pendant le dessin (`fen`), d'après les fenêtres arbitrées comme dans
    le lecteur (verifier.fenetres_surimpressions). Rend (interdites, effaçantes) : les surimpressions de
    coin (portraits, médaillon de lieu, objet, manuscrit) couvrent une marge, la citation le centre et
    le bas : interdites ; un chiffre clé ou une date républicaine efface le dessin le temps de leur
    passage (avertissement)."""
    global _REGISTRES
    import verifier as vf
    if _REGISTRES is None:
        lire = lambda n: json.loads((c.DONNEES / n).read_text()) if (c.DONNEES / n).exists() else []
        _REGISTRES = ({p['id']: p for p in lire('portraits.json') if p.get('id')}, {o['id']: o for o in lire('objets.json') if o.get('id')})
    F = vf.fenetres_surimpressions(x, *_REGISTRES)
    noms = {'lieu': 'médaillon de lieu', 'portraits': 'portraits', 'objet': 'objet', 'manuscrit': 'manuscrit',
            'citation': 'citation', 'chiffre': 'chiffre clé', 'date': 'date républicaine'}
    interdites, effacantes = [], []
    for k, w in F.items():
        if not w or w[1] <= fen[0] or w[0] >= fen[1]:
            continue
        txt = f'{noms.get(k, k)} ({w[0]:.1f}-{w[1]:.1f} s)'
        (effacantes if k in ('chiffre', 'date') else interdites).append(txt)
    return interdites, effacantes


def resoudre(d: dict, lot: dict) -> list[dict]:
    """Entrées du lot rattachées à leur image : {'v', 'e' (images()), 'pb' (refus), 'av' (avertissements)}."""
    par_cle = {e['cle']: e for e in images(d)}
    sortie = []
    for v in lot.get('vignettes', []):
        e = par_cle.get(cle(v.get('n', '?')))
        pb, av = [], []
        if e is None:
            pb.append('image absente de la période')
        else:
            im, x = e['image'], e['x']
            if v.get('commons') and v['commons'] != im.get('commons'):
                pb.append(f"commons changé ({v['commons'][:40]} → {im.get('commons', '')[:40]}) : renuméroté ?")
            if not im.get('entier'):
                pb.append("image qui n'est pas montrée en entier")
            if x['image'].get('apres') or x.get('mosaique'):
                pb.append('avant / après ou mosaïque')
            if marge(im) < MARGE_MIN:
                pb.append(f'marge trop étroite ({marge(im):.2f} hauteur d\'image)')
            fen = fenetre_vignette(x, e['k'], v)
            inter, eff = surimpressions(x, fen)
            if inter:
                pb.append(f"à l'écran pendant le dessin : {', '.join(inter)}")
            if eff:
                av.append(f"{', '.join(eff)} : le dessin s'efface le temps de leur passage")
            t, pb_q = depart(x, e['k'], v)
            if pb_q:
                pb.append(pb_q)
            elif t + DUREE > fenetre(x, e['k'])['t'][1] + 0.5:
                av.append(f"tracé de {t:.1f} à {t + DUREE:.1f} s, image jusqu'à {fenetre(x, e['k'])['t'][1]:.1f} s : il finit après elle")
        sortie.append({'v': v, 'e': e, 'pb': pb, 'av': av})
    return sortie


# --- Préparation et calcul --------------------------------------------------------------------

def reprise_src(reprise: str, k: int) -> Path | None:
    """« essai-simple:031-C-zimage » → tirage k de l'essai des dessins simples."""
    if ':' not in reprise:
        return None
    sous, nom = reprise.split(':', 1)
    f = ESSAI / 'second-empire' / sous / 'bruts2' / f'{nom}-g{k}.png'
    return f if f.exists() else None


def preparer(slug: str) -> None:
    _, d = c.lire(slug)
    slug = d['slug']
    lot = lire_lot(slug)
    dest = dossier(slug)
    (dest / 'bruts').mkdir(exist_ok=True)
    elements, lignes, refus = [], [], 0
    for r in resoudre(d, lot):
        v, e = r['v'], r['e']
        if e is None:
            print(f"  REFUS {v.get('n')} : {'; '.join(r['pb'])}")
            refus += 1
            continue
        im, x = e['image'], e['x']
        f = fenetre(x, e['k'])
        t, _ = depart(x, e['k'], v)
        if v.get('reprise'):
            for k in (1, 2, 3):
                src = reprise_src(v['reprise'], k)
                if src and not (dest / 'bruts' / f"{e['nom']}-g{k}.png").exists():
                    shutil.copy(src, dest / 'bruts' / f"{e['nom']}-g{k}.png")
            origine = f"reprise ({v['reprise']})"
        else:
            elements.append(dict(nom=e['nom'], cle=e['cle'], graine=int(v['graine']), style='', scene='', largeur=GEN[0], hauteur=GEN[1],
                                 consigne=consigne(lot, v, im)))
            origine = f'{GEN[0]}×{GEN[1]}'
        lignes.append(f"  {e['cle']:>5} marge {marge(im):.2f} h (a {aspect(im):.2f}), centre {centre(im)} ; "
                      f"image {f['t'][0]:.1f}–{f['t'][1]:.1f} s, tracé dès {t:.1f} s ; {origine}"
                      + ''.join(f'\n          ! {p}' for p in r['pb']) + ''.join(f'\n          ~ {p}' for p in r['av']))
    (dest / 'manifeste.json').write_text(json.dumps(dict(slug=slug, modele=MODELE, style='', elements=elements),
                                                    ensure_ascii=False, indent=1), encoding='utf-8')
    print('\n'.join(lignes))
    print(f"{len(lignes)} dessins ({len(elements)} à calculer, {len(lignes) - len(elements)} reprises), {refus} refus ; "
          f"manifeste {(dest / 'manifeste.json').relative_to(c.RACINE)}")


def distant(slug: str) -> str:
    return f'{REMOTE}/{slug}'


def suivre(slug: str, session: str, lignes: int = 4) -> str:
    code = (f'import os\np = "{distant(slug)}/out/log.txt"\nt = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""\n'
            f'L = [l for l in t.splitlines() if l.strip() and "━" not in l and "it/s]" not in l and "s/it]" not in l and "Fetching" not in l and "Downloading" not in l]\n'
            f'print(chr(10).join(l[:200] for l in L[-{lignes}:]))')
    return fond.colab('exec', '-s', session, '--timeout', '30', timeout=45, code=code, strict=False)


def rapatrier(slug: str, session: str) -> int:
    """Rapatrie les dessins absents du disque (une archive), sans rien arrêter."""
    dest = dossier(slug)
    bruts = dest / 'bruts'
    bruts.mkdir(exist_ok=True)
    R = distant(slug)
    deja = sorted(f.name for f in bruts.glob('*.png'))
    code = (f'import zipfile, pathlib, json\ndeja = set(json.loads({json.dumps(json.dumps(deja))}))\n'
            f'fs = [f for f in sorted(pathlib.Path("{R}/out").iterdir()) if f.suffix in (".png", ".jsonl", ".txt") and f.name not in deja]\n'
            f'z = zipfile.ZipFile("{R}/sorties.zip", "w", zipfile.ZIP_STORED)\n[z.write(f, f.name) for f in fs]\nz.close(); print(len(fs))')
    print('à rapatrier :', fond.colab('exec', '-s', session, '--timeout', '60', timeout=90, code=code).strip(), 'fichiers')
    fond.colab('download', '-s', session, f'{R}/sorties.zip', str(dest / 'sorties.zip'), timeout=900)
    with zipfile.ZipFile(dest / 'sorties.zip') as z:
        for n in z.namelist():
            (bruts if n.endswith('.png') else dest).joinpath(n).write_bytes(z.read(n))
    n = len(list(bruts.glob('*.png')))
    print(f'{n} dessins dans {bruts.relative_to(c.RACINE)}')
    return n


def lancer(slug: str, gpu: str, session: str, graines: str, seulement: str, reprendre: bool, garder: bool, sans_suivi: bool) -> None:
    dest = dossier(slug)
    if not (dest / 'manifeste.json').exists():
        raise SystemExit(f'Manifeste absent : lancer « preparer {slug} » d\'abord')
    R = distant(slug)
    if not reprendre:
        print(f'session « {session} » ({gpu})…', flush=True)
        fond.colab('new', '-s', session, '--gpu', gpu, timeout=600)
    try:
        fond.colab('exec', '-s', session, '--timeout', '60', timeout=90, code=f'import os; os.makedirs("{R}/in", exist_ok=True); os.makedirs("{R}/out", exist_ok=True)')
        fond.colab('upload', '-s', session, str(dest / 'manifeste.json'), f'{R}/in/manifeste.json', timeout=300)
        fond.colab('upload', '-s', session, str(c.RACINE / 'scripts/colab/vignettes.py'), f'{R}/vignettes.py', timeout=300)
        env = f'GRAINES={graines} SEULEMENT={seulement} ENTREE={R}/in SORTIE={R}/out'
        fond.colab('exec', '-s', session, '--timeout', '60', timeout=90, code=(
            f'import subprocess; subprocess.Popen("nohup env {env} python3 {R}/vignettes.py > {R}/out/log.txt 2>&1 &", shell=True); print("lancé")'))
        print('calcul lancé', flush=True)
        if sans_suivi:
            print(f'sans suivi : « rapatrier {slug} » puis « arreter {slug} » à la main (session {session})')
            return
        debut = time.time()
        while time.time() - debut < 3 * 3600:
            time.sleep(60)
            fin = suivre(slug, session, 3).splitlines()
            if fin:
                print(' ', fin[-1], flush=True)
            if any(l.endswith(' FIN') or ' ERREUR' in l for l in fin):
                break
        rapatrier(slug, session)
    finally:
        if not garder and not sans_suivi:
            fond.arreter(session)


# --- Trait, relecture --------------------------------------------------------------------------

def tirages(slug: str, nom: str) -> list[int]:
    return sorted(int(m[1]) for f in (dossier(slug) / 'bruts').glob(f'{nom}-g*.png') if (m := re.fullmatch(rf'{re.escape(nom)}-g(\d+)\.png', f.name)))


def tracer(slug: str, seulement: set[str]) -> None:
    """Encre et tracés de chaque tirage, en mode « plein » (venv .cache/venv-vignettes ; refait si le
    dessin a changé)."""
    if not VENV.exists():
        raise SystemExit(f'venv absent ({VENV.relative_to(c.RACINE)}) : voir la docstring')
    _, d = c.lire(slug)
    dest = dossier(slug)
    (dest / 'trace').mkdir(exist_ok=True)
    taches = []
    for r in resoudre(d, lire_lot(slug)):
        e = r['e']
        if e is None or (seulement and e['cle'] not in seulement):
            continue
        for k in tirages(slug, e['nom']):
            src, sortie = dest / 'bruts' / f"{e['nom']}-g{k}.png", dest / 'trace' / f"{e['nom']}-g{k}"
            j = Path(f'{sortie}.json')
            if j.exists() and j.stat().st_mtime >= src.stat().st_mtime and Path(f'{sortie}-encre.webp').exists():
                continue
            taches.append((src, sortie))

    def un(t):
        r = subprocess.run([str(VENV), str(Path(__file__).with_name('vignettes_trace.py')), str(t[0]), str(t[1]), '--plein'], capture_output=True, text=True)
        if r.returncode:
            return f'{t[0].name} : ERREUR {r.stderr.strip()[-300:]}'
        i = json.loads(r.stdout)
        return f"{t[0].name} : encre {i['encre'][0]}×{i['encre'][1]}, {i['contours']} contours, {i['hachures']} petits traits, {i['octets'] / 1e3:.0f} ko"
    with ThreadPoolExecutor(6) as pool:
        for ligne in pool.map(un, taches):
            print(' ', ligne, flush=True)
    print(f'{len(taches)} tirage(s) tracé(s) dans {(dest / "trace").relative_to(c.RACINE)}')


def planche(slug: str) -> None:
    """Relecture : un montage par dessin (les trois tirages l'un sous l'autre, le centre caché grisé :
    releve/) et planche.html (maquette 16:10 avec l'image au rapprochement final, son fond prolongé, le
    tirage retenu qui se trace sur les deux bords en 8 s ; un clic sur un autre tirage le joue)."""
    from PIL import Image, ImageDraw
    _, d = c.lire(slug)
    slug = d['slug']
    lot = lire_lot(slug)
    dest = dossier(slug)
    (dest / 'releve').mkdir(exist_ok=True)
    items, scripts = [], []
    for r in resoudre(d, lot):
        v, e = r['v'], r['e']
        if e is None:
            continue
        ks = tirages(slug, e['nom'])
        if not ks:
            continue
        im = e['image']
        x0, x1 = centre(im)
        vues = []
        for k in ks:
            g = Image.open(dest / 'bruts' / f"{e['nom']}-g{k}.png").convert('L')
            g = g.resize((900, round(900 * g.height / g.width)), Image.LANCZOS).convert('RGB')
            dr = ImageDraw.Draw(g, 'RGBA')
            dr.rectangle((round(x0 * g.width), 0, round(x1 * g.width), g.height), fill=(120, 120, 120, 60))
            dr.text((4, 4), f"{e['cle']} tirage {k}", fill=(0, 0, 0))
            vues.append(g)
        m = Image.new('RGB', (900, sum(g.height + 10 for g in vues)), 'white')
        y = 0
        for g in vues:
            m.paste(g, (0, y)); y += g.height + 10
        m.save(dest / 'releve' / f"{e['nom']}.jpg", quality=86)
        tr = {}
        for k in ks:
            j = dest / 'trace' / f"{e['nom']}-g{k}.json"
            if j.exists():
                ident = f"{e['nom']}-g{k}"
                (dest / 'trace' / f'{ident}.js').write_text(f'(window.TR = window.TR || {{}})[{json.dumps(ident)}] = ' + j.read_text() + ';')
                scripts.append(f'<script src="trace/{ident}.js"></script>')
                tr[k] = ident
        x = e['x']
        f = fenetre(x, e['k'])
        items.append(dict(cle=e['cle'], nom=e['nom'], tirage=int(v.get('tirage') or ks[0]), tirages=tr,
                          jugement=v.get('jugement', ''), raison=v.get('raison', ''), gauche=v.get('gauche', ''), droite=v.get('droite', ''),
                          quand=v.get('quand', ''), texte=x['narration'][f['car'][0]:f['car'][1]], titre=im.get('titre_court') or im.get('titre'),
                          image=f"../../../../public/diaporamas/{slug}/{im['fichier']}", utile=im.get('utile') or [0, 0, 1, 1],
                          largeur=im['largeur'], hauteur=im['hauteur'], zoom=im.get('entier_zoom') or 1.3,
                          fond=f"../../../../public/diaporamas/{slug}/{im['fond']['fichier']}" if im.get('fond') else None,
                          boite=(im.get('fond') or {}).get('boite')))
    page = PLANCHE.replace('__TITRE__', html.escape(slug)).replace('__TRACES__', ''.join(scripts)).replace(
        '__DONNEES__', json.dumps(dict(items=items, style=lot.get('style', ''), duree=DUREE), ensure_ascii=False).replace('</', '<\\/'))
    (dest / 'planche.html').write_text(page, encoding='utf-8')
    print(f"{len(items)} dessins ; montages dans {(dest / 'releve').relative_to(c.RACINE)}, planche {(dest / 'planche.html').relative_to(c.RACINE)}")


PLANCHE = r'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,"><title>Dessins traversants : __TITRE__</title>
<style>
:root { --fond: #fbfaf7; --texte: #1a1a1a; --doux: #5c5c5c; --filet: #c8c5bd; }
* { box-sizing: border-box; }
html { background: var(--fond); color: var(--texte); font: 17px/1.45 'EB Garamond', Garamond, Georgia, serif; }
body { margin: 0 auto; padding: 1.2rem 16px 4rem; max-width: 1500px; }
h1 { font-weight: 500; margin: 0 0 .3rem; } .doux { color: var(--doux); } .sur { font-variant: small-caps; letter-spacing: .06em; color: var(--doux); }
section { border-top: 1px solid var(--filet); padding: .8rem 0; display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 1rem; }
@media (max-width: 900px) { section { grid-template-columns: 1fr; } }
.ecran { position: relative; aspect-ratio: 16 / 10; background: #000; overflow: hidden; }
.ecran > * { position: absolute; } .ecran .fond { background-size: 100% 100%; } .ecran .img { overflow: hidden; } .ecran .img img { position: absolute; max-width: none; }
.ecl { background: radial-gradient(closest-side, rgba(255,250,240,.42) 0%, rgba(255,250,240,.3) 55%, rgba(255,250,240,.12) 80%, rgba(255,250,240,0) 100%); }
.tirages { display: flex; flex-direction: column; gap: 6px; } .tirages img { width: 100%; border: 1px solid var(--filet); cursor: pointer; } .tirages img.retenu { border: 2px solid var(--texte); }
p { margin: .3rem 0; } .ecarte { opacity: .55; }
</style></head><body>
<p class="sur">Spec 17, dessins traversants (essai 5, révision du 2026-10-14) · planche de relecture · rien n'est publié par cette page</p>
<h1>Dessins traversants : __TITRE__</h1>
<p class="doux">Maquette 16:10 : l'image d'époque au rapprochement final, son fond prolongé, le dessin posé dessous à la hauteur de
l'image au repos, centré ; seuls ses deux bords se voient, chacun sur une éclaircie, et se tracent ensemble en 8 s. Dessins générés par
IA (Z-Image-Turbo) : relire personnage, cadre, faux texte, anachronisme, centre chargé (zone grisée des miniatures : cachée par l'image).</p>
<div id="liste"></div>
__TRACES__
<script>
const D = __DONNEES__;
const encres = {};
const encre = (id) => encres[id] || (encres[id] = Object.assign(new Image(), { src: `trace/${id}-encre.webp` }));
function jouer(sec, it, id) {
  const e = sec.querySelector('.ecran'), W = e.clientWidth, H = e.clientHeight, u = it.utile, T = TR[id], ink = encre(id), jeton = sec.jeton = {};
  const iw = it.largeur * (u[2] - u[0]), ih = it.hauteur * (u[3] - u[1]), s0 = Math.min(W / iw, H / ih), s = s0 * it.zoom;
  const dw = iw * s, dh = ih * s, x = (W - dw) / 2, y = (H - dh) / 2;
  const cadre = e.querySelector('.img'), img = cadre.firstChild, fond = e.querySelector('.fond');
  Object.assign(cadre.style, { left: x + 'px', top: y + 'px', width: dw + 'px', height: dh + 'px' });
  Object.assign(img.style, { width: it.largeur * s + 'px', height: it.hauteur * s + 'px', left: -u[0] * it.largeur * s + 'px', top: -u[1] * it.hauteur * s + 'px' });
  if (it.boite && fond) { const b = it.boite, w0 = dw / (b[2] - b[0]), h0 = dh / (b[3] - b[1]);
    Object.assign(fond.style, { left: x - w0 * b[0] + 'px', top: y - h0 * b[1] + 'px', width: w0 + 'px', height: h0 + 'px', filter: `blur(${(0.0025 * W).toFixed(1)}px) brightness(0.8)` }); }
  // Dessin : à la hauteur de l'image au repos, centré sur elle.
  const hr = ih * s0, top = (H - hr) / 2, wd = hr * T.l / T.h, left = W / 2 - wd / 2, can = e.querySelector('canvas');
  Object.assign(can.style, { left: left + 'px', top: top + 'px', width: wd + 'px', height: hr + 'px' });
  e.querySelectorAll('.ecl').forEach((el, j) => Object.assign(el.style, { top: top + 0.08 * hr + 'px', height: 0.84 * hr + 'px', width: x * 1.15 + 'px', left: (j ? x + dw - 0.075 * x : -0.075 * x) + 'px' }));
  const k = T.l / wd, g = (x - left) * k, dd = (x + dw - left) * k, visG = Math.max(0, -left * k), visD = Math.min(T.l, (W - left) * k);
  const S = T.t.map((t, i) => { const p = [[t[4], t[5]]]; for (let j = 6; j < t.length; j += 2) p.push([p.at(-1)[0] + t[j], p.at(-1)[1] + t[j + 1]]);
    const xs = p.map((q) => q[0]); return { w: t[0] / 10, c: t[3], i, p, x0: Math.min(...xs), x1: Math.max(...xs), L: p.reduce((a, q, j) => j ? a + Math.hypot(q[0] - p[j - 1][0], q[1] - p[j - 1][1]) : 0, 0) }; })
    .filter((t) => (t.x0 < g && t.x1 > visG) || (t.x1 > dd && t.x0 < visD));
  const ordre = (a, b) => (b.c - a.c) || (a.i - b.i);
  for (const G of [S.filter((t) => t.x0 < g).sort(ordre), S.filter((t) => t.x0 >= g).sort(ordre)]) {
    const tot = G.reduce((a, t) => a + Math.max(t.L, 1), 0) || 1; let acc = 0;
    for (const t of G) { t.a = acc / tot * D.duree; acc += Math.max(t.L, 1); t.b = acc / tot * D.duree; } }
  const M = document.createElement('canvas'); let t0 = null;
  const pas = (now) => {
    if (sec.jeton !== jeton) return;
    if (!ink.complete) { requestAnimationFrame(pas); return; }
    if (t0 === null) { t0 = now; can.width = M.width = ink.naturalWidth; can.height = M.height = ink.naturalHeight; }
    const t = (now - t0) / 1000, mx = M.getContext('2d'), q = M.width / T.l;
    mx.setTransform(q, 0, 0, q, 0, 0); mx.strokeStyle = '#fff'; mx.lineCap = mx.lineJoin = 'round';
    for (const s of S) { if (s.fait || t < s.a) continue; const f = Math.min(1, (t - s.a) / Math.max(1e-3, s.b - s.a)); let r = f * s.L;
      mx.lineWidth = s.w; mx.beginPath(); mx.moveTo(...s.p[0]);
      for (let i = 1; i < s.p.length && r > 0; i++) { const [ax, ay] = s.p[i - 1], [bx, by] = s.p[i], l = Math.hypot(bx - ax, by - ay); if (l <= r) { mx.lineTo(bx, by); r -= l; } else { mx.lineTo(ax + (bx - ax) * r / l, ay + (by - ay) * r / l); r = 0; } }
      if (s.L < 0.5) mx.lineTo(s.p[0][0] + 0.1, s.p[0][1]); mx.stroke(); if (f >= 1) s.fait = true; }
    const c2 = can.getContext('2d'); c2.globalCompositeOperation = 'source-over'; c2.clearRect(0, 0, can.width, can.height); c2.drawImage(ink, 0, 0);
    if (t < D.duree + 0.4) { c2.globalCompositeOperation = 'destination-in'; c2.drawImage(M, 0, 0);
      if (t > D.duree) { c2.globalCompositeOperation = 'destination-over'; c2.globalAlpha = (t - D.duree) / 0.4; c2.drawImage(ink, 0, 0); c2.globalAlpha = 1; } }
    c2.globalCompositeOperation = 'source-in'; c2.fillStyle = '#1a1714'; c2.fillRect(0, 0, can.width, can.height); c2.globalCompositeOperation = 'source-over';
    if (t < D.duree + 0.4) requestAnimationFrame(pas);
  };
  requestAnimationFrame(pas);
}
const liste = document.getElementById('liste');
for (const it of D.items) {
  const sec = document.createElement('section');
  if (it.jugement === 'ecarte') sec.className = 'ecarte';
  const ks = Object.keys(it.tirages);
  sec.innerHTML = `<div><div class="ecran">${it.fond ? `<div class="fond" style="background-image:url('${it.fond}')"></div>` : ''}<i class="ecl"></i><i class="ecl"></i><canvas></canvas><div class="img"><img src="${it.image}" alt=""></div></div>
    <p class="sur">${it.cle}${it.jugement ? ' · ' + it.jugement : ''}</p><p><i>${it.titre}</i></p>
    <p class="doux">« ${it.texte} »${it.quand ? `<br>Départ : « ${it.quand} »` : ''}</p>
    <p class="doux"><span class="sur">Gauche</span> ${it.gauche}<br><span class="sur">Droite</span> ${it.droite}</p>
    ${it.raison ? `<p><span class="sur">Relecture</span> ${it.raison}</p>` : ''}</div>
    <div class="tirages">${ks.map((k) => `<img data-k="${k}" class="${+k === it.tirage ? 'retenu' : ''}" src="bruts/${it.nom}-g${k}.png" alt="tirage ${k}" title="tirage ${k}">`).join('')}</div>`;
  liste.append(sec);
  const id = it.tirages[it.tirage] || it.tirages[ks[0]];
  sec.querySelectorAll('.tirages img').forEach((im) => im.onclick = () => { sec.querySelectorAll('.tirages img').forEach((j) => j.classList.toggle('retenu', j === im)); jouer(sec, it, it.tirages[im.dataset.k]); });
  if (id) new IntersectionObserver((es, o) => { if (es[0].isIntersecting) { jouer(sec, it, id); o.disconnect(); } }, { threshold: 0.4 }).observe(sec);
}
</script></body></html>'''


# --- Intégration à la période ----------------------------------------------------------------

def luminance_marges(slug: str, im: dict) -> float | None:
    """Luminance moyenne (0-1) du fond prolongé dans les deux marges, sur la hauteur où pose le dessin
    (bas de l'image) ; None sans fond prolongé."""
    from PIL import Image
    f = im.get('fond')
    if not f or not (c.PUBLIC / slug / f['fichier']).exists():
        return None
    with Image.open(c.PUBLIC / slug / f['fichier']) as fo:
        g = fo.convert('L')
        W, H = g.size
        x0, y0, x1, y1 = f['boite']
        haut, bas = int(H * (y0 + 0.3 * (y1 - y0))), max(int(H * y1), int(H * (y0 + 0.3 * (y1 - y0))) + 1)
        zones = [(0, haut, int(W * x0), bas), (int(W * x1), haut, W, bas)]
        vals = [sum(i * n for i, n in enumerate(g.crop(z).histogram())) / (255 * (z[2] - z[0]) * (z[3] - z[1]))
                for z in zones if z[2] - z[0] >= 2]
    return sum(vals) / len(vals) if vals else None


def encre(slug: str, im: dict) -> dict:
    """Champ « encre » du dessin : claire sur un fond sombre (sinon rien : encre sombre)."""
    lum = luminance_marges(slug, im)
    return {'encre': 'claire'} if lum is not None and lum < ENCRE_SEUIL else {}


def encres(slug: str, essai: bool) -> int:
    """Recalcule l'encre des dessins publiés d'après leur fond prolongé."""
    f, d = c.lire(slug)
    slug = d['slug']
    n = 0
    for e in images(d):
        v = e['image'].get('vignette')
        if not v:
            continue
        lum, avant = luminance_marges(slug, e['image']), v.get('encre')
        v.pop('encre', None)
        v.update(encre(slug, e['image']))
        n += v.get('encre') != avant
        print(f"  {e['cle']:>5} : marges {'?' if lum is None else f'{lum:.2f}'} → encre {v.get('encre', 'sombre')}"
              + (' (changée)' if v.get('encre') != avant else ''))
    if not essai:
        c.ecrire(f, d)
    print(f"{n} encre(s) {'à changer' if essai else 'changée(s)'} dans {slug}")
    return 0


def publier(slug: str, seulement: set[str], sauf: set[str], essai: bool) -> int:
    from PIL import Image
    f, d = c.lire(slug)
    slug = d['slug']
    lot = lire_lot(slug)
    dest = dossier(slug)
    publies, refus, ecartees, poids = [], [], [], 0
    for r in resoudre(d, lot):
        v, e = r['v'], r['e']
        n = cle(v.get('n', '?'))
        if (seulement and n not in seulement) or n in sauf:
            continue
        if v.get('jugement') != 'bon':
            ecartees.append(f"{n} ({v.get('jugement') or 'non relu'}{' : ' + v['raison'] if v.get('raison') else ''})")
            continue
        if r['pb']:
            refus.append(f"{n} : {'; '.join(r['pb'])}")
            continue
        k = int(v.get('tirage') or 0)
        src_e, src_t = dest / 'trace' / f"{e['nom']}-g{k}-encre.webp", dest / 'trace' / f"{e['nom']}-g{k}.json"
        if not k or not src_e.exists() or not src_t.exists():
            refus.append(f'{n} : tirage {k or "?"} non tracé (« tracer {slug} »)')
            continue
        publies.append((e, v, src_e, src_t))
    autres = sum(1 for e in images(d) if e['image'].get('vignette') and e['cle'] not in {p[0]['cle'] for p in publies})
    if len(publies) + autres > PLAFOND:
        refus.append(f'plus de {PLAFOND} dessins dans la période : rien n\'est publié')
        publies = []
    for e, v, src_e, src_t in publies:
        im = e['image']
        base = Path(im['fichier']).with_suffix('').as_posix() + SUFFIXE
        cible_e, cible_t = c.PUBLIC / slug / f'{base}.webp', c.PUBLIC / slug / f'{base}.json'
        with Image.open(src_e) as ink:
            L, H = ink.size
        brut = dest / 'bruts' / f"{e['nom']}-g{int(v['tirage'])}.png"
        if not essai:
            for s, t in ((src_e, cible_e), (src_t, cible_t)):
                if not t.exists() or t.read_bytes() != s.read_bytes():
                    shutil.copy(s, t)
            im['vignette'] = {'fichier': cible_e.name, 'traces': cible_t.name, 'centre': centre(im, L / H),
                              **({'quand': v['quand']} if v.get('quand') else {}),
                              'largeur': L, 'hauteur': H, **encre(slug, im), 'modele': lot.get('modele') or MODELE,
                              'genere_le': datetime.date.fromtimestamp(brut.stat().st_mtime).isoformat()}
        o = src_e.stat().st_size + src_t.stat().st_size
        poids += o
        print(f"  {e['cle']:>5} : {base}.webp {L}×{H} + tracés, {o / 1e3:.0f} ko")
    for x in refus:
        print(f'  REFUS {x}')
    if ecartees:
        print(f"  écartés ou non retenus : {', '.join(ecartees)}")
    if not essai:
        c.ecrire(f, d)
    print(f"{len(publies)} dessin(s) {'à publier' if essai else 'publié(s)'} dans {slug} ({poids / 1e6:.2f} Mo), {len(refus)} refus"
          + ('' if essai else f' ; puis : python3 scripts/diaporamas/verifier.py {slug} et npm run build'))
    return 1 if refus else 0


def retirer(slug: str, cibles: set[str], tout: bool) -> int:
    f, d = c.lire(slug)
    slug = d['slug']
    retires = []
    for e in images(d):
        v = e['image'].get('vignette')
        if not v or not (tout or e['cle'] in cibles):
            continue
        for k in ('fichier', 'traces'):
            if v.get(k):
                (c.PUBLIC / slug / v[k]).unlink(missing_ok=True)
        del e['image']['vignette']
        retires.append(e['cle'])
    c.ecrire(f, d)
    inconnues = sorted(cibles - set(retires))
    print(f"{len(retires)} dessin(s) retiré(s) de {slug} : {', '.join(retires) or 'aucun'}" + (f" ; sans dessin : {', '.join(inconnues)}" if inconnues else ''))
    return 0


def lister(slug: str) -> int:
    _, d = c.lire(slug)
    poids = n = 0
    for e in images(d):
        v = e['image'].get('vignette')
        if not v:
            continue
        ko = sum((c.PUBLIC / d['slug'] / v[k]).stat().st_size for k in ('fichier', 'traces') if (c.PUBLIC / d['slug'] / v[k]).exists()) / 1e3
        poids += ko
        n += 1
        print(f"  {e['cle']:>5} : {v['fichier']} {v['largeur']}×{v['hauteur']}, {ko:.0f} ko"
              f"{' ; dès « ' + v['quand'] + ' »' if v.get('quand') else ''} — {e['image'].get('titre_court') or e['image'].get('titre')}")
    print(f"{n} dessin(s) dans {d['slug']} (plafond {PLAFOND}), {poids / 1e3:.2f} Mo")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('commande', choices=['preparer', 'lancer', 'rapatrier', 'arreter', 'tracer', 'planche', 'publier', 'encres', 'retirer', 'lister'])
    ap.add_argument('slug')
    ap.add_argument('cibles', nargs='*', metavar='CLE', help='retirer : numéros actuels (31 34b)')
    ap.add_argument('--seulement', default='', help='lancer : noms de fichiers (031,034-b) ; tracer, publier : numéros (31,34b)')
    ap.add_argument('--sauf', default='', help='publier : numéros à laisser (31,34b)')
    ap.add_argument('--tout', action='store_true', help='retirer : tous les dessins de la période')
    ap.add_argument('--essai', action='store_true', help="publier, encres : n'écrit rien")
    ap.add_argument('--graines', default='1,2,3', help='tirages à calculer (ex. 1,2,3)')
    ap.add_argument('--gpu', default='L4')
    ap.add_argument('--session', default=None)
    ap.add_argument('--reprendre', action='store_true', help='session déjà ouverte')
    ap.add_argument('--garder', action='store_true', help='ne pas arrêter la session à la fin')
    ap.add_argument('--sans-suivi', action='store_true', help='lancer et rendre la main (session laissée ouverte)')
    a = ap.parse_args()
    session = a.session or f'vignettes-{a.slug}'
    cles = {cle(k) for k in a.seulement.split(',') if k.strip()} if a.commande != 'lancer' else set()
    if a.commande == 'preparer':
        preparer(a.slug)
    elif a.commande == 'lancer':
        lancer(a.slug, a.gpu, session, a.graines, a.seulement, a.reprendre, a.garder, a.sans_suivi)
    elif a.commande == 'rapatrier':
        rapatrier(a.slug, session)
    elif a.commande == 'arreter':
        fond.arreter(session)
    elif a.commande == 'tracer':
        tracer(a.slug, cles)
    elif a.commande == 'planche':
        planche(a.slug)
    elif a.commande == 'publier':
        sys.exit(publier(a.slug, cles, {cle(k) for k in a.sauf.split(',') if k.strip()}, a.essai))
    elif a.commande == 'encres':
        sys.exit(encres(a.slug, a.essai))
    elif a.commande == 'retirer':
        if not a.cibles and not a.tout:
            raise SystemExit('retirer : donner des cibles (31 34b) ou --tout')
        sys.exit(retirer(a.slug, {cle(k) for k in a.cibles}, a.tout))
    else:
        sys.exit(lister(a.slug))


if __name__ == '__main__':
    main()
