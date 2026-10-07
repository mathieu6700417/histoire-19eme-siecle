"""Voix off d'une période : synthèse Gemini, contrôle de fidélité, encodage m4a (spec 12).

Usage :
    python3 scripts/diaporamas/voix.py revolution             # ce qui manque ou a changé
    python3 scripts/diaporamas/voix.py revolution --n 12      # une diapositive (refaite)
    python3 scripts/diaporamas/voix.py revolution --force     # tout refaire
    python3 scripts/diaporamas/voix.py revolution --paralleles 4
    python3 scripts/diaporamas/voix.py revolution --horodater  # phrases seulement, sans synthèse
    python3 scripts/diaporamas/voix.py revolution --mots       # mots des lectures, sans synthèse

Pour chaque diapositive : applique le lexique (prononciation.yaml) au texte envoyé à la
voix, synthétise avec Gemini TTS (voix Charon), retranscrit l'audio et compare la
transcription mot à mot au texte envoyé ; sous 0,9, on recommence (trois essais), puis on
signale l'échec. L'audio est encodé en AAC mono 64 kb/s (ffmpeg) dans
public/diaporamas/<slug>/NNN.m4a, et sa durée écrite dans `audio.duree`.

Chaque phrase de l'audio est horodatée (`audio.phrases` : [[début, fin], …], en secondes) :
ffmpeg `silencedetect` repère les pauses, et l'on retient une pause par fin de phrase, dans
l'ordre, en favorisant les pauses longues proches de la position estimée au prorata des
caractères (repris de alignement.py du projet « Histoire zoomable »). Sans pause utilisable,
la fin de phrase garde l'estimation au prorata. La caméra du lecteur s'en sert (spec 12).
`--horodater` refait ces horodatages à partir des m4a existants, sans resynthétiser.

Lectures d'époque : chaque mot est en outre minuté (`audio.mots` : [[début, fin], …], un
couple par mot de `commun.mots_lus`) par alignement forcé de l'audio sur le texte (wav2vec2
français, voir alignement.py) ; le lecteur révèle le texte mot par mot au rythme de la voix.
Fait après chaque synthèse de lecture si torch/torchaudio sont là ; `--mots` le (re)fait sur
les audios existants. Sans alignement possible, `audio.mots` reste absent et le lecteur situe
les mots au prorata des caractères dans leur phrase horodatée.

Ne refait que ce qui manque ou dont le texte envoyé a changé (empreinte dans
.cache/diaporamas/<slug>/voix.json). Clé : GEMINI_API_KEY dans .env.

Piège connu (projet « Histoire zoomable », 28/09/2026) : Gemini TTS lit à voix haute
TOUTE consigne jointe au texte (ton, langue, notes), en français comme en anglais. On ne
lui envoie donc que le texte à lire ; la langue passe par `languageCode`. La transcription
de contrôle n'impose aucune langue, pour qu'une consigne lue en anglais soit détectée.
"""
import argparse, base64, difflib, hashlib, io, json, os, re, subprocess, sys, threading, time
import unicodedata, urllib.error, urllib.request, wave
from concurrent.futures import ThreadPoolExecutor, as_completed

import commun as c

MODELE_VOIX = os.environ.get('DIAPORAMAS_MODELE_VOIX') or 'gemini-3.8-flash-tts'
MODELE_TRANSCRIPTION = os.environ.get('DIAPORAMAS_MODELE_TRANSCRIPTION') or 'gemini-3.8-flash'
VOIX = 'Charon'
# Voix de lecture (lectures d'époque) : une seule voix de femme pour tous les textes, quel que
# soit l'auteur, nettement distincte du narrateur (décision de l'utilisateur du 2026-10-07).
# Le champ `auteur.voix` des lectures reste renseigné mais n'est plus utilisé.
VOIX_LECTURE = os.environ.get('DIAPORAMAS_VOIX_LECTURE') or 'Aoede'
URL = 'https://generativelanguage.googleapis.com/v1beta/models'
TAUX = 24_000
SEUIL_FIDELITE = 0.9
ESSAIS = 3

