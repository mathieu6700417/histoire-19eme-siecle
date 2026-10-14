#!/usr/bin/env python3
"""Couche générée (spec 16) : images d'époque mises en mouvement par un modèle à poids ouverts,
calculées sur Google Colab (script scripts/colab/mouvement.py par la CLI `colab`), encodées, jugées
sur une planche, puis publiées dans le diaporama (`image.video`, lu par mouvement.ts).

    python3 scripts/diaporamas/generation.py preparer <slug>              # kit-mouvement.zip pour Colab
    python3 scripts/diaporamas/generation.py lancer <slug> [--gpu A100] [--high-mem] [--seulement 18,56] [--profil rapide]
                                                           [--session nom --reprendre] [--garder]
                                                                          # session Colab par la CLI `colab`,
                                                                          # calcul, rapatriement, arrêt
    python3 scripts/diaporamas/generation.py encoder <slug> [zip|dossier]  # clips pour le site (ralentis ×2, 10 s)
    python3 scripts/diaporamas/generation.py planche <slug>               # page HTML de visionnage
    python3 scripts/diaporamas/generation.py publier <slug> [--seulement 18,56]
                                                                          # clips → public/, champ image.video
    python3 scripts/diaporamas/generation.py retirer <slug> --seulement 56  # retire un clip du diaporama

Le lot (diapositives, consignes, graines, modèle) est `src/data/diaporamas/generation/<slug>.json`.
Tout le reste vit dans `.cache/diaporamas/<slug>/generation/` : `kit-mouvement.zip` (manifeste +
sources JPEG), `bruts/` (sorties de Colab, 5 s), `clips/` (ralentis de moitié par interpolation de
mouvement, 10 s, encodés comme pour le site : joués une fois par le lecteur, dernière image tenue),
`planche-mouvement.html` (original, clip, narration, à ouvrir dans un navigateur).
`publier` copie `clips/<id>.mp4` en `public/diaporamas/<slug>/NNN-mouvement.mp4` et écrit
`image.video` (fichier, type, durée, dimensions, modèle, date) ; `verifier.py` contrôle le tout.

`lancer` pilote Colab par la CLI officielle `colab` (google-colab-cli, `uv tool install`) : `colab new`
(A100 par défaut), envoi du kit et de `scripts/colab/mouvement.py`, lancement en arrière-plan (nohup),
lecture du journal de bord par des `colab exec` courts toutes les 60 s, `colab download` de chaque
sortie dans `bruts/`, puis `colab stop` (toujours, même en cas d'erreur : une session oubliée coûte
des unités). `--garder` laisse la session ouverte pour une reprise. Dépendances : Pillow, ffmpeg, colab.
"""
import html, io, json, math, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

from PIL import Image

import commun as c

COTE_SOURCE = 1600        # grand côté des sources envoyées au carnet (le modèle travaille en 1280×704)
QUALITE_SOURCE = 92
MODELE = 'Wan 2.2 TI2V-5B'  # modèle par défaut (crédits), sauf `modele` dans le lot
# Encodage pour le site (mesures du 2026-10-12 sur les 8 clips de la Révolution) : le clip de 5 s est
# ralenti ×RALENTI par interpolation de mouvement (ffmpeg minterpolate, images intermédiaires
# calculées : 24 images/s fluides, ≈ 20 s de calcul par clip ; retour de l'utilisateur : « deux fois
# plus lentement »), puis H.264 crf 27 avec un plafond de débit de 3,2 Mbit/s, qui borne les gravures
# très détaillées (sans le plafond : 10 à 12 Mo ; avec : 4,2 Mo, sans perte visible à l'échelle 1) ;
# les tableaux font 1,2 à 2,5 Mo.
CRF = 27
DEBIT_MAX = '3200k'
RALENTI = 2
IMAGES_PAR_S = 24
# Longueur générée par diapositive (retour de l'utilisateur du 2026-10-12 : le clip ne doit pas
# s'arrêter avant la fin de la diapositive) : le clip ralenti part à DEBUT_CLIP s de voix (ou après la
# plongée d'une mosaïque) et doit durer jusqu'à la fin de la voix et de sa pause ; le nombre d'images
# générées (4k + 1) en découle, entre 121 (5 s, longueur d'entraînement du modèle) et IMAGES_MAX.
PAUSE = 0.6                  # s : pause après la voix (diaporamas.ts PAUSE, verifier.py)
DEBUT_CLIP = 1.8             # s de voix (constantes.ts DEBUT_CLIP)
DEBUT_CLIP_MOSAIQUE = 0.3    # s après la plongée (constantes.ts)
PLONGEE_MAX = 6.0            # s : durée maximale de la plongée (DUREE_MIN à 2 × MISE_EN_ROUTE + …)
MOSAIQUE = {'apparition': 1.0, 'pas': 0.9, 'tenue': 0.6}  # diaporamas.ts MOSAIQUE
MARGE_CLIP = 0.5             # s générées de marge (l'interpolation retire la dernière image)
IMAGES_MIN, IMAGES_MAX = 121, 289   # 5 s à 12 s générées (10 à 24 s ralenties)


