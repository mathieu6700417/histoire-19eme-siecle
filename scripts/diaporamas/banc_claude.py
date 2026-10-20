"""Caméra proposée par des sous-agents Claude, sans API externe : banc d'essai et production (spec 12).

Pendant de banc_gemini.py (tâche `camera`) et de la passe de camera.py : au lieu d'appeler Gemini,
on écrit pour chaque image un fichier de tâche qu'un agent Claude lit (avec l'image, par son outil
Read) et auquel il répond par un fichier JSON ; ce script note ces réponses avec les contrôles de
camera.py puis, en production, pose les meilleures dans le JSON de la période. Aucun appel payant
(l'appel Gemini de camera.py est neutralisé). `preparer`, `noter`, `relire` et `factice` n'écrivent
que dans .cache/diaporamas/banc-claude/<horodatage>/ ; seuls `appliquer` et `restaurer` (sans
--essai) écrivent dans le JSON de la période et dans le cache .cache/diaporamas/<slug>/camera.json.

Usage (banc) :
    python3 scripts/diaporamas/banc_claude.py preparer camera consulat-empire      # 10 tâches
    python3 scripts/diaporamas/banc_claude.py noter <dossier> [--etiquette haiku]
Usage (production) :
    python3 scripts/diaporamas/banc_claude.py preparer <slug> --toutes --etiquette sonnet     # période neuve
    python3 scripts/diaporamas/banc_claude.py preparer restauration --statiques --etiquette sonnet
    python3 scripts/diaporamas/banc_claude.py preparer restauration --n 12 100 100b --etiquette sonnet
    python3 scripts/diaporamas/banc_claude.py relire <dossier>/lot-2      # second tour d'un lot (ou du dossier)
    python3 scripts/diaporamas/banc_claude.py noter <dossier>             # tableau, planches
    python3 scripts/diaporamas/banc_claude.py appliquer <dossier> --essai # ce qui changerait
    python3 scripts/diaporamas/banc_claude.py appliquer <dossier>         # écrit (sauvegarde gardée)
    python3 scripts/diaporamas/banc_claude.py restaurer <dossier>         # remet les caméras remplacées
    python3 scripts/diaporamas/banc_claude.py factice <dossier>           # réponses d'essai du circuit

Fichiers du dossier (à la racine, ou dans lot-K/ quand les tâches sont découpées en lots) :
- LISEZMOI.md : marche à suivre de l'agent répondant (un par lot) ; taches.json (racine) : vues
  figées (texte, image, visages, caméra du JSON à ce moment), pour noter à l'identique plus tard ;
- tache-NNN.md (tache-NNNb.md pour un plan de la spec 14) : consignes de camera.py (CONSIGNES, mot
  pour mot), texte de la vue tel que `cadrer` l'envoie (`texte_diapo`), instant de chaque mot,
  géométrie des vues et rappel sur les visages, format de réponse (celui de SCHEMA), chemin de l'image ;
- image-NNN.jpg : l'image telle que Gemini la reçoit (1024 px au plus, grille graduée, JPEG 85) ;
- reponse-NNN.<etiquette>.json (ou reponse-NNN.json, nommée par --etiquette) : les réponses ;
  plusieurs étiquettes peuvent cohabiter (deux modèles comparés) ;
- retour-NNN.<etiquette>.md, relecture-*.jpg, tours/ : second tour (`relire`) ;
- comparatif.md / .json, planche[-NN].jpg : écrits par `noter` ; sauvegarde-*.json : par `appliquer`.

Décisions :
- Vues : celles de `commun.vues_camera` (une diapositive sans plans, ou chaque image d'une
  diapositive à plans avec la narration et le minutage de sa fenêtre), comme camera.py. Les images
  sans narration (lectures, galeries) restent à camera.py (cadre local).
- Sélection : --n (« 100 » : la diapositive et ses plans ; « 100b » : ce plan) ; --toutes : toutes
  les vues narrées (période neuve, après utile.py et surimpressions.py) ; --statiques : vues sans
  caméra ou dont la caméra actuelle tient un cadre plus de TENUE_MAX s (c'est le cas de toute caméra à une
  étape sur une fenêtre de plus de 7 s ; une étape sur une fenêtre plus courte n'a rien à gagner),
  hors `camera_manuelle`, plans sans `instant`, avant/après et mosaïques ; sans option : les
  diapositives du dernier banc Gemini caméra, plus AUTRES (banc).
- Entrée en scène (spec 12, « Entrée en scène des grandes vues ») : la tâche d'une image qui peut en
  recevoir une (entree.motif_image : ni portrait, ni document, ni ouverture, ni avant/après, ni
  mosaïque, ni clip, ni première image d'un acte) demande en plus le champ `entree` (consigne
  d'entree.consigne_banc, avec la règle de fenêtre) ; `appliquer` le pose avec la caméra s'il passe
  entree.depuis_camera. Contrôle après build : `entree.py plans` puis `entree.py etapes`.
- Vue réelle (bilan de la période 05) : la tâche dit ce que l'écran montrera pour un cadre de cette
  image (hauteur maximale utile, bande, coupe par le haut, haut repoussé sous le cartouche, zoom
  lent de 12 %), avec des exemples calculés par camera.vue_reelle et camera.vue_zoomee.
- Images entières : avec --toutes ou --statiques, pas de tâche pour une image qui est ou passera en
  image entière (`image.entier`, ou règle de `camera.py --entiers` : `camera.entier_propose`) ; leur
  caméra n'est pas jouée, `appliquer` pose à celles qui n'en ont pas une étape sur la zone utile
  (exigée par verifier.py). --avec-entieres garde ces tâches (leur dernier cadre sert alors de
  `entier_vers`) ; --n les garde toujours.
- Réponse « image entière » : pour un groupe de visages serrés qu'aucune vue ne montre sans couper
  une tête, la tâche admet `{"entier": true, "vers": [x0, y0, x1, y1] ou null, "raison": "…"}` au lieu
  des étapes ; `appliquer` pose alors `entier`, `entier_manuel`, `entier_vers` et `entier_zoom` comme
  la correction à la main du README (« Images entières sur fond noir »). Un cadre qui ne montre pas
  le sujet (détail de col, bande sans visage, marge) est pire qu'un repli.
- Lots d'environ 15 tâches (--lot) dès qu'il y en a plus, ou avec --statiques / --toutes : un sous-agent par lot.
- Minutage mot à mot : les narrations n'ont que `audio.phrases` (pas d'alignement par mot) ; la
  tâche donne donc l'instant de chaque mot tel que la chaîne le calcule (prorata des caractères
  dans la phrase horodatée, `camera.instants`) : c'est celui qu'emploient le contrôle et le lecteur.
- Visages : ceux de `camera.visages` (relevé Gemini en cache complété de la détection locale) ; la
  détection locale manquante est faite en mémoire (YuNet, gratuit), sans écrire dans les caches.
- Même traitement qu'une réponse de Gemini, tours en moins : `controler` ; s'il refuse, pas de
  renvoi au modèle mais la réparation géométrique de `camera.py --reparer` ; à défaut, le repli de
  `cadrer` (une étape). `relire` rapproche du dialogue de `cadrer` : retour-NNN.md par réponse
  (erreurs à corriger, sinon relance des tenues longues et relecture des cadres dessinés).
- Mesure = celle de banc_gemini.py (erreurs_vues + ignorees + tete_hors_champ sur la caméra rendue,
  repli), plus les refus du contrôle au premier jet, les étapes proposées et gardées, la tenue.
- `appliquer` ne pose qu'une caméra acceptée ou réparée, sans erreur ni repli, d'au moins autant
  d'étapes que l'actuelle et différente d'elle (--strict : plus d'étapes ou tenue plus courte), sur
  une vue inchangée depuis la préparation (narration, image, zone utile) et non manuelle. Écriture
  par `camera.ecrire_cameras` (relecture du JSON et fusion sous verrou de `commun.ecrire`).
- Provenance et protection : l'entrée de la vue dans .cache/diaporamas/<slug>/camera.json est
  remplacée (empreinte actuelle, caméra, `source` « claude:<etiquette> ») ; camera.py ne recadre
  une vue que si elle n'a pas de caméra ou si l'empreinte du cache n'est plus valide (narration,
  image ou consignes changées), et remet la caméra du cache quand elle manque : la caméra de Claude
  n'est donc pas refaite à la passe suivante. Elle le serait par `camera.py --force` (comme toute
  caméra non manuelle) ; à lancer quand aucun camera.py ne tourne sur la période (il réécrit son
  cache en entier).
"""
import argparse, copy, json, math, re, subprocess, sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

import commun as c
import camera as cam
import entree as ent
import gemini