verrou = threading.Lock()
usage = {'appels_voix': 0, 'appels_transcription': 0, 'jetons': 0, 'secondes': 0.0}


class ErreurGemini(Exception):
    pass


def _appel(modele: str, corps: dict) -> dict:
    cle = os.environ.get('GEMINI_API_KEY', '')
    if not cle:
        raise ErreurGemini('GEMINI_API_KEY absente de .env')
    for essai in range(6):
        req = urllib.request.Request(
            f'{URL}/{modele}:generateContent', data=json.dumps(corps).encode(),
            headers={'x-goog-api-key': cle, 'Content-Type': 'application/json'})
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=300).read())
            with verrou:
                usage['jetons'] += int((d.get('usageMetadata') or {}).get('totalTokenCount') or 0)
            return d
        except urllib.error.HTTPError as e:
            corps_err = e.read().decode(errors='replace')[:400]
            if e.code in (429, 500, 502, 503, 504) and essai < 5:
                time.sleep(10 * (essai + 1))
                continue
            raise ErreurGemini(f'Gemini {e.code} : {corps_err}') from None
        except (urllib.error.URLError, TimeoutError) as e:
            if essai < 5:
                time.sleep(10 * (essai + 1))
                continue
            raise ErreurGemini(f'Gemini injoignable : {e}') from None
    raise ErreurGemini('Gemini : trop de tentatives')


def _pcm(donnees: bytes, mime: str) -> bytes:
    """PCM16 mono 24 kHz, que Gemini renvoie du WAV ou du PCM brut (audio/L16)."""
    if 'wav' not in mime:
        return donnees
    with wave.open(io.BytesIO(donnees)) as w:
        if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (TAUX, 1, 2):
            raise ErreurGemini(f'Format audio inattendu : {w.getparams()}')
        return w.readframes(w.getnframes())


def synthese(texte: str, voix: str = VOIX) -> bytes:
    """Le texte seul, sans aucune consigne (voir le docstring du module)."""
    r = _appel(MODELE_VOIX, {
        'contents': [{'parts': [{'text': texte}]}],
        'generationConfig': {
            'responseModalities': ['AUDIO'],
            'speechConfig': {'languageCode': 'fr-FR',
                             'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voix}}},
        },
    })
    with verrou:
        usage['appels_voix'] += 1
    try:
        partie = r['candidates'][0]['content']['parts'][0]['inlineData']
    except (KeyError, IndexError):
        raise ErreurGemini(f"pas d'audio dans la réponse ({str(r)[:300]})") from None
    return _pcm(base64.b64decode(partie['data']), partie.get('mimeType', ''))


def transcrire(pcm: bytes) -> str:
    tampon = io.BytesIO()
    with wave.open(tampon, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAUX)
        w.writeframes(pcm)
    r = _appel(MODELE_TRANSCRIPTION, {
        'contents': [{'parts': [
            # Pas de langue imposée : une consigne lue par erreur (souvent en anglais) doit
            # apparaître dans la transcription pour faire échouer le contrôle de fidélité.
            {'text': 'Transcribe everything that is spoken in this recording, verbatim, in '
                     'whatever language each part is spoken. Do not omit, translate or correct '
                     'anything. Write numbers, dates and Roman numerals out in words, exactly '
                     'as they are pronounced. Output only the transcript.'},
            {'inlineData': {'mimeType': 'audio/wav', 'data': base64.b64encode(tampon.getvalue()).decode()}},
        ]}],
        'generationConfig': {'temperature': 0},
    })
    with verrou:
        usage['appels_transcription'] += 1
    return ''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts']).strip()


# --- Contrôle de fidélité (repris de histoire/tts.py) ---------------------------------

NOMBRE = '#'
_MOTS_NOMBRES = set(
    'zero un une deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze seize '
    'vingt vingts trente quarante cinquante soixante cent cents mil mille'.split())
_ROMAIN = re.compile(r'\b[IVXLC]{2,}\b|\b[IVX]{1,4}(?=e\b|ᵉ)')


def _mots(texte: str) -> list[str]:
    """Mots comparables : sans accents ni casse, chaque nombre réduit à un seul jeton."""
    texte = _ROMAIN.sub(' 0 ', texte)
    texte = unicodedata.normalize('NFKD', texte.lower())
    texte = ''.join(ch for ch in texte if not unicodedata.combining(ch))
    mots: list[str] = []
    for m in re.findall(r'[a-z0-9]+', texte):
        nombre = m.isdigit() or m in _MOTS_NOMBRES
        if nombre and mots and mots[-1] == NOMBRE:
            continue
        if m == 'et' and mots and mots[-1] == NOMBRE:
            mots.append('et')
            continue
        if nombre and len(mots) >= 2 and mots[-1] == 'et' and mots[-2] == NOMBRE:
            mots.pop()
            continue
        mots.append(NOMBRE if nombre else m)
    return mots


def fidelite(attendu: str, obtenu: str) -> float:
    return difflib.SequenceMatcher(None, _mots(attendu), _mots(obtenu), autojunk=False).ratio()


def encoder_m4a(pcm: bytes, destination) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 's16le', '-ar', str(TAUX), '-ac', '1',
                    '-i', 'pipe:0', '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart',
                    str(destination)], input=pcm, check=True)


