#!/usr/bin/env python3
"""Images colorisées par IA (spec 16, « la colorisation couleur seule ») : publication dans une période.

Les versions colorisées sont fabriquées hors du site (Colab : FLUX.2 klein 4B, dont on ne garde que la
chrominance, posée sur la luminance de l'original ; journal docs/journal/<siecle>/generation-colorisation.jsonl)
et jugées sur planche. Ce script les intègre au diaporama, où le lecteur montre l'original puis un
fondu lent vers la couleur (src/scripts/diaporama/couleur.ts).

    python3 scripts/diaporamas/couleur.py publier <slug> <lot.json> [--seulement 86 34b …] [--sauf 100 …]
                                                  [--jugement bon] [--modele NOM] [--essai]
    python3 scripts/diaporamas/couleur.py retirer <slug> 86 34b …      # ou --tout
    python3 scripts/diaporamas/couleur.py lister <slug>

`lot.json` : la liste des images colorisées (ou un objet qui la porte dans `images`), chacune avec
`commons` (le fichier Commons de l'image d'origine : c'est la clé, elle survit aux renumérotations),
`utile` (zone utile au moment de la fabrication), `sortie` (le WebP colorisé, chemin relatif au lot),
et au besoin `jugement`, `modele`, `consigne`, `graine`, `saturation`. Le premier lot
(`resultats-couleur.json`, avec `variantes.couleur`) est lu aussi.

`publier` retrouve chaque image par son `commons` parmi les images des diapositives et des plans,
refuse celle dont la zone utile a changé ou dont le WebP n'a pas exactement la taille de la zone
utile (le calque couleur se superpose au pixel), refuse un clip `video`, un avant / après, une
mosaïque ; copie le WebP dans public/<siecle>/diaporamas/<slug>/ sous le nom de l'image suivi de « -couleur »
(086-couleur.webp, 034-b-couleur.webp) ; écrit `image.couleur` { fichier, largeur, hauteur, modele,
genere_le } ; consigne la recette (consigne, graine, saturation, méthode) dans
src/data/diaporamas/<siecle>/generation/<slug>-couleur.json, par `commons`. Idempotent.
Les cibles de `--seulement`, `--sauf` et `retirer` sont des numéros ACTUELS : `86` (image de la
diapositive), `34b` ou `34-b` (plan). `renumeroter.py` suit fichiers et champs ; `verifier.py`
contrôle la famille « couleur (spec 16) ».
"""
from __future__ import annotations

import argparse, datetime, json, re, shutil, sys
from pathlib import Path

from PIL import Image

import commun as c

MODELE = 'black-forest-labs/FLUX.2-klein-4B'
SUFFIXE = '-couleur.webp'


def images(d: dict) -> list[dict]:
    """Images qui peuvent être colorisées, dans l'ordre : {'cle' (86, 34b), 'image', 'x' (diapositive),
    'plan' (rang du plan, None pour l'image de la diapositive)}."""
    sortie = []
    for x in d['diapositives']:
        sortie.append({'cle': str(x['n']), 'image': x['image'], 'x': x, 'plan': None})
        for k, p in enumerate(x.get('plans') or []):
            if isinstance(p.get('image'), dict):
                lettre = c.LETTRES_PLANS[k] if k < len(c.LETTRES_PLANS) else chr(ord('b') + k)
                sortie.append({'cle': f"{x['n']}{lettre}", 'image': p['image'], 'x': x, 'plan': k})
    return sortie


def cle(texte: str) -> str:
    """« 34-b », « 034b » → « 34b »."""
    m = re.fullmatch(r'0*(\d+)-?([a-z]?)', texte.strip().lower())
    if not m:
        raise SystemExit(f'cible « {texte} » : attendu un numéro de diapositive (86) ou de plan (34b)')
    return m[1] + m[2]


def zone_px(i: dict) -> tuple[int, int, int, int]:
    """Zone utile de l'image en pixels entiers (même arrondi qu'à la fabrication et que dans le lecteur)."""
    u = i.get('utile') or [0, 0, 1, 1]
    L, H = i.get('largeur') or 1600, i.get('hauteur') or 1200
    return round(u[0] * L), round(u[1] * H), round(u[2] * L), round(u[3] * H)


