#!/usr/bin/env python3
"""Mise en mouvement d'images d'époque (spec 16) sur une session Colab pilotée par la CLI `colab`.

Version script du carnet mouvement.ipynb, pour `generation.py lancer` :
    entrées  /content/mouvement/in/manifeste.json et …/sources/NNN.jpg (kit de `generation.py preparer`)
    sorties  /content/mouvement/out/<id>.mp4, …/journal.jsonl ; journal de bord …/out/log.txt
    réglages par variables d'environnement : PROFIL (qualite | rapide), ESSAI_RAPIDE (1 | 0),
    SEULEMENT (ex. « 18,56 » ; vide = toutes)
Lancé en arrière-plan (nohup) par `generation.py lancer`, qui lit log.txt par des `colab exec` courts.
La dernière ligne du journal de bord est « FIN » quand tout est fait.
"""
import json, math, os, pathlib, subprocess, sys, time

# Dossiers propres au script (variables ENTREE et SORTIE) : une session réutilisée peut porter les
# fichiers d'un autre travail dans /content.
ENTREE = pathlib.Path(os.environ.get('ENTREE', '/content/mouvement/in'))
SORTIE = pathlib.Path(os.environ.get('SORTIE', '/content/mouvement/out'))
MARQUE_INSTALL = pathlib.Path('/content/.bibliotheques-ok')
MODELE = 'Wan-AI/Wan2.2-TI2V-5B-Diffusers'
PROFILS = {
    'qualite': dict(aire=1280 * 704, images=121, pas=40),
    'rapide': dict(aire=832 * 480, images=81, pas=25),
}
# Nombre d'images par élément : `images` du manifeste (calculé par generation.py preparer d'après la
# durée de la voix, pour que le clip ralenti couvre toute la diapositive), sinon celui du profil. Le
# modèle est entraîné sur 121 images (5 s) ; au-delà, l'attention coûte plus et la mémoire aussi :
# en cas de mémoire insuffisante, l'aire est réduite (×0,7, deux fois au plus) et on recommence.
REDUCTION_OOM = 0.7


def log(*args):
    print(time.strftime('%H:%M:%S'), *args, flush=True)


def installer():
    if MARQUE_INSTALL.exists():
        return
    log('installation des bibliothèques (torchao retiré : la version préinstallée casse diffusers)')
    subprocess.run('pip -q uninstall -y torchao; '
                   'pip -q install -U transformers accelerate ftfy imageio imageio-ffmpeg sentencepiece protobuf; '
                   'pip -q install git+https://github.com/huggingface/diffusers', shell=True, check=True)
    MARQUE_INSTALL.touch()


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    installer()
    import torch
    from PIL import Image
    from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
    from diffusers.utils import export_to_video

    nom_gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 2 ** 30
    log(f'{nom_gpu} {vram:.0f} Go')
    if vram < 20:
        raise SystemExit('Carte trop petite : L4 ou A100.')
    manifeste = json.loads((ENTREE / 'manifeste.json').read_text(encoding='utf-8'))
    profil = os.environ.get('PROFIL', 'qualite')
    essai_rapide = os.environ.get('ESSAI_RAPIDE', '1') == '1'
    seulement = [int(x) for x in os.environ.get('SEULEMENT', '').split(',') if x.strip()]

    def charger(**types):
        vae = AutoencoderKLWan.from_pretrained(MODELE, subfolder='vae', **{k: torch.float32 for k in types})
        return WanImageToVideoPipeline.from_pretrained(MODELE, vae=vae, **{k: torch.bfloat16 for k in types})

    log('chargement du modèle')
    try:
        pipe = charger(dtype=None)
    except TypeError:
        pipe = charger(torch_dtype=None)
    if vram < 40:
        pipe.enable_model_cpu_offload()
        if hasattr(pipe.vae, 'enable_tiling'):
            pipe.vae.enable_tiling()
    else:
        pipe.to('cuda')
    mod = pipe.vae_scale_factor_spatial * pipe.transformer.config.patch_size[1]
    log('modèle prêt')
    journal = SORTIE / 'journal.jsonl'

    def dimensions(im, aire):
        r = im.height / im.width
        h = max(mod, round(math.sqrt(aire * r)) // mod * mod)
        w = max(mod, round(math.sqrt(aire / r)) // mod * mod)
        return w, h

    def generer(el, profil, suffixe=''):
        p = PROFILS[profil]
        f = SORTIE / f"{el['id']}{suffixe}.mp4"
        if f.exists():
            log('déjà fait :', f.name)
            return
        images = int(el.get('images') or p['images']) if profil == 'qualite' else p['images']
        source = Image.open(ENTREE / el['source']).convert('RGB')
        aire = p['aire']
        for essai in range(3):
            w, h = dimensions(source, aire)
            im = source.resize((w, h), Image.LANCZOS)
            g = torch.Generator(device='cuda').manual_seed(int(el.get('graine', 0)))
            t0 = time.time()
            log(f"{f.name} : {w}×{h}, {images} images ({images / 24:.1f} s), {p['pas']} pas…")
            try:
                frames = pipe(image=im, prompt=el['prompt'], negative_prompt=manifeste['negatif'],
                              height=h, width=w, num_frames=images, guidance_scale=5.0,
                              num_inference_steps=p['pas'], generator=g).frames[0]
                break
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                aire = int(aire * REDUCTION_OOM ** 2)
                log(f'  mémoire insuffisante en {w}×{h} : on réduit à une aire de {aire} px²')
        else:
            raise RuntimeError(f"{f.name} : mémoire insuffisante même réduit")
        export_to_video(frames, str(f), fps=24)
        d = time.time() - t0
        ligne = dict(id=el['id'], profil=profil, fichier=f.name, largeur=w, hauteur=h,
                     images=images, pas=p['pas'], secondes=round(d), gpu=nom_gpu)
        with journal.open('a', encoding='utf-8') as j:
            j.write(json.dumps(ligne, ensure_ascii=False) + '\n')
        log(f'  → {d / 60:.1f} min')

    elements = [e for e in manifeste['elements'] if not seulement or e['n'] in seulement]
    if essai_rapide and elements:
        generer(elements[0], 'rapide', '-rapide')
    for el in elements:
        generer(el, profil)
    log('terminé :', sorted(f.name for f in SORTIE.glob('*.mp4')))
    log('FIN')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # le journal de bord doit toujours finir par une ligne lisible
        import traceback
        traceback.print_exc()
        log('ERREUR', repr(e))
        sys.exit(1)
