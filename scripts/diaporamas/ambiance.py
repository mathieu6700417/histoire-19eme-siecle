#!/usr/bin/env python3
"""Ambiances sonores des images mises en mouvement (spec 17, « Ambiances sonores : règles d'intégration »).

    python3 scripts/diaporamas/ambiance.py preparer <slug> [--seulement 18,56]
    python3 scripts/diaporamas/ambiance.py lancer <slug> [--gpu L4] [--session nom] [--garder] [--reprendre]
    python3 scripts/diaporamas/ambiance.py encoder <slug> [--bruts DOSSIER] [--seulement …]
    python3 scripts/diaporamas/ambiance.py ecoute <slug>          # page d'écoute : OBLIGATOIRE avant de publier
    python3 scripts/diaporamas/ambiance.py publier <slug> [--seulement …]
    python3 scripts/diaporamas/ambiance.py retirer <slug> [--seulement …]
    python3 scripts/diaporamas/ambiance.py lister <slug>

Règle : toute diapositive mise en mouvement (`image.video`, spec 16) a son ambiance, jamais une image
fixe. La consigne (anglais ; rien que la narration ne dise ; ni voix, ni musique, ni son anachronique)
est le champ `ambiance` de l'élément du lot src/data/diaporamas/generation/<slug>.json, à côté de la
consigne du clip ; modèle et graines dans `ambiance` du lot (EzAudio s3_xl, licence MIT).

`preparer` écrit le kit (.cache/diaporamas/<slug>/ambiance/kit-ambiance.zip) ; `lancer` pilote Colab par
la CLI officielle (scripts/colab/ambiance.py : deux tirages de 10 s par diapositive, session arrêtée à
la fin, même en cas d'erreur) ; `encoder` enchaîne les tirages en fondu (tirage 1, tirage 2, tirage 1),
coupe à la durée utile (du départ du clip à la fin de la diapositive), pose un fondu d'entrée et de
sortie, ramène à NIVEAU LUFS (crêtes rabotées par un limiteur) et encode en AAC ; il mesure durée,
niveau, crête et silences (mesures.json). `--bruts` : tirages déjà calculés ailleurs (Révolution : ceux
de l'essai, .cache/diaporamas/essais-colab/colab/out/sons). `ecoute` fabrique la page d'écoute
(.cache/diaporamas/essais-colab/sons/ecoute-<slug>.html, servie par essais-colab/servir.py) : **aucun
agent ne peut écouter, l'utilisateur juge chaque lot avant publication.** `publier` copie
NNN-ambiance.m4a dans public/diaporamas/<slug>/ et écrit `image.ambiance` { fichier, duree, modele,
genere_le }. Le lecteur (src/scripts/diaporama/ambiance.ts) la joue avec le clip, à -12 dB, calée sur
l'horloge de la voix ; signalement : crédits de la page et livre d'images, rien au cartouche.
`generation.py retirer` retire l'ambiance avec le clip ; `verifier.py` : famille « ambiance (spec 17) ».
"""
from __future__ import annotations

import datetime, json, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

import commun as c
import generation as g

MODELE = 'EzAudio s3_xl'
GRAINES = [42, 43]
NIVEAU, CRETE = -23.0, -1.5        # LUFS intégrés et plafond de crête (dBTP) visés, comme à l'essai
FONDU_ENTREE, FONDU_SORTIE = 1.2, 1.5
MARGE_FIN = 0.8                    # s au-delà de la voix et de sa pause (le lecteur coupe au changement d'image)
ENCHAINE = 1.5                     # s : fondu enchaîné entre deux tirages
NIVEAU_LECTEUR_DB = -12            # constantes.ts AMBIANCE_DB (pour la page d'écoute)
REMOTE = '/content/ambiance'


def dossier(slug: str) -> Path:
    d = c.CACHE / slug / 'ambiance'
    d.mkdir(parents=True, exist_ok=True)
    return d


def elements(slug: str, seulement: set[int]) -> tuple[dict, list[dict]]:
    lot = g.lot(slug)
    els = [el for el in lot['elements'] if el.get('type') == 'mouvement' and (not seulement or el['n'] in seulement)]
    sans = [el['n'] for el in els if not el.get('ambiance')]
    if sans:
        raise SystemExit(f"Consigne d'ambiance absente du lot pour : {sans} (champ « ambiance » de l'élément)")
    return lot, els


