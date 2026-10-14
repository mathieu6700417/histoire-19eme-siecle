"""Carte « L'empire en … » d'un épisode (spec 12, « Les colonies au fil du récit »).

Usage :
    python3 scripts/diaporamas/empire.py 1789 --vue monde
    python3 scripts/diaporamas/empire.py 1811 --depuis 1802 --vue antilles

Affiche le visuel `carte` (JSON) à coller dans `visuels` d'un épisode : fond commun `empire`
(carte.py), cadre de la vue, et un élément par possession de src/data/diaporamas/<siecle>/commun/empire.json
tenue à la date (`de` <= année, `a` absent ou > année ; ou `periodes` : [[de, a], …] pour une
possession perdue puis rendue ; `noms` : [[année, nom], …] pour un nom d'époque). Dessin constant d'une période à l'autre :
territoire = zone pleine (hachures si limites incertaines), île ou comptoir = point plein.
Avec `--depuis` : ce qui a été perdu entre les deux dates est en hachures (zone) ou en cercle vide
(point), libellé suivi de l'année de perte ; ce qui a été gagné porte son année d'entrée.
Reste à faire à la main : `quand` de chaque élément (passage exact de la narration ; sans `quand`,
les éléments entrent en cascade), retouche des `position`, et `source`.
"""
import argparse, json

import commun as c


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('annee', type=int)
    ap.add_argument('--depuis', type=int)
    ap.add_argument('--vue', default='monde')
    a = ap.parse_args()
    d = json.loads((c.DONNEES / 'commun' / 'empire.json').read_text())
    vue = d['vues'][a.vue]
    par_id = {p['id']: p for p in d['possessions']}

    def periodes(p):
        """Périodes de possession [[de, a], …] : `periodes` (possession perdue puis rendue), sinon `de`/`a`."""
        return p.get('periodes') or ([[p['de'], p.get('a')]] if p.get('de') is not None else [])

    def periode(p, an):
        """La période [de, a] qui contient l'année, ou None."""
        return next((q for q in periodes(p) if q[0] <= an and (q[1] is None or q[1] > an)), None)

    tenue = lambda p, an: periode(p, an) is not None

    def nom_a(p, an):
        """Nom d'époque : `noms` = [[année, nom], …] (le dernier dont l'année est atteinte), sinon `nom`."""
        return next((n for d0, n in reversed(p.get('noms', [])) if d0 <= an), p['nom'])

    def annee_cle(p, e):
        """Année de perte (fin de la période tenue à `--depuis`) ou d'entrée ; un groupe : la dernière de ses membres."""
        if p.get('groupe'):
            ans = [annee_cle(par_id[m], etat(par_id[m])) for m in p['groupe'] if etat(par_id[m]) == e]
            return max((x for x in ans if x), default=None)
        if e == 'perdue':
            return periode(p, a.depuis)[1]
        return periode(p, a.annee)[0] if e == 'gagnee' else None

    def etat(p):
        """'tenue', 'gagnee', 'perdue' ou None ; un groupe suit ses membres."""
        if p.get('groupe'):
            e = {etat(par_id[m]) for m in p['groupe']}
            return 'tenue' if 'tenue' in e else 'gagnee' if 'gagnee' in e else 'perdue' if 'perdue' in e else None
        if tenue(p, a.annee):
            return 'gagnee' if a.depuis is not None and periode(p, a.annee)[0] > a.depuis else 'tenue'
        return 'perdue' if a.depuis is not None and tenue(p, a.depuis) else None

    elements, perdu = [], False
    for p in d['possessions']:
        e = etat(p)
        if a.vue not in p['vues'] or not e:
            continue
        an = annee_cle(p, e)
        nom = nom_a(p, a.depuis if a.depuis is not None else a.annee) + (f" ({an})" if an and e in ('perdue', 'gagnee') else '')
        perdu |= e == 'perdue'
        if p.get('zone'):
            el = {'type': 'zone', 'points': p['zone'], 'libelle': nom, 'style': 'hachures' if e == 'perdue' else p.get('style', 'plein')}
            et = p.get('etiquette', {}).get(a.vue)
            if et:
                el['etiquette'] = et
            elif a.vue in ('monde', 'tout') or vue.get('large'):   # `large` : vue ajoutée (monde-pacifique, 2026-10-12)
                # Vue large : la zone est minuscule, un point porte le libellé.
                elements.append({'type': 'zone', 'points': p['zone'], 'style': el['style']})
                el = {'type': 'ville', 'lieu': p['lieu'], 'libelle': nom, 'rebelle': e != 'perdue'}
        else:
            el = {'type': 'ville', 'lieu': p['lieu'], 'libelle': nom, 'rebelle': e != 'perdue'}
        if el['type'] == 'ville':
            if not el['rebelle']:
                del el['rebelle']
            el['position'] = p.get('position', {}).get(a.vue, 'droite')
        elements.append(el)
    legende = [['rebelle', 'île ou comptoir français'], ['plein', 'colonie française'], ['zone', 'limites incertaines' + (' ou territoire perdu' if perdu else '')]]
    v = {'type': 'carte', 'fond': d['fond'], 'titre': vue['titre'].format(annee=a.annee), 'elements': elements,
         'legende': legende, 'source': d['source']}
    if vue['cadre']:
        v['cadre'] = vue['cadre']
    print(json.dumps(v, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
