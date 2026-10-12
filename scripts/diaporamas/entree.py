"""Entrée en scène des grandes vues (`image.entree`, spec 12) : choix des images, tâches pour des
sous-agents Claude, planches de relecture, application, contrôle des étapes sur le lecteur. 0 $.

    python3 scripts/diaporamas/entree.py candidates <slug> [--plans plans.json] [--planches DOSSIER]
    python3 scripts/diaporamas/entree.py regle <slug> [--plans plans.json]      # entrées déjà posées
    python3 scripts/diaporamas/entree.py plans <slug> --dist BUILD --sortie plans.json
    python3 scripts/diaporamas/entree.py preparer <slug> --n 12 34b … [--plans plans.json] [--lot 15]
    python3 scripts/diaporamas/entree.py planche <dossier>          # propositions dessinées (vues réelles)
    python3 scripts/diaporamas/entree.py appliquer <dossier> [--essai] [--sauf 12 34b]
    python3 scripts/diaporamas/entree.py retirer <slug> --n 12 34b
    python3 scripts/diaporamas/entree.py etapes <slug> --avant plans-avant.json --apres plans-apres.json
    python3 scripts/diaporamas/entree.py bilan <slug>               # nombre et types de mouvement

Marche (README, « Entrée en scène d'une grande vue ») :
1. `candidates` : tri mécanique des vues (image principale ou plan). Écartées : entrée déjà posée,
   détail d'`ouverture`, avant / après, mosaïque, clip `video`, plan sans `instant`, première
   image d'un acte (les volets du carton sont son entrée), portrait d'une personne seule (titre ou
   registre), document (carte, affiche, imprimé…), et la **règle de fenêtre** : l'image reste au
   moins FENETRE_2 s si sa caméra a une deuxième étape, FENETRE_1 s sinon, et l'entrée (4 s au
   moins) doit finir avant que la transition vers la deuxième étape ne parte. Avec `--plans` (relevé
   du lecteur par `plans`), ce dernier point est exact (ordinateur et téléphone) ; sinon il est
   estimé (deuxième étape au plus tôt à 4 + MARGE_ETAPE s).
   Le tri de fond (lieu ou scène : bâtiment, place, assemblée, foule, cortège, bataille, paysage)
   se fait à l'œil sur les planches de vignettes (`--planches`), puis `preparer --n …`.
2. `preparer` : une tâche par image (image quadrillée, première vue réelle en vert, visages, durée
   permise), en lots ; un sous-agent par lot répond `reponse-NNN.json`. `planche` dessine les
   vues de départ en pointillé ; `appliquer` contrôle (CONTROLES ci-dessous) et n'écrit que le
   champ `entree`.
3. Après build : `plans` sur l'ancien et le nouveau build puis `etapes` : aucune étape de caméra
   existante n'est décalée ni supprimée (seule la fin de la première tenue change).
"""
import argparse, json, math, re, sys, textwrap
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

import commun as c
import camera as cam

DOSSIER = c.CACHE / 'entree'
FENETRE_1, FENETRE_2 = 6.0, 9.0     # s : fenêtre minimale de l'image (une étape de caméra ; deux ou plus)
DUREES = (4.0, 7.0)                 # s : durée d'une entrée (verifier.py : ENTREE_DUREES)
PART = 0.75                         # ENTREE_PART du lecteur
MARGE_ETAPE = 3.0                   # s : transition la plus courte vers une deuxième étape (DUREE_MIN)
VISE_ZOOM, VISE_GLISSE, RAMPE = 0.22 / 1.05, 0.3 / 1.05, 0.4    # plafonds de vitesse du lecteur
ZOOM_MAX = 0.88                     # log : ×2,4 (verifier.py : ENTREE_AMPLEUR)
A_ENTIER = 2.0                      # largeur / hauteur approchée de la scène d'une image entière (ordinateur)
DOCUMENT = re.compile(r'\b(carte|plan de|affiche|imprime|page de titre|manuscrit|medaille|monnaie|assignat|lettre|'
                      r'journal|autographe|placard|proclamation imprimee|partition|une du|frontispice|billet)\b')
TYPES = ('montée', 'descente', 'travelling', 'recul', 'avancée', 'deux temps')


# --- Vues et règle de fenêtre -----------------------------------------------------------------

def premiere(i: dict) -> list[float]:
    """Premier cadre actuel : celui de la caméra, ou l'image entière (`entier`)."""
    k = i.get('camera') or []
    return [0, 0, 1, 1] if i.get('entier') or not k else k[0].get('cadre') or [0, 0, 1, 1]


def vue_ecran(v: dict, cadre: list[float]) -> list[float]:
    """Partie de l'image montrée sur ordinateur pour `cadre` (approchée). Image entière : le cadre
    porté aux proportions de la scène, qui peut déborder (bandes noires)."""
    i = v['image']
    L, H = i.get('largeur') or 1600, i.get('hauteur') or 1200
    if not i.get('entier'):
        return cam.vue_reelle(cadre, L, H, cam.utile_de(v))
    w, h = (cadre[2] - cadre[0]) * L, (cadre[3] - cadre[1]) * H
    w, h = max(w, h * A_ENTIER), max(h, w / A_ENTIER)
    cx, cy = (cadre[0] + cadre[2]) / 2, (cadre[1] + cadre[3]) / 2
    pose = lambda centre, t: (1 - t) / 2 if t >= 1 else min(max(centre - t / 2, 0), 1 - t)
    x0, y0 = pose(cx, w / L), pose(cy, h / H)
    return [x0, y0, x0 + w / L, y0 + h / H]


def cout(a: list[float], b: list[float]) -> tuple[float, float]:
    """Zoom (log) et glissement (fraction de la scène) d'un trajet, comme `ampleur` du lecteur."""
    wa, ha = a[2] - a[0], a[3] - a[1]
    r = (b[2] - b[0]) / wa
    lr = math.log(r)
    k = 1 if abs(r - 1) < 1e-4 else lr / (r - 1)
    g = max(abs(b[0] + b[2] - a[0] - a[2]) / 2 / wa, abs(b[1] + b[3] - a[1] - a[3]) / 2 / ha) * k
    return abs(lr), g


