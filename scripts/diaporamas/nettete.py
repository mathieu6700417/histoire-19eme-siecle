#!/usr/bin/env python3
"""Netteté des images (spec 17, « Netteté : règles d'intégration ») : une variante « grand écran » de
chaque image trop petite pour le cadre le plus serré de sa caméra.

    python3 scripts/diaporamas/nettete.py mesurer <slug> [--dist dist]   # relevé dans le lecteur construit
    python3 scripts/diaporamas/nettete.py preparer <slug> [--seulement 83 34b …]
    python3 scripts/diaporamas/nettete.py lancer <slug> [--gpu L4] [--session nom] [--garder] [--reprendre]
    python3 scripts/diaporamas/nettete.py accorder <slug>                # couleurs des images agrandies (fait par lancer)
    python3 scripts/diaporamas/nettete.py publier <slug> [--seulement …]
    python3 scripts/diaporamas/nettete.py retirer <slug> 83 34b …        # ou --tout
    python3 scripts/diaporamas/nettete.py lister <slug>
    python3 scripts/diaporamas/nettete.py planche <slug>                 # relecture des images agrandies par IA

Principe. L'image servie (NNN.webp, 1 600 px au plus) ne change pas : zone utile, caméra, clip, version
colorisée, livre d'images et téléphone restent tels quels. On lui ajoute une variante de mêmes
proportions, `NNN-grand.webp` (plan : `NNN-b-grand.webp`), que le lecteur ne charge que sur un grand
écran (`etat.ts` : `grandEcran`), dans la même boîte : aucun cadre ne bouge, seule la finesse change.

`mesurer` ouvre la page construite (`npm run build`) dans le vrai Chrome sans fenêtre, en plein écran
1920 × 1080, et relève par le crochet `__camera` le cadre le plus serré de l'image de chaque
diapositive (ouverture d'acte comprise) et de chaque plan (spec 14), au pas de 0,1 s. Il en tire la
largeur qu'il faudrait pour 1 pixel d'image par pixel d'écran (grand côté plafonné à COTE_MAX, 2 560 px),
la compare à l'original de Commons recadré comme l'image servie, et décide :
  - `rien`      l'image servie suffit (au plus SEUIL_BESOIN, 1,3 px d'écran par px d'image, au cadre le
                plus serré), ou l'original n'apporte pas GAIN_MIN de plus ;
  - `original`  un fichier plus grand tiré de l'original suffit (au plus SEUIL_IA px d'écran par px) ;
  - `ia`        l'original laisse plus de SEUIL_IA : Real-ESRGAN x4plus (BSD-3) sur l'original, puis
                réduction à la largeur utile.
La Révolution, pilote commité, garde ses réglages d'alors (REGLAGES_PILOTE : 3 200 px, seuil 1).
Mosaïques (vignettes), avant / après (image « après »), objets, médaillons, cartes, galeries, lectures
et épisodes : hors champ. Résultat : .cache/diaporamas/<slug>/nettete/mesure.json.

`preparer` télécharge les originaux (cache commun .cache/diaporamas/originaux/), fabrique les variantes
`original` dans .cache/diaporamas/<slug>/nettete/grand/ et le kit Colab des images `ia`
(kit-nettete.zip : sources PNG et manifeste). `lancer` pilote Colab par la CLI officielle (script
scripts/colab/nettete.py, session arrêtée à la fin, même en cas d'erreur), puis accorde les couleurs
des images agrandies à celles de l'original (`accorder` : le modèle les décale un peu). `publier` copie les variantes
dans public/<siecle>/diaporamas/<slug>/ et écrit `image.grand` { fichier, largeur, hauteur, source (« original »
ou « ia »), et pour l'IA : modele, facteur, genere_le } ; idempotent. Une image colorisée (`image.couleur`, spec 16) reçoit aussi sa version colorisée à la même finesse,
`NNN-couleur-grand.webp` (`grand.couleur` { fichier, largeur, hauteur } : couleur + (variante − image
servie), sans modèle ; voir `couleur_grande`). `renumeroter.py` suit fichiers et
champs ; `verifier.py` contrôle la famille « netteté (spec 17) ». Signalement des images agrandies par
IA : crédits de la page et livre d'images seulement, rien au cartouche.
"""
from __future__ import annotations

import datetime, functools, http.server, io, json, shutil, subprocess, sys, threading, time, zipfile
from pathlib import Path

from PIL import Image

import commun as c
import couleur as co
from generation import colab, une_seule_session   # CLI colab, tuée et refaite si elle ne répond pas ; règle d'une seule session

Image.MAX_IMAGE_PIXELS = None
ECRAN = 1920            # largeur de l'écran de référence (plein écran 1920 × 1080)
COTE_MAX = 2560         # grand côté d'une variante, au plus (2 560 px depuis le 2026-10-14)
SEUIL_BESOIN = 1.3      # pas de variante si l'image servie laisse au plus 1,3 px d'écran par px d'image
SEUIL_IA = 1.25         # px d'écran par px d'image que l'original peut laisser sans qu'on passe à l'IA
# Pilote de la Révolution (2026-10-12), validé et commité avec les réglages d'alors : 3 200 px, une
# variante dès que l'image servie laisse plus de 1 px d'écran par px. Gardés pour elle seule, afin
# qu'une nouvelle mesure ne la republie pas (spec 17, « Netteté : poids, et généralisation »).
REGLAGES_PILOTE = {'revolution': dict(cote_max=3200, seuil_besoin=1.0)}