def debut_clip(s: dict) -> float:
    """Instant de la voix où le clip part (mouvement.ts) ; mosaïque : après la plongée, au plus tard."""
    mo = s.get('mosaique')
    if mo and not s['image'].get('ouverture'):
        return MOSAIQUE['apparition'] + len(mo.get('vignettes', [])) * MOSAIQUE['pas'] + MOSAIQUE['tenue'] + PLONGEE_MAX + DEBUT_CLIP_MOSAIQUE
    return DEBUT_CLIP


def besoin_clip(s: dict) -> float:
    """Durée (s) que le clip ralenti doit couvrir : du départ à la fin de la voix et de sa pause."""
    return max(0.0, ((s.get('audio') or {}).get('duree') or 6) + PAUSE - debut_clip(s))


def images_clip(s: dict) -> int:
    """Images à générer (4k + 1) pour couvrir `besoin_clip` une fois ralenti."""
    sec = besoin_clip(s) / RALENTI + MARGE_CLIP
    k = math.ceil((sec * IMAGES_PAR_S - 1) / 4)
    return max(IMAGES_MIN, min(IMAGES_MAX, 4 * k + 1))


def lot(slug: str) -> dict:
    f = c.DONNEES / 'generation' / f'{slug}.json'
    if not f.exists():
        raise SystemExit(f'Lot introuvable : {f.relative_to(c.RACINE)}')
    return json.loads(f.read_text(encoding='utf-8'))


def dossier(slug: str) -> Path:
    d = c.CACHE / slug / 'generation'
    d.mkdir(parents=True, exist_ok=True)
    return d


def ident(el: dict) -> str:
    return f"{el['n']:03d}-{el['type']}"


def source(slug: str, s: dict) -> Image.Image:
    """L'image servie (recadrage déjà appliqué), réduite à sa zone utile."""
    im = Image.open(c.PUBLIC / slug / s['image']['fichier']).convert('RGB')
    u = s['image'].get('utile')
    if u and u != [0, 0, 1, 1]:
        x0, y0, x1, y1 = u
        im = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
    im.thumbnail((COTE_SOURCE, COTE_SOURCE), Image.LANCZOS)
    return im


