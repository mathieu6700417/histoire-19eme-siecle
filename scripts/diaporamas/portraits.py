"""Portraits des personnes nommées par la narration (spec 12, « Portraits des personnes nommées »,
2026-10-08).

Usage :
    # Aide à la recherche : Wikidata (dates, image P18 et sa notice Commons) puis recherche Commons
    python3 scripts/diaporamas/portraits.py --chercher "Charles Alexandre de Calonne"
    python3 scripts/diaporamas/portraits.py --infos "File:David Self Portrait.jpg"
    # Par lots : une personne par ligne « id|nom » ; --essai : sans écrire le registre
    python3 scripts/diaporamas/portraits.py --lot personnes.txt [--essai]

    # Registre : licence relevée par l'API, téléchargement (cache), cadre du visage (détecteur local
    # YuNet, gratuit ; spec 13), webp ovale ~450 px de haut
    python3 scripts/diaporamas/portraits.py --registre
    python3 scripts/diaporamas/portraits.py --registre --id danton calonne --force
    python3 scripts/diaporamas/portraits.py --registre --id prudhon --repli-gemini --budget 0.05
    python3 scripts/diaporamas/portraits.py --registre --essai # étalonnage de YuNet, sans rien écrire
    python3 scripts/diaporamas/portraits.py --planche          # planche de contrôle des recadrages

    # Mentions d'une période : visibilité de chaque personne nommée sur l'image de sa diapositive
    python3 scripts/diaporamas/portraits.py revolution --visibilite
    python3 scripts/diaporamas/portraits.py revolution --relever    # bilan des mentions

Données :
- `src/data/diaporamas/<siecle>/portraits.json` (commun à toutes les périodes) : liste de personnes
  `{ id, nom, dates, commons, page, fichier, auteur, date, licence, cadre_visage, note? }` ;
  une personne sans portrait fiable garde `id`, `nom`, `dates` et une `note`, sans `commons` ni
  `fichier` (le lecteur ne montre rien pour elle). `cadre_visage` : [x0, y0, x1, y1] en fractions
  de l'original, le visage avec cheveux et menton ; `cadre_visage_manuel: true` le fige.
- Dans chaque diapositive : `personnes` = mentions d'une personne qui **n'est pas visible** sur
  l'image, `{ id, quand }` (`quand` : le nom tel qu'il est dit, cherché après le précédent ;
  `instant` écrit par surimpressions.py) ; `personnes_vues` = mentions d'une personne visible sur
  l'image (pas de portrait), gardées pour mémoire et pour verifier.py.
- Images : `public/<siecle>/diaporamas/portraits/<id>.webp` (rectangle 4:5 recadré sur le visage, que le
  lecteur montre en ovale), ~450 px de haut.

Visibilité : « visible » veut dire représentée de façon reconnaissable (sujet de l'œuvre, ou figure
nettement identifiable par la scène ou le titre) ; une silhouette indistincte dans une foule ne
compte pas. Le titre de l'œuvre et sa notice d'abord, puis Gemini Flash (une question par
diapositive, toutes ses personnes à la fois) ; le script signale chaque désaccord entre les données
et le modèle, à trancher à la main. Cache : .cache/diaporamas/<slug>/personnes.json.

Recadrage (spec 13, outil 3, depuis le 2026-10-10) : le rectangle du visage vient du détecteur local
YuNet (`visages_local.py` en mode portrait, dans le venv `.cache/venv-visages` ; un seul lancement
pour tous les portraits à cadrer ; 0 $). On en tire un rectangle 4:5 où le visage occupe ~58 % de la
hauteur, un peu au-dessus du centre (place du cou et du col), ramené dans l'image.
- Un cadre déjà au registre n'est pas recalculé (cache `cle` : même fichier Commons, même personne ;
  les cadres posés par Gemini avant la bascule restent valides), sauf `--force` ;
  `cadre_visage_manuel: true` reste prioritaire.
- Visage non trouvé : le portrait est signalé « cadre à poser à la main » (`cadre_visage` puis
  `cadre_visage_manuel: true`). Avec `--repli-gemini` (et `--budget`), le modèle de vision propose
  alors le rectangle sur l'image quadrillée puis revoit le recadrage, comme avant.
- Planche des seuls portraits nouveaux ou douteux (score bas, boîte très petite ou très décentrée,
  repli Gemini) : .cache/diaporamas/portraits/planche-a-relire.jpg ; la planche de tous : planche.jpg.
- `--registre --essai [--marge HAUT BAS CÔTÉS]` : étalonnage, sans rien écrire. YuNet est comparé
  aux cadres du registre (hors cadres manuels) : visages trouvés, IoU médiane, 10 plus gros écarts
  et leur planche (etalonnage-yunet.jpg). Objectif : 90 % de visages trouvés, IoU médiane de 0,7.
- venv ou modèle `yunet.onnx` absents : message avec les deux commandes d'installation, et arrêt.
Cache : .cache/diaporamas/portraits/ (originaux, cadres.json).
"""
import argparse, hashlib, json, os, subprocess, sys, threading, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageDraw

import commun as c
import camera
import gemini
from camera import _jpeg, _police, avec_grille, reduire

MODELE = gemini.modele('portraits')  # DIAPORAMAS_MODELE_PORTRAITS (ou _VISION), ou --modele

