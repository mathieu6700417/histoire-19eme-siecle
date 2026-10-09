"""Banc d'essai des modèles Gemini par tâche : jetons réels, coût estimé, qualité (spec 12, outillage).

À lancer quand les crédits Gemini sont rechargés, AVANT toute passe de masse : pour une tâche,
quelques diapositives (5 par défaut), chaque modèle candidat et chaque budget de réflexion ; il
mesure les jetons réellement renvoyés (entrée, sortie, réflexion), le temps, le coût estimé
(tarifs indicatifs de gemini.py) et une mesure de qualité propre à la tâche, puis écrit un tableau
et, pour les tâches d'image, une planche (une ligne par diapositive, une colonne par réglage).
Rien n'est écrit dans les JSON des périodes ; les caches des scripts ne sont ni lus ni écrits.

Usage :
    python3 scripts/diaporamas/banc_gemini.py camera consulat-empire --essai      # plan, sans appel
    python3 scripts/diaporamas/banc_gemini.py camera consulat-empire --budget 1.00
    python3 scripts/diaporamas/banc_gemini.py visages revolution --n 6 19 77 91 106
    python3 scripts/diaporamas/banc_gemini.py utile consulat-empire --reflexions 0 256
    python3 scripts/diaporamas/banc_gemini.py transcription revolution \\
        --modeles gemini-3.8-flash gemini-3.5-transcribe --reflexions 0

Tâches et qualité mesurée :
- camera        : caméra proposée (camera.cadrer, essais et relecture compris) ; qualité = erreurs du
                  contrôle mécanique sur la caméra rendue (vues, visages, tête hors champ, étapes
                  ignorées) et repli ; planche des vues réelles.
- visages       : relevé des visages ; qualité = rappel et précision contre la détection locale
                  (YuNet, visages-local.json) ; planche des rectangles.
- utile         : zone utile proposée par le modèle ; qualité = écart moyen des bords à la zone
                  actuelle du JSON ; planche.
- transcription : transcription de contrôle de voix.py sur l'audio existant ; qualité = fidélité
                  (voix.fidelite) au texte lu (cache voix.json).

Sorties : .cache/diaporamas/banc/<tache>-<slug>-<horodatage>.json (toutes les mesures) et .jpg
(planche) ; tableau récapitulatif à l'écran (moyennes par réglage).
"""
import argparse, json, subprocess, sys, time
from datetime import datetime

from PIL import Image, ImageDraw

import commun as c
import gemini

CANDIDATS = {
    'camera': ['gemini-3.8-flash', 'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite'],
    'visages': ['gemini-3.8-flash', 'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite'],
    'utile': ['gemini-3.8-flash', 'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite'],
    'transcription': ['gemini-3.8-flash', 'gemini-3.5-transcribe', 'gemini-3.5-flash-lite'],
}
REFLEXIONS = [0, 256, 1024]
# Ordre de grandeur des jetons par diapositive (pour le plan --essai seulement) : entrée, sortie.
ESTIMATION = {'camera': (15000, 8000), 'visages': (1500, 400), 'utile': (1500, 300), 'transcription': (1200, 300)}


