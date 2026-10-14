"""Registre des enregistrements libres du « Siècle en images » (spec 13, outil 1).

La recherche musicale est l'étape la plus chère de l'agent B (période 02 : ~35 min, ~25 appels) et
se recoupe d'une période à l'autre (Méhul, Cherubini, Boieldieu reviennent). Ce registre, commun aux
neuf périodes, garde chaque enregistrement déjà vérifié, retenu ou non, et les œuvres cherchées sans
succès : on le consulte AVANT toute recherche sur Commons ou l'Internet Archive.

Usage :
    python3 scripts/diaporamas/registre_musique.py chercher thill           # première commande de l'agent B
    python3 scripts/diaporamas/registre_musique.py chercher mehul symphonie # tous les mots, sans accents ni casse
    python3 scripts/diaporamas/registre_musique.py ajouter --depuis restauration   # après musique.py <slug>
    python3 scripts/diaporamas/registre_musique.py ecarter "<id>" "<motif>"
    python3 scripts/diaporamas/registre_musique.py possible "<id>" "<œuvre>" "<compositeur>" "<interprète>"
    python3 scripts/diaporamas/registre_musique.py introuvable "<œuvre>" "<compositeur>" "<où>"
    python3 scripts/diaporamas/registre_musique.py --amorcer                # périodes existantes + journal 02

Données : src/data/diaporamas/<siecle>/commun/registre-musique.json
    { "enregistrements": [ … ], "introuvables": [ … ] }

Une entrée par ENREGISTREMENT (un fichier d'une source), pas par piste d'une période :
- `id` : `<type>:<identifiant>#<fichier>` pour l'Internet Archive, `commons:File:…` pour Commons ; unique.
- `source`, `licence`, `interprete`, `enregistrement`, `filtres` : repris tels quels de la piste du
  JSON de la période ; `oeuvre` = son `titre`, `compositeur` = son `compositeur` (ou, pour un
  chant, son `auteur`, qui nomme d'ordinaire le compositeur et le parolier ; `auteur_texte` à part
  seulement si la piste donne les deux), `date_oeuvre` = sa `date`.
- `genre` : `chant` (intermède chanté) ou `instrumental`.
- `preuve_date` : ce qui fonde la licence (année de publication déclarée, licence relevée par
  musique.py, page de la source).
- `duree` : durée de l'enregistrement entier (s), lue sur la source en cache
  (.cache/diaporamas/musique/sources/) si elle y est.
- `structure` : passages utiles connus, `[début, fin, libellé]` en secondes de l'enregistrement
  (fin `null` : jusqu'au bout) ; chaque extrait utilisé par une période y est versé.
- `periodes` : périodes qui l'utilisent (noms de fichier, « 01-revolution »).
- `statut` : `retenu` (utilisé par une période), `possible` (vérifié, libre, pas encore utilisé),
  `ecarte` (avec `motif` : on ne le recherche plus).
- `verifie` : date de la vérification (amorçage : date du relevé de licence par musique.py).
`introuvables` : œuvres cherchées sans enregistrement libre trouvé, `{ oeuvre, compositeur, cherche,
ou, note }` ; on ne les recherche plus sans raison nouvelle (source nouvelle, date passée).

Décisions :
- `--amorcer` et `ajouter` sont idempotents : relancés, ils n'ajoutent ni doublon ni passage déjà
  noté, et ne touchent pas à `verifie`.
- Deux pistes tirées du même fichier (deux mouvements, ou le même chant dans deux périodes) font
  UNE entrée, avec plusieurs passages et plusieurs périodes.
- Les introuvables de la période 02 sont saisis ici à la main (INTROUVABLES_02), d'après l'entrée 35
  de docs/journal/<siecle>/diaporama-02-consulat-empire.jsonl ; les requêtes d'alors n'ont pas été consignées.
- Écriture par commun.ecrire (atomique, sous verrou). Aucun appel réseau, aucun appel Gemini.
"""
import argparse, datetime, json, re, sys, unicodedata
from pathlib import Path

import commun as c

REGISTRE = c.DONNEES / 'commun' / 'registre-musique.json'
STATUTS = ('retenu', 'possible', 'ecarte')