DOSSIER = c.CACHE / 'banc-claude'
TAILLE_LOT = 15
# Banc : diapositives ajoutées à celles du banc Gemini, et nature de chacune (pour le tableau).
AUTRES = {'consulat-empire': [52, 41, 34, 92, 30]}
NATURES = {'consulat-empire': {
    1: 'portrait en pied, tableau en hauteur', 23: 'portrait gravé', 45: 'estampe coloriée, scène',
    67: 'portrait gravé', 89: 'tableau, scène', 52: 'portrait peint', 41: 'scène de foule',
    34: 'estampe à marges (caricature)', 92: 'carte', 30: 'grand tableau (foule)'}}
FORMAT = """\
{"etapes": [
  {"quand": null, "montre": "ce que montre le cadre de départ", "cadre": [x0, y0, x1, y1]},
  {"quand": "passage exact de la narration", "montre": "…", "cadre": [x0, y0, x1, y1]}
 ],
 "non_identifies": []}"""


# Tâche d'une grande vue (image qui peut recevoir une entrée en scène : entree.motif_image) : la
# réponse porte en plus le champ `entree`, posé par `appliquer` s'il passe les contrôles d'entree.py.
FORMAT_ENTREE = FORMAT[:-1] + """,
 "entree": {"cadres": [[x0, y0, x1, y1]], "duree": 5, "intention": "le mouvement, en une phrase"}}"""


# Réponse « image entière » (groupe de visages serrés qu'aucune vue ne montre sans couper une tête).
FORMAT_ENTIER = '{"entier": true, "vers": [x0, y0, x1, y1], "raison": "pourquoi aucune vue ne convient, en une phrase"}'
CLES_ENTIER = ('entier', 'entier_vers', 'entier_zoom', 'entier_manuel')


# --- Sans effet de bord -----------------------------------------------------------------------

def _interdit(*_, **__):
    raise cam.ErreurCamera('banc_claude.py : aucun appel Gemini (0 $).')


def neutraliser(slug: str | None = None, vues: list[dict] | None = None) -> int:
    """camera.py sans appel payant ni écriture dans ses caches. Avec `vues` : les visages locaux qui
    manquent sont détectés (YuNet, gratuit) et gardés en mémoire ; rend leur nombre."""
    cam.appel = _interdit
    cam.preparer_visages_locaux = lambda s, xs: 0
    if slug is None:
        return 0
    f, cache = cam._visages_locaux_cache(slug)
    cache = dict(cache)
    cam._visages_locaux_cache = lambda s: (f, cache)
    script = str(Path(__file__).resolve().parent / 'visages_local.py')

    def detecter(entree) -> list:
        if not cam.VENV_VISAGES.exists():
            return []
        r = subprocess.run([str(cam.VENV_VISAGES), script], input=json.dumps(entree), capture_output=True, text=True)
        return json.loads(r.stdout) if not r.returncode else []

    def portrait(s: str, x: dict) -> list:
        cle = 'portrait:' + cam.empreinte_image(s, x)
        if cle not in cache:
            cache[cle] = (detecter({'portrait': True, 'chemins': [str(c.PUBLIC / s / x['image']['fichier'])]}) or [[]])[0]
        return cache[cle]
    cam.visage_portrait_local = portrait
    manque = {}
    for x in vues or []:
        cle = cam.empreinte_image(slug, x)
        if cle not in cache:
            manque[cle] = str(c.PUBLIC / slug / x['image']['fichier'])
    if manque and cam.SOURCE_VISAGES != 'gemini':
        trouves = detecter(list(manque.values()))
        if len(trouves) != len(manque):
            print(f'ATTENTION : détection locale des visages en échec pour {len(manque)} image(s) : listes vides.')
        cache.update(zip(manque, trouves))
    return len(manque)


def figer_visages(taches: list[dict]) -> None:
    """Les contrôles et réparations de camera.py lisent les visages figés à la préparation."""
    par_n = {str(t['x']['n']): t['visages'] for t in taches}
    cam.visages = lambda slug, x, appeler=True: par_n.get(str(x['n']), [])


def nom(n) -> str:
    m = re.fullmatch(r'(\d+)([a-z]?)', str(n))
    return f'{int(m[1]):03d}{m[2]}' if m else str(n)


def rel(p: Path) -> Path:
    return p.relative_to(c.RACINE) if p.is_relative_to(c.RACINE) else p


def periode(slug: str) -> dict:
    return json.loads(c.fichier_periode(slug).read_text())


def vues_narrees(d: dict) -> list[dict]:
    return [v for v in c.vues_camera(d, series=False)
            if (v.get('image') or {}).get('fichier') and (c.PUBLIC / d['slug'] / v['image']['fichier']).exists()]


# --- Banc Gemini de référence -----------------------------------------------------------------

def dernier_banc(slug: str) -> tuple[Path | None, list[dict]]:
    fs = sorted((c.CACHE / 'banc').glob(f'camera-{slug}-*.json'))
    return (fs[-1], json.loads(fs[-1].read_text())) if fs else (None, [])


def reference(mesures: list[dict], voulu: str | None) -> str | None:
    """Réglage Gemini comparé : celui demandé, sinon celui de production, sinon le meilleur."""
    bilan = {}
    for m in mesures:
        if 'resultat' in m:
            b = bilan.setdefault(m['reglage'], [0, 0])
            b[0] += m.get('erreurs', 0)
            b[1] += bool(m.get('repli'))
    if not bilan:
        return None
    prod = f"{gemini.modele('camera')} r{gemini.reflexion('camera')}"
    for r in (voulu, prod):
        if r in bilan:
            return r
    return min(bilan, key=lambda r: (bilan[r][1], bilan[r][0]))


# --- Préparer ---------------------------------------------------------------------------------

def statique(v: dict, d: dict, toutes: bool = False) -> bool:
    """Vue à cadrer : sans caméra, ou caméra qui tient un cadre plus de TENUE_MAX s (`toutes` : quelle
    que soit sa caméra), hors cas laissés tels quels."""
    parent = next(x for x in d['diapositives'] if x['n'] == v.get('diapositive', v['n']))
    if v.get('camera_manuelle') or v.get('sans_instant') or not v.get('narration'):
        return False
    if v['image'].get('apres') or (parent.get('mosaique') and v['image'] is parent['image']):
        return False
    return toutes or not v['image'].get('camera') or cam.tenue_max(v) > cam.TENUE_MAX


def hauteur_max(x: dict, L: int, H: int) -> float:
    """Hauteur maximale utile d'une vue (fraction de la hauteur de l'image), comme camera.vue_reelle."""
    u = cam.utile_de(x)
    return min((u[2] - u[0]) * L / cam.RATIO_VUE, (u[3] - u[1]) * H / (1 + cam.BANDE_HAUT + cam.BANDE_BAS)) / H


def passe_entiere(slug: str, x: dict) -> str | None:
    """Raison pour laquelle la vue est ou passera en image entière (`camera.py --entiers`), sinon None."""
    im = x['image']
    if im.get('entier_manuel'):
        return 'image entière (réglage manuel)' if im.get('entier') else None
    if im.get('entier'):
        return 'image entière'
    r = cam.entier_propose(slug, x) if im.get('largeur') else None
    return r['raison'] if r else None


def _dedans(k: list[float], v: list[float]) -> bool:
    i = max(0, min(k[2], v[2]) - max(k[0], v[0])) * max(0, min(k[3], v[3]) - max(k[1], v[1]))
    return i >= cam.FACE_DEDANS * (k[2] - k[0]) * (k[3] - k[1])


def groupe_serre(x: dict, L: int, H: int, faces: list) -> tuple[int, int] | None:
    """Groupe de visages serrés : (visages nets, nombre qu'une vue montre au plus sans en couper aucun,
    au début de la tenue et au bout du zoom lent) quand aucune vue n'en montre la moitié, ou plus d'un ;
    sinon None (personne seule, moins de deux visages nets, groupe montrable). Balayage de la zone
    utile à trois hauteurs de vue."""
    nets = [k for k in faces if k[3] - k[1] >= cam.FACE_ENTIER and (k[2] - k[0]) <= 3 * (k[3] - k[1])]
    if len(nets) < 2 or cam.personne_seule(faces, x) is not None:
        return None
    u, hmax, k = cam.utile_de(x), hauteur_max(x, L, H), cam.RATIO_VUE * H / L
    pas, mieux = 24, 0
    for part in (1.0, 0.8, 0.6):
        vh = hmax * part
        vw = vh * k
        if vw * L < cam.MIN_FRACTION * max(L, H) and part < 1:
            continue
        for i in range(pas + 1):
            for j in range(pas + 1):
                x0 = u[0] + (u[2] - u[0] - vw) * i / pas
                y0 = u[1] + (u[3] - u[1] - vh) * j / pas
                cadre = [x0, y0, x0 + vw, y0 + vh]
                v = cam.vue_reelle(cadre, L, H, u)
                z = cam.vue_zoomee(v, cam.dans_utile(cadre, u))
                if not (cam.visages_coupes(v, faces) or cam.visages_coupes(z, faces)):
                    mieux = max(mieux, sum(_dedans(n, v) and _dedans(n, z) for n in nets))
    return (len(nets), mieux) if mieux <= 1 or 2 * mieux < len(nets) else None


