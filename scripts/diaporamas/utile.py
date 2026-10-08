"""Zone utile des images d'une période : `image.utile` (spec 12, « Sans bordures »).

Usage :
    python3 scripts/diaporamas/utile.py revolution            # ce qui manque ou a changé
    python3 scripts/diaporamas/utile.py revolution --n 12 37  # ces diapositives (refaites)
    python3 scripts/diaporamas/utile.py revolution --force    # tout refaire (sauf manuelles)
    python3 scripts/diaporamas/utile.py revolution --planche  # planche de contrôle seulement
    python3 scripts/diaporamas/utile.py revolution --pixels   # analyse des bords seule, sans modèle

La zone utile `[x0, y0, x1, y1]` (fractions de l'image servie, après `recadrage`) est la
partie de l'image qui est vraiment l'œuvre : sans liseré de numérisation (blanc ou noir), sans
marge de papier, sans cadre de tableau photographié, et sans la légende gravée sous une estampe.
Le lecteur ne montre jamais rien en dehors (caméra, respiration, ouverture, intermèdes).

Deux propositions :
1. **Analyse des bords** (Pillow, numpy) : depuis chaque bord, les lignes « uniformes » (peu de
   pixels qui s'écartent de leur médiane : liseré, papier peu texturé) sont retirées ; un trait
   isolé (cuvette de la plaque, filet d'encadrement) suivi d'autre papier est franchi.
2. **Modèle de vision** (Gemini Flash, GEMINI_API_KEY de .env, comme camera.py) : il voit
   l'image avec une grille graduée et rend le rectangle de l'œuvre, sans marges de papier,
   cadre, ni légende gravée ou texte imprimé hors de la scène.

On garde la plus prudente des deux (l'intersection : chaque bord le plus rentré), plus une
petite garde de GARDE. Une zone absurde (moins de AIRE_MIN de l'image, ou un bord rentré de
plus de BORD_MAX) est refusée : on retombe sur l'autre proposition, ou sur l'image entière, et
la diapositive est signalée « à relire ».

`"utile_manuel": true` dans `image` : la zone est saisie à la main et n'est jamais réécrite.
Cache : .cache/diaporamas/<slug>/utile.json (empreinte du fichier servi et des consignes).
Planche de contrôle : .cache/diaporamas/<slug>/utile-NN.jpg (zone tracée, extérieur grisé).
"""
import argparse, hashlib, json, os, sys, textwrap, threading, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from PIL import Image, ImageDraw

import commun as c
from camera import MODELE, URL, PRIX_ENTREE, PRIX_SORTIE, _jpeg, _police, avec_grille, reduire

VERSION = 'u1'      # à changer quand les consignes ou l'analyse changent (invalide le cache)
COTE_ANALYSE = 900  # plus grand côté de l'image analysée
UNIE = 10           # étendue (5e à 95e centile, niveaux de gris) d'une bande unie (liseré)
PAPIER = 24         # étendue d'une ligne de papier clair peu texturé
TRAIT = 0.012       # un trait non uniforme plus fin (fraction du côté) suivi de papier est franchi
BORD_MAX = 0.30     # un bord n'est jamais rentré de plus (fraction du côté)
AIRE_MIN = 0.50     # une zone plus petite (fraction de l'aire de l'image) est refusée
GARDE = 0.004       # garde ajoutée de chaque côté rogné (fraction du côté)
SEUIL_ROGNE = 0.004 # un bord rentré de moins est considéré comme intact (bord ramené à 0 ou 1)

verrou = threading.Lock()
usage = {'appels': 0, 'entree': 0, 'sortie': 0}

