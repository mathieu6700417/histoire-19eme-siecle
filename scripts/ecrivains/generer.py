"""Assemble le fichier MDX d'un chapitre de la section « écrivains ».

Usage : python3 scripts/ecrivains/generer.py <slug> [--sortie fichier.mdx]

Entrées (dans scripts/ecrivains/chapitres/) :
  <slug>.json          page Wikisource, segments, passage clé et ancres de chaque extrait ;
  <slug>.gabarit.mdx   le chapitre rédigé, où @@T:id@@ marque le texte de l'extrait
                       et @@L:id@@ son lien Wikisource.
Pour chaque extrait : texte exact extrait de Wikisource, passage clé encadré par
<div class="cle">, appels de note insérés après le « mot » de chaque note (dans l'ordre
du texte ; une ancre différente peut être donnée dans "ancres"), lien vers la page.
"""
import argparse, re, sys
from pathlib import Path
from extraits import DOSSIER, charger, extraire
from wikisource import RACINE, url_page

CLE_MIN, CLE_MAX = 150, 350


def mots_des_notes(gabarit: str, k: str) -> list[str]:
    # L'ouverture du <Extrait> (et non le premier id="…" venu : une <Oeuvre> peut précéder).
    bloc = gabarit[re.search(rf'<Extrait\b[^>]*?\bid="{re.escape(k)}"', gabarit).start():]
    bloc = bloc[:bloc.index('</Extrait>')]
    return re.findall(r'\{ mot: "([^"]+)"', bloc.split(']}>')[0])


def texte_extrait(k: str, paras: list[str], cle: list[int], mots: list[str], ancres: dict) -> str:
    i, j = cle
    paras = list(paras)
    if '[…]' in paras[i:j + 1]:
        sys.exit(f'{k} : le passage clé contient une coupure')
    n = sum(len(p.split()) for p in paras[i:j + 1])
    if not CLE_MIN <= n <= CLE_MAX:
        sys.exit(f'{k} : passage clé de {n} mots (attendu {CLE_MIN}-{CLE_MAX})')
    paras[i] = '<div class="cle">\n\n' + paras[i]
    paras[j] += '\n\n</div>'
    t, pos = '\n\n'.join(paras), 0
    for n, mot in enumerate(mots, 1):
        a = ancres.get(mot, mot.replace("'", '’'))
        x = t.find(a, pos)
        if x < 0:
            sys.exit(f'{k} : ancre « {a} » ' + ('hors d’ordre' if t.find(a) >= 0 else 'introuvable'))
        x += len(a)
        tag = f'<Appel ex="{k}" n={{{n}}} />'
        t = t[:x] + tag + t[x:]
        pos = x + len(tag)
    return re.sub(r'(?m)^(\d)o ', r'\1<sup>o</sup> ', t)  # « 1o » de l'édition → 1º


def generer(slug: str) -> str:
    data = charger(slug)
    s = (DOSSIER / data['gabarit']).read_text()
    for k, spec in data['extraits'].items():
        t = texte_extrait(k, extraire(spec), spec['cle'], mots_des_notes(s, k), data.get('ancres', {}).get(k, {}))
        s = s.replace(f'@@T:{k}@@', t).replace(f'@@L:{k}@@', url_page(spec['page']))
    reste = re.findall(r'@@[^@]+@@', s)
    if reste:
        sys.exit(f'Marques non remplacées : {reste}')
    return s


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--sortie', help='fichier de sortie (par défaut : celui de la spécification)')
    a = ap.parse_args()
    s = generer(a.slug)
    sortie = Path(a.sortie) if a.sortie else RACINE / charger(a.slug)['sortie']
    sortie.write_text(s)
    print(f'{sortie} : {s.count("<Extrait ")} extraits')
