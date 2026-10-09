"""Portraits des personnes nommées par la narration (spec 12, « Portraits des personnes nommées »,
2026-10-08).

Usage :
    # Aide à la recherche : Wikidata (dates, image P18 et sa notice Commons) puis recherche Commons
    python3 scripts/diaporamas/portraits.py --chercher "Charles Alexandre de Calonne"
    python3 scripts/diaporamas/portraits.py --infos "File:David Self Portrait.jpg"
    # Par lots : une personne par ligne « id|nom » ; --essai : sans écrire le registre
    python3 scripts/diaporamas/portraits.py --lot personnes.txt [--essai]

    # Registre : licence relevée par l'API, téléchargement (cache), cadre du visage (proposé par
    # le modèle de vision puis contrôlé sur le recadrage), webp ovale ~450 px de haut
    python3 scripts/diaporamas/portraits.py --registre
    python3 scripts/diaporamas/portraits.py --registre --id danton calonne --force
    python3 scripts/diaporamas/portraits.py --planche          # planche de contrôle des recadrages

    # Mentions d'une période : visibilité de chaque personne nommée sur l'image de sa diapositive
    python3 scripts/diaporamas/portraits.py revolution --visibilite
    python3 scripts/diaporamas/portraits.py revolution --relever    # bilan des mentions

Données :
- `src/data/diaporamas/portraits.json` (commun à toutes les périodes) : liste de personnes
  `{ id, nom, dates, commons, page, fichier, auteur, date, licence, cadre_visage, note? }` ;
  une personne sans portrait fiable garde `id`, `nom`, `dates` et une `note`, sans `commons` ni
  `fichier` (le lecteur ne montre rien pour elle). `cadre_visage` : [x0, y0, x1, y1] en fractions
  de l'original, le visage avec cheveux et menton ; `cadre_visage_manuel: true` le fige.
- Dans chaque diapositive : `personnes` = mentions d'une personne qui **n'est pas visible** sur
  l'image, `{ id, quand }` (`quand` : le nom tel qu'il est dit, cherché après le précédent ;
  `instant` écrit par surimpressions.py) ; `personnes_vues` = mentions d'une personne visible sur
  l'image (pas de portrait), gardées pour mémoire et pour verifier.py.
- Images : `public/diaporamas/portraits/<id>.webp` (rectangle 4:5 recadré sur le visage, que le
  lecteur montre en ovale), ~450 px de haut.

Visibilité : « visible » veut dire représentée de façon reconnaissable (sujet de l'œuvre, ou figure
nettement identifiable par la scène ou le titre) ; une silhouette indistincte dans une foule ne
compte pas. Le titre de l'œuvre et sa notice d'abord, puis Gemini Flash (une question par
diapositive, toutes ses personnes à la fois) ; le script signale chaque désaccord entre les données
et le modèle, à trancher à la main. Cache : .cache/diaporamas/<slug>/personnes.json.

Recadrage : le modèle propose le rectangle du visage sur l'image quadrillée ; on en tire un
rectangle 4:5 où le visage occupe ~58 % de la hauteur, un peu au-dessus du centre (place du cou et
du col), ramené dans l'image ; puis le modèle revoit le recadrage (un seul visage entier, centré,
ni coupé ni minuscule) ; un refus est signalé « à relire ». Cache : .cache/diaporamas/portraits/.
"""
import argparse, hashlib, json, os, sys, threading, time, urllib.error, urllib.parse, urllib.request
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


