#!/usr/bin/env python3
"""Fonds prolongés des images entières (spec 17, « Fonds prolongés des images entières »).

Une image montrée en entier (drapeau `image.entier`) laissait du noir autour d'elle. Un modèle à poids
ouverts (FLUX.2 klein 4B, Apache 2.0, sur Colab) prolonge la scène autour de l'image ; le lecteur
montre ce prolongement flouté et un peu assombri derrière l'image d'époque, qui reste le fichier
servi, intact (src/scripts/diaporama/fond.ts). Mode d'emploi complet : README, « Fonds prolongés ».

    python3 scripts/diaporamas/fond.py preparer <slug>                 # passe 1 : toiles, consignes, kit
    python3 scripts/diaporamas/fond.py lancer <slug> [--graines 1,2] [--seulement 001,004-b] [--garder]
                                              [--gpu L4] [--session NOM] [--reprendre [--renvoyer-kit]] [--sans-suivi]
    python3 scripts/diaporamas/fond.py relire <slug> [--tirage 1] [--seulement …]     # passe 1 : choisir les tirages (constats.json)
    python3 scripts/diaporamas/fond.py lancer <slug> --passe 2 --reprendre [--graines 1,2]   # haut et bas des décors
    python3 scripts/diaporamas/fond.py relire <slug> [--tirage2 2]                     # relecture finale, à l'échelle de génération
    python3 scripts/diaporamas/fond.py planche <slug> [--largeur 1024]                 # fonds finis, fonds.json, planche.html
    python3 scripts/diaporamas/fond.py publier <slug> [--seulement 86,34b] [--sauf 100,12b] [--essai] [--lot fonds.json]
    python3 scripts/diaporamas/fond.py retirer <slug> 86 34b …            # ou --tout
    python3 scripts/diaporamas/fond.py lister <slug>
    python3 scripts/diaporamas/fond.py rapatrier <slug> [--passe 2] | arreter <slug>   # session laissée ouverte

Sur la session, chaque période a son dossier (/content/fond/<slug>/) : une session sert plusieurs périodes
(`--session NOM --garder`, puis `--reprendre --renvoyer-kit` pour la période suivante).

Tout va dans .cache/diaporamas/fonds/<slug>/ :
    lot.json                   par image (nom du fichier servi sans extension) : { "genre": "decor|uni|papier",
                               "plus": "phrase anglaise : ce que montrent les côtés", "dessus": "…", "dessous": "…"
                               (ce qu'il y a au-dessus et au-dessous : obligatoires pour un décor),
                               "bandes": "modele|papier|etire" (rare : force le procédé du haut et du bas),
                               "teinte": "gauche|droite|coins" (uni, papier : même teinte des deux côtés, prise sur ce bord
                               ou dans les coins de l'image, quand les deux côtés sortent de teintes différentes) }
    in/, manifeste.json, kit.zip        passe 1 (`preparer`) ; orig/ : zones utiles pour la planche
    bruts/<nom>-g<k>.jpg                sorties de la passe 1, tirage k
    in2/, manifeste2.json, kit2.zip     passe 2 (`lancer --passe 2`, d'après les tirages retenus)
    bruts2/<nom>-g<k>.jpg               sorties de la passe 2
    constats.json                       relecture, par image : { "tirage": 1, "tirage2": 1, "flou": "faible|fort",
                                        "invente": "…", "raison": "… (pourquoi le flou fort)" }
    relecture-g…-h…/                    montages à l'échelle de génération (`relire`)
    fonds/<nom>-fond.webp, fonds.json   fonds finis (`planche`) ; planche.html

**Méthode (retenue le 2026-10-12 après deux retours de l'utilisateur).** Deux passes du modèle.
Passe 1 : la zone utile est posée au centre d'une toile de 1392 × 576 px (2,42 hauteurs d'image de
large, multiples de 16), le reste prérempli d'un flou de la même image ; le modèle prolonge **les
côtés**. Toile grise unie à la place du flou (2026-10-18, `toile_de`) pour les décors photographiques ou
sombres, où le modèle laissait le flou (période 06) ; `"toile": "grise" | "floue"` dans lot.json force
le choix, et la passe 2 suit la même toile. La sortie est accordée en couleur sur l'original (gain et décalage par canal mesurés sur la
partie commune), raccordée à ses bords, et l'original est recollé. Passe 2, pour les décors : cette
image élargie est posée au milieu d'une toile de 1392 × 864 px (25 % de plus en haut et en bas),
bandes préremplies d'un flou, et le modèle prolonge **le haut et le bas** d'après une consigne qui
les nomme ; les bandes sont accordées sur les lignes de bord et la jonction est fondue sur
`JONCTION` px. Genres « papier » et « uni » : pas de passe 2, des bandes de papier continues sans
modèle (miroir des lignes des côtés, teinte interpolée au-dessus et au-dessous de l'image).

**Format du fond.** Toile centrée sur l'image : 2,42 h de large, 1,5 h de haut (h = hauteur de
l'image). Elle couvre ce que la scène montre autour d'une image entière au repos pour les formes de
scène de `camera.py` (`SCENES_ENTIER`, 1:1 à 2,3:1), le plein écran 16:9 (les bandeaux ne laissent à
l'image que ≈ 80 % de la hauteur, décalée vers le haut) et le téléphone (image posée au-dessus des
cartouches du bas). Le lecteur pose le fond d'après `boite` (place de l'image dans le fond, en
fractions) et lui donne la transformation de l'image ; au-delà de la toile, fond noir. Fichier WebP
de `LARGEUR_FAIBLE` px (1 024 : indiscernable de 1 392 px à 0,25 % de flou sur une scène de
2 560 px ; 640 px se voit) ou de `LARGEUR_FORT` px (640) en flou fort.

**Relecture obligatoire, à l'échelle de génération** (`relire` : 1392 × 864, pas de montage réduit) :
personnage, visage, animal, texte, enseigne, cachet, cadre, image dans l'image, objet incongru,
anachronisme, rendu de photographie → autre tirage ; si l'invention persiste, `"flou": "fort"` dans
constats.json (le fond n'est pas rejeté : 2,5 % de flou le cachent). Regarder aussi les défauts de
continuité : zone restée floue (préremplissage laissé par le modèle : refaire ce tirage sur toile
grise), jonction horizontale à la limite des bandes, sujet répété sous l'image.

**Faux départs à ne pas refaire.** (1) Une consigne générique pour les décors (« sky, ground, walls,
drapery, vegetation or water ») fait peindre un paysage sans rapport autour d'un intérieur : il faut
une phrase par image (`plus`, `dessus`, `dessous`). (2) Demander en une seule passe les côtés, le
haut et le bas : le modèle peint une pièce où le tableau est posé debout ; d'où les deux passes.
(3) Des bandes du haut et du bas étirées sans IA à partir du bord : refusées par l'utilisateur.

`publier` lit fonds.json, retrouve chaque image par son `commons` (la clé survit aux
renumérotations), refuse celle qui n'est plus montrée en entier ou dont la zone utile a changé depuis
la fabrication (la boîte en dépend) ; copie le WebP dans public/<siecle>/diaporamas/<slug>/ (001-fond.webp,
004-b-fond.webp) ; écrit `image.fond` { fichier, largeur, hauteur, boite, flou, modele, genere_le } ;
consigne la recette dans src/data/diaporamas/<siecle>/generation/<slug>-fond.json. Idempotent. Les cibles
sont des numéros ACTUELS : `86`, `34b`. `renumeroter.py` suit fichiers et champs ; `verifier.py`
contrôle la famille « fond (spec 17) ».
"""
from __future__ import annotations

import argparse, datetime, html, json, math, re, shutil, subprocess, sys, time, zipfile, zlib
from pathlib import Path

import commun as c
from generation import sessions_colab, une_seule_session   # règle « une seule session Colab à la fois » (aussi pour vignettes.py)