CONSIGNES = """\
Tu prépares les images d'un diaporama documentaire : chaque image sera montrée en plein écran,
zoomée, et rien ne doit apparaître qui ne soit pas l'œuvre elle-même.

L'image t'est montrée avec une grille graduée de 0 à 1 (origine en haut à gauche). Rends le
rectangle [x0, y0, x1, y1] de la partie qui est l'œuvre proprement dite (la scène peinte,
gravée ou dessinée, le portrait, la carte, la page), en excluant tout ce qui l'entoure :
- liserés et bandes de numérisation (blancs, noirs, gris), mires de couleur, règles ;
- marges de papier autour d'une estampe ou d'un dessin, y compris la cuvette (trait de la
  plaque) et les filets d'encadrement gravés autour de la scène ;
- cadre d'un tableau photographié avec son cadre, passe-partout, mur ;
- la légende gravée ou imprimée sous (ou au-dessus de) la scène d'une estampe : titre, texte
  explicatif, noms du dessinateur et du graveur, adresse de l'éditeur, numéro de planche. Ces
  textes sont hors de la zone, même s'ils sont dans le trait carré.
Le texte qui fait partie de la scène elle-même (banderole, inscription sur un mur, phylactère,
titre d'une affiche ou d'une page imprimée qui est le sujet) reste dans la zone.

Sois précis au centième près : le bord de la zone suit le bord de la scène, sans en couper.
Si l'image n'a rien à exclure, rends [0, 0, 1, 1]. `exclu` : ce que tu as exclu, en quelques
mots (« marge de papier, légende gravée », « cadre doré », « rien »)."""

SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'zone': {'type': 'ARRAY', 'items': {'type': 'NUMBER'}, 'description': '[x0, y0, x1, y1] entre 0 et 1'},
        'exclu': {'type': 'STRING'},
        'legende_gravee': {'type': 'BOOLEAN', 'description': 'une légende gravée ou imprimée est exclue'},
    },
    'required': ['zone', 'exclu', 'legende_gravee'],
}


class ErreurUtile(Exception):
    pass


# --- Analyse des bords ------------------------------------------------------------------

def _uniformes(gris: np.ndarray, sat: np.ndarray) -> np.ndarray:
    """Pour chaque ligne (tableaux 2D : lignes × pixels), vrai si c'est une bande de bord :
    bande unie et neutre (liseré de numérisation blanc, gris ou noir), ou papier clair peu
    texturé et peu saturé. Un fond peint sombre ou un ciel (saturés, ou texturés) ne l'est pas."""
    p5, p95 = np.percentile(gris, [5, 95], axis=1)
    etendue = p95 - p5
    moy, s = gris.mean(axis=1), sat.mean(axis=1)
    unie = (etendue < UNIE) & (s < 50)
    papier = (moy > 140) & (etendue < PAPIER) & (s < 80)
    return unie | papier


def _bord(uni: np.ndarray, n: int) -> int:
    """Nombre de lignes à retirer depuis le bord : les lignes uniformes, en franchissant un
    trait non uniforme plus fin que TRAIT (cuvette, filet) quand du papier le suit."""
    maxi = int(BORD_MAX * n)
    trait = max(2, int(TRAIT * n))
    k = 0
    while k < maxi:
        if uni[k]:
            k += 1
            continue
        # Course non uniforme : franchie si courte et suivie d'au moins autant de lignes uniformes.
        j = k
        while j < maxi and not uni[j]:
            j += 1
        if j - k <= trait and j < maxi and uni[j:j + trait].all() and k > 0:
            k = j
            continue
        break
    return k


def analyse_bords(im: Image.Image) -> list[float]:
    r = reduire(im, COTE_ANALYSE)
    a = np.asarray(r.convert('L'), dtype=np.float32)
    s = np.asarray(r.convert('HSV'), dtype=np.float32)[..., 1]
    h, l = a.shape
    haut = _bord(_uniformes(a, s), h)
    bas = _bord(_uniformes(a[::-1], s[::-1]), h)
    gauche = _bord(_uniformes(a.T, s.T), l)
    droite = _bord(_uniformes(a.T[::-1], s.T[::-1]), l)
    return [gauche / l, haut / h, 1 - droite / l, 1 - bas / h]