def original(p: dict, info: dict) -> Image.Image:
    """Original Commons (cache), ou vignette de 2400 px pour un très grand fichier."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha1(p['commons'].encode()).hexdigest()[:16] + '.img')
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


def traiter(p: dict, force: bool) -> tuple[dict, str]:
    """Licence, original, cadre du visage, contrôle, webp. Rend (entrée mise à jour, bilan)."""
    if not p.get('commons'):
        return p, f"{p['id']:28s} pas de portrait ({p.get('note', 'sans note')})"
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
    im = original(p, info)
    L, H = im.size
    cache_f = CACHE / 'cadres.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    cle = hashlib.sha1(json.dumps([VERSION, MODELE, p['commons'], p['nom']]).encode()).hexdigest()[:16]
    bilan = ''
    if not p.get('cadre_visage_manuel') and (force or not p.get('cadre_visage') or cache.get(p['id'], {}).get('cle') != cle):
        r = appel(CONSIGNES_VISAGE, SCHEMA_VISAGE, [{'role': 'user', 'parts': [
            {'text': f"Portrait de {p['nom']} ({p['dates']}) : {p.get('titre') or p['commons']}."},
            {'inline_data': {'mime_type': 'image/jpeg', 'data': _jpeg(avec_grille(reduire(im)))}}]}])
        v = [round(float(z), 3) for z in r.get('visage', [])]
        if len(v) != 4 or not (0 <= v[0] < v[2] <= 1 and 0 <= v[1] < v[3] <= 1):
            raise ErreurPortrait(f"{p['id']} : visage illisible {v}")
        p['cadre_visage'] = v
        boite = recadrage(v, L, H)
        k = appel(CONSIGNES_CONTROLE, SCHEMA_CONTROLE, [{'role': 'user', 'parts': [
            {'text': f"Personne nommée : {p['nom']} ({p['dates']})."},
            {'inline_data': {'mime_type': 'image/jpeg', 'data': _jpeg(im.crop(boite).resize((320, 400)))}}]}])
        with verrou:
            cache[p['id']] = {'cle': cle, 'visage': v, 'controle': k}
            cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=1) + '\n')
        bilan = 'cadre proposé, contrôle ' + ('ok' if k.get('ok') else f"REFUSÉ : {k.get('probleme')} (à relire)")
    else:
        k = cache.get(p['id'], {}).get('controle')
        bilan = 'cadre manuel' if p.get('cadre_visage_manuel') else ('cadre en cache, contrôle ' + ('ok' if (k or {}).get('ok') else 'à relire'))
    boite = recadrage(p['cadre_visage'], L, H)
    SORTIE.mkdir(parents=True, exist_ok=True)
    p['fichier'] = f"portraits/{p['id']}.webp"
    sortie = c.PUBLIC / p['fichier']
    v = im.crop(boite)
    v = v.resize((round(HAUTEUR * RATIO), HAUTEUR), Image.LANCZOS)
    v.save(sortie, 'WEBP', quality=QUALITE, method=6)
    return p, f"{p['id']:28s} {licence:22s} {sortie.stat().st_size // 1024:3d} Ko  {bilan}"


def registre(ids: list[str] | None, force: bool) -> int:
    r = lire_registre()
    a_faire = [p for p in r if not ids or p['id'] in ids]
    erreurs = 0
    with ThreadPoolExecutor(4) as ex:
        futurs = {ex.submit(traiter, p, force): p for p in a_faire}
        for f in as_completed(futurs):
            try:
                _, bilan = f.result()
                print(bilan)
            except gemini.BudgetAtteint as e:
                erreurs += 1
                print('ARRÊT', e)
                for fu in futurs:
                    fu.cancel()
            except ErreurPortrait as e:
                erreurs += 1
                print('ERREUR', e)
    ordre = {p['id']: k for k, p in enumerate(r)}
    ecrire_registre(sorted(r, key=lambda p: ordre[p['id']]))
    print(f"{len(a_faire)} portrait(s) ; {cout()}")
    return 1 if erreurs else 0


def planche() -> None:
    """Planche de contrôle : chaque médaillon en ovale, avec son nom (.cache/diaporamas/portraits/planche.jpg)."""
    r = [p for p in lire_registre() if p.get('fichier')]
    col, lc, hc = 8, 160, 230
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
        d.text((x + 8, y + 202), p.get('dates', ''), fill=(90, 90, 90), font=police)
    f = CACHE / 'planche.jpg'
    page.save(f, quality=88)
    print(f.relative_to(c.RACINE))


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
    p.add_argument('--essai', action='store_true', help='avec --lot : affiche sans écrire le registre')
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
    if a.registre:
        code = registre(a.id, a.force)
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