def reglages(slug: str) -> dict:
    """Plafond du grand côté et seuil de besoin de la période (les réglages du 2026-10-14, sauf pilote)."""
    return REGLAGES_PILOTE.get(slug, dict(cote_max=COTE_MAX, seuil_besoin=SEUIL_BESOIN))
GAIN_MIN = 1.15         # une variante doit être au moins 15 % plus large que l'image servie
QUALITE = 74            # WebP, comme les images du site
QUALITE_BRUT = 92       # sortie de Colab, avant l'accord des couleurs (réencodée ensuite à QUALITE)
RAYON_ACCORD = 0.012    # flou de l'accord des couleurs, en fraction du grand côté
MODELE = 'Real-ESRGAN x4plus'
SUFFIXE = '-grand.webp'
SUFFIXE_COULEUR = '-couleur-grand.webp'   # version colorisée d'une image à variante (spec 16 × 17)
REMOTE = '/content/nettete'


def dossier(slug: str) -> Path:
    d = c.CACHE / slug / 'nettete'
    d.mkdir(parents=True, exist_ok=True)
    return d


def nom_grand(image: dict) -> str:
    return Path(image['fichier']).with_suffix('').as_posix() + SUFFIXE


def nom_couleur_grand(image: dict) -> str:
    return Path(image['fichier']).with_suffix('').as_posix() + SUFFIXE_COULEUR


def couleur_grande(slug: str, i: dict, grand: Path) -> dict | None:
    """Version colorisée à la finesse de la variante, pour une image qui porte les deux (`image.couleur`,
    spec 16, et `image.grand`). Le lecteur pose la couleur sur l'image après un fondu lent et l'y laisse :
    à 1 600 px, elle masquerait la finesse de la variante pendant la plus grande part de la diapositive.
    Aucun calcul de modèle : couleur + (variante − image servie), sur la zone que couvre la couleur.
    Les couleurs restent exactement celles de la version relue, seul le détail vient de la variante (le
    trait de l'original, ou celui de Real-ESRGAN). Mêmes proportions que la version colorisée : le
    lecteur la pose dans la même boîte (`couleur.ts`). Rend le champ `grand.couleur`, ou None."""
    import numpy as np
    coul = i.get('couleur')
    if not coul:
        return None
    L, H = i['largeur'], i['hauteur']
    x0, y0, _, _ = co.zone_px(i)
    x1, y1 = x0 + coul['largeur'], y0 + coul['hauteur']
    G = Image.open(grand).convert('RGB')
    k = G.width / L
    boite = (round(x0 * k), round(y0 * k), min(G.width, round(x1 * k)), min(G.height, round(y1 * k)))
    g = G.crop(boite)
    S = Image.open(c.PUBLIC / slug / i['fichier']).convert('RGB').crop((x0, y0, x1, y1)).resize(g.size, Image.LANCZOS)
    C = Image.open(c.PUBLIC / slug / coul['fichier']).convert('RGB').resize(g.size, Image.LANCZOS)
    a = lambda im: np.asarray(im, dtype=np.int16)
    sortie = c.PUBLIC / slug / nom_couleur_grand(i)
    Image.fromarray(np.clip(a(C) + a(g) - a(S), 0, 255).astype(np.uint8)).save(sortie, 'WEBP', quality=QUALITE, method=6)
    return dict(fichier=sortie.name, largeur=g.width, hauteur=g.height)


def cibles(args: list[str]) -> set[str]:
    return {co.cle(a) for a in args if not a.startswith('--')}


# --- Mesure ------------------------------------------------------------------------------------

RELEVE = """() => {
  const r = document.querySelector('.diaporama');
  const D = JSON.parse(r.querySelector('.diaporama__donnees').textContent);
  const out = {};
  const voir = (cle, v, t) => { const l = v[2] - v[0]; if (!out[cle] || l < out[cle].l - 1e-6) out[cle] = { l, t: +t.toFixed(1), vue: v.map((x) => +x.toFixed(5)) }; };
  for (const x of D.diapos) {
    const d = x.duree || 6, P = x.plans || [];
    for (let t = x.ouv ? -3.5 : 0; t <= d + 0.001; t += 0.1) {
      const c = r.__camera(x.n, t);
      if (!c) continue;
      // Image de la diapositive : jusqu'à la fin du fondu vers le premier plan (ou l'image « après »).
      if ((!P.length || t <= P[0].t + 0.8) && (!x.ap || t <= x.ap.t + 2)) voir(String(x.n), c.cadre, t);
      c.plans.forEach((p, k) => { if (t >= p.t - 0.3 && (k + 1 >= P.length || t <= P[k + 1].t + 0.8)) voir(x.n + 'bcdefgh'[k], p.cadre, t); });
    }
  }
  return out; }"""


