"""Paroles des intermèdes chantés calées au mot (spec 12, « Paroles des chants façon clip »,
2026-10-08).

Usage :
    python3 scripts/diaporamas/paroles.py revolution                  # calcule, contrôle, écrit
    python3 scripts/diaporamas/paroles.py revolution --ecoute         # + écoute ciblée par Gemini
    python3 scripts/diaporamas/paroles.py revolution --chant chant-marseillaise --essai   # n'écrit rien

Pour chaque intermède chanté (`musique.intermedes`, sans `instrumental`) :
1. **Voix isolée** : séparation de sources (Hybrid Demucs de torchaudio,
   `HDEMUCS_HIGH_MUSDB_PLUS`, ~320 Mo téléchargés une fois ; rien à installer) appliquée au
   fichier joué par le lecteur (public/diaporamas/<slug>/musique/…m4a) : les instants sont donc
   ceux de l'extrait. Piste de voix en cache (.cache/diaporamas/<slug>/paroles/).
2. **Alignement forcé** (alignement.py, wav2vec2 français) :
   le texte entier est aligné sur tout l'extrait, sur la voix isolée et, pour contrôle, sur le
   mélange ; un vers rétif (relu sur la planche) est cherché dans une fenêtre saisie à la main
   (`calage_fenetres`).
3. **Contrôles** : mots dans l'ordre, durées plausibles (0,05 à 4 s), dans la fenêtre et dans
   l'extrait ; écart voix isolée / mélange relevé (au-delà de 0,35 s, le mot est signalé) ;
   avec `--ecoute`, Gemini transcrit chaque vers découpé selon le calage (il doit entendre le vers
   entier, rien du suivant) et la première moitié de chaque vers (il ne doit pas entendre la
   seconde) ; ses écarts sont signalés pour relecture (sur des découpes de 1 à 2 s, il lui arrive
   d'inventer), pas bloquants.
4. **Écriture** : `paroles` = [[début du vers, vers, [[début, fin], …]], …] (un couple par mot de
   `commun.mots_lus(vers)`) et `calage: "mot"`. Un chant dont le calage échoue aux contrôles
   reçoit le repli : `calage: "vers"`, paroles [[début, vers]] (le lecteur montre alors le vers
   entier en fondu à son début). Planche de contrôle (spectrogramme de la voix et mots) :
   .cache/diaporamas/<slug>/paroles/<id>.png.

Corrections à la main, après relecture des planches : `calage_fenetres` (une fenêtre [t0, t1] par
vers, en s dans l'extrait, ou `null` pour garder l'alignement d'ensemble) et `calage_retouches`
([[vers, mot, début], …], rangs à partir de 1 : début d'un mot corrigé) dans l'intermède ; `calage_force: "vers"` impose le repli.
"""
import argparse, base64, hashlib, json, re, subprocess, sys, unicodedata
from pathlib import Path

import commun as c

ECART_SIGNALE = 0.35     # s : écart voix isolée / mélange au-delà duquel un mot est signalé
DUREE_MOT = (0.05, 4.0)  # s : durée plausible d'un mot chanté (note tenue comprise)


# --- Voix isolée ---------------------------------------------------------------------------------

def separer(fichier: Path, dest: Path) -> Path:
    """Piste de la voix (wav 44,1 kHz stéréo), en cache selon l'empreinte du fichier joué."""
    cle = hashlib.sha256(fichier.read_bytes()).hexdigest()[:16]
    marque = dest.with_suffix('.cle')
    if dest.exists() and marque.exists() and marque.read_text() == cle:
        return dest
    import numpy as np, soundfile as sf, torch
    from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS as B
    modele = B.get_model().eval()
    taux = B.sample_rate
    brut = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(fichier), '-ac', '2', '-ar', str(taux),
                           '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = torch.from_numpy(np.frombuffer(brut, dtype=np.float32).copy()).view(-1, 2).T.unsqueeze(0)
    ref = x.mean(0)
    mu, sd = ref.mean(), ref.std()
    with torch.inference_mode():
        y = modele((x - mu) / sd) * sd + mu
    voix = y[0, list(modele.sources).index('vocals')]
    dest.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(dest), voix.T.numpy(), taux)
    marque.write_text(cle)
    return dest


# --- Calage --------------------------------------------------------------------------------------

def fenetres(p: dict) -> list[list[float]] | None:
    """Fenêtre de recherche de chaque vers, saisie à la main (`calage_fenetres`) ; sans elle, le
    chant entier est aligné d'un seul tenant."""
    return p.get('calage_fenetres')


def caler(audio: Path, vers: list[str], fen: list[list[float]] | None) -> list[list[list[float]]]:
    """Mots horodatés de chaque vers : le texte entier sur tout l'extrait, ou vers par vers
    dans les fenêtres données (les vers sans fenêtre, `null`, suivent le texte entier)."""
    import alignement
    tout = alignement.aligner(audio, ' '.join(vers))
    sortie, k = [], 0
    for j, v in enumerate(vers):
        n = len(c.mots_lus(v))
        f = fen[j] if fen else None
        sortie.append(alignement.aligner(audio, v, None, f[0], f[1]) if f else tout[k:k + n])
        k += n
    return sortie