# --- Modèle de vision -------------------------------------------------------------------

def appel(contenus: list[dict]) -> dict:
    cle = os.environ.get('GEMINI_API_KEY', '')
    if not cle:
        raise ErreurUtile('GEMINI_API_KEY absente de .env')
    corps = {
        'systemInstruction': {'parts': [{'text': CONSIGNES}]},
        'contents': contenus,
        'generationConfig': {'temperature': 0.1, 'responseMimeType': 'application/json', 'responseSchema': SCHEMA},
    }
    for essai in range(6):
        req = urllib.request.Request(f'{URL}/{MODELE}:generateContent', data=json.dumps(corps).encode(),
                                     headers={'x-goog-api-key': cle, 'Content-Type': 'application/json'})
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=180).read())
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:300]
            if e.code in (429, 500, 502, 503, 504) and essai < 5:
                time.sleep(8 * (essai + 1))
                continue
            raise ErreurUtile(f'Gemini {e.code} : {msg}') from None
        except (urllib.error.URLError, TimeoutError) as e:
            if essai < 5:
                time.sleep(8 * (essai + 1))
                continue
            raise ErreurUtile(f'Gemini injoignable : {e}') from None
    else:
        raise ErreurUtile('Gemini : trop de tentatives')
    u = d.get('usageMetadata') or {}
    with verrou:
        usage['appels'] += 1
        usage['entree'] += int(u.get('promptTokenCount') or 0)
        usage['sortie'] += int(u.get('candidatesTokenCount') or 0) + int(u.get('thoughtsTokenCount') or 0)
    try:
        texte = ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts'])
        return json.loads(texte)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise ErreurUtile(f'réponse illisible : {str(d)[:300]}') from e


def vision(im: Image.Image, x: dict) -> dict:
    i = x['image']
    notice = ', '.join(v for v in (i.get('titre'), i.get('auteur'), i.get('date'), i.get('technique')) if v)
    r = appel([{'role': 'user', 'parts': [
        {'text': f'Image : {notice}.'},
        {'inline_data': {'mime_type': 'image/jpeg', 'data': _jpeg(avec_grille(reduire(im)))}},
    ]}])
    z = r.get('zone') or []
    if len(z) != 4 or not all(isinstance(v, (int, float)) for v in z):
        raise ErreurUtile(f'zone illisible : {z}')
    return {'zone': [float(v) for v in z], 'exclu': r.get('exclu', ''), 'legende': bool(r.get('legende_gravee'))}


# --- Synthèse ---------------------------------------------------------------------------

def valide(z: list[float] | None) -> bool:
    if not z or len(z) != 4:
        return False
    x0, y0, x1, y1 = z
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        return False
    if max(x0, y0, 1 - x1, 1 - y1) > BORD_MAX + 0.02:
        return False
    return (x1 - x0) * (y1 - y0) >= AIRE_MIN


def finir(z: list[float]) -> list[float]:
    """Garde sur les côtés rognés ; un bord à peine rentré reste au bord ; arrondi au millième
    (vers l'intérieur)."""
    x0, y0, x1, y1 = z
    x0 = 0.0 if x0 < SEUIL_ROGNE else x0 + GARDE
    y0 = 0.0 if y0 < SEUIL_ROGNE else y0 + GARDE
    x1 = 1.0 if x1 > 1 - SEUIL_ROGNE else x1 - GARDE
    y1 = 1.0 if y1 > 1 - SEUIL_ROGNE else y1 - GARDE
    up = lambda v: float(np.ceil(v * 1000) / 1000)
    dn = lambda v: float(np.floor(v * 1000) / 1000)
    return [up(x0), up(y0), dn(x1), dn(y1)]


