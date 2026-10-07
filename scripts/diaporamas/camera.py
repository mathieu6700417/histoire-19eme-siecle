"""Caméra calée sur la narration : étapes `image.camera` d'une période (spec 12).

Usage :
    python3 scripts/diaporamas/camera.py revolution             # ce qui manque ou a changé
    python3 scripts/diaporamas/camera.py revolution --n 12 37   # ces diapositives (refaites)
    python3 scripts/diaporamas/camera.py revolution --force     # tout refaire (sauf manuelles)
    python3 scripts/diaporamas/camera.py revolution --planche   # planche-contact seulement

Pour chaque diapositive, un modèle de vision (Gemini Flash, GEMINI_API_KEY de .env) voit
l'image (réduite, avec une grille graduée) et la narration, et rend 1 à 3 étapes :
un cadre [x0, y0, x1, y1] (fractions de l'image servie, après `recadrage`) et, sauf pour la
première, un passage exact de la narration (`quand`) où la caméra doit l'avoir rejoint.

Contrôle mécanique : passages présents mot pour mot, dans l'ordre et assez espacés ; cadres
dans [0, 1] ; chaque cadre est élargi autour de son centre jusqu'à la taille minimale (voir
`ajuster`). Les erreurs sont renvoyées au modèle (deux nouveaux essais), puis, faute de mieux,
repli sur une étape unique. Le modèle relit ensuite ses cadres dessinés sur l'image et les
corrige au besoin (une relecture).

Une diapositive marquée `"camera_manuelle": true` n'est jamais réécrite. Les réponses sont
gardées dans .cache/diaporamas/<slug>/camera.json (empreinte de la narration, de l'image et
des consignes) : relancer ne rappelle le modèle que pour ce qui a changé.

`--planche` dessine les cadres numérotés sur des vignettes (12 par page) dans
.cache/diaporamas/<slug>/planche-NN.jpg, pour relire d'un coup d'œil. Elle est aussi
produite à la fin de chaque passe.

Modèle d'origine : pipeline/histoire/steps/cadrer.py du projet « Histoire zoomable » (§6.5).
"""
import argparse, base64, hashlib, io, json, os, sys, textwrap, threading, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageDraw, ImageFont

import commun as c

MODELE = os.environ.get('DIAPORAMAS_MODELE_VISION') or 'gemini-3.8-flash'
URL = 'https://generativelanguage.googleapis.com/v1beta/models'
VERSION = 'v1'          # à changer quand les consignes changent : invalide le cache, donc tout est
                        # recadré à la passe suivante (sauf les diapositives manuelles)
COTE_MODELE = 1024      # plus grand côté de l'image envoyée au modèle
MIN_FRACTION = 0.3      # largeur minimale d'un cadre, en fraction du plus grand côté de l'image,
RATIO = 1.6             # … comptée sur le cadre élargi aux proportions d'un écran (16/10)
ECART_MIN = 5           # mots entre deux passages `quand` (et depuis le début)
MAX_ETAPES = 3
ESSAIS = 3              # propositions refusées par le contrôle mécanique avant repli
RELECTURES = 1
# Tarif indicatif Gemini Flash (hypothèse, $ par million de jetons) : entrée, sortie.
PRIX_ENTREE, PRIX_SORTIE = 0.30, 2.50

verrou = threading.Lock()
usage = {'appels': 0, 'entree': 0, 'sortie': 0}


class ErreurCamera(Exception):
    pass


# --- Consignes ------------------------------------------------------------------------

