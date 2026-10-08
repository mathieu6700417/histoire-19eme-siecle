"""Images d'une période : métadonnées Commons, licence, téléchargement, WebP (spec 12).

Usage :
    python3 scripts/diaporamas/images.py revolution            # toutes les diapositives
    python3 scripts/diaporamas/images.py revolution --n 12     # une seule
    python3 scripts/diaporamas/images.py revolution --force    # refait les WebP existants
    python3 scripts/diaporamas/images.py --chercher "prise de la Bastille" [nombre]
    python3 scripts/diaporamas/images.py --infos "File:…" ["File:…" …]

Pour chaque diapositive : interroge l'API Commons (imageinfo, extmetadata), refuse toute
licence autre que le domaine public (ou CC0), télécharge une version de 2400 px de large
au plus (cache dans .cache/diaporamas/originaux/), retire les marges de papier si le JSON
donne `image.recadrage` ([x0, y0, x1, y1] en fractions), écrit public/diaporamas/<slug>/NNN.webp
(1600 px au plus sur le grand côté, qualité 74) et complète dans le JSON les métadonnées
laissées vides (titre, auteur, date) ainsi que licence, largeur et hauteur. Les champs
déjà remplis à la main ne sont jamais écrasés. Écrit aussi vignette.webp (diapositive 1,
480 px) pour le portail.

Annexes (spec 12, « Lectures d'époque et épisodes ») : les portraits des lectures qui ont leur
propre fichier Commons (`lectures[].portrait.commons` → lectures/<id>.webp, 640 px) et les
fac-similés des épisodes (`visuels[].image` des visuels « document » → episodes/<id>.webp,
2400 px pour rester lisibles au zoom), avec le même contrôle de licence. Un portrait peut aussi
reprendre l'image d'une diapositive (`portrait.diapositive`) : rien à télécharger.
Avant / après et mosaïques (points 3 et 5 des « Enrichissements visuels ») : `image.apres` →
NNN-apres.webp (1600 px, `recadrage` admis) ; `mosaique.vignettes` → NNN-mK.webp (1000 px), la
vignette `principale` reprenant l'image de la diapositive. Même contrôle de licence et de largeur.
"""
import argparse, hashlib, io, json, sys, time
from pathlib import Path

from PIL import Image

import commun as c

LARGEUR_MIN = 1000
GRAND_COTE = 1600
COTE_PORTRAIT = 640
COTE_DOCUMENT = 2400
COTE_VIGNETTE = 1000   # vignettes d'une mosaïque (une case de la grille)
QUALITE = 74


def telecharger(url: str) -> bytes:
    cache = c.CACHE / 'originaux'
    cache.mkdir(parents=True, exist_ok=True)
    f = cache / (hashlib.sha1(url.encode()).hexdigest() + Path(url.split('?')[0]).suffix.lower())
    if f.exists():
        return f.read_bytes()
    donnees = c.http_get(url)
    f.write_bytes(donnees)
    time.sleep(1)
    return donnees


