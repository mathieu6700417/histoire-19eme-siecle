"""Contrôle de `verifier.py --etape` (spec 13, outil 2) : les étapes A, B et C couvrent tout.

Usage :
    python3 scripts/diaporamas/tester_etapes.py consulat-empire [--hors-ligne]

Lance `verifier.py <slug>` puis `--etape A`, `B` et `C` (avec `--tout`) et compare les lignes
« ERREUR » et « avertissement » :
- la réunion des trois étapes est égale à la vérification complète (mêmes messages, mêmes nombres) ;
- A et B n'ont aucun message en commun, et chacun de leurs messages est dans la vérification complète ;
- C, étape finale, redonne tout ; le script indique combien de messages ne sont vus qu'à l'étape C.
Affiche aussi le nombre de lignes de chaque sortie sans `--tout` (visé : moins de 40 pour A).
Code de sortie 1 si la réunion diffère.
"""
import subprocess, sys
from collections import Counter
from pathlib import Path

VERIFIER = Path(__file__).with_name('verifier.py')


def lancer(slug: str, *options: str) -> list[str]:
    r = subprocess.run([sys.executable, str(VERIFIER), slug, *options], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        sys.exit(f"verifier.py {slug} {' '.join(options)} : échec\n{r.stderr[-500:]}")
    return r.stdout.splitlines()


def messages(lignes: list[str]) -> Counter:
    return Counter(l.strip() for l in lignes if l.strip().startswith(('ERREUR ', 'avertissement ')))


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        sys.exit(__doc__)
    slug, hl = args[0], [a for a in sys.argv[1:] if a == '--hors-ligne']
    complet = messages(lancer(slug, *hl))
    par = {e: messages(lancer(slug, '--etape', e, '--tout', *hl)) for e in 'ABC'}
    lignes = {e: len([l for l in lancer(slug, '--etape', e, *hl) if l.strip()]) for e in 'ABC'}
    reunion = Counter()
    for m in par.values():
        reunion |= m
    print(f'{slug} : vérification complète, {sum(complet.values())} message(s).')
    for e in 'ABC':
        print(f"  étape {e} : {sum(par[e].values())} message(s), sortie de {lignes[e]} ligne(s) sans --tout")
    ok = True
    if reunion != complet:
        ok = False
        for m in sorted((complet - reunion) + (reunion - complet)):
            print(f"  ÉCART {'absent des étapes' if m in complet - reunion else 'absent du complet'} : {m[:150]}")
    communs = par['A'] & par['B']
    if communs:
        ok = False
        print(f'  ÉCART {sum(communs.values())} message(s) à la fois en A et en B : {next(iter(communs))[:120]}')
    if (par['A'] + par['B']) - complet:
        ok = False
        print('  ÉCART des messages de A ou de B sont absents de la vérification complète')
    seuls_c = par['C'] - par['A'] - par['B']
    print(f"  propres à l'étape C : {sum(seuls_c.values())} message(s).")
    print('OK : réunion des étapes = vérification complète' if ok else 'ÉCHEC')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
