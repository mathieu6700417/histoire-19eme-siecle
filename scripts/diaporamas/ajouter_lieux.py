"""Ajoute aux diapositives de la Révolution les lieux de leurs médaillons à plusieurs lieux (spec 12,
« Cartes de lieu et citations en surimpression », révision du 2026-10-08 : « Plusieurs lieux sur
une diapositive »).

Usage :
    python3 scripts/diaporamas/ajouter_lieux.py                      # src/data/diaporamas/<siecle>/01-revolution.json
    python3 scripts/diaporamas/ajouter_lieux.py --fichier copie.json # une copie (essai)
    python3 scripts/diaporamas/ajouter_lieux.py --essai              # montre sans écrire

Idempotent : un lieu déjà présent (même `quand`) n'est ni ajouté ni modifié, et rien d'autre du
script n'est touché ; on peut relancer sans dommage. Les lieux d'une diapositive sont rangés dans
l'ordre où la narration les dit (chaque passage cherché après le début du précédent). Une
diapositive dont la narration ne contient plus un passage est passée, avec un message.

`instant` : repris du cache de surimpressions.py quand l'audio et le texte n'ont pas changé ;
sinon, lancer ensuite `python3 scripts/diaporamas/surimpressions.py revolution` (les nouveaux lieux
sans instant sont signalés par verifier.py ; le lecteur se replie au prorata en attendant).

Coordonnées : Wikidata (P625) pour chaque lieu nouveau (`wikidata` ci-dessous, non écrit dans le
JSON) ; un lieu déjà situé ailleurs dans la période reprend les coordonnées de sa première carte.
Un lieu de Paris placé avec des lieux de province est noté `fond: "france"`, nom « Paris » (le
lecteur le montrerait ainsi de toute façon ; voir `medaillonMultiple` dans src/utils/diaporamas.ts).
"""
import argparse, json, sys
from pathlib import Path

import commun as c

PARIS = {'nom': 'Paris', 'lon': 2.35222, 'lat': 48.85667, 'fond': 'france', 'wikidata': 'Q90'}

# n : lieux à ajouter (dans l'ordre de la narration ; les lieux déjà présents restent tels quels).
AJOUTS: dict[int, list[dict]] = {
    # Paris, 14 juillet au matin : des Invalides à la Bastille (plan de Verniquet).
    17: [
        {'nom': 'Bastille', 'quand': 'à la Bastille', 'lon': 2.36802, 'lat': 48.85318, 'fond': 'paris', 'wikidata': 'Q1865480'},
        {'nom': 'Faubourg Saint-Antoine', 'quand': 'le faubourg Saint-Antoine', 'lon': 2.3792, 'lat': 48.8505, 'fond': 'paris', 'wikidata': 'Q3067308'},
    ],
    # Les Jacobins (Paris) et Arras, la ville de Robespierre : carte de France.
    36: [{'nom': 'Arras', 'quand': "d'Arras", 'lon': 2.78, 'lat': 50.28917, 'fond': 'france', 'wikidata': 'Q131329'}],
    # Fuite de Varennes : départ des Tuileries, arrestation à Varennes (carte de France).
    39: [{'nom': 'Palais des Tuileries', 'quand': 'des Tuileries', 'lon': 2.33111, 'lat': 48.86222, 'fond': 'paris', 'wikidata': 'Q234364'}],
    # 17 juillet 1791 : pétition du Champ-de-Mars, lancée par les Cordeliers (plan de Verniquet).
    43: [{'nom': 'Champ-de-Mars', 'quand': 'au Champ-de-Mars', 'lon': 2.29803, 'lat': 48.85613, 'fond': 'paris', 'wikidata': 'Q217925'}],
    # La Marseillaise : Strasbourg, les volontaires de Marseille, Paris.
    47: [
        {'nom': 'Marseille', 'quand': 'marseillais', 'lon': 5.37639, 'lat': 43.29667, 'fond': 'france', 'wikidata': 'Q23482'},
        {**PARIS, 'quand': 'à Paris pendant'},
    ],
    # La méridienne, de Dunkerque à Barcelone : France et voisins.
    51: [{'nom': 'Barcelone', 'quand': 'à Barcelone', 'lon': 2.17694, 'lat': 41.3825, 'fond': 'voisins', 'wikidata': 'Q1492'}],
    # Août-septembre 1792 : Longwy, Verdun, et Paris qui craint les prisons.
    55: [
        {'nom': 'Longwy', 'quand': 'prennent Longwy', 'lon': 5.76056, 'lat': 49.51972, 'fond': 'france', 'wikidata': 'Q318535'},
        {**PARIS, 'quand': 'à Paris, on craint'},
    ],
    # Révolte fédéraliste : Lyon, Marseille, Bordeaux, Toulon.
    72: [
        {'nom': 'Marseille', 'quand': 'Marseille', 'lon': 5.37639, 'lat': 43.29667, 'fond': 'france', 'wikidata': 'Q23482'},
        {'nom': 'Bordeaux', 'quand': 'Bordeaux', 'lon': -0.57944, 'lat': 44.83778, 'fond': 'france', 'wikidata': 'Q1479'},
        {'nom': 'Toulon', 'quand': 'Toulon', 'lon': 5.93056, 'lat': 43.125, 'fond': 'france', 'wikidata': 'Q44160'},
    ],
    # Télégraphe Chappe : la Convention, à Paris, apprend la reprise du Quesnoy.
    101: [{**PARIS, 'quand': 'la Convention apprend'}],
    # Terreur blanche : les prisons de Lyon et de Marseille.
    107: [{'nom': 'Lyon', 'quand': 'de Lyon', 'lon': 4.835, 'lat': 45.7675, 'fond': 'france', 'wikidata': 'Q456'}],
    # Campo-Formio, puis le triomphe de Bonaparte à Paris (palais du Luxembourg).
    115: [{**PARIS, 'quand': 'au palais du Luxembourg'}],
    # 18 fructidor : Paris occupé, déportation en Guyane (carte du monde).
    116: [{**PARIS, 'quand': 'occuper Paris'}],
    # Œuvres saisies en Italie : de Venise à Paris.
    119: [
        {**PARIS, 'quand': 'à Paris'},
        {'nom': 'Venise', 'quand': 'Saint-Marc de Venise', 'lon': 12.33194, 'lat': 45.43972, 'fond': 'voisins', 'wikidata': 'Q641'},
    ],
    # Égypte : les Pyramides, puis la flotte détruite à Aboukir.
    122: [{'nom': 'Aboukir', 'quand': 'à Aboukir', 'lon': 30.06667, 'lat': 31.31667, 'fond': 'europe', 'wikidata': 'Q139773'}],
}
CLES = ('nom', 'quand', 'lon', 'lat', 'fond')


