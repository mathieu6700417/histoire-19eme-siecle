"""Caméra calée sur la narration : étapes `image.camera` d'une période (spec 12).

Usage :
    python3 scripts/diaporamas/camera.py revolution             # ce qui manque ou a changé
    python3 scripts/diaporamas/camera.py revolution --n 12 37   # ces diapositives (refaites)
    python3 scripts/diaporamas/camera.py revolution --force     # tout refaire (sauf manuelles)
    python3 scripts/diaporamas/camera.py revolution --tenues    # seulement les tenues de plus de 7 s
    python3 scripts/diaporamas/camera.py revolution --planche   # planche-contact seulement

Pour chaque diapositive, un modèle de vision (Gemini Flash, GEMINI_API_KEY de .env) voit
l'image (réduite, avec une grille graduée), la narration et son minutage (`audio.phrases`), et
rend 1 à 4 étapes :
un cadre [x0, y0, x1, y1] (fractions de l'image servie, après `recadrage`) et, sauf pour la
première, un passage exact de la narration (`quand`) où la caméra doit l'avoir rejoint.

Contrôle mécanique : passages présents mot pour mot, dans l'ordre et assez espacés ; cadres
dans [0, 1] ; chaque cadre est élargi autour de son centre jusqu'à la taille minimale (voir
`ajuster`). Les erreurs sont renvoyées au modèle (deux nouveaux essais), puis, faute de mieux,
repli sur une étape unique. Le modèle relit ensuite ses cadres dessinés sur l'image et les
corrige au besoin (une relecture).

Tenues longues (spec 12, « Moins de tenues statiques ») : si la proposition laisse la caméra plus
de TENUE_MAX secondes sur un même cadre (minutage du lecteur : transitions de 2,5 s lancées
0,6 s avant chaque passage), le modèle est relancé une fois avec le texte dit pendant cette
tenue et invité à ajouter une étape calée sur un passage exact qui nomme un élément visible ;
s'il n'y en a pas, il garde ses étapes (le lecteur fait alors « respirer » l'image).
`--tenues` ne refait que les diapositives dont la caméra actuelle a une telle tenue.

Une diapositive marquée `"camera_manuelle": true` n'est jamais réécrite. Les réponses sont
gardées dans .cache/diaporamas/<slug>/camera.json (empreinte de la narration, de l'image et
des consignes) : relancer ne rappelle le modèle que pour ce qui a changé.

`--planche` dessine les cadres numérotés sur des vignettes (12 par page) dans
.cache/diaporamas/<slug>/planche-NN.jpg, pour relire d'un coup d'œil. Elle est aussi
produite à la fin de chaque passe.

Modèle d'origine : pipeline/histoire/steps/cadrer.py du projet « Histoire zoomable » (§6.5).
"""
import argparse, base64, hashlib, io, json, math, os, re, sys, textwrap, threading, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageDraw, ImageFont

import commun as c

MODELE = os.environ.get('DIAPORAMAS_MODELE_VISION') or 'gemini-3.8-flash'
URL = 'https://generativelanguage.googleapis.com/v1beta/models'
VERSION = 'v3'          # à changer quand les consignes changent : invalide le cache, donc tout est
                        # recadré à la passe suivante (sauf les diapositives manuelles ; une caméra
                        # v1/v2 qui passe les contrôles de vue reste valable : `empreintes_valides`)
COTE_MODELE = 1024      # plus grand côté de l'image envoyée au modèle
MIN_FRACTION = 0.3      # largeur minimale d'un cadre, en fraction du plus grand côté de l'image,
RATIO = 1.6             # … comptée sur le cadre élargi aux proportions d'un écran (16/10)
ECART_MIN = 5           # mots entre deux passages `quand` (et depuis le début)
# Règles du lecteur (spec 12, « Caméra calme et lente ») : il ignore une étape à moins de 5 s du
# passage précédent (ou du début) et un micro-déplacement ; on les refuse donc dès la proposition.
# Ces contrôles et la consigne ne changent pas l'empreinte du cache (VERSION inchangée) : les
# caméras déjà calculées restent telles quelles, le lecteur les filtre au rendu.
ECART_MIN_S = 5.0       # s entre deux passages (et depuis le début)
MICRO = 0.12            # écart de zoom (log) et de position (fraction de l'écran) minimal
MAX_ETAPES = 4
# Vue réelle (spec 12, « Caméra plus vivante et cadres justes ») : le lecteur montre un cadre dans
# la zone utile, l'image couvrant la scène, sous le cartouche et au-dessus des bandeaux du bas. La
# partie libre est une bande panoramique (~2,6:1 sur ordinateur, ~2,3:1 en plein écran 16/9) : un
# cadre plus haut est montré depuis son bord supérieur (le bas est coupé), et un cadre peu différent
# du précédent une fois ainsi coupé est ignoré (micro-déplacement). On reproduit ce calcul
# (`vue_reelle`, approché de `vue` dans Diaporama.astro) pour contrôler ce qui sera vraiment vu.
RATIO_VUE = 2.5         # largeur / hauteur de la partie libre de la scène
BANDE_HAUT, BANDE_BAS = 0.2, 0.15   # bandeaux couverts au-dessus et au-dessous, en hauteurs de vue
COUVERT_MIN = 0.8       # part du cadre (hauteur et largeur) que la vue doit montrer : sujet entier
UNI_MAX = 0.75          # dernière vue : part de pixels sans détail (ciel, fond, marge) au-delà de laquelle elle est refusée
TENUE_MAX = 7.0         # s : au-delà, une tenue sur un même cadre appelle une étape de plus
# Minutage des transitions du lecteur, approché (src/components/Diaporama.astro, `plan`, désormais
# 3 à 6 s, arrivée ~1 s après le passage) : on garde l'ancien calcul, qui sert aussi à valider le
# cache v1 (`empreintes_valides`) ; l'écart sur une tenue est d'environ une seconde.
TRANSITION, AVANCE = 2.5, 0.6
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
- Rythme : le minutage de la voix t'est donné (début et fin de chaque phrase, en secondes). La
  caméra ne devrait pas rester plus de ~{TENUE_MAX:.0f} s sur un même cadre : si, pendant une
  tenue plus longue, la voix nomme ou décrit un autre élément précis et visible (un détail, un
  personnage, un objet), ajoute une étape calée sur ce passage exact. Jamais d'étape sans lien
  avec ce que dit la voix : s'il n'y a rien de tel, garde moins d'étapes (le lecteur anime
  doucement les tenues longues).