def choisir(d: dict, ns: list[int] | None, k: int, tache: str) -> list[dict]:
    xs = [x for x in d['diapositives'] if (x.get('image') or {}).get('fichier')]
    if tache == 'transcription':
        xs = [x for x in xs if (x.get('audio') or {}).get('fichier')]
    if ns:
        return [x for x in xs if x['n'] in ns]
    pas = max(1, len(xs) // k)
    return xs[::pas][:k]


def regler(tache: str, modele: str, reflexion: int) -> None:
    gemini._choix[tache] = modele
    gemini._reflexion[tache] = reflexion
    if tache == 'camera':
        import camera
        camera.MODELE = modele
    elif tache == 'utile':
        import utile
        utile.MODELE = modele
    elif tache == 'transcription':
        import voix
        voix.MODELE_TRANSCRIPTION = modele


def _iou(a, b) -> float:
    i = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


def mesurer(tache: str, slug: str, x: dict) -> dict:
    """Un appel (ou une suite d'appels) de la tâche ; rend résultat et qualité."""
    if tache == 'camera':
        import camera as cam
        r = cam.cadrer(slug, x)
        L, H = cam.dims(x)
        faces = cam.visages(slug, x, appeler=False) or []
        e = (cam.erreurs_vues(x, r['camera'], L, H, cam.image_de(slug, x), faces)
             + cam.ignorees(x, r['camera'], L, H) + cam.tete_hors_champ(x, r['camera'], L, H, faces))
        return {'resultat': r['camera'], 'erreurs': len(e), 'repli': bool(r.get('repli')),
                'qualite': f"{len(e)} erreur(s){' repli' if r.get('repli') else ''}"}
    if tache == 'visages':
        import camera as cam
        im = cam.avec_grille(cam.reduire(cam.image_de(slug, x)))
        r = cam.appel([{'role': 'user', 'parts': [{'text': f"Image : {x['image'].get('titre')}."},
                                                  {'inlineData': {'mimeType': 'image/jpeg', 'data': cam._jpeg(im)}}]}],
                      cam.VISAGES_CONSIGNES, cam.VISAGES_SCHEMA, tache='visages')
        g = [[float(k[q]) for q in ('gauche', 'haut', 'droite', 'bas')] for k in r.get('visages') or []]
        cam.preparer_visages_locaux(slug, [x])
        loc = [k for k in cam._visages_locaux_cache(slug)[1].get(cam.empreinte_image(slug, x), [])
               if k[3] - k[1] >= cam.FACE_MIN]
        trouves = sum(1 for k in loc if any(_iou(k, h) > 0.3 for h in g))
        return {'resultat': g, 'rappel_local': trouves / len(loc) if loc else None,
                'qualite': f"{len(g)} visage(s), {trouves}/{len(loc)} des locaux"}
    if tache == 'utile':
        import utile
        im = Image.open(c.PUBLIC / slug / x['image']['fichier']).convert('RGB')
        v = utile.vision(im, x)
        ref = x['image'].get('utile') or [0, 0, 1, 1]
        ecart = sum(abs(a - b) for a, b in zip(v['zone'], ref)) / 4
        return {'resultat': v['zone'], 'ecart': ecart, 'qualite': f'écart moyen {ecart:.3f}'}
    if tache == 'transcription':
        import voix
        etat = json.loads((c.CACHE / slug / 'voix.json').read_text())
        attendu = (etat.get(str(x['n'])) or {}).get('texte') or x['narration']
        fichier = c.PUBLIC / slug / x['audio']['fichier']
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(fichier), '-ac', '1', '-ar', str(voix.TAUX),
                              '-f', 's16le', '-'], capture_output=True, check=True).stdout
        t = voix.transcrire(pcm)
        f = voix.fidelite(attendu, t)
        return {'resultat': t, 'fidelite': f, 'qualite': f'fidélité {f:.3f}'}
    raise SystemExit(f'tâche inconnue : {tache}')


