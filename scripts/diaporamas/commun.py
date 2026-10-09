"""Bibliothèque commune de la chaîne « Le siècle en images » (spec 12).

Chemins, lecture et écriture du script d'une période, accès à l'API Wikimedia Commons,
lexique de prononciation. Les scripts images.py, voix.py et verifier.py l'importent.
Bibliothèque standard seulement, sauf Pillow (dans images.py) pour le WebP.
"""
import html, json, os, re, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DONNEES = RACINE / 'src' / 'data' / 'diaporamas'
PUBLIC = RACINE / 'public' / 'diaporamas'
CACHE = RACINE / '.cache' / 'diaporamas'
LEXIQUE = Path(__file__).resolve().parent / 'prononciation.yaml'

API_COMMONS = 'https://commons.wikimedia.org/w/api.php'
# User-Agent explicite et en ASCII (Wikimedia refuse les agents génériques).
UA = 'xixe-siecle-diaporamas/1.0 (site d apprentissage, usage personnel; mathieu6700417@gmail.com)'


# --- Script d'une période -------------------------------------------------------------

def fichier_periode(slug: str) -> Path:
    """src/data/diaporamas/NN-<slug>.json (on accepte aussi « NN-slug » ou le nom complet)."""
    slug = slug.removesuffix('.json')
    for f in sorted(DONNEES.glob('*.json')):
        if f.stem == slug or re.sub(r'^\d+-', '', f.stem) == slug:
            return f
    raise SystemExit(f'Script introuvable pour « {slug} » dans {DONNEES.relative_to(RACINE)}/')


# Écriture sûre : plusieurs scripts (voix.py, utile.py, camera.py, musique.py…) peuvent
# tourner en même temps sur le même JSON. Chacun garde la version qu'il a lue (« base ») ;
# à l'écriture, sous verrou de fichier, on relit le disque et on n'y reporte que les champs
# que CE script a changés depuis sa base (fusion à trois voies). Si un autre script a changé
# le même champ autrement entre-temps, on refuse explicitement (ConflitEcriture).

class ConflitEcriture(SystemExit):
    pass


_MANQUE = object()
_BASES: dict[int, tuple[dict, object]] = {}     # id(données) -> (données, copie de la base)


def _copie(v):
    return json.loads(json.dumps(v))


def _fusion(base, nous, eux, chemin: str):
    """Fusion à trois voies de valeurs JSON ; _MANQUE = clé absente."""
    if nous == base:
        return eux
    if eux == base or eux == nous:
        return nous
    if isinstance(base, dict) and isinstance(nous, dict) and isinstance(eux, dict):
        r = {}
        for k in list(eux) + [k for k in nous if k not in eux]:
            v = _fusion(base.get(k, _MANQUE), nous.get(k, _MANQUE), eux.get(k, _MANQUE), f'{chemin}.{k}')
            if v is not _MANQUE:
                r[k] = v
        return r
    if (isinstance(base, list) and isinstance(nous, list) and isinstance(eux, list)
            and len(base) == len(nous) == len(eux)):
        return [_fusion(b, n, e, f'{chemin}[{i}]') for i, (b, n, e) in enumerate(zip(base, nous, eux))]
    raise ConflitEcriture(f'Écriture refusée : « {chemin or "racine"} » a été modifié par un autre script '
                          f'depuis la lecture. Relancer ce script (ses caches évitent de refaire le travail).')


def _verrou(f: Path):
    import fcntl
    v = CACHE / 'verrous' / (f.name + '.lock')
    v.parent.mkdir(parents=True, exist_ok=True)
    h = v.open('w')
    fcntl.flock(h, fcntl.LOCK_EX)
    return h


def _suivre(donnees: dict) -> None:
    _BASES[id(donnees)] = (donnees, _copie(donnees))


def lire(slug: str) -> tuple[Path, dict]:
    f = fichier_periode(slug)
    d = json.loads(f.read_text())
    _suivre(d)
    return f, d


def ecrire(f: Path, donnees: dict) -> None:
    """Écrit le script (indentation de 2, accents en clair), atomiquement et sous verrou.

    Si `donnees` vient de lire(), seuls les champs modifiés depuis la lecture (ou depuis la
    dernière écriture) sont reportés sur la version du disque : les changements faits
    entre-temps par un autre script sont conservés. Conflit sur un même champ : refus.
    """
    h = _verrou(f)
    try:
        suivi = _BASES.get(id(donnees))
        if suivi and suivi[0] is donnees and f.exists():
            disque = json.loads(f.read_text())
            final = _fusion(suivi[1], _copie(donnees), disque, '')
        else:
            final = donnees
        tmp = f.with_suffix(f'.json.{os.getpid()}.tmp')
        tmp.write_text(json.dumps(final, ensure_ascii=False, indent=2) + '\n')
        tmp.replace(f)
        _suivre(donnees)        # nouvelle base : ce que ce script a déjà reporté
    finally:
        h.close()