def _r(v: list[float]) -> str:
    return f'x {v[0]:.2f}-{v[2]:.2f}, y {v[1]:.2f}-{v[3]:.2f}'


def vue_reelle_tache(x: dict, L: int, H: int, faces: list) -> str:
    """Section « Vue réelle » d'une tâche : la règle du lecteur avec les nombres de cette image, et
    des exemples calculés par la chaîne (vue au début de la tenue, vue au bout du zoom lent)."""
    u, hmax, k = cam.utile_de(x), hauteur_max(x, L, H), cam.RATIO_VUE * H / L
    serre = 1 - 1 / cam.ZOOM_TENUE
    exemples = [('toute la partie montrable', list(u))]
    cx = (u[0] + u[2]) / 2
    exemples.append(('cadre haut et étroit au milieu', [cx - 0.15 * (u[2] - u[0]), u[1], cx + 0.15 * (u[2] - u[0]), u[3]]))
    grands = sorted((f for f in faces if f[3] - f[1] >= cam.FACE_MIN), key=lambda f: f[1] - f[3])
    if grands:
        g = grands[0]       # bande aux proportions de la vue, de taille admise, la tête dans son tiers haut
        w = min(u[2] - u[0], max(2.2 * (g[2] - g[0]), 0.36 * max(L, H) / L, 2.4 * (g[3] - g[1]) * k))
        h, gx, gy = min(w / k, hmax), (g[0] + g[2]) / 2, (g[1] + g[3]) / 2
        exemples.append(('bande serrée sur le plus grand visage', cam.dans_utile([gx - w / 2, gy - 0.4 * h, gx + w / 2, gy + 0.6 * h], u)))
    lignes = []
    for titre, cadre in exemples:
        cadre = [round(v, 2) for v in cadre]
        v = cam.vue_reelle(cadre, L, H, u)
        z = cam.vue_zoomee(v, cam.dans_utile(cadre, u))
        _, ch = cam.couverture(cadre, v, u)
        coupes = len(cam.visages_coupes(v, faces) or cam.visages_coupes(z, faces))
        lignes.append(f'- {titre}, cadre {cadre} → vue {_r(v)} ({ch:.0%} de la hauteur du cadre) ; au bout du '
                      f'zoom lent : {_r(z)} ; ' + (f'{coupes} visage(s) coupé(s) : refusé' if coupes else 'aucun visage coupé'))
    return (
        f'## Vue réelle : ce que l\'écran montrera pour un cadre\n\n'
        f'Tu proposes des CADRES ; l\'écran montre une VUE, une bande panoramique. Pour cette image, un cadre de '
        f'largeur w et de hauteur h (fractions de l\'image) donne la vue suivante :\n\n'
        f'1. le cadre est ramené dans la partie montrable ({_r(u)}) ;\n'
        f'2. hauteur de la vue : vh = min(max(h, w / {k:.2f}), {hmax:.2f}). **Hauteur maximale utile : {hmax:.2f}** '
        f'de la hauteur de l\'image : ce qu\'un cadre a de plus haut est perdu ;\n'
        f'3. largeur de la vue : vw = vh × {k:.2f} (au plus {hmax * k:.2f}), centrée sur le cadre sans sortir de la '
        f'partie montrable : la vue est souvent PLUS LARGE que le cadre ;\n'
        f'4. si h ≤ vh, la vue est centrée en hauteur sur le cadre ; sinon elle part du BORD SUPÉRIEUR du cadre et '
        f'LE BAS EST COUPÉ (deux cadres trop hauts de même sommet donnent la même vue : la seconde étape est ignorée) ;\n'
        f'5. haut repoussé sous le cartouche : la vue ne commence jamais au-dessus de y = {u[1]:.2f} + '
        f'{cam.BANDE_HAUT} × vh et ne finit jamais au-dessous de y = {u[3]:.2f} − {cam.BANDE_BAS} × vh. Une vue de '
        f'hauteur maximale couvre donc au plus y {u[1] + cam.BANDE_HAUT * hmax:.2f}-{u[3] - cam.BANDE_BAS * hmax:.2f} ; '
        f'ce qui est plus haut ou plus bas ne se montre que par une vue moins haute ;\n'
        f'6. pendant la tenue, zoom lent de {(cam.ZOOM_TENUE - 1) * 100:.0f} % : la vue finit à vw / {cam.ZOOM_TENUE} sur '
        f'vh / {cam.ZOOM_TENUE} (elle perd jusqu\'à {serre * 50:.1f} % de sa taille sur chaque bord), en glissant vers le '
        f'centre de ton cadre. Les contrôles portent sur la vue du début ET sur cette vue resserrée.\n\n'
        f'Exemples calculés par la chaîne pour cette image (ne les recopie pas, sers-t\'en pour vérifier ton calcul) :\n'
        + '\n'.join(lignes) + '\n\n')


def entier_tache(x: dict, L: int, H: int, faces: list) -> str:
    """Section d'une tâche qui admet la réponse « image entière » (bilan de la période 05 : cadres
    d'évitement rendus pour satisfaire le contrôle des visages)."""
    g = groupe_serre(x, L, H, faces)
    office = (f'**Calcul de la chaîne pour cette image : des {g[0]} visages nets (hauteur d\'au moins {cam.FACE_ENTIER}), '
              f'aucune vue n\'en montre plus de {g[1]} sans en couper un.** Si le sujet dont parle la voix est ce groupe, '
              f'la réponse « image entière » est ici la réponse attendue ; propose une caméra seulement si la narration '
              f'désigne un sujet qu\'un cadre montre vraiment (une figure isolée, un objet, une inscription, un décor).\n\n'
              if g else '')
    return (
        f'## Si aucun cadre ne montre le sujet : réponse « image entière »\n\n'
        f'Un cadre qui ne montre pas le sujet est pire qu\'un repli. Si le sujet est un groupe de visages serrés '
        f'(ou une tête plus haute que la vue) qu\'aucune vue ne peut montrer sans couper une tête, ne rends PAS un '
        f'cadre d\'évitement pour satisfaire le contrôle des visages (détail de col ou de vêtement, bande sans '
        f'visage, marge, ciel, fond) : réponds que l\'image doit être montrée en entier, sur fond noir, par cet objet '
        f'à la place de celui des étapes :\n\n```json\n{FORMAT_ENTIER}\n```\n\n'
        f'- `vers` : le sujet dont l\'image entière s\'approchera lentement (le groupe, la tête principale), en '
        f'fractions de l\'image, ou null (centre) ; ni `etapes` ni `entree` dans cette réponse ;\n'
        f'- réservé à ce cas : si un cadre montre vraiment le sujet dont parle la voix, propose la caméra.\n\n'
        + office)


def minutage_mots(x: dict) -> str:
    """Instant de chaque mot, comme `camera.instants` le calcule (prorata dans la phrase horodatée)."""
    texte, lignes = x['narration'], []
    for j, (d, f, t0, t1) in enumerate(cam.phrases_horodatees(x), 1):
        mots = [f"[{t0 + (m.start()) / max(1, f - d) * (t1 - t0):.1f}] {m.group()}" for m in re.finditer(r'\S+', texte[d:f])]
        lignes.append(f'{j}. ' + ' '.join(mots))
    return '\n'.join(lignes)