OU_02 = ('Commons, Internet Archive et web (recherche de l’agent B, journal de la période 02, entrée 35 ; '
         'requêtes non consignées)')
INTROUVABLES_02 = [
    ('Les Deux Journées, ouverture', 'Luigi Cherubini', ''),
    ('Anacréon, ouverture', 'Luigi Cherubini', ''),
    ('Joseph, ouverture', 'Étienne Méhul', 'l’air « Champs paternels » du même opéra existe (Campagnola, 1924)'),
    ('Jean de Paris, ouverture', 'François-Adrien Boieldieu', 'seul enregistrement trouvé : microsillon de 1966, trop récent'),
    ('Partant pour la Syrie', 'Hortense de Beauharnais', 'seul item trouvé sous licence NC-ND (enregistrement russe)'),
    ('Veillons au salut de l’Empire', 'Nicolas Dalayrac (air), Adrien-Simon Boy (paroles)', ''),
    ('Le Roi d’Yvetot', 'Pierre-Jean de Béranger', 'trouvé seulement chanté en anglais'),
    ('Vive Henri IV', 'chant traditionnel', 'enregistrement des Quatre Barbus, année de publication inconnue ; '
     'aucun chant royaliste libre trouvé'),
    ('La Vestale (enregistrement de Maria Callas, 1954-1955)', 'Gaspare Spontini',
     'étiquette pirate ERR, date de publication inconnue ; l’enregistrement de Rosa Ponselle (1926) est retenu'),
]


def sans_accents(t: str) -> str:
    t = str(t or '').lower().replace('’', "'")      # apostrophe courbe ou droite : même mot
    return ''.join(ch for ch in unicodedata.normalize('NFD', t) if unicodedata.category(ch) != 'Mn')


def id_source(src: dict) -> str:
    """Identifiant d'un enregistrement : `archive:<id>#<fichier>` ou `commons:File:<fichier>`."""
    if src.get('type') == 'commons':
        fichier = src.get('fichier', '')
        return 'commons:' + (fichier if fichier.startswith('File:') else f'File:{fichier}')
    return f"{src.get('type')}:{src.get('id', '')}#{src.get('fichier', '')}"


def source_de(ident: str) -> dict:
    """Source reconstruite depuis un `id` saisi à la main (ecarter, possible)."""
    t, _, reste = ident.partition(':')
    if t == 'commons' and reste.startswith('File:'):
        return {'type': 'commons', 'fichier': reste}
    if t == 'archive' and '#' in reste:
        item, _, fichier = reste.partition('#')
        return {'type': 'archive', 'id': item, 'fichier': fichier}
    sys.exit(f'id invalide : {ident!r} (attendu : archive:<identifiant>#<fichier> ou commons:File:<fichier>)')


def lire() -> dict:
    if REGISTRE.exists():
        r = json.loads(REGISTRE.read_text())
    else:
        r = {}
    r.setdefault('note', 'Enregistrements libres déjà vérifiés et œuvres cherchées en vain : à consulter avant toute '
                         'recherche musicale (scripts/diaporamas/registre_musique.py chercher <mots>).')
    r.setdefault('enregistrements', [])
    r.setdefault('introuvables', [])
    return r


def ecrire(r: dict) -> None:
    REGISTRE.parent.mkdir(parents=True, exist_ok=True)
    c.ecrire(REGISTRE, r)


def periodes_existantes() -> list[Path]:
    return [f for f in sorted(c.DONNEES.glob('*.json')) if re.match(r'\d+-', f.stem)]


def _pistes(d: dict) -> list[tuple[dict, bool]]:
    m = d.get('musique') or {}
    return [(p, False) for p in m.get('fond', [])] + [(p, True) for p in m.get('intermedes', [])]


