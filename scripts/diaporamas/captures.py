#!/usr/bin/env python3
"""Captures du lecteur de diaporamas avec une horloge factice (contrôles visuels, non-régression).

Usage (depuis la racine, après `npm run build` ou `npx astro build --outDir dist-xxx`) :

    python3 scripts/diaporamas/captures.py revolution 2:12.5 20:s10 1:c5 --appareil les-deux --planche
    python3 scripts/diaporamas/captures.py consulat-empire 65:s20 --dist dist-xxx --sortie /chemin/ref
    python3 scripts/diaporamas/captures.py revolution 2:12.5 --sortie apres --comparer avant

Plan : une liste d'instants, chacun `n[:instant]` :
  - `n` ou `n:t`  : diapositive n, voix à l'instant t (s ; 2 par défaut), en pause ;
  - `n:sT`        : segment joué après la voix de n (chant, lecture, épisode), à l'instant T, en pause ;
  - `n:cT`        : carton de l'acte qui commence à n, T secondes après son début (0 à 12).
Chaque capture se fait dans un onglet neuf (aucune reprise mémorisée ; « date précédente » de la
frise = diapositive 1), avec une horloge entièrement factice : `page.clock` (Playwright) pour
performance.now, minuteries et requestAnimationFrame, et un faux moteur audio (HORLOGE ci-dessous)
qui avance avec elle. Les animations CSS finies sont menées à leur terme avant la photo. Deux
passages du même plan sur le même build donnent donc des images identiques au pixel près.

Options : --appareil ordinateur|telephone|les-deux (1280×760 ; 390×844), --dist (dossier construit,
`dist` par défaut), --sortie (dossier des PNG), --planche (assemble planche.png), --comparer DOSSIER
(compare pixel à pixel aux PNG de même nom, code de sortie 1 en cas d'écart), --attente (ms
d'horloge factice avant de poser l'instant ; 2500 par défaut : entrée de l'image finie, frise du
bas encore affichée). Serveur statique intégré sur un port libre (`astro preview` refuse une
seconde instance) ; Chromium de Playwright trouvé automatiquement.
"""
from __future__ import annotations

import argparse
import functools
import glob
import http.server
import os
import re
import sys
import tempfile
import threading
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
APPAREILS = {'ordinateur': (1280, 760, 'o'), 'telephone': (390, 844, 't')}

# Faux moteur audio : play/pause/currentTime/paused/ended, remis à zéro quand la source change.
# Il lit performance.now, que page.clock rend factice : l'audio avance avec l'horloge factice.
HORLOGE = r"""
(() => {
  const P = HTMLMediaElement.prototype, S = new WeakMap();
  const st = (e) => { let s = S.get(e); if (!s) { s = { t: 0, paused: true, last: 0, ended: false }; S.set(e, s); } return s; };
  const dur = (e) => { const d = Object.getOwnPropertyDescriptor(P, 'duration').get.call(e); return isFinite(d) && d > 0 ? d : 1e9; };
  const now = (e) => { const s = st(e); return s.paused ? s.t : Math.min(dur(e), s.t + (performance.now() - s.last) / 1000); };
  const srcD = Object.getOwnPropertyDescriptor(P, 'src');
  Object.defineProperty(P, 'src', { get() { return srcD.get.call(this); }, set(v) { const s = st(this); s.t = 0; s.paused = true; s.ended = false; srcD.set.call(this, v); }, configurable: true });
  Object.defineProperty(P, 'currentTime', { get() { return now(this); }, set(v) { const s = st(this); s.t = +v; s.last = performance.now(); s.ended = false; this.dispatchEvent(new Event('seeked')); }, configurable: true });
  Object.defineProperty(P, 'paused', { get() { return st(this).paused; }, configurable: true });
  Object.defineProperty(P, 'ended', { get() { return st(this).ended; }, configurable: true });
  P.play = function () { const s = st(this); if (s.paused) { s.paused = false; s.last = performance.now(); this.dispatchEvent(new Event('play')); this.dispatchEvent(new Event('playing')); } return Promise.resolve(); };
  P.pause = function () { const s = st(this); if (!s.paused) { s.t = now(this); s.paused = true; this.dispatchEvent(new Event('pause')); } };
  setInterval(() => { document.querySelectorAll('audio,video').forEach((e) => { const s = st(e); if (!s.paused) { e.dispatchEvent(new Event('timeupdate')); if (now(e) >= dur(e) - 0.01) { s.t = dur(e); s.paused = true; s.ended = true; e.dispatchEvent(new Event('pause')); e.dispatchEvent(new Event('ended')); } } }); }, 100);
})();
"""