MODELE = 'black-forest-labs/FLUX.2-klein-4B'
H_IMAGE = 576            # hauteur de l'image dans la toile (px)
HAUT = 1.5               # hauteur du fond fini, en hauteurs d'image (25 % au-dessus et au-dessous : passe 2)
BANDE_FLOU = 9           # px : lissage des bandes de secours (× 3)
BANDE_SOMBRE = 0.5       # luminosité au bord extérieur des bandes de secours
JONCTION = 40            # px : fondu de la jonction entre l'image élargie et les bandes d'un décor
DECALAGE_GRAINE_2 = 31   # la passe 2 ne reprend pas la graine de la passe 1
LARGE = 2.4              # largeur minimale de la toile, en hauteurs d'image
LARGEUR_FAIBLE = 1024    # largeur du fichier d'un fond en flou faible (indiscernable de 1392 px à 0,25 % sur une scène de 2560 px)
LARGEUR_FORT = 640       # largeur du fichier d'un fond montré en flou fort
FLOU = {'faible': 0.25, 'fort': 2.5}   # % de la largeur de la scène (FOND_FLOU_* du lecteur)
LUMIERE = 0.8            # FOND_LUMIERE du lecteur
REMOTE = '/content/fond'   # racine distante ; un sous-dossier par période (`distant`) : une session sert plusieurs périodes
SUFFIXE = '-fond.webp'
METHODE = ('Deux passes de FLUX.2 klein 4B. Passe 1 : la zone utile au centre d\'une toile préremplie d\'un flou de la même image, le modèle prolonge les côtés ; '
           'sortie accordée en couleur sur l\'original et raccordée à ses bords (sans IA), original recollé. Passe 2 (« haut_bas » : « modele », décors) : '
           'l\'image élargie au milieu d\'une toile plus haute, le modèle prolonge le haut et le bas d\'après une consigne qui les nomme ; bandes accordées '
           'et jonction fondue (sans IA). « haut_bas » : « papier » (genres papier et uni) : bandes de papier continues sans modèle (miroir des côtés). '
           '« haut_bas » : « etire » : bord étiré et assombri sans modèle (premier procédé, gardé par exception).')
TOLERANCE_UTILE = 1e-6

STYLES = (
    (('huile', 'peinture', 'aquarelle', 'gouache'), 'early 19th-century oil painting, same palette, same brushwork, same light'),
    (('lithographie',), '19th-century lithograph on paper, same soft crayon grain, same paper tone'),
    (('gravure', 'eau-forte', 'manière noire', 'estampe', 'burin', 'dessin'), '19th-century engraving, same fine hatching, same ink and paper tone'),
    (('daguerréotype', 'héliographie', 'photographie'), 'early photograph, same tone, same grain'),
)
STYLE_DEFAUT = 'same medium, same colours, same texture as the picture'
QUOI = {
    # « decor » : le lot doit dire quoi prolonger (`plus`) ; une liste générique (ciel, eau, végétation…)
    # fait peindre au modèle un paysage sans rapport autour de l'image (essai du 2026-10-12).
    'decor': 'the same setting that is visible at the very edges of the picture, in the same place, the same light and the same colours',
    'uni': ('the plain background behind the subject: one even, flat tone of the same colour as the background at the edges of the picture, '
            'with the same soft gradient and texture, sharp and not blurred, and nothing else'),
    'papier': 'the plain empty sheet of paper around the drawing: the same paper tone and grain, left blank',
}
INTERDITS = ('no people, no figures, no faces, no bodies, no animals, no text, no letters, no signature, no stamp, '
             'no frame, no border, no drop shadow, no picture within a picture, no window, no modern elements')
DESSUS_DESSOUS = {   # passe 2, genres sans décor : ce qu'il y a au-dessus et au-dessous
    'papier': ('the same blank sheet of paper, in the same tone and grain, with nothing on it',) * 2,
    'uni': ('the same plain background, in the same even tone, with nothing on it',) * 2,
}
PAPIER = ('lithographie', 'gravure', 'eau-forte', 'estampe', 'dessin', 'manuscrit', 'placard', 'imprimé')
# Toile grise (2026-10-18, bilan de la période 06) : sur les décors sombres ou photographiques, le
# modèle laisse souvent le préremplissage flou tel quel (10 décors sur 37 dans la 06, tous réussis
# une fois refaits sur une toile grise unie). Par défaut, ces décors partent donc sur une toile grise ;
# `"toile": "grise" | "floue"` dans lot.json force le choix (les deux passes suivent la même toile).
GRIS_TOILE = (128, 128, 128)
SOMBRE = 90              # luminance moyenne (0-255) des bandes latérales de la zone utile sous laquelle un décor est « sombre »
BANDE_SOMBRE = 0.08      # largeur de ces bandes (fraction de la zone utile)
PHOTO = ('photographi', 'albumin', 'daguerréotype', 'collodion', 'ferrotype')


def dossier(slug: str) -> Path:
    d = c.CACHE / 'fonds' / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def images_entieres(d: dict) -> list[dict]:
    """Images montrées en entier, dans l'ordre : image de la diapositive, puis ses plans et sa galerie.
    {'cle' (86, 34b), 'nom' (086, 034-b : le nom du fichier servi), 'image', 'n'}."""
    sortie = []
    for x in d['diapositives']:
        serie = [(str(x['n']), x.get('image'))]
        for k, p in enumerate(x.get('plans') or []):
            lettre = c.LETTRES_PLANS[k] if k < len(c.LETTRES_PLANS) else chr(ord('b') + k)
            serie.append((f"{x['n']}{lettre}", p.get('image') if isinstance(p, dict) else None))
        s = x.get('suite') or {}
        for k, p in enumerate((s.get('galerie') or s.get('images') or []) if isinstance(s, dict) else []):
            serie.append((f"{x['n']}g{k + 1}", p.get('image') if isinstance(p, dict) and isinstance(p.get('image'), dict) else p))
        for cle, im in serie:
            if isinstance(im, dict) and im.get('entier') and im.get('fichier'):
                sortie.append({'cle': cle, 'nom': Path(im['fichier']).stem, 'image': im, 'n': x['n']})
    return sortie


def zone_utile(slug: str, im: dict):
    from PIL import Image
    src = Image.open(c.PUBLIC / slug / im['fichier']).convert('RGB')
    u = im.get('utile') or [0, 0, 1, 1]
    return src.crop((round(u[0] * src.width), round(u[1] * src.height), round(u[2] * src.width), round(u[3] * src.height)))


def genre_de(im: dict) -> str:
    t = (im.get('technique') or '').lower()
    if 'huile' in t:
        return 'decor'
    return 'papier' if any(m in t for m in PAPIER) else 'uni'


def style_de(im: dict) -> str:
    t = (im.get('technique') or '').lower()
    for mots, style in STYLES:
        if any(m in t for m in mots):
            return style
    return STYLE_DEFAUT


def toile_de(regle: dict, genre: str, im: dict, zone) -> str:
    """« grise » ou « floue » : le lot décide (`toile`), sinon grise pour un décor photographique
    (technique) ou sombre (bords latéraux de la zone utile sous SOMBRE)."""
    if regle.get('toile') in ('grise', 'floue'):
        return regle['toile']
    if genre != 'decor':
        return 'floue'
    if any(m in (im.get('technique') or '').lower() for m in PHOTO):
        return 'grise'
    from PIL import ImageStat
    g = zone.convert('L')
    b = max(4, round(g.width * BANDE_SOMBRE))
    lum = (ImageStat.Stat(g.crop((0, 0, b, g.height))).mean[0] + ImageStat.Stat(g.crop((g.width - b, 0, g.width, g.height))).mean[0]) / 2
    return 'grise' if lum < SOMBRE else 'floue'