def retoucher(cal: list, retouches: list) -> None:
    """Corrections relues à la main : `calage_retouches` = [[vers, mot, début], …] (rangs à
    partir de 1) ; le mot précédent s'arrête au plus tard au nouveau début."""
    for v, m, d in retouches or []:
        mots = cal[v - 1]
        mots[m - 1][0] = d
        if mots[m - 1][1] <= d:
            suivant = mots[m][0] if m < len(mots) else (cal[v][0][0] if v < len(cal) else d + 0.4)
            mots[m - 1][1] = round(min(suivant, d + 0.4), 2)
        prec = mots[m - 2] if m > 1 else (cal[v - 2][-1] if v > 1 else None)
        if prec and prec[1] > d:
            prec[1] = d


def controler(vers: list[str], cal: list, controle: list, fen: list, duree: float) -> tuple[list[str], list[str]]:
    """(erreurs, signalements) du calage d'un chant."""
    err, sig = [], []
    prec = -1.0
    for k, (v, mots, mm, f) in enumerate(zip(vers, cal, controle, fen or [None] * len(vers))):
        noms = [m for _, _, m in c.mots_lus(v)]
        if len(mots) != len(noms):
            err.append(f'vers {k + 1} : {len(mots)} instants pour {len(noms)} mots')
            continue
        for nom, (d, fi), (dm, _) in zip(noms, mots, mm):
            if d <= prec:
                err.append(f'vers {k + 1}, « {nom} » : instant {d} pas après le mot précédent ({prec})')
            if not (DUREE_MOT[0] <= fi - d <= DUREE_MOT[1]) and not (fi - d < DUREE_MOT[0] and len(nom.strip(",;:!?.'’")) <= 2):
                (err if fi - d > DUREE_MOT[1] else sig).append(f'vers {k + 1}, « {nom} » : durée {fi - d:.2f} s')
            if not ((not f or f[0] <= d and fi <= f[1]) and 0 <= d and fi <= duree):
                err.append(f'vers {k + 1}, « {nom} » : hors de la fenêtre {f} ou de l\'extrait')
            if abs(d - dm) > ECART_SIGNALE:
                sig.append(f'vers {k + 1}, « {nom} » : voix isolée {d:.2f} s, mélange {dm:.2f} s')
            prec = d
    return err, sig


# --- Écoute ciblée (Gemini) ---------------------------------------------------------------------

def _norm(s: str) -> list[str]:
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.findall(r"[a-z]+", s.replace("'", ' ').replace('’', ' '))


def ecouter(fichier: Path, t0: float, t1: float) -> str:
    import voix
    wav = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t0:.2f}', '-to', f'{t1:.2f}', '-i', str(fichier),
                          '-ac', '1', '-ar', '16000', '-f', 'wav', '-'], capture_output=True, check=True).stdout
    r = voix._appel(voix.MODELE_TRANSCRIPTION, {'contents': [{'parts': [
        {'text': 'This is a short cut from a French song recording (1930s). Transcribe exactly the '
                 'French words that are sung in it, in order, including a word that is only partly '
                 'heard at the very start or end. Output only the words, nothing else; if no word is '
                 'sung, output an empty line.'},
        {'inlineData': {'mimeType': 'audio/wav', 'data': base64.b64encode(wav).decode()}}]}],
        'generationConfig': {'temperature': 0}})
    try:
        return r['candidates'][0]['content']['parts'][0]['text'].strip()
    except (KeyError, IndexError):
        return ''