def texte_tache(slug: str, x: dict, L: int, H: int, faces: list, img: Path, reponse: Path, entree: bool = False) -> str:
    hmax = hauteur_max(x, L, H)
    k = cam.RATIO_VUE * H / L
    controles = [f for f in faces if f[3] - f[1] >= cam.FACE_MIN]
    plan = ''
    if x.get('fenetre'):
        t0, t1 = x['fenetre']['t']
        plan = (f"Cette image est l'une des images de la diapositive {x['diapositive']} : elle n'est à l'écran que de "
                f"{t0 or 0:.1f} s à {t1 if t1 is not None else 0:.1f} s de la voix. La narration ci-dessus est celle dite "
                f"pendant qu'elle est visible, et tous les instants sont comptés depuis son apparition.\n\n")
    return (
        f"# Tâche {nom(x['n'])} : caméra de la vue {x['n']} ({slug})\n\n"
        f'## Consignes\n\n{cam.CONSIGNES}\n\n'
        f'## Diapositive\n\n{cam.texte_diapo(x, L, H, faces)}\n\n{plan}'
        f'## Instant de chaque mot (secondes, tel que la chaîne le calcule)\n\n{minutage_mots(x)}\n\n'
        f"Le premier mot d'un `quand` doit avoir un instant d'au moins {cam.ECART_MIN_S:.1f} s, et d'au moins "
        f"{cam.ECART_MIN_S:.0f} s de plus que celui du `quand` précédent ; sinon l'étape est refusée. La caméra "
        f"ne devrait pas tenir un même cadre plus de {cam.TENUE_MAX:.0f} s si la voix désigne autre chose de visible.\n\n"
        + vue_reelle_tache(x, L, H, faces) +
        f'## Le piège des visages\n\n'
        f"Ce sont les bords de la VUE, non ceux du cadre, qui ne doivent couper aucun visage. "
        f"Cause la plus fréquente de refus : un petit visage de foule coupé par un bord de la vue. Des "
        f"{len(faces)} rectangle(s) de visages donnés plus haut, {len(controles)} sont contrôlés (hauteur d'au "
        f"moins {cam.FACE_MIN}) : chacun doit être ENTIER dans la vue, ou FRANCHEMENT à l'écart (ni à cheval sur "
        f"un bord, ni au ras). Avant d'écrire, calcule la vue de chaque cadre et compare ses quatre bords aux "
        f"rectangles ; au besoin élargis le cadre pour englober le visage voisin, ou écarte-le nettement.\n\n"
        + entier_tache(x, L, H, faces) + (f'## Entrée en scène (spec 12, « Entrée en scène des grandes vues »)\n\n{ent.consigne_banc(hmax, k)}\n\n' if entree else '') +
        f'## Image à regarder (outil Read)\n\n{img}\n\n'
        f'Elle porte la grille graduée de 0 à 1 ; les cadres et les visages sont en fractions de cette image.\n\n'
        f'## Réponse attendue\n\n'
        f'Un objet JSON, et rien d\'autre, écrit dans `{reponse}` :\n\n'
        f'```json\n{FORMAT_ENTREE if entree else FORMAT}\n```\n\n'
        f'(ou, dans le seul cas décrit plus haut, l\'objet de la réponse « image entière » à sa place.)\n\n'
        + ('- `entree` : null si l\'image ne se prête pas à une entrée en scène, sinon `cadres` (un ou deux cadres '
           'de départ), `duree` (4 à 7 s) et `intention` (une phrase) ;\n' if entree else '') +
        f'- `etapes` : 1 à {cam.MAX_ETAPES} ; `quand` vaut null pour la première, un passage exact de la '
        f'narration (2 à 8 mots) pour les suivantes ;\n'
        f'- `cadre` : quatre nombres entre 0 et 1, x0 < x1 et y0 < y1 ;\n'
        f'- `non_identifies` : personnes nommées par la voix que l\'image ne permet pas de situer (liste, '
        f'vide le plus souvent).\n')


def lisezmoi(slug: str, rep: Path, ids: list[str], suffixe: str) -> str:
    return f"""\
# Caméra d'un diaporama proposée par Claude

Tu règles la caméra de {len(ids)} images d'un diaporama narré sur l'histoire de France
(période « {slug} »). Une tâche par image, chacune indépendante des autres.

## Marche à suivre

Pour chaque fichier `tache-NNN.md` de ce dossier ({', '.join(ids)}) :

1. Lis `tache-NNN.md` en entier : consignes, texte de la diapositive (zone utile, hauteur maximale
   d'une vue, visages, narration, minutage, instant de chaque mot), géométrie des vues, format de réponse.
2. Regarde l'image `image-NNN.jpg` avec l'outil Read (chemin absolu dans la tâche). Lis les
   coordonnées sur sa grille graduée (0 à 1, origine en haut à gauche).
3. Écris ta réponse dans `reponse-NNN{suffixe}.json`, dans ce dossier (chemin exact dans la tâche) :
   l'objet JSON demandé, seul, sans texte ni balise autour.

## Règles

- Une réponse par fichier, une seule version : pas de brouillon, pas d'autre fichier.
- Ne lance aucun script, ne modifie ni les tâches ni les images, n'écris rien hors de ce dossier.
- Chaque `quand` est recopié caractère pour caractère de la narration (apostrophes et accents
  compris) ; la première étape a `quand` à null.
- Cherche les mouvements que la voix justifie : quand elle nomme ou décrit un élément visible
  assez tard (voir l'instant de chaque mot), une étape de plus vaut mieux qu'un cadre tenu
  pendant toute la narration. Jamais d'étape sans lien avec ce que dit la voix.
- Vérifie chaque cadre contre la hauteur maximale d'une vue et contre les rectangles des visages
  donnés dans la tâche avant d'écrire (la vue est souvent plus large que le cadre) : la section
  « Vue réelle » de la tâche donne le calcul avec les nombres de l'image et des exemples.
- Un cadre qui ne montre pas le sujet est pire qu'un repli : jamais de cadre d'évitement (détail de
  col, bande sans visage, marge, ciel) pour passer le contrôle des visages. Si aucune vue ne peut
  montrer un groupe de visages serrés sans couper une tête, rends la réponse « image entière »
  décrite dans la tâche (`{{"entier": true, "vers": …, "raison": "…"}}`), au premier comme au second tour.
- Si un fichier `retour-NNN{suffixe}.md` existe, c'est un second tour : lis-le, regarde l'image de
  relecture qu'il cite, puis réécris la réponse correspondante.

Dossier : {rep}
"""


def preparer(a) -> int:
    slug_demande = a.cible[-1]
    d = periode(slug_demande)
    slug = d['slug']
    vues = vues_narrees(d)
    banc_f, mesures = dernier_banc(slug)
    communes = list(dict.fromkeys(str(m['n']) for m in mesures))
    if a.n:
        choix = [v for v in vues if cam.demande(v, a.n)]
    elif a.statiques or a.toutes:
        choix = [v for v in vues if statique(v, d, a.toutes)]
    else:
        ns = communes + [str(n) for n in AUTRES.get(slug, []) if str(n) not in communes]
        choix = sorted((v for v in vues if str(v['n']) in ns), key=lambda v: ns.index(str(v['n'])))
    nb = neutraliser(slug, choix)
    if nb:
        print(f'Visages locaux détectés en mémoire pour {nb} image(s) (YuNet, gratuit, cache non écrit).')
    # Pas de tâche pour une image qui est ou passera en image entière (sa caméra n'est pas jouée).
    entieres = []
    if (a.statiques or a.toutes) and not a.avec_entieres:
        raisons = {str(v['n']): passe_entiere(slug, v) for v in choix}
        entieres = [{'n': v['n'], 'raison': raisons[str(v['n'])]} for v in choix if raisons[str(v['n'])]]
        choix = [v for v in choix if not raisons[str(v['n'])]]
        if entieres:
            print(f"{len(entieres)} image(s) entière(s) sans tâche (--avec-entieres pour les garder) : "
                  f"{' '.join(str(e['n']) for e in entieres)}")
    if not choix:
        raise SystemExit(f'Aucune vue à préparer pour « {slug} » (--n, --statiques, --toutes, ou un banc Gemini caméra).')
    sortie = DOSSIER / f'{datetime.now():%Y%m%d-%H%M}'
    if sortie.exists():                 # deux préparations dans la même minute : jamais le même dossier
        sortie = DOSSIER / f'{datetime.now():%Y%m%d-%H%M%S}'
    sortie.mkdir(parents=True)
    par_lots = a.statiques or a.toutes or len(choix) > a.lot
    nb_lots = math.ceil(len(choix) / a.lot) if par_lots else 1
    taille = math.ceil(len(choix) / nb_lots)
    suffixe = f'.{a.etiquette}' if a.etiquette else ''
    taches, actes = [], ent.debuts_actes(d)
    for i, x in enumerate(choix):
        lot = f'lot-{i // taille + 1}' if par_lots else None
        rep = sortie / lot if lot else sortie
        rep.mkdir(exist_ok=True)
        ident = nom(x['n'])
        image = cam.image_de(slug, x)
        L, H = image.size
        faces = cam.visages(slug, x, appeler=False) or []
        img = rep / f'image-{ident}.jpg'
        cam.avec_grille(cam.reduire(image)).save(img, 'JPEG', quality=85)
        grande_vue = ent.motif_image(d, x, actes) is None
        (rep / f'tache-{ident}.md').write_text(
            texte_tache(slug, x, L, H, faces, img, rep / f'reponse-{ident}{suffixe}.json', grande_vue))
        fige = {k: v for k, v in x.items() if k != 'plan'}
        taches.append({'id': ident, 'n': x['n'], 'lot': lot, 'commune': str(x['n']) in communes, 'visages': faces, 'entree': grande_vue,
                       'nature': NATURES.get(slug, {}).get(x['n']) or (x['image'].get('technique') or '?'), 'x': fige})
    for lot in dict.fromkeys(t['lot'] for t in taches):
        rep = sortie / lot if lot else sortie
        (rep / 'LISEZMOI.md').write_text(lisezmoi(slug, rep, [t['id'] for t in taches if t['lot'] == lot], suffixe))
    (sortie / 'taches.json').write_text(json.dumps(
        {'slug': slug, 'tache': 'camera', 'prepare': f'{datetime.now():%Y-%m-%d %H:%M}', 'consignes': cam.VERSION,
         'etiquette': a.etiquette, 'banc_gemini': str(banc_f.relative_to(c.RACINE)) if banc_f and not (a.n or a.statiques or a.toutes) else None,
         'entieres': entieres, 'taches': taches}, ensure_ascii=False, indent=1))
    lots = [f"{lot} ({sum(t['lot'] == lot for t in taches)})" for lot in dict.fromkeys(t['lot'] for t in taches) if lot]
    print(f"{len(taches)} tâche(s) dans {rel(sortie)}" + (f" : {', '.join(lots)}" if lots else
          f" : {' '.join(t['id'] for t in taches)}") + f" ; {sum(len(t['x']['image'].get('camera') or []) for t in taches)} "
          f"étape(s) actuelles.")
    return 0


