"""Aide à la rédaction : affiche les paragraphes numérotés d'une page Wikisource.

Usage : python3 scripts/ecrivains/voir.py "Titre/de/la/page" [début fin] [--vers]
Chaque ligne indique le numéro du paragraphe, son nombre de mots et son début, pour
choisir un extrait (puis recopier les marqueurs de début et de fin dans la spécification).
"""
import sys
from wikisource import paragraphes, url_page

args = [a for a in sys.argv[1:] if a != '--vers']
titre = args[0]
P = paragraphes(titre, vers='--vers' in sys.argv)
a = int(args[1]) if len(args) > 1 else 0
b = int(args[2]) if len(args) > 2 else len(P)
print(url_page(titre))
for i, p in enumerate(P[a:b], a):
    print(f'[{i}] ({len(p.split())} mots) {p[:150]}')