def besoin(s: dict) -> float:
    """Durée utile (s) : du départ du clip (image simple : DEBUT_CLIP ; mosaïque : plus tard, le
    lecteur coupe) à la fin de la voix et de sa pause, plus une marge."""
    return round(((s.get('audio') or {}).get('duree') or 6) + g.PAUSE + MARGE_FIN - g.DEBUT_CLIP, 2)


def preparer(slug: str, seulement: set[int]) -> None:
    lot, els = elements(slug, seulement)
    dest = dossier(slug)
    graines = (lot.get('ambiance') or {}).get('graines') or GRAINES
    man = dict(slug=slug, modele=MODELE, graines=graines, elements=[dict(n=el['n'], prompt=el['ambiance']) for el in els])
    (dest / 'manifeste.json').write_text(json.dumps(man, ensure_ascii=False, indent=1))
    with zipfile.ZipFile(dest / 'kit-ambiance.zip', 'w') as z:
        z.write(dest / 'manifeste.json', 'manifeste.json')
    print(f"{len(els)} ambiance(s) à calculer ({len(graines)} tirages chacune, ≈ {len(els) * len(graines) * 24 / 60:.0f} min de L4) : {(dest / 'kit-ambiance.zip').relative_to(c.RACINE)}")


def lancer(slug: str, gpu: str, session: str | None, garder: bool, reprendre: bool) -> None:
    dest = dossier(slug)
    kit = dest / 'kit-ambiance.zip'
    if not kit.exists():
        raise SystemExit(f'Kit absent : lancer « ambiance.py preparer {slug} » d\'abord')
    session = session or f'ambiance-{slug}'
    R = REMOTE
    if not reprendre:
        print(f'session « {session} » ({gpu})…')
        g.colab('new', '-s', session, '--gpu', gpu, timeout=600)
    try:
        g.colab('exec', '-s', session, '--timeout', '60', timeout=90, code=f'import os; os.makedirs("{R}/in", exist_ok=True); os.makedirs("{R}/out", exist_ok=True)')
        g.colab('upload', '-s', session, str(kit), f'{R}/kit.zip', silencieux=True)
        g.colab('upload', '-s', session, str(c.RACINE / 'scripts' / 'colab' / 'ambiance.py'), f'{R}/ambiance.py', silencieux=True)
        g.colab('exec', '-s', session, '--timeout', '60', timeout=90, code=(
            f'import zipfile, subprocess; zipfile.ZipFile("{R}/kit.zip").extractall("{R}/in"); '
            f'subprocess.Popen("nohup env ENTREE={R}/in SORTIE={R}/out python3 {R}/ambiance.py > {R}/out/log.txt 2>&1 &", shell=True); print("lancé")'))
        lu, debut = 0, time.time()
        while True:
            time.sleep(30)
            try:
                texte = g.colab('exec', '-s', session, '--timeout', '30', timeout=60, essais=1, silencieux=True,
                                code=f'import os; p="{R}/out/log.txt"; print(open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else "")')
            except (SystemExit, subprocess.TimeoutExpired) as e:
                print(f'  (lecture du journal impossible : {e})')
                continue
            lignes = [l for l in texte.splitlines() if re.match(r'\d\d:\d\d:\d\d ', l)]
            for l in lignes[lu:]:
                print(l)
            lu = len(lignes)
            if any(l.endswith(' FIN') or ' ERREUR ' in l for l in lignes[-2:]):
                break
            if time.time() - debut > 3600:
                print('plus d\'une heure : on arrête le suivi')
                break
        g.colab('exec', '-s', session, '--timeout', '60', timeout=90, code=f'import subprocess; subprocess.run("cd {R}/out && rm -f ../sorties.zip && zip -q -0 ../sorties.zip *.wav journal.jsonl", shell=True)')
        g.colab('download', '-s', session, f'{R}/sorties.zip', str(dest / 'sorties.zip'), silencieux=True, timeout=900)
        (dest / 'bruts').mkdir(exist_ok=True)
        with zipfile.ZipFile(dest / 'sorties.zip') as z:
            z.extractall(dest / 'bruts')
        (dest / 'sorties.zip').unlink()
        print(f"{len(list((dest / 'bruts').glob('*.wav')))} tirage(s) dans {(dest / 'bruts').relative_to(c.RACINE)}/")
    finally:
        if garder:
            print(f'session « {session} » laissée ouverte (colab stop -s {session})')
        else:
            g.colab('stop', '-s', session, timeout=300)
            print(f'session « {session} » arrêtée ; vérifier : colab sessions')


