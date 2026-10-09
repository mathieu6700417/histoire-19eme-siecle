"""Objets de musée et manuscrits en surimpression (spec 12, « Enrichissements visuels », points 1 et 2,
2026-10-08).

Usage :
    python3 scripts/diaporamas/objets.py --chercher "assiette révolutionnaire"   # aide (Commons)
    python3 scripts/diaporamas/objets.py --registre                 # tout le registre (ce qui manque)
    python3 scripts/diaporamas/objets.py --registre --id assiette-cocarde --force
    python3 scripts/diaporamas/objets.py --planche                  # planche de contrôle (à relire)
    python3 scripts/diaporamas/objets.py revolution --relever       # bilan des mentions d'une période

Registre `src/data/diaporamas/objets.json` (commun à toutes les périodes) :
- objet : `{ id, type: "objet", nom, date, musee, inventaire?, commons, recadrage?, detourage? }` ;
  `nom` est la légende courte (« Assiette à la cocarde tricolore, faïence de Nevers »), `date` celle de
  l'objet, `musee` l'institution qui le conserve. L'objet est d'époque ; la photo peut être récente.
- manuscrit : `{ id, type: "manuscrit", nom, date, musee, inventaire?, commons, recadrage?, halo,
  passage }` ; `halo` : [x0, y0, x1, y1] (fractions de l'image servie, après `recadrage`) de la
  signature ou de la phrase éclairée, `passage` : sa transcription exacte.
- écrits par le script : `fichier` (chemin dans public/diaporamas/), `largeur`, `hauteur`, `auteur_photo`,
  `licence`, `page` (notice Commons).

Licence relevée par l'API Commons : domaine public, CC0, CC BY et CC BY-SA (crédit et lien affichés sur
la page) ; NC, ND, GFDL seule ou licence inconnue refusées.

Détourage (objets) : `rembg` (modèle `isnet-general-use`, libre, local) dans le venv
`.cache/venv-rembg` (`python3 -m venv .cache/venv-rembg && .cache/venv-rembg/bin/pip install
"rembg[cpu]" pillow` ; le modèle, ~180 Mo, est téléchargé au premier usage dans ~/.rembg/models). Le masque
est durci (seuils), l'image rognée sur l'objet avec une petite marge, réduite à 720 px au plus et
écrite en webp à fond transparent (`public/diaporamas/objets/<id>.webp`). `detourage: "convexe"` pour un
objet convexe (assiette, médaille) : enveloppe convexe du masque, qui rend le blanc de la faïence que
le modèle prend pour le fond ; `detourage: "aucun"` pour un objet plat montré tel quel. Manuscrits : webp 1400 px au plus, sans détourage
(`public/diaporamas/manuscrits/<id>.webp`). Originaux en cache : `.cache/diaporamas/objets/`.

Dans une diapositive : `objets: [{ id, quand, cote? }]` et `manuscrits: [{ id, quand, cote? }]` (un de
chaque au plus) ; `quand` : passage exact de la narration ; `instant` écrit par surimpressions.py ;
`cote` : "droite" (défaut) ou "gauche", le coin bas (objet) ou le côté (manuscrit) où il se pose.
"""
import argparse, hashlib, io, json, re, subprocess, sys, time
from pathlib import Path

from PIL import Image, ImageDraw

import commun as c

REGISTRE = c.DONNEES / 'objets.json'
CACHE = c.CACHE / 'objets'
VENV = c.RACINE / '.cache' / 'venv-rembg' / 'bin' / 'python'
MODELE = 'isnet-general-use'
COTE_OBJET = 720
COTE_MANUSCRIT = 1400
QUALITE = 84

# Licences admises : domaine public, CC0, CC BY, CC BY-SA (pas NC, pas ND, pas GFDL seule).
LICENCE_BY = re.compile(r'^CC BY(-SA)? \d\.\d( [a-z]{2})?$', re.I)


def licence(info: dict) -> tuple[bool, str]:
    meta = info.get('meta', {})
    court = c.texte_meta(meta.get('LicenseShortName'))
    pd, _ = c.licence_libre(info)
    if pd:
        return True, 'CC0' if re.match(r'cc0|cc-zero', court, re.I) else 'Domaine public'
    if LICENCE_BY.match(court) and not re.search(r'\bnc\b|\bnd\b', court, re.I):
        return True, court
    return False, court or 'inconnue'


def lire_registre() -> list[dict]:
    return json.loads(REGISTRE.read_text()) if REGISTRE.exists() else []