CONSIGNES = f"""\
Tu règles la caméra d'un diaporama documentaire narré sur l'histoire de France. Une image
d'époque reste à l'écran pendant que la voix lit la narration (15 à 25 secondes) ; la caméra
peut passer d'un cadre à l'autre au moment où la voix prononce un passage précis.

L'image t'est montrée avec une grille graduée de 0 à 1 (origine en haut à gauche) : lis-y les
coordonnées de ce que tu cadres.

Règles :
- 1 à {MAX_ETAPES} étapes. La première, sans `quand` (null), est le cadre de départ : le sujet
  principal, ou une vue d'ensemble (toute l'image : [0, 0, 1, 1]) si la narration commence par
  une idée générale.
- Une étape suivante n'existe que si la narration nomme ou décrit un élément précis et visible
  de l'image (un personnage, un groupe, un objet, une inscription, un lieu) : son cadre montre
  cet élément, et son `quand` est le passage qui en parle.
- Pas de mouvement gratuit : si la narration ne désigne rien de précis dans l'image, une seule
  étape, sur le sujet principal. Pour un portrait, le visage avec le buste.
- Chaque `quand` est recopié caractère pour caractère de la narration (2 à 8 mots), dans
  l'ordre de la narration, à au moins {ECART_MIN} mots du début et du passage précédent.
- Un cadre est [x0, y0, x1, y1] : coin supérieur gauche puis coin inférieur droit, entre 0 et 1.
  Il englobe l'élément en entier avec un peu de marge : un visage avec le haut des épaules,
  un personnage de la tête aux pieds, une inscription avec sa voisine.
- Ne zoome pas à l'excès : un cadre fait au moins un tiers de la largeur de l'image environ
  (plus serré, il serait flou ; la chaîne l'élargira). L'écran est en paysage (16/10) : un
  cadre haut et étroit sera montré avec ses côtés, et un cadre trop haut pour l'écran est
  montré à partir de son bord supérieur (le bas est coupé) : ne coupe jamais une tête.
- Évite le bord inférieur et le coin supérieur gauche de l'image : en plein écran, le
  sous-titre couvre le bas et le cartouche (titre de l'œuvre) le haut à gauche. En
  particulier, ne cadre pas une légende gravée tout en bas de l'estampe : préfère la scène.
- N'attribue un nom à une figure que si l'image (légende, attribut, place connue dans une
  œuvre célèbre) ou la notice permet de l'identifier. Sinon, cadre le groupe ou la scène, et
  nomme la personne dans `non_identifies`.
- `montre` : ce que le cadre montre, en quelques mots."""

RELECTURE = """\
Voici tes cadres, ajustés par la chaîne (taille minimale, limites de l'image), dessinés et
numérotés sur l'image. Vérifie que chacun montre bien ce que tu annonçais, en entier, sans
couper un visage ou un élément important, et que chaque mouvement sert la narration.
Renvoie toutes les étapes, corrigées au besoin (les mêmes si tout est juste)."""

SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'etapes': {'type': 'ARRAY', 'items': {
            'type': 'OBJECT',
            'properties': {
                'quand': {'type': 'STRING', 'nullable': True,
                          'description': 'Passage exact de la narration ; null pour la première étape.'},
                'montre': {'type': 'STRING'},
                'cadre': {'type': 'ARRAY', 'items': {'type': 'NUMBER'},
                          'description': '[x0, y0, x1, y1] entre 0 et 1'},
            },
            'required': ['quand', 'montre', 'cadre'],
        }},
        'non_identifies': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
    },
    'required': ['etapes'],
}


# --- Appel Gemini ---------------------------------------------------------------------