def ff(*a) -> str:
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-y', *map(str, a)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-800:])
    return r.stderr


def mesurer(f: Path) -> dict:
    """Durée, niveau intégré (LUFS), crête vraie (dBTP), plus long silence (sous -50 dB, 0,8 s au moins)."""
    e = ff('-i', f, '-af', 'ebur128=peak=true,silencedetect=noise=-50dB:d=0.8', '-f', 'null', '-')
    fin = e[e.rfind('Summary:'):]
    val = lambda motif: float(re.search(motif, fin).group(1).replace('-inf', '-99'))
    silences = [float(x) for x in re.findall(r'silence_duration: ([\d.]+)', e)]
    duree = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout)
    return dict(duree=round(duree, 2), lufs=val(r'I:\s+(-?[\d.]+|-inf) LUFS'), crete_dbtp=val(r'Peak:\s+(-?[\d.]+|-inf) dBFS'), silence_max=round(max(silences, default=0), 2))


def encoder(slug: str, bruts: Path | None, seulement: set[int]) -> None:
    _, els = elements(slug, seulement)
    _, d = c.lire(slug)
    par_n = {s['n']: s for s in d['diapositives']}
    dest = dossier(slug)
    bruts = bruts or dest / 'bruts'
    (dest / 'sons').mkdir(exist_ok=True)
    tmp = dest / 'tmp'
    tmp.mkdir(exist_ok=True)
    f_mes = dest / 'mesures.json'
    mesures = json.loads(f_mes.read_text()) if f_mes.exists() else {}
    for el in els:
        n, s = el['n'], par_n[el['n']]
        a, b = bruts / f'{n:03d}-ezaudio-0.wav', bruts / f'{n:03d}-ezaudio-1.wav'
        if not (a.exists() and b.exists()):
            print(f'  {n:3d} : tirages absents de {bruts}')
            continue
        duree = besoin(s)
        # Tirage 1, tirage 2, tirage 1 en fondus enchaînés (27 s) : assez pour toute diapositive, sans boucle audible.
        ff('-i', a, '-i', b, '-i', a, '-filter_complex', f'[0][1]acrossfade=d={ENCHAINE}:c1=tri:c2=tri[x];[x][2]acrossfade=d={ENCHAINE}:c1=tri:c2=tri',
           '-c:a', 'pcm_f32le', tmp / 'chaine.wav')
        ff('-i', tmp / 'chaine.wav', '-t', duree, '-af', f'afade=t=in:d={FONDU_ENTREE},afade=t=out:st={duree - FONDU_SORTIE:.2f}:d={FONDU_SORTIE}',
           '-ar', 48000, '-ac', 2, '-c:a', 'pcm_f32le', tmp / 'coupe.wav')
        m0 = mesurer(tmp / 'coupe.wav')
        gain = NIVEAU - m0['lufs']
        sortie = dest / 'sons' / f'{n:03d}-ambiance.m4a'
        # Niveau fixe ; les crêtes au-dessus du plafond (coups de canon) passent par un limiteur, réglé
        # 2,5 dB sous le plafond pour laisser sa marge au codage AAC.
        ff('-i', tmp / 'coupe.wav', '-af', f'volume={gain:.2f}dB,alimiter=level=disabled:limit={10 ** ((CRETE - 2.5) / 20):.3f}:attack=2:release=60',
           '-ar', 48000, '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', sortie)
        m = mesurer(sortie)
        m.update(besoin=duree, gain_db=round(gain, 1), limiteur=m0['crete_dbtp'] + gain > CRETE - 2.5, consigne=el['ambiance'],
                 genere_le=datetime.date.fromtimestamp(a.stat().st_mtime).isoformat())
        m['alertes'] = [t for t, v in (('silence de plus de 2 s', m['silence_max'] > 2), ('niveau à plus de 2 dB de la cible', abs(m['lufs'] - NIVEAU) > 2),
                                       ('crête au-dessus de -1 dBTP', m['crete_dbtp'] > -1), ('durée trop courte', m['duree'] < duree - 0.3)) if v]
        mesures[str(n)] = m
        print(f"  {n:3d} : {m['duree']} s, {m['lufs']} LUFS, crête {m['crete_dbtp']} dBTP, silence {m['silence_max']} s{' ; ' + ' ; '.join(m['alertes']) if m['alertes'] else ''}")
    f_mes.write_text(json.dumps(mesures, ensure_ascii=False, indent=1))
    shutil.rmtree(tmp)