def nom(n: int, ext: str) -> str:
    return f'{n:03d}.{ext}'


# --- Environnement --------------------------------------------------------------------

def charger_env() -> None:
    """Lit .env (CLE=valeur) sans écraser l'environnement existant."""
    f = RACINE / '.env'
    if not f.exists():
        return
    for ligne in f.read_text().splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith('#') or '=' not in ligne:
            continue
        cle, val = ligne.split('=', 1)
        os.environ.setdefault(cle.strip(), val.strip().strip('"').strip("'"))


# --- Lexique de prononciation ---------------------------------------------------------

def charger_lexique() -> dict[str, str]:
    """prononciation.yaml : une ligne « Mot: graphie » par entrée (YAML plat, sans imbrication)."""
    lexique: dict[str, str] = {}
    if not LEXIQUE.exists():
        return lexique
    for ligne in LEXIQUE.read_text().splitlines():
        if not ligne.strip() or ligne.lstrip().startswith('#') or ':' not in ligne:
            continue
        mot, graphie = ligne.split(':', 1)
        lexique[mot.strip().strip('"\'')] = graphie.strip().strip('"\'')
    return lexique


def appliquer_lexique(texte: str, lexique: dict[str, str]) -> str:
    """Remplace les entrées du lexique (mots entiers), les plus longues d'abord."""
    for mot in sorted(lexique, key=len, reverse=True):
        texte = re.sub(rf'(?<![\w-]){re.escape(mot)}(?![\w-])', lexique[mot], texte)
    return texte


# --- Wikimedia Commons ----------------------------------------------------------------

def http_get(url: str, essais: int = 6) -> bytes:
    for essai in range(essais):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            return urllib.request.urlopen(req, timeout=120).read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or essai == essais - 1:
                raise
            time.sleep(5 * (essai + 1))
        except urllib.error.URLError:
            if essai == essais - 1:
                raise
            time.sleep(5 * (essai + 1))
    raise RuntimeError(url)


def api_commons(**params) -> dict:
    params = {'format': 'json', 'formatversion': 2, **params}
    return json.loads(http_get(f'{API_COMMONS}?{urllib.parse.urlencode(params)}'))


def texte_meta(valeur: str | None) -> str:
    """Texte visible d'un champ extmetadata (sans les blocs cachés Wikidata ni balises)."""
    if not valeur:
        return ''
    visible = re.sub(r'<div style="display:\s*none;?">.*?</div>', '', valeur, flags=re.S)
    visible = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', visible, flags=re.S)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', visible)).split())


def titre_objet(valeur: str | None) -> str:
    """Titre d'une œuvre : la version française si le modèle Artwork en donne plusieurs."""
    if not valeur:
        return ''
    fr = re.search(r'lang="fr"[^>]*>(.*?)</div>', valeur, flags=re.S)
    if fr:
        return texte_meta(fr.group(1))
    libelle = re.search(r'label QS:Lfr,"(.*?)"', valeur, flags=re.S)
    if libelle:
        return texte_meta(libelle.group(1))
    return texte_meta(valeur)


def infos_fichiers(titres: list[str], largeur: int = 2400) -> dict[str, dict]:
    """Métadonnées de plusieurs fichiers Commons (`File:…`), par lots de 25.

    Renvoie {titre demandé: info} ; info vaut {'manquant': True} si le fichier n'existe pas.
    Les redirections et normalisations de titre sont suivies.
    """
    resultat: dict[str, dict] = {}
    for i in range(0, len(titres), 25):
        lot = [t if t.startswith('File:') else f'File:{t}' for t in titres[i:i + 25]]
        d = api_commons(action='query', titles='|'.join(lot), redirects=1, prop='imageinfo',
                        iiprop='url|size|mime|extmetadata', iiurlwidth=largeur,
                        iiextmetadatalanguage='fr')
        q = d.get('query', {})
        alias = {}
        for cle in ('normalized', 'redirects'):
            for x in q.get(cle, []):
                alias[x['from']] = x['to']
        pages = {p['title']: p for p in q.get('pages', [])}
        for t, demande in zip(lot, titres[i:i + 25]):
            final = t
            while final in alias:
                final = alias[final]
            p = pages.get(final)
            if not p or p.get('missing') or not p.get('imageinfo'):
                resultat[demande] = {'manquant': True}
                continue
            info = p['imageinfo'][0]
            meta = {k: v.get('value') for k, v in (info.get('extmetadata') or {}).items()}
            resultat[demande] = {
                'titre_fichier': p['title'],
                'url': info.get('url'),
                'vignette': info.get('thumburl') or info.get('url'),
                'page': info.get('descriptionurl'),
                'mime': info.get('mime'),
                'largeur': info.get('width'),
                'hauteur': info.get('height'),
                'meta': meta,
            }
        time.sleep(1)
    return resultat


