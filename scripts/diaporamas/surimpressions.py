"""Cartes de lieu, citations, portraits, objets de musée et manuscrits en surimpression : instants
calés sur la voix (spec 12, « Cartes de lieu et citations en surimpression », 2026-10-07 ; « Portraits
des personnes nommées » et « Enrichissements visuels », 2026-10-08).

Usage :
    python3 scripts/diaporamas/surimpressions.py revolution            # ce qui manque ou a changé
    python3 scripts/diaporamas/surimpressions.py revolution --n 14 56  # refaire ces diapositives
    python3 scripts/diaporamas/surimpressions.py revolution --relever  # aide : passages « » non relevés

Pour chaque diapositive qui porte `lieux` ou `citations`, l'audio de la narration est aligné mot
à mot sur son texte (alignement forcé, alignement.py, comme les lectures d'époque) :
- chaque citation reçoit `mots` : [[début, fin], …] (s), un couple par mot de
  `commun.mots_lus(texte)` ; le lecteur inscrit les mots un à un au rythme de la voix ;
- chaque lieu reçoit `instant` : début (s) du premier mot de son passage `quand` ; le médaillon
  apparaît alors (plusieurs lieux : un seul médaillon, chaque point paraît à son instant ; chaque
  passage est cherché après le début du précédent) ;
- chaque personne nommée (`personnes`, portraits.py) reçoit `instant` de la même façon : début du
  premier mot du nom tel qu'il est dit (`quand`), chaque passage cherché après le précédent ;
- chaque objet de musée et chaque manuscrit (`objets`, `manuscrits`, objets.py) reçoit `instant` :
  début du premier mot de son passage `quand` (première occurrence) ;
- chaque chiffre clé (`chiffres`) et chaque date du calendrier républicain (`dates_republicaines`)
  reçoit `instant` de même (« Enrichissements visuels », point 4) ; la date reçoit en plus
  `gregorien`, sa correspondance calculée par `commun.date_republicaine` (tables officielles : années
  sextiles III, VII, XI), écrite même sans alignement.
Le texte aligné est le texte DIT (lexique de prononciation appliqué à toute la narration, entrées
de plusieurs mots comprises : « Louis XVI » → « Louis seize ») ; les mots affichés sont ensuite
rattachés aux mots dits par correspondance de séquences (un mot réécrit par le lexique prend les
instants des mots dits qui le remplacent).

Les instants des mots de chaque narration sont gardés en cache (.cache/diaporamas/<slug>/
surimpressions.json), avec l'empreinte de l'audio et du texte : seul ce qui a changé est refait.
Après une nouvelle voix (voix.py), relancer ce script ; verifier.py signale les instants périmés.
Sans torch/torchaudio (alignement indisponible), rien n'est écrit : le lecteur situe alors les
passages au prorata des caractères dans les phrases horodatées (`audio.phrases`).
"""
import argparse, difflib, hashlib, json, re, sys, warnings

import commun as c


# Surimpressions dont les passages sont calés sur la voix.
CLES = ('lieux', 'citations', 'personnes', 'objets', 'manuscrits', 'chiffres', 'dates_republicaines')


def empreinte_audio(fichier, narration: str) -> str:
    h = hashlib.sha1(fichier.read_bytes())
    h.update(narration.encode())
    return h.hexdigest()[:16]


def _norme(mot: str) -> str:
    return re.sub(r'\W', '', mot.lower())


def instants_narration(fichier, narration: str, lexique: dict) -> list[list[float]]:
    """[[début, fin], …] de chaque mot de `mots_lus(narration)` : alignement du texte dit, puis
    correspondance des mots affichés et des mots dits."""
    import alignement
    dit = c.appliquer_lexique(narration, lexique)
    t_dit = alignement.aligner(fichier, dit, {})
    a = [_norme(m) for _, _, m in c.mots_lus(narration)]
    b = [_norme(m) for _, _, m in c.mots_lus(dit)]
    sortie: list[list[float] | None] = [None] * len(a)
    for op, i0, i1, j0, j1 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == 'equal':
            for k in range(i1 - i0):
                sortie[i0 + k] = t_dit[j0 + k]
        elif j1 > j0:
            # Mots réécrits (« XVI » → « seize ») : la plage des mots dits, partagée.
            d0, f0 = t_dit[j0][0], t_dit[j1 - 1][1]
            n = i1 - i0
            for k in range(n):
                sortie[i0 + k] = [round(d0 + (f0 - d0) * k / n, 2), round(d0 + (f0 - d0) * (k + 1) / n, 2)]
    for k, v in enumerate(sortie):  # mot sans équivalent dit : entre ses voisins
        if v is None:
            avant = next((sortie[j][1] for j in range(k - 1, -1, -1) if sortie[j]), 0.0)
            sortie[k] = [avant, avant]
    return sortie


def mots_du_passage(narration: str, texte: str, instants, depuis: int = 0):
    """Instants des mots de `mots_lus(texte)`, `texte` étant une sous-chaîne de la narration."""
    pos = narration.index(texte, depuis)
    mots_n = c.mots_lus(narration)
    sortie = []
    for d, f, _ in c.mots_lus(texte):
        d, f = d + pos, f + pos
        k = next(k for k, (a, b, _) in enumerate(mots_n) if a < f and b > d)
        sortie.append(instants[k])
    return sortie