def relever(slug: str, dist: Path) -> dict:
    """Cadre le plus serré de chaque image (fractions de sa zone utile), relevé dans le lecteur construit."""
    from playwright.sync_api import sync_playwright
    if not (c.dist_diaporama(dist, slug) / 'index.html').is_file():
        raise SystemExit(f'Page absente de {dist} : lancer « npm run build » d\'abord')

    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Silencieux, directory=str(dist)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        pg = b.new_page(viewport={'width': ECRAN, 'height': 1080})
        pg.goto(f'http://127.0.0.1:{srv.server_address[1]}{c.url_diaporama(slug)}', wait_until='load')
        pg.wait_for_timeout(800)
        pg.click('[data-action="lancer"]')
        pg.wait_for_timeout(400)
        pg.evaluate("() => { const r = document.querySelector('.diaporama'); r.__generique && r.__generique('passer'); }")
        pg.wait_for_timeout(300)
        pg.click('[data-action="plein-ecran"]')
        pg.wait_for_timeout(1200)
        scene = pg.evaluate("() => { const s = document.querySelector('.lecteur__scene'); return [s.clientWidth, s.clientHeight]; }")
        if scene != [ECRAN, 1080]:
            raise SystemExit(f'Plein écran non obtenu (scène {scene}) : mesure abandonnée')
        releve = pg.evaluate(RELEVE)
        b.close()
    srv.shutdown()
    return releve


def decider(image: dict, vue_l: float, original: tuple[int, int], cote_max: int = COTE_MAX, seuil_besoin: float = SEUIL_BESOIN) -> dict:
    """Largeur utile et décision pour une image dont la vue la plus serrée fait `vue_l` de sa zone utile."""
    L, H = image['largeur'], image['hauteur']
    u = image.get('utile') or [0, 0, 1, 1]
    rc = image.get('recadrage') or [0, 0, 1, 1]
    besoin = ECRAN / (vue_l * (u[2] - u[0]))                 # largeur d'image pour 1 px d'écran par px d'image
    cible = min(besoin, cote_max * L / max(L, H))            # grand côté plafonné
    lo = original[0] * (rc[2] - rc[0])                       # largeur de l'original, recadré comme l'image servie
    r = dict(servie=[L, H], original=list(original), original_recadre=round(lo), besoin=round(besoin),
             densite_servie=round(besoin / L, 2), densite_original=round(besoin / lo, 2))
    if besoin <= L * seuil_besoin or cible < L * GAIN_MIN:
        return dict(r, decision='rien', motif='image servie suffisante')
    if lo * SEUIL_IA >= cible:
        largeur = round(min(cible, lo))
        if largeur < L * GAIN_MIN:
            return dict(r, decision='rien', motif='original à peine plus grand que l\'image servie')
        source = 'original'
    else:
        largeur, source = round(min(cible, 4 * lo)), 'ia'
    return dict(r, decision=source, largeur=largeur, hauteur=round(largeur * H / L), densite_finale=round(besoin / largeur, 2))


def mesurer(slug: str, dist: Path) -> None:
    f, d = c.lire(slug)
    releve = relever(slug, dist)
    imgs = co.images(d)
    rg = reglages(slug)
    infos = c.infos_fichiers([e['image']['commons'] for e in imgs])
    mesure = {}
    for e in imgs:
        i = e['image']
        v = releve.get(e['cle'])
        info = infos.get(i['commons'], {'manquant': True})
        if not v or info.get('manquant') or not i.get('largeur'):
            continue
        # `image.rotation` (images.py) : l'original se compte redressé, comme l'image servie.
        original = (info['largeur'], info['hauteur'])
        if (i.get('rotation') or 0) % 180:
            original = original[::-1]
        m = decider(i, v['l'], original, **rg)
        if i.get('rotation'):
            m['rotation'] = i['rotation']
        m.update(cle=e['cle'], commons=i['commons'], titre=i.get('titre_court') or i.get('titre'), auteur=i.get('auteur'), technique=i.get('technique'),
                 vue=v['vue'], instant=v['t'], utile=i.get('utile') or [0, 0, 1, 1], recadrage=i.get('recadrage'), url=info['url'],
                 plan=e['plan'] is not None)
        mesure[e['cle']] = m
    (dossier(slug) / 'mesure.json').write_text(json.dumps(dict(slug=slug, ecran=ECRAN, **rg, seuil_ia=SEUIL_IA, images=mesure), ensure_ascii=False, indent=1))
    nb = {k: sum(m['decision'] == k for m in mesure.values()) for k in ('rien', 'original', 'ia')}
    ds = sorted(m['densite_servie'] for m in mesure.values())
    print(f"{len(mesure)} image(s) mesurée(s) ({sum(m['plan'] for m in mesure.values())} plan(s)) ; px d'écran par px servi : médiane {ds[len(ds) // 2]}, maximum {ds[-1]}")
    print(f"décision : {nb['rien']} sans changement, {nb['original']} par l'original de Commons, {nb['ia']} par {MODELE}")
    for m in sorted(mesure.values(), key=lambda m: -m['densite_original']):
        if m['decision'] == 'ia':
            print(f"  ia {m['cle']:>4} : original {m['original_recadre']} px pour {m['besoin']} utiles (×{m['densite_original']}) → {m['largeur']}×{m['hauteur']} · {(m['titre'] or '')[:60]}")


