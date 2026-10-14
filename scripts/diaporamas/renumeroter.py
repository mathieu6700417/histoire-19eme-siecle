"""Insertion de diapositives et renumérotation d'une période (spec 12, « Arts et techniques »).

Usage :
    python3 scripts/diaporamas/renumeroter.py revolution --inserer ajouts.json [--essai]
    python3 scripts/diaporamas/renumeroter.py revolution [--essai]   # renumérote seulement

`ajouts.json` : liste de groupes `{"apres": 12, "diapositives": [{…}, …]}`, où `apres` est le
numéro ACTUEL de la diapositive après laquelle le groupe s'insère (0 : en tête). Les nouvelles
diapositives n'ont ni `n`, ni fichiers : `images.py`, `voix.py` et `camera.py` les produiront.
Sans `--inserer`, l'ordre de la liste `diapositives` du JSON fait foi (diapositives déplacées à
la main) et les anciens numéros `n` servent de clés.

Tout renvoi par numéro est recalculé : `n`, fichiers `NNN.webp` / `NNN.m4a` (renommés dans
public/<siecle>/diaporamas/<slug>/, en deux temps pour éviter les collisions), `image.fichier` et
`audio.fichier` (et `NNN-apres.webp`, `NNN-mK.webp` des avant/après et mosaïques, `NNN-mouvement.mp4` et
`NNN-couleur.webp`, `NNN-b-couleur.webp` de la couche générée, spec 16, `NNN-grand.webp` et `NNN-b-grand.webp`
de la netteté, `NNN-fond.webp` et `NNN-b-fond.webp` des fonds prolongés, spec 17, `NNN-vignette.webp` et `NNN-vignette.json`
des vignettes dessinées ; les recettes de colorisation et de fonds, indexées par fichier Commons, ne bougent pas ; les numéros
du lot des vignettes, src/data/diaporamas/<siecle>/generation/<slug>-vignettes.json, sont remplacés sur place), débuts d'actes, `apres` des intermèdes, lectures et épisodes,
`portrait.diapositive` des lectures. Les états de .cache/diaporamas/<slug>/ indexés par numéro
(images.json, voix.json, camera.json) sont réindexés : les voix, licences et cadrages inchangés
restent reconnus, rien n'est resynthétisé (l'empreinte du texte fait foi). L'empreinte de
caméra, qui contient le nom du fichier image, est recalculée pour les entrées encore valables.
Les annotations de visionnage (docs/annotations/<siecle>/<slug>.jsonl, spec 15) suivent : `lieu.n` et
`ecran.image.fichier` (NNN.webp, NNN-b.webp) passent au nouveau numéro, un champ `renumerote` garde
le numéro d'origine ; identifiant (qui finit par l'ancien numéro) et capture ne changent pas.
`--essai` affiche la correspondance sans rien écrire.
"""
import argparse, re, json, sys
from datetime import date

import commun as c
import camera
import annotations