REGISTRE = c.DONNEES / 'portraits.json'
SORTIE = c.PUBLIC / 'portraits'
CACHE = c.CACHE / 'portraits'
VERSION = 'p1'          # consignes du modèle (invalide le cache des cadres et des contrôles)
HAUTEUR = 450           # px de haut de la webp (ovales jusqu’à 180 px, nets sur écran à densité 2 ; 300 avant le 2026-10-08)
RATIO = 0.8             # largeur / hauteur du recadrage (ovale vertical)
PART_VISAGE = 0.58      # hauteur du visage dans le recadrage
QUALITE = 82

# Cadre du visage par le détecteur local (spec 13, outil 3) : YuNet, par visages_local.py en mode portrait.
VENV_VISAGES = camera.VENV_VISAGES
MODELE_YUNET = c.RACINE / '.cache' / 'modeles-visages' / 'yunet.onnx'
INSTALLER = ('    python3 -m venv .cache/venv-visages && .cache/venv-visages/bin/pip install opencv-python-headless numpy\n'
             '    mkdir -p .cache/modeles-visages && curl -L -o .cache/modeles-visages/yunet.onnx \\\n'
             '      https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx')
VERSION_LOCALE = 'y1'   # réglages du détecteur local (invalide le cache de SES cadres, pas ceux de Gemini)
# Marge ajoutée à la boîte de visages_local.py (déjà « crâne-menton, oreille à oreille ») : haut, bas,
# côtés, en fractions de la boîte. Étalonnage du 2026-10-10 sur les 93 cadres Gemini des périodes 01 et
# 02 : sans marge, visage trouvé 92 fois sur 93, IoU médiane 0,76 ; la meilleure marge essayée
# (0, -0,05, -0,05) ne gagne que 0,02 : aucune marge retenue.
MARGE = (0.0, 0.0, 0.0)
OBJECTIF_TROUVES, OBJECTIF_IOU = 0.90, 0.70     # objectif de l'étalonnage (spec 13)
# Cadre « douteux », à relire sur la planche : score bas, boîte très petite ou très décentrée
# (aucun des 92 cadres de l'étalonnage : scores de 0,79 à 0,94, hauteurs de 9 % au moins).
SCORE_DOUTEUX, HAUTEUR_DOUTEUSE, DECENTRE = 0.6, 0.06, 0.3
verrou = threading.Lock()


class ErreurPortrait(Exception):
    pass


# --- Modèle de vision (même appel que camera.py, consignes propres) ---------------------------

def appel(consignes: str, schema: dict, contenus: list[dict]) -> dict:
    corps = {
        'systemInstruction': {'parts': [{'text': consignes}]},
        'contents': contenus,
        'generationConfig': {'temperature': 0.1, 'responseMimeType': 'application/json', 'responseSchema': schema},
    }
    d = gemini.generer('portraits', corps, nom=MODELE, erreur=ErreurPortrait)
    return gemini.json_de(d, ErreurPortrait)


def cout() -> str:
    return gemini.bilan()


# --- Registre ------------------------------------------------------------------------------

def lire_registre() -> list[dict]:
    return json.loads(REGISTRE.read_text()) if REGISTRE.exists() else []


def ecrire_registre(r: list[dict]) -> None:
    tmp = REGISTRE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(REGISTRE)


def chemin_original(p: dict):
    return CACHE / (hashlib.sha1(p['commons'].encode()).hexdigest()[:16] + '.img')