def preparer(slug: str) -> None:
    _, d = c.lire(slug)
    par_n = {s['n']: s for s in d['diapositives']}
    l = lot(slug)
    dest = dossier(slug)
    manifeste = {'slug': slug, 'negatif': l['negatif'], 'elements': []}
    kit = dest / 'kit-mouvement.zip'
    with zipfile.ZipFile(kit, 'w', zipfile.ZIP_DEFLATED) as z:
        for el in l['elements']:
            s = par_n.get(el['n'])
            if not s:
                raise SystemExit(f'Diapositive {el["n"]} absente de {slug}')
            im = source(slug, s)
            tampon = io.BytesIO()
            im.save(tampon, 'JPEG', quality=QUALITE_SOURCE)
            nom = f'sources/{el["n"]:03d}.jpg'
            z.writestr(nom, tampon.getvalue())
            (dest / 'sources').mkdir(exist_ok=True)
            (dest / nom).write_bytes(tampon.getvalue())
            manifeste['elements'].append({
                'id': ident(el), 'n': el['n'], 'type': el['type'], 'source': nom,
                'prompt': el['prompt'], 'graine': el.get('graine', 0), 'images': images_clip(s),
                'titre': s['image']['titre'], 'narration': s['narration'],
                'commons': s['image']['commons'], 'utile': s['image'].get('utile') or [0, 0, 1, 1],
                'largeur': im.width, 'hauteur': im.height,
            })
        z.writestr('manifeste.json', json.dumps(manifeste, ensure_ascii=False, indent=1))
    (dest / 'manifeste.json').write_text(json.dumps(manifeste, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{kit.relative_to(c.RACINE)} : {len(manifeste["elements"])} sources, {kit.stat().st_size / 1e6:.1f} Mo')
    for el in manifeste['elements']:
        s = par_n[el['n']]
        print(f"  {el['id']}  {el['largeur']}×{el['hauteur']}  {el['images']} images ({el['images'] / IMAGES_PAR_S:.1f} s générées, "
              f"{el['images'] / IMAGES_PAR_S * RALENTI:.0f} s ralenties pour {besoin_clip(s):.1f} s à couvrir)  {el['titre'][:50]}")


def encoder(slug: str, origine: str) -> None:
    """Sorties du carnet (zip ou dossier) → bruts/ puis clips/ (H.264 pour le site, sans son)."""
    dest = dossier(slug)
    bruts = dest / 'bruts'
    bruts.mkdir(exist_ok=True)
    o = Path(origine).expanduser()
    if o.is_file() and o.suffix == '.zip':
        with zipfile.ZipFile(o) as z:
            for n in z.namelist():
                if n.endswith(('.mp4', '.jsonl')) and not n.endswith('/'):
                    (bruts / Path(n).name).write_bytes(z.read(n))
    elif o.is_dir():
        for f in o.iterdir():
            if f.suffix in ('.mp4', '.jsonl') and f.resolve() != (bruts / f.name).resolve():
                shutil.copy(f, bruts / f.name)
    else:
        raise SystemExit(f'Origine inconnue : {origine}')
    clips = dest / 'clips'
    clips.mkdir(exist_ok=True)
    for brut in sorted(bruts.glob('*.mp4')):
        clip = clips / brut.name
        if clip.exists() and clip.stat().st_mtime >= brut.stat().st_mtime:
            continue
        # Le clip est joué une seule fois par le lecteur, puis tenu sur sa dernière image (retour de
        # l'utilisateur du 2026-10-12 : ni boucle ni aller-retour), ralenti par interpolation.
        subprocess.run([
            'ffmpeg', '-y', '-loglevel', 'error', '-i', str(brut),
            '-vf', f'setpts={RALENTI}*PTS,minterpolate=fps={IMAGES_PAR_S}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1',
            '-map', '0:v:0', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(CRF),
            '-maxrate', DEBIT_MAX, '-bufsize', str(int(DEBIT_MAX[:-1]) * 2) + 'k',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(clip),
        ], check=True)
        print(f'{clip.relative_to(c.RACINE)} : {clip.stat().st_size / 1e6:.1f} Mo')


def colab(*args: str, timeout: float = 300, silencieux: bool = False, code: str | None = None, essais: int = 3) -> str:
    """Appel de la CLI colab ; renvoie la sortie standard. Échec explicite sinon. `code` : programme
    Python donné à `colab exec` par l'entrée standard (la CLI n'accepte pas de code en argument).
    Un appel qui ne répond plus (connexion restée en attente, vu le 2026-10-12 sur une session
    réutilisée après une longue inactivité) est tué et refait, `essais` fois au plus."""
    for essai in range(essais):
        try:
            r = subprocess.run(['colab', *args], capture_output=True, text=True, timeout=timeout, input=code)
            break
        except subprocess.TimeoutExpired:
            if essai + 1 < essais:
                print(f'  (colab {args[0]} sans réponse après {timeout:.0f} s : nouvel essai {essai + 2}/{essais})')
    else:
        raise SystemExit(f'colab {" ".join(args[:2])} : sans réponse')
    if r.returncode != 0:
        raise SystemExit(f'colab {" ".join(args[:2])} : {r.stderr.strip() or r.stdout.strip()}')
    if not silencieux and r.stdout.strip():
        print(r.stdout.rstrip())
    return r.stdout


REMOTE = '/content/mouvement'   # dossier propre au script sur la machine Colab (session réutilisable)


def lancer(slug: str, gpu: str, session: str | None, profil: str, seulement: str, essai_rapide: bool,
           garder: bool, high_mem: bool = False, reprendre: bool = False) -> None:
    dest = dossier(slug)
    kit = dest / 'kit-mouvement.zip'
    if not kit.exists():
        raise SystemExit(f'Kit absent : lancer « preparer {slug} » d\'abord')
    script = c.RACINE / 'scripts' / 'colab' / 'mouvement.py'
    session = session or f'mouvement-{slug}'
    bruts = dest / 'bruts'
    bruts.mkdir(exist_ok=True)
    if reprendre:
        print(f'session « {session} » réutilisée (--reprendre)')
    else:
        print(f'session « {session} » ({gpu}{", mémoire haute" if high_mem else ""})…')
        colab('new', '-s', session, '--gpu', gpu, *(['--high-mem'] if high_mem else []), timeout=600)
    R = REMOTE
    try:
        colab('exec', '-s', session, '--timeout', '60', timeout=90, code=f'import os; os.makedirs("{R}/in", exist_ok=True); os.makedirs("{R}/out", exist_ok=True); print("dossiers prêts")')
        colab('upload', '-s', session, str(kit), f'{R}/kit.zip', silencieux=True)
        colab('upload', '-s', session, str(script), f'{R}/mouvement.py', silencieux=True)
        colab('exec', '-s', session, '--timeout', '120', timeout=150, code=(
              f'import zipfile, os; zipfile.ZipFile("{R}/kit.zip").extractall("{R}/in"); print("kit :", sorted(os.listdir("{R}/in/sources")))'))
        # Les variables d'environnement sont écrites dans la commande : `--env` ne vaut que pour le noyau,
        # pas pour un processus lancé en arrière-plan par nohup.
        env = f'PROFIL={profil} ESSAI_RAPIDE={1 if essai_rapide else 0} SEULEMENT={seulement} ENTREE={R}/in SORTIE={R}/out'
        colab('exec', '-s', session, '--timeout', '60', timeout=90, code=(
              f'import subprocess; subprocess.Popen("nohup env {env} python3 {R}/mouvement.py > {R}/out/log.txt 2>&1 &", shell=True); print("lancé")'))
        lu = 0
        debut = time.time()
        echecs = 0
        rapatries: set[str] = set()
        while True:
            time.sleep(60)
            try:
                texte = colab('exec', '-s', session, '--timeout', '30', silencieux=True, timeout=60, essais=1,
                              code=f'import os; p="{R}/out/log.txt"; print(open(p, encoding="utf-8").read() if os.path.exists(p) else "")')
                echecs = 0
            except (SystemExit, subprocess.TimeoutExpired) as e:
                print(f'  (lecture du journal impossible : {e}) ')
                echecs += 1
                # Session perdue (2026-10-14 : « Session … not found » pendant une heure) : on cesse d'attendre.
                if 'not found' in str(e) or echecs >= 10:
                    print('session injoignable : suivi arrêté (clips déjà rapatriés gardés dans bruts/)')
                    break
                continue
            # Chaque clip annoncé avant le dernier est fini : on le rapatrie aussitôt, pour ne pas tout
            # perdre si la session disparaît (2026-10-14 : onze clips perdus avec la session).
            annonces = re.findall(r'(\d{3}-mouvement\.mp4) :', texte)
            for nom in annonces[:-1]:
                if nom not in rapatries:
                    try:
                        colab('download', '-s', session, f'{R}/out/{nom}', str(bruts / nom), silencieux=True, timeout=600)
                        rapatries.add(nom)
                        print(f'  ← {nom}')
                    except (SystemExit, subprocess.TimeoutExpired) as e:
                        print(f'  ({nom} non rapatrié pour l\'instant : {e})')
            nouveau = texte[lu:]
            if nouveau.strip():
                print(nouveau.rstrip())
            lu = len(texte)
            # Les lignes du journal distant portent l'heure en tête (« 00:03:02 FIN ») : on regarde la fin.
            lignes = [l.strip() for l in texte.splitlines() if l.strip()]
            if any(l == 'FIN' or l.endswith(' FIN') for l in lignes[-3:]):
                break
            if any(l.startswith(('ERREUR', 'Traceback')) or ' ERREUR ' in l for l in lignes):
                print('ERREUR dans le script distant (voir ci-dessus)')
                break
            if time.time() - debut > 4 * 3600:
                print('plus de 4 h : on arrête le suivi')
                break
        fichiers = colab('ls', '-s', session, f'{R}/out', silencieux=True, timeout=120)
        for nom in sorted(set(l.strip().split()[-1] for l in fichiers.splitlines() if l.strip())):
            nom = Path(nom).name
            if nom.endswith(('.mp4', '.jsonl', '.txt')):
                colab('download', '-s', session, f'{R}/out/{nom}', str(bruts / nom), silencieux=True, timeout=600)
                print(f'  ← {nom}')
    finally:
        if garder:
            print(f'session « {session} » laissée ouverte (colab stop -s {session} pour l\'arrêter)')
        else:
            colab('stop', '-s', session, timeout=300)
            print(f'session « {session} » arrêtée')
    encoder(slug, bruts)
    planche(slug)


def sonder(f: Path) -> dict:
    """Dimensions, durée et codec d'un clip (ffprobe)."""
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,codec_name,pix_fmt',
                        '-show_entries', 'format=duration', '-of', 'json', str(f)], capture_output=True, text=True, check=True)
    info = json.loads(r.stdout)
    flux = info['streams'][0]
    return {'largeur': flux['width'], 'hauteur': flux['height'], 'duree': round(float(info['format']['duration']), 2),
            'codec': flux.get('codec_name'), 'pix_fmt': flux.get('pix_fmt')}