def publier(slug: str, seulement: set[int]) -> None:
    lot, els = elements(slug, seulement)
    dest = dossier(slug)
    mesures = json.loads((dest / 'mesures.json').read_text()) if (dest / 'mesures.json').exists() else {}
    f, d = c.lire(slug)
    par_n = {s['n']: s for s in d['diapositives']}
    publies = 0
    for el in els:
        s, m = par_n.get(el['n']), mesures.get(str(el['n']))
        src = dest / 'sons' / f"{el['n']:03d}-ambiance.m4a"
        if not s or not s['image'].get('video'):
            print(f"  {el['n']:3d} : pas de clip publié (image.video) : pas d'ambiance sur une image fixe")
            continue
        if not src.is_file() or not m:
            print(f"  {el['n']:3d} : ambiance absente ({src.relative_to(c.RACINE)}) : encoder d'abord")
            continue
        if m['alertes']:
            print(f"  {el['n']:3d} : non publiée, alertes : {' ; '.join(m['alertes'])}")
            continue
        cible = c.PUBLIC / slug / src.name
        if not cible.exists() or cible.read_bytes() != src.read_bytes():
            shutil.copy(src, cible)
        s['image']['ambiance'] = {'fichier': cible.name, 'duree': m['duree'], 'modele': (lot.get('ambiance') or {}).get('modele') or MODELE, 'genere_le': m['genere_le']}
        publies += 1
        print(f"  {el['n']:3d} : {cible.name}, {m['duree']} s, {cible.stat().st_size / 1e3:.0f} ko")
    c.ecrire(f, d)
    print(f'{publies} ambiance(s) publiée(s) dans {slug} ; puis : python3 scripts/diaporamas/verifier.py {slug} et npm run build')


def retirer(slug: str, seulement: set[int]) -> None:
    f, d = c.lire(slug)
    retires = 0
    for s in d['diapositives']:
        a = s['image'].get('ambiance')
        if not a or (seulement and s['n'] not in seulement):
            continue
        fichier = c.PUBLIC / slug / a['fichier']
        if fichier.exists():
            fichier.unlink()
        del s['image']['ambiance']
        retires += 1
    c.ecrire(f, d)
    print(f'{retires} ambiance(s) retirée(s) de {slug}')


def lister(slug: str) -> None:
    _, d = c.lire(slug)
    for s in d['diapositives']:
        v, a = s['image'].get('video'), s['image'].get('ambiance')
        if v or a:
            print(f"{s['n']:4d} clip {'oui' if v else 'NON'} · ambiance {a['fichier'] + ' ' + str(a['duree']) + ' s' if a else 'ABSENTE'} · {(s['image'].get('titre_court') or s['image'].get('titre') or '')[:50]}")


def ecoute(slug: str) -> None:
    """Page d'écoute du lot encodé : clip, narration, musique de fond de l'acte, ambiance, niveau réglable."""
    _, els = elements(slug, set())
    _, d = c.lire(slug)
    par_n = {s['n']: s for s in d['diapositives']}
    src = dossier(slug)
    mesures = json.loads((src / 'mesures.json').read_text())
    base = c.CACHE / 'essais-colab' / 'sons'
    media = base / f'ecoute-{slug}'
    media.mkdir(parents=True, exist_ok=True)
    actes = sorted(d['actes'], key=lambda a: a['debut'])
    diapos = []
    for el in els:
        n, s = el['n'], par_n[el['n']]
        son = src / 'sons' / f'{n:03d}-ambiance.m4a'
        if not son.exists():
            continue
        im = s['image']
        acte = [a for a in actes if a['debut'] <= n][-1]
        fond = next((p for p in (d.get('musique') or {}).get('fond', []) if p['acte'] == acte['id']), None)
        for nom in (im['fichier'], s['audio']['fichier'], im['video']['fichier'], *([fond['fichier']] if fond else [])):
            shutil.copy(c.PUBLIC / slug / nom, media / Path(nom).name)
        shutil.copy(son, media / son.name)
        diapos.append(dict(n=n, titre=im.get('titre_court') or im.get('titre'), auteur=im.get('auteur'), narration=s['narration'], duree=s['audio']['duree'],
                           debut=g.debut_clip(s) if s.get('mosaique') else g.DEBUT_CLIP, utile=im.get('utile') or [0, 0, 1, 1], consigne=el['ambiance'], mesure=mesures[str(n)],
                           image=f"ecoute-{slug}/{im['fichier']}", voix=f"ecoute-{slug}/{s['audio']['fichier']}", clip=f"ecoute-{slug}/{im['video']['fichier']}",
                           ambiance=f'ecoute-{slug}/{son.name}', musique=f"ecoute-{slug}/{Path(fond['fichier']).name}" if fond else None,
                           plan=(s.get('plans') or [{}])[0].get('instant'), suite=bool(s.get('plans'))))
    page = base / f'ecoute-{slug}.html'
    page.write_text(GABARIT.replace('__DONNEES__', json.dumps(dict(slug=slug, titre=d.get('titre'), modele=MODELE, niveau=NIVEAU_LECTEUR_DB, cible=NIVEAU, diapos=diapos), ensure_ascii=False)))
    print(f"{len(diapos)} ambiance(s) à écouter : {page.relative_to(c.RACINE)} (python3 .cache/diaporamas/essais-colab/servir.py, puis http://127.0.0.1:8017/sons/{page.name})")