def _duree_source(src: dict) -> float | None:
    """Durée de l'enregistrement entier, si la source est dans le cache de musique.py."""
    import musique
    if src.get('type') == 'commons':
        f = musique.SOURCES / 'commons' / musique.nom_cache(src['fichier'].removeprefix('File:'))
        if not f.exists():   # le titre canonique de Commons peut différer (espaces, redirection)
            f = musique.SOURCES / 'commons' / musique.nom_cache(src['fichier'].removeprefix('File:').replace('_', ' '))
    else:
        f = musique.SOURCES / 'archive' / musique.nom_cache(f"{src.get('id')}--{src.get('fichier')}")
    try:
        return round(musique.duree_audio(f), 1) if f.exists() else None
    except Exception:  # noqa: BLE001  (ffprobe absent ou fichier illisible : la durée reste inconnue)
        return None


def _passage(p: dict, chant: bool) -> list:
    if chant and p.get('paroles'):
        quoi = f"« {p['paroles'][0][1]} »"
    elif chant:
        quoi = 'intermède musical'
    else:
        quoi = f"fond, {p['titre'].split(' : ', 1)[-1]}" if ' : ' in p.get('titre', '') else 'fond'
    return [float(p.get('debut') or 0), p.get('fin'), quoi]


def _entree(p: dict, chant: bool, etat: dict, verifie: str) -> dict:
    src = p['source']
    e = {'id': id_source(src), 'source': src, 'oeuvre': p.get('titre', '')}
    e['compositeur'] = p.get('compositeur') or p.get('auteur') or ''
    if p.get('auteur') and p.get('compositeur'):
        e['auteur_texte'] = p['auteur']
    e['date_oeuvre'] = p.get('date', '')
    e['interprete'] = p.get('interprete', '')
    if p.get('enregistrement'):
        e['enregistrement'] = p['enregistrement']
    e['genre'] = 'chant' if chant and not p.get('instrumental') else 'instrumental'
    e['licence'] = p.get('licence', '')
    preuves = []
    if src.get('publication'):
        preuves.append(f"année de publication déclarée dans la source : {src['publication']}")
    if etat.get('licence_relevee'):
        preuves.append(f"licence relevée par musique.py : {etat['licence_relevee']}")
    if etat.get('page'):
        preuves.append(etat['page'])
    e['preuve_date'] = ' ; '.join(preuves)
    duree = _duree_source(src)
    if duree:
        e['duree'] = duree
    if p.get('filtres'):
        e['filtres'] = p['filtres']
    e.update({'structure': [], 'periodes': [], 'statut': 'retenu', 'verifie': verifie})
    return e


def verser(r: dict, fichier: Path) -> tuple[int, int, list[str]]:
    """Verse les pistes d'une période : (entrées créées, entrées complétées, alertes)."""
    d = json.loads(fichier.read_text())
    periode = fichier.stem
    etat_f = c.CACHE / d['slug'] / 'musique.json'
    etat = json.loads(etat_f.read_text()) if etat_f.exists() else {}
    verifie = (datetime.date.fromtimestamp(etat_f.stat().st_mtime) if etat_f.exists() else datetime.date.today()).isoformat()
    par_id = {e['id']: e for e in r['enregistrements']}
    nouveaux, touches = set(), set()
    alertes = []
    for p, chant in _pistes(d):
        src = p.get('source') or {}
        if src.get('type') not in ('commons', 'archive'):
            continue
        e = par_id.get(id_source(src))
        change = False
        if not e:
            e = _entree(p, chant, etat.get(p.get('id'), {}), verifie)
            r['enregistrements'].append(e)
            par_id[e['id']] = e
            nouveaux.add(e['id'])
        elif e.get('statut') == 'ecarte':
            alertes.append(f"{p.get('id')} : enregistrement écarté au registre ({e.get('motif', 'sans motif')}) : {e['id']}")
            continue
        elif e.get('statut') != 'retenu':
            e['statut'] = 'retenu'
            change = True
        if periode not in e['periodes']:
            e['periodes'] = sorted(e['periodes'] + [periode])
            change = True
        passage = _passage(p, chant)
        if not any(q[:2] == passage[:2] for q in e['structure']):
            e['structure'].append(passage)
            change = True
        if change and e['id'] not in nouveaux:
            touches.add(e['id'])
    return len(nouveaux), len(touches), alertes