LICENCE_PD = re.compile(r'^(public domain|domaine public|pd\b|pd-|cc0|cc-zero|no restrictions)', re.I)


def licence_libre(info: dict) -> tuple[bool, str]:
    """(domaine public ?, libellé brut). Seuls le domaine public et CC0 sont admis (spec 12)."""
    meta = info.get('meta', {})
    court = texte_meta(meta.get('LicenseShortName'))
    licence = texte_meta(meta.get('License'))
    libre = bool(LICENCE_PD.match(court) or LICENCE_PD.match(licence))
    # Garde-fou : jamais une licence CC BY / BY-SA / NC / ND, même mal étiquetée.
    if re.search(r'\bcc[- ]by\b|by-sa|\bnc\b|\bnd\b|gfdl', f'{court} {licence}', re.I):
        libre = False
    return libre, court or licence or 'inconnue'


def chercher(requete: str, nombre: int = 10) -> list[dict]:
    """Recherche plein texte de fichiers bitmap sur Commons (aide à l'écriture du script)."""
    d = api_commons(action='query', generator='search', gsrsearch=f'{requete} filetype:bitmap',
                    gsrnamespace=6, gsrlimit=nombre, prop='imageinfo',
                    iiprop='size|mime|extmetadata', iiextmetadatalanguage='fr',
                    iiextmetadatafilter='ObjectName|Artist|DateTimeOriginal|LicenseShortName')
    pages = sorted(d.get('query', {}).get('pages', []), key=lambda p: p.get('index', 0))
    sortie = []
    for p in pages:
        info = (p.get('imageinfo') or [{}])[0]
        meta = {k: v.get('value') for k, v in (info.get('extmetadata') or {}).items()}
        sortie.append({
            'fichier': p['title'], 'largeur': info.get('width'), 'hauteur': info.get('height'),
            'titre': titre_objet(meta.get('ObjectName'))[:90], 'auteur': texte_meta(meta.get('Artist'))[:60],
            'date': texte_meta(meta.get('DateTimeOriginal'))[:40],
            'licence': texte_meta(meta.get('LicenseShortName')),
        })
    return sortie


# --- Narration ------------------------------------------------------------------------

def phrases(texte: str) -> list[str]:
    """Découpe en phrases (point, point d'exclamation ou d'interrogation, points de suspension)."""
    morceaux = re.split(r'(?<=[.!?…])\s+(?=[«A-ZÀÂÉÈÊÎÔÛÇ0-9])', texte.strip())
    return [m for m in morceaux if m]


