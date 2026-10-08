"""Minutage mot par mot des lectures d'époque : alignement forcé de l'audio sur le texte (spec 12,
révision « journal télévisé » du 2026-10-07).

Méthode : le modèle d'alignement français de whisperx (wav2vec2 VoxPopuli, entraîné sur le
français : `torchaudio.pipelines.VOXPOPULI_ASR_BASE_10K_FR`, ~360 Mo, téléchargé une fois dans
~/.cache/torch/hub/checkpoints) donne, image par image (20 ms), la probabilité de chaque lettre ;
l'alignement forcé CTC (`torchaudio.functional.forced_align`, Viterbi) place ensuite le texte
connu, lettre par lettre, sur ces probabilités. Un mot va de sa première à sa dernière lettre.
C'est le cœur de `whisperx.align`, appelé directement : on évite ainsi la pile transformers de
whisperx, qui ne se charge pas dans l'environnement Anaconda de la machine (paquets compilés pour
numpy 1.x face à numpy 2), et l'on n'installe rien.

Le texte aligné est le texte **dit** : chaque mot affiché passe par le lexique de prononciation
(prononciation.yaml, entrées d'un mot), puis en minuscules ; les lettres absentes de l'alphabet
du modèle sont translittérées (sans accent) ou ignorées ; un mot sans lettre utilisable (rare :
chiffres) reçoit un instant interpolé entre ses voisins.

Python : torch et torchaudio (≥ 2.1) sont requis. `python3` (Anaconda) les a ; sinon, un
environnement séparé : python3 -m venv .cache/venv-alignement && .cache/venv-alignement/bin/pip
install torch torchaudio, puis DIAPORAMAS_PYTHON_ALIGNEMENT=.cache/venv-alignement/bin/python3.
"""
import os, subprocess, sys, unicodedata
from pathlib import Path

import commun as c

TAUX = 16_000
_modele = None


def disponible() -> tuple[bool, str]:
    try:
        import torch, torchaudio  # noqa: F401
        from torchaudio.functional import forced_align  # noqa: F401
        return True, f'torch {torch.__version__}, torchaudio {torchaudio.__version__}'
    except Exception as e:  # noqa: BLE001
        return False, f'{type(e).__name__} : {e}'


def _charger():
    global _modele
    if _modele is None:
        import torch, torchaudio
        torch.set_num_threads(max(1, (os.cpu_count() or 4) // 2))
        b = torchaudio.pipelines.VOXPOPULI_ASR_BASE_10K_FR
        modele = b.get_model().eval()
        etiquettes = b.get_labels()
        _modele = (modele, {ch: k for k, ch in enumerate(etiquettes)}, b.sample_rate)
    return _modele


def _audio(fichier: Path):
    """Échantillons float32 mono 16 kHz (ffmpeg), en tenseur (1, n)."""
    import numpy as np, torch
    brut = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(fichier), '-ac', '1', '-ar', str(TAUX),
                           '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return torch.from_numpy(np.frombuffer(brut, dtype=np.float32).copy()).unsqueeze(0)


def _lettres(mot: str, dico: dict[str, int]) -> list[int]:
    """Indices des lettres d'un mot dans l'alphabet du modèle (« | » entre les parties d'un mot
    composé : Saint-Just, est-ce)."""
    sortie: list[int] = []
    for ch in mot.lower():
        if ch in dico and ch not in '-|':
            sortie.append(dico[ch])
        elif ch in '-–' and sortie and sortie[-1] != dico['|']:
            sortie.append(dico['|'])
        else:
            base = unicodedata.normalize('NFKD', ch)[0]
            if base in dico and base not in '-|':
                sortie.append(dico[base])
    while sortie and sortie[-1] == dico['|']:
        sortie.pop()
    return sortie


def aligner(fichier: Path, texte: str, lexique: dict[str, str] | None = None,
            debut: float = 0.0, fin: float | None = None) -> list[list[float]]:
    """[[début, fin], …] (s) de chaque mot de `commun.mots_lus(texte)` dans l'audio. `debut` et
    `fin` : le texte est cherché dans cette fenêtre seulement (instants rendus dans tout l'audio ;
    paroles des chants, alignées vers par vers, spec 12, « Paroles des chants façon clip »)."""
    import torch
    from torchaudio.functional import forced_align, merge_tokens
    modele, dico, taux = _charger()
    mots = c.mots_lus(texte)
    lexique = lexique or {}
    lettres = [_lettres(c.appliquer_lexique(m, lexique), dico) for _, _, m in mots]
    cibles: list[int] = []
    proprietaire: list[int] = []  # mot de chaque lettre de la cible (-1 : séparateur)
    for k, ls in enumerate(lettres):
        if not ls:
            continue
        if cibles:
            cibles.append(dico['|'])
            proprietaire.append(-1)
        cibles += ls
        proprietaire += [k] * len(ls)
    son = _audio(fichier)
    if debut or fin is not None:
        son = son[:, int(debut * TAUX):None if fin is None else int(fin * TAUX)]
    with torch.inference_mode():
        emission, _ = modele(son)
        emission = torch.log_softmax(emission, dim=-1)
    pas = son.shape[1] / emission.shape[1] / taux  # secondes par image
    alignes, scores = forced_align(emission, torch.tensor([cibles], dtype=torch.int32), blank=0)
    jetons = merge_tokens(alignes[0], scores[0].exp())
    assert len(jetons) == len(cibles), (len(jetons), len(cibles))
    bornes: list[list[float] | None] = [None] * len(mots)
    for j, k in zip(jetons, proprietaire):
        if k < 0:
            continue
        d, f = j.start * pas, j.end * pas
        if bornes[k] is None:
            bornes[k] = [d, f]
        else:
            bornes[k][1] = f
    # Mots sans lettre utilisable : instant interpolé entre les voisins.
    duree = son.shape[1] / TAUX
    for k, b in enumerate(bornes):
        if b is None:
            avant = next((bornes[j][1] for j in range(k - 1, -1, -1) if bornes[j]), 0.0)
            apres = next((bornes[j][0] for j in range(k + 1, len(bornes)) if bornes[j]), duree)
            bornes[k] = [avant, max(avant, apres)]
    return [[round(debut + d, 2), round(debut + f, 2)] for d, f in bornes]


def prorata(texte: str, phrases: list[list[float]], duree: float) -> list[list[float]]:
    """Repli : chaque mot situé au prorata des caractères dans sa phrase horodatée (même calcul
    que le lecteur quand `audio.mots` manque)."""
    debuts = [0]
    for p in c.phrases(texte)[:-1]:
        debuts.append(texte.index(p, debuts[-1]) + len(p))
    if not phrases or len(phrases) != len(debuts):
        phrases, debuts = [[0.0, duree]], [0]
    fins = debuts[1:] + [len(texte)]
    sortie = []
    for d, f, _ in c.mots_lus(texte):
        j = max(k for k, x in enumerate(debuts) if x <= d)
        t0, t1 = phrases[j]
        lg = max(1, fins[j] - debuts[j])
        sortie.append([round(t0 + (d - debuts[j]) / lg * (t1 - t0), 2), round(t0 + (f - debuts[j]) / lg * (t1 - t0), 2)])
    return sortie


if __name__ == '__main__':
    ok, info = disponible()
    print('alignement :', 'disponible' if ok else 'indisponible', '—', info)
    sys.exit(0 if ok else 1)
