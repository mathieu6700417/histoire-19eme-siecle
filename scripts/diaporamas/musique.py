"""Musique d'une période du « Siècle en images » : fond par acte et intermèdes chantés (spec 12,
section « Musique », révision du 2026-10-07).

Usage :
    python3 scripts/diaporamas/musique.py revolution              # ce qui manque ou a changé
    python3 scripts/diaporamas/musique.py revolution --force      # tout refaire
    python3 scripts/diaporamas/musique.py revolution --piste fond-crise-1
    python3 scripts/diaporamas/musique.py revolution --sources    # télécharge et contrôle seulement
    python3 scripts/diaporamas/musique.py --indicatif             # indicatif commun du générique

Indicatif (spec 12, « Générique d'ouverture et récapitulatif de fin ») : décrit dans
src/data/diaporamas/commun/indicatif.json. Depuis le 2026-10-09, thème original composé avec Lyria
(extraits préparés à part, rien à faire ici) ; pour un enregistrement (Commons, Internet Archive),
deux extraits préparés comme un chant (-16 LUFS, 128 kb/s) dans public/diaporamas/commun/.

Données : `musique` dans src/data/diaporamas/NN-<slug>.json (format dans le README) :
`fond` (pistes de fond, par acte, enchaînées en fondu par le lecteur) et `intermedes`
(chants réels joués au premier plan après une diapositive).

Uniquement de vrais enregistrements libres (décision du 2026-10-07 : pas de rendu MIDI).

Pour chaque piste :
1. **Source** téléchargée une fois dans .cache/diaporamas/musique/sources/ :
   - `commons` : fichier Wikimedia Commons (licence relevée par l'API, `extmetadata`) ;
   - `archive` : enregistrement de l'Internet Archive (78 tours) ; la date de publication
     déclarée (`source.publication`) doit être antérieure à 1963 (domaine public en Europe),
     et la licence de l'item ne doit être ni NC ni ND.
   NC et ND sont toujours refusés ; CC BY et BY-SA sont admis (crédit affiché par le lecteur).
2. **Découpe** [debut, fin], fondus (fond : 3 s ; chant : court), filtres 78 tours éventuels
   (`filtres: "78tours"` : coupe-bas, coupe-haut, débruitage léger ; `"microsillon"` : coupe-bas
   doux, craquements ôtés, souffle à peine réduit), **normalisation** de sonie
   (ffmpeg loudnorm : -20 LUFS pour le fond, que le lecteur baisse encore sous la voix ;
   -16 LUFS pour les chants), encodage AAC stéréo (96 kb/s fond, 128 kb/s chants) dans
   public/diaporamas/<slug>/musique/. La durée est écrite dans le JSON.

État (empreintes, licences relevées) : .cache/diaporamas/<slug>/musique.json.
Ne lance rien qui provienne des téléchargements : ils ne sont que lus (audio, métadonnées).
"""
import argparse, hashlib, json, re, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

import commun as c

MUSIQUE = c.CACHE / 'musique'
SOURCES = MUSIQUE / 'sources'
TAUX = 48_000

LUFS_FOND = -20
LUFS_CHANT = -16
FONDU_FOND = 3.0
UA_NAVIGATEUR = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) xixe-siecle-diaporamas/1.0'

# Licence d'une piste : NC et ND refusés ; domaine public, CC0, CC BY, CC BY-SA admis.
REFUS = re.compile(r'\bnc\b|non[- ]?commercial|\bnd\b|no[- ]?deriv|by-nc|by-nd', re.I)
ADMIS = re.compile(r'public domain|domaine public|^pd\b|pd-|cc0|cc-zero|publicdomain|'
                   r'cc[- ]by(-sa)?\b|creativecommons\.org/licenses/by(-sa)?/', re.I)


def licence_admise(texte: str) -> bool:
    return bool(texte) and not REFUS.search(texte) and bool(ADMIS.search(texte))


def empreinte(*parts) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def telecharger(url: str, dest: Path, ua: str = c.UA) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    for essai in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua})
            donnees = urllib.request.urlopen(req, timeout=300).read()
            break
        except Exception:
            if essai == 3:
                raise
            time.sleep(5 * (essai + 1))
    if donnees[:15].lower().startswith((b'<!doctype', b'<html')):
        raise SystemExit(f'{url} : page HTML reçue au lieu du fichier (contrôle anti-robot ?)')
    tmp = dest.with_suffix(dest.suffix + '.tmp')
    tmp.write_bytes(donnees)
    tmp.replace(dest)
    return dest


# --- Sources et licences -----------------------------------------------------------------

def nom_cache(s: str) -> str:
    n = re.sub(r'[^\w.-]+', '_', s)
    if len(n) <= 150:
        return n
    # Nom trop long : début lisible, empreinte (deux pistes d'un même disque ne se confondent
    # pas) et extension conservée.
    return f'{n[:120]}-{hashlib.sha256(n.encode()).hexdigest()[:10]}{Path(n).suffix[:6]}'