def lire_mesure(slug: str) -> dict:
    f = dossier(slug) / 'mesure.json'
    if not f.exists():
        raise SystemExit(f'Mesure absente : lancer « nettete.py mesurer {slug} » d\'abord')
    return json.loads(f.read_text())['images']


# --- Fabrication -------------------------------------------------------------------------------

def original_recadre(m: dict, largeur_mini: int) -> Image.Image:
    """L'original de Commons (ou une version réduite d'au moins `largeur_mini` px une fois recadrée),
    recadré comme l'image servie, en RVB."""
    import images as im_mod
    rc = m['recadrage'] or [0, 0, 1, 1]
    rot = m.get('rotation') or 0                              # `original` est compté redressé (mesurer)
    demande = min(m['original'][0], round(largeur_mini / (rc[2] - rc[0])) + 8)
    url = m['url']
    if demande < m['original'][0] * 0.9:
        # Version réduite servie par Commons : un original de 12 000 px pèse des dizaines de Mo.
        # Commons compte la largeur de l'original non tourné.
        largeur_commons = round(demande * m['original'][1] / m['original'][0]) if rot % 180 else demande
        info = c.infos_fichiers([m['commons']], largeur=largeur_commons)[m['commons']]
        url = info.get('vignette') or url
    im = im_mod.tourner(Image.open(io.BytesIO(im_mod.telecharger(url))), rot)
    im.load()
    if im.width < demande * 0.98 and url != m['url']:        # Commons a servi plus petit que demandé : l'original
        im = im_mod.tourner(Image.open(io.BytesIO(im_mod.telecharger(m['url']))), rot)
        im.load()
    if im.mode not in ('RGB', 'L'):
        fond = Image.new('RGB', im.size, (251, 250, 247))
        im = im.convert('RGBA')
        fond.paste(im, mask=im.split()[-1])
        im = fond
    im = im.convert('RGB')
    return im.crop((round(rc[0] * im.width), round(rc[1] * im.height), round(rc[2] * im.width), round(rc[3] * im.height)))


def preparer(slug: str, seulement: set[str]) -> None:
    mesure = lire_mesure(slug)
    dest = dossier(slug)
    (dest / 'grand').mkdir(exist_ok=True)
    sources = dest / 'sources'
    sources.mkdir(exist_ok=True)
    elements, faits = [], 0
    for cle, m in mesure.items():
        if m['decision'] == 'rien' or (seulement and cle not in seulement):
            continue
        if m['decision'] == 'original':
            sortie = dest / 'grand' / f'{cle}.webp'
            if not sortie.exists():
                im = original_recadre(m, m['largeur'])
                if im.width < m['largeur'] * 0.98:
                    print(f"  {cle:>4} : original recadré de {im.width} px seulement ({m['largeur']} attendus) : ignoré, relancer mesurer")
                    continue
                im.resize((m['largeur'], m['hauteur']), Image.LANCZOS).save(sortie, 'WEBP', quality=QUALITE, method=6)
            faits += 1
        else:
            src = sources / f'{cle}.png'
            if not src.exists():
                original_recadre(m, m['original'][0]).save(src)
            elements.append(dict(cle=cle, source=f'sources/{cle}.png', largeur=m['largeur'], hauteur=m['hauteur']))
    (dest / 'manifeste.json').write_text(json.dumps(dict(slug=slug, modele=MODELE, qualite=QUALITE_BRUT, elements=elements), ensure_ascii=False, indent=1))
    with zipfile.ZipFile(dest / 'kit-nettete.zip', 'w', zipfile.ZIP_STORED) as z:
        z.write(dest / 'manifeste.json', 'manifeste.json')
        for el in elements:
            z.write(dest / el['source'], el['source'])
    poids = sum(f.stat().st_size for f in (dest / 'grand').glob('*.webp'))
    print(f"{faits} variante(s) tirée(s) de l'original ({poids / 1e6:.1f} Mo dans {(dest / 'grand').relative_to(c.RACINE)}/) ; "
          f"{len(elements)} image(s) pour {MODELE} : kit {(dest / 'kit-nettete.zip').stat().st_size / 1e6:.0f} Mo")