def planche(tache: str, slug: str, xs: list[dict], reglages: list[str], mesures: list[dict], sortie) -> None:
    if tache not in ('camera', 'visages', 'utile'):
        return
    import camera as cam
    W = 300
    P = Image.new('RGB', (W * len(reglages), W * len(xs)), 'white')
    dr0 = ImageDraw.Draw(P)
    for i, x in enumerate(xs):
        base = cam.image_de(slug, x).convert('RGB')
        L, H = cam.dims(x)
        for j, rg in enumerate(reglages):
            m = next((m for m in mesures if m['n'] == x['n'] and m['reglage'] == rg), None)
            im = base.copy()
            if m and 'resultat' in m:
                if tache == 'camera':
                    im = cam.avec_vues(im, x, m['resultat'], L, H)
                else:
                    d = ImageDraw.Draw(im)
                    boites = m['resultat'] if tache == 'visages' else [m['resultat']]
                    for k in boites:
                        d.rectangle([k[0] * im.width, k[1] * im.height, k[2] * im.width, k[3] * im.height],
                                    outline=(220, 0, 0), width=max(2, im.width // 200))
            im.thumbnail((W, W - 30))
            P.paste(im, (j * W, i * W + 30))
            dr0.text((j * W + 4, i * W + 4), f"{x['n']} · {rg}", fill='black')
            if m:
                dr0.text((j * W + 4, i * W + 16), (m.get('qualite') or m.get('erreur', ''))[:48], fill='black')
    P.save(sortie, quality=82)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('tache', choices=sorted(CANDIDATS))
    p.add_argument('slug')
    p.add_argument('--n', type=int, nargs='+', help='diapositives (défaut : 5 réparties sur la période)')
    p.add_argument('--nombre', type=int, default=5)
    p.add_argument('--modeles', nargs='+', help='modèles candidats (défaut : ceux de la tâche)')
    p.add_argument('--reflexions', type=int, nargs='+', default=REFLEXIONS, help='budgets de réflexion essayés')
    p.add_argument('--budget', type=float, default=1.00, help='plafond de dépense du banc ($, défaut 1,00)')
    p.add_argument('--essai', action='store_true', help='affiche le plan et une estimation, sans appel')
    a = p.parse_args()
    c.charger_env()
    _, d = c.lire(a.slug)
    xs = choisir(d, a.n, a.nombre, a.tache)
    modeles = a.modeles or CANDIDATS[a.tache]
    reglages = [(m, r) for m in modeles for r in a.reflexions]
    noms = [f'{m} r{r}' for m, r in reglages]
    est_e, est_s = ESTIMATION[a.tache]
    est = sum(len(xs) * (est_e * gemini.tarif(m)[0] + (est_s + max(r, 0)) * gemini.tarif(m)[1]) / 1e6 for m, r in reglages)
    print(f"Banc {a.tache} sur {a.slug} : diapositives {[x['n'] for x in xs]} ; {len(reglages)} réglage(s) "
          f"({', '.join(noms)}) ; {len(xs) * len(reglages)} essai(s) ; estimation grossière ~{est:.2f} $ "
          f"(plafond {a.budget:.2f} $).")
    if a.essai:
        return 0
    gemini.plafond = a.budget
    mesures = []
    try:
        for (m, r), nom in zip(reglages, noms):
            regler(a.tache, m, r)
            for x in xs:
                avant = dict(gemini.depense)
                t0 = time.time()
                try:
                    res = mesurer(a.tache, a.slug, x)
                except gemini.BudgetAtteint:
                    raise
                except Exception as e:  # noqa: BLE001
                    res = {'erreur': str(e)[:200]}
                dep = {k: gemini.depense[k] - avant[k] for k in ('appels', 'entree', 'sortie', 'reflexion', 'dollars')}
                mesures.append({'reglage': nom, 'modele': m, 'reflexion': r, 'n': x['n'],
                                'secondes': round(time.time() - t0, 1), **dep, **res})
                print(f"{nom:32s} {x['n']:4d} {dep['entree']:6d} e {dep['sortie']:6d} s ({dep['reflexion']:5d} r) "
                      f"{dep['dollars']:.4f} $ {res.get('qualite') or res.get('erreur', '')}")
    except gemini.BudgetAtteint as e:
        print(f'ARRÊT : {e} ; mesures gardées.')
    dossier = c.CACHE / 'banc'
    dossier.mkdir(parents=True, exist_ok=True)
    base = dossier / f"{a.tache}-{d['slug']}-{datetime.now():%Y%m%d-%H%M}"
    base.with_suffix('.json').write_text(json.dumps(mesures, ensure_ascii=False, indent=1))
    print(f"\n{'réglage':32s} {'essais':>6s} {'entrée':>8s} {'sortie':>8s} {'réflex.':>8s} {'$ / diapo':>9s}  qualité")
    for nom in noms:
        ms = [m for m in mesures if m['reglage'] == nom]
        if not ms:
            continue
        moy = lambda k: sum(m[k] for m in ms) / len(ms)
        q = {'camera': lambda: f"{sum(m.get('erreurs', 0) for m in ms)} erreur(s), {sum(m.get('repli', False) for m in ms)} repli(s)",
             'visages': lambda: f"rappel local moyen {sum(m.get('rappel_local') or 0 for m in ms) / len(ms):.0%}",
             'utile': lambda: f"écart moyen {sum(m.get('ecart', 0) for m in ms) / len(ms):.3f}",
             'transcription': lambda: f"fidélité moyenne {sum(m.get('fidelite', 0) for m in ms) / len(ms):.3f}"}[a.tache]()
        err = sum('erreur' in m for m in ms)
        print(f"{nom:32s} {len(ms):6d} {moy('entree'):8.0f} {moy('sortie'):8.0f} {moy('reflexion'):8.0f} "
              f"{moy('dollars'):9.4f}  {q}{f' ; {err} échec(s)' if err else ''}")
    planche(a.tache, d['slug'], xs, noms, mesures, base.with_suffix('.jpg'))
    print(gemini.bilan())
    print('Mesures :', base.with_suffix('.json').relative_to(c.RACINE))
    return 0


if __name__ == '__main__':
    sys.exit(main())