GABARIT = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,"><title>Ambiances sonores : écoute avant publication</title><link rel="stylesheet" href="../commun.css">
<style>
  #reglages { position: sticky; top: 0; z-index: 2; background: var(--fond); border-top: 1px solid var(--texte); border-bottom: 1px solid var(--texte); padding: .5rem 0; margin: 1rem 0; }
  .diapo { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 4fr); gap: 1.4rem; align-items: start; }
  .ecran { position: relative; background: #111; }
  .ecran img { display: block; width: 100%; height: auto; }
  .ecran video { position: absolute; object-fit: fill; opacity: 0; transition: opacity 1.2s; }
  .ecran.clip video { opacity: 1; }
  .barre { height: 3px; background: var(--filet); margin-top: 4px; } .barre i { display: block; height: 100%; width: 0; background: var(--texte); }
  @media (max-width: 800px) { .diapo { grid-template-columns: 1fr; } }
</style></head><body>
<p class="sur">Spec 17 · ambiances sonores · écoute avant publication</p>
<h1 id="titre"></h1>
<p>Chaque diapositive mise en mouvement, avec sa narration, la musique de fond de son acte et son ambiance générée (<span id="modele"></span>, licence MIT).
L'ambiance entre avec le clip et sort à la fin de la diapositive, comme dans le lecteur ; niveau par défaut : celui du lecteur.</p>
<p class="doux"><strong>Ces sons n'ont été écoutés par personne.</strong> Ils ont été contrôlés par mesure seulement (durée, niveau, crête, silences). À juger à l'oreille : aucune voix
intelligible, aucune musique, rien d'anachronique, rien que la narration ne dise. Pour en écarter une : retirer la diapositive au moment de publier
(<code>ambiance.py publier SLUG --seulement …</code>) ou réécrire sa consigne dans le lot et la recalculer.</p>
<div id="reglages"><div class="outils">
  <label style="flex: 1 1 18rem">niveau de l'ambiance <input type="range" id="niveau" min="-36" max="-4" step="1" style="flex:1"> <span id="niveau-t" style="min-width: 15rem"></span></label>
  <label><input type="checkbox" id="avec" checked> ambiance</label>
  <label><input type="checkbox" id="musique" checked> musique de fond</label>
  <button id="stop">Arrêter</button></div></div>
<div id="planche"></div>
<script>
const S = __DONNEES__, fr = (x, d = 1) => x.toFixed(d).replace('.', ','), GAIN_MUSIQUE = 0.08;
document.getElementById('titre').textContent = `Ambiances sonores : ${S.titre || S.slug}`;
document.getElementById('modele').textContent = S.modele;
document.body.innerHTML = document.body.innerHTML.replace('SLUG', S.slug);
const niveau = document.getElementById('niveau'); niveau.value = S.niveau;
const gain = () => (document.getElementById('avec').checked ? Math.pow(10, +niveau.value / 20) : 0);
let courant = null;
for (const d of S.diapos) {
  const s = document.createElement('section'); s.className = 'image';
  const u = d.utile, m = d.mesure;
  s.innerHTML = `<p class="sur">Diapositive ${d.n} · ${fr(d.duree)} s de voix · ambiance de ${fr(m.duree)} s à partir de ${fr(d.debut)} s</p>
    <h2>${d.auteur || ''}, <em>${d.titre}</em></h2>
    <div class="diapo"><div><div class="ecran"><img src="${d.image}" alt=""><video src="${d.clip}" muted playsinline preload="metadata"
        style="left:${u[0] * 100}%;top:${u[1] * 100}%;width:${(u[2] - u[0]) * 100}%;height:${(u[3] - u[1]) * 100}%"></video></div><div class="barre"><i></i></div>
      <div class="outils"><button class="jouer" aria-pressed="false">Lecture</button><span class="etat doux"></span></div></div>
    <div><p>${d.narration}</p><p class="doux">Consigne donnée au modèle : « ${d.consigne} ».</p>
      <p class="doux">Mesures : ${fr(m.duree)} s, ${fr(m.lufs)} LUFS, crête ${fr(m.crete_dbtp)} dBTP, plus long silence ${fr(m.silence_max)} s${m.limiteur ? ' ; crêtes rabotées par le limiteur' : ''}.
      ${d.suite ? 'Dans le lecteur, l’ambiance s’efface quand une autre image (plan) couvre le clip.' : ''}</p></div></div>`;
  document.getElementById('planche').append(s);
  const voix = new Audio(d.voix), musique = d.musique ? new Audio(d.musique) : null, amb = new Audio(d.ambiance), video = s.querySelector('video'), ecran = s.querySelector('.ecran');
  if (musique) musique.preload = 'none';
  const btn = s.querySelector('.jouer'), sc = { d, voix, musique, amb, video, joue: false };
  d.sc = sc;
  sc.arreter = () => { sc.joue = false; [voix, musique, amb, video].forEach((x) => x && x.pause()); clearTimeout(sc.t1); cancelAnimationFrame(sc.raf);
    btn.setAttribute('aria-pressed', 'false'); btn.textContent = 'Lecture'; ecran.classList.remove('clip'); if (courant === sc) courant = null; };
  sc.jouer = () => { if (courant) courant.arreter(); courant = sc; sc.joue = true; btn.setAttribute('aria-pressed', 'true'); btn.textContent = 'Arrêter';
    voix.currentTime = 0; video.currentTime = 0; amb.currentTime = 0; amb.volume = gain();
    if (musique) { musique.currentTime = 30; musique.volume = document.getElementById('musique').checked ? GAIN_MUSIQUE : 0; musique.play().catch(() => {}); }
    voix.play();
    sc.t1 = setTimeout(() => { ecran.classList.add('clip'); video.play().catch(() => {}); amb.play().catch(() => {}); }, d.debut * 1000);
    const suivre = () => { s.querySelector('.barre i').style.width = Math.min(100, 100 * voix.currentTime / d.duree) + '%'; if (sc.joue) sc.raf = requestAnimationFrame(suivre); }; suivre(); };
  voix.onended = () => setTimeout(() => { if (sc.joue && courant === sc) sc.arreter(); }, 1500);
  btn.onclick = () => (sc.joue ? sc.arreter() : sc.jouer());
}
const maj = () => { const v = +niveau.value;
  document.getElementById('niveau-t').textContent = `${v} dB : ≈ ${Math.round(-19.5 - (S.cible + v))} dB sous la voix${v === S.niveau ? ' (niveau du lecteur)' : ''}`;
  for (const d of S.diapos) { d.sc.amb.volume = gain(); if (d.sc.musique) d.sc.musique.volume = document.getElementById('musique').checked ? GAIN_MUSIQUE : 0; } };
niveau.oninput = maj; document.getElementById('musique').onchange = maj; document.getElementById('avec').onchange = maj;
document.getElementById('stop').onclick = () => courant && courant.arreter();
maj(); window.__ecoute = S;
</script></body></html>
"""


def main() -> None:
    a = sys.argv[1:]
    if len(a) < 2 or a[0] not in ('preparer', 'lancer', 'encoder', 'ecoute', 'publier', 'retirer', 'lister'):
        raise SystemExit(__doc__)
    commande, slug, reste = a[0], a[1], a[2:]

    def option(nom, defaut=None):
        return reste[reste.index(nom) + 1] if nom in reste else defaut
    seulement = g.selection(reste)
    if commande == 'preparer':
        preparer(slug, seulement)
    elif commande == 'lancer':
        lancer(slug, option('--gpu', 'L4'), option('--session'), '--garder' in reste, '--reprendre' in reste)
    elif commande == 'encoder':
        encoder(slug, Path(option('--bruts')).resolve() if option('--bruts') else None, seulement)
    elif commande == 'ecoute':
        ecoute(slug)
    elif commande == 'publier':
        publier(slug, seulement)
    elif commande == 'retirer':
        retirer(slug, seulement)
    else:
        lister(slug)


if __name__ == '__main__':
    main()