# --- Réponses ---------------------------------------------------------------------------------

def charger(chemin: str) -> tuple[Path, dict, list[dict]]:
    """(racine, manifeste, tâches visées) ; `chemin` est le dossier d'un banc ou l'un de ses lots."""
    dossier = Path(chemin).resolve()
    lot = None
    if not (dossier / 'taches.json').exists() and (dossier.parent / 'taches.json').exists():
        dossier, lot = dossier.parent, dossier.name
    if not (dossier / 'taches.json').exists():
        raise SystemExit(f'{dossier}/taches.json introuvable : lancer `preparer` d\'abord.')
    m = json.loads((dossier / 'taches.json').read_text())
    for t in m['taches']:
        t.setdefault('id', nom(t['n']))
        t.setdefault('lot', None)
    figer_visages(m['taches'])
    return dossier, m, [t for t in m['taches'] if lot is None or t['lot'] == lot]


def rep_de(racine: Path, t: dict) -> Path:
    return racine / t['lot'] if t.get('lot') else racine


def reponses(racine: Path, taches: list[dict], etiquette: str) -> dict[str, dict[str, Path]]:
    """{étiquette: {id de tâche: fichier}} ; reponse-NNN.json prend l'étiquette de la commande."""
    sortie: dict[str, dict[str, Path]] = {}
    for t in taches:
        for f in sorted(rep_de(racine, t).glob(f"reponse-{t['id']}*.json")):
            m = re.fullmatch(rf"reponse-{t['id']}(?:\.([^.]+))?\.json", f.name)
            if m:
                sortie.setdefault(m.group(1) or etiquette, {})[t['id']] = f
    return sortie


def lire_reponse(f: Path) -> tuple[dict, str | None]:
    """Objet JSON de la réponse (tolère du texte ou des balises autour, signalés)."""
    texte = f.read_text().strip()
    try:
        r, note = json.loads(texte), None
    except json.JSONDecodeError:
        a, b = texte.find('{'), texte.rfind('}')
        try:
            r, note = json.loads(texte[a:b + 1]), 'texte autour du JSON'
        except json.JSONDecodeError as e:
            return {}, f'JSON illisible ({e.msg})'
    return (r, note) if isinstance(r, dict) else ({}, 'la réponse n\'est pas un objet')


def mesure_banc(slug: str, x: dict, etapes: list[dict], faces: list) -> list[str]:
    """Les erreurs comptées par banc_gemini.py sur une caméra rendue."""
    L, H = cam.dims(x)
    return (cam.erreurs_vues(x, etapes, L, H, cam.image_de(slug, x), faces)
            + cam.ignorees(x, etapes, L, H) + cam.tete_hors_champ(x, etapes, L, H, faces))


def camera_utile(x: dict) -> list[dict]:
    """Caméra d'une image entière (exigée par verifier.py, non jouée) : une étape sur la zone utile."""
    return [{'cadre': [round(v, 3) for v in cam.utile_de(x)]}]


def reponse_entiere(slug: str, t: dict, rendu: dict) -> dict:
    """Réponse « image entière » : réglage calculé comme `camera.py --entiers` (zoom le plus fort qui
    garde les visages nets entiers), le sujet étant celui que donne l'agent (`vers`)."""
    x = copy.deepcopy(t['x'])
    vers, note = rendu.get('vers'), []
    if vers is not None and not (isinstance(vers, list) and len(vers) == 4 and all(isinstance(v, (int, float)) for v in vers)
                                 and 0 <= vers[0] < vers[2] <= 1 and 0 <= vers[1] < vers[3] <= 1):
        vers, note = None, [f"`vers` invalide ({rendu.get('vers')}) : rapprochement vers le centre"]
    x['image']['camera'] = [{'cadre': vers}] if vers else []
    sujet = cam.sujet_portrait
    if vers:
        cam.sujet_portrait = lambda *a, **k: None       # le sujet est celui de la réponse
    try:
        r = cam.entier_propose(slug, x, seuil=2.0)      # seuil jamais atteint : le réglage, pas la règle
    finally:
        cam.sujet_portrait = sujet
    reglage = {'entier': True, 'entier_manuel': True}
    if r.get('entier_vers'):
        reglage['entier_vers'] = r['entier_vers']
    if abs(r['entier_zoom'] - cam.ZOOM_ENTIER) > 1e-6:
        reglage['entier_zoom'] = r['entier_zoom']
    final = camera_utile(t['x'])
    return {'proposees': 0, 'premier_jet': note, 'suite': 'image entière', 'repli': False, 'resultat': final,
            'erreurs': 0, 'detail': [], 'tenue_max': round(cam.tenue_max(t['x'], final), 1), 'montre': [],
            'non_identifies': [], 'entier': reglage, 'raison': str(rendu.get('raison') or '')}


def traiter(slug: str, t: dict, rendu: dict) -> dict:
    """Une réponse passée par la chaîne de camera.py, sans renvoi au modèle."""
    if rendu.get('entier') is True:
        return reponse_entiere(slug, t, rendu)
    x, faces = t['x'], t['visages']
    image = cam.image_de(slug, x)
    L, H = image.size
    etapes, erreurs = cam.controler(x['narration'], rendu, L, H, x, image, faces)
    suite = 'acceptée'
    final = etapes
    if erreurs or not etapes:
        gardees = [e for i, e in enumerate(etapes) if i == 0 or e.get('quand')]
        final = None
        if gardees:
            y = copy.deepcopy(x)
            y['image']['camera'] = gardees
            try:    # comme camera.py --reparer
                if any(m.startswith('portrait :') for m in cam.erreurs_vues(y, gardees, L, H, image, faces)):
                    final, _ = cam.reparer_tete(slug, y)
                else:
                    final, _ = cam.reparer(slug, y)
                if final is None:
                    final, _ = cam.reparer(slug, y, foule=True)
            except Exception as e:  # noqa: BLE001
                erreurs = erreurs + [f'réparation en échec : {e}']
        suite = 'réparée' if final else 'repli'
        final = final or [{'cadre': (etapes[:1] or [{'cadre': [0.0, 0.0, 1.0, 1.0]}])[0]['cadre']}]
    e = mesure_banc(slug, x, final, faces)
    return {'proposees': len(rendu.get('etapes') or []), 'premier_jet': erreurs, 'suite': suite,
            'repli': suite == 'repli', 'resultat': final, 'erreurs': len(e), 'detail': e,
            'tenue_max': round(cam.tenue_max(x, final), 1),
            'montre': [str(k.get('montre', '')) for k in rendu.get('etapes') or [] if isinstance(k, dict)],
            'non_identifies': rendu.get('non_identifies') or []}


def tours(f: Path) -> int:
    """1 + versions antérieures de cette réponse gardées par `relire` (et différentes)."""
    actuel = f.read_text().strip()
    return 1 + sum(g.read_text().strip() != actuel for g in (f.parent / 'tours').glob(f'{f.stem}.t*.json'))


# --- Noter ------------------------------------------------------------------------------------

def _case(etapes: list[dict] | None, erreurs, repli=False) -> str:
    if etapes is None:
        return '—'
    return f"{len(etapes)} ét., {erreurs} err.{' REPLI' if repli else ''}"


def planches(slug: str, taches: list[dict], colonnes: list[tuple[str, dict]], base: Path, par_page: int = 12) -> list[Path]:
    """Une ligne par vue, une colonne par source : cadres (trait plein) et vues réelles (pointillé)."""
    W, T = 440, 34
    police = cam._police(13)
    for vieux in base.parent.glob('planche*.jpg'):
        vieux.unlink()
    sorties = []
    pages = [taches[i:i + par_page] for i in range(0, len(taches), par_page)]
    for p, lot in enumerate(pages, 1):
        P = Image.new('RGB', (W * len(colonnes), (W - 60) * len(lot)), 'white')
        dessin = ImageDraw.Draw(P)
        for i, t in enumerate(lot):
            x = t['x']
            base_im = cam.image_de(slug, x).convert('RGB')
            L, H = cam.dims(x)
            for j, (titre, par_id) in enumerate(colonnes):
                m = par_id.get(t['id'])
                y0 = i * (W - 60)
                dessin.text((j * W + 4, y0 + 2), f"{x['n']} · {titre}", fill='black', font=police)
                if not m:
                    dessin.text((j * W + 4, y0 + 17), '—', fill='black', font=police)
                    continue
                dessin.text((j * W + 4, y0 + 17), m['note'][:62], fill='black', font=police)
                im = cam.avec_vues(cam.avec_cadres(base_im, m['resultat']), x, m['resultat'], L, H)
                im.thumbnail((W - 8, W - 60 - T - 4))
                P.paste(im, (j * W + 4, y0 + T))
        f = base if len(pages) == 1 else base.with_name(f'{base.stem}-{p:02d}.jpg')
        P.save(f, quality=85)
        sorties.append(f)
    return sorties