def selection(args: list[str]) -> set[int]:
    """Numéros de diapositives de `--seulement 18,56` (vide : tous)."""
    if '--seulement' not in args:
        return set()
    return {int(n) for n in args[args.index('--seulement') + 1].split(',') if n.strip()}


def publier(slug: str, seulement: set[int]) -> None:
    """Clips jugés bons → public/diaporamas/<slug>/NNN-<type>.mp4 et champ `image.video` de la
    diapositive (fichier, type, durée, dimensions, modèle, date du calcul). Idempotent. Un avant / après
    est ignoré (autre calque) ; une mosaïque est admise (le clip paraît après la plongée)."""
    import datetime
    f, d = c.lire(slug)
    par_n = {s['n']: s for s in d['diapositives']}
    l = lot(slug)
    modele = l.get('modele') or MODELE
    dest = dossier(slug)
    publies = 0
    for el in l['elements']:
        if seulement and el['n'] not in seulement:
            continue
        s = par_n.get(el['n'])
        if not s:
            raise SystemExit(f'Diapositive {el["n"]} absente de {slug}')
        if s['image'].get('apres'):
            print(f"  {el['n']:3d} : avant / après, clip sans effet : ignoré")
            continue
        clip = dest / 'clips' / f'{ident(el)}.mp4'
        if not clip.is_file():
            print(f"  {el['n']:3d} : pas de clip ({clip.relative_to(c.RACINE)}) : encoder d'abord")
            continue
        cible = c.PUBLIC / slug / f"{el['n']:03d}-{el['type']}.mp4"
        if not cible.exists() or cible.read_bytes() != clip.read_bytes():
            shutil.copy(clip, cible)
        info = sonder(cible)
        brut = dest / 'bruts' / clip.name
        quand = datetime.date.fromtimestamp((brut if brut.exists() else clip).stat().st_mtime).isoformat()
        s['image']['video'] = {'fichier': cible.name, 'type': el['type'], 'duree': info['duree'], 'largeur': info['largeur'],
                               'hauteur': info['hauteur'], 'modele': modele, 'genere_le': quand}
        publies += 1
        print(f"  {el['n']:3d} : {cible.name} {info['largeur']}×{info['hauteur']}, {info['duree']} s, {cible.stat().st_size / 1e6:.1f} Mo")
    c.ecrire(f, d)
    print(f'{publies} clip(s) publié(s) dans {slug} ; puis : python3 scripts/diaporamas/verifier.py {slug} et npm run build')