def combiner(pix: list[float], vis: list[float] | None) -> tuple[list[float], str]:
    """La plus prudente des deux (intersection) si elle est valide ; sinon la seule valide."""
    if vis is not None:
        vis = [min(1.0, max(0.0, v)) for v in vis]
    if vis is not None and valide(vis):
        inter = [max(pix[0], vis[0]), max(pix[1], vis[1]), min(pix[2], vis[2]), min(pix[3], vis[3])]
        if valide(inter):
            return finir(inter), 'les deux'
        return finir(vis), 'modèle (intersection refusée)'
    if valide(pix):
        return finir(pix), 'bords seuls' + (' (modèle refusé)' if vis is not None else '')
    return [0.0, 0.0, 1.0, 1.0], 'image entière (tout refusé)'


def empreinte(slug: str, x: dict) -> str:
    f = c.PUBLIC / slug / x['image']['fichier']
    h = hashlib.sha1(f.read_bytes()).hexdigest()[:16]
    return hashlib.sha1(json.dumps([VERSION, MODELE, h]).encode()).hexdigest()[:16]


def traiter(slug: str, x: dict, pixels_seuls: bool) -> dict:
    im = Image.open(c.PUBLIC / slug / x['image']['fichier']).convert('RGB')
    pix = analyse_bords(im)
    vis = None if pixels_seuls else vision(im, x)
    zone, source = combiner(pix, vis['zone'] if vis else None)
    return {'pixels': [round(v, 4) for v in pix], 'vision': vis, 'utile': zone, 'source': source}


# --- Planche de contrôle ----------------------------------------------------------------