def source_commons(src: dict) -> tuple[Path, dict]:
    titre = src['fichier'] if src['fichier'].startswith('File:') else f"File:{src['fichier']}"
    d = c.api_commons(action='query', titles=titre, redirects=1, prop='imageinfo',
                      iiprop='url|size|mime|extmetadata', iiextmetadatalanguage='fr')
    pages = d.get('query', {}).get('pages', [])
    if not pages or 'imageinfo' not in pages[0]:
        raise SystemExit(f'Commons : {titre} introuvable')
    info = pages[0]['imageinfo'][0]
    meta = {k: v.get('value') for k, v in (info.get('extmetadata') or {}).items()}
    licence = c.texte_meta(meta.get('LicenseShortName')) or c.texte_meta(meta.get('License'))
    chemin = telecharger(info['url'], SOURCES / 'commons' / nom_cache(pages[0]['title'].removeprefix('File:')))
    return chemin, {'licence': licence, 'libre': licence_admise(licence),
                    'page': info.get('descriptionurl'), 'auteur': c.texte_meta(meta.get('Artist'))[:200]}


def source_archive(src: dict) -> tuple[Path, dict]:
    ident, fichier = src['id'], src['fichier']
    d = json.loads(c.http_get(f'https://archive.org/metadata/{urllib.parse.quote(ident)}'))
    m = d.get('metadata') or {}
    if not any(f.get('name') == fichier for f in d.get('files', [])):
        raise SystemExit(f'Internet Archive : {fichier} absent de {ident}')
    licence_item = m.get('licenseurl') or ''
    pub = src.get('publication')
    libre = bool(pub) and int(str(pub)[:4]) < 1963 and not REFUS.search(licence_item)
    url = f'https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(fichier)}'
    chemin = telecharger(url, SOURCES / 'archive' / nom_cache(f'{ident}--{fichier}'))
    lib = (f'Domaine public en Europe (enregistrement publié en {pub}, avant 1963)'
           + (f' ; item : {licence_item}' if licence_item else ''))
    return chemin, {'licence': lib, 'libre': libre, 'page': f'https://archive.org/details/{ident}',
                    'date_item': m.get('date') or m.get('year')}


def obtenir_source(src: dict) -> tuple[Path, dict]:
    t = src['type']
    if t == 'commons':
        return source_commons(src)
    if t == 'archive':
        return source_archive(src)
    if t == 'midi':
        raise SystemExit('source MIDI refusée : uniquement de vrais enregistrements (spec 12)')
    raise SystemExit(f'type de source inconnu : {t}')


# --- Découpe, fondus, sonie, encodage ----------------------------------------------------

def duree_audio(f: Path) -> float:
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def filtres_piste(p: dict, chant: bool, duree: float) -> str:
    f = []
    if p.get('mono'):
        # Pressage « stéréo » électronique d'un enregistrement mono : les deux canaux additionnés.
        f.append('pan=mono|c0=0.5*c0+0.5*c1')
    if p.get('filtres') == '78tours':
        # Coupe-bas (ronflement), coupe-haut (souffle), débruitage léger du crépitement.
        f += ['highpass=f=70', 'lowpass=f=8500', 'afftdn=nf=-30']
    elif p.get('filtres') == 'microsillon':
        # Premiers microsillons (années 1950) : coupe-bas doux, craquements ôtés (adeclick),
        # souffle à peine réduit (afftdn léger) ; pas de coupe-haut, pour ne pas ternir le son.
        f += ['highpass=f=35', 'adeclick=w=55:o=75:t=4', 'afftdn=nf=-45:nr=10:tn=1']
    entree = p.get('fondu_entree', 0.4 if chant else FONDU_FOND)
    sortie = p.get('fondu_sortie', 1.2 if chant else FONDU_FOND)
    if entree:
        f.append(f'afade=t=in:st=0:d={entree}')
    if sortie:
        f.append(f'afade=t=out:st={max(0, duree - sortie):.3f}:d={sortie}')
    cible = LUFS_CHANT if chant else LUFS_FOND
    f.append(f'loudnorm=I={cible}:TP=-1.5:LRA=11')
    f.append(f'aresample={TAUX}')
    return ','.join(f)


def preparer(audio: Path, p: dict, dest: Path, chant: bool) -> float:
    debut = float(p.get('debut', 0))
    fin = p.get('fin')
    total = duree_audio(audio)
    fin = min(float(fin), total) if fin else total
    duree = fin - debut
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.stem + '.tmp.m4a')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{debut:.3f}', '-t', f'{duree:.3f}',
                    '-i', str(audio), '-vn', '-af', filtres_piste(p, chant, duree), '-ac', '2',
                    '-c:a', 'aac', '-b:a', '128k' if chant else '96k', '-movflags', '+faststart',
                    str(tmp)], check=True)
    tmp.replace(dest)
    return round(duree_audio(dest), 2)