- Chaque `quand` est recopié caractère pour caractère de la narration (2 à 8 mots), dans
  l'ordre de la narration, à au moins {ECART_MIN} mots et {ECART_MIN_S:.0f} secondes (d'après le
  minutage) du début et du passage précédent.
- Pas de micro-déplacement : un cadre suivant diffère nettement du précédent (autre élément,
  ou zoom franc) ; sinon, garde le précédent.
- Un cadre est [x0, y0, x1, y1] : coin supérieur gauche puis coin inférieur droit, entre 0 et 1.
  Il englobe l'élément en entier avec un peu de marge : un visage avec le haut des épaules,
  un personnage de la tête aux pieds, une inscription avec sa voisine.
- Ne zoome pas à l'excès : un cadre fait au moins un tiers de la largeur de l'image environ
  (plus serré, il serait flou ; la chaîne l'élargira).
- L'écran montre une BANDE PANORAMIQUE d'environ {RATIO_VUE}:1 (largeur sur hauteur, en pixels) :
  un cadre haut et étroit sera montré avec ses côtés, et un cadre plus haut que sa largeur
  divisée par {RATIO_VUE} est montré à partir de son bord supérieur, LE BAS ÉTANT COUPÉ. Sur une
  image en hauteur, même « toute l'image » ne montre qu'une bande en haut (souvent du ciel ou des
  arbres). La hauteur maximale d'une vue t'est donnée avec l'image : choisis des cadres qui y
  tiennent, quitte à cadrer la partie la plus parlante du sujet (visage et buste plutôt qu'un
  personnage en pied, la nacelle et ses passagers plutôt que tout le ballon). Ne coupe jamais une
  tête.
- Le sujet dont parle la voix est ENTIER dans son cadre (pas seulement le haut d'un ballon, pas un
  personnage coupé au bord). Le DERNIER cadre de la diapositive montre un sujet (personnage, groupe,
  objet, scène) : jamais surtout du ciel, du feuillage, un fond uni, un mur ou une marge.
- AUCUN cadre (de départ, intermédiaire ou final) ne coupe un visage : chaque visage est soit
  entier dans la vue, soit franchement hors de la vue. Les visages de l'image te sont donnés
  (rectangles) : vérifie-les contre la vue réelle (bande coupée en bas si le cadre est trop haut).
  Attention aux portraits en buste : un cadre serré sur un détail (main, décoration, objet) coupe
  souvent la tête ; cadre alors le détail avec le visage entier, ou franchement sous le menton.
- Évite le bord inférieur et le coin supérieur gauche de l'image : en plein écran, le
  sous-titre couvre le bas et le cartouche (titre de l'œuvre) le haut à gauche. En
  particulier, ne cadre pas une légende gravée tout en bas de l'estampe : préfère la scène.
- N'attribue un nom à une figure que si l'image (légende, attribut, place connue dans une
  œuvre célèbre) ou la notice permet de l'identifier. Sinon, cadre le groupe ou la scène, et
  nomme la personne dans `non_identifies`.
- `montre` : ce que le cadre montre, en quelques mots."""

RELECTURE = """\
Voici tes cadres, ajustés par la chaîne (taille minimale, limites de l'image), dessinés et
numérotés sur l'image (trait plein) avec, en pointillé de même couleur, la partie que l'écran
montrera vraiment (bande panoramique). Suivent, dans l'ordre des étapes, les vues telles qu'elles
apparaîtront à l'écran. Vérifie sur ces vues que chacune montre bien ce que tu annonçais, EN
ENTIER, sans couper un visage ou l'élément dont parle la voix, que la DERNIÈRE vue montre un sujet
(pas surtout du ciel, du feuillage, un fond ou une marge), et que chaque mouvement sert la
narration. Renvoie toutes les étapes, corrigées au besoin (les mêmes si tout est juste)."""

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

def appel(contenus: list[dict], systeme: str | None = None, schema: dict | None = None) -> dict:
    """Réponse JSON du modèle de vision (la clé n'est jamais affichée)."""
    cle = os.environ.get('GEMINI_API_KEY', '')
    if not cle:
        raise ErreurCamera('GEMINI_API_KEY absente de .env')
    corps = {
        'systemInstruction': {'parts': [{'text': systeme or CONSIGNES}]},
        'contents': contenus,
        'generationConfig': {'temperature': 0.2, 'responseMimeType': 'application/json',
                             'responseSchema': schema or SCHEMA},
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


# --- Visages (règle « aucun visage coupé », 2026-10-09) ---------------------------------------
# Relevé une fois par image (Gemini Flash, ~0,001 $), gardé dans .cache/diaporamas/<slug>/visages.json
# par empreinte du fichier servi : la liste sert au contrôle mécanique des vues et est donnée au
# modèle avec l'image.

VISAGES_VERSION = 'v2'
VISAGES_CONSIGNES = """\
Tu relèves les visages humains d'une image d'époque (peinture, estampe, photographie). L'image t'est
montrée avec une grille graduée de 0 à 1 (origine en haut à gauche). Rends chaque visage
reconnaissable (tête vue de face, de trois quarts ou de profil, y compris d'une statue ou d'un
portrait peint dans l'image) dont la hauteur dépasse environ 2 % de celle de l'image : un rectangle
(gauche, haut, droite, bas : abscisses lues sur la graduation horizontale du haut, ordonnées sur
la graduation verticale de gauche) qui va du haut du crâne (cheveux, perruque, sans le chapeau) au menton et d'une
oreille à l'autre. Ignore les têtes minuscules d'une foule lointaine. Aucun visage : liste vide."""
# Clés nommées : avec une simple liste, Gemini rend parfois sa convention [y0, x0, y1, x1].
VISAGES_SCHEMA = {'type': 'OBJECT', 'properties': {'visages': {'type': 'ARRAY', 'items': {
    'type': 'OBJECT', 'properties': {k: {'type': 'NUMBER'} for k in ('gauche', 'haut', 'droite', 'bas')},
    'required': ['gauche', 'haut', 'droite', 'bas']}}}, 'required': ['visages']}
FACE_DEDANS, FACE_DEHORS = 0.9, 0.1   # part de l'aire du visage dans la vue : entier / franchement hors
FACE_MIN = 0.03         # hauteur minimale (fraction de l'image) d'un visage contrôlé : pas les têtes d'une foule


def empreinte_image(slug: str, x: dict) -> str:
    f = c.PUBLIC / slug / x['image']['fichier']
    return hashlib.sha1(VISAGES_VERSION.encode() + f.read_bytes()).hexdigest()[:16]


def _visages_cache(slug: str) -> tuple:
    f = c.CACHE / slug / 'visages.json'
    return f, (json.loads(f.read_text()) if f.exists() else {})


def visages(slug: str, x: dict, appeler: bool = True) -> list[list[float]] | None:
    """Rectangles des visages de l'image (fractions) ; None si non relevés et `appeler` faux."""
    cle = empreinte_image(slug, x)
    with verrou:
        f, cache = _visages_cache(slug)
        if cle in cache:
            return cache[cle]
    if not appeler:
        return None
    grille = avec_grille(reduire(image_de(slug, x)))
    r = appel([{'role': 'user', 'parts': [{'text': f"Image : {x['image'].get('titre')}."},
                                          {'inlineData': {'mimeType': 'image/jpeg', 'data': _jpeg(grille)}}]}],
              VISAGES_CONSIGNES, VISAGES_SCHEMA)
    liste = [[round(min(1, max(0, float(k[c_]))), 3) for c_ in ('gauche', 'haut', 'droite', 'bas')]
             for k in r.get('visages') or [] if isinstance(k, dict)]
    liste = [k for k in liste if k[2] > k[0] and k[3] > k[1]]
    with verrou:
        f, cache = _visages_cache(slug)
        cache[cle] = liste
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(cache, ensure_ascii=False))
    return liste


ZOOM_TENUE = 1.12      # zoom lent continu du lecteur pendant une tenue (SOUFFLE dans Diaporama.astro)


def vue_zoomee(v: list[float], cadre: list[float]) -> list[float]:
    """Vue `v` au bout du zoom lent d'une tenue : resserrée de ZOOM_TENUE, glissée vers le centre du
    cadre visé dans la limite de la marge libre (comme `souffle` du lecteur)."""
    w, h = v[2] - v[0], v[3] - v[1]
    k = 1 / ZOOM_TENUE
    mx, my = (1 - k) * w / 2, (1 - k) * h / 2
    ox = max(-mx, min(mx, (cadre[0] + cadre[2] - v[0] - v[2]) / 2))
    oy = max(-my, min(my, (cadre[1] + cadre[3] - v[1] - v[3]) / 2))
    return [v[0] + mx + ox, v[1] + my + oy, v[2] - mx + ox, v[3] - my + oy]


def visages_coupes(v: list[float], faces: list[list[float]]) -> list[list[float]]:
    """Visages ni entiers dans la vue `v`, ni franchement dehors (les rectangles aberrants rendus
    par le modèle, bandes plus de trois fois plus larges que hautes en proportion de l'image, sont
    ignorés)."""
    sortie = []
    for k in faces:
        if k[3] - k[1] < FACE_MIN or (k[2] - k[0]) > 3 * (k[3] - k[1]):
            continue
        a = (k[2] - k[0]) * (k[3] - k[1])
        i = max(0, min(k[2], v[2]) - max(k[0], v[0])) * max(0, min(k[3], v[3]) - max(k[1], v[1]))
        if a > 0 and FACE_DEHORS < i / a < FACE_DEDANS:
            sortie.append(k)
    return sortie


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


def utile_de(x: dict) -> list[float]:
    u = x['image'].get('utile')
    return u if u and 0 <= u[0] < u[2] <= 1 and 0 <= u[1] < u[3] <= 1 else [0.0, 0.0, 1.0, 1.0]


def dans_utile(cadre: list[float], u: list[float]) -> list[float]:
    """Cadre ramené dans la zone utile (déplacé s'il y tient, sinon réduit), comme `versUtile`."""
    def borne(a, b, lo, hi):
        if b - a >= hi - lo:
            return lo, hi
        if a < lo:
            a, b = lo, b + lo - a
        if b > hi:
            a, b = a - (b - hi), hi
        return a, b
    x0, x1 = borne(cadre[0], cadre[2], u[0], u[2])
    y0, y1 = borne(cadre[1], cadre[3], u[1], u[3])
    return [x0, y0, x1, y1]


def vue_reelle(cadre: list[float], L: int, H: int, u: list[float]) -> list[float]:
    """Partie de l'image (fractions) que l'écran montre pour `cadre` : bande de RATIO_VUE:1 dans la
    zone utile `u`, cadre en entier s'il y tient, sinon depuis son bord supérieur (approché de `vue`
    du lecteur)."""
    r = dans_utile(cadre, u)
    ux0, uy0, uw, uh = u[0] * L, u[1] * H, (u[2] - u[0]) * L, (u[3] - u[1]) * H
    rx, ry, rw, rh = r[0] * L, r[1] * H, (r[2] - r[0]) * L, (r[3] - r[1]) * H
    hmax = min(uw / RATIO_VUE, uh / (1 + BANDE_HAUT + BANDE_BAS))
    h = min(max(rh, rw / RATIO_VUE), hmax)
    w = h * RATIO_VUE
    x = min(max(rx + rw / 2 - w / 2, ux0), ux0 + uw - w)
    y = ry if rh > h + 0.5 else ry + rh / 2 - h / 2
    y = max(min(y, uy0 + uh - h - BANDE_BAS * h), uy0 + BANDE_HAUT * h)
    return [x / L, y / H, (x + w) / L, (y + h) / H]


def couverture(cadre: list[float], v: list[float], u: list[float]) -> tuple[float, float]:
    """Part de la largeur et de la hauteur du cadre (ramené dans la zone utile) que la vue montre."""
    r = dans_utile(cadre, u)
    cw = max(0.0, min(r[2], v[2]) - max(r[0], v[0])) / max(1e-6, r[2] - r[0])
    ch = max(0.0, min(r[3], v[3]) - max(r[1], v[1])) / max(1e-6, r[3] - r[1])
    return cw, ch


def ensemble(cadre: list[float], u: list[float]) -> bool:
    """Vue d'ensemble (le cadre couvre presque toute la zone utile) ?"""
    r = dans_utile(cadre, u)
    return (r[2] - r[0]) * (r[3] - r[1]) >= 0.85 * (u[2] - u[0]) * (u[3] - u[1])


def part_unie(image: Image.Image, v: list[float]) -> float:
    """Part des pixels sans détail (gradient faible : ciel, fond uni, marge) dans la vue `v`."""
    l, h = image.size
    g = image.convert('L').crop((int(v[0] * l), int(v[1] * h), max(int(v[0] * l) + 2, int(v[2] * l)),
                                 max(int(v[1] * h) + 2, int(v[3] * h))))
    g.thumbnail((240, 240))
    px = g.load()
    gw, gh = g.size
    plat = total = 0
    for j in range(1, gh - 1):
        for i in range(1, gw - 1):
            d = abs(px[i + 1, j] - px[i - 1, j]) + abs(px[i, j + 1] - px[i, j - 1])
            plat += d < 10
            total += 1
    return plat / max(1, total)


def erreurs_vues(x: dict, etapes: list[dict], L: int, H: int, image: Image.Image | None = None,
                 faces: list[list[float]] | None = None) -> list[str]:
    """Contrôle de ce que l'écran montrera (spec 12, « Cadres justes ») : chaque cadre tient dans
    sa vue (sujet entier ; seule une première étape de vue d'ensemble suivie d'autres en est
    dispensée) ; la dernière vue n'est pas surtout unie (avec `image`)."""
    u = utile_de(x)
    hmax = min((u[2] - u[0]) * L / RATIO_VUE, (u[3] - u[1]) * H / (1 + BANDE_HAUT + BANDE_BAS)) / H
    erreurs = []
    for i, e in enumerate(etapes):
        v = vue_reelle(e['cadre'], L, H, u)
        cw, ch = couverture(e['cadre'], v, u)
        if i == 0 and len(etapes) > 1 and ensemble(e['cadre'], u):
            continue
        if min(cw, ch) < COUVERT_MIN:
            erreurs.append(f"étape {i + 1} : cadre {e['cadre']} trop haut pour l'écran : seule la bande "
                           f"y {v[1]:.2f}-{v[3]:.2f} (x {v[0]:.2f}-{v[2]:.2f}) sera vue, soit {ch:.0%} de sa hauteur. "
                           f"Une vue fait au plus {hmax:.2f} de la hauteur de l'image : resserre le cadre sur la "
                           f"partie la plus parlante du sujet (qu'elle soit entière), sans couper de tête.")
    for i, e in enumerate(etapes):
        v = vue_reelle(e['cadre'], L, H, u)
        # La vue au début de la tenue et au bout du zoom lent (au plus fort).
        coupes = visages_coupes(v, faces or []) or visages_coupes(vue_zoomee(v, dans_utile(e['cadre'], u)), faces or [])
        if coupes:
            erreurs.append(f"étape {i + 1} : la vue montrée (x {v[0]:.2f}-{v[2]:.2f}, y {v[1]:.2f}-{v[3]:.2f}) coupe "
                           f"le(s) visage(s) {coupes} : chaque visage doit être entier dans la vue ou franchement dehors.")
    if image is not None and etapes:
        v = vue_reelle(etapes[-1]['cadre'], L, H, u)
        p = part_unie(image, v)
        if p > UNI_MAX:
            erreurs.append(f"dernière étape : la vue montrée (y {v[1]:.2f}-{v[3]:.2f}) est à {p:.0%} sans détail "
                           f"(ciel, fond uni, marge) : le dernier cadre doit montrer un sujet.")
    return erreurs


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


# --- Minutage (même calcul que etapesCamera et cadreA du lecteur) -----------------------------

_DEBUT_PHRASE = re.compile(r'[.!?…]\s+(?=[«A-ZÀÂÉÈÊÎÔÛÇ0-9])')


def debuts_phrases(texte: str) -> list[int]:
    return [0] + [m.end() for m in _DEBUT_PHRASE.finditer(texte)]


def phrases_horodatees(x: dict) -> list[tuple[int, int, float, float]]:
    """[(premier car., car. suivant, début s, fin s)] de chaque phrase de la narration ; au
    prorata des caractères si `audio.phrases` manque ou ne correspond pas."""
    texte = x['narration']
    debuts = debuts_phrases(texte)
    duree = (x.get('audio') or {}).get('duree') or 6
    ph = (x.get('audio') or {}).get('phrases')
    sortie = []
    for j, d in enumerate(debuts):
        f = debuts[j + 1] if j + 1 < len(debuts) else len(texte)
        if ph and len(ph) == len(debuts):
            t0, t1 = ph[j]
        else:
            t0, t1 = d / len(texte) * duree, f / len(texte) * duree
        sortie.append((d, f, float(t0), float(t1)))
    return sortie


def instants(x: dict, etapes: list[dict]) -> list[float]:
    """Instant (s) de chaque étape : 0 pour la première, puis le passage `quand` situé au
    prorata dans sa phrase horodatée."""
    texte, apres, sortie = x['narration'], 0, []
    phrases = phrases_horodatees(x)
    for k, e in enumerate(etapes):
        q = e.get('quand')
        pos = texte.find(q, apres) if k and q else -1
        if k and q and pos < 0:
            pos = texte.find(q)
        if pos < 0:
            sortie.append(0.0)
            continue
        apres = pos + len(q)
        d, f, t0, t1 = next(p for p in reversed(phrases) if p[0] <= pos)
        sortie.append(round(t0 + (pos - d) / max(1, f - d) * (t1 - t0), 2))
    return sortie


def tenues(x: dict, etapes: list[dict]) -> list[tuple[int, float, float]]:
    """[(étape, début, fin)] : temps passé sur chaque cadre, de la fin de la transition qui y
    mène au début de la suivante (ou à la fin de la voix)."""
    t = instants(x, etapes)
    duree = (x.get('audio') or {}).get('duree') or 6
    fen = [(0.0, 0.0)]
    for k in range(1, len(etapes)):
        place = min(TRANSITION, max(0.8, (t[k] - t[k - 1]) * 0.8))
        de = max(fen[-1][1], t[k] - AVANCE)
        fen.append((de, de + place))
    return [(k, fen[k][1], fen[k + 1][0] if k + 1 < len(etapes) else duree) for k in range(len(etapes))]


def tenue_max(x: dict, etapes: list[dict] | None = None) -> float:
    etapes = etapes if etapes is not None else (x['image'].get('camera') or [{'cadre': [0, 0, 1, 1]}])
    return max(b - a for _, a, b in tenues(x, etapes))


def minutage(x: dict) -> str:
    texte = x['narration']
    lignes = [f"Minutage de la voix ({(x.get('audio') or {}).get('duree') or 6:.1f} s) :"]
    for j, (d, f, t0, t1) in enumerate(phrases_horodatees(x), 1):
        lignes.append(f'{j}. {t0:.1f}-{t1:.1f} s : {texte[d:f].strip()}')
    return '\n'.join(lignes)


def dit_entre(x: dict, a: float, b: float) -> str:
    """Texte prononcé (à la phrase près) entre les instants a et b."""
    texte = x['narration']
    return ' '.join(texte[d:f].strip() for d, f, t0, t1 in phrases_horodatees(x) if t1 > a + 0.3 and t0 < b - 0.3)


def relance_tenues(x: dict, etapes: list[dict], montre: list[str]) -> str | None:
    """Message au modèle si une tenue dépasse TENUE_MAX et qu'il reste une étape possible."""
    if len(etapes) >= MAX_ETAPES:
        return None
    longues = [(k, a, b) for k, a, b in tenues(x, etapes) if b - a > TENUE_MAX]
    if not longues:
        return None
    lignes = []
    for k, a, b in longues:
        m = montre[k] if k < len(montre) and montre[k] else 'cadre'
        lignes.append(f'- étape {k + 1} ({m}) : la caméra y reste {b - a:.0f} s, de {a:.1f} s à {b:.1f} s, '
                      f'pendant que la voix dit : « {dit_entre(x, a, b)} »')
    return ('Rythme : avec ces étapes, la caméra reste longtemps sur un même cadre :\n' + '\n'.join(lignes)
            + f'\nSi, pendant cette tenue, la voix nomme ou décrit un élément précis et visible de l\'image '
            f'(un détail, un personnage, un objet) que le cadre tenu ne met pas en valeur, ajoute une étape '
            f'(au plus {MAX_ETAPES} en tout) dont le `quand` est ce passage exact, et dont le cadre montre cet '
            f'élément. Sinon, renvoie exactement les mêmes étapes : pas d\'étape sans lien avec la voix.')


def micro(a: list[float], b: list[float], L: int, H: int) -> bool:
    """Les deux cadres, portés aux proportions de l'écran (16/10), diffèrent-ils à peine ?"""
    def vue(k):
        w, h = (k[2] - k[0]) * L, (k[3] - k[1]) * H
        return max(w, h * RATIO), (k[0] + k[2]) / 2 * L, (k[1] + k[3]) / 2 * H
    (wa, xa, ya), (wb, xb, yb) = vue(a), vue(b)
    return (abs(math.log(wb / wa)) < MICRO
            and max(abs(xb - xa) / wa, abs(yb - ya) / (wa / RATIO)) < MICRO)


def controler(narration: str, rendu: dict, L: int, H: int, x: dict | None = None,
              image: Image.Image | None = None, faces: list[list[float]] | None = None) -> tuple[list[dict], list[str]]:
    """Étapes ajustées et erreurs à renvoyer au modèle (`x` : la diapositive, pour le minutage et
    les vues réelles ; `image` : pour le contrôle de la dernière vue)."""
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
    if x is not None and not erreurs and len(sortie) > 1:
        t = instants(x, sortie)
        for i in range(1, len(sortie)):
            if t[i] - t[i - 1] < ECART_MIN_S:
                erreurs.append(f"étape {i + 1} : « {sortie[i]['quand']} » est prononcé {t[i] - t[i - 1]:.1f} s après "
                               f"{'le début' if i == 1 else 'le passage précédent'} ; il faut au moins "
                               f"{ECART_MIN_S:.0f} s (le lecteur l'ignorerait) : choisis un passage plus tardif ou "
                               f"supprime l'étape.")
            elif micro(vue_reelle(sortie[i - 1]['cadre'], L, H, utile_de(x)),
                       vue_reelle(sortie[i]['cadre'], L, H, utile_de(x)), L, H):
                erreurs.append(f'étape {i + 1} : une fois à l’écran, vue presque identique à la précédente '
                               f'(micro-déplacement, que le lecteur ignorerait ; un cadre trop haut est coupé en bas) : '
                               f'cadre un autre élément, moins haut, ou supprime l’étape.')
    if x is not None and not erreurs and sortie:
        erreurs += erreurs_vues(x, sortie, L, H, image, faces)
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


COULEURS = [(255, 60, 60), (40, 190, 255), (70, 220, 70), (255, 170, 0)]


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


def avec_vues(image: Image.Image, x: dict, etapes: list[dict], L: int, H: int) -> Image.Image:
    """Vues réelles (pointillés de la couleur de l'étape) par-dessus les cadres."""
    image = image.copy()
    dessin = ImageDraw.Draw(image)
    l, h = image.size
    u = utile_de(x)
    for i, e in enumerate(etapes):
        v = vue_reelle(e['cadre'], L, H, u)
        couleur = COULEURS[i % len(COULEURS)]
        b = [v[0] * l + 2, v[1] * h + 2, v[2] * l - 3, v[3] * h - 3]
        pas = max(6, l // 60)
        for xx in range(int(b[0]), int(b[2]), 2 * pas):
            for yy in (b[1], b[3]):
                dessin.line([(xx, yy), (min(xx + pas, b[2]), yy)], fill=couleur, width=max(2, l // 250))
        for yy in range(int(b[1]), int(b[3]), 2 * pas):
            for xx in (b[0], b[2]):
                dessin.line([(xx, yy), (xx, min(yy + pas, b[3]))], fill=couleur, width=max(2, l // 250))
    return image


def vues_decoupees(image: Image.Image, x: dict, etapes: list[dict], L: int, H: int) -> list[Image.Image]:
    l, h = image.size
    u = utile_de(x)
    sortie = []
    for e in etapes:
        v = vue_reelle(e['cadre'], L, H, u)
        im = image.crop((int(v[0] * l), int(v[1] * h), int(v[2] * l), int(v[3] * h)))
        im.thumbnail((640, 640))
        sortie.append(im)
    return sortie


def _jpeg(image: Image.Image) -> str:
    tampon = io.BytesIO()
    image.save(tampon, 'JPEG', quality=85)
    return base64.b64encode(tampon.getvalue()).decode()


# --- Une diapositive ------------------------------------------------------------------

def image_de(slug: str, x: dict) -> Image.Image:
    return Image.open(c.PUBLIC / slug / x['image']['fichier'])


def texte_diapo(x: dict, L: int, H: int, faces: list[list[float]] | None = None) -> str:
    i = x['image']
    notice = ', '.join(v for v in (i.get('auteur'), i.get('date'), i.get('technique')) if v)
    u = utile_de(x)
    hmax = min((u[2] - u[0]) * L / RATIO_VUE, (u[3] - u[1]) * H / (1 + BANDE_HAUT + BANDE_BAS)) / H
    return (f"Image : {i.get('titre')} ({notice}), {L} × {H} px.\n"
            f"Partie montrable (sans marges ni légende) : x {u[0]:.2f}-{u[2]:.2f}, y {u[1]:.2f}-{u[3]:.2f}. "
            f"Une vue à l'écran fait au plus {hmax:.2f} de la hauteur de l'image (bande {RATIO_VUE}:1) : "
            f"un cadre plus haut sera coupé en bas.\n"
            f"Visages de l'image (à garder entiers ou franchement hors de chaque vue) : {faces or 'aucun'}.\n"
            f"Narration : {x['narration']}\n{minutage(x)}")


def cadrer(slug: str, x: dict) -> dict:
    """{'camera': [...], 'montre': [...], 'non_identifies': [...], 'repli': bool, 'erreur': str|None}."""
    image = image_de(slug, x)
    L, H = image.size
    petite = reduire(image)
    grille = avec_grille(petite)
    faces = visages(slug, x)
    contenus = [{'role': 'user', 'parts': [{'text': texte_diapo(x, L, H, faces)},
                                            {'inlineData': {'mimeType': 'image/jpeg', 'data': _jpeg(grille)}}]}]
    refus = relectures = 0
    relance = False
    valide: tuple[list[dict], dict] | None = None   # dernière proposition sans erreur
    precedentes: list[dict] | None = None
    meilleur: list[dict] | None = None
    dernier_rendu: dict = {}
    while True:
        rendu = appel(contenus)
        contenus.append({'role': 'model', 'parts': [{'text': json.dumps(rendu, ensure_ascii=False)}]})
        etapes, erreurs = controler(x['narration'], rendu, L, H, x, image, faces)
        if etapes and meilleur is None:
            meilleur = etapes[:1]
        if erreurs:
            refus += 1
            if refus >= ESSAIS and valide:
                # Une proposition juste existait (avant relance ou relecture) : on la garde.
                etapes, dernier_rendu = valide
                break
            if refus >= ESSAIS:
                # Repli : une seule étape (le premier cadre valable, sinon toute l'image).
                return {'camera': [{'cadre': (meilleur or [{'cadre': [0, 0, 1, 1]}])[0]['cadre']}],
                        'montre': [(dernier_rendu.get('etapes') or [{}])[0].get('montre', 'repli')],
                        'non_identifies': [], 'repli': True, 'erreur': '; '.join(erreurs)}
            contenus.append({'role': 'user', 'parts': [{'text': 'Corrige ces erreurs et renvoie toutes les étapes :\n- '
                                                                + '\n- '.join(erreurs)}]})
            continue
        dernier_rendu = rendu
        valide = (etapes, rendu)
        # Tenue de plus de TENUE_MAX s : une relance (une seule) pour une étape de plus, si la voix
        # nomme alors un élément visible.
        if not relance and relectures == 0:
            message = relance_tenues(x, etapes, [e.get('montre', '') for e in rendu.get('etapes', [])])
            relance = True
            if message:
                contenus.append({'role': 'user', 'parts': [{'text': message}]})
                continue
        if relectures >= RELECTURES:
            break
        relectures += 1
        contenus.append({'role': 'user', 'parts': [
            {'text': RELECTURE},
            {'inlineData': {'mimeType': 'image/jpeg', 'data': _jpeg(avec_vues(avec_cadres(grille, etapes), x, etapes, L, H))}}]
            + [{'inlineData': {'mimeType': 'image/jpeg', 'data': _jpeg(v)}} for v in vues_decoupees(petite, x, etapes, L, H)]})
        precedentes = etapes
    return {'camera': etapes, 'montre': [e.get('montre', '') for e in dernier_rendu.get('etapes', [])],
            'non_identifies': dernier_rendu.get('non_identifies') or [], 'repli': False, 'erreur': None,
            'relu_identique': etapes == precedentes, 'tenue_max': round(tenue_max(x, etapes), 1)}


def empreinte(x: dict, version: str = VERSION) -> str:
    i = x['image']
    cle = json.dumps([version, MODELE, x['narration'], i['fichier'], i['commons'], i.get('recadrage'),
                      i.get('largeur'), i.get('hauteur')], ensure_ascii=False)
    return hashlib.sha1(cle.encode()).hexdigest()[:16]


def empreintes_valides(x: dict, slug: str) -> set[str]:
    """Empreintes acceptées dans le cache : celle des consignes actuelles ; pour une caméra dont les
    vues réelles passent le contrôle (sans l'image : la dernière vue unie n'est vue qu'à la relecture),
    celle des consignes v2 et, sans tenue de plus de TENUE_MAX, celle des v1."""
    cles = {empreinte(x)}
    cam = x['image'].get('camera')
    if cam and not erreurs_vues(x, cam, *dims(x), faces=visages(slug, x, appeler=False)):
        cles.add(empreinte(x, 'v2'))
        if tenue_max(x) <= TENUE_MAX:
            cles.add(empreinte(x, 'v1'))
    return cles


def dims(x: dict) -> tuple[int, int]:
    return int(x['image'].get('largeur') or 1600), int(x['image'].get('hauteur') or 1000)


# --- Planche-contact --------------------------------------------------------------------

def planche(slug: str, d: dict, cache: dict, par_page: int = 12, colonnes: int = 3,
            ns: list[int] | None = None) -> list:
    """Vignettes avec cadres numérotés et passages, dans .cache/diaporamas/<slug>/planche-NN.jpg."""
    vl, vh, texte_h = 600, 420, 120
    police, petite = _police(22), _police(15)
    sorties = []
    diapos = [x for x in d['diapositives'] if ns is None or x['n'] in ns]
    nom = 'planche' if ns is None else 'planche-choix'
    for p in range(0, len(diapos), par_page):
        lot = diapos[p:p + par_page]
        lignes = (len(lot) + colonnes - 1) // colonnes
        feuille = Image.new('RGB', (colonnes * vl, lignes * (vh + texte_h)), (245, 243, 238))
        dessin = ImageDraw.Draw(feuille)
        for k, x in enumerate(lot):
            ox, oy = (k % colonnes) * vl, (k // colonnes) * (vh + texte_h)
            etapes = x['image'].get('camera') or []
            im = reduire(image_de(slug, x), 800)
            im = avec_vues(avec_cadres(im, etapes), x, etapes, *dims(x))
            fd = ImageDraw.Draw(im)
            for k in visages(d['slug'], x, appeler=False) or []:
                if k[3] - k[1] >= FACE_MIN:
                    fd.rectangle([k[0] * im.width, k[1] * im.height, k[2] * im.width, k[3] * im.height],
                                 outline=(255, 255, 255), width=2)
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
        f = c.CACHE / d['slug'] / f'{nom}-{p // par_page + 1:02d}.jpg'
        f.parent.mkdir(parents=True, exist_ok=True)
        feuille.save(f, quality=82)
        sorties.append(f)
    return sorties


def ignorees(x: dict, etapes: list[dict], L: int, H: int) -> list[str]:
    """Étapes que le lecteur ignorerait (passage à moins de ECART_MIN_S s du précédent retenu, ou
    vue presque identique), approché de `plan`."""
    t, u, sortie, k0 = instants(x, etapes), utile_de(x), [], 0
    for k in range(1, len(etapes)):
        if t[k] - t[k0] < ECART_MIN_S:
            sortie.append(f"étape {k + 1} ignorée ({t[k] - t[k0]:.1f} s après la précédente)")
        elif micro(vue_reelle(etapes[k0]['cadre'], L, H, u), vue_reelle(etapes[k]['cadre'], L, H, u), L, H):
            sortie.append(f'étape {k + 1} ignorée (vue presque identique)')
        else:
            k0 = k
    return sortie


def _coupes(x, e, i, n, L, H, u, faces) -> int | None:
    """Nombre de visages coupés par l'étape (début et bout du zoom) ; None si le cadre ne tient pas."""
    v = vue_reelle(e['cadre'], L, H, u)
    if not (i == 0 and n > 1 and ensemble(e['cadre'], u)) and min(couverture(e['cadre'], v, u)) < COUVERT_MIN:
        return None
    return len({tuple(k) for k in visages_coupes(v, faces) + visages_coupes(vue_zoomee(v, dans_utile(e['cadre'], u)), faces)})


def _etape_juste(x, e, i, n, L, H, u, faces) -> bool:
    return _coupes(x, e, i, n, L, H, u, faces) == 0


def reparer_etape(x: dict, e: dict, i: int, n: int, L: int, H: int, faces: list,
                  foule_permise: bool = False) -> dict | None:
    """Le cadre juste le plus proche de `e` (réparation géométrique, sans appel) : bandes de la
    hauteur d'une vue prises dans le cadre (de haut en bas : on garde les têtes), puis petits
    déplacements et changements d'échelle ; None si rien ne convient."""
    u = utile_de(x)
    if _etape_juste(x, e, i, n, L, H, u, faces):
        return e
    r = dans_utile(e['cadre'], u)
    # Le sujet : le plus grand visage que le cadre d'origine contient ; il doit rester entier dans la
    # vue réparée (sinon on « réparerait » un portrait en montrant son gilet).
    dedans = [k for k in faces if k[3] - k[1] >= FACE_MIN and (k[2] - k[0]) <= 3 * (k[3] - k[1])
              and k[0] >= r[0] - 0.01 and k[2] <= r[2] + 0.01 and k[1] >= r[1] - 0.01 and k[3] <= r[3] + 0.01]
    sujet = max(dedans, key=lambda k: (k[2] - k[0]) * (k[3] - k[1])) if dedans and not ensemble(e['cadre'], u) else None
    w, h = r[2] - r[0], r[3] - r[1]
    hmax = min((u[2] - u[0]) * L / RATIO_VUE, (u[3] - u[1]) * H / (1 + BANDE_HAUT + BANDE_BAS)) / H
    candidats = []
    hb = min(h, hmax * 0.98)
    for k in range(0, 41):                      # bandes dans le cadre, du haut vers le bas
        y0 = r[1] + (h - hb) * k / 40
        candidats.append((k / 40 * 0.5, [r[0], y0, r[2], y0 + hb]))
    for sc in (1.0, 0.9, 1.1, 0.8, 1.25, 0.7, 1.4):
        for dy in [j / 100 for j in range(-20, 21)]:
            for dx in [j / 100 for j in range(-12, 13, 2)]:
                cx, cy = (r[0] + r[2]) / 2 + dx, (r[1] + r[3]) / 2 + dy
                ww, hh = w * sc, min(h * sc, hmax * 0.98)
                cout = abs(dx) + abs(dy) + abs(math.log(sc)) + (0.05 if hh < h * sc else 0)
                candidats.append((cout, [cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2]))
    meilleur, m_coupes = None, None
    tri = sorted(candidats, key=lambda c_: c_[0])
    # Visage du sujet plus haut qu'une vue (portrait serré, zone utile étroite) : on garde au moins
    # son haut (front, yeux, nez : 60 % de sa hauteur), comme le lecteur garde les têtes.
    part = 1.0 if sujet is None or sujet[3] - sujet[1] <= hmax * 0.95 else 0.6
    if part < 1:
        foule_permise = True
    for cout, k in tri:
        k = [round(min(1, max(0, v)), 3) for v in k]
        if k[2] - k[0] < 0.05 or k[3] - k[1] < 0.05:
            continue
        f = dict(e, cadre=ajuster(k, L, H))
        if sujet is not None:
            v = vue_reelle(f['cadre'], L, H, u)
            if not (v[0] <= sujet[0] and sujet[2] <= v[2] and v[1] <= sujet[1]
                    and sujet[1] + part * (sujet[3] - sujet[1]) <= v[3]):
                continue
        nc = _coupes(x, f, i, n, L, H, u, faces)
        if nc == 0:
            return f
        if nc is not None and (m_coupes is None or nc < m_coupes):
            meilleur, m_coupes = f, nc
    # Foule ou visage plus grand qu'une vue : aucun cadre sans visage coupé ; on garde celui qui en
    # coupe le moins (signalé par `--audit`, à relire).
    return meilleur if foule_permise else None


def reparer(slug: str, x: dict, foule: bool = False) -> tuple[list[dict] | None, list[str]]:
    """Caméra réparée sans appel (cadres justes, aucun visage coupé, aucune étape que le lecteur
    ignorerait) ; (None, raisons) si impossible."""
    cam = x['image'].get('camera') or []
    L, H = dims(x)
    faces = visages(slug, x, appeler=False) or []
    sortie = []
    for i, e in enumerate(cam):
        f = reparer_etape(x, e, i, len(cam), L, H, faces, foule_permise=foule)
        if f is None:
            if i == 0:
                return None, [f'étape 1 irréparable']
            continue                            # étape abandonnée : la précédente reste
        sortie.append(f)
    # Étapes que le lecteur ignorerait : on les retire (le rendu est le même) ; si c'est la
    # dernière, on retire plutôt l'étape intermédiaire qui la précède de trop près.
    while len(sortie) > 1 and ignorees(x, sortie, L, H):
        t = instants(x, sortie)
        dernier_ignore = any(f'étape {len(sortie)} ' in m for m in ignorees(x, sortie, L, H))
        if dernier_ignore and len(sortie) > 2:
            sortie.pop(len(sortie) - 2)
        else:
            k = int(ignorees(x, sortie, L, H)[0].split()[1]) - 1
            sortie.pop(k)
    # Première étape seule restante : elle doit tenir seule (sans dispense de vue d'ensemble).
    if len(sortie) == 1 and not _etape_juste(x, sortie[0], 0, 1, L, H, utile_de(x), faces):
        f = reparer_etape(x, sortie[0], 0, 1, L, H, faces, foule_permise=foule)
        if f is None:
            return None, ['étape unique irréparable']
        sortie = [f]
    sortie[0].pop('quand', None)
    e = erreurs_vues(x, sortie, L, H, image_de(slug, x), faces)
    if foule:      # meilleur effort : seuls les cadres trop hauts et les aplats restent bloquants
        e = [m for m in e if 'visage' not in m]
    return (sortie, []) if not e else (None, e)


def audit(d: dict) -> list[tuple[int, list[str]]]:
    fautes = []
    for x in d['diapositives']:
        cam = x['image'].get('camera')
        if not cam:
            continue
        L, H = dims(x)
        e = (erreurs_vues(x, cam, L, H, image_de(d['slug'], x), visages(d['slug'], x, appeler=False))
             + ignorees(x, cam, L, H))
        if e:
            fautes.append((x['n'], e))
    return fautes


# --- Programme -------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug')
    p.add_argument('--n', type=int, nargs='+', help='diapositive(s) à (re)faire')
    p.add_argument('--force', action='store_true', help='refaire toutes les diapositives non manuelles')
    p.add_argument('--planche', action='store_true', help='planche-contact seulement')
    p.add_argument('--tenues', action='store_true',
                   help=f'seulement les diapositives dont la caméra tient plus de {TENUE_MAX:.0f} s un même cadre '
                        '(sauf celles déjà cadrées avec les consignes actuelles, sauf --force)')
    p.add_argument('--audit', action='store_true',
                   help='sans appel : diapositives dont les vues réelles échouent au contrôle (sujet coupé, '
                        'dernière vue unie) ou dont une étape serait ignorée par le lecteur')
    p.add_argument('--reparer', action='store_true',
                   help='sans appel : répare géométriquement les caméras fautives (avec --n : ces diapositives) ; '
                        'les manuelles sont seulement signalées')
    p.add_argument('--visages', action='store_true',
                   help='relever les visages de toutes les images (un appel par image, en cache), sans cadrer')
    p.add_argument('--paralleles', type=int, default=4)
    a = p.parse_args()
    c.charger_env()

    f, d = c.lire(a.slug)
    etat_f = c.CACHE / d['slug'] / 'camera.json'
    cache = json.loads(etat_f.read_text()) if etat_f.exists() else {}

    if a.visages:
        with ThreadPoolExecutor(max_workers=a.paralleles) as pool:
            res = list(pool.map(lambda x: (x['n'], visages(d['slug'], x)), d['diapositives']))
        print(f"{sum(len(v) for _, v in res)} visages sur {len(res)} images ; appels : {usage['appels']} "
              f"(~{usage['entree'] / 1e6 * PRIX_ENTREE + usage['sortie'] / 1e6 * PRIX_SORTIE:.3f} $).")
        return 0

    if a.reparer:
        faites, echecs = [], []
        for n, e in audit(d):
            x = next(y for y in d['diapositives'] if y['n'] == n)
            if a.n and n not in a.n:
                continue
            if x.get('camera_manuelle'):
                echecs.append((n, ['manuelle'] + e))
                continue
            cam, raisons = reparer(d['slug'], x)
            if cam is None:
                cam, raisons = reparer(d['slug'], x, foule=True)
                if cam is not None:
                    echecs.append((n, ['réparée au mieux : visage(s) encore coupé(s) (foule ou visage plus grand qu’une vue)']))
            if cam is None:
                echecs.append((n, raisons))
                continue
            x['image']['camera'] = cam
            faites.append(n)
        f2, d2 = c.lire(a.slug)            # relu juste avant d'écrire : seules les caméras changent
        for y in d2['diapositives']:
            if y['n'] in faites:
                y['image']['camera'] = next(x for x in d['diapositives'] if x['n'] == y['n'])['image']['camera']
        c.ecrire(f2, d2)
        print(f"Réparées : {len(faites)} : {' '.join(map(str, faites))}")
        for n, r in echecs:
            print(f'{n:3d} NON RÉPARÉE : ' + ' | '.join(r)[:300])
        return 0

    if a.audit:
        fautes = audit(d)
        for n, e in fautes:
            print(f'{n:3d} ' + ' | '.join(e))
        print(f"{len(fautes)} diapositive(s) à revoir : {' '.join(str(n) for n, _ in fautes)}")
        return 0

    if a.planche:
        # Avec --n : ces diapositives seulement, dans planche-choix-NN.jpg.
        for s in planche(d['slug'], d, cache, ns=a.n):
            print(s.relative_to(c.RACINE))
        return 0

    a_faire = []
    for x in d['diapositives']:
        if x.get('camera_manuelle'):
            continue
        cles = empreintes_valides(x, d['slug'])
        if a.n is not None:
            if x['n'] in a.n:
                a_faire.append(x)
        elif a.tenues:
            if tenue_max(x) > TENUE_MAX and (a.force or cache.get(str(x['n']), {}).get('empreinte') != empreinte(x)):
                a_faire.append(x)
        elif a.force or not x['image'].get('camera') or cache.get(str(x['n']), {}).get('empreinte') not in cles:
            # Réponse déjà en cache pour ce texte et cette image : on la remet sans appel.
            e = cache.get(str(x['n']))
            if not a.force and e and e.get('empreinte') in cles and e.get('camera'):
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
                                for m, e in zip(r['montre'] + [''] * MAX_ETAPES, r['camera']))
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