def lancer(slug: str, gpu: str, session: str | None, garder: bool, reprendre: bool) -> None:
    dest = dossier(slug)
    kit = dest / 'kit-nettete.zip'
    if not kit.exists():
        raise SystemExit(f'Kit absent : lancer « nettete.py preparer {slug} » d\'abord')
    session = session or f'nettete-{slug}'
    R = REMOTE
    if not reprendre:
        une_seule_session(session)
        print(f'session « {session} » ({gpu})…')
        colab('new', '-s', session, '--gpu', gpu, timeout=600)
    try:
        colab('exec', '-s', session, '--timeout', '60', timeout=90, code=f'import os; os.makedirs("{R}/in", exist_ok=True); os.makedirs("{R}/out", exist_ok=True)')
        # Sources envoyées une à une (un kit de 90 Mo d'un bloc a échoué le 2026-10-12 : connexion coupée).
        man = json.loads((dest / 'manifeste.json').read_text())
        colab('exec', '-s', session, '--timeout', '60', timeout=90, code=f'import os; os.makedirs("{R}/in/sources", exist_ok=True)')
        colab('upload', '-s', session, str(dest / 'manifeste.json'), f'{R}/in/manifeste.json', silencieux=True)
        for el in man['elements']:
            for essai in range(3):
                try:
                    colab('upload', '-s', session, str(dest / el['source']), f"{R}/in/{el['source']}", timeout=300, silencieux=True)
                    break
                except SystemExit as e:
                    if essai == 2:
                        raise
                    print(f"  (envoi de {el['source']} en échec, nouvel essai : {str(e)[:120]})")
        print(f"{len(man['elements'])} source(s) envoyée(s)")
        colab('upload', '-s', session, str(c.RACINE / 'scripts' / 'colab' / 'nettete.py'), f'{R}/nettete.py')
        colab('exec', '-s', session, '--timeout', '120', timeout=150, code=(
            f'import subprocess; '
            f'subprocess.Popen("nohup env ENTREE={R}/in SORTIE={R}/out python3 {R}/nettete.py > {R}/out/log.txt 2>&1 &", shell=True); print("lancé")'))
        lu, debut = 0, time.time()
        while True:
            time.sleep(30)
            try:
                texte = colab('exec', '-s', session, '--timeout', '30', timeout=60, essais=1, silencieux=True,
                              code=f'import os; p="{R}/out/log.txt"; print(open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else "")')
            except (SystemExit, subprocess.TimeoutExpired) as e:
                print(f'  (lecture du journal impossible : {e})')
                continue
            lignes = [l for l in texte.splitlines() if l[:2].isdigit() and l[2:3] == ':']
            for l in lignes[lu:]:
                print(l)
            lu = len(lignes)
            if any(l.endswith(' FIN') or ' ERREUR ' in l for l in lignes[-2:]):
                break
            if time.time() - debut > 3600:
                print('plus d\'une heure : on arrête le suivi')
                break
        colab('exec', '-s', session, '--timeout', '120', timeout=150, code=f'import subprocess; subprocess.run("cd {R}/out && rm -f ../sorties.zip && zip -q -0 -r ../sorties.zip .", shell=True)')
        colab('download', '-s', session, f'{R}/sorties.zip', str(dest / 'sorties.zip'), timeout=1200, silencieux=True)
        (dest / 'ia-brut').mkdir(exist_ok=True)
        with zipfile.ZipFile(dest / 'sorties.zip') as z:
            z.extractall(dest / 'ia-brut')
        (dest / 'sorties.zip').unlink()
        print(f"{len(list((dest / 'ia-brut').glob('*.webp')))} image(s) agrandie(s) dans {(dest / 'ia-brut').relative_to(c.RACINE)}/")
        accorder(slug)
    finally:
        if garder:
            print(f'session « {session} » laissée ouverte (colab stop -s {session})')
        else:
            colab('stop', '-s', session, timeout=300)
            print(f'session « {session} » arrêtée ; vérifier : colab sessions')


def accorder(slug: str) -> None:
    """Accord des couleurs des images agrandies (ia-brut/ → ia/) : Real-ESRGAN décale un peu la teinte,
    la saturation et la clarté (mesuré le 2026-10-12 : jusqu'à 5 niveaux sur 255 de clarté, et une
    saturation en baisse sur presque toutes). On rend à l'image agrandie les basses fréquences de
    l'original : agrandie + flou(original) − flou(agrandie). Le détail vient du modèle, la couleur
    et la lumière du document."""
    import numpy as np
    from PIL import ImageFilter
    dest = dossier(slug)
    (dest / 'ia').mkdir(exist_ok=True)
    for brut in sorted((dest / 'ia-brut').glob('*.webp')):
        src = dest / 'sources' / f'{brut.stem}.png'
        if not src.exists():
            continue
        v = Image.open(brut).convert('RGB')
        o = Image.open(src).convert('RGB').resize(v.size, Image.LANCZOS)
        r = max(v.size) * RAYON_ACCORD
        d = np.asarray(o.filter(ImageFilter.GaussianBlur(r)), dtype=np.int16) - np.asarray(v.filter(ImageFilter.GaussianBlur(r)), dtype=np.int16)
        Image.fromarray(np.clip(np.asarray(v, dtype=np.int16) + d, 0, 255).astype(np.uint8)).save(dest / 'ia' / brut.name, 'WEBP', quality=QUALITE, method=6)
    print(f"couleurs accordées à l'original : {len(list((dest / 'ia').glob('*.webp')))} image(s) dans {(dest / 'ia').relative_to(c.RACINE)}/")


# --- Publication -------------------------------------------------------------------------------