def actuelles(slug: str, taches: list[dict]) -> dict:
    """Caméra du JSON à la préparation, mesurée comme les autres."""
    prod = {}
    for t in taches:
        k = t['x']['image'].get('camera')
        if k:
            e = len(mesure_banc(slug, t['x'], k, t['visages']))
            prod[t['id']] = {'resultat': k, 'erreurs': e, 'repli': False, 'note': _case(k, e),
                             'tenue_max': round(cam.tenue_max(t['x'], k), 1)}
    return prod


def noter(a) -> int:
    neutraliser()
    dossier, m, taches = charger(a.dossier)
    slug = m['slug']
    banc = json.loads((c.RACINE / m['banc_gemini']).read_text()) if m.get('banc_gemini') else []
    ref = reference(banc, a.reference)
    rep = reponses(dossier, taches, a.etiquette or m.get('etiquette') or 'claude')
    if not rep:
        raise SystemExit(f'Aucune reponse-NNN.json dans {dossier}.')
    gem = {nom(x['n']): {'resultat': x['resultat'], 'erreurs': x.get('erreurs', 0), 'repli': bool(x.get('repli')),
                         'note': _case(x['resultat'], x.get('erreurs', 0), x.get('repli'))}
           for x in banc if x['reglage'] == ref and 'resultat' in x}
    prod = actuelles(slug, taches)
    mesures: dict[str, dict] = {}
    for et, fichiers in rep.items():
        mesures[et] = {}
        for t in taches:
            f = fichiers.get(t['id'])
            if not f:
                continue
            rendu, note = lire_reponse(f)
            r = traiter(slug, t, rendu)
            r['lecture'], r['tours'] = note, tours(f)
            r['note'] = (f"{r['proposees']}→{len(r['resultat'])} ét., {len(r['premier_jet'])} refus, "
                         f"{r['suite']}, {r['erreurs']} err.")
            mesures[et][t['id']] = r

    G = bool(gem)
    lignes = [f"# Caméra : Claude contre Gemini ({slug}, {datetime.now():%Y-%m-%d %H:%M})", '',
              (f"Gemini (banc) : `{ref}`, {m.get('banc_gemini')} ; " if G else '')
              + f"JSON : caméra de production à la préparation ({m['prepare']}). Cases : étapes, erreurs de la mesure "
              f"du banc (vues, visages, tête hors champ, étapes ignorées), repli. Claude : étapes proposées→gardées, "
              f"refus du contrôle au premier jet, suite (acceptée, réparée, repli), erreurs finales, tenue la plus longue.",
              '', '| n | nature | ' + ('Gemini (banc) | ' if G else '') + 'JSON actuel | ' + ' | '.join(mesures) + ' |',
              '|---|---|---|' + ('---|' if G else '') + '---|' * len(mesures)]
    for groupe, titre in ((True, 'communes au banc Gemini'), (False, 'Claude seul' if G else '')):
        ts = [t for t in taches if t['commune'] == groupe]
        if ts and titre:
            lignes.append(f"| | **{titre}** | |" + (' |' if G else '') + ' |' * len(mesures))
        for t in ts:
            i = t['id']
            cases = ([gem[i]['note'] if i in gem else '—'] if G else []) + \
                    [f"{prod[i]['note']}, tenue {prod[i]['tenue_max']} s" if i in prod else '—']
            for et in mesures:
                r = mesures[et].get(i)
                cases.append(f"{r['note']}, tenue {r['tenue_max']} s"
                             + (f", {r['tours']} tours" if r['tours'] > 1 else '')
                             + (f" ({r['lecture']})" if r['lecture'] else '') if r else '—')
            lignes.append(f"| {t['n']} | {t['nature']} | " + ' | '.join(cases) + ' |')
    lignes += ['', '## Totaux', '', '| source | vues | étapes | acceptées d\'emblée | réparées | replis | erreurs finales | tenues > 7 s |',
               '|---|---|---|---|---|---|---|---|']
    communes = [t['id'] for t in taches if t['commune']]
    tenues_x = {t['id']: t['x'] for t in taches}

    def total(titre: str, par_id: dict, ids: list[str]) -> None:
        ms = [(i, par_id[i]) for i in ids if i in par_id]
        if ms:
            suite = lambda s: sum(x.get('suite') == s for _, x in ms) if 'suite' in ms[0][1] else '—'
            longues = sum(cam.tenue_max(tenues_x[i], x['resultat']) > cam.TENUE_MAX for i, x in ms)
            lignes.append(f"| {titre} | {len(ms)} | {sum(len(x['resultat']) for _, x in ms)} | {suite('acceptée')} | "
                          f"{suite('réparée')} | {sum(x['repli'] for _, x in ms)} | {sum(x['erreurs'] for _, x in ms)} | {longues} |")
    for portee, ids in (('communes', communes), ('toutes', [t['id'] for t in taches])):
        if not ids or (portee == 'toutes' and len(ids) == len(communes)):
            continue
        if portee == 'communes':
            total(f'Gemini banc `{ref}` (communes)', gem, ids)
        for et in mesures:      # à périmètre égal : les vues auxquelles cette étiquette a répondu
            faits = [i for i in ids if i in mesures[et]]
            total(f'JSON actuel ({portee}, vues de {et})', prod, faits)
            total(f'Claude {et} ({portee})', mesures[et], faits)
    if banc:
        lignes += ['', '## Tous les réglages du banc Gemini (diapositives communes)', '',
                   '| réglage | essais | échecs | erreurs | replis | étapes | $ |', '|---|---|---|---|---|---|---|']
        for rg in dict.fromkeys(x['reglage'] for x in banc):
            ms = [x for x in banc if x['reglage'] == rg]
            ok = [x for x in ms if 'resultat' in x]
            lignes.append(f"| {rg} | {len(ms)} | {len(ms) - len(ok)} | {sum(x.get('erreurs', 0) for x in ok)} | "
                          f"{sum(bool(x.get('repli')) for x in ok)} | {sum(len(x['resultat']) for x in ok)} | "
                          f"{sum(x.get('dollars', 0) for x in ms):.3f} |")
    lignes += ['', '## Refus du contrôle au premier jet et erreurs restantes', '']
    for et in mesures:
        for i, r in mesures[et].items():
            for msg in r['premier_jet']:
                lignes.append(f'- {et} {i} (premier jet) : {msg}')
            for msg in r['detail']:
                lignes.append(f'- {et} {i} (final) : {msg}')
    (dossier / 'comparatif.md').write_text('\n'.join(lignes) + '\n')
    (dossier / 'comparatif.json').write_text(json.dumps(
        {'slug': slug, 'reference': ref, 'gemini': gem, 'json': prod, 'claude': mesures}, ensure_ascii=False, indent=1))
    ps = planches(slug, [t for t in taches if any(t['id'] in mesures[et] for et in mesures)],
                  ([(f'Gemini banc {ref}', gem)] if G else []) + [('JSON actuel', prod)]
                  + [(f'Claude {et}', mesures[et]) for et in mesures], dossier / 'planche.jpg')
    for et in mesures:
        ms = list(mesures[et].values())
        print(f"{et:12s} {len(ms):3d} réponse(s) sur {len(taches)} : {sum(x['suite'] == 'acceptée' for x in ms)} acceptée(s), "
              f"{sum(x['suite'] == 'réparée' for x in ms)} réparée(s), {sum(x['suite'] == 'image entière' for x in ms)} "
              f"image(s) entière(s), {sum(x['repli'] for x in ms)} repli(s), "
              f"{sum(x['erreurs'] for x in ms)} erreur(s) finale(s), {sum(len(x['resultat']) for x in ms)} étape(s) "
              f"(JSON : {sum(len(prod[i]['resultat']) for i in mesures[et] if i in prod)}).")
    print('Tableau :', rel(dossier / 'comparatif.md'), f'; {len(ps)} planche(s) :',
          rel(ps[0]) if ps else '—')
    return 0


# --- Second tour (facultatif) -----------------------------------------------------------------

