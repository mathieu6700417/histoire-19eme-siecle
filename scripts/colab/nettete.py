#!/usr/bin/env python3
"""Agrandissement d'images par Real-ESRGAN x4plus (spec 17) sur une session Colab pilotée par la CLI `colab`.

    entrées  $ENTREE/manifeste.json et $ENTREE/sources/<cle>.png (kit de `nettete.py preparer`)
    sorties  $SORTIE/<cle>.webp (×4 puis réduction Lanczos à la largeur et la hauteur du manifeste),
             $SORTIE/journal.jsonl ; journal de bord sur la sortie standard (log.txt), fini par « FIN »
Lancé en arrière-plan (nohup) par `nettete.py lancer`. Modèle : poids RealESRGAN_x4plus.pth de la version
v0.1.0 du dépôt xinntao/Real-ESRGAN (BSD 3-Clause, code et poids), chargé par spandrel (MIT). Calcul par
tuiles de 512 px recouvertes de 32 px, fondues en rampe : aucune couture. ≈ 5 à 20 s par image sur L4.
"""
import json, os, pathlib, subprocess, sys, time

ENTREE = pathlib.Path(os.environ.get('ENTREE', '/content/nettete/in'))
SORTIE = pathlib.Path(os.environ.get('SORTIE', '/content/nettete/out'))
POIDS = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
TUILE, BORD = 512, 32


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    subprocess.run('pip -q install spandrel', shell=True, check=True)
    import numpy as np, torch
    from PIL import Image
    from spandrel import ModelLoader
    Image.MAX_IMAGE_PIXELS = None
    log(torch.cuda.get_device_name(0))
    poids = SORTIE.parent / 'RealESRGAN_x4plus.pth'
    if not poids.exists():
        subprocess.run(f'wget -q -O {poids} {POIDS}', shell=True, check=True)
    mod = ModelLoader().load_from_file(str(poids))
    net, s = mod.model.cuda().eval().half(), mod.scale
    M = json.loads((ENTREE / 'manifeste.json').read_text(encoding='utf-8'))
    for el in M['elements']:
        f = SORTIE / f"{el['cle']}.webp"
        if f.exists():
            continue
        im = Image.open(ENTREE / el['source']).convert('RGB')
        x = (torch.tensor(np.asarray(im), device='cuda').permute(2, 0, 1)[None].float() / 255).half()
        H, W = x.shape[-2:]
        somme = torch.zeros(3, H * s, W * s)
        poids_t = torch.zeros(1, H * s, W * s)
        pas = TUILE - 2 * BORD
        ys = sorted({min(y, max(0, H - TUILE)) for y in range(0, H, pas)})
        xs = sorted({min(v, max(0, W - TUILE)) for v in range(0, W, pas)})
        t0 = time.time()
        for y in ys:
            for v in xs:
                t = x[..., y:y + TUILE, v:v + TUILE]
                h, w = t.shape[-2:]
                with torch.no_grad():
                    o = net(t)[0].float().clamp(0, 1).cpu()
                ry = torch.minimum(torch.arange(1, h * s + 1), torch.arange(h * s, 0, -1)).clamp(max=BORD * s).float()
                rx = torch.minimum(torch.arange(1, w * s + 1), torch.arange(w * s, 0, -1)).clamp(max=BORD * s).float()
                m = (ry[:, None] * rx[None, :])[None]
                somme[:, y * s:(y + h) * s, v * s:(v + w) * s] += o * m
                poids_t[:, y * s:(y + h) * s, v * s:(v + w) * s] += m
        grand = Image.fromarray(((somme / poids_t.clamp(min=1e-6)).permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8))
        grand.resize((int(el['largeur']), int(el['hauteur'])), Image.LANCZOS).save(f, 'WEBP', quality=int(M.get('qualite', 74)), method=6)
        d = time.time() - t0
        with (SORTIE / 'journal.jsonl').open('a', encoding='utf-8') as j:
            j.write(json.dumps(dict(cle=el['cle'], entree=[W, H], sortie=[el['largeur'], el['hauteur']], secondes=round(d, 1), octets=f.stat().st_size)) + '\n')
        log(f"{f.name} : {W}×{H} → {el['largeur']}×{el['hauteur']}, {d:.0f} s, {f.stat().st_size / 1e6:.2f} Mo")
    log('FIN')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # le journal de bord doit toujours finir par une ligne lisible
        import traceback
        traceback.print_exc()
        log('ERREUR', repr(e), 'FIN-EN-ERREUR')
        sys.exit(1)