def planche(slug: str, d: dict, cache: dict, par_page: int = 15, colonnes: int = 5) -> list:
    vl, vh, texte_h = 420, 420, 64
    police, petite = _police(20), _police(13)
    sorties = []
    diapos = d['diapositives']
    for p in range(0, len(diapos), par_page):
        lot = diapos[p:p + par_page]
        lignes = (len(lot) + colonnes - 1) // colonnes
        feuille = Image.new('RGB', (colonnes * vl, lignes * (vh + texte_h)), (245, 243, 238))
        dessin = ImageDraw.Draw(feuille)
        for k, x in enumerate(lot):
            ox, oy = (k % colonnes) * vl, (k // colonnes) * (vh + texte_h)
            im = Image.open(c.PUBLIC / slug / x['image']['fichier']).convert('RGB')
            im.thumbnail((vl - 10, vh - 10), Image.LANCZOS)
            u = x['image'].get('utile') or [0, 0, 1, 1]
            l, h = im.size
            boite = [u[0] * l, u[1] * h, u[2] * l - 1, u[3] * h - 1]
            voile = Image.new('RGBA', im.size, (255, 0, 255, 110))
            masque = Image.new('L', im.size, 255)
            ImageDraw.Draw(masque).rectangle(boite, fill=0)
            im = Image.composite(Image.alpha_composite(im.convert('RGBA'), voile).convert('RGB'), im, masque)
            ImageDraw.Draw(im).rectangle(boite, outline=(255, 0, 0), width=2)
            feuille.paste(im, (ox + (vl - im.width) // 2, oy + 5))
            info = cache.get(str(x['n']), {})
            marque = ' MANUEL' if x['image'].get('utile_manuel') else ''
            rog = 1 - (u[2] - u[0]) * (u[3] - u[1])
            dessin.text((ox + 8, oy + vh), f"{x['n']}{marque}  −{rog * 100:.0f} %", fill=(0, 0, 0), font=police)
            v = info.get('vision') or {}
            txt = f"{info.get('source', '')} · {v.get('exclu', '')}"
            for j, morceau in enumerate(textwrap.wrap(txt, 58)[:2]):
                dessin.text((ox + 8, oy + vh + 24 + 16 * j), morceau, fill=(40, 40, 40), font=petite)
        f = c.CACHE / d['slug'] / f'utile-{p // par_page + 1:02d}.jpg'
        f.parent.mkdir(parents=True, exist_ok=True)
        feuille.save(f, quality=85)
        sorties.append(f)
    return sorties


# --- Programme --------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug')
    p.add_argument('--n', type=int, nargs='+', help='diapositive(s) à (re)faire')
    p.add_argument('--force', action='store_true', help='tout refaire (sauf manuelles)')
    p.add_argument('--planche', action='store_true', help='planche de contrôle seulement')
    p.add_argument('--pixels', action='store_true', help='analyse des bords seule (sans modèle)')
    p.add_argument('--paralleles', type=int, default=6)
    a = p.parse_args()
    c.charger_env()

    f, d = c.lire(a.slug)
    etat_f = c.CACHE / d['slug'] / 'utile.json'
    cache = json.loads(etat_f.read_text()) if etat_f.exists() else {}
    if a.planche:
        for s in planche(d['slug'], d, cache):
            print(s.relative_to(c.RACINE))
        return 0

    a_faire = []
    for x in d['diapositives']:
        if x['image'].get('utile_manuel'):
            continue
        e = cache.get(str(x['n']))
        emp = empreinte(d['slug'], x)
        if a.n is not None:
            if x['n'] in a.n:
                a_faire.append(x)
        elif a.force or not e or e.get('empreinte') != emp or (e.get('vision') is None and not a.pixels):
            a_faire.append(x)
        elif e.get('utile'):
            x['image']['utile'] = e['utile']  # réponse en cache, sans appel
    manuelles = [x['n'] for x in d['diapositives'] if x['image'].get('utile_manuel')]
    print(f"{len(a_faire)} image(s) à analyser ({'bords seuls' if a.pixels else MODELE}) ; "
          f"manuelles : {manuelles or 'aucune'}.")

    debut = time.time()
    with ThreadPoolExecutor(max_workers=a.paralleles) as pool:
        futurs = {pool.submit(traiter, d['slug'], x, a.pixels): x for x in a_faire}
        for fut in as_completed(futurs):
            x = futurs[fut]
            try:
                r = fut.result()
            except Exception as e:  # noqa: BLE001
                print(f"{x['n']:3d} ERREUR {e}")
                continue
            x['image']['utile'] = r['utile']
            cache[str(x['n'])] = {'empreinte': empreinte(d['slug'], x), **r}
            v = r['vision'] or {}
            print(f"{x['n']:3d} {r['utile']} ({r['source']}) bords {r['pixels']} "
                  f"modèle {v.get('zone')} « {v.get('exclu', '')} »")
            with verrou:
                c.ecrire(f, d)
                etat_f.parent.mkdir(parents=True, exist_ok=True)
                etat_f.write_text(json.dumps(cache, ensure_ascii=False, indent=1))

    c.ecrire(f, d)
    rognees = [x for x in d['diapositives'] if (x['image'].get('utile') or [0, 0, 1, 1]) != [0, 0, 1, 1]]
    if rognees:
        retrait = [1 - (u[2] - u[0]) * (u[3] - u[1]) for u in (x['image']['utile'] for x in rognees)]
        print(f"\nImages rognées : {len(rognees)} / {len(d['diapositives'])} ; aire retirée moyenne "
              f"{sum(retrait) / len(retrait) * 100:.1f} % (max {max(retrait) * 100:.1f} %).")
    cout = usage['entree'] / 1e6 * PRIX_ENTREE + usage['sortie'] / 1e6 * PRIX_SORTIE
    print(f"Appels : {usage['appels']} ; jetons : {usage['entree']} en entrée, {usage['sortie']} en sortie ; "
          f"{time.time() - debut:.0f} s (coût indicatif ~{cout:.3f} $).")
    for s in planche(d['slug'], d, cache):
        print('Planche :', s.relative_to(c.RACINE))
    return 0


if __name__ == '__main__':
    sys.exit(main())