def duree_jouee(v: dict, e: dict) -> float:
    """Durée que le lecteur donnera à l'entrée (allongée sous les plafonds de vitesse), hors fenêtre."""
    V = [vue_ecran(v, r) for r in e['cadres']] + [vue_ecran(v, premiere(v['image']))]
    u = [max(z / VISE_ZOOM, g / VISE_GLISSE) for z, g in (cout(V[k], V[k + 1]) for k in range(len(V) - 1))]
    voulu = e.get('duree', 5)
    if len(u) == 1:
        return max(voulu, u[0] / (1 - RAMPE))
    s = sum(u)
    a = 0.5 if s < 1e-6 else min(0.7, max(0.3, u[0] / s))
    k = 1 - RAMPE * min(a, 1 - a)
    return k * max(voulu / k, u[0] / ((1 - RAMPE) * a), u[1] / ((1 - RAMPE) * (1 - a)))


def type_mouvement(v: dict, e: dict) -> str:
    if len(e['cadres']) == 2:
        return 'deux temps'
    S, F = vue_ecran(v, e['cadres'][0]), vue_ecran(v, premiere(v['image']))
    r = (F[2] - F[0]) / (S[2] - S[0])
    # Déplacement du centre, en parts de la vue de départ : au-delà d'un quart, c'est un mouvement
    # de translation (qui peut s'élargir en chemin) ; en deçà, un recul ou une avancée.
    gx, gy = (F[0] + F[2] - S[0] - S[2]) / 2 / (S[2] - S[0]), (F[1] + F[3] - S[1] - S[3]) / 2 / (S[3] - S[1])
    if max(abs(gx), abs(gy)) < 0.25 and abs(math.log(r)) >= 0.2:
        return 'recul' if r > 1 else 'avancée'
    if abs(gy) >= abs(gx):
        return 'descente' if gy > 0 else 'montée'
    return 'travelling'


def debuts_actes(d: dict) -> set:
    return {a.get('debut') for a in d.get('actes', [])}


def budget(v: dict, plans: dict | None) -> tuple[float, float | None]:
    """(durée d'entrée permise, instant de la 2e étape compté depuis l'apparition de l'image).
    Avec le relevé du lecteur : la transition vers la 2e étape retenue part à `de` ; l'entrée doit
    finir TENUE_MIN (1 s) avant, sur l'ordinateur comme sur le téléphone."""
    i, fen = v['image'], v['audio']['duree']
    permis, t2 = min(DUREES[1], PART * fen), None
    etapes = [] if i.get('entier') else (i.get('camera') or [])
    if len(etapes) > 1:
        t2 = cam.instants(v, etapes)[1]
        permis = min(permis, t2 - MARGE_ETAPE)
    for app in (plans or {}).values():
        p = app.get(str(v['n']))
        if p and len(p['plan']) > 1:
            permis = min(permis, p['plan'][1]['de'] - p['t'] - 1.0)
    return permis, t2


def motif(d: dict, v: dict, plans: dict | None = None, actes: set | None = None) -> str | None:
    """Pourquoi la vue n'est pas candidate (None : candidate mécanique)."""
    return motif_image(d, v, actes) or regle(v, plans)


def motif_image(d: dict, v: dict, actes: set | None = None) -> str | None:
    """Nature de l'image, hors règle de fenêtre (qui dépend de la caméra)."""
    i = v['image']
    parent = next(x for x in d['diapositives'] if x['n'] == v.get('diapositive', v['n']))
    principale = i is parent['image']
    if i.get('entree'):
        return 'entrée déjà posée'
    if i.get('ouverture'):
        return 'détail d\'ouverture'
    if i.get('apres') or (parent.get('mosaique') and principale):
        return 'avant / après ou mosaïque'
    if i.get('video'):
        return 'clip vidéo'
    if v.get('sans_instant'):
        return 'plan sans instant'
    if principale and parent['n'] in (actes if actes is not None else debuts_actes(d)):
        return 'première image d\'un acte'
    titre = cam._sans_accents((i.get('titre') or '') + ' ' + (i.get('technique') or ''))
    if cam.indice_portrait(v) or re.match(r'\s*(buste|medaillon|silhouette)\b', titre):
        return 'portrait'
    if DOCUMENT.search(titre):
        return 'document'
    return None


def regle(v: dict, plans: dict | None = None) -> str | None:
    """Règle de fenêtre (None : respectée)."""
    i, fen = v['image'], v['audio']['duree']
    n = 1 if i.get('entier') else len(i.get('camera') or [])
    mini = FENETRE_2 if n > 1 else FENETRE_1
    if fen < mini:
        return f'fenêtre de {fen:.1f} s ({mini:.0f} s au moins avec {n} étape(s))'
    permis, t2 = budget(v, plans)
    if permis < DUREES[0]:
        return f'2e étape à {t2:.1f} s : une entrée de {DUREES[0]:.0f} s la décalerait (permis {max(0, permis):.1f} s)'
    return None


def vues(d: dict) -> list[dict]:
    return [v for v in c.vues_camera(d, series=False)
            if (v.get('image') or {}).get('fichier') and (c.PUBLIC / d['slug'] / v['image']['fichier']).exists()]


def lire_plans(chemin: str | None) -> dict | None:
    return json.loads(Path(chemin).read_text()) if chemin else None


def instant_diapo(d: dict, v: dict) -> str:
    """Repère lisible : « 34 b, à 11,2 s »."""
    t0 = (v.get('fenetre') or {}).get('t', (0, 0))[0] or 0
    return f"{v['n']}" + (f' (à {t0:.1f} s de la diapositive {v["diapositive"]})' if t0 else '')


# --- Candidates -------------------------------------------------------------------------------