def publier(slug: str, seulement: set[str]) -> None:
    mesure = lire_mesure(slug)
    dest = dossier(slug)
    f, d = c.lire(slug)
    par_cle = {e['cle']: e for e in co.images(d)}
    n = {'original': 0, 'ia': 0, 'couleur': 0}
    poids = 0
    for cle, m in mesure.items():
        if m['decision'] == 'rien' or (seulement and cle not in seulement):
            continue
        e = par_cle.get(cle)
        if not e or e['image'].get('commons') != m['commons']:
            print(f'  {cle:>4} : image changée depuis la mesure (renumérotation ?) : ignorée, relancer mesurer')
            continue
        i = e['image']
        src = dest / ('grand' if m['decision'] == 'original' else 'ia') / f'{cle}.webp'
        if not src.is_file():
            print(f"  {cle:>4} : variante absente ({src.relative_to(c.RACINE)}) : {'preparer' if m['decision'] == 'original' else 'lancer'} d'abord")
            continue
        with Image.open(src) as im:
            taille = im.size
        if [i['largeur'], i['hauteur']] != m['servie'] or (i.get('recadrage') or None) != (m['recadrage'] or None) \
                or (i.get('rotation') or 0) != (m.get('rotation') or 0):
            print(f'  {cle:>4} : image servie ou recadrage changés depuis la mesure : ignorée')
            continue
        if abs(taille[0] / taille[1] - i['largeur'] / i['hauteur']) > 0.004 * i['largeur'] / i['hauteur']:
            print(f"  {cle:>4} : proportions {taille[0]}×{taille[1]} ≠ image servie {i['largeur']}×{i['hauteur']} : ignorée")
            continue
        cible = c.PUBLIC / slug / nom_grand(i)
        if not cible.exists() or cible.read_bytes() != src.read_bytes():
            shutil.copy(src, cible)
        champ = dict(fichier=nom_grand(i), largeur=taille[0], hauteur=taille[1], source=m['decision'])
        if m['decision'] == 'ia':
            ancien = i.get('grand') or {}
            champ.update(modele=MODELE, facteur=round(taille[0] / m['original_recadre'], 2),
                         genere_le=ancien.get('genere_le') if ancien.get('source') == 'ia' and ancien.get('largeur') == taille[0]
                         else datetime.date.fromtimestamp(src.stat().st_mtime).isoformat())
        cg = couleur_grande(slug, i, cible)
        if cg:
            champ['couleur'] = cg
            poids += (c.PUBLIC / slug / cg['fichier']).stat().st_size
            n['couleur'] += 1
        elif (c.PUBLIC / slug / nom_couleur_grand(i)).exists():
            (c.PUBLIC / slug / nom_couleur_grand(i)).unlink()
        i['grand'] = champ
        n[m['decision']] += 1
        poids += cible.stat().st_size
    c.ecrire(f, d)
    print(f"{n['original']} variante(s) tirée(s) de l'original, {n['ia']} agrandie(s) par {MODELE}, dont {n['couleur']} avec leur version colorisée : {poids / 1e6:.1f} Mo ; "
          f'puis : python3 scripts/diaporamas/verifier.py {slug} et npm run build')


def retirer(slug: str, seulement: set[str], tout: bool) -> None:
    if not seulement and not tout:
        raise SystemExit('Indiquer des images (83 34b …) ou --tout')
    f, d = c.lire(slug)
    retires = 0
    for e in co.images(d):
        g = e['image'].get('grand')
        if not g or (not tout and e['cle'] not in seulement):
            continue
        for nom in (g['fichier'], (g.get('couleur') or {}).get('fichier')):
            if nom and (c.PUBLIC / slug / nom).exists():
                (c.PUBLIC / slug / nom).unlink()
        del e['image']['grand']
        retires += 1
    c.ecrire(f, d)
    print(f'{retires} variante(s) retirée(s) de {slug}')


def lister(slug: str) -> None:
    _, d = c.lire(slug)
    L = [(e, e['image']['grand']) for e in co.images(d) if e['image'].get('grand')]
    for e, g in L:
        f = c.PUBLIC / slug / g['fichier']
        print(f"{e['cle']:>4} {g['fichier']:<22} {g['largeur']}×{g['hauteur']} {f.stat().st_size / 1e3 if f.exists() else 0:6.0f} ko  "
              f"{'IA ×' + str(g.get('facteur')) if g['source'] == 'ia' else 'original'}  {(e['image'].get('titre_court') or e['image'].get('titre') or '')[:50]}")
    print(f"{len(L)} variante(s), dont {sum(g['source'] == 'ia' for _, g in L)} par IA ; "
          f"{sum((c.PUBLIC / slug / g['fichier']).stat().st_size for _, g in L if (c.PUBLIC / slug / g['fichier']).exists()) / 1e6:.1f} Mo")


def est_portrait(e: dict) -> bool:
    i = e['image']
    titre = (i.get('titre') or '').lower()
    return 'portrait' in titre or bool(i.get('visage')) or (len(e['x'].get('personnes_vues') or []) == 1 and i['hauteur'] > i['largeur'])


