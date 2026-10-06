"""Aide à la recherche de sources sur Wikisource.

Usage : python3 scripts/ecrivains/chercher.py "mots clés" [nombre]     recherche plein texte
        python3 scripts/ecrivains/chercher.py --sous-pages "Titre"     sous-pages d'une œuvre
Les titres obtenus servent de champ "page" dans la spécification JSON du chapitre.
"""
import json, re, sys, urllib.parse
from wikisource import API, _get, url_page

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
if args[0] == '--sous-pages':
    q = {'action': 'query', 'list': 'allpages', 'apnamespace': 0, 'aplimit': 500, 'format': 'json',
         'apprefix': args[1].replace('_', ' ').rstrip('/') + '/'}
    for p in json.loads(_get(f'{API}?{urllib.parse.urlencode(q)}'))['query']['allpages']:
        print(' -', p['title'].replace(' ', '_'))
else:
    q = {'action': 'query', 'list': 'search', 'format': 'json', 'srsearch': args[0],
         'srlimit': args[1] if len(args) > 1 else 8}
    for r in json.loads(_get(f'{API}?{urllib.parse.urlencode(q)}'))['query']['search']:
        print(' -', r['title'].replace(' ', '_'), '|', re.sub('<[^>]+>', '', r['snippet'])[:160])
        print('  ', url_page(r['title']))