def retirer(slug: str, seulement: set[int]) -> None:
    """Retire le clip (champ et fichier) des diapositives données (toutes avec un clip, sans --seulement)."""
    f, d = c.lire(slug)
    retires = 0
    for s in d['diapositives']:
        v = s['image'].get('video')
        if not v or (seulement and s['n'] not in seulement):
            continue
        fichier = c.PUBLIC / slug / v['fichier']
        if fichier.exists():
            fichier.unlink()
        del s['image']['video']
        # L'ambiance sonore du clip (spec 17) part avec lui : pas d'ambiance sur une image fixe.
        amb = s['image'].pop('ambiance', None)
        if amb and (c.PUBLIC / slug / amb['fichier']).exists():
            (c.PUBLIC / slug / amb['fichier']).unlink()
        retires += 1
        print(f"  {s['n']:3d} : clip retiré ({v['fichier']})")
    c.ecrire(f, d)
    print(f'{retires} clip(s) retiré(s) de {slug}')


def planche(slug: str) -> None:
    dest = dossier(slug)
    manifeste = json.loads((dest / 'manifeste.json').read_text(encoding='utf-8'))
    journal = {}
    jf = dest / 'bruts' / 'journal.jsonl'
    if jf.exists():
        for ligne in jf.read_text(encoding='utf-8').splitlines():
            if ligne.strip():
                j = json.loads(ligne)
                journal[Path(j['fichier']).stem] = j
    public = Path('../../../../public/diaporamas') / slug
    blocs = []
    for el in manifeste['elements']:
        videos = []
        for nom, legende in ((el['id'] + '-rapide', 'essai rapide'), (el['id'], 'clip brut, 5 s'),):
            if (dest / 'bruts' / f'{nom}.mp4').exists():
                j = journal.get(nom, {})
                info = f"{j.get('largeur', '?')}×{j.get('hauteur', '?')}, {j.get('pas', '?')} pas, {j.get('secondes', 0) / 60:.1f} min" if j else ''
                videos.append(f'<figure><video src="bruts/{nom}.mp4" muted loop playsinline controls></video>'
                              f'<figcaption>{legende} <span>{info}</span></figcaption></figure>')
        clip = dest / 'clips' / f'{el["id"]}.mp4'
        if clip.exists():
            videos.append(f'<figure><video src="clips/{el["id"]}.mp4" muted loop autoplay playsinline controls></video>'
                          f'<figcaption>encodé pour le site : ralenti ×{RALENTI}, joué une fois, dernière image tenue <span>{clip.stat().st_size / 1e6:.1f} Mo</span></figcaption></figure>')
        if not videos:
            videos.append('<p class="absent">Pas encore de clip.</p>')
        blocs.append(f'''
<section>
  <h2>{el['n']} · {html.escape(el['titre'])}</h2>
  <div class="rang">
    <figure><img src="{el['source']}" alt=""><figcaption>image d'époque (source envoyée)</figcaption></figure>
    {''.join(videos)}
  </div>
  <p class="narration">{html.escape(el['narration'])}
    <audio controls preload="none" src="{public}/{el['n']:03d}.m4a"></audio></p>
  <p class="consigne">{html.escape(el['prompt'])}</p>
</section>''')
    page = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Essai mouvement · {html.escape(manifeste['slug'])}</title>