def vignette(slug: str, v: dict, cote: int = 256, etiquette: str = '') -> Image.Image:
    im = cam.reduire(cam.image_de(slug, v), cote)
    case = Image.new('RGB', (cote, cote + 30), (255, 255, 255))
    case.paste(im, ((cote - im.width) // 2, (cote - im.height) // 2))
    g = ImageDraw.Draw(case)
    g.text((3, cote + 1), etiquette[:44], fill=(0, 0, 0), font=cam._police(12))
    g.text((3, cote + 15), (v['image'].get('titre_court') or v['image'].get('titre') or '')[:44], fill=(90, 90, 90), font=cam._police(11))
    return case


def mosaique(cases: list[Image.Image], colonnes: int) -> Image.Image:
    l, h = cases[0].size
    page = Image.new('RGB', (colonnes * l, math.ceil(len(cases) / colonnes) * h), (255, 255, 255))
    for k, im in enumerate(cases):
        page.paste(im, (k % colonnes * l, k // colonnes * h))
    return page


def candidates(a) -> int:
    d = json.loads(c.fichier_periode(a.slug).read_text())
    plans, actes = lire_plans(a.plans), debuts_actes(d)
    garde, motifs = [], {}
    for v in vues(d):
        m = motif(d, v, plans, actes)
        if m:
            motifs.setdefault(re.sub(r' de [\d.,]+ s.*|^2e étape.*', '', m) or 'deuxième étape trop proche', []).append(str(v['n']))
        else:
            garde.append(v)
    for m, ns in motifs.items():
        print(f'Écartées ({len(ns)}) : {m} : {" ".join(ns)}')
    print(f'{len(garde)} candidate(s) mécanique(s) pour « {d["slug"]} » (à trier à l\'œil : lieu ou scène) :')
    for v in garde:
        i, (permis, t2) = v['image'], budget(v, plans)
        n = 1 if i.get('entier') else len(i.get('camera') or [])
        print(f"  {str(v['n']):>5} fen {v['audio']['duree']:5.1f} s, {n} étape(s){f' (2e à {t2:.1f} s)' if t2 else ''}, "
              f"entrée ≤ {permis:.1f} s{', entière' if i.get('entier') else ''} : {i.get('titre_court') or i.get('titre')}")
    if a.planches:
        rep = Path(a.planches)
        rep.mkdir(parents=True, exist_ok=True)
        cases = [vignette(d['slug'], v, 256, f"{v['n']}  {v['audio']['duree']:.0f} s{' E' if v['image'].get('entier') else ''}") for v in garde]
        for k in range(0, len(cases), 30):
            f = rep / f'candidates-{d["slug"]}-{k // 30 + 1:02d}.jpg'
            mosaique(cases[k:k + 30], 6).save(f, 'JPEG', quality=80)
            print(f'planche : {f}')
    return 0


def regle_posees(a) -> int:
    d = json.loads(c.fichier_periode(a.slug).read_text())
    plans, faute = lire_plans(a.plans), 0
    for v in vues(d):
        e = v['image'].get('entree')
        if not e:
            continue
        m = regle(v, plans)
        jouee, (permis, t2) = duree_jouee(v, e), budget(v, plans)
        if not m and jouee > permis + 0.05:
            m = f'entrée de {jouee:.1f} s pour {permis:.1f} s permis' + (f' (2e étape à {t2:.1f} s)' if t2 else '')
        faute += bool(m)
        print(f"  {str(v['n']):>5} fen {v['audio']['duree']:5.1f} s, entrée {jouee:.1f} s, {type_mouvement(v, e)} : {m or 'règle respectée'}")
    return 1 if faute else 0


# --- Relevé du lecteur ------------------------------------------------------------------------

RELEVE = """() => { const r = document.querySelector('.diaporama');
  const D = JSON.parse(r.querySelector('.diaporama__donnees').textContent).diapos, o = {};
  for (const x of D) { const k = r.__camera(x.n, 0); if (!k) continue;
    o[x.n] = { t: 0, plan: k.plan.map((e) => ({ t: e.t, de: e.de, a: e.a })) };
    k.plans.forEach((p, j) => { o[x.n + 'bcdefg'[j]] = { t: p.t, plan: p.plan }; }); }
  return o; }"""


def releve(a) -> int:
    """Étapes retenues par le lecteur (instants `de`, `a`) pour chaque vue, sur ordinateur et téléphone."""
    import captures
    from playwright.sync_api import sync_playwright
    dist = Path(a.dist).resolve()
    slug = json.loads(c.fichier_periode(a.slug).read_text())['slug']
    srv, port = captures.serveur(dist)
    sortie = {}
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch(executable_path=captures.chromium())
            for app, (w, h, _) in captures.APPAREILS.items():
                pg = nav.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1).new_page()
                pg.goto(f'http://127.0.0.1:{port}/diaporamas/{slug}/', wait_until='load')
                pg.wait_for_timeout(600)
                pg.click('[data-action="lancer"]')
                pg.evaluate("() => { const r = document.querySelector('.diaporama'); r.__generique && r.__generique('passer'); }")
                pg.wait_for_timeout(600)
                sortie[app] = pg.evaluate(RELEVE)
            nav.close()
    finally:
        srv.shutdown()
    Path(a.sortie).write_text(json.dumps(sortie))
    print(f"{len(sortie['ordinateur'])} vues relevées ({', '.join(sortie)}) : {a.sortie}")
    return 0


def etapes(a) -> int:
    """Compare deux relevés : hors la fin de la première tenue, rien ne doit avoir bougé."""
    avant, apres, ecarts = lire_plans(a.avant), lire_plans(a.apres), 0
    posees = {str(v['n']) for v in vues(json.loads(c.fichier_periode(a.slug).read_text())) if v['image'].get('entree')}
    for app in avant:
        for n, p in avant[app].items():
            q = apres[app].get(n)
            if q is None:
                print(f'  {app} {n} : vue disparue')
                ecarts += 1
                continue
            A, B = p['plan'], q['plan']
            pareil = len(A) == len(B) and all(abs(x['de'] - y['de']) < 0.02 and abs(x['a'] - y['a']) < 0.02 for x, y in zip(A[1:], B[1:]))
            if not pareil or (n not in posees and abs(A[0]['a'] - B[0]['a']) > 0.02):
                ecarts += 1
                print(f"  {app} {n} : étapes {[(round(x['de'], 1), round(x['a'], 1)) for x in A[1:]]} → "
                      f"{[(round(x['de'], 1), round(x['a'], 1)) for x in B[1:]]}, fin de l'entrée {B[0]['a'] - q['t']:.1f} s")
    fins = [apres[app][n]['plan'][0]['a'] - apres[app][n]['t'] for app in apres for n in posees if n in apres[app]]
    print(f"{len(posees)} entrée(s) ; {ecarts} écart(s) d'étapes" + (f" ; entrées de {min(fins):.1f} à {max(fins):.1f} s" if fins else ''))
    return 1 if ecarts else 0


# --- Tâches -----------------------------------------------------------------------------------

REPERTOIRE = """\
- **montée** le long d'une façade, d'une colonne, d'un escalier, jusqu'à la scène ;
- **descente** du ciel, des toits ou de la voûte vers la foule ou l'assemblée ;
- **travelling** latéral le long d'un cortège, d'une rangée, d'un champ de bataille jusqu'à son centre ;
- **recul** depuis un détail qui situe le lieu (une tribune, un drapeau, une enseigne, un clocher,
  un groupe au premier plan) jusqu'au premier cadre ;
- **avancée** depuis le plan large quand le premier cadre est serré sur le cœur de la scène ;
- **deux temps** (rare, deux cadres de départ) : par exemple des toits, on descend la façade, puis
  on glisse vers la foule."""


def consigne(permis: float, entier: bool, V0: list[float], hmax: float, k: float, cle: str = 'entree') -> str:
    """Consigne de l'entrée en scène (commune à entree.py et à banc_claude.py)."""
    fin = ('Cette image est montrée ENTIÈRE sur fond noir : l\'entrée finit donc sur l\'image entière '
           '([0, 0, 1, 1]) ; le mouvement est un recul depuis un cadre de départ, à choisir pour que le recul '
           'soit aussi une montée, une descente ou un glissement (le cadre de départ est en bas, en haut ou '
           'sur un côté). Le cadre de départ est montré tel quel, élargi à l\'écran (environ 2:1). Le zoom se '
           'compte sur la vue : le cadre de départ couvre au moins la MOITIÉ de la hauteur de l\'image (image en '
           'hauteur ou peu allongée) ou de sa largeur (image très allongée), sinon le recul dépasse ×2.'
           if entier else
           f'La caméra finit EXACTEMENT sur la première vue : x {V0[0]:.2f}-{V0[2]:.2f}, y {V0[1]:.2f}-{V0[3]:.2f}. '
           f'Pour un cadre de départ de largeur w et de hauteur h (fractions de l\'image), l\'écran montre une vue '
           f'de hauteur vh = min(max(h, w / {k:.2f}), {hmax:.2f}) et de largeur vh × {k:.2f}, centrée sur le cadre. '
           f'Conséquence : tout cadre plus haut qu\'environ {hmax:.2f} est montré PLEINE LARGEUR, et deux cadres '
           f'hauts donnent la même vue (aucun mouvement). Une montée ou une descente se fait donc entre deux '
           f'vues de même largeur, décalées en hauteur ; un travelling latéral, un recul ou une avancée demandent '
           f'un cadre BAS ET SERRÉ (h ≤ {min(0.35, hmax * 0.8):.2f}) au départ ou à l\'arrivée.')
    return f"""\
Pense l'arrivée de cette image comme un cinéaste qui filmerait le lieu : par quel mouvement la
caméra arrive-t-elle à la première vue ? Ce mouvement ne se cale PAS sur la narration (aucun mot
ne le déclenche) : c'est l'arrivée de l'image, pas son commentaire.

Seules s'y prêtent les images qui montrent un LIEU ou une SCÈNE : bâtiment, place, salle,
assemblée, foule, cortège, bataille, paysage, vue de ville. Pas d'entrée (`"{cle}": null`) pour
un portrait, un groupe serré de quelques personnages, un document, un objet, une carte, une
caricature à personnage unique, ni quand aucun mouvement ne dirait quelque chose du lieu : mieux
vaut pas d'entrée qu'un mouvement mécanique.

Répertoire (un seul mouvement, simple et lisible) :
{REPERTOIRE}

{fin}

Règles :
- Ce que le spectateur doit découvrir EN DERNIER (le cœur de la scène, le personnage, la foule)
  n'est pas dans la vue de départ, ou n'y est qu'en bord : on le garde pour la fin.
- Ne pars pas du plan large si la caméra s'élargit ensuite (mouvement inversé), ni d'un détail
  que la caméra ira montrer plus tard.
- Aucun visage coupé par les bords de la vue de départ (rectangles des visages : entiers dans la
  vue ou franchement dehors). La vue de départ reste dans la partie montrable de l'image, sans
  marge, légende ni fond uni (pas un ciel vide : un ciel avec des toits, des drapeaux, de la fumée).
- Mouvement net mais mesuré : la vue de départ diffère franchement de la première vue (au moins
  15 % de l'image en position, ou un zoom d'au moins ×1,3) ; zoom total d'au plus ×2 ; cadre de
  départ large d'au moins 0,3 (plus serré, l'image serait floue).
- `duree` : 4 à {permis:.1f} s (5 d'ordinaire ; plus long pour un grand trajet). Au-delà, l'entrée
  retarderait la caméra existante.
- `intention` : une phrase, en français, qui dit le mouvement comme on le tournerait
  (« On descend de la voûte vers les bancs des députés. »).
- `mouvement` : {', '.join(TYPES)}."""


def consigne_banc(hmax: float, k: float) -> str:
    """Section « Entrée en scène » d'une tâche de caméra (banc_claude.py) : le premier cadre est
    celui que l'agent propose dans la même réponse."""
    return f"""\
En plus de la caméra, et seulement si l'image montre un LIEU ou une SCÈNE (bâtiment, place, salle,
assemblée, foule, cortège, bataille, paysage, vue de ville), propose son entrée en scène : le
mouvement par lequel un cinéaste arriverait à ton PREMIER cadre. Ce mouvement ne se cale pas sur
la narration : c'est l'arrivée de l'image, pas son commentaire. Pas d'entrée (`"entree": null`)
pour un portrait, un groupe serré, un document, un objet, une carte, une caricature à personnage
unique, ni quand aucun mouvement ne dirait quelque chose du lieu : mieux vaut pas d'entrée qu'un
mouvement mécanique.

Répertoire (un seul mouvement, simple et lisible ; varie d'une image à la suivante) :
{REPERTOIRE}

Règles :
- Règle de fenêtre : l'entrée ne doit décaler ni supprimer aucune étape de ta caméra. Pas d'entrée
  si l'image reste moins de {FENETRE_1:.0f} s à l'écran, ou moins de {FENETRE_2:.0f} s quand tu proposes une deuxième
  étape ; et l'entrée (4 s au moins) finit au moins {MARGE_ETAPE:.0f} s avant l'instant du `quand` de ta deuxième
  étape (deuxième étape à 8 s : entrée de 5 s au plus ; avant 7 s : pas d'entrée).
- `cadres` : un cadre de départ (deux pour un mouvement en deux temps, rare). Sa vue réelle suit la
  même géométrie que les cadres de caméra : tout cadre plus haut qu'environ {hmax:.2f} est montré pleine
  largeur, et deux cadres hauts donnent la même vue (aucun mouvement). Une montée ou une descente
  se fait entre deux vues de même largeur décalées en hauteur ; un travelling latéral, un recul ou
  une avancée demandent un cadre BAS ET SERRÉ (h ≤ {min(0.35, hmax * 0.8):.2f}) au départ ou à l'arrivée.
- Ce que le spectateur doit découvrir en dernier n'est pas dans la vue de départ. Ne pars pas du
  plan large si ta caméra s'élargit ensuite, ni d'un détail que ta caméra ira montrer plus tard.
- Aucun visage coupé par la vue de départ ; elle reste dans la partie montrable (ni marge, ni
  légende, ni ciel vide).
- Mouvement net mais mesuré : au moins 15 % de l'image en position ou un zoom de ×1,3 ; zoom total
  de ×2 au plus ; cadre de départ large d'au moins 0,3.
- `duree` : 4 à 7 s (5 d'ordinaire) ; `intention` : une phrase qui dit le mouvement comme on le
  tournerait (« On descend de la voûte vers les bancs des députés. »)."""


def depuis_camera(v: dict, camera: list[dict], e, faces: list) -> tuple[dict | None, str | None]:
    """Entrée proposée avec une caméra (banc_claude.py) : (entrée à poser, None) ou (None, raison)."""
    import copy
    w = dict(v, image=dict(copy.deepcopy(v['image']), camera=camera))
    w['image'].pop('entree', None)
    if not isinstance(e, dict):
        return None, 'entrée illisible'
    e = {'cadres': [[round(float(x), 3) for x in k] for k in e.get('cadres') or [] if isinstance(k, list) and len(k) == 4],
         'duree': e.get('duree', 5), 'intention': str(e.get('intention') or '').strip()}
    m = regle(w)
    if m:
        return None, m
    err, _ = controler(w, e, faces, budget(w, None)[0])
    return (None, '; '.join(err)) if err else (e, None)


FORMAT = """\
{"entree": {"cadres": [[x0, y0, x1, y1]], "duree": 5, "intention": "…"}, "mouvement": "descente"}
ou, si l'image ne s'y prête pas :
{"entree": null, "raison": "portrait de groupe serré"}"""


def geometrie(v: dict) -> tuple[float, float]:
    """(hauteur maximale d'une vue, rapport largeur / hauteur d'une vue en fractions de l'image)."""
    i, u = v['image'], cam.utile_de(v)
    L, H = i.get('largeur') or 1600, i.get('hauteur') or 1200
    hmax = min((u[2] - u[0]) * L / cam.RATIO_VUE, (u[3] - u[1]) * H / (1 + cam.BANDE_HAUT + cam.BANDE_BAS)) / H
    return hmax, cam.RATIO_VUE * H / L


def rectangle(g: ImageDraw.ImageDraw, b: list[float], l: int, h: int, couleur, pointille: bool, ep: int = 3) -> None:
    b = [max(1, b[0] * l), max(1, b[1] * h), min(l - 2, b[2] * l), min(h - 2, b[3] * h)]
    if not pointille:
        g.rectangle(b, outline=couleur, width=ep)
        return
    pas = max(6, l // 60)
    for xx in range(int(b[0]), int(b[2]), 2 * pas):
        for yy in (b[1], b[3]):
            g.line([(xx, yy), (min(xx + pas, b[2]), yy)], fill=couleur, width=ep)
    for yy in range(int(b[1]), int(b[3]), 2 * pas):
        for xx in (b[0], b[2]):
            g.line([(xx, yy), (xx, min(yy + pas, b[3]))], fill=couleur, width=ep)


VERT, ROUGE, ORANGE = (40, 210, 70), (255, 50, 50), (255, 170, 0)


def image_tache(slug: str, v: dict, cote: int = 1024, e: dict | None = None, grille: bool = True) -> Image.Image:
    im = cam.reduire(cam.image_de(slug, v), cote)
    if grille:
        im = cam.avec_grille(im)
    g = ImageDraw.Draw(im)
    l, h = im.size
    ep = max(2, l // 250)
    rectangle(g, vue_ecran(v, premiere(v['image'])), l, h, VERT, False, ep)
    for k, r in enumerate((e or {}).get('cadres') or []):
        rectangle(g, vue_ecran(v, r), l, h, (ROUGE, ORANGE)[k % 2], True, ep)
    return im


def texte_tache(slug: str, v: dict, permis: float, faces: list, img: Path, reponse: Path, voisines: str) -> str:
    i = v['image']
    L, H = i.get('largeur') or 1600, i.get('hauteur') or 1200
    u, (hmax, k) = cam.utile_de(v), geometrie(v)
    V0 = vue_ecran(v, premiere(i))
    suite = [e['cadre'] for e in (i.get('camera') or [])[1:]] if not i.get('entier') else ([i['entier_vers']] if i.get('entier_vers') else [])
    notice = ', '.join(x for x in (i.get('auteur'), i.get('date'), i.get('technique')) if x)
    course = ''
    if not i.get('entier'):
        haut = cam.vue_reelle([u[0], u[1], u[2], u[1] + hmax], L, H, u)
        bas = cam.vue_reelle([u[0], u[3] - hmax, u[2], u[3]], L, H, u)
        course = (f"Vues pleine largeur possibles : de y {haut[1]:.2f}-{haut[3]:.2f} (la plus haute) à y {bas[1]:.2f}-{bas[3]:.2f} "
                  f"(la plus basse) ; hauteur d'une vue pleine largeur : {hmax:.2f}.\n")
    return (
        f"# Tâche {v['n']} : entrée en scène ({slug})\n\n"
        f"Image : {i.get('titre')} ({notice}), {L} × {H} px.\n"
        f"Partie montrable (sans marges ni légende) : x {u[0]:.2f}-{u[2]:.2f}, y {u[1]:.2f}-{u[3]:.2f}.\n"
        + ("Première vue : l'image ENTIÈRE, sur fond noir (rectangle VERT plein au bord de l'image).\n" if i.get('entier') else
           f"Première vue (rectangle VERT plein sur l'image) : x {V0[0]:.2f}-{V0[2]:.2f}, y {V0[1]:.2f}-{V0[3]:.2f}.\n") +
        f"Cadres que la caméra montrera ensuite : {suite or 'aucun (la caméra reste sur la première vue)'}.\n"
        f"{course}"
        f"Visages (rectangles x0, y0, x1, y1) : {[[round(t, 2) for t in f] for f in faces if f[3] - f[1] >= cam.FACE_MIN] or 'aucun relevé'}.\n"
        f"L'image reste {v['audio']['duree']:.1f} s à l'écran. Narration dite pendant ce temps (pour comprendre "
        f"la scène, pas pour caler le mouvement) : {v['narration']}\n\n"
        f"## Consigne\n\n{consigne(permis, bool(i.get('entier')), V0, hmax, k)}\n\n"
        f"{voisines}"
        f"## Image à regarder (outil Read)\n\n{img}\n\n"
        f"Grille graduée de 0 à 1 (origine en haut à gauche) ; les cadres sont en fractions de cette image.\n\n"
        f"## Réponse\n\nUn objet JSON, et rien d'autre, écrit dans `{reponse}` :\n\n```json\n{FORMAT}\n```\n")


def lisezmoi(slug: str, rep: Path, ids: list[str]) -> str:
    return f"""\
# Entrée en scène des grandes vues d'un diaporama

Tu choisis le mouvement d'arrivée de {len(ids)} images d'un diaporama narré sur l'histoire de
France (période « {slug} »), comme un cinéaste. Une tâche par image : {', '.join(ids)}.

Pour chaque `tache-NNN.md` de ce dossier, dans l'ordre :
1. Lis la tâche en entier (première vue, géométrie de l'écran, visages, durée permise, consigne).
2. Regarde `image-NNN.jpg` avec l'outil Read : le rectangle vert est la première vue, celle où
   le mouvement doit finir. Lis les coordonnées sur la grille.
3. Décide : cette image mérite-t-elle une entrée ? Si oui, quel mouvement un cinéaste ferait-il,
   et de quel cadre part-il ? Calcule la vue de départ réelle (formule de la tâche) et vérifie-la
   contre les visages et la partie montrable.
4. Écris `reponse-NNN.json` (chemin exact dans la tâche) : l'objet JSON demandé, seul.

Règles :
- VARIE les mouvements d'une image à la suivante : pas deux fois de suite le même type, et pas
  plus d'un tiers de reculs dans le lot. Si le seul mouvement possible répète le précédent sans
  rien apporter, réponds `"entree": null`.
- Ce qui passe mal l'écran (relecture des périodes 01 à 05) : un travelling ou un recul dont la vue
  de départ recouvre plus de la moitié de la première vue est imperceptible (il faut une vue de
  départ franchement ailleurs ou deux fois plus serrée) ; une montée partie du premier plan d'une
  foule coupe les têtes du rang du dessus. Les descentes (ciel, toits, voûte) et les reculs d'une
  image entière sont sûrs, mais pas plus de quatre descentes sur dix images : cherche aussi la
  montée d'une façade ou d'une colonne, le recul depuis une enseigne, un drapeau, un clocher.
- Sois sélectif : une quinzaine de belles entrées vaut mieux que des mouvements mécaniques.
  Refuser (null, avec la raison) est une bonne réponse pour une image qui ne s'y prête pas.
- Ne lance aucun script, ne modifie ni les tâches ni les images, n'écris rien hors de ce dossier.
- Une réponse par tâche, une seule version.

Dossier : {rep}
"""


def nom(n) -> str:
    m = re.fullmatch(r'(\d+)([a-z]?)', str(n))
    return f'{int(m[1]):03d}{m[2]}' if m else str(n)


def visages_de(slug: str, choix: list[dict]) -> dict:
    import banc_claude as bc
    bc.neutraliser(slug, choix)
    return {str(v['n']): cam.visages(slug, v, appeler=False) or [] for v in choix}


def preparer(a) -> int:
    d = json.loads(c.fichier_periode(a.slug).read_text())
    slug, plans, actes = d['slug'], lire_plans(a.plans), debuts_actes(d)
    choix = []
    for v in vues(d):
        if str(v['n']) not in a.n:
            continue
        m = motif(d, v, plans, actes)
        if m and not a.force:
            print(f"  {v['n']} laissée : {m}")
            continue
        choix.append(v)
    if not choix:
        raise SystemExit('Aucune vue à préparer.')
    faces = visages_de(slug, choix)
    sortie = DOSSIER / f'{slug}-{datetime.now():%Y%m%d-%H%M%S}'
    nb = math.ceil(len(choix) / a.lot)
    taille = math.ceil(len(choix) / nb)
    taches = []
    for k, v in enumerate(choix):
        rep = sortie / f'lot-{k // taille + 1}'
        rep.mkdir(parents=True, exist_ok=True)
        ident = nom(v['n'])
        img = rep / f'image-{ident}.jpg'
        image_tache(slug, v).save(img, 'JPEG', quality=85)
        permis = math.floor(budget(v, plans)[0] * 2) / 2
        (rep / f'tache-{ident}.md').write_text(texte_tache(slug, v, permis, faces[str(v['n'])], img, rep / f'reponse-{ident}.json', ''))
        taches.append({'id': ident, 'n': v['n'], 'lot': rep.name, 'permis': permis, 'visages': faces[str(v['n'])],
                       'camera': v['image'].get('camera'), 'fichier': v['image']['fichier']})
    for lot in dict.fromkeys(t['lot'] for t in taches):
        (sortie / lot / 'LISEZMOI.md').write_text(lisezmoi(slug, sortie / lot, [t['id'] for t in taches if t['lot'] == lot]))
    (sortie / 'taches.json').write_text(json.dumps({'slug': slug, 'plans': a.plans, 'taches': taches}, ensure_ascii=False, indent=1))
    print(f"{len(taches)} tâche(s) dans {sortie} : " + ', '.join(f"{lot} ({sum(t['lot'] == lot for t in taches)})" for lot in dict.fromkeys(t['lot'] for t in taches)))
    return 0


# --- Réponses : contrôle, planche, application ------------------------------------------------

def controler(v: dict, e: dict, faces: list, permis: float) -> tuple[list[str], list[str]]:
    """CONTROLES d'une entrée proposée : (erreurs, avertissements)."""
    if not isinstance(e, dict) or not isinstance(e.get('cadres'), list) or not 1 <= len(e['cadres']) <= 2:
        return ['« cadres » attendu : un ou deux cadres'], []
    err, av = [], []
    u = cam.utile_de(v)
    for r in e['cadres']:
        if not (isinstance(r, list) and len(r) == 4 and all(isinstance(t, (int, float)) for t in r) and 0 <= r[0] < r[2] <= 1 and 0 <= r[1] < r[3] <= 1):
            return [f'cadre invalide ({r})'], []
        dedans = max(0, min(r[2], u[2]) - max(r[0], u[0])) * max(0, min(r[3], u[3]) - max(r[1], u[1])) / ((r[2] - r[0]) * (r[3] - r[1]))
        if dedans < 0.75:
            err.append(f'cadre {r} hors de la partie montrable ({dedans:.0%})')
    if not isinstance(e.get('duree', 5), (int, float)) or not DUREES[0] <= e.get('duree', 5) <= DUREES[1]:
        err.append(f"durée {e.get('duree')} hors de 4-7 s")
    if not (e.get('intention') or '').strip():
        err.append('intention absente')
    if err:
        return err, av
    V = [vue_ecran(v, r) for r in e['cadres']] + [vue_ecran(v, premiere(v['image']))]
    for k, S in enumerate(V[:-1]):
        coupes = cam.visages_coupes(S, [f for f in faces if f[3] - f[1] >= cam.FACE_MIN])
        if coupes:
            av.append(f'vue de départ {k + 1} : {len(coupes)} visage(s) coupé(s) {[[round(t, 2) for t in f] for f in coupes[:3]]}')
        z, g = cout(S, V[k + 1])
        if z < 0.2 and g < 0.15:
            err.append(f'mouvement {k + 1} imperceptible (zoom ×{math.exp(z):.2f}, glissement {g:.2f})')
    total = sum(cout(V[k], V[k + 1])[0] for k in range(len(V) - 1))
    if total > ZOOM_MAX:
        err.append(f'zoom total ×{math.exp(total):.1f} (×2,4 au plus)')
    jouee = duree_jouee(v, e)
    if jouee > permis + 0.05:
        err.append(f'entrée jouée en {jouee:.1f} s pour {permis:.1f} s permis (elle décalerait la caméra) : mouvement plus court')
    return err, av


def reparer(v: dict, e: dict, faces: list, permis: float) -> dict | None:
    """Entrée refusée pour son ampleur ou sa durée : même mouvement, moins ample (cadre de départ
    agrandi autour de son centre, ramené dans la partie montrable ; durée ramenée au permis).
    None si elle reste refusée ou devient imperceptible."""
    u = [0, 0, 1, 1] if v['image'].get('entier') else cam.utile_de(v)
    duree = min(e.get('duree', 5), math.floor(permis * 2) / 2)
    if duree < DUREES[0]:
        return None
    for k in range(0, 40):
        f = 1 + 0.05 * k
        cadres = []
        for r in e['cadres']:
            cx, cy, w, h = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, (r[2] - r[0]) * f / 2, (r[3] - r[1]) * f / 2
            cadres.append([round(t, 3) for t in cam.dans_utile([cx - w, cy - h, cx + w, cy + h], u)])
        e2 = dict(e, cadres=cadres, duree=duree)
        err, _ = controler(v, e2, faces, permis)
        if not err:
            return e2
        if any('imperceptible' in x or 'cadre invalide' in x for x in err):
            return None
    return None


def charger(chemin: str) -> tuple[Path, dict, list[dict]]:
    p = Path(chemin).resolve()
    racine = p if (p / 'taches.json').exists() else p.parent
    m = json.loads((racine / 'taches.json').read_text())
    return racine, m, [t for t in m['taches'] if p == racine or t['lot'] == p.name]


def reponses(a) -> tuple[str, list[dict]]:
    """Réponses lues et contrôlées : {'t', 'v', 'e' (ou None), 'raison', 'err', 'av', 'type', 'dit'}."""
    racine, m, taches = charger(a.dossier)
    slug = m['slug']
    d = json.loads(c.fichier_periode(slug).read_text())
    par_n, plans, sortie = {str(v['n']): v for v in vues(d)}, lire_plans(m.get('plans')), []
    for t in taches:
        f = racine / t['lot'] / f"reponse-{t['id']}.json"
        v = par_n.get(str(t['n']))
        if not f.exists() or v is None:
            continue
        try:
            brut = json.loads(re.sub(r'^```(?:json)?\s*|\s*```\s*$', '', f.read_text().strip()))
        except ValueError as x:
            sortie.append({'t': t, 'v': v, 'e': None, 'raison': None, 'err': [f'JSON illisible : {x}'], 'av': [], 'type': None, 'dit': None})
            continue
        e = brut.get('entree')
        r = {'t': t, 'v': v, 'e': None, 'raison': brut.get('raison'), 'err': [], 'av': [], 'type': None, 'dit': brut.get('mouvement')}
        if e:
            e = {'cadres': [[round(float(x), 3) for x in k] for k in e.get('cadres') or [] if isinstance(k, list)],
                 'duree': e.get('duree', 5), 'intention': (e.get('intention') or '').strip()}
            r['e'] = e
            if v['image'].get('camera') != t['camera']:
                r['err'] = ['caméra changée depuis la préparation']
            else:
                permis = budget(v, plans)[0]
                r['err'], r['av'] = controler(v, e, t['visages'], permis)
                if r['err'] and all(re.search('zoom total|entrée jouée|durée', x) for x in r['err']):
                    e2 = reparer(v, e, t['visages'], permis)
                    if e2:
                        r['e'], (r['err'], r['av']) = e2, controler(v, e2, t['visages'], permis)
                        r['av'] = ['RÉPARÉE (moins ample)'] + r['av']
            if not r['err']:
                r['type'] = type_mouvement(v, e)
        sortie.append(r)
    return slug, sortie


def planche(a) -> int:
    slug, R = reponses(a)
    racine = charger(a.dossier)[0]
    cases = []
    for r in R:
        if not r['e'] or (r['err'] and not a.tout):
            continue
        im = image_tache(slug, r['v'], 520, r['e'], grille=False)
        case = Image.new('RGB', (530, 470), (255, 255, 255))
        case.paste(im, ((530 - im.width) // 2, 0))
        g = ImageDraw.Draw(case)
        y = min(im.height, 400) + 2
        g.text((4, y), f"{r['v']['n']} · {r['type'] or 'REFUS'} (dit : {r['dit']}) · {r['e'].get('duree')} s"
               + (' · ' + '; '.join(r['err'] + r['av'])[:60] if r['err'] or r['av'] else ''), fill=(200, 0, 0) if r['err'] or r['av'] else (0, 0, 0), font=cam._police(13))
        for j, ligne in enumerate(textwrap.wrap(r['e'].get('intention', ''), 84)[:3]):
            g.text((4, y + 16 + 14 * j), ligne, fill=(60, 60, 60), font=cam._police(12))
        cases.append(case)
    for k in range(0, len(cases), 9):
        f = racine / f"planche-{Path(a.dossier).resolve().name}-{k // 9 + 1:02d}.jpg"
        mosaique(cases[k:k + 9], 3).save(f, 'JPEG', quality=82)
        print(f'planche : {f}')
    for r in R:
        if not r['e']:
            print(f"  {r['v']['n']} : pas d'entrée ({r['raison'] or '; '.join(r['err'])})")
        elif r['err'] or r['av']:
            print(f"  {r['v']['n']} : {'REFUS ' if r['err'] else ''}{'; '.join(r['err'] + r['av'])}")
    return 0


def poser(slug: str, entrees: dict) -> int:
    """Relit le JSON et n'y écrit que ces champs `entree` (clé : n de la vue ; None : retirer)."""
    f, d = c.lire(slug)
    nb = 0
    for v in c.vues_camera(d, series=False):
        cle = str(v['n'])
        if cle in entrees:
            if entrees[cle] is None:
                nb += v['image'].pop('entree', None) is not None
            else:
                v['image']['entree'] = entrees[cle]
                nb += 1
    c.ecrire(f, d)
    return nb


def appliquer(a) -> int:
    slug, R = reponses(a)
    sauf = set(a.sauf or [])
    bons = {str(r['v']['n']): r for r in R if r['e'] and not r['err'] and str(r['v']['n']) not in sauf and not r['v']['image'].get('entree')}
    types = {}
    for r in bons.values():
        types[r['type']] = types.get(r['type'], 0) + 1
    print(f"{'À poser' if a.essai else 'Posées'} : {len(bons)} entrée(s) sur {len(R)} réponse(s) ({', '.join(f'{k} {n}' for k, n in types.items())}) : {' '.join(bons)}")
    for r in R:
        if r['e'] and r['err']:
            print(f"  refus {r['v']['n']} : {'; '.join(r['err'])}")
    if not a.essai and bons:
        poser(slug, {n: r['e'] for n, r in bons.items()})
    return 0


def retirer(a) -> int:
    print(f"{poser(json.loads(c.fichier_periode(a.slug).read_text())['slug'], {str(n): None for n in a.n})} entrée(s) retirée(s)")
    return 0


def bilan(a) -> int:
    d = json.loads(c.fichier_periode(a.slug).read_text())
    types = {}
    for v in vues(d):
        e = v['image'].get('entree')
        if e:
            t = type_mouvement(v, e)
            types.setdefault(t, []).append(str(v['n']))
            if a.detail:
                print(f"  {instant_diapo(d, v)} · {t} · {e.get('duree', 5)} s · {e.get('intention')}")
    print(f"{d['slug']} : {sum(map(len, types.values()))} entrée(s) : " + ' ; '.join(f'{t} {len(ns)} ({" ".join(ns)})' for t, ns in types.items()))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='commande', required=True)

    def cmd(nom_, f, *args):
        q = s.add_parser(nom_)
        for noms, kw in args:
            q.add_argument(*noms, **kw)
        q.set_defaults(f=f)
    slug, plans = (['slug'], {}), (['--plans'], {'help': 'relevé du lecteur (commande `plans`)'})
    cmd('candidates', candidates, slug, plans, (['--planches'], {'help': 'dossier des planches de vignettes'}))
    cmd('regle', regle_posees, slug, plans)
    cmd('plans', releve, slug, (['--dist'], {'required': True}), (['--sortie'], {'required': True}))
    cmd('preparer', preparer, slug, plans, (['--n'], {'nargs': '+', 'required': True}), (['--lot'], {'type': int, 'default': 15}),
        (['--force'], {'action': 'store_true', 'help': 'même les vues écartées par le tri mécanique'}))
    cmd('planche', planche, (['dossier'], {}), (['--tout'], {'action': 'store_true', 'help': 'aussi les réponses refusées'}))
    cmd('appliquer', appliquer, (['dossier'], {}), (['--essai'], {'action': 'store_true'}), (['--sauf'], {'nargs': '+'}))
    cmd('retirer', retirer, slug, (['--n'], {'nargs': '+', 'required': True}))
    cmd('etapes', etapes, slug, (['--avant'], {'required': True}), (['--apres'], {'required': True}))
    cmd('bilan', bilan, slug, (['--detail'], {'action': 'store_true'}))
    a = p.parse_args()
    return a.f(a)


if __name__ == '__main__':
    sys.exit(main())