def incompatibilite(e: dict) -> str | None:
    """Ce qui interdit de coloriser cette image (spec 16), ou None."""
    i, x = e['image'], e['x']
    if e['plan'] is None and i.get('video'):
        return 'image mise en mouvement (clip `video`)'
    if x['image'].get('apres'):
        return 'avant / après'
    if x.get('mosaique'):
        return 'mosaïque'
    return None


def entrees(lot_f: Path) -> tuple[list[dict], dict]:
    """Entrées du lot, ramenées au même format, et ses champs communs (méthode, modèle)."""
    brut = json.loads(lot_f.read_text(encoding='utf-8'))
    commun = {k: v for k, v in brut.items() if k not in ('images', 'ecartees')} if isinstance(brut, dict) else {}
    liste = brut.get('images', []) if isinstance(brut, dict) else brut
    sortie = []
    for el in liste:
        v = (el.get('variantes') or {}).get('couleur')   # premier lot : resultats-couleur.json
        sortie.append({**{k: w for k, w in el.items() if k != 'variantes'}, **(v or {})})
    return sortie, commun


def recettes_f(slug: str) -> Path:
    return c.DONNEES / 'generation' / f'{slug}-couleur.json'


def lire_recettes(slug: str) -> dict:
    f = recettes_f(slug)
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {'usage': 'couleur', 'images': {}}


def ecrire_recettes(slug: str, r: dict) -> None:
    f = recettes_f(slug)
    if not r['images']:
        f.unlink(missing_ok=True)
        return
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def publier(slug: str, lot_f: Path, seulement: set[str], sauf: set[str], jugement: str | None, modele: str | None, essai: bool) -> int:
    f, d = c.lire(slug)
    slug = d['slug']
    liste, commun = entrees(lot_f)
    par_commons: dict[str, list[dict]] = {}
    for e in images(d):
        par_commons.setdefault(e['image'].get('commons'), []).append(e)
    recettes = lire_recettes(slug)
    if commun.get('methode'):
        recettes['methode'] = commun['methode']
    publies, refus, poids = [], [], 0
    for el in liste:
        nom = f"{el.get('cle', '?')} ({el.get('commons', '?')[:60]})"
        if jugement and el.get('jugement') != jugement:
            continue
        src = lot_f.parent / (el.get('sortie') or '')
        candidats = par_commons.get(el.get('commons'), [])
        if not candidats:
            refus.append(f'{nom} : image absente de la période (commons inconnu)')
            continue
        if not el.get('sortie') or not src.is_file():
            refus.append(f"{nom} : fichier colorisé absent ({el.get('sortie')})")
            continue
        with Image.open(src) as im:
            taille, fmt = im.size, im.format
        for e in candidats:
            i = e['image']
            if (seulement and e['cle'] not in seulement) or e['cle'] in sauf:
                continue
            ici = f"{e['cle']:>5}"
            pb = incompatibilite(e)
            u, uf = i.get('utile') or [0, 0, 1, 1], el.get('utile') or [0, 0, 1, 1]
            x0, y0, x1, y1 = zone_px(i)
            if pb:
                refus.append(f'{ici} : {pb} : pas de couleur')
            elif max(abs(a - b) for a, b in zip(u, uf)) > 1e-6:
                refus.append(f'{ici} : zone utile changée depuis la fabrication ({uf} → {u}) : à refaire')
            elif taille != (x1 - x0, y1 - y0):
                refus.append(f'{ici} : {taille[0]}×{taille[1]} ≠ zone utile {x1 - x0}×{y1 - y0} : à refaire')
            elif fmt != 'WEBP':
                refus.append(f'{ici} : format {fmt} (WebP attendu)')
            else:
                cible = c.PUBLIC / slug / (Path(i['fichier']).with_suffix('').as_posix() + SUFFIXE)
                quand = datetime.date.fromtimestamp(src.stat().st_mtime).isoformat()
                if not essai:
                    if not cible.exists() or cible.read_bytes() != src.read_bytes():
                        shutil.copy(src, cible)
                    i['couleur'] = {'fichier': cible.relative_to(c.PUBLIC / slug).as_posix(), 'largeur': taille[0], 'hauteur': taille[1],
                                    'modele': modele or el.get('modele') or commun.get('modele') or MODELE, 'genere_le': quand}
                    recettes['images'][i['commons']] = {k: el[k] for k in ('consigne', 'graine', 'saturation', 'pas', 'methode', 'jugement', 'remarque') if el.get(k) is not None}
                poids += src.stat().st_size
                publies.append(e['cle'])
                print(f"  {ici} : {cible.name} {taille[0]}×{taille[1]}, {src.stat().st_size / 1e3:.0f} ko")
    for r in refus:
        print(f'  REFUS {r}')
    if not essai:
        c.ecrire(f, d)
        ecrire_recettes(slug, recettes)
    print(f"{len(publies)} image(s) colorisée(s) {'à publier' if essai else 'publiée(s)'} dans {slug} ({poids / 1e6:.1f} Mo), {len(refus)} refus"
          + ('' if essai else f' ; puis : python3 scripts/diaporamas/verifier.py {slug} et npm run build'))
    return 1 if refus else 0