def suivre_annotations(slug: str, m: dict, essai: bool = False) -> list[str]:
    """Reporte la renumérotation `m` (ancien n → nouveau n) dans les annotations de visionnage.

    Renvoie les lignes « identifiant : ancien → nouveau ». Le numéro d'origine (celui de
    l'identifiant et de la capture) est conservé dans `renumerote` d'une renumérotation à l'autre."""
    if not annotations.fichier(slug).exists():
        return []
    liste, suivi = annotations.lire(slug), []
    for a in liste:
        lieu = a.get('lieu') or {}
        o = lieu.get('n')
        if not isinstance(o, int) or m.get(o, o) == o:
            continue
        nv = m[o]
        lieu['n'] = nv
        img = (a.get('ecran') or {}).get('image') or {}
        f_ = img.get('fichier') or ''
        if re.match(rf'{o:03d}[-.]', f_):
            img['fichier'] = f'{nv:03d}' + f_[3:]
        avant = re.match(r'diapositive (\d+) devenue', a.get('renumerote') or '')
        origine = int(avant[1]) if avant else o
        a['renumerote'] = f'diapositive {origine} devenue {nv} (renumeroter.py, {date.today().isoformat()})'
        suivi.append(f"{annotations.court(a['id'])} : {o}→{nv}")
    if suivi and not essai:
        annotations.ecrire(slug, liste)
    return suivi


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug')
    p.add_argument('--inserer', metavar='AJOUTS.json')
    p.add_argument('--essai', action='store_true')
    a = p.parse_args()

    f, d = c.lire(a.slug)
    dossier = c.PUBLIC / d['slug']
    anciens = d['diapositives']
    if len({x['n'] for x in anciens if 'n' in x}) != sum(1 for x in anciens if 'n' in x):
        raise SystemExit('numéros en double dans le JSON')
    # Empreintes de caméra valables AVANT (avec les anciens noms de fichiers).
    cam_f = c.CACHE / d['slug'] / 'camera.json'
    cam = json.loads(cam_f.read_text()) if cam_f.exists() else {}
    cam_valide = {x['n'] for x in anciens if 'n' in x and cam.get(str(x['n']), {}).get('empreinte') == camera.empreinte(x)}

    liste = list(anciens)
    if a.inserer:
        groupes = json.loads(open(a.inserer).read())
        connus = {x['n'] for x in anciens}
        for g in sorted(groupes, key=lambda g: g['apres'], reverse=True):
            if g['apres'] != 0 and g['apres'] not in connus:
                raise SystemExit(f"apres={g['apres']} : diapositive inconnue")
            k = 0 if g['apres'] == 0 else next(i for i, x in enumerate(liste) if x.get('n') == g['apres']) + 1
            for x in g['diapositives']:
                x.pop('n', None)
            liste[k:k] = g['diapositives']

    m = {}  # ancien n → nouveau n
    for k, x in enumerate(liste, 1):
        if 'n' in x:
            m[x['n']] = k
    nouvelles = [k for k, x in enumerate(liste, 1) if 'n' not in x]
    deplaces = {o: nv for o, nv in m.items() if o != nv}
    print(f"{len(anciens)} → {len(liste)} diapositives ; nouvelles : {nouvelles or 'aucune'} ; "
          f"{len(deplaces)} renumérotée(s).")
    if a.essai:
        print('Correspondance (ancien → nouveau) :', ', '.join(f'{o}→{nv}' for o, nv in deplaces.items()))
        suivi = suivre_annotations(d['slug'], m, essai=True)
        print(f'Annotations de visionnage à renuméroter : {len(suivi)}' + (' (' + ', '.join(suivi) + ')' if suivi else '') + '.')
        return 0

    # 1. Fichiers : ancien nom → nom temporaire → nouveau nom.
    renommages = []
    for x in liste:
        if 'n' not in x:
            continue
        o, nv = x['n'], m[x['n']]
        for cle, ext in (('image', 'webp'), ('audio', 'm4a')):
            obj = x.get(cle) or {}
            if obj.get('fichier') == c.nom(o, ext) and o != nv:
                renommages.append((dossier / c.nom(o, ext), dossier / c.nom(nv, ext)))
                obj['fichier'] = c.nom(nv, ext)
        # Image « après » d'un avant / après (NNN-apres.webp) et vignettes d'une mosaïque (NNN-mK.webp ;
        # la principale reprend le fichier de l'image).
        if o != nv:
            autres = ([x['image'].get('apres') or {}] + list((x.get('mosaique') or {}).get('vignettes', []))
                      + [p.get('image') or {} for p in x.get('plans') or []]   # plans de la spec 14 (NNN-b.webp)
                      + [x['image'].get('video') or {}]   # clip de la couche générée (spec 16, NNN-mouvement.mp4)
                      + [x['image'].get('ambiance') or {}]   # ambiance sonore du clip (spec 17, NNN-ambiance.m4a)
                      # versions colorisées (spec 16) : NNN-couleur.webp, NNN-b-couleur.webp
                      + [x['image'].get('couleur') or {}] + [(p.get('image') or {}).get('couleur') or {} for p in x.get('plans') or []]
                      # variantes grand écran (spec 17) : NNN-grand.webp, NNN-b-grand.webp
                      + [x['image'].get('grand') or {}] + [(p.get('image') or {}).get('grand') or {} for p in x.get('plans') or []]
                      # et leur version colorisée (NNN-couleur-grand.webp, NNN-b-couleur-grand.webp)
                      + [(x['image'].get('grand') or {}).get('couleur') or {}] + [((p.get('image') or {}).get('grand') or {}).get('couleur') or {} for p in x.get('plans') or []]
                      # fonds prolongés (spec 17) : NNN-fond.webp, NNN-b-fond.webp
                      + [x['image'].get('fond') or {}] + [(p.get('image') or {}).get('fond') or {} for p in x.get('plans') or []])
            # vignettes dessinées (spec 17, essai 5) : encre et tracés, NNN-vignette.webp et .json, NNN-b-vignette.…
            vignettes = [x['image'].get('vignette') or {}] + [(p.get('image') or {}).get('vignette') or {} for p in x.get('plans') or []]
            for obj, cle_f in [(o_, 'fichier') for o_ in autres] + [(v, k) for v in vignettes for k in ('fichier', 'traces')]:
                f_ = obj.get(cle_f) or ''
                if f_.startswith(f'{o:03d}-'):
                    neuf = f'{nv:03d}-' + f_[4:]
                    renommages.append((dossier / f_, dossier / neuf))
                    obj[cle_f] = neuf
                elif f_ == c.nom(o, 'webp'):
                    obj[cle_f] = c.nom(nv, 'webp')
    temporaires = []
    for src, dst in renommages:
        if src.exists():
            tmp = src.with_name(src.name + '.renum')
            src.rename(tmp)
            temporaires.append((tmp, dst))
    for tmp, dst in temporaires:
        tmp.rename(dst)

    # 2. Numéros et renvois.
    for k, x in enumerate(liste, 1):
        x['n'] = k
        x['image'].setdefault('fichier', c.nom(k, 'webp'))
    d['diapositives'] = liste
    for acte in d['actes']:
        acte['debut'] = m[acte['debut']]
    for i in (d.get('musique') or {}).get('intermedes', []):
        i['apres'] = m[i['apres']]
    for l in d.get('lectures', []):
        l['apres'] = m[l['apres']]
        if (l.get('portrait') or {}).get('diapositive'):
            l['portrait']['diapositive'] = m[l['portrait']['diapositive']]
    for e in d.get('episodes', []):
        e['apres'] = m[e['apres']]

    # Lot des vignettes dessinées (spec 17, essai 5), écrit à la main et indexé par numéro (« 31 »,
    # « 34b ») : les numéros sont remplacés sur place, la mise en forme du fichier est gardée.
    lot_v = c.DONNEES / 'generation' / f"{d['slug']}-vignettes.json"
    if lot_v.exists():
        texte = lot_v.read_text(encoding='utf-8')
        neuf = re.sub(r'("n":\s*")(\d+)([a-z]?")', lambda mm: f'{mm[1]}{m.get(int(mm[2]), int(mm[2]))}{mm[3]}', texte)
        if neuf != texte:
            lot_v.write_text(neuf, encoding='utf-8')

    # 3. États du cache indexés par numéro.
    # utile.json a aussi des clés « 18m2 », « 20a » (mosaïques, avant / après) ; personnes.json et
    # surimpressions.json sont indexés par numéro (ajout du 2026-10-12, avec la couche générée).
    for nom_etat in ('images.json', 'voix.json', 'camera.json', 'utile.json', 'personnes.json', 'surimpressions.json'):
        ef = c.CACHE / d['slug'] / nom_etat
        if not ef.exists():
            continue
        etat = json.loads(ef.read_text())
        nouvel = {}
        for cle, v in etat.items():
            mm = re.fullmatch(r'(\d+)((?:m\d+|a)?)', cle)
            if mm:
                if int(mm[1]) in m:
                    nouvel[str(m[int(mm[1])]) + mm[2]] = v
            else:
                nouvel[cle] = v   # lectures, épisodes, annexes : clés par identifiant
        if nom_etat == 'camera.json':
            for x in liste:
                v = nouvel.get(str(x['n']))
                ancien = next((o for o, nv in m.items() if nv == x['n']), None)
                if v and ancien in cam_valide:
                    v['empreinte'] = camera.empreinte(x)
        ef.write_text(json.dumps(nouvel, ensure_ascii=False, indent=1))
    # 4. Couche générée (spec 16) : lot src/data/diaporamas/<siecle>/generation/<slug>.json, manifeste et fichiers
    # du cache (.cache/diaporamas/<slug>/generation/{sources,clips,bruts,planches}/NNN…). Le kit zip, lui,
    # garde les anciens numéros : le refaire par `generation.py preparer` avant un nouveau `lancer`.
    lot = c.DONNEES / 'generation' / f"{d['slug']}.json"
    if lot.exists():
        l = json.loads(lot.read_text())
        for el in l.get('elements', []):
            el['n'] = m.get(el['n'], el['n'])
        lot.write_text(json.dumps(l, ensure_ascii=False, indent=2) + '\n')
    gen = c.CACHE / d['slug'] / 'generation'
    if gen.is_dir():
        deux = []
        for sous in ('sources', 'clips', 'bruts', 'planches'):
            for g in sorted((gen / sous).glob('[0-9][0-9][0-9]*')):
                o = int(g.name[:3])
                if o in m and m[o] != o:
                    tmp = g.with_name(g.name + '.renum')
                    g.rename(tmp)
                    deux.append((tmp, g.with_name(f'{m[o]:03d}' + g.name[3:])))
        for tmp, dst in deux:
            tmp.rename(dst)
        mf = gen / 'manifeste.json'
        if mf.exists():
            man = json.loads(mf.read_text())
            for el in man.get('elements', []):
                nv = m.get(el['n'], el['n'])
                el['id'] = f'{nv:03d}' + el['id'][3:]
                el['source'] = el['source'].replace(f"{el['n']:03d}", f'{nv:03d}')
                el['n'] = nv
            mf.write_text(json.dumps(man, ensure_ascii=False, indent=1))
    c.ecrire(f, d)
    suivi = suivre_annotations(d['slug'], m)
    if suivi:
        print(f'{len(suivi)} annotation(s) de visionnage renumérotée(s) : ' + ', '.join(suivi) + '.')
    print(f'{len(temporaires)} fichier(s) renommé(s) ; débuts d’actes : {[x["debut"] for x in d["actes"]]}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