# --- Traitement d'une période --------------------------------------------------------------

def pistes(d: dict) -> list[tuple[str, dict, bool]]:
    m = d.get('musique') or {}
    return [(p['id'], p, False) for p in m.get('fond', [])] + [(p['id'], p, True) for p in m.get('intermedes', [])]


def traiter(slug: str, force: bool, seulement: list[str] | None, sources_seules: bool) -> int:
    f, d = c.lire(slug)
    m = d.get('musique')
    if not m:
        print('Pas de champ « musique » dans le script.')
        return 1
    m.pop('moteur', None)   # ancien champ du rendu MIDI, abandonné
    etat_f = c.CACHE / d['slug'] / 'musique.json'
    etat = json.loads(etat_f.read_text()) if etat_f.exists() else {}
    dossier = c.PUBLIC / d['slug']
    erreurs = 0
    for pid, p, chant in pistes(d):
        if seulement and pid not in seulement:
            continue
        src = p['source']
        try:
            audio, info = obtenir_source(src)
        except SystemExit as e:
            print(f'  ERREUR {pid} : {e}')
            erreurs += 1
            continue
        etat.setdefault(pid, {}).update({'source': src, 'licence_relevee': info['licence'],
                                         'libre': info['libre'], 'page': info.get('page')})
        if not info['libre']:
            print(f"  REFUS {pid} : licence non admise ({info['licence']})")
            erreurs += 1
            continue
        if sources_seules:
            print(f"  {pid} : {audio.name} ({info['licence']})")
            continue
        cle = empreinte(src, p.get('debut'), p.get('fin'), p.get('filtres'), p.get('fondu_entree'),
                        p.get('fondu_sortie'), chant, None, LUFS_FOND, LUFS_CHANT)
        dest = dossier / p['fichier']
        if not force and dest.exists() and etat[pid].get('empreinte') == cle and p.get('duree'):
            continue
        print(f"  {pid} : découpe, fondus, sonie → {p['fichier']}")
        p['duree'] = preparer(audio, p, dest, chant)
        etat[pid]['empreinte'] = cle
        etat[pid].pop('moteur', None)
        c.ecrire(f, d)
    etat_f.parent.mkdir(parents=True, exist_ok=True)
    etat_f.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
    c.ecrire(f, d)
    poids = sum(x.stat().st_size for x in (dossier / 'musique').glob('*.m4a')) if (dossier / 'musique').exists() else 0
    print(f'Musique : {len(pistes(d))} pistes, {poids / 1e6:.1f} Mo ; {erreurs} erreur(s).')
    return 1 if erreurs else 0


INDICATIF = c.RACINE / 'src' / 'data' / 'diaporamas' / 'commun' / 'indicatif.json'


def traiter_indicatif(force: bool) -> int:
    """Indicatif commun du générique : extraits d'ouverture et de fin, -16 LUFS, durées écrites."""
    d = json.loads(INDICATIF.read_text())
    if d['source'].get('type') == 'lyria':
        print('Indicatif composé avec Lyria : extraits déjà préparés (voir docs/journal/indicatif-original.jsonl).')
        return 0
    audio, info = obtenir_source(d['source'])
    if not info['libre']:
        print(f"  REFUS indicatif : licence non admise ({info['licence']})")
        return 1
    for nom, x in d['extraits'].items():
        p = {**{k: d[k] for k in ('filtres', 'mono') if k in d}, **x}
        cle = empreinte(d['source'], p, LUFS_CHANT)
        dest = c.PUBLIC / x['fichier']
        if not force and dest.exists() and x.get('empreinte') == cle and x.get('duree'):
            continue
        print(f"  indicatif {nom} : découpe, fondus, sonie → {x['fichier']}")
        x['duree'] = preparer(audio, p, dest, True)
        x['empreinte'] = cle
    d['page'] = info.get('page')
    INDICATIF.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
    print('Indicatif : ' + ', '.join(f"{n} {x['duree']} s" for n, x in d['extraits'].items()))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('slug', nargs='?')
    p.add_argument('--force', action='store_true')
    p.add_argument('--piste', nargs='+')
    p.add_argument('--sources', action='store_true', help='télécharger et contrôler les licences seulement')
    p.add_argument('--indicatif', action='store_true', help='indicatif commun du générique')
    a = p.parse_args()
    if a.indicatif:
        return traiter_indicatif(a.force)
    if not a.slug:
        p.error('indiquer une période')
    return traiter(a.slug, a.force, a.piste, a.sources)


if __name__ == '__main__':
    sys.exit(main())