def relire(a) -> int:
    """Pour chaque réponse : le message que `cadrer` renverrait au modèle, et l'image de relecture."""
    neutraliser()
    dossier, m, taches = charger(a.dossier)
    slug = m['slug']
    defaut = a.etiquette or m.get('etiquette') or 'claude'
    ecrits = fautes = 0
    for et, fichiers in reponses(dossier, taches, defaut).items():
        if a.etiquette and et != a.etiquette:
            continue
        for t in taches:
            f = fichiers.get(t['id'])
            if not f:
                continue
            x, faces = t['x'], t['visages']
            image = cam.image_de(slug, x)
            L, H = image.size
            rendu, _ = lire_reponse(f)
            if rendu.get('entier') is True:     # réponse « image entière » : rien à relire
                continue
            etapes, erreurs = cam.controler(x['narration'], rendu, L, H, x, image, faces)
            if a.fautives and not (erreurs or not etapes):
                continue
            (f.parent / 'tours').mkdir(exist_ok=True)
            k = len(list((f.parent / 'tours').glob(f'{f.stem}.t*.json'))) + 1
            (f.parent / 'tours' / f'{f.stem}.t{k}.json').write_text(f.read_text())
            texte = f'# Retour sur {f.name} (vue {t["n"]})\n\n'
            if erreurs or not etapes:
                fautes += 1
                texte += 'Corrige ces erreurs et renvoie toutes les étapes :\n- ' + '\n- '.join(erreurs or ['aucune étape'])
                texte += ('\n\nNe corrige pas par un cadre d\'évitement (détail de col, bande sans visage, marge) : un cadre '
                          'qui ne montre pas le sujet est pire qu\'un repli. Si aucune vue ne peut montrer le sujet sans '
                          f'couper une tête, rends la réponse « image entière » de la tâche : `{FORMAT_ENTIER}`.')
            else:
                relance = cam.relance_tenues(x, etapes, [str(e.get('montre', '')) for e in rendu.get('etapes', [])])
                petite = cam.reduire(image)
                img = f.parent / f'relecture-{f.stem.removeprefix("reponse-")}.jpg'
                dessin = cam.avec_vues(cam.avec_cadres(cam.avec_grille(petite), etapes), x, etapes, L, H)
                vues = cam.vues_decoupees(petite, x, etapes, L, H)
                P = Image.new('RGB', (max(dessin.width, max(v.width for v in vues)),
                                      dessin.height + sum(v.height + 8 for v in vues)), 'white')
                P.paste(dessin, (0, 0))
                y = dessin.height + 8
                for v in vues:
                    P.paste(v, (0, y))
                    y += v.height + 8
                P.save(img, 'JPEG', quality=85)
                texte += ((relance + '\n\n') if relance else '') + cam.RELECTURE + \
                    f'\n\nImage de relecture (outil Read) : {img}\n(en haut, les cadres et les vues ; dessous, ' \
                    f'chaque vue telle qu\'elle apparaîtra, dans l\'ordre des étapes).\n\nCadres ajustés : ' \
                    + json.dumps(etapes, ensure_ascii=False)
            texte += f'\n\nRéécris `{f}` au même format (toutes les étapes).\n'
            (f.parent / f.name.replace('reponse-', 'retour-').replace('.json', '.md')).write_text(texte)
            ecrits += 1
    print(f'{ecrits} retour(s) écrit(s) (retour-NNN[.étiquette].md), dont {fautes} avec des erreurs à corriger.')
    return 0


# --- Production : appliquer, restaurer --------------------------------------------------------

def _meme_vue(a: dict, b: dict) -> bool:
    cles = ('fichier', 'commons', 'recadrage', 'rotation', 'largeur', 'hauteur', 'utile', 'visage')
    return a['narration'] == b['narration'] and all(a['image'].get(k) == b['image'].get(k) for k in cles) \
        and (a.get('audio') or {}).get('phrases') == (b.get('audio') or {}).get('phrases')


def _cache_camera(slug: str) -> tuple[Path, dict]:
    f = c.CACHE / slug / 'camera.json'
    return f, (json.loads(f.read_text()) if f.exists() else {})


def poser_entiers(slug: str, reglages: dict) -> None:
    """Réglages d'image entière (clé : n de la vue), comme la correction à la main du README (« Images
    entières sur fond noir ») : les quatre champs sont remplacés par ceux du réglage."""
    f2, d2 = c.lire(slug)
    for y in c.vues_camera(d2):
        if y['n'] in reglages:
            for cle in CLES_ENTIER:
                y['image'].pop(cle, None)
            y['image'].update(reglages[y['n']])
    c.ecrire(f2, d2)


def _entier_de(v: dict) -> dict:
    return {k: v['image'][k] for k in CLES_ENTIER if k in v['image']}


def appliquer(a) -> int:
    neutraliser()
    c.charger_env()
    cam.MODELE = gemini.modele('camera')         # même empreinte que camera.py
    dossier, m, taches = charger(a.dossier)
    slug = m['slug']
    rep = reponses(dossier, taches, a.etiquette or m.get('etiquette') or 'claude')
    et = a.etiquette or (next(iter(rep)) if len(rep) == 1 else None)
    if et not in rep:
        raise SystemExit(f"Étiquette à appliquer : --etiquette parmi {sorted(rep) or 'aucune réponse'}.")
    vues = {str(v['n']): v for v in vues_narrees(periode(slug))}
    poser, refus, entiers = [], {}, []
    for t in taches:
        f = rep[et].get(t['id'])
        if not f:
            continue
        v = vues.get(str(t['n']))
        r = traiter(slug, t, lire_reponse(f)[0])
        avant = (v or {}).get('image', {}).get('camera') or []
        raison = None
        if v is None:
            raison = 'vue disparue du JSON'
        elif v.get('camera_manuelle'):
            raison = 'caméra manuelle'
        elif not _meme_vue(v, t['x']):
            raison = 'vue changée depuis la préparation (narration, image, zone utile ou minutage)'
        elif r.get('entier'):
            # Réponse « image entière » : réglage posé comme à la main ; la caméra, non jouée, est gardée
            # (ou réduite à une étape sur la zone utile si la vue n'en a pas).
            if v['image'].get('entier') or v['image'].get('entier_manuel'):
                raison = 'image entière déjà réglée'
            elif v['image'].get('video'):
                raison = 'image entière incompatible avec un clip'
            else:
                entiers.append((t, v, r, avant))
                print(f"{t['id']:>5} image entière" + (f", vers {r['entier']['entier_vers']}" if r['entier'].get('entier_vers') else ', vers le centre')
                      + (f", zoom {r['entier']['entier_zoom']:g}" if 'entier_zoom' in r['entier'] else '') + f" : {r['raison'][:90]}")
                continue
        elif r['repli']:
            raison = 'repli'
        elif r['erreurs']:
            raison = f"{r['erreurs']} erreur(s) du contrôle"
        elif len(r['resultat']) < len(avant):
            raison = f"moins d'étapes ({len(avant)} → {len(r['resultat'])})"
        elif r['resultat'] == avant:
            raison = 'identique à l\'actuelle'
        elif a.strict and not (len(r['resultat']) > len(avant) or r['tenue_max'] < round(cam.tenue_max(v), 1)):
            raison = 'ni plus d\'étapes ni tenue plus courte (--strict)'
        if raison:
            refus.setdefault(raison, []).append(t['id'])
            continue
        poser.append((t, v, r, avant))
        print(f"{t['id']:>5} {len(avant)} → {len(r['resultat'])} étape(s), tenue {cam.tenue_max(v) if avant else 0:.1f} → "
              f"{r['tenue_max']:.1f} s ({r['suite']})")
    for raison, ids in refus.items():
        print(f"Laissées ({len(ids)}) : {raison} : {' '.join(ids)}")
    print(f"{'À poser' if a.essai else 'Posées'} : {len(poser)} caméra(s) de « {et} » sur {len(rep[et])} réponse(s) ; "
          f"étapes {sum(len(p[3]) for p in poser)} → {sum(len(p[2]['resultat']) for p in poser)}.")
    # Entrées en scène jointes aux caméras posées (tâches de grandes vues) : contrôles d'entree.py
    # contre la caméra retenue (règle de fenêtre, visages, ampleur) ; les autres sont laissées.
    entrees = {}
    for t, v, r, avant in poser:
        e = lire_reponse(rep[et][t['id']])[0].get('entree') if t.get('entree') else None
        if e and not v['image'].get('entree'):
            bonne, raison = ent.depuis_camera(v, r['resultat'], e, t['visages'])
            if bonne:
                entrees[str(t['n'])] = bonne
            else:
                print(f"{t['id']:>5} entrée en scène laissée : {raison}")
    if entrees:
        print(f"{'À poser' if a.essai else 'Posées'} : {len(entrees)} entrée(s) en scène : {' '.join(entrees)}")
    if entiers:
        print(f"{'À poser' if a.essai else 'Posées'} : {len(entiers)} image(s) entière(s) (entier, entier_manuel) : "
              f"{' '.join(t['id'] for t, *_ in entiers)}")
    # Caméra d'une étape sur la zone utile (exigée par verifier.py, non jouée) : réponses « image
    # entière » et images entières laissées sans tâche par `preparer`, quand la vue n'a pas de caméra.
    sans_camera = [(t, v, r) for t, v, r, avant in entiers if not avant]
    for e in m.get('entieres') or []:
        v = vues.get(str(e['n']))
        if v is not None and not v['image'].get('camera') and not v.get('camera_manuelle'):
            sans_camera.append(({'n': e['n']}, v, {'resultat': camera_utile(v), 'montre': [], 'non_identifies': [],
                                                 'tenue_max': round(cam.tenue_max(v, camera_utile(v)), 1)}))
    if sans_camera:
        print(f"{'À poser' if a.essai else 'Posées'} : {len(sans_camera)} caméra(s) d'une étape sur la zone utile "
              f"(images entières, caméra non jouée) : {' '.join(str(t['n']) for t, *_ in sans_camera)}")
    if a.essai or not (poser or entiers or sans_camera):
        return 0
    fc, cache = _cache_camera(slug)
    cameras = [(t, v, r, avant, f'claude:{et}') for t, v, r, avant in poser] \
        + [(t, v, r, [], 'entier') for t, v, r in sans_camera]
    sauvegarde = dossier / f'sauvegarde-{datetime.now():%Y%m%d-%H%M%S}.json'
    sauvegarde.write_text(json.dumps(
        {'slug': slug, 'etiquette': et, 'quand': f'{datetime.now():%Y-%m-%d %H:%M:%S}',
         'vues': [{'n': t['n'], 'avant': avant, 'apres': r['resultat'], 'cache': cache.get(str(t['n']))}
                  for t, v, r, avant, _ in cameras],
         'entiers': [{'n': t['n'], 'avant': _entier_de(v), 'apres': r['entier']} for t, v, r, avant in entiers]},
        ensure_ascii=False, indent=1))
    cam.ecrire_cameras(slug, {v['n']: r['resultat'] for t, v, r, avant, _ in cameras})
    fc, cache = _cache_camera(slug)
    for t, v, r, avant, source in cameras:
        cache[str(t['n'])] = {'empreinte': cam.empreinte(v), 'camera': r['resultat'], 'montre': r['montre'],
                              'non_identifies': r['non_identifies'], 'repli': False, 'erreur': None,
                              'tenue_max': r['tenue_max'], 'source': source,
                              'dossier': str(rel(dossier))}
    fc.parent.mkdir(parents=True, exist_ok=True)
    fc.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
    if entiers:
        poser_entiers(slug, {v['n']: r['entier'] for t, v, r, avant in entiers})
    if entrees:
        ent.poser(slug, entrees)
    print(f'JSON et cache caméra écrits ; sauvegarde : {rel(sauvegarde)}')
    return 0