def nb_mots(texte: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ]+(?:[-'’][\wÀ-ÿ]+)*", texte))


def texte_lu(lecture: dict) -> str:
    """Texte lu d'une lecture : paragraphes sans les coupures « […] », joints par une espace ;
    les retours à la ligne des vers deviennent des espaces (mêmes positions de caractères que
    l'affichage ; même calcul que `texteLu` dans src/utils/diaporamas.ts)."""
    return ' '.join(b for b in lecture['texte'] if b.strip() != '[…]').replace('\n', ' ')


def mots_lus(texte: str) -> list[tuple[int, int, str]]:
    """Mots d'un texte lu, pour le minutage mot par mot des lectures : suites de caractères
    sans espace (insécables comprises) qui contiennent au moins une lettre ou un chiffre ;
    la ponctuation isolée (« ? », « : », « » ») n'en est pas un, le lecteur la rattache au mot
    voisin. (début, fin, mot) en caractères ; même découpage que `motsLus` dans
    src/utils/diaporamas.ts."""
    return [(m.start(), m.end(), m.group()) for m in re.finditer(r'\S+', texte)
            if any(ch.isalnum() for ch in m.group())]


# --- Chiffres clés et dates du calendrier républicain (spec 12, « Enrichissements visuels »,
# point 4, 2026-10-08) -------------------------------------------------------------------------

_UNITES = {'zéro': 0, 'un': 1, 'une': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5, 'six': 6, 'sept': 7,
           'huit': 8, 'neuf': 9, 'dix': 10, 'onze': 11, 'douze': 12, 'treize': 13, 'quatorze': 14,
           'quinze': 15, 'seize': 16, 'vingt': 20, 'vingts': 20, 'trente': 30, 'quarante': 40,
           'cinquante': 50, 'soixante': 60}
_MULT = {'cent': 100, 'cents': 100, 'mille': 1000, 'million': 10 ** 6, 'millions': 10 ** 6,
         'milliard': 10 ** 9, 'milliards': 10 ** 9}


def nombre_dit(texte: str) -> int | None:
    """Nombre écrit dans `texte`, en chiffres (« 1 300 », « 7 ») ou en toutes lettres (« trois cent
    mille », « vingt-neuf », « quatre-vingt-trois », « mille trois cents ») : la première suite de
    mots-nombres ; None s'il n'y en a pas."""
    m = re.search(r'\d[\d   ]*\d|\d', texte)
    mots = re.findall(r"[a-zà-ÿ]+", texte.lower().replace('-', ' '))
    suite, vu = [], False
    for w in mots:
        if w in _UNITES or w in _MULT or (w == 'et' and vu):
            suite.append(w)
            vu = True
        elif vu:
            break
    if not suite:
        return int(re.sub(r'\D', '', m.group())) if m else None
    total, courant = 0, 0
    for w in suite:
        if w == 'et':
            continue
        if w in _UNITES:
            # « quatre vingt » : 4 × 20 (aussi après une centaine : « deux cent quatre-vingt-un »)
            if _UNITES[w] == 20 and courant % 100 == 4:
                courant += 76
            else:
                courant += _UNITES[w]
        elif _MULT[w] == 100:
            courant = max(1, courant) * 100
        else:
            total += max(1, courant) * _MULT[w]
            courant = 0
    return total + courant


MOIS_REPUBLICAINS = ('vendémiaire', 'brumaire', 'frimaire', 'nivôse', 'pluviôse', 'ventôse', 'germinal',
                     'floréal', 'prairial', 'messidor', 'thermidor', 'fructidor')
# Années sextiles réellement appliquées (règle de l'équinoxe, tables officielles de l'Annuaire) :
# III, VII et XI (et XV, jamais atteinte). La « règle de Romme » (années multiples de 4), proposée
# mais jamais adoptée, donnerait d'autres dates à partir de l'an IV : on ne l'emploie pas.
ANS_SEXTILES = (3, 7, 11, 15)
_ROMAINS = {'I': 1, 'V': 5, 'X': 10}


def romain(texte: str) -> int:
    v = [_ROMAINS[ch] for ch in texte]
    return sum(-a if k + 1 < len(v) and a < v[k + 1] else a for k, a in enumerate(v))


def premier_vendemiaire(an: int):
    """Jour grégorien du 1er vendémiaire de l'an `an` (an I : 22 septembre 1792), en ajoutant la
    durée des années précédentes (366 jours pour une année sextile, 365 sinon)."""
    import datetime
    j = datetime.date(1792, 9, 22)
    for a in range(1, an):
        j += datetime.timedelta(days=366 if a in ANS_SEXTILES else 365)
    return j


def vers_gregorien(jour: int, mois: int, an: int):
    """Date grégorienne d'un jour républicain (`mois` de 1 à 12, 13 pour les sans-culottides)."""
    import datetime
    return premier_vendemiaire(an) + datetime.timedelta(days=30 * (mois - 1) + jour - 1)


def _date_fr(j) -> str:
    return f"{'1er' if j.day == 1 else j.day} {MOIS[j.month - 1]} {j.year}"


MOIS = ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre',
        'octobre', 'novembre', 'décembre')


def date_republicaine(texte: str) -> tuple[str, str] | None:
    """(« 9 thermidor an II », « 27 juillet 1794 ») pour une date républicaine complète
    (« 9 thermidor an II », « 1er prairial an III ») ; pour une année seule (« an III ») :
    (« an III », « 22 septembre 1794 – 22 septembre 1795 »). None si le texte n'en est pas une."""
    m = re.fullmatch(r'(?:(1er|\d{1,2}) (\w+) )?an ([IVX]+)', texte.strip())
    if not m:
        return None
    an = romain(m.group(3))
    if m.group(2) is None:
        import datetime
        d0, d1 = premier_vendemiaire(an), premier_vendemiaire(an + 1) - datetime.timedelta(days=1)
        return texte.strip(), f'{_date_fr(d0)} – {_date_fr(d1)}'
    if m.group(2) not in MOIS_REPUBLICAINS:
        return None
    jour = 1 if m.group(1) == '1er' else int(m.group(1))
    if not 1 <= jour <= 30:
        return None
    return texte.strip(), _date_fr(vers_gregorien(jour, MOIS_REPUBLICAINS.index(m.group(2)) + 1, an))