def ordonner(narration: str, lieux: list[dict]) -> list[dict] | None:
    """Lieux rangés dans l'ordre de la narration (passage cherché après le début du précédent) ;
    None si un passage manque."""
    restants, sortie, depuis = list(lieux), [], 0
    while restants:
        poss = [(narration.find(li['quand'], depuis), k) for k, li in enumerate(restants)]
        poss = [(p, k) for p, k in poss if p >= 0]
        if not poss:
            return None
        p, k = min(poss)
        sortie.append(restants.pop(k))
        depuis = p + 1
    return sortie


def instants_du_cache(slug: str, x: dict) -> list | None:
    """Instants des mots de la narration (cache de surimpressions.py), s'ils sont à jour."""
    from surimpressions import empreinte_audio
    f = c.CACHE / slug / 'surimpressions.json'
    audio = c.PUBLIC / slug / (x.get('audio') or {}).get('fichier', '')
    if not f.exists() or not audio.is_file():
        return None
    entree = json.loads(f.read_text()).get(str(x['n']), {})
    return entree.get('mots') if entree.get('empreinte') == empreinte_audio(audio, x['narration']) else None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--fichier', type=Path, help='script JSON à modifier (par défaut 01-revolution.json)')
    p.add_argument('--essai', action='store_true', help='montrer sans écrire')
    a = p.parse_args()
    f = a.fichier.resolve() if a.fichier else c.fichier_periode('revolution')
    d = json.loads(f.read_text())
    from surimpressions import mots_du_passage
    par_n = {x['n']: x for x in d['diapositives']}
    ajoutes, sans_instant = 0, []
    for n, nouveaux in AJOUTS.items():
        x = par_n.get(n)
        if not x:
            print(f'{n:3d} : diapositive absente, passée')
            continue
        lieux = list(x.get('lieux') or [])
        deja = {li['quand'] for li in lieux}
        neufs = [{k: li[k] for k in CLES} for li in nouveaux if li['quand'] not in deja]
        if not neufs:
            print(f'{n:3d} : déjà à jour ({", ".join(li["nom"] for li in lieux)})')
            continue
        ordre = ordonner(x['narration'], lieux + neufs)
        if ordre is None:
            print(f'{n:3d} : un passage manque dans la narration (texte changé ?), passée')
            continue
        inst = instants_du_cache(d['slug'], x)
        depuis = 0
        for li in ordre:
            pos = x['narration'].find(li['quand'], depuis)
            depuis = pos + 1
            if 'instant' not in li and inst is not None:
                li['instant'] = mots_du_passage(x['narration'], li['quand'], inst, pos)[0][0]
        if any('instant' not in li for li in ordre):
            sans_instant.append(n)
        x['lieux'] = ordre
        ajoutes += len(neufs)
        print(f'{n:3d} : ' + ' ; '.join(f"{li['nom']} [{li['fond']}]" + (f" {li['instant']:.2f} s" if 'instant' in li else '')
                                          for li in ordre))
    if a.essai or not ajoutes:
        print(f'{ajoutes} lieu(x) à ajouter' + (' (essai : rien d’écrit).' if a.essai else '.'))
        return 0
    # Relecture juste avant l'écriture : un autre outil a pu toucher le fichier entre-temps.
    frais = json.loads(f.read_text())
    for x in frais['diapositives']:
        y = par_n.get(x['n'])
        if y and x['n'] in AJOUTS and x['narration'] == y['narration']:
            x['lieux'] = y['lieux']
    c.ecrire(f, frais)
    print(f'{ajoutes} lieu(x) ajouté(s) dans {f}.')
    if sans_instant:
        print('Instants à caler (audio non aligné ou changé) : diapositives ' + ', '.join(map(str, sans_instant))
              + ' ; lancer : python3 scripts/diaporamas/surimpressions.py revolution')
    return 0


if __name__ == '__main__':
    sys.exit(main())