def restaurer(a) -> int:
    neutraliser()
    dossier, m, _ = charger(a.dossier)
    slug = m['slug']
    fs = [Path(a.sauvegarde).resolve()] if a.sauvegarde else sorted(
        f for f in dossier.glob('sauvegarde-*.json') if not json.loads(f.read_text()).get('restauree'))
    if not fs:
        raise SystemExit('Aucune sauvegarde à restaurer dans ce dossier.')
    s = json.loads(fs[-1].read_text())
    vues = {str(v['n']): v for v in vues_narrees(periode(slug))}
    remettre, laissees = {}, []
    for e in s['vues']:
        v = vues.get(str(e['n']))
        if v is None or (v['image'].get('camera') != e['apres'] and not a.force):
            laissees.append(str(e['n']))        # changée depuis (camera.py, réparation, main) : on n'y touche pas
        else:
            remettre[v['n']] = e
    # Réglages d'image entière posés par `appliquer` (réponses « image entière »), s'ils n'ont pas changé.
    entiers = {vues[str(e['n'])]['n']: e['avant'] for e in s.get('entiers') or []
               if str(e['n']) in vues and (_entier_de(vues[str(e['n'])]) == e['apres'] or a.force)}
    print(f"{'À restaurer' if a.essai else 'Restaurées'} ({fs[-1].name}) : {len(remettre)} caméra(s) : "
          f"{' '.join(map(str, remettre))}" + (f" ; laissées (changées depuis, --force pour les remettre) : "
                                                 f"{' '.join(laissees)}" if laissees else '')
          + (f" ; {len(entiers)} réglage(s) d'image entière : {' '.join(map(str, entiers))}" if entiers else ''))
    if a.essai or not (remettre or entiers):
        return 0
    if entiers:
        poser_entiers(slug, entiers)
    cam.ecrire_cameras(slug, {n: e['avant'] for n, e in remettre.items()})
    fc, cache = _cache_camera(slug)
    for n, e in remettre.items():
        if e.get('cache') is None:
            cache.pop(str(n), None)
        else:
            cache[str(n)] = e['cache']
    fc.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
    s['restauree'] = f'{datetime.now():%Y-%m-%d %H:%M:%S}'
    fs[-1].write_text(json.dumps(s, ensure_ascii=False, indent=1))
    return 0


def factice(a) -> int:
    """Réponses d'essai : la caméra du JSON remise au format de réponse (preuve du circuit)."""
    dossier, m, taches = charger(a.dossier)
    for t in taches:
        k = t['x']['image'].get('camera') or [{'cadre': [0, 0, 1, 1]}]
        (rep_de(dossier, t) / f"reponse-{t['id']}.{a.etiquette}.json").write_text(json.dumps(
            {'etapes': [{'quand': e.get('quand'), 'montre': 'cadre du JSON', 'cadre': e['cadre']} for e in k],
             'non_identifies': []}, ensure_ascii=False, indent=1))
    print(f"{len(taches)} réponse(s) factice(s) : reponse-NNN.{a.etiquette}.json")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='commande', required=True)
    q = s.add_parser('preparer', help='écrit les tâches et les images')
    q.add_argument('cible', nargs='+', metavar='[camera] slug', help='période (« camera » devant est admis)')
    q.add_argument('--n', nargs='+', help='vues (« 100 » : la diapositive et ses plans ; « 100b » : ce plan)')
    q.add_argument('--statiques', action='store_true', help=f'vues dont la caméra tient un cadre plus de {cam.TENUE_MAX:.0f} s')
    q.add_argument('--toutes', action='store_true', help='toutes les vues narrées non manuelles (période neuve)')
    q.add_argument('--avec-entieres', action='store_true',
                   help='avec --toutes / --statiques : garde les tâches des images entières (image.entier, camera.py --entiers)')
    q.add_argument('--lot', type=int, default=TAILLE_LOT, help=f'tâches par lot (défaut {TAILLE_LOT})')
    q.add_argument('--etiquette', help='étiquette inscrite dans le nom des réponses demandées (ex. sonnet)')
    q.set_defaults(f=preparer)
    q = s.add_parser('noter', help='note les réponses, écrit le tableau et les planches')
    q.add_argument('dossier', help='dossier du banc, ou l\'un de ses lots')
    q.add_argument('--etiquette', help='nom donné aux reponse-NNN.json sans étiquette')
    q.add_argument('--reference', help='réglage du banc Gemini comparé (ex. « gemini-3.8-flash r0 »)')
    q.set_defaults(f=noter)
    q = s.add_parser('relire', help='second tour : erreurs à corriger ou relecture des cadres dessinés')
    q.add_argument('dossier', help='dossier du banc, ou l\'un de ses lots')
    q.add_argument('--etiquette', help='ne relire que cette étiquette')
    q.add_argument('--fautives', action='store_true', help='seulement les réponses refusées par le contrôle')
    q.set_defaults(f=relire)
    q = s.add_parser('appliquer', help='pose dans le JSON les caméras meilleures que les actuelles')
    q.add_argument('dossier')
    q.add_argument('--etiquette', help='étiquette à appliquer (obligatoire s\'il y en a plusieurs)')
    q.add_argument('--essai', action='store_true', help='affiche ce qui changerait, sans écrire')
    q.add_argument('--strict', action='store_true', help='exige plus d\'étapes ou une tenue plus courte')
    q.set_defaults(f=appliquer)
    q = s.add_parser('restaurer', help='remet les caméras remplacées par le dernier `appliquer`')
    q.add_argument('dossier')
    q.add_argument('--sauvegarde', help='fichier de sauvegarde (défaut : la dernière non restaurée)')
    q.add_argument('--essai', action='store_true')
    q.add_argument('--force', action='store_true', help='même les caméras changées depuis')
    q.set_defaults(f=restaurer)
    q = s.add_parser('factice', help='réponses d\'essai tirées du JSON')
    q.add_argument('dossier')
    q.add_argument('--etiquette', default='factice')
    q.set_defaults(f=factice)
    a = p.parse_args()
    return a.f(a)


if __name__ == '__main__':
    sys.exit(main())