def ecrire_registre(r: list[dict]) -> None:
    tmp = REGISTRE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(REGISTRE)


def original(o: dict, info: dict) -> Image.Image:
    """Original Commons (cache) ; vignette de 3000 px pour un très grand fichier."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha1(o['commons'].encode()).hexdigest()[:16] + '.img')
    if not f.exists():
        grand = (info.get('largeur') or 0) > 3200 or info.get('mime') not in ('image/jpeg', 'image/png', 'image/webp')
        f.write_bytes(c.http_get(info['vignette'] if grand else info['url']))
        time.sleep(1)
    im = Image.open(f)
    im.load()
    return im


def detourer(im: Image.Image) -> Image.Image:
    """Détourage local par rembg (sous-processus du venv) : RGBA, masque durci."""
    if not VENV.exists():
        raise SystemExit(f'venv de détourage absent ({VENV.relative_to(c.RACINE)}) : voir la notice du script.')
    CACHE.mkdir(parents=True, exist_ok=True)
    entree, sortie = CACHE / '_entree.png', CACHE / '_sortie.png'
    im.convert('RGB').save(entree)
    code = ("import sys; from rembg import remove, new_session; from PIL import Image; "
            f"s = new_session('{MODELE}'); "
            "remove(Image.open(sys.argv[1]), session=s, post_process_mask=True).save(sys.argv[2])")
    subprocess.run([str(VENV), '-I', '-c', code, str(entree), str(sortie)], check=True)
    # Couleurs de l'original (rembg met à zéro celles des pixels qu'il juge transparents : le blanc
    # d'une faïence rendu par l'enveloppe convexe serait noir), masque du modèle.
    rgba = im.convert('RGBA')
    rgba.putalpha(Image.open(sortie).getchannel('A'))
    # Masque durci : les franges à demi transparentes du fond de studio disparaissent, le bord reste doux.
    a = rgba.getchannel('A').point(lambda v: 0 if v < 40 else 255 if v > 215 else int((v - 40) * 255 / 175))
    rgba.putalpha(a)
    entree.unlink(missing_ok=True)
    sortie.unlink(missing_ok=True)
    return rgba


def convexe(rgba: Image.Image) -> Image.Image:
    """Objet convexe (assiette, médaille) : le masque devient l'enveloppe convexe du détourage, ce
    qui rend les parties blanches de la faïence que le modèle confond avec le fond de studio."""
    import numpy as np
    from scipy.spatial import ConvexHull
    a = np.asarray(rgba.getchannel('A')) > 128
    ys, xs = np.nonzero(a)
    pts = np.column_stack([xs, ys])
    coque = pts[ConvexHull(pts).vertices]
    m = Image.new('L', rgba.size, 0)
    ImageDraw.Draw(m).polygon([tuple(map(float, p)) for p in coque], fill=255)
    # Bord adouci d'un pixel environ (l'enveloppe est tracée sans anticrénelage).
    from PIL import ImageFilter
    rgba.putalpha(m.filter(ImageFilter.GaussianBlur(1.2)))
    return rgba


def rogner(rgba: Image.Image, marge: float = 0.02) -> Image.Image:
    boite = rgba.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    if not boite:
        raise SystemExit('détourage vide')
    x0, y0, x1, y1 = boite
    m = int(marge * max(x1 - x0, y1 - y0))
    return rgba.crop((max(0, x0 - m), max(0, y0 - m), min(rgba.width, x1 + m), min(rgba.height, y1 + m)))


def traiter(o: dict, force: bool) -> str:
    dossier = 'objets' if o['type'] == 'objet' else 'manuscrits'
    fichier = f"{dossier}/{o['id']}.webp"
    dest = c.PUBLIC / fichier
    info = c.infos_fichiers([o['commons']], 3000)[o['commons']]
    if info.get('manquant'):
        raise SystemExit(f"{o['id']} : fichier Commons introuvable ({o['commons']})")
    ok, lib = licence(info)
    if not ok:
        raise SystemExit(f"{o['id']} : licence refusée ({lib})")
    meta = info['meta']
    o['licence'] = lib
    o['page'] = info['page']
    if lib.startswith('CC BY'):
        o['auteur_photo'] = re.sub(r'\s+', ' ', c.texte_meta(meta.get('Artist'))).strip()
    else:
        o.pop('auteur_photo', None)
    if dest.exists() and not force and o.get('fichier') == fichier:
        return 'déjà fait'
    im = original(o, info)
    if o.get('recadrage'):
        x0, y0, x1, y1 = o['recadrage']
        im = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    if o['type'] == 'objet' and o.get('detourage') != 'aucun':
        im.thumbnail((2000, 2000))
        im = detourer(im)
        if o.get('detourage') == 'convexe':
            im = convexe(im)
        im = rogner(im)
        im.thumbnail((COTE_OBJET, COTE_OBJET), Image.LANCZOS)
        im.save(dest, 'WEBP', quality=QUALITE, alpha_quality=90, method=6)
    else:
        im = im.convert('RGB')
        im.thumbnail((COTE_OBJET if o['type'] == 'objet' else COTE_MANUSCRIT,) * 2, Image.LANCZOS)
        im.save(dest, 'WEBP', quality=QUALITE - 4, method=6)
    o['fichier'], o['largeur'], o['hauteur'] = fichier, im.width, im.height
    return f'{im.width} × {im.height}, {dest.stat().st_size // 1024} Ko, {lib}'


def registre(ids: list[str] | None, force: bool) -> int:
    r = lire_registre()
    for o in r:
        if ids and o['id'] not in ids:
            continue
        print(f"{o['id']:28s} {traiter(o, force)}")
        ecrire_registre(r)
    return 0


def planche() -> None:
    """Objets détourés sur damier, gris moyen et fond sombre ; manuscrits avec leur halo."""
    r = [o for o in lire_registre() if o.get('fichier')]
    T = 260
    P = Image.new('RGB', (T * 3 + 20, (T + 24) * len(r)), 'white')
    d = ImageDraw.Draw(P)
    for k, o in enumerate(r):
        im = Image.open(c.PUBLIC / o['fichier']).convert('RGBA')
        im.thumbnail((T - 10, T - 10))
        y = k * (T + 24)
        for j, fond in enumerate(('damier', (128, 128, 128), (30, 28, 26))):
            x = j * (T + 10)
            if fond == 'damier':
                f = Image.new('RGB', (T, T), 'white')
                df = ImageDraw.Draw(f)
                for a in range(0, T, 16):
                    for b in range(0, T, 16):
                        if (a + b) // 16 % 2:
                            df.rectangle([a, b, a + 15, b + 15], fill=(205, 205, 205))
            else:
                f = Image.new('RGB', (T, T), fond)
            ox, oy = (T - im.width) // 2, (T - im.height) // 2
            f.paste(im, (ox, oy), im)
            if o['type'] == 'manuscrit' and o.get('halo') and j == 0:
                h = o['halo']
                ImageDraw.Draw(f).rectangle([ox + h[0] * im.width, oy + h[1] * im.height, ox + h[2] * im.width, oy + h[3] * im.height], outline=(220, 0, 0), width=2)
            P.paste(f, (x, y))
        d.text((4, y + T + 4), f"{o['id']} - {o['nom'][:70]} ({o['date']}, {o['musee']})", fill='black')
    CACHE.mkdir(parents=True, exist_ok=True)
    P.save(CACHE / 'planche.jpg', quality=85)
    print(f"planche : {(CACHE / 'planche.jpg').relative_to(c.RACINE)}")


def relever(d: dict) -> None:
    par_id = {o['id']: o for o in lire_registre()}
    for x in d['diapositives']:
        for cle in ('objets', 'manuscrits'):
            for m in x.get(cle, []):
                o = par_id.get(m['id'], {})
                print(f"{x['n']:3d} {cle[:-1]:9s} {m['id']:28s} « {m['quand']} » {m.get('instant', '—')} s, {m.get('cote', 'droite')} — {o.get('musee', '?')}, {o.get('licence', '?')}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug', nargs='?')
    p.add_argument('--chercher')
    p.add_argument('--registre', action='store_true')
    p.add_argument('--id', nargs='+')
    p.add_argument('--force', action='store_true')
    p.add_argument('--planche', action='store_true')
    p.add_argument('--relever', action='store_true')
    a = p.parse_args()
    if a.chercher:
        for x in c.chercher(a.chercher, 15):
            print(f"{x['fichier'][:100]} {x['largeur']}×{x['hauteur']} | {x['licence']} | {x['date']}")
        return 0
    if a.registre:
        registre(a.id, a.force)
    if a.planche:
        planche()
    if a.relever and a.slug:
        relever(c.lire(a.slug)[1])
    return 0


if __name__ == '__main__':
    sys.exit(main())