def original(p: dict, info: dict) -> Image.Image:
    """Original Commons (cache), ou vignette de 2400 px pour un très grand fichier."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = chemin_original(p)
    if not f.exists():
        url = info['url'] if (info.get('largeur') or 0) <= 4000 and info.get('mime') in ('image/jpeg', 'image/png', 'image/webp') else info['vignette']
        f.write_bytes(c.http_get(url))
        time.sleep(1)
    im = Image.open(f)
    im.load()
    return im.convert('RGB')


CONSIGNES_VISAGE = """\
Tu prépares le médaillon ovale d'un portrait. L'image t'est montrée avec une grille graduée de 0 à
1 (origine en haut à gauche). Rends le rectangle [x0, y0, x1, y1] du VISAGE de la personne
portraiturée : du haut des cheveux (ou de la perruque, sans le chapeau) au bas du menton, d'une
oreille à l'autre. S'il y a plusieurs personnes, celle qui est nommée. Précision au centième."""
SCHEMA_VISAGE = {'type': 'OBJECT', 'properties': {
    'visage': {'type': 'ARRAY', 'items': {'type': 'NUMBER'}}, 'remarque': {'type': 'STRING'}},
    'required': ['visage']}

CONSIGNES_CONTROLE = """\
On te montre un médaillon recadré dans un portrait ancien, qui sera affiché en ovale (les coins
seront masqués). Vérifie : un seul visage, entier (cheveux et menton compris), à peu près centré,
qui occupe une bonne part de la hauteur, et que ce visage est bien celui de la personne nommée
(d'après ce que tu vois : homme ou femme, âge apparent, costume cohérent avec l'époque).
`ok` : true si le médaillon convient ; sinon `probleme` en quelques mots."""
SCHEMA_CONTROLE = {'type': 'OBJECT', 'properties': {
    'ok': {'type': 'BOOLEAN'}, 'probleme': {'type': 'STRING'}}, 'required': ['ok']}


def recadrage(visage: list[float], L: int, H: int) -> tuple[int, int, int, int]:
    """Rectangle 4:5 (pixels) autour du visage : visage à PART_VISAGE de la hauteur, son centre
    à 44 % de la hauteur du rectangle, ramené dans l'image (réduit s'il le faut)."""
    x0, y0, x1, y1 = visage
    fh = (y1 - y0) * H
    h = fh / PART_VISAGE
    w = h * RATIO
    if w > L or h > H:
        k = min(L / w, H / h)
        w, h = w * k, h * k
    cx, cy = (x0 + x1) / 2 * L, (y0 + y1) / 2 * H
    a = min(max(cx - w / 2, 0), L - w)
    b = min(max(cy - 0.44 * h, 0), H - h)
    return round(a), round(b), round(a + w), round(b + h)


# --- Cadre du visage par le détecteur local (YuNet, spec 13) ---------------------------------

def verifier_yunet() -> None:
    if not VENV_VISAGES.exists() or not MODELE_YUNET.exists():
        manque = ' et '.join(str(f.relative_to(c.RACINE)) for f in (VENV_VISAGES, MODELE_YUNET) if not f.exists())
        raise SystemExit(f'Détecteur local des visages absent ({manque}). Installer :\n{INSTALLER}')


def visages_yunet(chemins: list, marge: tuple = MARGE) -> list[tuple[list[float], float] | None]:
    """Cadre du visage (fractions de l'image) et score de YuNet pour chaque image, en UN lancement de
    visages_local.py (mode portrait) dans le venv ; None quand aucun visage n'est trouvé."""
    verifier_yunet()
    if not chemins:
        return []
    r = subprocess.run([str(VENV_VISAGES), str(c.RACINE / 'scripts' / 'diaporamas' / 'visages_local.py')],
                       input=json.dumps({'portrait': True, 'scores': True, 'chemins': [str(x) for x in chemins]}),
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f'visages_local.py : échec\n{r.stderr[-600:]}\nRéinstaller au besoin :\n{INSTALLER}')
    haut, bas, cote = marge
    sortie = []
    for v in json.loads(r.stdout):
        if not v:
            sortie.append(None)
            continue
        x0, y0, x1, y1, score = v[0]
        w, h = x1 - x0, y1 - y0
        b = [x0 - cote * w, y0 - haut * h, x1 + cote * w, y1 + bas * h]
        sortie.append(([round(min(1.0, max(0.0, z)), 3) for z in b], score))
    return sortie


def doutes(v: list[float], score: float) -> list[str]:
    """Raisons de relire un cadre du détecteur : score bas, boîte très petite ou très décentrée."""
    r = []
    if score < SCORE_DOUTEUX:
        r.append(f'score bas ({score:.2f})')
    if v[3] - v[1] < HAUTEUR_DOUTEUSE:
        r.append(f'visage très petit ({(v[3] - v[1]) * 100:.0f} % de la hauteur)')
    if abs((v[0] + v[2]) / 2 - 0.5) > DECENTRE or (v[1] + v[3]) / 2 > 0.5 + DECENTRE - 0.1:
        r.append('visage très décentré')
    return r


def cles(p: dict) -> tuple[str, str]:
    """Clés de cache du cadre : celle du détecteur local, et celle des cadres Gemini d'avant la
    spec 13 (toujours admise : ces cadres ne sont pas recalculés)."""
    h = lambda *x: hashlib.sha1(json.dumps(list(x)).encode()).hexdigest()[:16]
    return h(VERSION_LOCALE, 'yunet', p['commons'], p['nom']), h(VERSION, MODELE, p['commons'], p['nom'])


def a_cadrer(p: dict, force: bool, cache: dict) -> bool:
    """Faut-il (re)calculer le cadre ? Jamais un cadre manuel ; un cadre existant est gardé tant que
    sa clé de cache vaut encore (même fichier Commons, même personne), sauf --force. Un cadre du
    registre sans entrée de cache (cache perdu) est gardé lui aussi."""
    if p.get('cadre_visage_manuel'):
        return False
    if force or not p.get('cadre_visage'):
        return True
    e = cache.get(p['id'])
    return bool(e) and e.get('cle') not in cles(p)


def preparer(p: dict) -> tuple[Image.Image, str]:
    """Licence relevée (refus si elle n'est pas libre), métadonnées, original en cache."""
    info = c.infos_fichiers([p['commons']]).get(p['commons'], {})
    if info.get('manquant'):
        raise ErreurPortrait(f"{p['id']} : fichier Commons introuvable ({p['commons']})")
    libre, licence = c.licence_libre(info)
    if not libre:
        raise ErreurPortrait(f"{p['id']} : licence refusée ({licence})")
    m = info['meta']
    p['licence'] = licence
    p['page'] = info['page']
    p.setdefault('auteur', c.texte_meta(m.get('Artist'))[:120])
    p.setdefault('date', c.texte_meta(m.get('DateTimeOriginal'))[:60])
    return original(p, info), licence


def cadre_gemini(p: dict, im: Image.Image) -> tuple[list[float], dict]:
    """Repli (`--repli-gemini`) : cadre proposé par le modèle de vision, puis contrôle du recadrage."""
    r = appel(CONSIGNES_VISAGE, SCHEMA_VISAGE, [{'role': 'user', 'parts': [
        {'text': f"Portrait de {p['nom']} ({p['dates']}) : {p.get('titre') or p['commons']}."},
        {'inline_data': {'mime_type': 'image/jpeg', 'data': _jpeg(avec_grille(reduire(im)))}}]}])
    v = [round(float(z), 3) for z in r.get('visage', [])]
    if len(v) != 4 or not (0 <= v[0] < v[2] <= 1 and 0 <= v[1] < v[3] <= 1):
        raise ErreurPortrait(f"{p['id']} : visage illisible {v}")
    k = appel(CONSIGNES_CONTROLE, SCHEMA_CONTROLE, [{'role': 'user', 'parts': [
        {'text': f"Personne nommée : {p['nom']} ({p['dates']})."},
        {'inline_data': {'mime_type': 'image/jpeg', 'data': _jpeg(im.crop(recadrage(v, *im.size)).resize((320, 400)))}}]}])
    return v, k


def medaillon(p: dict, im: Image.Image) -> int:
    """Écrit la webp 4:5 recadrée sur le visage ; rend son poids (Ko)."""
    SORTIE.mkdir(parents=True, exist_ok=True)
    p['fichier'] = f"portraits/{p['id']}.webp"
    sortie = c.PUBLIC / p['fichier']
    v = im.crop(recadrage(p['cadre_visage'], *im.size))
    v = v.resize((round(HAUTEUR * RATIO), HAUTEUR), Image.LANCZOS)
    v.save(sortie, 'WEBP', quality=QUALITE, method=6)
    return sortie.stat().st_size // 1024


def registre(ids: list[str] | None, force: bool, repli: bool = False) -> int:
    """Licences et originaux (en parallèle), cadres manquants par YuNet en un seul lancement
    (Gemini seulement en repli demandé), médaillons, planche des portraits à relire."""
    r = lire_registre()
    a_faire = [p for p in r if not ids or p['id'] in ids]
    erreurs = 0
    prets: dict[str, tuple[Image.Image, str]] = {}
    with ThreadPoolExecutor(4) as ex:
        futurs = {ex.submit(preparer, p): p for p in a_faire if p.get('commons')}
        for f in as_completed(futurs):
            try:
                prets[futurs[f]['id']] = f.result()
            except ErreurPortrait as e:
                erreurs += 1
                print('ERREUR', e)
    cache_f = CACHE / 'cadres.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    besoin = [p for p in a_faire if p['id'] in prets and a_cadrer(p, force, cache)]
    trouves = visages_yunet([chemin_original(p) for p in besoin]) if besoin else []
    bilans, relire, arret = {}, {}, None
    for p, t in zip(besoin, trouves):
        im = prets[p['id']][0]
        if t:
            v, score = t
            d = doutes(v, score)
            p['cadre_visage'] = v
            cache[p['id']] = {'cle': cles(p)[0], 'visage': v, 'source': 'yunet', 'score': score, 'douteux': d}
            bilans[p['id']] = f'cadre YuNet (score {score:.2f})' + (f" DOUTEUX : {', '.join(d)} (à relire)" if d else '')
            relire[p['id']] = ', '.join(d) or 'nouveau'
            continue
        if repli and not arret:
            try:
                v, k = cadre_gemini(p, im)
            except gemini.BudgetAtteint as e:
                arret = str(e)
                print('ARRÊT', e)
            except ErreurPortrait as e:
                print('ERREUR', e)
            else:
                p['cadre_visage'] = v
                cache[p['id']] = {'cle': cles(p)[0], 'visage': v, 'source': 'gemini', 'controle': k}
                bilans[p['id']] = 'visage non trouvé par YuNet, cadre Gemini, contrôle ' + (
                    'ok' if k.get('ok') else f"REFUSÉ : {k.get('probleme')} (à relire)")
                relire[p['id']] = 'repli Gemini' + ('' if k.get('ok') else f" refusé : {k.get('probleme')}")
                continue
        erreurs += 1
        bilans[p['id']] = ('VISAGE NON TROUVÉ : cadre à poser à la main (`cadre_visage` et `cadre_visage_manuel: true`)'
                           + ('' if repli else ', ou relancer avec --repli-gemini --budget')
                           + (' ; ancien cadre gardé' if p.get('cadre_visage') else ''))
    for p in a_faire:
        if not p.get('commons'):
            print(f"{p['id']:28s} pas de portrait ({p.get('note', 'sans note')})")
            continue
        if p['id'] not in prets:
            continue
        im, licence = prets[p['id']]
        if p['id'] not in bilans:
            e = cache.get(p['id'])
            if p.get('cadre_visage_manuel'):
                bilans[p['id']] = 'cadre manuel'
            else:
                if not e:   # cadre d'avant le cache : noté, pour repérer un changement de fichier Commons
                    cache[p['id']] = {'cle': cles(p)[0], 'visage': p['cadre_visage'], 'source': 'registre'}
                k = (e or {}).get('controle')
                bilans[p['id']] = 'cadre en cache' + ('' if k is None or k.get('ok') else ', contrôle à relire') + (
                    f" ; douteux : {', '.join(e['douteux'])}" if (e or {}).get('douteux') else '')
        if not p.get('cadre_visage'):
            print(f"{p['id']:28s} {licence:22s}   -     {bilans[p['id']]}")
            continue
        print(f"{p['id']:28s} {licence:22s} {medaillon(p, im):3d} Ko  {bilans[p['id']]}")
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=1) + '\n')
    ordre = {p['id']: k for k, p in enumerate(r)}
    ecrire_registre(sorted(r, key=lambda p: ordre[p['id']]))
    relire = {i: n for i, n in relire.items() if next(p for p in r if p['id'] == i).get('fichier')}
    print(f"{len(a_faire)} portrait(s), {len(besoin)} cadre(s) à calculer, {sum(1 for t in trouves if t)} trouvé(s) par YuNet"
          f"{'' if not relire else f', {len(relire)} à relire'} ; {cout()}")
    if relire:
        planche(relire, 'planche-a-relire.jpg')
    return 1 if erreurs else 0