def planche(slug: str) -> None:
    """Page de relecture des images agrandies par IA (portraits en tête) : cadre le plus serré à
    l'échelle 1, image servie contre variante, côte à côte et sous un volet glissant."""
    mesure = lire_mesure(slug)
    _, d = c.lire(slug)
    dest = c.CACHE / 'essais-colab' / 'nettete'
    (dest / f'relecture-{slug}').mkdir(parents=True, exist_ok=True)
    images = []
    for e in co.images(d):
        i, g, m = e['image'], e['image'].get('grand'), mesure.get(e['cle'])
        if not g or g['source'] != 'ia' or not m:
            continue
        u, v = m['utile'], m['vue']
        cadre = [u[0] + v[0] * (u[2] - u[0]), u[1] + v[1] * (u[3] - u[1]), u[0] + v[2] * (u[2] - u[0]), u[1] + v[3] * (u[3] - u[1])]
        for nom in (i['fichier'], g['fichier']):
            shutil.copy(c.PUBLIC / slug / nom, dest / f'relecture-{slug}' / nom)
        images.append(dict(cle=e['cle'], titre=i.get('titre_court') or i.get('titre'), auteur=i.get('auteur'), technique=i.get('technique'), portrait=est_portrait(e),
                           cadre=[max(0, min(1, x)) for x in cadre], instant=m['instant'], facteur=g.get('facteur'), densite_servie=m['densite_servie'],
                           servie=dict(fichier=f"relecture-{slug}/{i['fichier']}", l=i['largeur'], h=i['hauteur'], octets=(c.PUBLIC / slug / i['fichier']).stat().st_size),
                           grand=dict(fichier=f"relecture-{slug}/{g['fichier']}", l=g['largeur'], h=g['hauteur'], octets=(c.PUBLIC / slug / g['fichier']).stat().st_size)))
    images.sort(key=lambda x: (not x['portrait'], -x['facteur']))
    (dest / f'relecture-{slug}.html').write_text(GABARIT.replace('__DONNEES__', json.dumps(dict(slug=slug, modele=MODELE, images=images), ensure_ascii=False)))
    print(f"{len(images)} image(s) agrandie(s) par IA ({sum(x['portrait'] for x in images)} portrait(s) en tête) : {(dest / f'relecture-{slug}.html').relative_to(c.RACINE)}")


