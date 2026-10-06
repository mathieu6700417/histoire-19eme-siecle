"""Recrée le gabarit d'un chapitre à partir de son MDX publié.

Usage : python3 scripts/ecrivains/gabarit.py <slug> [--sortie fichier]
À lancer quand l'appareil (chapeau, notes, regard…) a été retouché directement dans le
MDX, pour que la prochaine génération ne perde pas ces retouches : le texte de chaque
extrait est remplacé par @@T:id@@ et son lien par @@L:id@@.
"""
import argparse, re
from pathlib import Path
from extraits import DOSSIER, charger
from wikisource import RACINE

ap = argparse.ArgumentParser()
ap.add_argument('slug')
ap.add_argument('--sortie')
a = ap.parse_args()
data = charger(a.slug)
s = (RACINE / data['sortie']).read_text()
motif = re.compile(r'(<Extrait auteur="[^"]+"[^>]*?id="([^"]+)"[\s\S]*?lien=")([^"]+)("[\s\S]*?<div slot="texte">\n\n)([\s\S]*?)(\n\n</div>\s*<div slot="critique">)')
s, n = motif.subn(lambda m: f'{m[1]}@@L:{m[2]}@@{m[4]}@@T:{m[2]}@@{m[6]}', s)
sortie = Path(a.sortie) if a.sortie else DOSSIER / data['gabarit']
sortie.write_text(s)
print(f'{sortie} : {n} extraits')
