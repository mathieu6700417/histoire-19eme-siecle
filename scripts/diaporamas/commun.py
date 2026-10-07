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


def lire(slug: str) -> tuple[Path, dict]:
    f = fichier_periode(slug)
    return f, json.loads(f.read_text())


def ecrire(f: Path, donnees: dict) -> None:
    """Réécrit le script (indentation de 2, accents en clair). Écriture atomique."""
    tmp = f.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(f)


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