def rogner(pcm: bytes, seuil: int = 300, marge: float = 0.08) -> bytes:
    """Retire les silences de début et de fin (en gardant une petite marge)."""
    n = len(pcm) // 2
    echantillons = memoryview(pcm).cast('h')
    debut, fin = 0, n
    while debut < n and abs(echantillons[debut]) < seuil:
        debut += 1
    while fin > debut and abs(echantillons[fin - 1]) < seuil:
        fin -= 1
    m = int(marge * TAUX)
    return pcm[max(0, debut - m) * 2:min(n, fin + m) * 2]


# --- Horodatage des phrases (d'après alignement.py, « Histoire zoomable ») ---------------

PAUSE_MIN = 0.15        # durée minimale d'une pause entre phrases (s)
SEUIL_SILENCE = '-35dB'
PENALITE_ECART = 0.25   # score perdu par seconde d'écart à l'estimation au prorata


def pauses_audio(fichier) -> tuple[list[tuple[float, float]], float]:
    """Pauses (début, fin) d'un audio, hors silences de tête et de fin, et durée totale."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(fichier), '-af',
                        f'silencedetect=noise={SEUIL_SILENCE}:d={PAUSE_MIN}', '-f', 'null', '-'],
                       capture_output=True, text=True)
    sortie = r.stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', sortie)
    duree = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0
    debuts = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', sortie)]
    fins = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', sortie)]
    paires = []
    for k, d in enumerate(debuts):
        f = fins[k] if k < len(fins) else duree
        if d > 0.05 and f < duree - 0.05:
            paires.append((d, f))
    return paires, duree


def _choisir(candidates: list[tuple[float, float]], estimees: list[float]) -> list[tuple[float, float] | None]:
    """Une pause par fin de phrase, dans l'ordre, maximisant durée − pénalité d'écart
    (programmation dynamique) ; None quand il n'y a pas assez de pauses."""
    n, m = len(estimees), len(candidates)
    if m < n:
        choix: list[tuple[float, float] | None] = [None] * n
        for cand in candidates:
            milieu = (cand[0] + cand[1]) / 2
            i = min(range(n), key=lambda k: abs(estimees[k] - milieu))
            if choix[i] is None:
                choix[i] = cand
        return choix

    def score(i: int, j: int) -> float:
        cand = candidates[j]
        return (cand[1] - cand[0]) - PENALITE_ECART * abs((cand[0] + cand[1]) / 2 - estimees[i])

    inf = float('-inf')
    meilleur = [[inf] * (m + 1) for _ in range(n + 1)]
    for j in range(m + 1):
        meilleur[0][j] = 0.0
    for i in range(1, n + 1):
        for j in range(i, m + 1):
            meilleur[i][j] = max(meilleur[i][j - 1], meilleur[i - 1][j - 1] + score(i - 1, j - 1))
    choix, j = [], m
    for i in range(n, 0, -1):
        while meilleur[i][j] == meilleur[i][j - 1]:
            j -= 1
        choix.append(candidates[j - 1])
        j -= 1
    return choix[::-1]