<style>
body{{font-family:Georgia,serif;background:#faf9f6;color:#222;margin:0;padding:2rem;max-width:1500px}}
h1{{font-weight:normal;font-size:1.6rem}} h2{{font-weight:normal;font-size:1.15rem;margin:0 0 .6rem}}
section{{border-top:1px solid #bbb;padding:1.2rem 0}}
.rang{{display:flex;gap:1rem;flex-wrap:wrap;align-items:flex-start}}
figure{{margin:0;flex:1 1 420px;max-width:640px}} img,video{{width:100%;background:#000}}
figcaption{{font-size:.8rem;color:#666;font-variant:small-caps;margin-top:.3rem}} figcaption span{{font-variant:normal;color:#999;margin-left:.5rem}}
.narration{{font-size:.95rem;max-width:70ch}} .consigne{{font-size:.8rem;color:#777;max-width:90ch;font-family:ui-monospace,monospace}}
audio{{display:block;margin-top:.4rem}} .absent{{color:#999}}
</style></head><body>
<h1>Essai « mouvement » · {html.escape(manifeste['slug'])} · {len(manifeste['elements'])} images</h1>
<p>Touche espace sur une vidéo pour lire/pauser ; les clips bruts sont muets, l'audio sous chaque image joue la narration de la diapositive.</p>
{''.join(blocs)}
</body></html>'''
    f = dest / 'planche-mouvement.html'
    f.write_text(page, encoding='utf-8')
    print(f'{f.relative_to(c.RACINE)}')


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    quoi, slug = sys.argv[1], sys.argv[2]
    if quoi == 'preparer':
        preparer(slug)
    elif quoi == 'lancer':
        args = sys.argv[3:]
        def option(nom, defaut=None):
            return args[args.index(nom) + 1] if nom in args else defaut
        lancer(slug, gpu=option('--gpu', 'A100'), session=option('--session'), profil=option('--profil', 'qualite'),
               seulement=option('--seulement', ''), essai_rapide='--sans-essai' not in args, garder='--garder' in args,
               high_mem='--high-mem' in args, reprendre='--reprendre' in args)
    elif quoi == 'encoder':
        # Sans origine : les bruts déjà rapatriés sont réencodés (après un changement de réglage).
        encoder(slug, sys.argv[3] if len(sys.argv) > 3 else str(dossier(slug) / 'bruts'))
        planche(slug)
    elif quoi == 'planche':
        planche(slug)
    elif quoi == 'publier':
        publier(slug, selection(sys.argv[3:]))
    elif quoi == 'retirer':
        if '--seulement' not in sys.argv:
            raise SystemExit('retirer <slug> --seulement 18,56 (numéros des diapositives)')
        retirer(slug, selection(sys.argv[3:]))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