GABARIT = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,"><title>Images agrandies par IA : relecture</title><link rel="stylesheet" href="../commun.css">
<style>
  .cote { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: .5rem 0; }
  .fen, .volet-b { position: relative; overflow: hidden; background: #111; cursor: grab; touch-action: none; user-select: none; }
  .cadre { position: absolute; left: 0; top: 0; width: 1920px; overflow: hidden; }
  .cadre img { position: absolute; max-width: none; display: block; pointer-events: none; }
  .titre-v { font-variant: small-caps; letter-spacing: .05em; border-bottom: 1px solid var(--filet-2); margin-bottom: 4px; }
  .titre-v small { font-variant: normal; letter-spacing: 0; }
  .volet-b .dessus { position: absolute; inset: 0; overflow: hidden; }
  .volet-b .barre { position: absolute; top: 0; bottom: 0; width: 2px; background: #fbfaf7; mix-blend-mode: difference; pointer-events: none; }
  .entiere { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: .6rem; }
  .entiere img { width: 100%; height: auto; display: block; }
</style></head><body>
<p class="sur">Spec 17 · netteté · relecture avant publication</p>
<h1>Images agrandies par IA</h1>
<p id="chapeau"></p>
<p class="doux">Pour chaque image : le cadre le plus serré de la caméra à l'échelle 1 (1 920 px de large, comme en plein écran), image servie aujourd'hui à gauche
(agrandie par le navigateur), version agrandie par IA à droite. Faire glisser une fenêtre déplace les deux ; le volet compare au même endroit ; en dessous, les deux
images entières. À surveiller : visages modifiés, trait redessiné, textures inventées. Pour en écarter une : <code>python3 scripts/diaporamas/nettete.py retirer SLUG 83 49 …</code></p>
<div id="planche"></div>
<script>
const N = __DONNEES__, fr = (x, d = 2) => x.toFixed(d).replace('.', ','), ko = (o) => o < 1e6 ? Math.round(o / 1000) + ' ko' : fr(o / 1e6) + ' Mo';
document.getElementById('chapeau').textContent = `${N.images.length} images de « ${N.slug} » agrandies par ${N.modele}, portraits en tête (${N.images.filter((x) => x.portrait).length}).`;
document.body.innerHTML = document.body.innerHTML.replace('SLUG', N.slug);
const scenes = [];
for (const im of N.images) {
  const c = im.cadre, f0 = im.servie, H = Math.round(1920 * ((c[3] - c[1]) * f0.h) / ((c[2] - c[0]) * f0.l));
  const posee = (f) => { const L = 1920 / (c[2] - c[0]), hh = L * f0.h / f0.l; return `<img src="${f.fichier}" alt="" loading="lazy" style="width:${L}px;height:${hh}px;left:${-c[0] * L}px;top:${-c[1] * hh}px">`; };
  const s = document.createElement('section'); s.className = 'image';
  s.innerHTML = `<p class="sur">${im.portrait ? 'Portrait · ' : ''}Diapositive ${im.cle} · ${im.technique || ''} · cadre le plus serré à ${fr(im.instant, 1)} s</p>
    <h2>${im.auteur || ''}, <em>${im.titre}</em></h2>
    <p class="doux">Original de Commons agrandi ×${fr(im.facteur)} ; aujourd'hui ${fr(im.densite_servie)} px d'écran par px d'image. Poids : ${ko(im.servie.octets)} → ${ko(im.grand.octets)}.</p>
    <div class="outils"><label style="flex:1 1 14rem">position <input type="range" min="0" max="1" step="0.001" value="0.5" class="pos" style="width:100%"></label>
      <label style="flex:1 1 14rem">volet <input type="range" min="0" max="1" step="0.001" value="0.5" class="v" style="width:100%"></label></div>
    <div class="cote"><div><div class="titre-v">Servie <small class="doux">${f0.l} × ${f0.h}</small></div><div class="fen"><div class="cadre" style="height:${H}px">${posee(f0)}</div></div></div>
      <div><div class="titre-v">Agrandie par IA <small class="doux">${im.grand.l} × ${im.grand.h}</small></div><div class="fen"><div class="cadre" style="height:${H}px">${posee(im.grand)}</div></div></div></div>
    <div class="volet-b"><div class="cadre dessous" style="height:${H}px">${posee(f0)}</div><div class="dessus"><div class="cadre" style="height:${H}px">${posee(im.grand)}</div></div><div class="barre"></div></div>
    <details class="doux"><summary>Images entières</summary><div class="entiere"><img src="${f0.fichier}" loading="lazy" alt=""><img src="${im.grand.fichier}" loading="lazy" alt=""></div></details>`;
  document.getElementById('planche').append(s);
  const sc = { x: 0.5, y: 0.5, part: 0.5 }, fens = [...s.querySelectorAll('.fen')], vb = s.querySelector('.volet-b');
  const poser = () => {
    const lf = fens[0].clientWidth, hf = Math.min(H, Math.round(lf * 0.6)), dx = -sc.x * Math.max(0, 1920 - lf), dy = -sc.y * Math.max(0, H - hf);
    for (const f of fens) { f.style.height = hf + 'px'; f.firstElementChild.style.transform = `translate(${dx}px, ${dy}px)`; }
    const lv = Math.min(1920, vb.parentElement.clientWidth), hv = Math.min(H, 620), vx = -sc.x * Math.max(0, 1920 - lv), vy = -sc.y * Math.max(0, H - hv), coupe = Math.round(sc.part * lv);
    vb.style.width = lv + 'px'; vb.style.height = hv + 'px';
    vb.querySelector('.dessous').style.transform = `translate(${vx}px, ${vy}px)`;
    vb.querySelector('.dessus').style.clipPath = `inset(0 0 0 ${coupe}px)`; vb.querySelector('.dessus .cadre').style.transform = `translate(${vx}px, ${vy}px)`;
    vb.querySelector('.barre').style.left = coupe - 1 + 'px'; s.querySelector('.pos').value = sc.x;
  };
  s.querySelector('.pos').oninput = (e) => { sc.x = +e.target.value; poser(); };
  s.querySelector('.v').oninput = (e) => { sc.part = +e.target.value; poser(); };
  for (const el of [...fens, vb]) el.addEventListener('pointerdown', (e) => {
    el.setPointerCapture(e.pointerId);
    const x0 = e.clientX, y0 = e.clientY, sx = sc.x, sy = sc.y, lx = Math.max(1, 1920 - el.clientWidth), ly = Math.max(1, H - el.clientHeight);
    const bouge = (m) => { sc.x = Math.min(1, Math.max(0, sx - (m.clientX - x0) / lx)); sc.y = Math.min(1, Math.max(0, sy - (m.clientY - y0) / ly)); poser(); };
    const fin = () => { el.removeEventListener('pointermove', bouge); el.removeEventListener('pointerup', fin); };
    el.addEventListener('pointermove', bouge); el.addEventListener('pointerup', fin);
  });
  sc.poser = poser; scenes.push(sc); poser();
}
addEventListener('resize', () => scenes.forEach((s) => s.poser()));
</script></body></html>
"""


def main() -> None:
    a = sys.argv[1:]
    if len(a) < 2 or a[0] not in ('mesurer', 'preparer', 'lancer', 'accorder', 'publier', 'retirer', 'lister', 'planche'):
        raise SystemExit(__doc__)
    commande, slug, reste = a[0], a[1], a[2:]

    def option(nom, defaut=None):
        return reste[reste.index(nom) + 1] if nom in reste else defaut
    seulement = cibles(reste[reste.index('--seulement') + 1:]) if '--seulement' in reste else set()
    if commande == 'mesurer':
        mesurer(slug, c.RACINE / option('--dist', 'dist'))
    elif commande == 'preparer':
        preparer(slug, seulement)
    elif commande == 'lancer':
        lancer(slug, option('--gpu', 'L4'), option('--session'), '--garder' in reste, '--reprendre' in reste)
    elif commande == 'accorder':
        accorder(slug)
    elif commande == 'publier':
        publier(slug, seulement)
    elif commande == 'retirer':
        retirer(slug, cibles(reste), '--tout' in reste)
    elif commande == 'lister':
        lister(slug)
    else:
        planche(slug)


if __name__ == '__main__':
    main()
