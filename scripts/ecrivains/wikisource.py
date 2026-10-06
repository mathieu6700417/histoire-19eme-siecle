"""Accès à Wikisource et mise en texte des pages, pour la section « écrivains ».

Fonctions partagées par extraire.py, generer.py et verifier.py. Les pages
téléchargées sont mises en cache dans .cache/wikisource/ (ignoré par git).
"""
import hashlib, html, json, re, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
CACHE = RACINE / '.cache' / 'wikisource'
API = 'https://fr.wikisource.org/w/api.php'
WIKI = 'https://fr.wikisource.org/wiki/'
UA = {'User-Agent': 'xixe-siecle-verification/1.0 (site d apprentissage, usage personnel)'}


def url_page(titre: str) -> str:
    """URL publique d'une page (titre avec ou sans soulignés)."""
    return WIKI + urllib.parse.quote(titre.replace(' ', '_'), safe="/(),_")


def _get(url: str) -> bytes:
    for essai in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(5 * (essai + 1))
    raise RuntimeError(f'Wikisource refuse les requêtes (429) : {url}')


def html_parse(titre: str, cache: bool = True) -> str:
    """HTML rendu d'une page, via l'API « parse » (mis en cache si demandé)."""
    cle = hashlib.sha1(titre.encode()).hexdigest()
    fichier = CACHE / f'{cle}.json'
    if cache and fichier.exists():
        return json.loads(fichier.read_text())['html']
    q = urllib.parse.urlencode({'action': 'parse', 'page': titre.replace('_', ' '), 'prop': 'text', 'format': 'json', 'redirects': 1})
    d = json.loads(_get(f'{API}?{q}'))
    if 'error' in d:
        raise RuntimeError(f'Page introuvable sur Wikisource : {titre} ({d["error"].get("info")})')
    h = d['parse']['text']['*']
    if cache:
        CACHE.mkdir(parents=True, exist_ok=True)
        fichier.write_text(json.dumps({'titre': titre, 'html': h}, ensure_ascii=False))
    time.sleep(1)
    return h


def html_vers_texte(h: str) -> str:
    """Texte brut : un bloc (paragraphe, ligne, titre) par ligne ; numéros de page et appels de note retirés."""
    h = re.sub(r'<span[^>]*class="[^"]*(pagenum|ws-pagenum)[^"]*"[^>]*>.*?</span>', '', h, flags=re.S)
    h = re.sub(r'<sup[^>]*class="reference"[^>]*>.*?</sup>', '', h, flags=re.S)
    h = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', h, flags=re.S)
    h = re.sub(r'<br\s*/?>', '\n', h)
    h = re.sub(r'</?(p|div|h\d|li|tr|dd|dt)[^>]*>', '\n', h)
    t = html.unescape(re.sub(r'<[^>]+>', '', h))
    return re.sub(r'\n\s*\n+', '\n\n', t)


def normaliser(s: str) -> str:
    """Espaces normalisées (insécables comprises) ; espace parasite avant une virgule retirée."""
    s = s.replace('﻿', '').replace(' ', ' ').replace(' ', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.replace(' ,', ',')


def paragraphes(titre: str, vers: bool = False) -> list[str]:
    """Paragraphes d'une page. En prose, les lignes d'un même paragraphe sont rejointes ;
    avec vers=True, chaque ligne du texte source est gardée telle quelle."""
    t = html_vers_texte(html_parse(titre))
    if not vers:
        t = re.sub(r'[ \t]*\n(?![ \t]*\n)', ' ', t)
    return [p.strip() for p in normaliser(t).split('\n') if p.strip()]


def texte_de_page(url: str) -> str:
    """Texte d'une page publique (pour la vérification), tel qu'on le lit à l'URL."""
    h = _get(url).decode()
    h = re.sub(r'<sup[^>]*class="reference"[^>]*>.*?</sup>', '', h, flags=re.S)
    return h
