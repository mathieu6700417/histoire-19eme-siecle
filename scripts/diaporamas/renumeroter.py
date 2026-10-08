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
public/diaporamas/<slug>/, en deux temps pour éviter les collisions), `image.fichier` et
`audio.fichier` (et `NNN-apres.webp`, `NNN-mK.webp` des avant/après et mosaïques, `parallaxe/NNN-k.webp` des parallaxes), débuts d'actes, `apres` des intermèdes, lectures et épisodes,
`portrait.diapositive` des lectures. Les états de .cache/diaporamas/<slug>/ indexés par numéro
(images.json, voix.json, camera.json) sont réindexés : les voix, licences et cadrages inchangés
restent reconnus, rien n'est resynthétisé (l'empreinte du texte fait foi). L'empreinte de
caméra, qui contient le nom du fichier image, est recalculée pour les entrées encore valables.
`--essai` affiche la correspondance sans rien écrire.
"""
import argparse, json, sys

import commun as c
import camera


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
            autres = [x['image'].get('apres') or {}] + list((x.get('mosaique') or {}).get('vignettes', []))
            for obj in autres:
                f_ = obj.get('fichier') or ''
                if f_.startswith(f'{o:03d}-'):
                    neuf = f'{nv:03d}-' + f_[4:]
                    renommages.append((dossier / f_, dossier / neuf))
                    obj['fichier'] = neuf
                elif f_ == c.nom(o, 'webp'):
                    obj['fichier'] = c.nom(nv, 'webp')
            # Plans d'une parallaxe (parallaxe/NNN-k.webp, point 6).
            par = x['image'].get('parallaxe') or {}
            for k, f_ in enumerate(par.get('plans', [])):
                if f_.startswith(f'parallaxe/{o:03d}-'):
                    neuf = f'parallaxe/{nv:03d}-' + f_[len('parallaxe/') + 4:]
                    renommages.append((dossier / f_, dossier / neuf))
                    par['plans'][k] = neuf
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

    # 3. États du cache indexés par numéro.
    for nom_etat in ('images.json', 'voix.json', 'camera.json'):
        ef = c.CACHE / d['slug'] / nom_etat
        if not ef.exists():
            continue
        etat = json.loads(ef.read_text())
        nouvel = {}
        for cle, v in etat.items():
            if cle.isdigit():
                if int(cle) in m:
                    nouvel[str(m[int(cle)])] = v
            else:
                nouvel[cle] = v   # lectures, épisodes, annexes : clés par identifiant
        if nom_etat == 'camera.json':
            for x in liste:
                v = nouvel.get(str(x['n']))
                ancien = next((o for o, nv in m.items() if nv == x['n']), None)
                if v and ancien in cam_valide:
                    v['empreinte'] = camera.empreinte(x)
        ef.write_text(json.dumps(nouvel, ensure_ascii=False, indent=1))
    c.ecrire(f, d)
    print(f'{len(temporaires)} fichier(s) renommé(s) ; débuts d’actes : {[x["debut"] for x in d["actes"]]}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