def absentes(d: dict, periode: str, r: dict | None = None) -> list[str]:
    """Pistes de la période qui ne sont pas au registre comme `retenu` pour elle (verifier.py, musique.py)."""
    r = r if r is not None else lire()
    par_id = {e['id']: e for e in r['enregistrements']}
    manquent = []
    for p, _ in _pistes(d):
        src = p.get('source') or {}
        if src.get('type') not in ('commons', 'archive'):
            continue
        e = par_id.get(id_source(src))
        if not e or e.get('statut') != 'retenu' or periode not in e.get('periodes', []):
            manquent.append(p.get('id', '?'))
    return manquent


def ajouter_introuvable(r: dict, oeuvre: str, compositeur: str, ou: str, note: str = '', cherche: str | None = None) -> bool:
    """Ajoute une œuvre introuvable ; False si elle y est déjà (même œuvre, même compositeur)."""
    cle = (sans_accents(oeuvre), sans_accents(compositeur))
    if any((sans_accents(x.get('oeuvre')), sans_accents(x.get('compositeur'))) == cle for x in r['introuvables']):
        return False
    x = {'oeuvre': oeuvre, 'compositeur': compositeur, 'cherche': cherche or datetime.date.today().isoformat(), 'ou': ou}
    if note:
        x['note'] = note
    r['introuvables'].append(x)
    return True


def annee(e: dict) -> str:
    m = re.search(r'\b(18|19|20)\d\d\b', str((e.get('source') or {}).get('publication') or '') + ' ' + str(e.get('enregistrement') or '')
                  + ' ' + str(e.get('interprete') or ''))
    return m.group(0) if m else '?'


def ligne(e: dict) -> str:
    per = ', '.join(e.get('periodes') or []) or 'aucune période'
    motif = f" ; motif : {e['motif']}" if e.get('statut') == 'ecarte' and e.get('motif') else ''
    return (f"{e.get('statut', '?'):8} {e.get('oeuvre') or '(œuvre non notée)'} — {e.get('compositeur') or '?'} ; "
            f"{e.get('interprete') or 'interprète non noté'} ({annee(e)}) ; {per}{motif}\n         {e['id']}")


def chercher(r: dict, mots: list[str]) -> int:
    cles = [sans_accents(m) for m in mots]
    trouves = [e for e in r['enregistrements']
               if all(k in sans_accents(' '.join(str(e.get(ch) or '') for ch in ('oeuvre', 'compositeur', 'auteur_texte', 'interprete')))
                      for k in cles)]
    vains = [x for x in r['introuvables']
             if all(k in sans_accents(f"{x.get('oeuvre')} {x.get('compositeur')}") for k in cles)]
    for e in sorted(trouves, key=lambda e: (STATUTS.index(e.get('statut')) if e.get('statut') in STATUTS else 9, e.get('oeuvre', ''))):
        print(ligne(e))
    for x in vains:
        note = f" ; {x['note']}" if x.get('note') else ''
        print(f"introuvable {x['oeuvre']} — {x['compositeur']} ; cherché le {x['cherche']} : {x['ou']}{note}")
    print(f"{len(trouves)} enregistrement(s), {len(vains)} introuvable(s) pour « {' '.join(mots)} »."
          + ('' if trouves or vains else ' Rien au registre : recherche à faire (Commons, Internet Archive), puis la noter ici.'))
    return 0


def bilan(r: dict) -> str:
    n = {s: sum(1 for e in r['enregistrements'] if e.get('statut') == s) for s in STATUTS}
    return (f"Registre : {len(r['enregistrements'])} enregistrement(s) ({n['retenu']} retenu(s), {n['possible']} possible(s), "
            f"{n['ecarte']} écarté(s)), {len(r['introuvables'])} introuvable(s).")