def planche(notes: dict[str, str] | None = None, nom: str = 'planche.jpg') -> None:
    """Planche de contrôle : chaque médaillon en ovale, avec son nom (.cache/diaporamas/portraits/planche.jpg).
    Avec `notes` (id -> raison) : seulement ces portraits, la raison sous le nom (planche « à relire »)."""
    r = [p for p in lire_registre() if p.get('fichier') and (notes is None or p['id'] in notes)]
    col, lc, hc = (8, 160, 230) if notes is None else (min(6, max(1, len(r))), 210, 230)
    page = Image.new('RGB', (col * lc, ((len(r) + col - 1) // col) * hc), (250, 249, 246))
    d = ImageDraw.Draw(page)
    police = _police(13)
    for k, p in enumerate(r):
        x, y = (k % col) * lc, (k // col) * hc
        im = Image.open(c.PUBLIC / p['fichier']).convert('RGB').resize((136, 170))
        masque = Image.new('L', im.size, 0)
        ImageDraw.Draw(masque).ellipse([0, 0, 135, 169], fill=255)
        page.paste(im, (x + 12, y + 8), masque)
        d.text((x + 8, y + 184), p['id'][:22], fill=(20, 20, 20), font=police)
        d.text((x + 8, y + 202), p.get('dates', '') if notes is None else notes[p['id']][:30], fill=(90, 90, 90), font=police)
    f = CACHE / nom
    page.save(f, quality=88)
    print(f.relative_to(c.RACINE))


def _iou(a, b) -> float:
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - ix * iy
    return ix * iy / u if u > 0 else 0.0


def etalonner(ids: list[str] | None, marge: tuple) -> int:
    """`--registre --essai` : YuNet comparé aux cadres déjà au registre (posés par Gemini), sans rien
    écrire (ni registre, ni cache, ni médaillon). Bilan chiffré et planche des 10 plus gros écarts."""
    import statistics
    r = [p for p in lire_registre() if p.get('commons') and p.get('cadre_visage') and not p.get('cadre_visage_manuel')
         and (not ids or p['id'] in ids)]
    ps = [p for p in r if chemin_original(p).exists()]
    if not ps:
        print('Aucun portrait cadré dont l’original soit en cache.')
        return 1
    res = visages_yunet([chemin_original(p) for p in ps], marge)
    lignes = []     # (IoU des cadres, IoU des recadrages, personne, cadre YuNet ou None, score)
    for p, t in zip(ps, res):
        if not t:
            lignes.append((0.0, 0.0, p, None, 0.0))
            continue
        with Image.open(chemin_original(p)) as im:
            L, H = im.size
        lignes.append((_iou(p['cadre_visage'], t[0]), _iou(recadrage(p['cadre_visage'], L, H), recadrage(t[0], L, H)), p, t[0], t[1]))
    trouves = [x for x in lignes if x[3]]
    part = len(trouves) / len(ps)
    med = statistics.median(x[0] for x in trouves) if trouves else 0.0
    med_r = statistics.median(x[1] for x in trouves) if trouves else 0.0
    n_doutes = sum(1 for x in trouves if doutes(x[3], x[4]))
    print(f'Étalonnage de YuNet sur les cadres du registre (rien n’est écrit) : {len(r)} portrait(s) cadré(s) hors cadres manuels, '
          f'{len(ps)} original(aux) en cache ; marge haut {marge[0]}, bas {marge[1]}, côtés {marge[2]}.')
    print(f"Visage trouvé : {len(trouves)} / {len(ps)} ({part * 100:.1f} % ; visé : {OBJECTIF_TROUVES * 100:.0f} % au moins)"
          f"{' ; non trouvé : ' + ', '.join(x[2]['id'] for x in lignes if not x[3]) if len(trouves) < len(ps) else ''}.")
    print(f'IoU avec le cadre du registre : médiane {med:.3f} (visé : {OBJECTIF_IOU} au moins), minimum '
          f"{min((x[0] for x in trouves), default=0):.2f}, {sum(1 for x in trouves if x[0] >= 0.5)} à 0,5 ou plus ; "
          f'IoU des recadrages 4:5 (ce que montre le médaillon) : médiane {med_r:.3f}. Douteux selon les seuils : {n_doutes}.')
    pires = sorted(lignes, key=lambda x: x[0])[:10]
    print('10 plus gros écarts : ' + ', '.join(f"{x[2]['id']} {x[0]:.2f}" for x in pires))
    # Planche : original avec les deux cadres (registre en bleu, YuNet en orange), puis les deux médaillons.
    lc, hc, col = 620, 330, 2
    page = Image.new('RGB', (col * lc, ((len(pires) + col - 1) // col) * hc + 30), (250, 249, 246))
    d = ImageDraw.Draw(page)
    police = _police(13)
    d.text((10, 8), 'Cadre du registre (Gemini) en bleu, médaillon de gauche ; cadre YuNet en orange, médaillon de droite.',
           fill=(20, 20, 20), font=police)
    for k, (iou, iou_r, p, v, score) in enumerate(pires):
        x, y = (k % col) * lc, (k // col) * hc + 30
        im = Image.open(chemin_original(p)).convert('RGB')
        L, H = im.size
        vue = im.copy()
        vue.thumbnail((270, 280))
        dv = ImageDraw.Draw(vue)
        for cadre, couleur in ((p['cadre_visage'], (40, 90, 200)), (v, (230, 120, 20))):
            if cadre:
                dv.rectangle([cadre[0] * vue.width, cadre[1] * vue.height, cadre[2] * vue.width, cadre[3] * vue.height],
                             outline=couleur, width=3)
        page.paste(vue, (x + 10, y + 6))
        for j, cadre in enumerate((p['cadre_visage'], v)):
            if not cadre:
                d.text((x + 290 + j * 160 + 20, y + 80), 'non trouvé', fill=(160, 30, 30), font=police)
                continue
            m = im.crop(recadrage(cadre, L, H)).resize((136, 170))
            masque = Image.new('L', m.size, 0)
            ImageDraw.Draw(masque).ellipse([0, 0, 135, 169], fill=255)
            page.paste(m, (x + 290 + j * 160, y + 6), masque)
        d.text((x + 290, y + 190), p['id'][:40], fill=(20, 20, 20), font=police)
        d.text((x + 290, y + 208), f'IoU des cadres {iou:.2f} ; des recadrages {iou_r:.2f}', fill=(90, 90, 90), font=police)
        d.text((x + 290, y + 226), f'score YuNet {score:.2f}' if v else 'visage non trouvé par YuNet', fill=(90, 90, 90), font=police)
    f = CACHE / 'etalonnage-yunet.jpg'
    page.save(f, quality=88)
    print(f'Planche des écarts : {f.relative_to(c.RACINE)}')
    ok = part >= OBJECTIF_TROUVES and med >= OBJECTIF_IOU
    print('Objectif atteint.' if ok else 'Objectif NON atteint : ajuster --marge, puis montrer la planche avant de basculer.')
    return 0 if ok else 1


# --- Recherche assistée ----------------------------------------------------------------------

def wikidata(**params) -> dict:
    return json.loads(c.http_get('https://www.wikidata.org/w/api.php?' + urllib.parse.urlencode({'format': 'json', **params})))


def chercher(nom: str) -> None:
    r = wikidata(action='wbsearchentities', search=nom, language='fr', limit=4, type='item')
    for res in r.get('search', [])[:3]:
        q = res['id']
        e = wikidata(action='wbgetentities', ids=q, props='claims|labels|descriptions', languages='fr')['entities'][q]
        cl = e.get('claims', {})

        def an(prop):
            try:
                return cl[prop][0]['mainsnak']['datavalue']['value']['time'][1:5]
            except (KeyError, IndexError, TypeError):
                return '?'
        print(f"{q} {e.get('labels', {}).get('fr', {}).get('value')} — {e.get('descriptions', {}).get('fr', {}).get('value')} ({an('P569')}-{an('P570')})")
        imgs = ['File:' + x['mainsnak']['datavalue']['value'] for x in cl.get('P18', []) if 'datavalue' in x['mainsnak']]
        for f, i in c.infos_fichiers(imgs).items() if imgs else []:
            m = i.get('meta', {})
            print(f"   P18 {f}\n       {c.texte_meta(m.get('Artist'))[:70]} | {c.texte_meta(m.get('DateTimeOriginal'))[:40]} | "
                  f"{c.licence_libre(i)[1]} | {i.get('largeur')}×{i.get('hauteur')}")
    print('Commons :')
    for x in c.chercher(f'{nom} portrait', 12):
        print(f"   {x['fichier']}\n       {x['auteur']} | {x['date']} | {x['licence']} | {x['largeur']}×{x['hauteur']} | {x['titre']}")


def _personne_wikidata(nom: str) -> dict | None:
    """Premier être humain (P31 = Q5) trouvé sur Wikidata pour `nom` : Q, libellé, description,
    dates, image P18 (fichier Commons)."""
    r = wikidata(action='wbsearchentities', search=nom, language='fr', uselang='fr', limit=5, type='item')
    ids = [x['id'] for x in r.get('search', [])]
    if not ids:
        return None
    ents = wikidata(action='wbgetentities', ids='|'.join(ids), props='claims|labels|descriptions', languages='fr')['entities']
    for q in ids:
        e = ents.get(q) or {}
        cl = e.get('claims', {})
        if not any(x['mainsnak'].get('datavalue', {}).get('value', {}).get('id') == 'Q5' for x in cl.get('P31', [])):
            continue

        def an(prop):
            try:
                t = cl[prop][0]['mainsnak']['datavalue']['value']['time']
                return t[1:5].lstrip('0') if t[0] == '+' else '?'
            except (KeyError, IndexError, TypeError):
                return '?'
        p18 = [x['mainsnak']['datavalue']['value'] for x in cl.get('P18', []) if 'datavalue' in x['mainsnak']]
        return {'q': q, 'nom': e.get('labels', {}).get('fr', {}).get('value') or nom,
                'description': e.get('descriptions', {}).get('fr', {}).get('value', ''),
                'dates': f"{an('P569')}-{an('P570')}", 'p18': 'File:' + p18[0] if p18 else None}
    return None


def lot(fichier: str, ecrire: bool) -> int:
    """`--lot FICHIER` : une personne par ligne `id|nom` ; Wikidata (humain, dates, image P18 avec sa
    licence) en une ligne par personne ; les ids absents du registre y sont pré-remplis (`id`, `nom`,
    `dates`, `wikidata`, `commons` si l'image P18 est libre, sinon une `note`), à compléter ensuite par
    `--registre --id …` (téléchargement, cadre du visage)."""
    lignes = [l.split('|', 1) for l in open(fichier, encoding='utf-8').read().splitlines()
              if l.strip() and not l.lstrip().startswith('#')]
    if any(len(l) != 2 for l in lignes):
        raise SystemExit('format attendu : une ligne « id|nom » par personne')
    r = lire_registre()
    connus = {p['id'] for p in r}
    nouveaux = []
    for pid, nom in ((a.strip(), b.strip()) for a, b in lignes):
        w = _personne_wikidata(nom)
        if w is None:
            print(f'{pid:24s} INTROUVABLE sur Wikidata (« {nom} »)')
            continue
        img = ''
        libre = False
        if w['p18']:
            i = c.infos_fichiers([w['p18']])[w['p18']]
            if not i.get('manquant'):
                libre, lic = c.licence_libre(i)
                m = i.get('meta', {})
                img = (f" | P18 {w['p18']} ({'libre' if libre else 'REFUSÉE'} {lic}, {i.get('largeur')}×{i.get('hauteur')}, "
                       f"{c.texte_meta(m.get('Artist'))[:40]}, {c.texte_meta(m.get('DateTimeOriginal'))[:20]})")
        etat = 'déjà au registre' if pid in connus else ('ajouté' if ecrire else 'à ajouter')
        print(f"{pid:24s} {w['q']:10s} {w['nom']} ({w['dates']}) — {w['description'][:60]}{img or ' | sans image P18'} [{etat}]")
        if pid not in connus:
            p = {'id': pid, 'nom': w['nom'], 'dates': w['dates'], 'wikidata': w['q']}
            if libre:
                p['commons'] = w['p18']
            else:
                p['note'] = 'pré-rempli par portraits.py --lot : pas d’image P18 libre, portrait à chercher (--chercher)'
            nouveaux.append(p)
            connus.add(pid)
    if ecrire and nouveaux:
        ecrire_registre(r + nouveaux)
    print(f"{len(nouveaux)} personne(s) {'ajoutée(s) au registre' if ecrire else 'à ajouter (--essai : rien écrit)'} ; "
          f"puis : portraits.py --registre --id {' '.join(p['id'] for p in nouveaux if p.get('commons')) or '…'}")
    return 0


def infos(fichier: str) -> None:
    i = c.infos_fichiers([fichier])[fichier]
    if i.get('manquant'):
        print('introuvable')
        return
    m = i['meta']
    for k in ('ObjectName', 'Artist', 'DateTimeOriginal', 'ImageDescription', 'Credit', 'LicenseShortName'):
        print(f'{k:18s} {c.texte_meta(m.get(k))[:400]}')
    print(f"{'taille':18s} {i['largeur']}×{i['hauteur']}  {i['page']}")


# --- Visibilité des personnes nommées ------------------------------------------------------

CONSIGNES_VISIBLE = """\
Tu relis un diaporama documentaire sur l'histoire de France ({periode}). Pour une diapositive, on te donne
l'image (une œuvre d'époque), sa notice (titre, auteur, date) et la narration dite par la voix,
puis la liste des personnes que la narration nomme. Pour chacune, dis si elle est VISIBLE sur
l'image : représentée de façon reconnaissable, comme sujet de l'œuvre (portrait, scène dont elle
est le personnage principal) ou comme figure nettement identifiable (par le titre, la légende
gravée, la composition). Une personne seulement évoquée (son œuvre, sa maison, son cercueil, son
buste lointain), absente de la scène, ou réduite à une silhouette indistincte dans une foule n'est
PAS visible. Une personne représentée par une œuvre dans l'œuvre (un portrait accroché, un buste au
premier plan) est visible. Réponds pour chaque nom, dans l'ordre, avec une raison courte."""
SCHEMA_VISIBLE = {'type': 'OBJECT', 'properties': {'personnes': {'type': 'ARRAY', 'items': {
    'type': 'OBJECT', 'properties': {'id': {'type': 'STRING'}, 'visible': {'type': 'BOOLEAN'},
                                     'raison': {'type': 'STRING'}}, 'required': ['id', 'visible']}}},
    'required': ['personnes']}


def mentions(x: dict) -> list[tuple[str, str, bool]]:
    """(id, quand, visible selon les données) de chaque mention d'une diapositive."""
    return ([(p['id'], p['quand'], False) for p in x.get('personnes', [])]
            + [(p['id'], p['quand'], True) for p in x.get('personnes_vues', [])])


def visibilite(slug: str, d: dict, ns: list[int] | None, force: bool) -> None:
    noms = {p['id']: p for p in lire_registre()}
    # Titre de la période dans les consignes (« La Révolution, 1789-1799 »), pas en dur.
    periode = ', '.join(v for v in (d.get('titre'), d.get('periode')) if v) or slug
    cache_f = c.CACHE / slug / 'personnes.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}

    def une(x):
        ids = list(dict.fromkeys(i for i, _, _ in mentions(x)))
        i = x['image']
        cle = hashlib.sha1(json.dumps([VERSION, MODELE, i['fichier'], i.get('commons'), x['narration'], ids]).encode()).hexdigest()[:16]
        if not force and cache.get(str(x['n']), {}).get('cle') == cle:
            return x, cache[str(x['n'])]['reponse']
        notice = ', '.join(v for v in (i.get('titre'), i.get('auteur'), i.get('date'), i.get('technique')) if v)
        liste = '\n'.join(f"- id « {k} » : {noms[k]['nom'] if k in noms else k} ({noms.get(k, {}).get('dates', '')})" for k in ids)
        try:
            r = appel(CONSIGNES_VISIBLE.format(periode=periode), SCHEMA_VISIBLE, [{'role': 'user', 'parts': [
            {'text': f"Notice : {notice}.\nNarration : {x['narration']}\nPersonnes nommées :\n{liste}"},
            {'inline_data': {'mime_type': 'image/jpeg', 'data': _jpeg(reduire(Image.open(c.PUBLIC / slug / i['fichier'])))}}]}])
        except gemini.BudgetAtteint:
            return x, None
        with verrou:
            cache[str(x['n'])] = {'cle': cle, 'reponse': r.get('personnes', [])}
        return x, cache[str(x['n'])]['reponse']

    a_faire = [x for x in d['diapositives'] if mentions(x) and (not ns or x['n'] in ns)]
    desaccords = 0
    with ThreadPoolExecutor(6) as ex:
        res = sorted((f.result() for f in as_completed([ex.submit(une, x) for x in a_faire])), key=lambda r: r[0]['n'])
    cache_f.parent.mkdir(parents=True, exist_ok=True)
    cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=1) + '\n')
    if any(rep is None for _, rep in res):
        print(f"ARRÊT : plafond atteint, {sum(rep is None for _, rep in res)} diapositive(s) non vues (relancer).")
    for x, rep in res:
        if rep is None:
            continue
        vu = {r['id']: r for r in rep}
        donnees = {i: v for i, _, v in mentions(x)}
        for i, v in donnees.items():
            r = vu.get(i)
            accord = r is not None and bool(r['visible']) == v
            desaccords += not accord
            print(f"{x['n']:3d} {'  ' if accord else '≠ '}{i:28s} données : {'visible' if v else 'absente':8s} "
                  f"modèle : {('visible' if r['visible'] else 'absente') if r else '?':8s} {(r or {}).get('raison', '')[:110]}")
    print(f"{desaccords} désaccord(s) à trancher ; {cout()}")


def relever(d: dict) -> None:
    noms = {p['id']: p for p in lire_registre()}
    n_m = n_vues = n_mont = 0
    sans = set()
    for x in d['diapositives']:
        for i, q, v in mentions(x):
            n_m += 1
            p = noms.get(i, {})
            if v:
                n_vues += 1
            elif p.get('fichier'):
                n_mont += 1
            else:
                sans.add(i)
            print(f"{x['n']:3d} {'vue    ' if v else ('portrait' if p.get('fichier') else 'sans   ')} {i:28s} « {q} »")
    print(f"{n_m} mention(s) : {n_vues} visibles sur l'image, {n_mont} avec portrait, "
          f"{n_m - n_vues - n_mont} sans portrait fiable ({', '.join(sorted(sans))}).")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug', nargs='?')
    p.add_argument('--chercher', metavar='NOM')
    p.add_argument('--infos', metavar='FICHIER')
    p.add_argument('--registre', action='store_true')
    p.add_argument('--planche', action='store_true')
    p.add_argument('--id', nargs='+')
    p.add_argument('--n', type=int, nargs='+')
    p.add_argument('--force', action='store_true')
    p.add_argument('--visibilite', action='store_true')
    p.add_argument('--relever', action='store_true')
    p.add_argument('--lot', metavar='FICHIER', help='personnes par lots : lignes « id|nom » (Wikidata, pré-remplissage du registre)')
    p.add_argument('--essai', action='store_true',
                   help='avec --lot : affiche sans écrire le registre ; avec --registre : étalonnage de YuNet, sans rien écrire')
    p.add_argument('--repli-gemini', action='store_true',
                   help='avec --registre : cadre proposé par Gemini quand YuNet ne trouve pas de visage (donner --budget)')
    p.add_argument('--marge', type=float, nargs=3, metavar=('HAUT', 'BAS', 'COTES'),
                   help='avec --registre --essai : marge ajoutée à la boîte de YuNet (fractions de la boîte)')
    gemini.options(p, ['portraits'])
    a = p.parse_args()
    c.charger_env()
    global MODELE
    gemini.appliquer(a, ['portraits'])
    MODELE = gemini.modele('portraits')
    if a.chercher:
        chercher(a.chercher)
        return 0
    if a.lot:
        return lot(a.lot, not a.essai)
    if a.infos:
        infos(a.infos)
        return 0
    if a.registre and a.essai:
        return etalonner(a.id, tuple(a.marge) if a.marge else MARGE)
    if a.registre:
        code = registre(a.id, a.force, a.repli_gemini)
        planche()
        return code
    if a.planche:
        planche()
        return 0
    if not a.slug:
        p.error('période attendue (ou --chercher, --infos, --registre, --planche)')
    _, d = c.lire(a.slug)
    if a.visibilite:
        visibilite(a.slug, d, a.n, a.force)
    else:
        relever(d)
    return 0


if __name__ == '__main__':
    sys.exit(main())
