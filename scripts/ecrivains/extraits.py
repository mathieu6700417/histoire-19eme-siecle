"""Extraction des textes d'un chapitre à partir de sa spécification JSON.

Chaque extrait est décrit par la page Wikisource et une liste de segments :
  {"debut": "…", "fin": "…"}  sous-chaîne exacte, du marqueur de début jusqu'au marqueur
                               de fin inclus, sur un ou plusieurs paragraphes consécutifs ;
  "CUT"                        coupure, affichée « […] » dans un paragraphe à part.
Un poème est décrit par {"poeme": {"debut": premier vers, "fin": dernier vers, "strophe": 6}} :
les vers sont pris ligne à ligne et regroupés en strophes de la taille indiquée.
"""
import json, sys
from pathlib import Path
from wikisource import paragraphes

DOSSIER = Path(__file__).resolve().parent / 'chapitres'


def charger(slug: str) -> dict:
    f = DOSSIER / f'{slug}.json'
    if not f.exists():
        sys.exit(f'Spécification introuvable : {f}')
    return json.loads(f.read_text())


def _segment(P: list[str], debut: str, fin: str, page: str) -> list[str]:
    for i, p in enumerate(P):
        pos = p.find(debut)
        if pos < 0:
            continue
        for j in range(i, len(P)):
            fin_pos = P[j].find(fin, pos if j == i else 0)
            if fin_pos >= 0:
                fin_pos += len(fin)
                if i == j:
                    return [P[i][pos:fin_pos].strip()]
                return [P[i][pos:].strip(), *P[i + 1:j], P[j][:fin_pos].strip()]
        raise ValueError(f'{page} : fin introuvable après « {debut[:40]}… » : « {fin[-40:]} »')
    raise ValueError(f'{page} : début introuvable : « {debut[:50]} »')


def extraire(spec: dict) -> list[str]:
    """Paragraphes de l'extrait (avec « […] » pour les coupures)."""
    page = spec['page']
    if 'poeme' in spec:
        po = spec['poeme']
        V = paragraphes(page, vers=True)
        i = V.index(po['debut'])
        j = V.index(po['fin'], i)
        vers = V[i:j + 1]
        n = po.get('strophe', 0) or len(vers)
        if len(vers) % n:
            raise ValueError(f'{page} : {len(vers)} vers, non divisible en strophes de {n}')
        return ['\n'.join(vers[x:x + n]) for x in range(0, len(vers), n)]
    P = paragraphes(page)
    out = []
    for s in spec['segments']:
        out += ['[…]'] if s == 'CUT' else _segment(P, s['debut'], s['fin'], page)
    return out


if __name__ == '__main__':
    # Usage : python3 extraits.py <slug> [id]  → affiche les textes et leur nombre de mots.
    slug = sys.argv[1]
    data = charger(slug)
    for k, spec in data['extraits'].items():
        if len(sys.argv) > 2 and k != sys.argv[2]:
            continue
        ps = extraire(spec)
        mots = sum(len(p.split()) for p in ps if p != '[…]')
        i, j = spec['cle']
        cle = sum(len(p.split()) for p in ps[i:j + 1])
        print(f'{k:22s} {mots:5d} mots, passage clé {cle:4d} mots')
        if len(sys.argv) > 2:
            for n, p in enumerate(ps):
                print(f'[{n}] {p}\n')
