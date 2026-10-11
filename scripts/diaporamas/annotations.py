#!/usr/bin/env python3
"""Annotations de visionnage (spec 15) : lecture et écriture de docs/annotations/<slug>.jsonl.

Les annotations sont saisies dans le lecteur lancé par `npm run annoter` (touche A) ; ce script
les relit et les marque « traité ». Avant de retoucher un diaporama :

    python3 scripts/diaporamas/annotations.py lister restauration --a-faire
    python3 scripts/diaporamas/annotations.py lister restauration --categorie cadrage
    python3 scripts/diaporamas/annotations.py lister restauration --detail 142512-037
    python3 scripts/diaporamas/annotations.py traiter 142512-037 "tête recadrée (camera_manuelle)"
    python3 scripts/diaporamas/annotations.py bilan restauration

Un identifiant peut être abrégé par sa fin (« 142512-037 », « 037 ») tant qu'il reste unique.
Ce module sert aussi de bibliothèque au serveur local (`annoter.py`) : créer, modifier, supprimer,
toutes écritures atomiques (fichier temporaire puis remplacement) et sous verrou.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import threading
from datetime import datetime, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DOSSIER = RACINE / 'docs' / 'annotations'
CATEGORIES = ['image', 'cadrage', 'texte', 'voix', 'musique', 'surimpression', 'autre']
TYPES = ['diapositive', 'plan', 'chant', 'galerie', 'lecture', 'episode', 'carton', 'generique', 'recapitulatif']
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
ID = re.compile(r'\d{8}-\d{6}-\d{3}')
VERROU = threading.RLock()


class Refus(ValueError):
    """Demande invalide (slug, identifiant, contenu)."""


def fichier(slug: str) -> Path:
    if not SLUG.fullmatch(slug or ''):
        raise Refus(f'slug invalide : {slug!r}')
    return DOSSIER / f'{slug}.jsonl'


def lire(slug: str) -> list[dict]:
    f = fichier(slug)
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines() if l.strip()]


def ecrire(slug: str, annotations: list[dict]) -> None:
    """Réécrit le fichier d'un coup (temporaire dans le même dossier, puis remplacement)."""
    f = fichier(slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=f.parent, prefix=f'.{slug}-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as h:
            for a in annotations:
                h.write(json.dumps(a, ensure_ascii=False) + '\n')
            h.flush()
            os.fsync(h.fileno())
        os.replace(tmp, f)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def maintenant() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def _texte(v) -> str:
    t = str(v or '').replace('\r\n', '\n').strip()
    if not t:
        raise Refus('texte vide')
    return t[:5000]


def _categorie(v) -> str:
    return v if v in CATEGORIES else 'autre'


# --- Contexte complété d'après le JSON de la période -------------------------------------------

def _periode(slug: str) -> dict | None:
    for f in sorted((RACINE / 'src' / 'data' / 'diaporamas').glob('*.json')):
        if re.sub(r'^\d+-', '', f.stem) == slug:
            return json.loads(f.read_text(encoding='utf-8'))
    return None


def _image(d, nom: str) -> dict | None:
    """Premier dictionnaire d'image du JSON dont `fichier` vaut `nom`."""
    if isinstance(d, dict):
        if d.get('fichier') == nom and ('commons' in d or 'titre' in d):
            return d
        d = list(d.values())
    if isinstance(d, list):
        for v in d:
            r = _image(v, nom)
            if r:
                return r
    return None


def completer(slug: str, a: dict) -> None:
    """Ajoute ce que le lecteur ne connaît pas : identifiant de l'acte, notice de l'image
    (`commons`, `titre_court`), phrase exacte de la narration (bornes de `audio.phrases`)."""
    d = _periode(slug)
    if not d:
        return
    lieu, ecran = a['lieu'], a['ecran']
    n = lieu.get('n')
    acte = None
    for x in d.get('actes', []):
        if isinstance(n, int) and x.get('debut', 0) <= n:
            acte = x.get('id') or x.get('titre')
    if acte:
        lieu['acte'] = acte
    im = ecran.get('image')
    if isinstance(im, dict) and im.get('fichier'):
        notice = _image(d, im['fichier'])
        if notice:
            im['commons'] = notice.get('commons')
            im['titre_court'] = notice.get('titre_court') or notice.get('titre')
    if lieu.get('type') in ('diapositive', 'plan'):
        x = next((x for x in d.get('diapositives', []) if x.get('n') == n), None)
        if x and x.get('narration'):
            try:
                sys.path.insert(0, str(Path(__file__).parent))
                from commun import _phrases_horodatees
                t, texte = float(lieu.get('instant') or 0), x['narration']
                ph = _phrases_horodatees(x)
                c0, c1 = next(((c0, c1) for c0, c1, t0, t1 in reversed(ph) if t0 <= t), ph[0][:2])
                ecran['phrase'] = texte[c0:c1].strip()
            except Exception:
                pass


# --- Opérations (serveur et ligne de commande) ---------------------------------------------------

def _propre(slug: str, donnees: dict) -> dict:
    """Annotation au format de la spec 15, à partir de ce qu'envoie le lecteur."""
    lieu, ecran = donnees.get('lieu') or {}, donnees.get('ecran') or {}
    if lieu.get('type') not in TYPES:
        raise Refus(f"type de lieu inconnu : {lieu.get('type')!r}")
    num = lambda v: round(float(v), 2) if isinstance(v, (int, float)) else None
    im = ecran.get('image') if isinstance(ecran.get('image'), dict) else None
    fenetre = ecran.get('fenetre')
    return {
        'id': donnees.get('id'), 'cree': donnees.get('cree') or maintenant(), 'modifie': None,
        'slug': slug, 'categorie': _categorie(donnees.get('categorie')), 'texte': _texte(donnees.get('texte')),
        'etat': 'a-faire', 'traitement': None,
        'lieu': {
            'type': lieu['type'], 'n': lieu.get('n') if isinstance(lieu.get('n'), int) else None,
            'acte': lieu.get('acte'), 'segment': lieu.get('segment'), 'plan': lieu.get('plan'),
            'image_galerie': lieu.get('image_galerie'),
            'instant': num(lieu.get('instant')), 'temps_global': num(lieu.get('temps_global')),
        },
        'ecran': {
            'image': {'fichier': str(im.get('fichier')), 'commons': None, 'titre_court': None} if im and im.get('fichier') else None,
            'phrase': ecran.get('phrase'), 'sous_titre': ecran.get('sous_titre'),
            'surimpressions': [str(s) for s in ecran.get('surimpressions') or []],
            'camera': ecran.get('camera') if isinstance(ecran.get('camera'), dict) else None,
            'musique': ecran.get('musique'),
            'fenetre': [int(v) for v in fenetre[:2]] if isinstance(fenetre, list) and len(fenetre) >= 2 else None,
            'plein_ecran': bool(ecran.get('plein_ecran')),
        },
        'capture': None,
    }


def creer(slug: str, donnees: dict) -> tuple[dict, bool]:
    """Ajoute une annotation. Rend (annotation, nouvelle) : un renvoi de la même annotation (même
    identifiant, même texte : copie de secours du lecteur) ne crée pas de doublon."""
    a = _propre(slug, donnees)
    with VERROU:
        liste = lire(slug)
        ident = a['id'] if isinstance(a['id'], str) and ID.fullmatch(a['id']) else None
        if ident:
            deja = next((x for x in liste if x['id'] == ident), None)
            if deja and deja['texte'] == a['texte']:
                return deja, False
        else:
            ident = f"{datetime.now():%Y%m%d-%H%M%S}-{(a['lieu']['n'] or 0) % 1000:03d}"
        pris = {x['id'] for x in liste}
        while ident in pris:   # même seconde, même diapositive : seconde suivante
            j, h, n = ident.split('-')
            ident = f"{datetime.strptime(j + h, '%Y%m%d%H%M%S') + timedelta(seconds=1):%Y%m%d-%H%M%S}-{n}"
        a['id'] = ident
        completer(slug, a)
        liste.append(a)
        ecrire(slug, liste)
    return a, True


def _trouver(liste: list[dict], ident: str) -> dict:
    a = next((x for x in liste if x['id'] == ident), None)
    if not a:
        raise KeyError(ident)
    return a


def modifier(slug: str, ident: str, champs: dict) -> dict:
    with VERROU:
        liste = lire(slug)
        a = _trouver(liste, ident)
        if 'texte' in champs:
            a['texte'] = _texte(champs['texte'])
        if 'categorie' in champs:
            a['categorie'] = _categorie(champs['categorie'])
        a['modifie'] = maintenant()
        ecrire(slug, liste)
    return a


def supprimer(slug: str, ident: str) -> None:
    """Retire l'annotation et efface sa capture."""
    with VERROU:
        liste = lire(slug)
        a = _trouver(liste, ident)
        ecrire(slug, [x for x in liste if x is not a])
        (DOSSIER / slug / f'{ident}.jpg').unlink(missing_ok=True)
        try:
            (DOSSIER / slug).rmdir()   # dossier des captures vide
        except OSError:
            pass


def poser_capture(slug: str, ident: str, chemin: str | None) -> bool:
    with VERROU:
        liste = lire(slug)
        a = next((x for x in liste if x['id'] == ident), None)
        if not a:
            return False
        a['capture'] = chemin
        ecrire(slug, liste)
    return True


def traiter(slug: str, ident: str, traitement: str) -> dict:
    with VERROU:
        liste = lire(slug)
        a = _trouver(liste, ident)
        a['etat'], a['traitement'] = 'traite', traitement.strip()
        ecrire(slug, liste)
    return a


# --- Ligne de commande ---------------------------------------------------------------------------

def slugs() -> list[str]:
    return sorted(f.stem for f in DOSSIER.glob('*.jsonl'))


def court(ident: str) -> str:
    return ident[4:]


def lieu_lisible(a: dict) -> str:
    l = a['lieu']
    t = f"{l['instant']:.1f} s".replace('.', ',') if l.get('instant') is not None else ''
    if l['type'] in ('generique', 'recapitulatif'):
        return f"{'générique' if l['type'] == 'generique' else 'récapitulatif'} · {t}"
    quoi = {'diapositive': '', 'plan': f"plan {l.get('plan')}", 'carton': 'carton', 'episode': 'épisode'}.get(l['type'], l['type'])
    if l['type'] in ('galerie', 'lecture') and l.get('image_galerie'):
        quoi += f" image {l['image_galerie']}"
    return ' · '.join(p for p in (f"diapositive {l['n']}", quoi, t) if p)


def resoudre(ident: str, parmi: list[str] | None = None) -> tuple[str, dict]:
    """(slug, annotation) pour un identifiant complet ou abrégé par sa fin."""
    trouves = [(s, a) for s in (parmi or slugs()) for a in lire(s) if a['id'] == ident or a['id'].endswith(ident)]
    exacts = [x for x in trouves if x[1]['id'] == ident]
    if len(exacts) == 1:
        return exacts[0]
    if not trouves:
        sys.exit(f'Annotation introuvable : {ident}')
    if len(trouves) > 1:
        sys.exit(f"Identifiant ambigu ({ident}) : " + ', '.join(f'{s}/{a["id"]}' for s, a in trouves))
    return trouves[0]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sp = ap.add_subparsers(dest='commande', required=True)
    p = sp.add_parser('lister', help='une ligne par annotation, dans l\'ordre du diaporama')
    p.add_argument('slug')
    p.add_argument('--a-faire', action='store_true')
    p.add_argument('--categorie', choices=CATEGORIES)
    p.add_argument('--detail', metavar='ID', help='tout le contexte d\'une annotation et le chemin de sa capture')
    p = sp.add_parser('traiter', help='marque une annotation comme traitée')
    p.add_argument('id')
    p.add_argument('traitement', help='ce qui a été fait, ou pourquoi rien n\'a été fait')
    p = sp.add_parser('bilan', help='nombre par catégorie et par état')
    p.add_argument('slug')
    a = ap.parse_args()
    try:
        if a.commande == 'lister' and a.detail:
            _, x = resoudre(a.detail, [a.slug])
            print(json.dumps(x, ensure_ascii=False, indent=2))
            c = DOSSIER / x['capture'] if x.get('capture') else None
            print(f"capture : {c if c and c.exists() else 'aucune'}")
        elif a.commande == 'lister':
            liste = sorted(lire(a.slug), key=lambda x: (x['lieu'].get('temps_global') or 0, x['id']))
            liste = [x for x in liste if (not a.a_faire or x['etat'] == 'a-faire') and (not a.categorie or x['categorie'] == a.categorie)]
            for x in liste:
                etat = 'à faire' if x['etat'] == 'a-faire' else 'traité '
                texte = ' / '.join(x['texte'].splitlines())
                print(f"{court(x['id'])}  {etat}  {x['categorie']:<13}  {lieu_lisible(x):<34}  {texte}")
                if x['etat'] == 'traite' and x.get('traitement'):
                    print(f"{'':17}→ {x['traitement']}")
            print(f"{len(liste)} annotation(s)" + (' à faire' if a.a_faire else '') + f" · détail : lister {a.slug} --detail <id>")
        elif a.commande == 'traiter':
            slug, x = resoudre(a.id)
            x = traiter(slug, x['id'], a.traitement)
            print(f"{slug} {court(x['id'])} : traité — {x['traitement']}")
        elif a.commande == 'bilan':
            liste = lire(a.slug)
            faits = sum(1 for x in liste if x['etat'] == 'traite')
            print(f"{a.slug} : {len(liste)} annotation(s), {faits} traitée(s), {len(liste) - faits} à faire")
            for c in CATEGORIES:
                l = [x for x in liste if x['categorie'] == c]
                if l:
                    print(f"  {c:<13} {len(l):>3}  dont {sum(1 for x in l if x['etat'] == 'a-faire')} à faire")
    except Refus as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
