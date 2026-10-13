#!/usr/bin/env python3
"""Ambiances sonores des clips (spec 17) par EzAudio sur une session Colab pilotée par la CLI `colab`.

    entrées  $ENTREE/manifeste.json (kit de `ambiance.py preparer` : elements [{n, prompt}], graines)
    sorties  $SORTIE/NNN-ezaudio-<k>.wav (10 s, 24 kHz, un fichier par graine), $SORTIE/journal.jsonl ;
             journal de bord sur la sortie standard (log.txt), fini par « FIN »
Lancé en arrière-plan (nohup) par `ambiance.py lancer`. Modèle : EzAudio s3_xl (texte → son ; licence MIT,
code github.com/haidog-yaqub/EzAudio et poids huggingface.co/OpenSound/EzAudio), encodeur de texte
google/flan-t5-xl (Apache 2.0). ≈ 23 s de calcul par tirage sur L4, ≈ 3 min d'installation.
"""
import json, os, pathlib, subprocess, sys, time

ENTREE = pathlib.Path(os.environ.get('ENTREE', '/content/ambiance/in'))
SORTIE = pathlib.Path(os.environ.get('SORTIE', '/content/ambiance/out'))
DEPOT = SORTIE.parent / 'EzAudio'


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    if not DEPOT.exists():
        subprocess.run(f'git clone -q https://github.com/haidog-yaqub/EzAudio.git {DEPOT}', shell=True, check=True)
        # Dépendances du dépôt absentes de Colab (son requirements.txt réinstallerait torch) ; ffmpy et
        # pyloudnorm sont demandés par la copie d'audiotools qu'il embarque.
        subprocess.run('pip -q install alias_free_torch einops vector_quantize_pytorch julius torch_stoi pystoi flatten-dict randomname argbind '
                       'sentencepiece soundfile librosa ffmpy pyloudnorm importlib_resources rich markdown2 tensorboard', shell=True, check=True)
    os.chdir(DEPOT)
    sys.path.insert(0, str(DEPOT))
    import torch, soundfile as sf
    from api.ezaudio import EzAudio
    log(torch.cuda.get_device_name(0))
    ez = EzAudio(model_name='s3_xl', device='cuda')
    M = json.loads((ENTREE / 'manifeste.json').read_text(encoding='utf-8'))
    for el in M['elements']:
        for k, graine in enumerate(M.get('graines') or [42, 43]):
            f = SORTIE / f"{el['n']:03d}-ezaudio-{k}.wav"
            if f.exists():
                continue
            t0 = time.time()
            try:
                sr, audio = ez.generate_audio(el['prompt'], length=10, random_seed=int(graine))
            except TypeError:      # version du dépôt sans ces paramètres
                torch.manual_seed(int(graine))
                sr, audio = ez.generate_audio(el['prompt'])
            sf.write(str(f), audio, sr)
            with (SORTIE / 'journal.jsonl').open('a', encoding='utf-8') as j:
                j.write(json.dumps(dict(n=el['n'], graine=graine, sr=sr, secondes=round(time.time() - t0, 1), prompt=el['prompt']), ensure_ascii=False) + '\n')
            log(f.name, sr, 'Hz', round(len(audio) / sr, 1), 's ;', round(time.time() - t0, 1), 's de calcul')
    log('FIN')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # le journal de bord doit toujours finir par une ligne lisible
        import traceback
        traceback.print_exc()
        log('ERREUR', repr(e), 'FIN-EN-ERREUR')
        sys.exit(1)
