"""Vérifie les extraits publiés de la section « écrivains » contre Wikisource.

Usage : python3 scripts/ecrivains/verifier.py <slug> [<slug>…]
        python3 scripts/ecrivains/verifier.py --tous      (tous les src/content/ecrivains/*.mdx)
        (npm run verifier:ecrivains)

Pour chaque <Extrait> du MDX :
  1. la page à l'URL du lien répond (HTTP 200), téléchargée à neuf, sans cache ;
  2. chaque paragraphe (ou vers) du texte figure mot pour mot dans cette page
     (appels de note retirés des deux côtés, espaces normalisées) ;
  3. le texte complet fait 400 à 900 mots (pour un poème, prop `poeme`, pas de minimum) ;
  4. il y a exactement un passage clé <div class="cle">, de 150 à 350 mots,
     contenu tel quel dans le texte complet.
Code de sortie 1 si un contrôle échoue.
"""
import html, re, sys, time, urllib.error
from wikisource import RACINE, _get

DOSSIER_MDX = RACINE / 'src' / 'content' / 'ecrivains'
TEXTE = (400, 900)
CLE = (150, 350)
EXTRAIT = re.compile(r'(<Extrait auteur="[^"]+"[^>]*?id="([^"]+)"[\s\S]*?lien="([^"]+)"[\s\S]*?)<div slot="texte">([\s\S]*?)</div>\s*<div slot="critique">')
POEME = re.compile(r'\spoeme(?=[\s>=])')


def norm(s: str) -> str:
    s = html.unescape(s).replace('﻿', '').replace(' ', ' ').replace(' ', ' ').replace(' ', ' ')
    s = re.sub(r'\s*\[\d+\]', '', s)  # appels de note et numéros de page de l'édition
    return re.sub(r'\s+', ' ', s).replace(' ,', ',')


def page(url: str):
    try:
        h = _get(url).decode()
    except urllib.error.HTTPError as e:
        return e.code, '', ''
    h = re.sub(r'<sup[^>]*class="reference"[^>]*>.*?</sup>', '', h, flags=re.S)
    h = re.sub(r'<span[^>]*pagenum[^>]*>\s*</span>', '', h)
    return 200, norm(re.sub(r'<[^>]+>', ' ', h)), norm(re.sub(r'<[^>]+>', '', h))


def mots(s: str) -> int:
    return len(norm(re.sub(r'<[^>]+>', '', s.replace('[…]', ''))).split())


def verifier(slug: str) -> tuple[int, int]:
    mdx = (DOSSIER_MDX / f'{slug}.mdx').read_text()
    bons = total = 0
    print(f'\n== {slug}')
    for m in EXTRAIT.finditer(mdx):
        entete, ex, lien, t = m.groups()
        poeme = bool(POEME.search(entete.split('<div slot=')[0]))
        total += 1
        erreurs = []
        code, p1, p2 = page(lien)
        if code != 200:
            erreurs.append(f'HTTP {code} pour {lien}')
        t = re.sub(r'<Appel[^>]*/>', '', t)
        t = re.sub(r'</?sup>', '', t)
        cles = re.findall(r'<div class="cle">([\s\S]*?)</div>', t)
        t = re.sub(r'</?div[^>]*>', '', t)
        n = mots(t)
        if not (0 if poeme else TEXTE[0]) <= n <= TEXTE[1]:
            erreurs.append(f'texte complet de {n} mots (attendu {TEXTE[0]}-{TEXTE[1]})')
        nc = 0
        if len(cles) != 1:
            erreurs.append(f'{len(cles)} passage(s) clé(s) au lieu de 1')
        else:
            nc = mots(cles[0])
            if not CLE[0] <= nc <= CLE[1]:
                erreurs.append(f'passage clé de {nc} mots (attendu {CLE[0]}-{CLE[1]})')
            if norm(re.sub(r'<[^>]+>', '', cles[0])).strip() not in norm(t):
                erreurs.append('passage clé absent du texte complet')
        morceaux = [x.strip() for x in re.split(r'\n', t) if x.strip() and x.strip() != '[…]']
        if code == 200:
            for x in morceaux:
                if norm(x) not in p1 and norm(x) not in p2:
                    erreurs.append(f'introuvable à l’URL : {x[:100]}…')
        etat = 'ok ' if not erreurs else 'ÉCHEC'
        print(f'  {etat} {ex:22s} {len(morceaux):3d} {"vers    " if poeme else "morceaux"}, {n:4d} mots, passage clé {nc:3d} mots')
        for e in erreurs:
            print(f'       - {e}')
        bons += not erreurs
        time.sleep(1)
    return bons, total


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    slugs = sorted(f.stem for f in DOSSIER_MDX.glob('*.mdx')) if args == ['--tous'] else args
    bons = total = 0
    for s in slugs:
        b, t = verifier(s)
        bons, total = bons + b, total + t
    print(f'\n{bons}/{total} extraits vérifiés' + ('' if bons == total else f' — {total - bons} en échec'))
    sys.exit(0 if bons == total and total else 1)