def saisir(r: dict, ident: str, statut: str, a) -> str:
    """ecarter / possible : modifie l'entrée `ident` ou la crée (source reconstruite depuis l'id)."""
    e = next((x for x in r['enregistrements'] if x['id'] == ident), None)
    if e and statut == 'ecarte' and e.get('periodes'):
        sys.exit(f"Refus : {ident} est utilisé par {', '.join(e['periodes'])} ; retirer d'abord la piste de la période.")
    if e and statut == 'possible' and e.get('statut') == 'retenu':
        sys.exit(f"Refus : {ident} est déjà retenu ({', '.join(e.get('periodes') or [])}).")
    cree = e is None
    if cree:
        e = {'id': ident, 'source': source_de(ident), 'oeuvre': '', 'compositeur': '', 'interprete': '',
             'structure': [], 'periodes': []}
        r['enregistrements'].append(e)
    for champ in ('oeuvre', 'compositeur', 'interprete', 'licence'):
        if getattr(a, champ, None):
            e[champ] = getattr(a, champ)
    e['statut'] = statut
    if statut == 'ecarte':
        e['motif'] = a.motif
    else:
        e.pop('motif', None)
    e['verifie'] = datetime.date.today().isoformat()
    return f"{'Ajouté' if cree else 'Modifié'} : {ligne(e)}"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--amorcer', action='store_true', help='remplit le registre depuis les périodes existantes et le journal 02')
    sp = p.add_subparsers(dest='commande')
    q = sp.add_parser('chercher', help='recherche sans accents ni casse (œuvre, compositeur, interprète)')
    q.add_argument('mots', nargs='+')
    q = sp.add_parser('ajouter', help='verse les pistes d’une période (après musique.py)')
    q.add_argument('--depuis', required=True, metavar='SLUG')
    q = sp.add_parser('ecarter', help='note un enregistrement à ne plus rechercher')
    q.add_argument('id')
    q.add_argument('motif')
    q = sp.add_parser('possible', help='note un enregistrement vérifié, libre, pas encore utilisé')
    q.add_argument('id')
    q.add_argument('oeuvre')
    q.add_argument('compositeur')
    q.add_argument('interprete')
    for nom in ('ecarter', 'possible'):
        q = sp.choices[nom]
        if nom == 'ecarter':
            q.add_argument('--oeuvre')
            q.add_argument('--compositeur')
            q.add_argument('--interprete')
        q.add_argument('--licence')
    q = sp.add_parser('introuvable', help='note une œuvre cherchée sans enregistrement libre trouvé')
    q.add_argument('oeuvre')
    q.add_argument('compositeur')
    q.add_argument('ou', help='où et comment on a cherché (sources, requêtes)')
    q.add_argument('--note', default='')
    a = p.parse_args()
    r = lire()

    if a.amorcer:
        for f in periodes_existantes():
            crees, completes, alertes = verser(r, f)
            print(f'{f.stem} : {crees} enregistrement(s) ajouté(s), {completes} complété(s).')
            for x in alertes:
                print(f'  ALERTE {x}')
        n = sum(ajouter_introuvable(r, o, comp, OU_02, note, '2026-10-08') for o, comp, note in INTROUVABLES_02)
        print(f'Introuvables de la période 02 : {n} ajouté(s).')
        ecrire(r)
        print(bilan(r))
        return 0
    if a.commande == 'chercher':
        return chercher(r, a.mots)
    if a.commande == 'ajouter':
        f = c.fichier_periode(a.depuis)
        crees, completes, alertes = verser(r, f)
        for x in alertes:
            print(f'  ALERTE {x}')
        ecrire(r)
        print(f'{f.stem} : {crees} enregistrement(s) ajouté(s), {completes} complété(s). {bilan(r)}')
        return 1 if alertes else 0
    if a.commande in ('ecarter', 'possible'):
        print(saisir(r, a.id, 'ecarte' if a.commande == 'ecarter' else 'possible', a))
        ecrire(r)
        return 0
    if a.commande == 'introuvable':
        if ajouter_introuvable(r, a.oeuvre, a.compositeur, a.ou, a.note):
            ecrire(r)
            print(f'Introuvable noté : {a.oeuvre} — {a.compositeur}. {bilan(r)}')
        else:
            print(f'Déjà au registre des introuvables : {a.oeuvre} — {a.compositeur}.')
        return 0
    p.error('indiquer une commande (chercher, ajouter, ecarter, possible, introuvable) ou --amorcer')


if __name__ == '__main__':
    sys.exit(main())