def ecoute(fichier: Path, vers: list[str], cal: list, duree: float) -> list[str]:
    """Écarts relevés par Gemini : vers découpé entier, puis sa première moitié seule."""
    pb = []
    for k, (v, mots) in enumerate(zip(vers, cal)):
        attendu = _norm(v)
        fin = cal[k + 1][0][0] - 0.05 if k + 1 < len(cal) else duree
        entendu = _norm(ecouter(fichier, max(0, mots[0][0] - 0.15), min(fin, mots[-1][1] + 0.4)))
        manque = [w for w in attendu if w not in entendu]
        suivant = _norm(vers[k + 1]) if k + 1 < len(vers) else []
        en_trop = [w for w in entendu if w not in attendu and w in suivant]
        if len(manque) > max(1, len(attendu) // 4) or en_trop:
            pb.append(f'vers {k + 1} : entendu « {" ".join(entendu)} » (manque {manque}, déborde sur le suivant {en_trop})')
        noms = c.mots_lus(v)
        if len(noms) >= 4:
            j = len(noms) // 2
            moitie = _norm(ecouter(fichier, max(0, mots[0][0] - 0.15), mots[j][0] + 0.02))
            seconde = [w for w in _norm(' '.join(m for _, _, m in noms[j + 1:])) if w not in _norm(' '.join(m for _, _, m in noms[:j + 1]))]
            debordent = [w for w in seconde if w in moitie]
            if debordent:
                pb.append(f'vers {k + 1} : la première moitié (jusqu\'à « {noms[j][2]} ») fait déjà entendre {debordent}')
    return pb


# --- Planche de contrôle ----------------------------------------------------------------------

def planche(voix_wav: Path, vers: list[str], cal: list, controle: list, dest: Path) -> None:
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt, numpy as np, soundfile as sf
    except ImportError:
        return
    x, r = sf.read(str(voix_wav))
    x = x.mean(1) if x.ndim > 1 else x
    # Une rangée par tranche de 8 s : chaque mot lisible sur le spectrogramme de la voix.
    duree = len(x) / r
    rangs = int(np.ceil(duree / 8))
    fig, axes = plt.subplots(rangs, 1, figsize=(20, 3.4 * rangs), squeeze=False)
    for j, ax in enumerate(axes[:, 0]):
        t0 = 8 * j
        bout = x[int(t0 * r):int(min(duree, t0 + 8) * r)]
        ax.specgram(bout, NFFT=2048, Fs=r, noverlap=1792, cmap='gray_r', vmin=-120, xextent=(t0, t0 + len(bout) / r))
        ax.set_xlim(t0, t0 + 8)
        ax.set_ylim(0, 2500)
        ax.set_xticks(np.arange(t0, t0 + 8.01, 0.25))
        ax.tick_params(axis='x', labelsize=7)
        ax.grid(axis='x', alpha=0.3)
        for v, mots, mm in zip(vers, cal, controle):
            for (_, _, nom), (d, f), (dm, _) in zip(c.mots_lus(v), mots, mm):
                if not (t0 - 8 < d < t0 + 8):
                    continue
                ax.axvspan(d, f, color='k', alpha=0.07)
                ax.axvline(d, color='k', lw=1.2)
                ax.axvline(dm, color='k', lw=0.8, ls=':')
                if t0 <= d < t0 + 8:
                    ax.text(d + 0.02, 2450, nom, fontsize=11, va='top', backgroundcolor='w')
    fig.tight_layout()
    fig.savefig(str(dest), dpi=70)
    plt.close(fig)


# --- Traitement d'une période ---------------------------------------------------------------

def traiter(slug: str, seulement: list[str] | None, avec_ecoute: bool, essai: bool) -> int:
    c.charger_env()
    f, d = c.lire(slug)
    dossier = c.PUBLIC / d['slug']
    cache = c.CACHE / d['slug'] / 'paroles'
    replis = 0
    for p in (d.get('musique') or {}).get('intermedes', []):
        if p.get('instrumental') or not p.get('paroles') or (seulement and p['id'] not in seulement):
            continue
        fichier = dossier / p['fichier']
        vers = [x[1] for x in p['paroles']]
        fen = fenetres(p)
        voix_wav = separer(fichier, cache / f"{p['id']}-voix.wav")
        cal = caler(voix_wav, vers, fen)
        retoucher(cal, p.get('calage_retouches'))
        controle = caler(fichier, vers, fen)
        err, sig = controler(vers, cal, controle, fen, p['duree'])
        if avec_ecoute and not err:
            # Écoute bruitée sur des découpes courtes : signalée pour relecture, pas bloquante.
            sig += [f'écoute : {x}' for x in ecoute(fichier, vers, cal, p['duree'])]
        planche(voix_wav, vers, cal, controle, cache / f"{p['id']}.png")
        repli = bool(err) or p.get('calage_force') == 'vers'
        ecarts = sorted(abs(a[0] - b[0]) for x, y in zip(cal, controle) for a, b in zip(x, y))
        med = ecarts[len(ecarts) // 2] if ecarts else 0
        print(f"{p['id']} : {'REPLI (vers entiers)' if repli else 'calé au mot'} — {sum(len(x) for x in cal)} mots, "
              f"écart voix isolée / mélange médian {med:.2f} s, max {ecarts[-1] if ecarts else 0:.2f} s")
        for e in err:
            print('  ERREUR', e)
        for s in sig:
            print('  à revoir', s)
        for v, mots in zip(vers, cal):
            print('   ', ' '.join(f'{m}@{a[0]:.2f}' for (_, _, m), a in zip(c.mots_lus(v), mots)))
        if repli:
            replis += 1
            # Repli : début de vers d'après le calage s'il est sûr, sinon le début connu.
            p['paroles'] = [[x[0], x[1]] for x in p['paroles']]
            p['calage'] = 'vers'
        else:
            p['paroles'] = [[mots[0][0], v, mots] for v, mots in zip(vers, cal)]
            p['calage'] = 'mot'
    if not essai:
        c.ecrire(f, d)
    print(f'{replis} chant(s) en repli.' + (' (essai : rien écrit)' if essai else ''))
    return 0


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('slug')
    a.add_argument('--chant', nargs='+', help='identifiants des intermèdes à traiter')
    a.add_argument('--ecoute', action='store_true', help='écoute ciblée de chaque vers par Gemini')
    a.add_argument('--essai', action='store_true', help="n'écrit rien dans le script")
    x = a.parse_args()
    return traiter(x.slug, x.chant, x.ecoute, x.essai)


if __name__ == '__main__':
    sys.exit(main())