def relever(d: dict) -> None:
    """Passages entre guillemets des narrations, avec leur état (citation relevée ou non)."""
    for x in d['diapositives']:
        relevees = {ci['texte'] for ci in x.get('citations', [])}
        for m in re.finditer(r'«\s*(.+?)\s*»', x['narration']):
            etat = 'relevée' if m.group(1) in relevees else '—'
            print(f"{x['n']:3d}  {etat:8s} « {m.group(1)} » ({c.nb_mots(m.group(1))} mots)")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug')
    p.add_argument('--n', type=int, nargs='+', help='refaire ces diapositives')
    p.add_argument('--relever', action='store_true', help='lister les passages entre guillemets')
    a = p.parse_args()
    f, d = c.lire(a.slug)
    if a.relever:
        relever(d)
        return 0
    import alignement
    warnings.filterwarnings('ignore', message='.*forced_align has been deprecated')
    ok, info = alignement.disponible()
    if not ok:
        print(f'alignement indisponible ({info}) : le lecteur se repliera au prorata.')
        return 1
    lexique = c.charger_lexique()
    cache_f = c.CACHE / d['slug'] / 'surimpressions.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    dossier = c.PUBLIC / d['slug']
    faits = 0
    for x in d['diapositives']:
        for da in x.get('dates_republicaines', []):
            conv = c.date_republicaine(da.get('republicain', ''))
            if conv:
                da['gregorien'] = conv[1]
        if not any(x.get(k) for k in CLES):
            continue
        n = str(x['n'])
        audio = dossier / (x.get('audio') or {}).get('fichier', '')
        if not audio.is_file():
            print(f'{x["n"]:3d} : audio absent, passé')
            continue
        e = empreinte_audio(audio, x['narration'])
        if (a.n and x['n'] in a.n) or cache.get(n, {}).get('empreinte') != e:
            cache[n] = {'empreinte': e, 'mots': instants_narration(audio, x['narration'], lexique)}
            faits += 1
        inst = cache[n]['mots']
        bilan = []
        for ci in x.get('citations', []):
            ci['mots'] = mots_du_passage(x['narration'], ci['texte'], inst)
            bilan.append(f"« {ci['texte'][:24]}… » {ci['mots'][0][0]:.2f}-{ci['mots'][-1][1]:.2f} s")
        # Plusieurs lieux (révision du 2026-10-08) : chaque passage est cherché après le début du
        # précédent (« de Dunkerque à Barcelone » puis « à Barcelone »), comme dans le lecteur.
        depuis = 0
        for li in x.get('lieux', []):
            pos = x['narration'].find(li['quand'], depuis)
            if pos < 0:
                print(f"{x['n']:3d} : passage « {li['quand']} » introuvable (après le lieu précédent), passé")
                continue
            depuis = pos + 1
            li['instant'] = mots_du_passage(x['narration'], li['quand'], inst, pos)[0][0]
            bilan.append(f"{li['nom']} {li['instant']:.2f} s")
        # Personnes nommées (portraits) : même règle que les lieux.
        depuis = 0
        for pe in x.get('personnes', []):
            pos = x['narration'].find(pe['quand'], depuis)
            if pos < 0:
                print(f"{x['n']:3d} : nom « {pe['quand']} » introuvable (après le précédent), passé")
                continue
            depuis = pos + 1
            pe['instant'] = mots_du_passage(x['narration'], pe['quand'], inst, pos)[0][0]
            bilan.append(f"{pe['id']} {pe['instant']:.2f} s")
        # Objets de musée et manuscrits (objets.py) : début du passage `quand` (première occurrence).
        for cle in ('objets', 'manuscrits', 'chiffres', 'dates_republicaines'):
            for ob in x.get(cle, []):
                if ob['quand'] not in x['narration']:
                    print(f"{x['n']:3d} : passage « {ob['quand']} » introuvable, passé")
                    continue
                ob['instant'] = mots_du_passage(x['narration'], ob['quand'], inst)[0][0]
                bilan.append(f"{ob.get('id', ob['quand'])} {ob['instant']:.2f} s")
        print(f"{x['n']:3d} : " + ' ; '.join(bilan))
    cache_f.parent.mkdir(parents=True, exist_ok=True)
    cache_f.write_text(json.dumps(cache, ensure_ascii=False) + '\n')
    # Relecture juste avant l'écriture : d'autres outils peuvent avoir touché le script entre-temps.
    f2, frais = c.lire(a.slug)
    par_n = {x['n']: x for x in d['diapositives']}
    for x in frais['diapositives']:
        y = par_n.get(x['n'])
        if not y or y['narration'] != x['narration']:
            continue
        for cle in CLES:
            if cle in x and cle in y and [z.get('texte', z.get('quand')) for z in x[cle]] == [z.get('texte', z.get('quand')) for z in y[cle]]:
                for zx, zy in zip(x[cle], y[cle]):
                    for k in ('mots', 'instant', 'gregorien'):
                        if k in zy:
                            zx[k] = zy[k]
    c.ecrire(f2, frais)
    print(f'{faits} narration(s) alignée(s) ; {f2.relative_to(c.RACINE)} mis à jour.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
