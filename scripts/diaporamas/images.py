"""Images d'une période : métadonnées Commons, licence, téléchargement, WebP (spec 12).

Usage :
    python3 scripts/diaporamas/images.py revolution            # toutes les diapositives
    python3 scripts/diaporamas/images.py revolution --n 12     # une seule
    python3 scripts/diaporamas/images.py revolution --force    # refait les WebP existants
    python3 scripts/diaporamas/images.py --chercher "prise de la Bastille" [nombre]
    python3 scripts/diaporamas/images.py --infos "File:…" ["File:…" …]
    python3 scripts/diaporamas/images.py --lot recherches.txt [--nombre 12]   # lignes « cle|requête »

`--lot FICHIER` (2026-10-09) : une recherche Commons par ligne `cle|requête` (lignes vides et `#`
ignorées) ; ne garde que les fichiers libres (domaine public, CC0) d'au moins LARGEUR_MIN px ;
sortie compacte, une ligne par fichier retenu avec son nom complet (jamais tronqué) ; résultats
dans .cache/diaporamas/lots/<nom>.json et planche-contact <nom>.jpg (vignettes numérotées
`cle:k`, par ligne de recherche).

Pour chaque diapositive : interroge l'API Commons (imageinfo, extmetadata), refuse toute
licence autre que le domaine public (ou CC0), télécharge une version de 2400 px de large
au plus (cache dans .cache/diaporamas/originaux/), retire les marges de papier si le JSON
donne `image.recadrage` ([x0, y0, x1, y1] en fractions), écrit public/<siecle>/diaporamas/<slug>/NNN.webp
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

Spec 14 (plans, lectures illustrées, galeries, panneaux `image`) : `diapositives[].plans[].image` →
NNN-b.webp, NNN-c.webp ; `lectures[].images[].image` → lectures/<id>-<k>.webp ;
`musique.intermedes[].galerie[].image` → galeries/<id>-<k>.webp ; visuels « image » des épisodes →
episodes/<id>-<k>.webp (1600 px, `recadrage` admis, notice complétée, licence et largeur contrôlées).
`--n 3,7,12` : ces diapositives et les images de la spec 14 qui s'y rattachent (plans, segment « après n »).

Cadrage des vignettes (2026-10-09) : `mosaique.vignettes[].cadre` = le visage principal de la
vignette ([x0, y0, x1, y1], fractions du WebP servi), relevé localement et gratuitement (YuNet,
`visages_local.py`) à chaque passe ; le lecteur centre la case sur lui (dans la zone utile) au lieu
du centre de l'image (CE 100 : les portraits en pied montraient le torse et les jambes). Sans
visage net, pas de `cadre` (centre de la zone utile). Correction à la main : écrire `cadre` (le
point à garder au centre est son centre) et `"cadre_manuel": true`. `--vignettes` ne fait que ça.
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
VISAGE_VIGNETTE_MIN = 0.06   # hauteur minimale (fraction de la vignette) d'un visage de cadrage
QUALITE = 74
# Spec 14 : une image supplémentaire (plan, lecture, galerie, panneau) ne dépasse pas ~400 Ko ; une
# lithographie recadrée, très détaillée, est réencodée en baissant la qualité par paliers, puis, si
# cela ne suffit pas, réduite par paliers de 10 % (jamais sous COTE_MIN_SUP px de grand côté).
POIDS_MAX_SUP = 400_000
QUALITE_MIN_SUP = 56
COTE_MIN_SUP = 1200


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


def en_webp(donnees: bytes, destination: Path, cote: int, recadrage=None, poids_max: int | None = None) -> tuple[int, int]:
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
    qualite = QUALITE
    while poids_max and destination.stat().st_size > poids_max:
        if qualite > QUALITE_MIN_SUP:
            qualite = max(QUALITE_MIN_SUP, qualite - 6)
        elif max(im.size) * 0.9 >= COTE_MIN_SUP:
            im = im.resize((round(im.width * 0.9), round(im.height * 0.9)), Image.LANCZOS)
        else:
            break
        im.save(destination, 'WEBP', quality=qualite, method=6)
    return im.size


def annexes(d: dict, dossier: Path, etat: dict, force: bool, ns: list[int] | None = None) -> list[str]:
    """Portraits des lectures et fac-similés des épisodes (voir le docstring du module) ; images de
    la spec 14 (plans, lectures illustrées, galeries, panneaux `image`). `ns` : seulement les images
    de la spec 14 rattachées à ces diapositives."""
    a_faire = []  # (clé d'état, dictionnaire image, côté)
    # Spec 14 : plans (NNN-b.webp), images des lectures (lectures/<id>-k.webp), galeries des intermèdes
    # (galeries/<id>-k.webp), panneaux `image` des épisodes (episodes/<id>-k.webp). Clés d'état par
    # fichier Commons ; le nom du fichier d'un plan suit le numéro de la diapositive.
    for s in c.images_supplementaires(d, ns):
        img = s['image']
        if not img.get('commons'):
            continue
        if s['genre'] == 'plan':
            img['fichier'] = s['fichier']
        else:
            img.setdefault('fichier', s['fichier'])
        a_faire.append((f"spec14:{s['genre']}:{img['commons']}", img, GRAND_COTE))
    if ns is not None:
        return _annexes(a_faire, dossier, etat, force)
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
    return _annexes(a_faire, dossier, etat, force)


def _annexes(a_faire: list, dossier: Path, etat: dict, force: bool) -> list[str]:
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
        sup = cle.startswith('spec14:')
        if sup:
            # Notice manquante : complétée depuis Commons (à relire), comme pour une diapositive.
            meta = info['meta']
            etat[cle].update(auteur=c.texte_meta(meta.get('Artist')), date=c.texte_meta(meta.get('DateTimeOriginal')),
                             titre=c.titre_objet(meta.get('ObjectName')))
            for champ in ('titre', 'auteur', 'date'):
                if not img.get(champ) and etat[cle][champ]:
                    img[champ] = etat[cle][champ][:160]
        if (cle.startswith(('apres:', 'vignette:')) or sup) and (info['largeur'] or 0) < LARGEUR_MIN:
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
            largeur, hauteur = en_webp(telecharger(infos_l['vignette']), sortie, cote, img.get('recadrage'),
                                       POIDS_MAX_SUP if sup else None)
        except Exception as e:  # noqa: BLE001
            echecs.append(f'{cle} : téléchargement ou conversion impossible ({e})')
            continue
        img['largeur'], img['hauteur'] = largeur, hauteur
        print(f"{cle} {img['fichier']} {largeur}×{hauteur} {sortie.stat().st_size // 1024} Ko · {img['commons']}")
    return echecs


def visages_vignettes(slug: str, chemins: list[Path]) -> dict[str, list[list[float]]]:
    """Visages locaux (YuNet, `visages_local.py`, gratuit) des fichiers donnés, en cache par empreinte
    du fichier dans .cache/diaporamas/<slug>/vignettes-visages.json : {nom de fichier: rectangles}."""
    import subprocess
    f = c.CACHE / slug / 'vignettes-visages.json'
    cache = json.loads(f.read_text()) if f.exists() else {}
    cles = {p.name: hashlib.sha1(p.read_bytes()).hexdigest()[:16] for p in chemins if p.exists()}
    manque = [p for p in chemins if p.exists() and cles[p.name] not in cache]
    if manque:
        py = c.RACINE / '.cache' / 'venv-visages' / 'bin' / 'python'
        if not py.exists():
            raise SystemExit(f'venv des visages absent ({py.relative_to(c.RACINE)}) : voir visages_local.py.')
        r = subprocess.run([str(py), str(Path(__file__).with_name('visages_local.py'))],
                           input=json.dumps([str(p) for p in manque]), capture_output=True, text=True)
        if r.returncode:
            raise SystemExit('Détection locale des visages en échec :\n' + r.stderr[-1500:])
        cache.update(zip((cles[p.name] for p in manque), json.loads(r.stdout)))
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(cache, ensure_ascii=False))
    return {nom: cache[cle] for nom, cle in cles.items()}


def visage_principal(faces: list[list[float]]) -> list[float] | None:
    """Le visage net le plus grand (assez haut, pas une bande aberrante), un visage du bas de l'image
    comptant pour un tiers (fausses détections dans les drapés : l'hermine du sacre, CE 100), ou
    None. Les petites têtes d'une scène de foule (moins de VISAGE_VIGNETTE_MIN) ne cadrent rien."""
    nets = [k for k in faces if k[3] - k[1] >= VISAGE_VIGNETTE_MIN and (k[2] - k[0]) <= 3 * (k[3] - k[1])]
    poids = lambda k: (k[2] - k[0]) * (k[3] - k[1]) * (1 if (k[1] + k[3]) / 2 < 0.6 else 1 / 3)
    return max(nets, key=poids, default=None)


def cadrer_vignettes(d: dict, dossier: Path) -> list[str]:
    """`cadre` de chaque vignette (hors principale, cadrée par sa caméra) : son visage principal ;
    les cadres manuels (`cadre_manuel`) sont gardés. Rend une ligne par vignette changée."""
    mos = [(x, k, v) for x in d['diapositives'] for k, v in enumerate((x.get('mosaique') or {}).get('vignettes', []))
           if k != x['mosaique'].get('principale') and v.get('fichier')]
    faces = visages_vignettes(d['slug'], [dossier / v['fichier'] for _, _, v in mos])
    sortie = []
    for x, k, v in mos:
        if v.get('cadre_manuel') or v['fichier'] not in faces:
            continue
        cadre = visage_principal(faces[v['fichier']])
        if cadre != v.get('cadre'):
            sortie.append(f"{x['n']:3d} vignette {k} ({v['fichier']}) : cadre {v.get('cadre')} → {cadre}")
            if cadre is None:
                v.pop('cadre', None)
            else:
                v['cadre'] = cadre
    return sortie


def chercher_libres(requete: str, nombre: int) -> tuple[list[dict], int]:
    """Recherche Commons filtrée (licence libre, largeur) : (retenus, nombre de résultats bruts)."""
    d = c.api_commons(action='query', generator='search', gsrsearch=f'{requete} filetype:bitmap',
                      gsrnamespace=6, gsrlimit=nombre, prop='imageinfo', iiprop='size|mime|url|extmetadata',
                      iiurlwidth=300, iiextmetadatalanguage='fr',
                      iiextmetadatafilter='ObjectName|Artist|DateTimeOriginal|LicenseShortName|License')
    pages = sorted(d.get('query', {}).get('pages', []), key=lambda p: p.get('index', 0))
    retenus = []
    for p in pages:
        info = (p.get('imageinfo') or [{}])[0]
        meta = {k: v.get('value') for k, v in (info.get('extmetadata') or {}).items()}
        libre, licence = c.licence_libre({'meta': meta})
        if not libre or (info.get('width') or 0) < LARGEUR_MIN:
            continue
        retenus.append({'fichier': p['title'], 'largeur': info.get('width'), 'hauteur': info.get('height'),
                        'licence': licence, 'titre': c.titre_objet(meta.get('ObjectName')),
                        'auteur': c.texte_meta(meta.get('Artist')), 'date': c.texte_meta(meta.get('DateTimeOriginal')),
                        'vignette': info.get('thumburl'), 'page': info.get('descriptionurl')})
    return retenus, len(pages)


def lot(fichier: Path, nombre: int) -> int:
    """Recherches par lots (`cle|requête` par ligne) : sortie compacte, JSON, planche-contact."""
    from PIL import ImageDraw
    lignes = [l.split('|', 1) for l in fichier.read_text().splitlines() if l.strip() and not l.lstrip().startswith('#')]
    if any(len(l) != 2 for l in lignes):
        raise SystemExit('format attendu : une ligne « cle|requête » par recherche')
    resultats = {}
    for cle, requete in lignes:
        cle, requete = cle.strip(), requete.strip()
        retenus, bruts = chercher_libres(requete, nombre)
        resultats[cle] = {'requete': requete, 'resultats': retenus}
        print(f'{cle} « {requete} » : {len(retenus)} libre(s) ≥ {LARGEUR_MIN} px sur {bruts}')
        for k, r in enumerate(retenus, 1):
            print(f"  {cle}:{k} {r['largeur']}×{r['hauteur']} · {r['date'][:20]} · {r['auteur'][:40]} · {r['titre'][:60]}")
            print(f"      {r['fichier']}")
        time.sleep(0.5)
    dossier = c.CACHE / 'lots'
    dossier.mkdir(parents=True, exist_ok=True)
    base = dossier / f'images-{fichier.stem}'
    base.with_suffix('.json').write_text(json.dumps(resultats, ensure_ascii=False, indent=1))
    # Planche-contact : une rangée par recherche, vignettes numérotées cle:k.
    W, col = 200, max([len(v['resultats']) for v in resultats.values()] + [1])
    P = Image.new('RGB', (W * col + 120, (W + 20) * max(1, len(resultats))), 'white')
    dr = ImageDraw.Draw(P)
    for i, (cle, v) in enumerate(resultats.items()):
        dr.text((4, i * (W + 20) + W // 2), cle[:18], fill='black')
        for k, r in enumerate(v['resultats']):
            try:
                im = Image.open(io.BytesIO(c.http_get(r['vignette']))).convert('RGB')
            except Exception:  # noqa: BLE001
                continue
            im.thumbnail((W - 6, W - 6))
            P.paste(im, (120 + k * W, i * (W + 20) + 16))
            dr.text((120 + k * W, i * (W + 20) + 2), f"{cle}:{k + 1} {r['largeur']}px", fill='black')
    P.save(base.with_suffix('.jpg'), quality=80)
    print(f"Résultats : {base.with_suffix('.json').relative_to(c.RACINE)} ; planche : {base.with_suffix('.jpg').relative_to(c.RACINE)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug', nargs='?')
    p.add_argument('--n', type=lambda v: [int(k) for k in v.replace(',', ' ').split()], metavar='N[,N…]',
                   help='ces diapositives seulement (« 3,7,12 »), avec leurs plans et les images de la spec 14\n'
                        'qui s’y rattachent (lecture, galerie ou épisode « après n »)')
    p.add_argument('--force', action='store_true', help='refaire les WebP déjà présents')
    p.add_argument('--chercher', nargs='+', metavar=('REQUETE', 'NOMBRE'))
    p.add_argument('--infos', nargs='+', metavar='FICHIER', help='métadonnées Commons complètes de fichiers')
    p.add_argument('--lot', metavar='FICHIER', help='recherches par lots : lignes « cle|requête »')
    p.add_argument('--nombre', type=int, default=12, help='résultats bruts demandés par recherche (--lot)')
    p.add_argument('--vignettes', action='store_true',
                   help='seulement le cadrage des vignettes des mosaïques sur leur visage (local, sans réseau)')
    a = p.parse_args()

    if a.lot:
        return lot(Path(a.lot), a.nombre)
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
    if a.vignettes:
        for ligne in cadrer_vignettes(d, dossier) or ['vignettes déjà cadrées']:
            print(ligne)
        c.ecrire(f, d)
        return 0
    diapos = [x for x in d['diapositives'] if a.n is None or x['n'] in a.n]
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

    if a.n is not None:
        echecs += annexes(d, dossier, etat, a.force, a.n)
    if a.n is None:
        echecs += annexes(d, dossier, etat, a.force)
        for ligne in cadrer_vignettes(d, dossier):
            print(ligne)

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