def horodater(fichier, narration: str, duree: float | None = None) -> list[list[float]]:
    """[[début, fin], …] pour chaque phrase de la narration (découpage de commun.phrases)."""
    morceaux = c.phrases(narration)
    candidates, duree_lue = pauses_audio(fichier)
    duree = duree or duree_lue
    total = sum(len(p) for p in morceaux) or 1
    estimees, cumul = [], 0
    for p in morceaux[:-1]:
        cumul += len(p)
        estimees.append(cumul / total * duree)
    bornes = [b if b else (e, e) for b, e in zip(_choisir(candidates, estimees), estimees)]
    debuts = [0.0] + [b[1] for b in bornes]
    fins = [b[0] for b in bornes] + [duree]
    return [[round(d, 2), round(f, 2)] for d, f in zip(debuts, fins)]


def empreinte(texte: str, voix: str = VOIX) -> str:
    # Voix du narrateur : même empreinte qu'avant l'ajout des voix de lecture (rien à refaire).
    return hashlib.sha1(f'{MODELE_VOIX}|{voix}|{texte}'.encode()).hexdigest()[:16]


def pistes(d: dict, lexique: dict) -> list[dict]:
    """Tout ce qui se synthétise dans une période : diapositives (clé « 12 »), lectures
    (« lecture:<id> », voix de lecture) et épisodes (« episode:<id> », voix du narrateur).
    `texte` : le texte affiché (horodatage des phrases) ; `a_lire` : le texte envoyé à la voix."""
    sortie = []
    for x in d['diapositives']:
        sortie.append({'cle': str(x['n']), 'obj': x, 'texte': x['narration'], 'voix': VOIX,
                       'defaut': c.nom(x['n'], 'm4a'), 'nom': f"{x['n']:3d}"})
    for l in d.get('lectures', []):
        sortie.append({'cle': f"lecture:{l['id']}", 'obj': l, 'texte': c.texte_lu(l),
                       'voix': VOIX_LECTURE, 'defaut': f"lectures/{l['id']}.m4a",
                       'nom': f"lecture {l['id']}"})
    for e in d.get('episodes', []):
        sortie.append({'cle': f"episode:{e['id']}", 'obj': e, 'texte': e['narration'], 'voix': VOIX,
                       'defaut': f"episodes/{e['id']}.m4a", 'nom': f"épisode {e['id']}"})
    for q in sortie:
        q['a_lire'] = c.appliquer_lexique(q['texte'], lexique)
        q['empreinte'] = empreinte(q['a_lire'], q['voix'])
    return sortie


def traiter(q: dict, dossier) -> dict:
    meilleure = None
    for essai in range(1, ESSAIS + 1):
        pcm = rogner(synthese(q['a_lire'], q['voix']))
        transcription = transcrire(pcm)
        score = fidelite(q['a_lire'], transcription)
        if meilleure is None or score > meilleure[0]:
            meilleure = (score, pcm, transcription, essai)
        if score >= SEUIL_FIDELITE:
            break
    score, pcm, transcription, essai = meilleure
    duree = len(pcm) / 2 / TAUX
    if score < SEUIL_FIDELITE:
        return {'ok': False, 'score': score, 'transcription': transcription, 'essais': ESSAIS}
    fichier = (q['obj'].get('audio') or {}).get('fichier') or q['defaut']
    encoder_m4a(pcm, dossier / fichier)
    with verrou:
        usage['secondes'] += duree
    return {'ok': True, 'score': score, 'transcription': transcription, 'essais': essai,
            'fichier': fichier, 'duree': round(duree, 2),
            'phrases': horodater(dossier / fichier, q['texte'], round(duree, 2))}