def retirer(slug: str, cibles: set[str], tout: bool) -> int:
    f, d = c.lire(slug)
    slug = d['slug']
    recettes = lire_recettes(slug)
    retires = []
    for e in images(d):
        v = e['image'].get('couleur')
        if not v or not (tout or e['cle'] in cibles):
            continue
        (c.PUBLIC / slug / v['fichier']).unlink(missing_ok=True)
        del e['image']['couleur']
        retires.append(e['cle'])
    restantes = {e['image'].get('commons') for e in images(d) if e['image'].get('couleur')}
    recettes['images'] = {k: v for k, v in recettes['images'].items() if k in restantes}
    c.ecrire(f, d)
    ecrire_recettes(slug, recettes)
    inconnues = sorted(cibles - set(retires))
    print(f"{len(retires)} image(s) colorisée(s) retirée(s) de {slug} : {', '.join(retires) or 'aucune'}"
          + (f" ; sans couleur : {', '.join(inconnues)}" if inconnues else ''))
    return 0


def lister(slug: str) -> int:
    _, d = c.lire(slug)
    poids = n = 0
    for e in images(d):
        v = e['image'].get('couleur')
        if not v:
            continue
        g = c.PUBLIC / d['slug'] / v['fichier']
        ko = g.stat().st_size / 1e3 if g.exists() else 0
        poids += ko
        n += 1
        print(f"  {e['cle']:>5} : {v['fichier']} {v['largeur']}×{v['hauteur']}, {ko:.0f} ko — {e['image'].get('titre_court') or e['image'].get('titre')}")
    print(f"{n} image(s) colorisée(s) dans {d['slug']}, {poids / 1e3:.1f} Mo")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='commande', required=True)
    p = sp.add_parser('publier')
    p.add_argument('slug')
    p.add_argument('lot', type=Path)
    p.add_argument('--seulement', nargs='+', default=[], metavar='CLE')
    p.add_argument('--sauf', nargs='+', default=[], metavar='CLE')
    p.add_argument('--jugement', help='ne publier que les entrées de ce jugement (ex. bon)')
    p.add_argument('--modele')
    p.add_argument('--essai', action='store_true', help="n'écrit rien")
    r = sp.add_parser('retirer')
    r.add_argument('slug')
    r.add_argument('cibles', nargs='*', metavar='CLE')
    r.add_argument('--tout', action='store_true')
    l = sp.add_parser('lister')
    l.add_argument('slug')
    a = ap.parse_args()
    if a.commande == 'publier':
        return publier(a.slug, a.lot.resolve(), {cle(k) for k in a.seulement}, {cle(k) for k in a.sauf}, a.jugement, a.modele, a.essai)
    if a.commande == 'retirer':
        if not a.cibles and not a.tout:
            raise SystemExit('retirer : donner des cibles (86 34b) ou --tout')
        return retirer(a.slug, {cle(k) for k in a.cibles}, a.tout)
    return lister(a.slug)


if __name__ == '__main__':
    sys.exit(main())
