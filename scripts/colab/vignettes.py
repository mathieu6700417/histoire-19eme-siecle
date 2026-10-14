#!/usr/bin/env python3
"""Dessins traversants sous les images entières (spec 17, essai 5, révision du 2026-10-14) sur une
session Colab pilotée par la CLI `colab`. Z-Image-Turbo (Apache 2.0, modèle public, sans secret HF)
dessine une esquisse simple, sans personnage, au format de l'écran (1792 × 768). Repris de l'essai
(.cache/diaporamas/essais-colab/vignettes/vignettes_colab.py), un seul modèle.

    entrées  $ENTREE/manifeste.json  {elements: [{nom, graine, consigne, largeur, hauteur}]}
             (`consigne` composée par `vignettes.py preparer` ; à défaut, style + scene)
             (écrit par `scripts/diaporamas/vignettes.py preparer`)
    sorties  $SORTIE/<nom>-g<k>.png (tirage k), $SORTIE/journal.jsonl ; journal de bord $SORTIE/log.txt
    réglages GRAINES (ex. « 1,2,3 » : tirages à faire, toutes les vignettes du premier tirage
             d'abord), SEULEMENT (noms séparés par des virgules ; vide = toutes)
Lancé en arrière-plan (nohup) par `vignettes.py lancer`. Reprise : saute les sorties déjà faites.
Arrêt propre : créer $SORTIE/STOP (testé entre deux dessins). Dernière ligne du journal de bord :
« FIN » (ou « ERREUR … »).
"""
import gc, json, os, pathlib, subprocess, sys, time

ENTREE = pathlib.Path(os.environ.get('ENTREE', '/content/vignettes/in'))
SORTIE = pathlib.Path(os.environ.get('SORTIE', '/content/vignettes/out'))
MARQUE_INSTALL = pathlib.Path('/content/.vignettes-bibliotheques-ok')
MODELE = 'Tongyi-MAI/Z-Image-Turbo'
PAS = 9          # Z-Image-Turbo : 9 pas, sans guidage (réglage de l'essai)


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
    from diffusers import ZImagePipeline
    vram = torch.cuda.get_device_properties(0).total_memory / 2**30
    log('carte', torch.cuda.get_device_name(0), round(vram), 'Go')
    M = json.loads((ENTREE / 'manifeste.json').read_text(encoding='utf-8'))
    graines = [int(g) for g in os.environ.get('GRAINES', '1,2,3').split(',') if g.strip()]
    seulement = {s.strip() for s in os.environ.get('SEULEMENT', '').split(',') if s.strip()}
    elements = [e for e in M['elements'] if not seulement or e['nom'] in seulement]
    t = time.time()
    pipe = ZImagePipeline.from_pretrained(MODELE, torch_dtype=torch.bfloat16)
    # Le modèle et son encodeur de texte tiennent à peine sur une L4 (essai : déchargement CPU,
    # ≈ 28 s par dessin) ; tout sur la carte au-delà de 30 Go.
    if vram >= 30:
        pipe.to('cuda'); mode = 'tout sur la carte'
    else:
        pipe.enable_model_cpu_offload(); mode = 'déchargement CPU'
    log(f'modèle chargé en {time.time() - t:.0f} s ({mode}) ; {len(elements)} vignettes, tirages {graines}')
    for k in graines:
        for i, e in enumerate(elements):
            if (SORTIE / 'STOP').exists():
                log('STOP'); log('FIN'); return
            f = SORTIE / f"{e['nom']}-g{k}.png"
            if f.exists():
                continue
            # Dessin traversant (révision du 2026-10-14) : consigne déjà composée par `vignettes.py preparer`.
            consigne = e.get('consigne') or f"{e.get('style') or M['style']} Scene: {e['scene']}"
            graine = int(e['graine']) + 1000 * (k - 1)
            t = time.time()
            im = pipe(prompt=consigne, width=int(e['largeur']), height=int(e['hauteur']), guidance_scale=0.0,
                      num_inference_steps=PAS, generator=torch.Generator('cuda').manual_seed(graine)).images[0]
            im.save(f)
            d = time.time() - t
            with (SORTIE / 'journal.jsonl').open('a', encoding='utf-8') as j:
                j.write(json.dumps(dict(nom=e['nom'], modele=MODELE, tirage=k, graine=graine, fichier=f.name, pas=PAS,
                                        largeur=im.width, hauteur=im.height, consigne=consigne, secondes=round(d, 1)),
                                   ensure_ascii=False) + '\n')
            log(f'{f.name} ({i + 1}/{len(elements)}) : {d:.0f} s')
    del pipe; gc.collect()
    log('FIN')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # le journal de bord doit toujours finir par une ligne lisible
        import traceback
        traceback.print_exc()
        log('ERREUR', repr(e)[:300])
        sys.exit(1)