def horodater_tout(f, d: dict, dossier, seulement) -> int:
    """Horodate les phrases des audios déjà produits (sans appel à Gemini)."""
    replis = []
    for q in pistes(d, {}):
        a = q['obj'].get('audio') or {}
        if seulement and q['cle'] not in seulement:
            continue
        if not a.get('fichier') or not (dossier / a['fichier']).is_file():
            print(f"{q['nom']} : audio absent, ignoré")
            continue
        candidates, _ = pauses_audio(dossier / a['fichier'])
        a['phrases'] = horodater(dossier / a['fichier'], q['texte'], a.get('duree'))
        if len(candidates) < len(a['phrases']) - 1:
            replis.append(q['cle'])
    c.ecrire(f, d)
    print(f"Phrases horodatées. Repli au prorata (pauses insuffisantes) : {replis or 'aucun'}.")
    return 0


def minuter_mots(q: dict, dossier, lexique: dict) -> str:
    """Minutage mot par mot d'une lecture (alignement forcé) ; renvoie un bilan d'une ligne."""
    import alignement
    a = q['obj']['audio']
    mots = alignement.aligner(dossier / a['fichier'], q['texte'], lexique)
    a['mots'] = mots
    # Écart aux phrases horodatées (pauses) : contrôle grossier de l'alignement.
    ecarts = []
    debuts = [0]
    for p in c.phrases(q['texte'])[:-1]:
        debuts.append(q['texte'].index(p, debuts[-1]) + len(p))
    lus = c.mots_lus(q['texte'])
    if len(a.get('phrases') or []) == len(debuts):
        for (t0, _), dch in zip(a['phrases'][1:], debuts[1:]):
            k = next(i for i, (d, _, _) in enumerate(lus) if d >= dch)
            ecarts.append(abs(mots[k][0] - t0))
    bilan = f'{len(mots)} mots'
    if ecarts:
        bilan += f', début de phrase à {max(ecarts):.2f} s au plus des pauses'
    return bilan


