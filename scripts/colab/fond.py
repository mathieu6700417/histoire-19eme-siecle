#!/usr/bin/env python3
"""Fonds prolongés des images entières (spec 17, « Fonds prolongés ») sur une session Colab pilotée
par la CLI `colab`. FLUX.2 klein 4B (Apache 2.0) reçoit une toile où l'image d'époque est posée au
centre, le reste prérempli d'un flou de la même image, et la consigne de prolonger le décor.

    entrées  $ENTREE/manifeste.json et $ENTREE/<nom>.jpg (kit de `fond.py preparer`)
    sorties  $SORTIE/<nom>-g<k>.jpg (tirage k), $SORTIE/journal.jsonl ; journal de bord $SORTIE/log.txt
    réglages GRAINES (ex. « 1,2 » : tirages à faire, dans cet ordre, toutes les images du premier
             tirage d'abord), SEULEMENT (noms séparés par des virgules ; vide = toutes)
Lancé en arrière-plan (nohup) par `fond.py lancer`. Dernière ligne du journal de bord : « FIN ».
"""
import json, os, pathlib, subprocess, sys, time

ENTREE = pathlib.Path(os.environ.get('ENTREE', '/content/fond/in'))
SORTIE = pathlib.Path(os.environ.get('SORTIE', '/content/fond/out'))
MARQUE_INSTALL = pathlib.Path('/content/.fond-bibliotheques-ok')
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
    installer()
    import torch
    from PIL import Image
    from diffusers import Flux2KleinPipeline
    vram = torch.cuda.get_device_properties(0).total_memory / 2**30
    log('carte', torch.cuda.get_device_name(0), round(vram), 'Go')
    M = json.loads((ENTREE / 'manifeste.json').read_text(encoding='utf-8'))
    graines = [int(g) for g in os.environ.get('GRAINES', '1').split(',') if g.strip()]
    seulement = {s.strip() for s in os.environ.get('SEULEMENT', '').split(',') if s.strip()}
    elements = [e for e in M['elements'] if not seulement or e['nom'] in seulement]
    t = time.time()
    pipe = Flux2KleinPipeline.from_pretrained(MODELE, torch_dtype=torch.bfloat16)
    # Tout sur la carte si elle a la place (≈ 17 Go) : deux fois plus rapide que le déchargement CPU.
    if vram >= 20 and os.environ.get('DECHARGER', '0') != '1':
        try:
            pipe.to('cuda'); mode = 'tout sur la carte'
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache(); pipe.enable_model_cpu_offload(); mode = 'déchargement CPU (mémoire)'
    else:
        pipe.enable_model_cpu_offload(); mode = 'déchargement CPU'
    log(f'modèle chargé en {time.time() - t:.0f} s ({mode}) ; {len(elements)} images, tirages {graines}')
    for k in graines:
        for i, e in enumerate(elements):
            f = SORTIE / f"{e['nom']}-g{k}.jpg"
            if f.exists():
                continue
            im = Image.open(ENTREE / f"{e['nom']}.jpg").convert('RGB')
            graine = int(e['graine']) + 1000 * (k - 1)
            t = time.time()
            for essai in range(2):
                try:
                    out = pipe(prompt=e['consigne'], image=im, width=im.width, height=im.height, guidance_scale=1.0,
                               num_inference_steps=PAS, generator=torch.Generator('cuda').manual_seed(graine)).images[0]
                    break
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache(); pipe.enable_model_cpu_offload(); log('  mémoire : passage au déchargement CPU')
            else:
                raise RuntimeError(f'{f.name} : mémoire insuffisante')
            out.save(f, quality=93, subsampling=0)
            d = time.time() - t
            with (SORTIE / 'journal.jsonl').open('a', encoding='utf-8') as j:
                j.write(json.dumps(dict(nom=e['nom'], tirage=k, graine=graine, fichier=f.name, modele=MODELE, pas=PAS,
                                        largeur=im.width, hauteur=im.height, secondes=round(d, 1)), ensure_ascii=False) + '\n')
            log(f'{f.name} ({i + 1}/{len(elements)}) : {d:.0f} s')
    log('FIN')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # le journal de bord doit toujours finir par une ligne lisible
        import traceback
        traceback.print_exc()
        log('ERREUR', repr(e)[:300])
        sys.exit(1)