def toile(zone):
    """Dimensions de la toile et boîte de l'image [x0, y0, w, h] (px)."""
    h = H_IMAGE
    w = round(h * zone.width / zone.height)
    Hc = h    # le modèle ne prolonge que les côtés : avec une marge en haut et en bas, il peint une pièce où le tableau est posé
    Wc = max(math.ceil(h * LARGE / 16) * 16, math.ceil(w * 1.2 / 16) * 16)
    return Wc, Hc, [(Wc - w) // 2, (Hc - h) // 2, w, h]


def preparer(slug: str) -> None:
    from PIL import Image, ImageFilter
    _, d = c.lire(slug)
    dest = dossier(slug)
    for sous in ('in', 'orig'):
        (dest / sous).mkdir(exist_ok=True)
    lot = json.loads((dest / 'lot.json').read_text(encoding='utf-8')) if (dest / 'lot.json').exists() else {}
    elements = []
    for e in images_entieres(d):
        im, nom = e['image'], e['nom']
        zone = zone_utile(slug, im)
        orig = zone if zone.height <= 1200 else zone.resize((round(zone.width * 1200 / zone.height), 1200), Image.LANCZOS)
        orig.save(dest / 'orig' / f'{nom}.webp', quality=92, method=5)
        Wc, Hc, (x0, y0, w, h) = toile(zone)
        petit = zone.resize((w, h), Image.LANCZOS)
        regle = lot.get(nom) or {}
        genre = regle.get('genre') or genre_de(im)
        sorte = toile_de(regle, genre, im, zone)
        if sorte == 'grise':
            g = Image.new('RGB', (Wc, Hc), GRIS_TOILE)
        else:
            k = max(Wc / zone.width, Hc / zone.height) * 1.08
            g = zone.resize((round(zone.width * k), round(zone.height * k)), Image.BILINEAR)
            gx, gy = (g.width - Wc) // 2, (g.height - Hc) // 2
            g = g.crop((gx, gy, gx + Wc, gy + Hc)).filter(ImageFilter.GaussianBlur(28))
        g.paste(petit, (x0, y0))
        g.save(dest / 'in' / f'{nom}.jpg', quality=95, subsampling=0)
        if sorte == 'grise':   # consigne des tirages refaits sur toile grise de la période 06
            consigne = (f'Extend this picture to fill the whole wide frame: replace the flat gray areas on the left and right with a sharp, '
                        f'detailed, seamless continuation of {QUOI[genre]}. {regle.get("plus", "").strip()} Keep the central picture exactly '
                        f'unchanged, at the same place and size. Style: {style_de(im)}. The added areas contain only background, in sharp '
                        f'focus, not blurred; {INTERDITS}.')
        else:
            consigne = (f'Extend this picture to fill the whole wide frame: replace the blurred areas around it with a seamless '
                        f'continuation of {QUOI[genre]}. {regle.get("plus", "").strip()} Keep the central picture exactly unchanged, '
                        f'at the same place and size. Style: {style_de(im)}. The added areas contain only background; {INTERDITS}.')
        elements.append(dict(nom=nom, cle=e['cle'], n=e['n'], commons=im.get('commons'), titre=im.get('titre'), auteur=im.get('auteur'),
                             date=im.get('date'), technique=im.get('technique'), utile=im.get('utile') or [0, 0, 1, 1],
                             zone=[zone.width, zone.height], toile=[Wc, Hc], boite=[x0, y0, w, h], genre=genre, fond_toile=sorte,
                             dessus=regle.get('dessus'), dessous=regle.get('dessous'), bandes=regle.get('bandes'), teinte=regle.get('teinte'),
                             consigne=' '.join(consigne.split()), graine=zlib.crc32((im.get('commons') or nom).encode()) % 100000))
    (dest / 'manifeste.json').write_text(json.dumps(dict(slug=slug, modele=MODELE, elements=elements), ensure_ascii=False, indent=1), encoding='utf-8')
    with zipfile.ZipFile(dest / 'kit.zip', 'w', zipfile.ZIP_STORED) as z:
        z.write(dest / 'manifeste.json', 'manifeste.json')
        for el in elements:
            z.write(dest / 'in' / f"{el['nom']}.jpg", f"{el['nom']}.jpg")
    import collections
    sans = [e['nom'] for e in elements if e['genre'] == 'decor' and not (e['dessus'] and e['dessous'])]
    if sans:
        print(f"  à compléter dans lot.json avant la passe 2 (« dessus », « dessous » d'un décor) : {', '.join(sans)}")
    print(f"{len(elements)} images entières ({sum(1 for e in elements if e['cle'].isdigit())} images de diapositive, "
          f"{sum(1 for e in elements if not e['cle'].isdigit())} plans ou galeries) ; genres {dict(collections.Counter(e['genre'] for e in elements))} ; "
          f"{sum(1 for e in elements if e['fond_toile'] == 'grise')} sur toile grise ; "
          f"kit {(dest / 'kit.zip').stat().st_size / 1e6:.1f} Mo")


def manifeste(slug: str) -> dict:
    f = dossier(slug) / 'manifeste.json'
    if not f.exists():
        raise SystemExit(f'Manifeste absent : lancer « preparer {slug} » d\'abord')
    return json.loads(f.read_text(encoding='utf-8'))


# --- Colab ------------------------------------------------------------------------------

def distant(slug: str) -> str:
    """Dossier de la période sur la session : sans lui, deux périodes calculées dans la même session
    mêlaient leurs toiles et leurs sorties (mêmes noms : 001.jpg, 001-g1.jpg)."""
    return f'{REMOTE}/{dossier(slug).name}'


def colab(*args: str, timeout: float = 300, code: str | None = None, essais: int = 3, strict: bool = True) -> str:
    """Appel de la CLI colab (tué et refait s'il ne répond pas : blocage connu de `colab exec`)."""
    exe = str(Path.home() / '.local/bin/colab')
    for _ in range(essais):
        try:
            r = subprocess.run([exe, *args], capture_output=True, text=True, timeout=timeout, input=code)
            break
        except subprocess.TimeoutExpired:
            print(f'  (colab {args[0]} sans réponse : nouvel essai)', flush=True)
    else:
        if strict:
            raise SystemExit(f'colab {" ".join(args[:2])} : sans réponse')
        return ''
    if r.returncode != 0 and strict:
        raise SystemExit(f'colab {" ".join(args[:2])} : {r.stderr.strip() or r.stdout.strip()}')
    return '\n'.join(l for l in r.stdout.splitlines() if not l.startswith('[colab]'))


def rapatrier(slug: str, session: str, passe: int = 1) -> int:
    """Rapatrie les sorties absentes du disque (une archive), sans rien arrêter."""
    dest = dossier(slug)
    bruts = dest / ('bruts' if passe == 1 else 'bruts2')
    R = distant(slug)
    sortie = f"{R}/out{'' if passe == 1 else '2'}"
    bruts.mkdir(exist_ok=True)
    deja = sorted(f.name for f in bruts.glob('*.jpg'))
    code = (f'import zipfile, pathlib, json\ndeja = set(json.loads({json.dumps(json.dumps(deja))}))\n'
            f'fs = [f for f in sorted(pathlib.Path("{sortie}").iterdir()) if f.suffix in (".jpg", ".jsonl", ".txt") and f.name not in deja]\n'
            f'z = zipfile.ZipFile("{R}/sorties.zip", "w", zipfile.ZIP_STORED)\n[z.write(f, f.name) for f in fs]\nz.close(); print(len(fs))')
    print('à rapatrier :', colab('exec', '-s', session, '--timeout', '60', timeout=90, code=code).strip(), 'fichiers')
    colab('download', '-s', session, f'{R}/sorties.zip', str(dest / 'sorties.zip'), timeout=900)
    with zipfile.ZipFile(dest / 'sorties.zip') as z:
        z.extractall(bruts)
    n = len(list(bruts.glob('*.jpg')))
    print(f'{n} sorties dans {bruts.relative_to(c.RACINE)}')
    return n


def suivre(slug: str, session: str, lignes: int = 6, passe: int = 1) -> str:
    code = (f'import os\np = "{distant(slug)}/out{"" if passe == 1 else "2"}/log.txt"\nt = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""\n'
            f'L = [l for l in t.splitlines() if l.strip() and "━" not in l and "it/s]" not in l and "s/it]" not in l and "Fetching" not in l and "Downloading" not in l]\n'
            f'print(chr(10).join(l[:200] for l in L[-{lignes}:]))')
    return colab('exec', '-s', session, '--timeout', '30', timeout=45, code=code, strict=False)


def lancer(slug: str, gpu: str, session: str, graines: str, seulement: str, reprendre: bool, garder: bool, sans_suivi: bool,
           renvoyer_kit: bool = False, passe: int = 1) -> None:
    """Passe 1 : les côtés (kit.zip). Passe 2 : le haut et le bas des décors (kit2.zip, écrit ici d'après
    les tirages retenus de la passe 1 ; `--reprendre` pour la faire dans la session de la passe 1)."""
    dest = dossier(slug)
    manifeste(slug)
    s = '' if passe == 1 else '2'
    R = distant(slug)
    if passe == 2:
        preparer2(slug)
        renvoyer_kit = True
    if not reprendre:
        une_seule_session(session)
        print(f'session « {session} » ({gpu})…', flush=True)
        colab('new', '-s', session, '--gpu', gpu, timeout=600)
    try:
        # Premier exec : le noyau d'une session neuve peut répondre 503 (pas prêt, 2026-10-14) : on réessaie.
        for essai in range(4):
            try:
                colab('exec', '-s', session, '--timeout', '60', timeout=90, code=f'import os; os.makedirs("{R}/in{s}", exist_ok=True); os.makedirs("{R}/out{s}", exist_ok=True)')
                break
            except SystemExit as e:
                if essai == 3:
                    raise
                print(f'  (premier exec refusé : {str(e)[:120]} ; nouvel essai dans 30 s)', flush=True)
                time.sleep(30)
        if not reprendre or renvoyer_kit:
            colab('upload', '-s', session, str(dest / f'kit{s}.zip'), f'{R}/kit{s}.zip', timeout=900)
            colab('exec', '-s', session, '--timeout', '120', timeout=150, code=f'import zipfile; zipfile.ZipFile("{R}/kit{s}.zip").extractall("{R}/in{s}")')
        colab('upload', '-s', session, str(c.RACINE / 'scripts/colab/fond.py'), f'{R}/fond.py', timeout=300)
        env = f'GRAINES={graines} SEULEMENT={seulement} ENTREE={R}/in{s} SORTIE={R}/out{s}'
        colab('exec', '-s', session, '--timeout', '60', timeout=90, code=(
            f'import subprocess; subprocess.Popen("nohup env {env} python3 {R}/fond.py > {R}/out{s}/log.txt 2>&1 &", shell=True); print("lancé")'))
        print('calcul lancé', flush=True)
        if sans_suivi:
            print(f'sans suivi : « rapatrier {slug} » puis « arreter {slug} » à la main (session {session})')
            return
        debut = time.time()
        dernier_rapatriement = debut
        perdue = False
        while time.time() - debut < 3 * 3600:
            time.sleep(60)
            fin = suivre(slug, session, 3, passe).splitlines()
            if fin:
                print(' ', fin[-1], flush=True)
            else:
                # Journal illisible : la session a-t-elle disparu (2026-10-14 : deux sessions L4 perdues,
                # suivi resté trois heures sur une chaîne vide) ?
                noms = sessions_colab()
                if noms is not None and session not in noms:
                    print(f'session « {session} » absente de colab sessions : perdue ; suivi arrêté '
                          f'(sorties déjà rapatriées gardées ; relancer avec --seulement les images manquantes)', flush=True)
                    perdue = True
                    break
            if any(l.endswith(' FIN') or ' ERREUR' in l for l in fin):
                break
            # Rapatriement au fil de l'eau (toutes les 10 min) : une session perdue n'emporte que le reste.
            if time.time() - dernier_rapatriement > 600:
                try:
                    rapatrier(slug, session, passe)
                except SystemExit as e:
                    print(f'  (rapatriement intermédiaire impossible : {str(e)[:120]})', flush=True)
                dernier_rapatriement = time.time()
        if not perdue:
            rapatrier(slug, session, passe)
    finally:
        if not garder and not sans_suivi:
            arreter(session)


def arreter(session: str) -> None:
    print(colab('stop', '-s', session, timeout=300, strict=False))
    reste = subprocess.run([str(Path.home() / '.local/bin/colab'), 'sessions'], capture_output=True, text=True, timeout=120).stdout
    print(f'session « {session} » ' + ('ENCORE LÀ' if f'[{session}]' in reste else 'arrêtée et absente de colab sessions'))


# --- Fonds finis, relecture, planche -----------------------------------------------------

def accorder(g, petit, boite):
    """Accorde la sortie du modèle sur l'original d'après leur partie commune (sans IA)."""
    import numpy as np
    from PIL import Image
    x0, y0, w, h = boite
    a = np.asarray(g, dtype=np.float32)
    ca = a[y0 + h // 10:y0 + h - h // 10, x0 + w // 10:x0 + w - w // 10].reshape(-1, 3)
    cb = np.asarray(petit, dtype=np.float32)[h // 10:h - h // 10, w // 10:w - w // 10].reshape(-1, 3)
    gain = np.clip(cb.std(0) / np.maximum(ca.std(0), 1e-3), 0.7, 1.4)
    return Image.fromarray(np.clip((a - ca.mean(0)) * gain + cb.mean(0) + 0.5, 0, 255).astype(np.uint8))


def raccorder(g, petit, boite, genre: str, teinte: str | None = None):
    """Accorde chaque côté du prolongement sur le bord de l'original qu'il touche (sans IA) : écart
    de teinte entre la bande de bord de l'image et la bande voisine du prolongement, ajouté au
    prolongement. Fond uni ou papier : un seul écart par côté, sur toute sa largeur. Décor : un écart
    par ligne, lissé verticalement, borné, qui s'efface en s'éloignant de l'image.
    `teinte` (lot, genres uni et papier) : la même teinte cible des deux côtés, quand les deux bords de
    l'image ne disent pas la teinte du papier (bord droit pris dans des hachures, cadre doré d'un
    ovale) : « gauche » ou « droite » (le bord de ce côté fait foi), « coins » (les quatre coins)."""
    import numpy as np
    from PIL import Image
    x0, y0, w, h = boite
    a = np.asarray(g, dtype=np.float32).copy()
    o = np.asarray(petit, dtype=np.float32)
    e = max(4, w // 30)
    cible = None
    if teinte and genre in ('uni', 'papier'):
        k = max(8, min(w, h) // 12)
        zones = {'gauche': [o[:, :e]], 'droite': [o[:, -e:]], 'coins': [o[:k, :k], o[:k, -k:], o[-k:, :k], o[-k:, -k:]]}[teinte]
        cible = np.median(np.concatenate([z.reshape(-1, 3) for z in zones]), 0)
    for gauche in (True, False):
        cote = slice(0, x0) if gauche else slice(x0 + w, a.shape[1])
        if (cote.stop - cote.start) < e:
            continue
        bord_o = o[:, :e] if gauche else o[:, -e:]
        bord_g = a[y0:y0 + h, x0 - e:x0] if gauche else a[y0:y0 + h, x0 + w:x0 + w + e]
        if genre in ('uni', 'papier'):
            a[:, cote] += (np.median(bord_o.reshape(-1, 3), 0) if cible is None else cible) - np.median(bord_g.reshape(-1, 3), 0)
            continue
        d = bord_o.mean(1) - bord_g.mean(1)                                   # (h, 3) : écart par ligne
        s = max(3, h // 8)
        noyau = np.exp(-0.5 * (np.arange(-3 * s, 3 * s + 1) / s) ** 2); noyau /= noyau.sum()
        d = np.stack([np.convolve(np.pad(d[:, k], 3 * s, mode='edge'), noyau, mode='valid') for k in range(3)], 1)
        d = np.clip(d, -45, 45)
        dist = (x0 - 1 - np.arange(cote.start, cote.stop)) if gauche else (np.arange(cote.start, cote.stop) - (x0 + w))
        poids = 0.25 + 0.75 * np.exp(-dist / (0.5 * h))
        a[y0:y0 + h, cote] += d[:, None, :] * poids[None, :, None]
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))


def elargie(slug: str, el: dict, tirage: int):
    """Image élargie par la passe 1 (côtés) : sortie accordée, raccordée, original recollé. None si
    le tirage manque."""
    from PIL import Image
    f = dossier(slug) / 'bruts' / f"{el['nom']}-g{tirage}.jpg"
    if not f.exists():
        return None
    x0, y0, w, h = el['boite']
    petit = Image.open(dossier(slug) / 'in' / f"{el['nom']}.jpg").convert('RGB').crop((x0, y0, x0 + w, y0 + h))
    g = Image.open(f).convert('RGB')
    if g.size != tuple(el['toile']):
        g = g.resize(tuple(el['toile']), Image.LANCZOS)
    g = raccorder(accorder(g, petit, el['boite']), petit, el['boite'], el.get('genre', 'decor'), el.get('teinte'))
    g.paste(petit, (x0, y0))
    return g


def mode_bandes(el: dict) -> str:
    """Comment sont faits le haut et le bas : « modele » (passe 2) pour un décor, « papier » (bandes
    continues sans modèle) pour les genres papier et uni ; `bandes` du lot l'emporte (un papier dont
    les côtés portent un sol dessiné doit passer par le modèle : le miroir le refléterait)."""
    return el.get('bandes') or ('modele' if el.get('genre', 'decor') == 'decor' else 'papier')    # ou « etire » : bandes de secours


def fond_net(slug: str, el: dict, tirage: int, tirage2: int = 1):
    """Fond fini à pleine taille : image élargie (passe 1) au centre, haut et bas par la passe 2 du
    modèle (décor), par des bandes de papier continues (papier, uni), ou, si la passe 2 manque, par
    des bandes de secours étirées. Rend (image, hauteur d'une bande en px, mode) ; (None, 0, '') si
    le tirage de la passe 1 manque."""
    from PIL import Image
    g = elargie(slug, el, tirage)
    if g is None:
        return None, 0, ''
    m = marge_bande(g.height)
    mode = mode_bandes(el)
    if mode == 'papier':
        return bandes_papier(g, m, el['boite']), m, 'papier'
    if mode == 'etire':
        return etendre(g), m, 'etire'
    f = dossier(slug) / 'bruts2' / f"{el['nom']}-g{tirage2}.jpg"
    if not f.exists():
        return etendre(g), m, 'etire'
    s = Image.open(f).convert('RGB')
    if s.size != (g.width, g.height + 2 * m):
        s = s.resize((g.width, g.height + 2 * m), Image.LANCZOS)
    return accorder_bandes(s, g, m), m, 'modele'


def marge_bande(h: int) -> int:
    return round(h * (HAUT - 1) / 2)


def etendre(g):
    """Ajoute au-dessus et au-dessous une bande faite du reflet flouté et assombri du fond (sans IA) :
    elle ne sert que sous les bandeaux du plein écran et quand l'image est plus large que la scène."""
    import numpy as np
    from PIL import Image, ImageFilter, ImageOps
    m = marge_bande(g.height)
    if m <= 0:
        return g
    sortie = Image.new('RGB', (g.width, g.height + 2 * m))
    sortie.paste(g, (0, m))
    rampe = np.linspace(BANDE_SOMBRE, 1.0, m, dtype=np.float32)[:, None, None]      # du bord extérieur vers l'image
    for haut in (True, False):
        b = ImageOps.flip(g.crop((0, 0, g.width, m)) if haut else g.crop((0, g.height - m, g.width, g.height))).filter(ImageFilter.GaussianBlur(BANDE_FLOU))
        a = np.asarray(b, dtype=np.float32) * (rampe if haut else rampe[::-1])
        sortie.paste(Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)), (0, 0 if haut else m + g.height))
    return sortie


def _lisse(v, s):
    import numpy as np
    noyau = np.exp(-0.5 * (np.arange(-3 * s, 3 * s + 1) / s) ** 2); noyau /= noyau.sum()
    return np.stack([np.convolve(np.pad(v[:, k], 3 * s, mode='edge'), noyau, mode='valid') for k in range(v.shape[1])], 1)

def bandes_papier(g, m, boite):
    import numpy as np
    from PIL import Image, ImageFilter
    """Papier ou fond uni : bandes sans modèle, continues avec les côtés. Au-dessus et au-dessous
    des côtés, le miroir de leurs propres lignes (continuité exacte à la jonction) ; au-dessus et
    au-dessous de l'image, la teinte interpolée entre les deux côtés, avec le grain du côté gauche."""
    b = np.asarray(g, dtype=np.float32); h, W = b.shape[:2]; x0, _, w, _ = boite
    r = np.zeros((h + 2 * m, W, 3), np.float32); r[m:m + h] = b
    for haut in (True, False):
        src = b[:m] if haut else b[-m:][::-1]                       # lignes de bord, la jonction en ligne 0
        bande = src.copy()
        e = 24
        gche, drte = src[:, max(0, x0 - e):x0].mean(1), src[:, x0 + w:x0 + w + e].mean(1)      # (m, 3)
        a = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
        centre = gche[:, None, :] * (1 - a) + drte[:, None, :] * a
        # grain : hautes fréquences du côté gauche, répétées en miroir sur la largeur de l'image
        cote = src[:, :x0]
        if cote.shape[1] >= 16:
            flou = np.asarray(Image.fromarray(np.clip(cote, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), dtype=np.float32)
            grain = cote - flou
            pave = np.concatenate([grain, grain[:, ::-1]], 1)
            centre = centre + np.tile(pave, (1, w // pave.shape[1] + 2, 1))[:, :w]
        bande[:, x0:x0 + w] = centre
        # adoucit les raccords (bords verticaux de l'image, teintes des deux côtés) : version floutée
        # de la bande, de plus en plus présente en s'éloignant de la jonction (qui reste exacte)
        douce = np.asarray(Image.fromarray(np.clip(bande, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(22)), dtype=np.float32)
        k = np.clip(np.arange(m, dtype=np.float32) / 36, 0, 1)[:, None, None]        # src est en miroir : ligne 0 = jonction
        bande = bande * (1 - k) + (douce + (bande - np.asarray(Image.fromarray(np.clip(bande, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)), dtype=np.float32))) * k
        if haut: r[:m] = bande[::-1]
        else: r[m + h:] = bande
    sortie = Image.fromarray(np.clip(r + 0.5, 0, 255).astype(np.uint8))
    sortie.paste(g, (0, m))
    return sortie

def accorder_bandes(sortie, g, m):
    import numpy as np
    from PIL import Image
    """Décor : accord global sur la partie commune (la bande centrale = passe 1), raccord de teinte
    du haut et du bas sur les lignes de bord de la passe 1 (écart par colonne, peu lissé, qui
    s'efface en s'éloignant), puis fondu de la jonction sur `F` px avec le miroir des lignes de la
    passe 1 : plus de ligne dure à la jonction. """
    a = np.asarray(sortie, dtype=np.float32); b = np.asarray(g, dtype=np.float32); h = g.height
    ca = a[m + h // 10:m + h - h // 10].reshape(-1, 3); cb = b[h // 10:h - h // 10].reshape(-1, 3)
    gain = np.clip(cb.std(0) / np.maximum(ca.std(0), 1e-3), 0.7, 1.4)
    a = (a - ca.mean(0)) * gain + cb.mean(0)
    e, F = 10, JONCTION
    for haut in (True, False):
        bo = b[:e].mean(0) if haut else b[-e:].mean(0)
        bg = a[m - e:m].mean(0) if haut else a[m + h:m + h + e].mean(0)
        d = np.clip(_lisse(bo - bg, 14), -60, 60)
        dist = (m - 1 - np.arange(0, m)) if haut else np.arange(0, a.shape[0] - m - h)
        poids = (0.3 + 0.7 * np.exp(-dist / (0.6 * h)))[:, None, None]
        miroir = b[:F][::-1] if haut else b[-F:][::-1]              # lignes de la passe 1, en miroir
        if haut:
            a[:m] += d[None] * poids
            k = np.linspace(0, 1, F, dtype=np.float32)[:, None, None] ** 1.5      # 0 loin de la jonction → 1 à la jonction
            a[m - F:m] = a[m - F:m] * (1 - k) + miroir * k
        else:
            a[m + h:] += d[None] * poids
            k = np.linspace(1, 0, F, dtype=np.float32)[:, None, None] ** 1.5
            a[m + h:m + h + F] = a[m + h:m + h + F] * (1 - k) + miroir * k
    r = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))
    r.paste(g, (0, m))
    return r


def preparer2(slug: str) -> None:
    """Kit de la passe 2 : pour chaque décor, l'image élargie (tirage retenu de la passe 1,
    `constats.json`) au milieu d'une toile plus haute, le haut et le bas préremplis d'un flou, et
    une consigne qui nomme ce qu'il y a au-dessus et au-dessous (`dessus`, `dessous` du lot)."""
    from PIL import ImageFilter, Image
    dest = dossier(slug)
    (dest / 'in2').mkdir(exist_ok=True)
    constats = json.loads((dest / 'constats.json').read_text(encoding='utf-8')) if (dest / 'constats.json').exists() else {}
    els, manque = [], []
    for el in manifeste(slug)['elements']:
        if mode_bandes(el) != 'modele':
            continue
        dessus, dessous = (el.get('dessus'), el.get('dessous')) if el.get('dessus') and el.get('dessous') else DESSUS_DESSOUS.get(el['genre'], (None, None))
        g = elargie(slug, el, int((constats.get(el['nom']) or {}).get('tirage', 1)))
        if g is None or not dessus:
            manque.append(el['nom'] + (' (passe 1 absente)' if g is None else ' (dessus, dessous)'))
            continue
        m = marge_bande(g.height)
        Hc = g.height + 2 * m
        k = Hc / g.height * 1.04
        grise = el.get('fond_toile') == 'grise'   # même toile qu'en passe 1 (bandes restées floues : 22, 30, 59, 73b, 131 de la 06)
        if grise:
            pre = Image.new('RGB', (g.width, Hc), GRIS_TOILE)
        else:
            pre = g.resize((round(g.width * k), round(g.height * k)), Image.BILINEAR)
            px, py = (pre.width - g.width) // 2, (pre.height - Hc) // 2
            pre = pre.crop((px, py, px + g.width, py + Hc)).filter(ImageFilter.GaussianBlur(24))
        pre.paste(g, (0, m))
        pre.save(dest / 'in2' / f"{el['nom']}.jpg", quality=95, subsampling=0)
        consigne = (f'Extend this wide picture upward and downward to fill the whole frame: replace the {"flat gray" if grise else "blurred"} bands at the top and at the bottom with a sharp, '
                    f'seamless continuation of the same scene. Above the picture: {dessus}. Below the picture: {dessous}. Keep the wide central picture exactly '
                    f'unchanged, at the same place and size. Style: {style_de(el)}. The added bands contain only background, not blurred; {INTERDITS}.')
        els.append(dict(nom=el['nom'], marge=m, toile=[g.width, Hc], consigne=consigne, graine=el['graine'] + DECALAGE_GRAINE_2))
    (dest / 'manifeste2.json').write_text(json.dumps(dict(slug=slug, modele=MODELE, elements=els), ensure_ascii=False, indent=1), encoding='utf-8')
    with zipfile.ZipFile(dest / 'kit2.zip', 'w', zipfile.ZIP_STORED) as z:
        z.write(dest / 'manifeste2.json', 'manifeste.json')
        for e in els:
            z.write(dest / 'in2' / f"{e['nom']}.jpg", f"{e['nom']}.jpg")
    for x in manque:
        print(f'  passe 2 impossible : {x}')
    print(f"passe 2 : {len(els)} toiles (décors) ; kit {(dest / 'kit2.zip').stat().st_size / 1e6:.1f} Mo ; papier et uni : bandes sans modèle")


def lire_constats(slug: str) -> dict:
    f = dossier(slug) / 'constats.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}


def relire(slug: str, tirage: int | None, tirage2: int | None, seulement: list[str]) -> None:
    """Montages de relecture **à l'échelle de génération** (1392 × 864 px, deux fonds par montage) :
    c'est à cette échelle qu'on voit ce que le modèle a dessiné. `tirage`, `tirage2` : tirages des
    passes 1 et 2 à montrer (absents : ceux de constats.json, sinon 1)."""
    from PIL import Image, ImageDraw
    constats = lire_constats(slug)
    nom_dossier = f"relecture-g{tirage or 'c'}-h{tirage2 or 'c'}"
    dest = dossier(slug) / nom_dossier
    dest.mkdir(exist_ok=True)
    els = [e for e in manifeste(slug)['elements'] if not seulement or e['nom'] in seulement]
    for p in range(0, len(els), 2):
        vues = []
        for el in els[p:p + 2]:
            k = constats.get(el['nom']) or {}
            t1, t2 = tirage or int(k.get('tirage', 1)), tirage2 or int(k.get('tirage2', 1))
            g, _, mode = fond_net(slug, el, t1, t2)
            vues.append((f"{el['nom']}  passe 1 tirage {t1}, haut et bas : {mode or 'absent'}{f' tirage {t2}' if mode == 'modele' else ''}  ({el['genre']})", g))
        L = max((g.width for _, g in vues if g is not None), default=1392)
        H = max((g.height for _, g in vues if g is not None), default=864) + 20
        m = Image.new('RGB', (L, H * len(vues)), 'white')
        d = ImageDraw.Draw(m)
        for i, (titre, g) in enumerate(vues):
            if g is not None:
                m.paste(g, (0, i * H + 20))
            d.text((4, i * H + 4), titre.encode('ascii', 'replace').decode(), fill='black')
        f = dest / f"{p // 2 + 1:02d}-{'_'.join(e['nom'] for e in els[p:p + 2])}.jpg"
        m.save(f, quality=90)
    print(f'{len(els)} fonds à relire dans {dest.relative_to(c.RACINE)} (échelle de génération)')


def ko(o: float) -> str:
    return f'{o / 1000:.0f} ko'


def planche(slug: str, largeur: int) -> None:
    from PIL import Image
    dest = dossier(slug)
    M = manifeste(slug)
    constats = lire_constats(slug)
    (dest / 'fonds').mkdir(exist_ok=True)
    M2 = {e['nom']: e for e in json.loads((dest / 'manifeste2.json').read_text(encoding='utf-8'))['elements']} if (dest / 'manifeste2.json').exists() else {}
    D = []
    for el in M['elements']:
        k = constats.get(el['nom']) or {}
        tirage, tirage2, niveau = int(k.get('tirage', 1)), int(k.get('tirage2', 1)), k.get('flou', 'faible')
        g, bande, mode = fond_net(slug, el, tirage, tirage2)
        if g is None:
            print(f"  {el['nom']} : tirage {tirage} absent, image sautée")
            continue
        if mode == 'etire':
            print(f"  {el['nom']} : haut et bas étirés sans IA" + ('' if mode_bandes(el) == 'etire' else f' (passe 2 absente, tirage {tirage2})'))
        L = min(LARGEUR_FORT if niveau == 'fort' else largeur, g.width)
        petit = g.resize((L, round(L * g.height / g.width)), Image.LANCZOS)
        f = dest / 'fonds' / f"{el['nom']}-fond.webp"
        petit.save(f, 'WEBP', quality=78, method=6)
        x0, y0, w, h = el['boite']
        y0 += bande
        Wc, Hc = g.size
        d = dict(nom=el['nom'], cle=el['cle'], commons=el['commons'], titre=el['titre'], auteur=el['auteur'], date=el['date'],
                 technique=el['technique'], genre=el['genre'], haut_bas=mode, fichier=f.name, largeur=petit.width, hauteur=petit.height, octets=f.stat().st_size,
                 boite=[round(x0 / Wc, 5), round(y0 / Hc, 5), round((x0 + w) / Wc, 5), round((y0 + h) / Hc, 5)], aspect=round(w / h, 4),
                 flou=niveau, tirage=tirage, graine=el['graine'] + 1000 * (tirage - 1), invente=k.get('invente', ''), raison=k.get('raison', ''),
                 relu=bool(k), modele=MODELE, utile=el['utile'], consigne=el['consigne'])
        if mode == 'modele':
            d.update(tirage_haut_bas=tirage2, graine_haut_bas=el['graine'] + DECALAGE_GRAINE_2 + 1000 * (tirage2 - 1), consigne_haut_bas=(M2.get(el['nom']) or {}).get('consigne'))
        D.append(d)
    (dest / 'fonds.json').write_text(json.dumps(dict(slug=slug, modele=MODELE, genere_le=datetime.date.today().isoformat(), fonds=D), ensure_ascii=False, indent=1), encoding='utf-8')
    forts = [d for d in D if d['flou'] == 'fort']
    faibles = [d for d in D if d['flou'] != 'fort']

    def tuile(d: dict) -> str:
        b = d['boite']
        bw, bh = b[2] - b[0], b[3] - b[1]
        st = f"left:{-b[0] / bw * 100:.3f}%;top:{-b[1] / bh * 100:.3f}%;width:{100 / bw:.3f}%;height:{100 / bh:.3f}%"
        note = html.escape(d['raison'] or d['invente'] or ('' if d['relu'] else 'non relu'))
        return (f'<figure class="{d["flou"]}" id="f{d["nom"]}"><div class="scene"><div class="pose" style="--a:{d["aspect"]}">'
                f'<img class="fond" src="fonds/{d["fichier"]}" alt="" loading="lazy" style="{st}">'
                f'<img class="oeuvre" src="orig/{d["nom"]}.webp" alt="" loading="lazy"></div></div>'
                f'<figcaption><b>{d["cle"]}</b> {html.escape(d["titre"] or "")} <span class="doux">· {html.escape(d["technique"] or "")} · '
                f'{d["largeur"]} px, {ko(d["octets"])}</span>{"<br>" + note if note else ""}</figcaption></figure>')

    total = sum(d['octets'] for d in D)
    v = lambda x: str(x).replace('.', ',')
    page = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,"><title>Fonds prolongés : {html.escape(slug)} (spec 17)</title>
<style>
:root {{ --fond: #fbfaf7; --texte: #1a1a1a; --doux: #5c5c5c; --filet: #c8c5bd; --faible: {FLOU['faible']}; --fort: {FLOU['fort']}; --sombre: {LUMIERE}; --raccord: 0.3; --A: 1.7778; --k: 0.8; --cy: 44%; }}
* {{ box-sizing: border-box; }}
html {{ background: var(--fond); color: var(--texte); font: 18px/1.5 'EB Garamond', Garamond, 'Iowan Old Style', Palatino, Georgia, serif; }}
body {{ margin: 0 auto; padding: 1.5rem 16px 4rem; max-width: 1560px; }}
h1 {{ font-size: 1.7rem; font-weight: 500; margin: 0 0 .2rem; }} h2 {{ font-size: 1.25rem; font-weight: 500; margin: 2rem 0 .2rem; border-top: 1px solid var(--filet); padding-top: 1rem; }}
p {{ max-width: 62rem; margin: .5rem 0; }} a {{ color: inherit; }}
.sur {{ font-variant: small-caps; letter-spacing: .06em; color: var(--doux); font-size: .9rem; }} .doux {{ color: var(--doux); }}
.grille {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 440px), 1fr)); gap: 1rem .9rem; margin: .8rem 0; }}
figure {{ margin: 0; }} figure.grand {{ grid-column: 1 / -1; }}
figcaption {{ font-size: .85rem; margin-top: .25rem; line-height: 1.35; }}
.scene {{ position: relative; aspect-ratio: var(--A); background: #000; overflow: hidden; container-type: size; cursor: zoom-in; }}
.pose {{ position: absolute; left: 50%; top: var(--cy); height: min(calc(var(--k) * 100cqh), calc(100cqw / var(--a))); aspect-ratio: var(--a); transform: translate(-50%, -50%) scale(var(--zoom, 1)); }}
.fond {{ position: absolute; max-width: none; display: block; }}
.faible .fond {{ filter: blur(calc(var(--faible) * 1cqw)) brightness(var(--sombre)); }}
.fort .fond {{ filter: blur(calc(var(--fort) * 1cqw)) brightness(var(--sombre)); }}
body.net .fond {{ filter: none; }}
.oeuvre {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block;
  --r: calc(var(--raccord) * 1cqw);
  -webkit-mask-image: linear-gradient(to right, transparent, #000 var(--r), #000 calc(100% - var(--r)), transparent), linear-gradient(to bottom, transparent, #000 var(--r), #000 calc(100% - var(--r)), transparent);
  -webkit-mask-composite: source-in; mask-image: linear-gradient(to right, transparent, #000 var(--r), #000 calc(100% - var(--r)), transparent), linear-gradient(to bottom, transparent, #000 var(--r), #000 calc(100% - var(--r)), transparent); mask-composite: intersect; }}
body.net .oeuvre {{ -webkit-mask-image: none; mask-image: none; }}
.outils {{ position: sticky; top: 0; z-index: 5; background: var(--fond); border-bottom: 1px solid var(--filet); padding: .4rem 0; display: flex; flex-wrap: wrap; gap: .3rem 1.1rem; align-items: center; font-size: .9rem; }}
.outils label {{ display: inline-flex; gap: .35rem; align-items: center; white-space: nowrap; }} .outils output {{ min-width: 2.8em; font-variant-numeric: tabular-nums; }}
select {{ font: inherit; font-size: .9rem; }} input[type=range] {{ accent-color: #1a1a1a; }}
</style></head>
<body>
<p class="sur">Le siècle en images · spec 17, fonds prolongés · {datetime.date.today().isoformat()}</p>
<h1>Fonds prolongés : {html.escape(slug)}</h1>
<p>{len(D)} images entières ({sum(1 for d in D if d['cle'].isdigit())} images de diapositive, {sum(1 for d in D if not d['cle'].isdigit())} plans). Derrière chaque image d'époque, intacte, le prolongement généré par FLUX.2 klein 4B (Apache 2.0), flouté par le navigateur : <strong>{len(faibles)} en flou faible</strong> ({v(FLOU['faible'])} % de la largeur de la scène) et <strong>{len(forts)} en flou fort</strong> ({v(FLOU['fort'])} %), parce que le fond net montre encore, après plusieurs tirages, un personnage, un texte, un cachet, un anachronisme ou un objet incongru. Poids total des fonds : {total / 1e6:.1f} Mo (moyenne {ko(total / max(1, len(D)))}).</p>
<p class="doux">« Fond net » montre ce que le modèle a dessiné. Cliquer sur une vue l'agrandit. Formes de scène : en plein écran, les bandeaux du lecteur laissent à l'image environ 80 % de la hauteur, un peu au-dessus du centre ; sur téléphone, la scène est presque carrée (approximations de la pose réelle). Rien n'est publié par cette planche. L'image d'époque est ici une copie WebP ; le lecteur emploie le fichier servi.</p>
<div class="outils">
<label><input type="checkbox" id="net"> fond net</label>
<label>Scène <select id="scene"><option value="1.7778,0.8,44%">plein écran 16:9, bandeaux</option><option value="1,0.8,45%">téléphone 1:1</option><option value="2.3,1,50%">fenêtre large 2,3:1</option><option value="1.44,1,50%">fenêtre 1,44:1</option></select></label>
<label>Rapprochement <select id="zoom"><option value="1">image entière</option><option value="1.3">× 1,3</option></select></label>
<label>Flou faible <input type="range" id="faible" min="0" max="1" step="0.05" value="{FLOU['faible']}"><output></output></label>
<label>Flou fort <input type="range" id="fort" min="1" max="5" step="0.1" value="{FLOU['fort']}"><output></output></label>
<label>Luminosité du fond <input type="range" id="sombre" min="0.4" max="1" step="0.02" value="{LUMIERE}"><output></output></label>
<label>Raccord <input type="range" id="raccord" min="0" max="1.5" step="0.05" value="0.3"><output></output></label>
</div>
<h2>Passés en flou fort ({len(forts)})</h2>
<p class="doux">La raison est sous chaque vue ; le fond net la montre.</p>
<div class="grille">{''.join(tuile(d) for d in forts)}</div>
<h2>En flou faible ({len(faibles)})</h2>
<div class="grille">{''.join(tuile(d) for d in faibles)}</div>
<script>
const $ = (s) => document.querySelector(s), R = document.documentElement.style;
for (const id of ['faible', 'fort', 'sombre', 'raccord']) {{
  const el = $('#' + id), maj = () => {{ R.setProperty('--' + id, el.value); el.nextElementSibling.textContent = el.value.replace('.', ',') + (id === 'sombre' ? '' : ' %'); }};
  el.addEventListener('input', maj); maj();
}}
$('#net').addEventListener('change', (e) => document.body.classList.toggle('net', e.target.checked));
$('#scene').addEventListener('change', (e) => {{ const [A, k, cy] = e.target.value.split(','); R.setProperty('--A', A); R.setProperty('--k', k); R.setProperty('--cy', cy); }});
$('#zoom').addEventListener('change', (e) => R.setProperty('--zoom', e.target.value));
document.querySelectorAll('.scene').forEach((s) => s.addEventListener('click', () => s.parentElement.classList.toggle('grand')));
</script>
</body></html>'''
    (dest / 'planche.html').write_text(page, encoding='utf-8')
    modes = {m: sum(1 for d in D if d['haut_bas'] == m) for m in ('modele', 'papier', 'etire')}
    print(f"{len(D)} fonds ({len(faibles)} en flou faible à {largeur} px, {len(forts)} en flou fort à {LARGEUR_FORT} px ; haut et bas : {modes['modele']} par le modèle, "
          f"{modes['papier']} en papier continu, {modes['etire']} étirés sans modèle), {total / 1e6:.1f} Mo ; planche : {(dest / 'planche.html').relative_to(c.RACINE)}")

# --- Intégration à la période -------------------------------------------------------------

def cle(texte: str) -> str:
    """« 34-b », « 034b » → « 34b »."""
    m = re.fullmatch(r'0*(\d+)-?([a-z]\d*)?', texte.strip().lower())
    if not m:
        raise SystemExit(f'cible « {texte} » : attendu un numéro de diapositive (86) ou de plan (34b)')
    return m[1] + (m[2] or '')


def images(d: dict) -> list[dict]:
    """Images d'une période qui peuvent porter un fond (diapositives, plans, galeries) :
    {'cle', 'image', 'n'}, qu'elles soient entières ou non."""
    sortie = []
    for x in d['diapositives']:
        serie = [(str(x['n']), x.get('image'))]
        for k, p in enumerate(x.get('plans') or []):
            lettre = c.LETTRES_PLANS[k] if k < len(c.LETTRES_PLANS) else chr(ord('b') + k)
            serie.append((f"{x['n']}{lettre}", p.get('image') if isinstance(p, dict) else None))
        s = x.get('suite') or {}
        for k, p in enumerate((s.get('galerie') or s.get('images') or []) if isinstance(s, dict) else []):
            serie.append((f"{x['n']}g{k + 1}", p.get('image') if isinstance(p, dict) and isinstance(p.get('image'), dict) else p))
        sortie += [{'cle': k, 'image': im, 'n': x['n'], 'x': x} for k, im in serie if isinstance(im, dict) and im.get('fichier')]
    return sortie


def recettes_f(slug: str) -> Path:
    return c.DONNEES / 'generation' / f'{slug}-fond.json'


def lire_recettes(slug: str) -> dict:
    f = recettes_f(slug)
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {'usage': 'fond', 'images': {}}


def ecrire_recettes(slug: str, r: dict) -> None:
    f = recettes_f(slug)
    if not r['images']:
        f.unlink(missing_ok=True)
        return
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def publier(slug: str, seulement: set[str], sauf: set[str], essai: bool, lot_nom: str = 'fonds.json') -> int:
    from PIL import Image
    f, d = c.lire(slug)
    slug = d['slug']
    dest = dossier(slug)
    if not (dest / lot_nom).exists():
        raise SystemExit(f'{lot_nom} absent : lancer « planche {slug} » d\'abord')
    lot = json.loads((dest / lot_nom).read_text(encoding='utf-8'))
    sources = dest / Path(lot_nom).stem      # fonds.json → fonds/, fonds-v2.json → fonds-v2/
    par_commons: dict[str, list[dict]] = {}
    for e in images(d):
        par_commons.setdefault(e['image'].get('commons'), []).append(e)
    recettes = lire_recettes(slug)
    recettes.update(modele=lot.get('modele') or MODELE,
                    methode=METHODE)
    publies, refus, poids = [], [], 0
    for el in lot['fonds']:
        src = sources / el['fichier']
        nom = f"{el['cle']} ({(el.get('commons') or '?')[:60]})"
        candidats = par_commons.get(el.get('commons'), [])
        if not candidats:
            refus.append(f'{nom} : image absente de la période (commons inconnu)')
            continue
        if not src.is_file():
            refus.append(f'{nom} : fond absent ({el["fichier"]})')
            continue
        with Image.open(src) as im:
            taille, fmt = im.size, im.format
        for e in candidats:
            i = e['image']
            if (seulement and e['cle'] not in seulement) or e['cle'] in sauf:
                continue
            ici = f"{e['cle']:>5}"
            u = i.get('utile') or [0, 0, 1, 1]
            if not i.get('entier'):
                refus.append(f'{ici} : image qui n\'est plus montrée en entier : pas de fond')
            elif max(abs(a - b) for a, b in zip(u, el['utile'])) > TOLERANCE_UTILE:
                refus.append(f"{ici} : zone utile changée depuis la fabrication ({el['utile']} → {u}) : à refaire")
            elif fmt != 'WEBP':
                refus.append(f'{ici} : format {fmt} (WebP attendu)')
            else:
                cible = c.PUBLIC / slug / (Path(i['fichier']).with_suffix('').as_posix() + SUFFIXE)
                if not essai:
                    if not cible.exists() or cible.read_bytes() != src.read_bytes():
                        shutil.copy(src, cible)
                    i['fond'] = {'fichier': cible.relative_to(c.PUBLIC / slug).as_posix(), 'largeur': taille[0], 'hauteur': taille[1],
                                 'boite': el['boite'], 'flou': el['flou'], 'modele': el.get('modele') or MODELE,
                                 'genere_le': lot.get('genere_le') or datetime.date.fromtimestamp(src.stat().st_mtime).isoformat()}
                    recettes['images'][i['commons']] = {k: el[k] for k in ('consigne', 'graine', 'tirage', 'haut_bas', 'consigne_haut_bas', 'graine_haut_bas', 'tirage_haut_bas', 'genre', 'utile', 'flou', 'invente', 'raison') if el.get(k) not in (None, '')}
                poids += src.stat().st_size
                publies.append(e['cle'])
    for r in refus:
        print(f'  REFUS {r}')
    if not essai:
        c.ecrire(f, d)
        ecrire_recettes(slug, recettes)
    forts = sum(1 for el in lot['fonds'] if el['flou'] == 'fort')
    print(f"{len(publies)} fond(s) {'à publier' if essai else 'publié(s)'} dans {slug} ({poids / 1e6:.1f} Mo ; {forts} en flou fort dans le lot), {len(refus)} refus"
          + ('' if essai else f' ; puis : python3 scripts/diaporamas/verifier.py {slug} et npm run build'))
    return 1 if refus else 0


def retirer(slug: str, cibles: set[str], tout: bool) -> int:
    f, d = c.lire(slug)
    slug = d['slug']
    recettes = lire_recettes(slug)
    retires = []
    for e in images(d):
        v = e['image'].get('fond')
        if not v or not (tout or e['cle'] in cibles):
            continue
        (c.PUBLIC / slug / v['fichier']).unlink(missing_ok=True)
        del e['image']['fond']
        retires.append(e['cle'])
    restantes = {e['image'].get('commons') for e in images(d) if e['image'].get('fond')}
    recettes['images'] = {k: v for k, v in recettes['images'].items() if k in restantes}
    c.ecrire(f, d)
    ecrire_recettes(slug, recettes)
    inconnues = sorted(cibles - set(retires))
    print(f"{len(retires)} fond(s) retiré(s) de {slug} : {', '.join(retires) or 'aucun'}" + (f" ; sans fond : {', '.join(inconnues)}" if inconnues else ''))
    return 0


def lister(slug: str) -> int:
    _, d = c.lire(slug)
    poids = n = forts = 0
    for e in images(d):
        v = e['image'].get('fond')
        if not v:
            continue
        g = c.PUBLIC / d['slug'] / v['fichier']
        ko = g.stat().st_size / 1e3 if g.exists() else 0
        poids += ko
        n += 1
        forts += v.get('flou') == 'fort'
        print(f"  {e['cle']:>5} : {v['fichier']} {v['largeur']}×{v['hauteur']}, flou {v.get('flou')}, {ko:.0f} ko — {e['image'].get('titre_court') or e['image'].get('titre')}")
    entieres = sum(1 for e in images(d) if e['image'].get('entier'))
    print(f"{n} fond(s) dans {d['slug']} ({forts} en flou fort) pour {entieres} image(s) entière(s), {poids / 1e3:.1f} Mo")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('commande', choices=['preparer', 'lancer', 'rapatrier', 'arreter', 'relire', 'planche', 'publier', 'retirer', 'lister'])
    ap.add_argument('slug')
    ap.add_argument('cibles', nargs='*', metavar='CLE', help='retirer : numéros actuels (86 34b)')
    ap.add_argument('--sauf', default='', help='publier : cibles à laisser (séparées par des virgules)')
    ap.add_argument('--tout', action='store_true', help='retirer : tous les fonds de la période')
    ap.add_argument('--essai', action='store_true', help="publier : n'écrit rien")
    ap.add_argument('--lot', default='fonds.json', help='publier : lot à publier (fonds.json ; fonds-v2.json : jeu à haut et bas générés, fichiers dans fonds-v2/)')
    ap.add_argument('--graines', default='1', help='tirages à calculer (ex. 1,2)')
    ap.add_argument('--seulement', default='', help='noms d\'images séparés par des virgules (001,004-b)')
    ap.add_argument('--gpu', default='L4')
    ap.add_argument('--session', default=None)
    ap.add_argument('--reprendre', action='store_true', help='session déjà ouverte, kit déjà envoyé')
    ap.add_argument('--renvoyer-kit', action='store_true', help='avec --reprendre : renvoyer le kit (consignes changées)')
    ap.add_argument('--garder', action='store_true', help='ne pas arrêter la session à la fin')
    ap.add_argument('--sans-suivi', action='store_true', help='lancer et rendre la main (session laissée ouverte)')
    ap.add_argument('--passe', type=int, choices=[1, 2], default=1, help='preparer, lancer, rapatrier : 1 = côtés, 2 = haut et bas des décors')
    ap.add_argument('--tirage', type=int, default=None, help='relire : tirage de la passe 1 (défaut : celui de constats.json)')
    ap.add_argument('--tirage2', type=int, default=None, help='relire : tirage de la passe 2')
    ap.add_argument('--largeur', type=int, default=LARGEUR_FAIBLE, help='largeur des fonds en flou faible (px)')
    a = ap.parse_args()
    session = a.session or f'fond-{a.slug}'
    seulement = [s for s in a.seulement.split(',') if s.strip()]
    if a.commande == 'preparer':
        preparer(a.slug) if a.passe == 1 else preparer2(a.slug)
    elif a.commande == 'lancer':
        lancer(a.slug, a.gpu, session, a.graines, a.seulement, a.reprendre, a.garder, a.sans_suivi, a.renvoyer_kit, a.passe)
    elif a.commande == 'rapatrier':
        rapatrier(a.slug, session, a.passe)
    elif a.commande == 'arreter':
        arreter(session)
    elif a.commande == 'relire':
        relire(a.slug, a.tirage, a.tirage2, seulement)
    elif a.commande == 'planche':
        planche(a.slug, a.largeur)
    elif a.commande == 'publier':
        sys.exit(publier(a.slug, {cle(k) for k in seulement}, {cle(k) for k in a.sauf.split(',') if k.strip()}, a.essai, a.lot))
    elif a.commande == 'retirer':
        if not a.cibles and not a.tout:
            raise SystemExit('retirer : donner des cibles (86 34b) ou --tout')
        sys.exit(retirer(a.slug, {cle(k) for k in a.cibles}, a.tout))
    else:
        sys.exit(lister(a.slug))


if __name__ == '__main__':
    main()