def minuter_tout(f, d: dict, dossier, seulement) -> int:
    """Minutage mot par mot des lectures dont l'audio existe (sans appel à Gemini)."""
    import alignement
    ok, info = alignement.disponible()
    if not ok:
        print(f'Alignement indisponible ({info}) : voir alignement.py (venv dans .cache/).')
        return 1
    lexique = c.charger_lexique()
    for q in pistes(d, lexique):
        if not q['cle'].startswith('lecture:') or (seulement and q['cle'] not in seulement):
            continue
        a = q['obj'].get('audio') or {}
        if not a.get('fichier') or not (dossier / a['fichier']).is_file():
            print(f"{q['nom']} : audio absent, ignoré")
            continue
        print(f"{q['nom']} : {minuter_mots(q, dossier, lexique)}")
    c.ecrire(f, d)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug')
    p.add_argument('--n', type=int, nargs='+', help='diapositive(s) à (re)faire')
    p.add_argument('--segments', nargs='+', metavar='CLE',
                   help='lecture(s) ou épisode(s) à (re)faire : lecture:<id>, episode:<id>')
    p.add_argument('--force', action='store_true')
    p.add_argument('--paralleles', type=int, default=4)
    p.add_argument('--horodater', action='store_true',
                   help="horodate les phrases des audios existants, sans synthèse")
    p.add_argument('--mots', action='store_true',
                   help="minute les mots des lectures existantes (alignement forcé), sans synthèse")
    a = p.parse_args()
    c.charger_env()

    f, d = c.lire(a.slug)
    dossier = c.PUBLIC / d['slug']
    choisis = None
    if a.n is not None or a.segments:
        choisis = {str(n) for n in (a.n or [])} | set(a.segments or [])
    if a.horodater:
        return horodater_tout(f, d, dossier, choisis)
    if a.mots:
        return minuter_tout(f, d, dossier, choisis)
    lexique = c.charger_lexique()
    etat_f = c.CACHE / d['slug'] / 'voix.json'
    etat = json.loads(etat_f.read_text()) if etat_f.exists() else {}

    toutes = pistes(d, lexique)
    inconnues = (choisis or set()) - {q['cle'] for q in toutes}
    if inconnues:
        p.error(f"inconnu(s) : {', '.join(sorted(inconnues))}")
    a_faire = []
    for q in toutes:
        fichier = dossier / ((q['obj'].get('audio') or {}).get('fichier') or q['defaut'])
        if choisis is not None:
            if q['cle'] in choisis:
                a_faire.append(q)
        elif a.force or etat.get(q['cle'], {}).get('empreinte') != q['empreinte'] or not fichier.exists():
            a_faire.append(q)
    print(f"{len(a_faire)} piste(s) à synthétiser ({MODELE_VOIX} ; narrateur {VOIX}, lecture "
          f"{VOIX_LECTURE}).")

    echecs = []
    debut = time.time()
    with ThreadPoolExecutor(max_workers=a.paralleles) as pool:
        futurs = {pool.submit(traiter, q, dossier): q for q in a_faire}
        for fut in as_completed(futurs):
            q = futurs[fut]
            try:
                r = fut.result()
            except Exception as e:  # noqa: BLE001
                echecs.append(f"{q['nom']} : erreur : {e}")
                print(f"{q['nom']} ERREUR {e}")
                continue
            if not r['ok']:
                echecs.append(f"{q['nom']} : lecture infidèle ({r['score']:.2f}) : « {r['transcription'][:160]} »")
                print(f"{q['nom']} INFIDÈLE {r['score']:.2f}")
                continue
            q['obj']['audio'] = {'fichier': r['fichier'], 'duree': r['duree'], 'phrases': r['phrases']}
            if q['cle'].startswith('lecture:'):
                with verrou:
                    try:
                        print(f"{q['nom']} : mots minutés ({minuter_mots(q, dossier, lexique)})")
                    except Exception as e:  # noqa: BLE001  (torch absent…) : repli au prorata
                        print(f"{q['nom']} : mots non minutés ({type(e).__name__}), repli au prorata ; voir --mots")
            etat[q['cle']] = {'empreinte': q['empreinte'], 'voix': q['voix'], 'texte': q['a_lire'],
                              'transcription': r['transcription'], 'fidelite': round(r['score'], 3),
                              'essais': r['essais'], 'duree': r['duree']}
            print(f"{q['nom']} {r['duree']:5.1f} s · fidélité {r['score']:.2f} · essai {r['essais']}")
            # Sauvegarde au fil de l'eau : une interruption ne perd rien.
            with verrou:
                c.ecrire(f, d)
                etat_f.parent.mkdir(parents=True, exist_ok=True)
                etat_f.write_text(json.dumps(etat, ensure_ascii=False, indent=1))

    c.ecrire(f, d)
    total = sum((q['obj'].get('audio') or {}).get('duree', 0) for q in toutes)
    # Tarif indicatif Gemini 3.8 Flash TTS : ~0,027 $ par minute d'audio produite
    # (transcriptions en sus, négligeables). Le nombre d'appels inclut les essais refaits.
    cout = usage['secondes'] / 60 * 0.027 * (usage['appels_voix'] / max(1, len(a_faire) - len(echecs)))
    print(f"\nAppels : {usage['appels_voix']} synthèses, {usage['appels_transcription']} transcriptions, "
          f"{usage['jetons']} jetons ; {usage['secondes'] / 60:.1f} min produites en {time.time() - debut:.0f} s "
          f"(coût indicatif ~{cout:.2f} $).")
    print(f'Voix de la période (diapositives, lectures, épisodes ; sans pauses ni cartons) : {total / 60:.1f} min.')
    if echecs:
        print(f'\n{len(echecs)} échec(s) :', *sorted(echecs), sep='\n  ')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