def en_webp(donnees: bytes, destination: Path, cote: int, recadrage=None) -> tuple[int, int]:
    im = Image.open(io.BytesIO(donnees))
    im.load()
    if recadrage:
        # Marges de papier retirées : [x0, y0, x1, y1] en fractions de l'image d'origine.
        x0, y0, x1, y1 = recadrage
        im = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
    if im.mode not in ('RGB', 'L'):
        fond = Image.new('RGB', im.size, (251, 250, 247))
        im = im.convert('RGBA')
        fond.paste(im, mask=im.split()[-1])
        im = fond
    elif im.mode == 'L':
        im = im.convert('RGB')
    im.thumbnail((cote, cote), Image.LANCZOS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    im.save(destination, 'WEBP', quality=QUALITE, method=6)
    return im.size


def annexes(d: dict, dossier: Path, etat: dict, force: bool) -> list[str]:
    """Portraits des lectures et fac-similés des épisodes (voir le docstring du module)."""
    a_faire = []  # (clé d'état, dictionnaire image, côté)
    for l in d.get('lectures', []):
        po = l.get('portrait') or {}
        if po.get('commons'):
            po.setdefault('fichier', f"lectures/{l['id']}.webp")
            a_faire.append((f"lecture:{l['id']}", po, COTE_PORTRAIT))
    for e in d.get('episodes', []):
        for k, v in enumerate(e.get('visuels', [])):
            if v.get('type') == 'document':
                v['image'].setdefault('fichier', f"episodes/{e['id']}.webp")
                a_faire.append((f"episode:{e['id']}:{k}", v['image'], COTE_DOCUMENT))
    # Avant / après et mosaïques (spec 12, « Enrichissements visuels », points 3 et 5) : l'image
    # « après » (NNN-apres.webp, 1600 px) et les vignettes d'une mosaïque (NNN-mK.webp, 1000 px ; la
    # vignette principale est l'image de la diapositive, rien à télécharger). Clés d'état par
    # fichier Commons : elles survivent aux renumérotations.
    for x in d['diapositives']:
        ap = x['image'].get('apres')
        if ap and ap.get('commons'):
            ap['fichier'] = c.nom(x['n'], 'webp').replace('.webp', '-apres.webp')
            a_faire.append((f"apres:{ap['commons']}", ap, GRAND_COTE))
        mo = x.get('mosaique')
        for k, v in enumerate((mo or {}).get('vignettes', [])):
            if k == mo.get('principale'):
                v['fichier'] = x['image']['fichier']
                for champ in ('titre', 'auteur', 'date', 'technique', 'conservation', 'licence', 'largeur', 'hauteur', 'utile'):
                    if champ in x['image']:
                        v[champ] = x['image'][champ]
                continue
            v['fichier'] = c.nom(x['n'], 'webp').replace('.webp', f'-m{k}.webp')
            a_faire.append((f"vignette:{v['commons']}", v, COTE_VIGNETTE))
    if not a_faire:
        return []
    infos = c.infos_fichiers([img['commons'] for _, img, _ in a_faire])
    echecs = []
    for cle, img, cote in a_faire:
        info = infos.get(img['commons'], {'manquant': True})
        if info.get('manquant'):
            echecs.append(f"{cle} : fichier Commons introuvable : {img['commons']}")
            continue
        libre, licence = c.licence_libre(info)
        ancien = etat.get(cle, {})
        etat[cle] = {'commons': info['titre_fichier'], 'licence': licence, 'libre': libre,
                     'largeur': info['largeur'], 'hauteur': info['hauteur'], 'page': info['page']}
        if not libre:
            echecs.append(f"{cle} : licence refusée ({licence}) : {img['commons']}")
            continue
        if cle.startswith(('apres:', 'vignette:')) and (info['largeur'] or 0) < LARGEUR_MIN:
            echecs.append(f"{cle} : image trop petite ({info['largeur']} px)")
        img['commons'] = info['titre_fichier']
        img['licence'] = 'Domaine public'
        sortie = dossier / img['fichier']
        etat[cle]['recadrage'] = img.get('recadrage')
        if sortie.exists() and not force and img.get('largeur') and ancien.get('commons') == img['commons'] \
                and ancien.get('recadrage') == img.get('recadrage'):
            continue
        try:
            infos_l = c.infos_fichiers([img['commons']], largeur=max(cote, 2400 if cote == GRAND_COTE else cote))[img['commons']]
            largeur, hauteur = en_webp(telecharger(infos_l['vignette']), sortie, cote, img.get('recadrage'))
        except Exception as e:  # noqa: BLE001
            echecs.append(f'{cle} : téléchargement ou conversion impossible ({e})')
            continue
        img['largeur'], img['hauteur'] = largeur, hauteur
        print(f"{cle} {img['fichier']} {largeur}×{hauteur} {sortie.stat().st_size // 1024} Ko · {img['commons']}")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug', nargs='?')
    p.add_argument('--n', type=int, help='une seule diapositive')
    p.add_argument('--force', action='store_true', help='refaire les WebP déjà présents')
    p.add_argument('--chercher', nargs='+', metavar=('REQUETE', 'NOMBRE'))
    p.add_argument('--infos', nargs='+', metavar='FICHIER', help='métadonnées Commons complètes de fichiers')
    a = p.parse_args()

    if a.infos:
        for t, info in c.infos_fichiers(a.infos).items():
            if info.get('manquant'):
                print(f'{t}\n    INTROUVABLE\n')
                continue
            libre, licence = c.licence_libre(info)
            m = info['meta']
            print(f"{info['titre_fichier']}\n    {info['largeur']}×{info['hauteur']} · licence {licence} ({'acceptée' if libre else 'REFUSÉE'})")
            for champ in ('ObjectName', 'Artist', 'DateTimeOriginal', 'ImageDescription', 'Credit'):
                v = c.titre_objet(m.get(champ)) if champ == 'ObjectName' else c.texte_meta(m.get(champ))
                if v:
                    print(f'    {champ} : {v[:300]}')
            print()
        return 0

    if a.chercher:
        nombre = int(a.chercher[1]) if len(a.chercher) > 1 else 10
        for r in c.chercher(a.chercher[0], nombre):
            print(f"{r['fichier']}\n    {r['largeur']}×{r['hauteur']} · {r['licence']} · {r['auteur']} · {r['date']} · {r['titre']}")
        return 0
    if not a.slug:
        p.error('indiquer une période (slug) ou --chercher')

    f, d = c.lire(a.slug)
    dossier = c.PUBLIC / d['slug']
    diapos = [x for x in d['diapositives'] if a.n is None or x['n'] == a.n]
    infos = c.infos_fichiers([x['image']['commons'] for x in diapos])
    etat_f = c.CACHE / d['slug'] / 'images.json'
    etat = json.loads(etat_f.read_text()) if etat_f.exists() else {}
    ancien = json.loads(json.dumps(etat))
    echecs = []

    for x in diapos:
        img = x['image']
        img.setdefault('fichier', c.nom(x['n'], 'webp'))
        info = infos.get(img['commons'], {'manquant': True})
        if info.get('manquant'):
            echecs.append(f"{x['n']:3d} : fichier Commons introuvable : {img['commons']}")
            continue
        libre, licence = c.licence_libre(info)
        meta = info['meta']
        etat[str(x['n'])] = {
            'commons': info['titre_fichier'], 'licence': licence, 'libre': libre,
            'largeur': info['largeur'], 'hauteur': info['hauteur'], 'page': info['page'],
            'auteur': c.texte_meta(meta.get('Artist')), 'date': c.texte_meta(meta.get('DateTimeOriginal')),
            'titre': c.titre_objet(meta.get('ObjectName')),
        }
        if not libre:
            echecs.append(f"{x['n']:3d} : licence refusée ({licence}) : {img['commons']}")
            continue
        if (info['largeur'] or 0) < LARGEUR_MIN:
            echecs.append(f"{x['n']:3d} : image trop petite ({info['largeur']} px) : {img['commons']}")
        img['commons'] = info['titre_fichier']
        img['licence'] = 'Domaine public'
        # Métadonnées manquantes : complétées depuis Commons (à relire avant publication).
        for champ, valeur in (('titre', etat[str(x['n'])]['titre']), ('auteur', etat[str(x['n'])]['auteur']),
                              ('date', etat[str(x['n'])]['date'])):
            if not img.get(champ) and valeur:
                img[champ] = valeur[:160]
        sortie = dossier / img['fichier']
        etat[str(x['n'])]['recadrage'] = img.get('recadrage')
        if sortie.exists() and not a.force and img.get('largeur') and ancien.get(str(x['n']), {}).get('recadrage') == img.get('recadrage') \
                and ancien.get(str(x['n']), {}).get('commons') == img['commons']:
            continue
        try:
            donnees = telecharger(info['vignette'])
            largeur, hauteur = en_webp(donnees, sortie, GRAND_COTE, img.get('recadrage'))
        except Exception as e:  # noqa: BLE001 — on signale et on continue
            echecs.append(f"{x['n']:3d} : téléchargement ou conversion impossible ({e})")
            continue
        img['largeur'], img['hauteur'] = largeur, hauteur
        print(f"{x['n']:3d} {img['fichier']} {largeur}×{hauteur} {sortie.stat().st_size // 1024} Ko · {img['commons']}")

    if a.n is None:
        echecs += annexes(d, dossier, etat, a.force)

    # Vignette du portail : la première diapositive, petite.
    premiere = dossier / d['diapositives'][0]['image'].get('fichier', '001.webp')
    if premiere.exists() and (a.force or not (dossier / 'vignette.webp').exists()):
        en_webp(premiere.read_bytes(), dossier / 'vignette.webp', 480)

    c.ecrire(f, d)
    etat_f.parent.mkdir(parents=True, exist_ok=True)
    etat_f.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
    if echecs:
        print(f'\n{len(echecs)} problème(s) :', *echecs, sep='\n  ')
        return 1
    print(f'\n{len(diapos)} image(s) à jour dans {dossier.relative_to(c.RACINE)}/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