def appel(contenus: list[dict]) -> dict:
    """Réponse JSON du modèle de vision (la clé n'est jamais affichée)."""
    cle = os.environ.get('GEMINI_API_KEY', '')
    if not cle:
        raise ErreurCamera('GEMINI_API_KEY absente de .env')
    corps = {
        'systemInstruction': {'parts': [{'text': CONSIGNES}]},
        'contents': contenus,
        'generationConfig': {'temperature': 0.2, 'responseMimeType': 'application/json',
                             'responseSchema': SCHEMA},
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
            raise ErreurCamera(f'Gemini {e.code} : {msg}') from None
        except (urllib.error.URLError, TimeoutError) as e:
            if essai < 5:
                time.sleep(8 * (essai + 1))
                continue
            raise ErreurCamera(f'Gemini injoignable : {e}') from None
    else:
        raise ErreurCamera('Gemini : trop de tentatives')
    u = d.get('usageMetadata') or {}
    with verrou:
        usage['appels'] += 1
        usage['entree'] += int(u.get('promptTokenCount') or 0)
        usage['sortie'] += int(u.get('candidatesTokenCount') or 0) + int(u.get('thoughtsTokenCount') or 0)
    try:
        texte = ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts'])
        return json.loads(texte)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise ErreurCamera(f'réponse illisible : {str(d)[:300]}') from e


# --- Géométrie ------------------------------------------------------------------------

def ajuster(cadre: list[float], L: int, H: int) -> list[float]:
    """Cadre borné à l'image et élargi autour de son centre jusqu'à la taille minimale : une
    fois porté aux proportions d'un écran 16/10, il doit faire au moins MIN_FRACTION du plus
    grand côté de l'image en largeur (sinon l'agrandissement serait flou)."""
    x0, y0, x1, y1 = (min(1.0, max(0.0, float(v))) for v in cadre)
    pw, ph = (x1 - x0) * L, (y1 - y0) * H
    cx, cy = (x0 + x1) / 2 * L, (y0 + y1) / 2 * H
    largeur_min = MIN_FRACTION * max(L, H)
    hauteur_min = largeur_min / RATIO
    # La largeur de l'écran équivalent est max(pw, ph × RATIO) : on agrandit si elle est trop petite.
    if max(pw, ph * RATIO) < largeur_min:
        k = largeur_min / max(pw, ph * RATIO, 1.0)
        pw, ph = pw * k, ph * k
    pw, ph = max(pw, min(largeur_min, L) * 0.5), max(ph, min(hauteur_min, H) * 0.5)
    pw, ph = min(pw, L), min(ph, H)
    g = min(max(cx - pw / 2, 0.0), L - pw)
    h = min(max(cy - ph / 2, 0.0), H - ph)
    return [round(g / L, 3), round(h / H, 3), round((g + pw) / L, 3), round((h + ph) / H, 3)]


# --- Passages -------------------------------------------------------------------------

_SIMPLE = str.maketrans({'’': "'", '‘': "'", '«': '"', '»': '"', ' ': ' ', ' ': ' '})


def retrouver(narration: str, passage: str) -> str | None:
    """Le passage tel qu'il est écrit dans la narration (malgré apostrophes, guillemets ou
    espaces différents) ; None s'il n'y figure pas."""
    passage = (passage or '').strip().strip('.,;:')
    if passage and passage in narration:
        return passage
    simple = narration.translate(_SIMPLE)
    cherche = ' '.join(passage.translate(_SIMPLE).split())
    pos = simple.find(cherche)
    return narration[pos:pos + len(cherche)] if cherche and pos >= 0 else None


def controler(narration: str, rendu: dict, L: int, H: int) -> tuple[list[dict], list[str]]:
    """Étapes ajustées et erreurs à renvoyer au modèle."""
    etapes = rendu.get('etapes') or []
    erreurs: list[str] = []
    if not 1 <= len(etapes) <= MAX_ETAPES:
        erreurs.append(f'{len(etapes)} étape(s) : il en faut de 1 à {MAX_ETAPES}.')
    sortie: list[dict] = []
    position = 0       # en mots
    car = 0            # en caractères : un passage se cherche après le précédent
    for i, e in enumerate(etapes[:MAX_ETAPES], 1):
        k = e.get('cadre')
        if not (isinstance(k, list) and len(k) == 4 and all(isinstance(v, (int, float)) for v in k)):
            erreurs.append(f'étape {i} : cadre invalide {k} (il faut [x0, y0, x1, y1]).')
            continue
        if any(v < -0.03 or v > 1.03 for v in k) or k[2] <= k[0] or k[3] <= k[1]:
            erreurs.append(f'étape {i} : cadre {k} hors de [0, 1] ou inversé (x0 < x1, y0 < y1).')
            continue
        if i > 1 and k[1] >= 0.8:
            erreurs.append(f'étape {i} : cadre {k} collé au bas de l’image, caché par le sous-titre en plein '
                           f'écran ; cadre autre chose (pas une légende gravée en bas).')
            continue
        etape = {'cadre': ajuster(k, L, H)}
        if i == 1:
            if e.get('quand'):
                erreurs.append("étape 1 : la première étape n'a pas de `quand` (null).")
        elif not e.get('quand'):
            erreurs.append(f'étape {i} : `quand` manquant.')
        else:
            q = retrouver(narration, e['quand'])
            if q is None:
                erreurs.append(f"étape {i} : « {e['quand']} » ne figure pas dans la narration ; recopie-le exactement.")
            elif len(q.split()) > 8:
                erreurs.append(f'étape {i} : « {q} » est trop long (8 mots au plus).')
            else:
                ou = narration.find(q, car)
                if ou < 0:
                    ou = narration.find(q)
                mots = len(narration[:ou].split())
                if mots - position < ECART_MIN or ou < car:
                    erreurs.append(f'étape {i} : « {q} » vient trop tôt (au moins {ECART_MIN} mots après le '
                                   f'début ou le passage précédent, dans l’ordre de la narration).')
                position, car = mots, ou + len(q)
                etape['quand'] = q
        sortie.append(etape)
    return sortie, erreurs


# --- Images ---------------------------------------------------------------------------

def _police(taille: int):
    for chemin in ('/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf',
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(chemin, taille)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=taille)
    except TypeError:
        return ImageFont.load_default()


def reduire(image: Image.Image, cote: int = COTE_MODELE) -> Image.Image:
    image = image.convert('RGB')
    image.thumbnail((cote, cote), Image.LANCZOS)
    return image


def avec_grille(image: Image.Image) -> Image.Image:
    image = image.copy()
    dessin = ImageDraw.Draw(image, 'RGBA')
    l, h = image.size
    police = _police(max(12, l // 60))
    for k in range(1, 10):
        x, y = l * k / 10, h * k / 10
        dessin.line([(x, 0), (x, h)], fill=(255, 255, 0, 110), width=1)
        dessin.line([(0, y), (l, y)], fill=(255, 255, 0, 110), width=1)
        for pos, t in (((x + 3, 3), f'{k / 10:.1f}'), ((3, y + 3), f'{k / 10:.1f}')):
            dessin.text(pos, t, fill=(255, 255, 0, 255), font=police, stroke_width=2, stroke_fill=(0, 0, 0))
    return image


COULEURS = [(255, 60, 60), (40, 190, 255), (70, 220, 70)]


def avec_cadres(image: Image.Image, etapes: list[dict]) -> Image.Image:
    image = image.copy()
    dessin = ImageDraw.Draw(image)
    l, h = image.size
    police = _police(max(16, l // 22))
    for i, e in enumerate(etapes):
        x0, y0, x1, y1 = e['cadre']
        couleur = COULEURS[i % len(COULEURS)]
        boite = [x0 * l, y0 * h, x1 * l - 1, y1 * h - 1]
        decalage = i * max(2, l // 150)  # cadres confondus : on les voit tous
        boite = [boite[0] + decalage, boite[1] + decalage, boite[2] - decalage, boite[3] - decalage]
        dessin.rectangle(boite, outline=couleur, width=max(3, l // 160))
        dessin.text((boite[0] + 8, boite[1] + 4), str(i + 1), fill=couleur, font=police,
                    stroke_width=3, stroke_fill=(0, 0, 0))
    return image


def _jpeg(image: Image.Image) -> str:
    tampon = io.BytesIO()
    image.save(tampon, 'JPEG', quality=85)
    return base64.b64encode(tampon.getvalue()).decode()


# --- Une diapositive ------------------------------------------------------------------

def image_de(slug: str, x: dict) -> Image.Image:
    return Image.open(c.PUBLIC / slug / x['image']['fichier'])


def texte_diapo(x: dict, L: int, H: int) -> str:
    i = x['image']
    notice = ', '.join(v for v in (i.get('auteur'), i.get('date'), i.get('technique')) if v)
    return (f"Image : {i.get('titre')} ({notice}), {L} × {H} px.\n"
            f"Narration : {x['narration']}")


def cadrer(slug: str, x: dict) -> dict:
    """{'camera': [...], 'montre': [...], 'non_identifies': [...], 'repli': bool, 'erreur': str|None}."""
    image = image_de(slug, x)
    L, H = image.size
    petite = reduire(image)
    grille = avec_grille(petite)
    contenus = [{'role': 'user', 'parts': [{'text': texte_diapo(x, L, H)},
                                            {'inlineData': {'mimeType': 'image/jpeg', 'data': _jpeg(grille)}}]}]
    refus = relectures = 0
    precedentes: list[dict] | None = None
    meilleur: list[dict] | None = None
    dernier_rendu: dict = {}
    while True:
        rendu = appel(contenus)
        contenus.append({'role': 'model', 'parts': [{'text': json.dumps(rendu, ensure_ascii=False)}]})
        etapes, erreurs = controler(x['narration'], rendu, L, H)
        if etapes and meilleur is None:
            meilleur = etapes[:1]
        if erreurs:
            refus += 1
            if refus >= ESSAIS:
                # Repli : une seule étape (le premier cadre valable, sinon toute l'image).
                return {'camera': [{'cadre': (meilleur or [{'cadre': [0, 0, 1, 1]}])[0]['cadre']}],
                        'montre': [(dernier_rendu.get('etapes') or [{}])[0].get('montre', 'repli')],
                        'non_identifies': [], 'repli': True, 'erreur': '; '.join(erreurs)}
            contenus.append({'role': 'user', 'parts': [{'text': 'Corrige ces erreurs et renvoie toutes les étapes :\n- '
                                                                + '\n- '.join(erreurs)}]})
            continue
        dernier_rendu = rendu
        if relectures >= RELECTURES:
            break
        relectures += 1
        contenus.append({'role': 'user', 'parts': [
            {'text': RELECTURE},
            {'inlineData': {'mimeType': 'image/jpeg', 'data': _jpeg(avec_cadres(grille, etapes))}}]})
        precedentes = etapes
    return {'camera': etapes, 'montre': [e.get('montre', '') for e in dernier_rendu.get('etapes', [])],
            'non_identifies': dernier_rendu.get('non_identifies') or [], 'repli': False, 'erreur': None,
            'relu_identique': etapes == precedentes}


def empreinte(x: dict) -> str:
    i = x['image']
    cle = json.dumps([VERSION, MODELE, x['narration'], i['fichier'], i['commons'], i.get('recadrage'),
                      i.get('largeur'), i.get('hauteur')], ensure_ascii=False)
    return hashlib.sha1(cle.encode()).hexdigest()[:16]


# --- Planche-contact --------------------------------------------------------------------

def planche(slug: str, d: dict, cache: dict, par_page: int = 12, colonnes: int = 3) -> list:
    """Vignettes avec cadres numérotés et passages, dans .cache/diaporamas/<slug>/planche-NN.jpg."""
    vl, vh, texte_h = 600, 420, 120
    police, petite = _police(22), _police(15)
    sorties = []
    diapos = d['diapositives']
    for p in range(0, len(diapos), par_page):
        lot = diapos[p:p + par_page]
        lignes = (len(lot) + colonnes - 1) // colonnes
        feuille = Image.new('RGB', (colonnes * vl, lignes * (vh + texte_h)), (245, 243, 238))
        dessin = ImageDraw.Draw(feuille)
        for k, x in enumerate(lot):
            ox, oy = (k % colonnes) * vl, (k // colonnes) * (vh + texte_h)
            etapes = x['image'].get('camera') or []
            im = reduire(image_de(slug, x), 800)
            im = avec_cadres(im, etapes)
            im.thumbnail((vl - 10, vh - 10))
            feuille.paste(im, (ox + (vl - im.width) // 2, oy + 5))
            info = cache.get(str(x['n']), {})
            marque = ' MANUEL' if x.get('camera_manuelle') else (' REPLI' if info.get('repli') else '')
            dessin.text((ox + 8, oy + vh + 2), f"{x['n']}{marque}", fill=(0, 0, 0), font=police)
            montre = info.get('montre') or []
            lignes_txt = []
            for j, e in enumerate(etapes):
                m = montre[j] if j < len(montre) and not x.get('camera_manuelle') else ''
                q = f"« {e['quand']} »" if e.get('quand') else 'départ'
                lignes_txt.append(f"{j + 1}. {q} {('— ' + m) if m else ''}")
            y = oy + vh + 28
            for ligne in lignes_txt:
                for morceau in textwrap.wrap(ligne, 70)[:2]:
                    dessin.text((ox + 8, y), morceau, fill=(40, 40, 40), font=petite)
                    y += 18
        f = c.CACHE / d['slug'] / f'planche-{p // par_page + 1:02d}.jpg'
        f.parent.mkdir(parents=True, exist_ok=True)
        feuille.save(f, quality=82)
        sorties.append(f)
    return sorties


# --- Programme -------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug')
    p.add_argument('--n', type=int, nargs='+', help='diapositive(s) à (re)faire')
    p.add_argument('--force', action='store_true', help='refaire toutes les diapositives non manuelles')
    p.add_argument('--planche', action='store_true', help='planche-contact seulement')
    p.add_argument('--paralleles', type=int, default=4)
    a = p.parse_args()
    c.charger_env()

    f, d = c.lire(a.slug)
    etat_f = c.CACHE / d['slug'] / 'camera.json'
    cache = json.loads(etat_f.read_text()) if etat_f.exists() else {}

    if a.planche:
        for s in planche(d['slug'], d, cache):
            print(s.relative_to(c.RACINE))
        return 0

    a_faire = []
    for x in d['diapositives']:
        if x.get('camera_manuelle'):
            continue
        cle = empreinte(x)
        if a.n is not None:
            if x['n'] in a.n:
                a_faire.append(x)
        elif a.force or not x['image'].get('camera') or cache.get(str(x['n']), {}).get('empreinte') != cle:
            # Réponse déjà en cache pour ce texte et cette image : on la remet sans appel.
            e = cache.get(str(x['n']))
            if not a.force and e and e.get('empreinte') == cle and e.get('camera'):
                x['image']['camera'] = e['camera']
                continue
            a_faire.append(x)
    manuelles = [x['n'] for x in d['diapositives'] if x.get('camera_manuelle')]
    print(f'{len(a_faire)} diapositive(s) à cadrer ({MODELE}) ; manuelles laissées telles quelles : '
          f'{manuelles or "aucune"}.')

    debut = time.time()
    with ThreadPoolExecutor(max_workers=a.paralleles) as pool:
        futurs = {pool.submit(cadrer, d['slug'], x): x for x in a_faire}
        for fut in as_completed(futurs):
            x = futurs[fut]
            try:
                r = fut.result()
            except Exception as e:  # noqa: BLE001
                print(f"{x['n']:3d} ERREUR {e}")
                continue
            x['image']['camera'] = r['camera']
            x['image'].pop('cadrage', None)
            cache[str(x['n'])] = {'empreinte': empreinte(x), **r}
            etapes = ' → '.join(f"{m or '?'} ({e.get('quand') or 'départ'})"
                                for m, e in zip(r['montre'] + [''] * 3, r['camera']))
            note = f" [REPLI : {r['erreur']}]" if r['repli'] else ''
            if r['non_identifies']:
                note += f" [non identifié(s) : {', '.join(r['non_identifies'])}]"
            print(f"{x['n']:3d} {len(r['camera'])} étape(s) : {etapes}{note}")
            with verrou:
                c.ecrire(f, d)
                etat_f.parent.mkdir(parents=True, exist_ok=True)
                etat_f.write_text(json.dumps(cache, ensure_ascii=False, indent=1))

    for x in d['diapositives']:
        x['image'].pop('cadrage', None)
    c.ecrire(f, d)
    cout = usage['entree'] / 1e6 * PRIX_ENTREE + usage['sortie'] / 1e6 * PRIX_SORTIE
    print(f"\nAppels : {usage['appels']} ; jetons : {usage['entree']} en entrée, {usage['sortie']} en sortie ; "
          f"{time.time() - debut:.0f} s (coût indicatif ~{cout:.3f} $, tarif supposé "
          f"{PRIX_ENTREE} $ / {PRIX_SORTIE} $ par million de jetons).")
    from collections import Counter
    print('Étapes par diapositive :', dict(sorted(Counter(len(x['image'].get('camera') or [])
                                                            for x in d['diapositives']).items())))
    replis = [k for k, v in cache.items() if v.get('repli')]
    if replis:
        print('Replis sur une étape unique :', ', '.join(sorted(replis, key=int)))
    for s in planche(d['slug'], d, cache):
        print('Planche :', s.relative_to(c.RACINE))
    return 0


if __name__ == '__main__':
    sys.exit(main())
