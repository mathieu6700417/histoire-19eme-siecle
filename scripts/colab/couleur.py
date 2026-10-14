#!/usr/bin/env python3
"""Colorisation « couleur seule » (spec 16) sur une session Colab pilotée par la CLI `colab`.
FLUX.2 klein 4B (Apache 2.0) reçoit la zone utile de l'image d'époque et une consigne de pure
colorisation ; sur le Mac, on ne garde que la chrominance de sa sortie, posée sur la luminance de
l'original (aucun trait redessiné).

    entrées  $ENTREE/manifeste.json : [{"nom", "consigne", "graine"}, …] (ou {"elements": […]}),
             et $ENTREE/<nom>.jpg, déjà à la taille de travail (≈ 1,4 Mpx, multiples de 16)
    sorties  $SORTIE/<nom>--g<graine>.jpg, $SORTIE/journal.jsonl ; journal de bord $SORTIE/log.txt
    réglages GRAINES (ex. « 1866,7 » : graines à faire pour chaque image ; défaut : la graine de
             l'élément), SEULEMENT (noms séparés par des virgules ; vide = toutes)
Lancé en arrière-plan : nohup env GRAINES=… python3 couleur.py > $SORTIE/log.txt 2>&1 &
Reprise : saute les sorties déjà faites. Arrêt propre : créer $SORTIE/STOP (testé entre deux images).
Dernière ligne du journal de bord : « FIN » (ou « ERREUR … »).
"""
import json, os, pathlib, subprocess, sys, time

ENTREE = pathlib.Path(os.environ.get('ENTREE', '/content/couleur/in'))
SORTIE = pathlib.Path(os.environ.get('SORTIE', '/content/couleur/out'))
MARQUE_INSTALL = pathlib.Path('/content/.couleur-bibliotheques-ok')
MODELE = 'black-forest-labs/FLUX.2-klein-4B'
PAS = 4


def log(*args):
    print(time.strftime('%H:%M:%S'), *args, flush=True)


def installer():
    if MARQUE_INSTALL.exists():
        return
    log('installation des bibliothèques (torchao retiré : la version préinstallée casse diffusers)')
    subprocess.run('pip -q uninstall -y torchao; pip -q install -U transformers accelerate sentencepiece protobuf; '
                   'pip -q install git+https://github.com/huggingface/diffusers', shell=True, check=True)
    MARQUE_INSTALL.write_text('ok')


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / 'pid').write_text(str(os.getpid()))
    installer()
    import torch
    from PIL import Image
    from diffusers import Flux2KleinPipeline
    vram = torch.cuda.get_device_properties(0).total_memory / 2**30
    log('carte', torch.cuda.get_device_name(0), round(vram), 'Go')
    M = json.loads((ENTREE / 'manifeste.json').read_text(encoding='utf-8'))
    elements = M['elements'] if isinstance(M, dict) else M
    graines = [int(g) for g in os.environ.get('GRAINES', '').split(',') if g.strip()]
    seulement = {s.strip() for s in os.environ.get('SEULEMENT', '').split(',') if s.strip()}
    elements = [e for e in elements if not seulement or e['nom'] in seulement]
    t = time.time()
    pipe = Flux2KleinPipeline.from_pretrained(MODELE, torch_dtype=torch.bfloat16)
    if vram >= 20:
        pipe.to('cuda'); mode = 'tout sur la carte'
    else:
        pipe.enable_model_cpu_offload(); mode = 'déchargement CPU'
    log(f'modèle chargé en {time.time() - t:.0f} s ({mode}) ; {len(elements)} images, graines {graines or "de chaque élément"}')
    # toutes les images à la première graine d'abord : un arrêt en cours de route laisse un lot complet
    for g in (graines or [None]):
        for i, e in enumerate(elements):
            if (SORTIE / 'STOP').exists():
                log('STOP'); log('FIN'); return
            graine = g if g is not None else int(e.get('graine', 1848))
            f = SORTIE / f"{e['nom']}--g{graine}.jpg"
            if f.exists():
                continue
            im = Image.open(ENTREE / f"{e['nom']}.jpg").convert('RGB')
            t = time.time()
            out = pipe(prompt=e['consigne'], image=im, width=im.width, height=im.height, guidance_scale=1.0,
                       num_inference_steps=PAS, generator=torch.Generator('cuda').manual_seed(graine)).images[0]
            out.save(f, quality=95, subsampling=0)
            d = time.time() - t
            with (SORTIE / 'journal.jsonl').open('a', encoding='utf-8') as j:
                j.write(json.dumps(dict(nom=e['nom'], graine=graine, fichier=f.name, modele=MODELE, pas=PAS, consigne=e['consigne'],
                                        largeur=im.width, hauteur=im.height, secondes=round(d, 1)), ensure_ascii=False) + '\n')
            log(f'{f.name} ({i + 1}/{len(elements)}) : {d:.1f} s')
    log('FIN')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # le journal de bord doit toujours finir par une ligne lisible
        import traceback
        traceback.print_exc()
        log('ERREUR', repr(e)[:300])
        sys.exit(1)