def chromium() -> str | None:
    """Exécutable Chromium du cache de Playwright (le plus récent), ou None (choix de Playwright)."""
    base = os.environ.get('PLAYWRIGHT_BROWSERS_PATH') or str(Path.home() / ('Library/Caches/ms-playwright' if sys.platform == 'darwin' else '.cache/ms-playwright'))
    motifs = ['chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell',
              'chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium',
              'chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
              'chromium-*/chrome-linux*/chrome']
    for m in motifs:
        trouves = sorted(glob.glob(os.path.join(base, m)), key=lambda p: int(re.search(r'-(\d+)/', p).group(1)), reverse=True)
        if trouves:
            return trouves[0]
    return None


def serveur(dossier: Path) -> tuple[http.server.ThreadingHTTPServer, int]:
    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    class Serveur(http.server.ThreadingHTTPServer):
        def handle_error(self, *a):  # connexions coupées par le navigateur (médias abandonnés)
            pass
    srv = Serveur(('127.0.0.1', 0), functools.partial(Silencieux, directory=str(dossier)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def analyser(item: str) -> tuple[int, str, float]:
    m = re.fullmatch(r'(\d+)(?::([sc]?)(\d+(?:\.\d+)?))?', item)
    if not m:
        sys.exit(f'Instant illisible : {item!r} (attendu n, n:t, n:sT ou n:cT)')
    return int(m.group(1)), m.group(2) or '', float(m.group(3)) if m.group(3) else 2.0


def nom_fichier(tag: str, item: str) -> str:
    return f"{tag}-{item.replace(':', '_')}.png"


def capturer(navigateur, url: str, appareil: str, item: str, attente: int, chemin: Path) -> list[str]:
    w, h, _ = APPAREILS[appareil]
    n, genre, t = analyser(item)
    erreurs: list[str] = []
    ctx = navigateur.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, reduced_motion='no-preference')
    pg = ctx.new_page()
    pg.on('pageerror', lambda e: erreurs.append(str(e)))
    pg.clock.install(time=datetime(2026, 1, 1))
    pg.clock.pause_at(datetime(2026, 1, 1, 0, 0, 1))  # horloge arrêtée : n'avance que par run_for
    pg.add_init_script(HORLOGE)
    pg.goto(url, wait_until='load')
    pg.wait_for_timeout(600)
    pg.click('[data-action="lancer"]')
    pg.clock.run_for(100)
    r = "document.querySelector('.diaporama')"
    if genre == 'c':
        if pg.evaluate(f"() => {r}.querySelector('.lecteur__n').textContent") != str(n):
            pg.evaluate(f"() => {r}.__aller({n})")
        pg.wait_for_timeout(400)               # décodage des images (temps réel)
        pg.clock.run_for(int(t * 1000))
    elif genre == 's':
        pg.evaluate(f"() => {r}.__aller({n}, true)")
        pg.wait_for_timeout(400)
        pg.clock.run_for(attente)
        pg.evaluate(f"() => {{ const a = {r}.querySelector('.lecteur__suite'); a.currentTime = {t}; a.pause(); }}")
        pg.clock.run_for(500)
    else:
        pg.evaluate(f"() => {r}.__aller({n})")
        if pg.evaluate(f"() => {r}.querySelector('.lecteur').classList.contains('en-carton')"):
            pg.evaluate(f"() => {r}.querySelector('.lecteur__carton').click()")
        pg.wait_for_timeout(400)
        pg.clock.run_for(attente)
        pg.evaluate(f"() => {{ const a = {r}.querySelector('.lecteur__audio'); a.currentTime = {t}; a.pause(); }}")
        pg.clock.run_for(500)
    pg.wait_for_timeout(300)
    boite = pg.evaluate(f"() => {{ const b = {r}.querySelector('.lecteur').getBoundingClientRect(); return {{ x: b.x + scrollX, y: b.y + scrollY, width: b.width, height: b.height }}; }}")
    boite['width'] = min(boite['width'], w - boite['x'])
    pg.screenshot(path=str(chemin), clip=boite, full_page=True, animations='disabled', caret='hide')
    ctx.close()
    return erreurs


def planche(images: list[Path], sortie: Path) -> None:
    from PIL import Image, ImageDraw
    vignettes = []
    for p in images:
        im = Image.open(p).convert('RGB')
        im.thumbnail((640, 640))
        cadre = Image.new('RGB', (im.width, im.height + 22), 'white')
        cadre.paste(im, (0, 22))
        ImageDraw.Draw(cadre).text((4, 4), p.stem, fill='black')
        vignettes.append(cadre)
    col = 3
    lignes = [vignettes[k:k + col] for k in range(0, len(vignettes), col)]
    W = max(sum(v.width for v in l) + 8 * (len(l) - 1) for l in lignes)
    H = sum(max(v.height for v in l) for l in lignes) + 8 * (len(lignes) - 1)
    pl = Image.new('RGB', (W, H), (200, 200, 200))
    y = 0
    for l in lignes:
        x = 0
        for v in l:
            pl.paste(v, (x, y))
            x += v.width + 8
        y += max(v.height for v in l) + 8
    pl.save(sortie)


def comparer(images: list[Path], reference: Path) -> int:
    """Compare chaque PNG à son homonyme de `reference` ; écrit `ecart-<nom>` (pixels différents en noir)."""
    from PIL import Image, ImageChops
    ecarts = 0
    for p in images:
        q = reference / p.name
        if not q.exists():
            print(f'  {p.name} : absente de la référence'); ecarts += 1; continue
        a, b = Image.open(p).convert('RGB'), Image.open(q).convert('RGB')
        if a.size != b.size:
            print(f'  {p.name} : tailles différentes {a.size} / {b.size}'); ecarts += 1; continue
        diff = ImageChops.difference(a, b)
        boite = diff.getbbox()
        if boite is None:
            print(f'  {p.name} : identique')
            continue
        masque = diff.convert('L').point(lambda v: 255 if v else 0)
        nb = sum(1 for v in masque.getdata() if v)
        print(f'  {p.name} : {nb} pixels différents (écart max {max(e[1] for e in diff.getextrema())}), zone {boite}')
        Image.composite(Image.new('RGB', a.size, 'black'), Image.new('RGB', a.size, 'white'), masque).save(p.with_name('ecart-' + p.name))
        ecarts += 1
    print(f'{len(images) - ecarts}/{len(images)} captures identiques')
    return ecarts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('slug')
    ap.add_argument('plan', nargs='+', help='instants n[:t], n:sT, n:cT')
    ap.add_argument('--appareil', choices=['ordinateur', 'telephone', 'les-deux'], default='ordinateur')
    ap.add_argument('--dist', default='dist')
    ap.add_argument('--sortie')
    ap.add_argument('--planche', action='store_true')
    ap.add_argument('--comparer')
    ap.add_argument('--attente', type=int, default=2500)
    a = ap.parse_args()
    dist = (RACINE / a.dist) if not Path(a.dist).is_absolute() else Path(a.dist)
    if not (dist / 'diaporamas' / a.slug / 'index.html').exists():
        sys.exit(f'{dist}/diaporamas/{a.slug}/index.html introuvable : construire le site d\'abord')
    sortie = Path(a.sortie) if a.sortie else Path(tempfile.gettempdir()) / f'captures-{a.slug}'
    sortie.mkdir(parents=True, exist_ok=True)
    appareils = ['ordinateur', 'telephone'] if a.appareil == 'les-deux' else [a.appareil]
    from playwright.sync_api import sync_playwright
    srv, port = serveur(dist)
    url = f'http://127.0.0.1:{port}/diaporamas/{a.slug}/'
    images: list[Path] = []
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch(executable_path=chromium(), args=['--autoplay-policy=no-user-gesture-required'])
            for app in appareils:
                for item in a.plan:
                    chemin = sortie / nom_fichier(APPAREILS[app][2], item)
                    for e in capturer(nav, url, app, item, a.attente, chemin):
                        print(f'  erreur de page ({chemin.name}) : {e}')
                    images.append(chemin)
            nav.close()
    finally:
        srv.shutdown()
    print(f'{len(images)} captures dans {sortie}')
    if a.planche:
        planche(images, sortie / 'planche.png')
        print(f'planche : {sortie / "planche.png"}')
    if a.comparer:
        sys.exit(1 if comparer(images, Path(a.comparer)) else 0)


if __name__ == '__main__':
    main()
