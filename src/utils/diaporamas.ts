// Outils partagés par la section « Le siècle en images » (spec 12) : chargement des scripts
// de src/data/diaporamas/*.json, plan des neuf périodes (celles de la section écrivains),
// durées et adresses.
import { chapitresPrevus } from '../data/chapitres-ecrivains';
import registrePortraits from '../data/diaporamas/portraits.json';

export interface ImageDiapo {
  fichier: string;
  commons: string;
  titre: string;
  /** Titre court rédigé pour le cartouche du lecteur (60 caractères au plus) ; le titre
   *  officiel reste dans le livre d'images et l'`alt`. */
  titre_court?: string;
  auteur?: string;
  date?: string;
  technique?: string;
  conservation?: string;
  licence?: string;
  largeur?: number;
  hauteur?: number;
  /** Marges de papier retirées du WebP : [x0, y0, x1, y1] en fractions de l'original. */
  recadrage?: [number, number, number, number];
  /** Caméra calée sur la narration : 1 à 4 étapes (la première sans `quand`). */
  camera?: EtapeCamera[];
  /** Première diapositive d'un acte : détail [x0, y0, x1, y1] (un visage, un geste, un objet)
   *  sur lequel s'ouvrent les volets du carton, avant le recul vers le premier cadre. */
  ouverture?: [number, number, number, number];
  /** Zone utile (spec 12, « Sans bordures ») : [x0, y0, x1, y1] (fractions de l'image servie), la
   *  partie qui est l'œuvre (sans liseré, marge de papier, cadre ni légende gravée). Le lecteur ne
   *  montre jamais rien en dehors. Détectée par scripts/diaporamas/utile.py. */
  utile?: [number, number, number, number];
  /** La zone utile est saisie à la main : utile.py ne la réécrit pas. */
  utile_manuel?: boolean;
}
/** Cadre [x0, y0, x1, y1] (fractions de l'image servie) ; `quand` : passage exact de la narration. */
export interface EtapeCamera { cadre: [number, number, number, number]; quand?: string }
export interface Diapositive {
  n: number;
  narration: string;
  /** Frise du temps : date des faits racontés (pas de l'œuvre), ISO partiel « AAAA »,
   *  « AAAA-MM » ou « AAAA-MM-JJ » ; absente, la diapositive reprend la date de la précédente. */
  date?: string;
  /** Fin d'une durée (même format) : le curseur de la frise devient un court segment. */
  date_fin?: string;
  image: ImageDiapo;
  /** Correction manuelle de la caméra : camera.py ne la réécrit jamais. */
  camera_manuelle?: boolean;
  /** `phrases` : [début, fin] de chaque phrase de la voix, en secondes (voix.py). */
  audio?: { fichier: string; duree: number; phrases?: [number, number][] };
  /** Lieux (5 au plus, dans l'ordre de la voix) : un seul médaillon, dont chaque point paraît
   *  quand la voix prononce son `quand` (révision du 2026-10-08). */
  lieux?: LieuDiapo[];
  /** Citation courte attribuée, dite entre « » : inscrite mot à mot sur l'image. */
  citations?: CitationDiapo[];
  /** Personnes nommées qui ne sont pas visibles sur l'image (spec 12, « Portraits des personnes
   *  nommées ») : une mention par passage, dans l'ordre de la voix ; portrait du registre. */
  personnes?: PersonneDiapo[];
  /** Personnes nommées visibles sur l'image : pas de portrait (relevé gardé pour verifier.py). */
  personnes_vues?: PersonneDiapo[];
}
/** `id` : entrée du registre `portraits.json` ; `quand` : le nom tel qu'il est dit (cherché après
 *  le précédent) ; `instant` (s) : début du nom dans l'audio (surimpressions.py). */
export interface PersonneDiapo { id: string; quand: string; instant?: number }
/** Registre des portraits (commun à toutes les périodes, scripts/diaporamas/portraits.py) :
 *  sans `fichier`, pas de portrait fiable (`note`). `fichier` : chemin dans public/diaporamas/. */
export interface Portrait {
  id: string; nom: string; dates: string; fichier?: string; commons?: string; page?: string;
  auteur?: string; date?: string; licence?: string; cadre_visage?: [number, number, number, number]; note?: string;
}
/** `fond` : plan de Paris d'époque (`paris`) ou fond Natural Earth (carte.py) ; `instant` (s) :
 *  début du passage `quand` dans l'audio (surimpressions.py ; à défaut, prorata des phrases). */
export interface LieuDiapo { nom: string; quand: string; lon: number; lat: number; fond: 'paris' | 'france' | 'voisins' | 'europe' | 'monde'; instant?: number }
/** `texte` : sous-chaîne exacte de la narration (sans les guillemets) ; `prudence` : propos
 *  rapporté (« aurait dit ») ; `mots` : [début, fin] (s) de chaque mot de `motsLus(texte)`. */
export interface CitationDiapo { texte: string; auteur: string; prudence?: boolean; mots?: [number, number][]; /** Personne citée (registre des portraits) : son portrait l'accompagne. */ personne?: string }
/** `dates` : dates de l'acte, montrées par le carton de changement d'acte (« 1787-1789 »,
 *  « juillet-octobre 1789 »). */
export interface Acte { id: string; titre: string; dates: string; debut: number }
// --- Musique (spec 12, révision du 2026-10-07) : préparée par scripts/diaporamas/musique.py ---

/** Source d'une piste : fichier Commons ou enregistrement de l'Internet Archive (78 tours publié
 *  avant 1963). Uniquement de vrais enregistrements libres (pas de rendu MIDI). */
export interface SourceMusique {
  type: 'commons' | 'archive';
  fichier?: string;
  id?: string;
  page?: string;
  publication?: string;
}
interface PisteCommune {
  id: string;
  /** Chemin dans public/diaporamas/<slug>/ (« musique/fond-crise-1.m4a »). */
  fichier: string;
  /** Durée du fichier préparé, en secondes (musique.py). */
  duree?: number;
  titre: string;
  date: string;
  interprete: string;
  source: SourceMusique;
  licence: string;
  debut?: number;
  fin?: number;
  /** Cartouche du lecteur, rédigé à la main (deux lignes, sans troncature) :
   *  « Symphonie nº 87, menuet » / « Joseph Haydn, 1785 ». */
  cartouche?: { oeuvre: string; compositeur: string };
}
/** Piste de fond d'un acte ; les pistes d'un acte s'enchaînent en fondu (et bouclent). */
export interface PisteFond extends PisteCommune {
  acte: string;
  compositeur: string;
  /** Volume relatif (1 par défaut), appliqué par le lecteur. */
  volume?: number;
}
/** Intermède chanté joué au premier plan après la diapositive `apres`. `paroles` :
 *  [instant (s, dans l'extrait), vers, mots ?] ; `mots` (calage au mot, spec 12, « Paroles des
 *  chants façon clip ») : [début, fin] de chaque mot de `motsLus(vers)` ; sans lui (`calage:
 *  "vers"`, repli), le vers entier paraît à son instant. `instrumental` : intermède musical
 *  (œuvre sans paroles, spec 12, « Arts et techniques ») ; `paroles` est vide. */
export interface Intermede extends PisteCommune {
  apres: number;
  auteur: string;
  enregistrement: string;
  paroles: ([number, string] | [number, string, [number, number][]])[];
  /** « mot » : paroles calées au mot ; « vers » : repli, vers entiers (scripts/diaporamas/paroles.py). */
  calage?: 'mot' | 'vers';
  instrumental?: boolean;
  /** Cadre [x0, y0, x1, y1] (fractions de l'image de la diapositive `apres`) que la caméra
   *  rejoint au début de l'intermède, puis où elle respire ; sans lui, elle reste sur le dernier
   *  cadre de la diapositive. */
  cadre?: [number, number, number, number];
}
/** `note` : phrase facultative sous les crédits (ex. pourquoi des compositeurs étrangers). */
export interface Musique { note?: string; fond: PisteFond[]; intermedes: Intermede[] }

// --- Lectures d'époque et épisodes (spec 12, révision du 2026-10-07) -----------------------------

/** Audio d'une lecture ou d'un épisode (voix.py) : `phrases` = [début, fin] de chaque phrase ;
 *  `mots` (lectures) = [début, fin] de chaque mot de `motsLus(texteLu(l))`, par alignement forcé
 *  (voix.py --mots). */
export interface AudioSegment { fichier: string; duree: number; phrases?: [number, number][]; mots?: [number, number][] }

/** Portrait de l'auteur d'une lecture : l'image d'une diapositive (`diapositive`, recadrée sur
 *  `cadre`) ou un fichier Commons propre (`commons`, `fichier` dans public/diaporamas/<slug>/). */
export interface PortraitLecture {
  diapositive?: number;
  commons?: string;
  fichier?: string;
  titre?: string;
  auteur?: string;
  date?: string;
  conservation?: string;
  licence?: string;
  largeur?: number;
  hauteur?: number;
  /** Visage : [x0, y0, x1, y1] en fractions de l'image. */
  cadre?: [number, number, number, number];
}

/** Lecture d'un texte d'époque, vérifié mot pour mot sur Wikisource (`source.page`), lue par une
 *  seconde voix après la diapositive `apres`. `texte` : paragraphes (ou strophes, vers séparés
 *  par des retours à la ligne) ; « […] » seul = coupure. */
export interface Lecture {
  id: string;
  apres: number;
  date?: string;
  auteur: { nom: string; dates: string; voix: 'homme' | 'femme' };
  nature: string;
  oeuvre: string;
  annee: string;
  reference?: string;
  source: { page: string; edition?: string };
  /** Extrait du chapitre écrivains de la période dont la lecture est tirée. */
  ecrivains?: string;
  poeme?: boolean;
  texte: string[];
  portrait?: PortraitLecture;
  audio?: AudioSegment;
}

type Quand = { quand?: string };
export type VisuelEpisode =
  | ({ type: 'carton'; texte: string; sous?: string } & Quand)
  | ({ type: 'chiffres'; titre?: string; items: ({ valeur: string; unite?: string; libelle: string; accent?: boolean } & Quand)[]; source?: string } & Quand)
  | ({ type: 'barres'; titre: string; unite: string; max: number; barres: ({ libelle: string; valeur: number; affichage?: string; note?: string; accent?: boolean } & Quand)[]; source: string } & Quand)
  /** Courbe : `unite` dite une fois sous le titre ; chaque repère est étiqueté « date · valeur en
   *  clair » (valeur tirée de `points` et de `unite_point`, ou `libelle` rédigé en clair), placé
   *  automatiquement sans toucher la courbe ni les axes. */
  | ({ type: 'courbe'; titre: string; unite: string; unite_point?: string; ymax: number; points: [string, number][]; reperes: ({ date: string; libelle?: string } & Quand)[]; source: string } & Quand)
  | ({ type: 'carte'; fond: string; titre: string; elements: ElementCarte[]; legende?: [string, string][]; source: string } & Quand)
  | ({ type: 'document'; image: ImageDiapo & { fichier: string }; lignes: ({ cadre: [number, number, number, number]; texte: string } & Quand)[]; source: string } & Quand);
export type ElementCarte = Quand & (
  | { type: 'ville'; lieu: [number, number]; libelle: string; capitale?: boolean; rebelle?: boolean; position?: string }
  | { type: 'fleche'; de: [number, number]; a: [number, number]; libelle: string; position?: string }
  | { type: 'zone'; points: [number, number][]; libelle: string });

/** Épisode : courte narration (voix du narrateur) sur ce que les images ne montrent pas, avec des
 *  visuels animés synchronisés sur les passages `quand` de la narration. */
export interface Episode {
  id: string;
  apres: number;
  titre: string;
  date?: string;
  narration: string;
  visuels: VisuelEpisode[];
  sources: string[];
  audio?: AudioSegment;
}

/** Fond de carte (scripts/diaporamas/carte.py). */
export interface FondCarte {
  nom: string; licence: string; source: string; note: string;
  projection: { cadre: [number, number, number, number]; echelle: number; cx: number };
  largeur: number; hauteur: number; terres: string; france: string; fleuves: string[];
}

/** Plan de Paris d'époque (carte.py, src/data/diaporamas/plans/) : image servie, crédit et
 *  calage (lon, lat) → fractions (u, v) de l'image. */
export interface PlanParis {
  nom: string; fichier: string; largeur: number; hauteur: number; titre: string; auteur: string; date: string;
  credit: string; commons: string; licence: string; slugs: string[];
  calage: { u: [number, number, number]; v: [number, number, number]; metres_par_pixel: number; ecart_moyen_m: number };
}
const plans = Object.values(import.meta.glob<{ default: PlanParis }>('../data/diaporamas/plans/*.json', { eager: true })).map((m) => m.default);
/** Plan de Paris de la période (celui dont `slugs` la contient). */
export const planParis = (slug: string) => plans.find((p) => p.slugs.includes(slug));

export interface Diaporama {
  slug: string;
  numero: number;
  titre: string;
  periode: string;
  resume: string;
  actes: Acte[];
  diapositives: Diapositive[];
  musique?: Musique;
  lectures?: Lecture[];
  episodes?: Episode[];
}

const base = import.meta.env.BASE_URL;
export const urlSectionDiaporamas = `${base}diaporamas/`;
export const urlDiaporama = (slug: string) => `${base}diaporamas/${slug}/`;
export const urlMedia = (slug: string, fichier: string) => `${base}diaporamas/${slug}/${fichier}`;
export const urlCommons = (fichier: string) =>
  `https://commons.wikimedia.org/wiki/${encodeURIComponent(fichier.replace(/ /g, '_')).replace(/%3A/g, ':')}`;

/** Pause entre deux diapositives, en secondes (comptée dans la durée totale). */
export const PAUSE = 0.6;
/** Carton de changement d'acte, en secondes, avant la première image de chaque acte (compté dans
 *  la durée totale ; même valeur dans scripts/diaporamas/verifier.py). */
export const CARTON = 12;

const fichiers = import.meta.glob<{ default: Diaporama }>(['../data/diaporamas/*.json', '!../data/diaporamas/portraits.json'], { eager: true });
/** Registre des portraits des personnes nommées, commun à toutes les périodes. */
export const portraits: Portrait[] = registrePortraits as Portrait[];

/** Les diaporamas écrits, par numéro de période. */
export const diaporamas: Diaporama[] = Object.values(fichiers)
  .map((m) => m.default)
  .sort((a, b) => a.numero - b.numero);

export const diaporamaDe = (numero: number) => diaporamas.find((d) => d.numero === numero);

/** Durée totale en secondes (voix + pauses + cartons d'acte + intermèdes chantés, lectures et
 *  épisodes, chacun suivi d'une pause). */
export const dureeTotale = (d: Diaporama) =>
  d.diapositives.reduce((s, x) => s + (x.audio?.duree ?? 0) + pauseApres(x), 0) + CARTON * d.actes.length
  + (d.musique?.intermedes ?? []).reduce((s, x) => s + (x.duree ?? 0) + PAUSE, 0)
  + [...(d.lectures ?? []), ...(d.episodes ?? [])].reduce((s, x) => s + (x.audio?.duree ?? 0) + PAUSE, 0);

/** Texte lu d'une lecture : les paragraphes sans les coupures, joints par une espace (les retours
 *  à la ligne des vers deviennent des espaces : mêmes positions de caractères que l'affichage).
 *  Même calcul que `texte_lu` dans scripts/diaporamas/commun.py. */
export const texteLu = (l: Lecture) => l.texte.filter((b) => b.trim() !== '[…]').join(' ').replace(/\n/g, ' ');

/** URL publique d'une page Wikisource. */
export const urlWikisource = (page: string) =>
  `https://fr.wikisource.org/wiki/${encodeURIComponent(page.replace(/ /g, '_')).replace(/%2F/g, '/').replace(/%2C/g, ',').replace(/%28/g, '(').replace(/%29/g, ')')}`;

/** Page de la source d'une piste de musique (crédits). */
export function urlSourceMusique(s: SourceMusique) {
  if (s.type === 'archive' && s.id) return `https://archive.org/details/${encodeURIComponent(s.id)}`;
  if (s.type === 'commons' && s.fichier) return urlCommons(s.fichier);
  return s.page ?? '';
}
/** Libellé court de la source (crédits). */
export function nomSourceMusique(s: SourceMusique) {
  if (s.type === 'archive') return 'Internet Archive';
  return 'Wikimedia Commons';
}

/** « 21 min », « 1 h 05 ». */
export function formaterDuree(secondes: number) {
  const min = Math.round(secondes / 60);
  return min < 60 ? `${min} min` : `${Math.floor(min / 60)} h ${String(min % 60).padStart(2, '0')}`;
}

/** Les neuf périodes prévues, avec le diaporama correspondant s'il existe. */
export const planDiaporamas = () =>
  chapitresPrevus.map((p) => ({ ...p, diaporama: diaporamaDe(p.numero) }));

/** Débuts (en caractères) des phrases d'une narration ; même découpage que
 *  scripts/diaporamas/commun.py (`phrases`). */
function debutsPhrases(texte: string) {
  const debuts = [0];
  const re = /[.!?…]\s+(?=[«A-ZÀÂÉÈÊÎÔÛÇ0-9])/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(texte))) debuts.push(m.index + m[0].length);
  return debuts;
}

/**
 * Instant (s) où la voix prononce le caractère `pos` d'un texte : situé au prorata dans sa phrase
 * horodatée (`phrases`), ou de tout le texte si les phrases manquent.
 */
export function instantCaractere(texte: string, pos: number, duree: number, phrases?: [number, number][]) {
  const debuts = debutsPhrases(texte);
  if (!phrases || phrases.length !== debuts.length) return (pos / Math.max(1, texte.length)) * duree;
  let j = debuts.length - 1;
  while (j > 0 && debuts[j] > pos) j--;
  const finCar = j + 1 < debuts.length ? debuts[j + 1] : texte.length;
  const [d, f] = phrases[j];
  return Math.round((d + ((pos - debuts[j]) / Math.max(1, finCar - debuts[j])) * (f - d)) * 100) / 100;
}

/** Instant (s) du passage exact `quand` d'une narration horodatée (sa première occurrence), ou
 *  `null` s'il est absent. */
export function instantPassage(texte: string, quand: string, duree: number, phrases?: [number, number][]) {
  const pos = texte.indexOf(quand);
  return pos < 0 ? null : instantCaractere(texte, pos, duree, phrases);
}

/** Mots d'un texte lu (minutage mot par mot des lectures) : suites sans espace contenant au
 *  moins une lettre ou un chiffre ; la ponctuation isolée (« ? », « : », « » ») n'en est pas un.
 *  Même découpage que `mots_lus` dans scripts/diaporamas/commun.py. */
export function motsLus(texte: string) {
  const sortie: { d: number; f: number }[] = [];
  for (const m of texte.matchAll(/\S+/g)) if (/[\p{L}\p{N}]/u.test(m[0])) sortie.push({ d: m.index!, f: m.index! + m[0].length });
  return sortie;
}

/**
 * Minutage d'une lecture pour le lecteur : instant de début de chaque mot (alignement forcé de
 * `audio.mots`, ou repli au prorata des caractères dans sa phrase horodatée) et, pour chaque
 * phrase, [début (s), premier mot, mot suivant le dernier] (apparition par phrase quand le
 * mouvement est réduit).
 */
export function minutageLecture(l: Lecture) {
  const texte = texteLu(l);
  const mots = motsLus(texte);
  const duree = l.audio?.duree ?? 0;
  const bornes = phrasesDe(texte);
  const ph = l.audio?.phrases?.length === bornes.length ? l.audio.phrases : null;
  const aligne = l.audio?.mots?.length === mots.length;
  const debuts = aligne
    ? l.audio!.mots!.map(([t0]) => t0)
    : mots.map((m) => {
      if (!ph) return Math.round((m.d / Math.max(1, texte.length)) * duree * 100) / 100;
      let j = bornes.length - 1;
      while (j > 0 && bornes[j].d > m.d) j--;
      const [t0, t1] = ph[j];
      return Math.round((t0 + ((m.d - bornes[j].d) / Math.max(1, bornes[j].f - bornes[j].d)) * (t1 - t0)) * 100) / 100;
    });
  let k = 0;
  const phrases = bornes.map((b) => {
    const k0 = k;
    while (k < mots.length && mots[k].d < b.f) k++;
    return [k0 < mots.length ? debuts[k0] : duree, k0, k] as [number, number, number];
  });
  return { mots: debuts, phrases, aligne };
}

/** Phrases d'un texte avec leurs bornes en caractères (même découpage que commun.py). */
export function phrasesDe(texte: string) {
  const debuts = debutsPhrases(texte);
  return debuts.map((d, k) => ({ d, f: k + 1 < debuts.length ? debuts[k + 1] : texte.length }));
}

/**
 * Étapes de caméra d'une diapositive pour le lecteur : cadre et instant (en secondes dans
 * l'audio) où la voix prononce le passage `quand`, situé au prorata dans sa phrase horodatée
 * (au prorata de toute la narration si les phrases manquent). La première étape est à 0.
 */
export function etapesCamera(x: Diapositive): { c: [number, number, number, number]; t: number }[] {
  const etapes = x.image.camera?.length ? x.image.camera : [{ cadre: [0, 0, 1, 1] as [number, number, number, number] }];
  const texte = x.narration;
  const duree = x.audio?.duree ?? 6;
  const debuts = debutsPhrases(texte);
  const phrases = x.audio?.phrases;
  const horodate = phrases && phrases.length === debuts.length;
  let apres = 0;
  return etapes.map((e, k) => {
    if (k === 0 || !e.quand) return { c: e.cadre, t: 0 };
    let pos = texte.indexOf(e.quand, apres);
    if (pos < 0) pos = texte.indexOf(e.quand);
    if (pos < 0) return { c: e.cadre, t: 0 };
    apres = pos + e.quand.length;
    if (!horodate) return { c: e.cadre, t: (pos / texte.length) * duree };
    let j = debuts.length - 1;
    while (j > 0 && debuts[j] > pos) j--;
    const finCar = j + 1 < debuts.length ? debuts[j + 1] : texte.length;
    const [d, f] = phrases![j];
    return { c: e.cadre, t: Math.round((d + ((pos - debuts[j]) / Math.max(1, finCar - debuts[j])) * (f - d)) * 100) / 100 };
  });
}

type Rect = [number, number, number, number];
/** Zone utile d'une image (l'image entière si elle n'est pas renseignée ou invalide). */
export function zoneUtile(x: Diapositive): Rect {
  const u = x.image.utile;
  return u && u[0] >= 0 && u[1] >= 0 && u[2] <= 1 && u[3] <= 1 && u[2] > u[0] && u[3] > u[1] ? u : [0, 0, 1, 1];
}
/** Cadre `r` (fractions de l'image entière) exprimé dans la zone utile `u` (fractions de la zone)
 *  et ramené dedans : déplacé s'il y tient, sinon réduit à sa partie commune avec la zone. */
export function versUtile(r: Rect, u: Rect): Rect {
  const w = u[2] - u[0], h = u[3] - u[1];
  const borne = (a: number, b: number) => {
    let lo = a, hi = b;
    if (hi - lo >= 1) return [0, 1];
    if (lo < 0) { hi -= lo; lo = 0; }
    if (hi > 1) { lo -= hi - 1; hi = 1; }
    return [lo, hi];
  };
  const [x0, x1] = borne((r[0] - u[0]) / w, (r[2] - u[0]) / w);
  const [y0, y1] = borne((r[1] - u[1]) / h, (r[3] - u[1]) / h);
  const k = (v: number) => Math.round(v * 1e5) / 1e5;
  return [k(x0), k(y0), k(x1), k(y1)];
}

// --- Frise du temps (spec 12, révision du 2026-10-07) ------------------------------------------

/** Saut notable vers l'avant (en jours, ~3 mois) au-delà duquel la frise s'affiche en
 *  surimpression ; même valeur que SAUT_JOURS dans scripts/diaporamas/verifier.py. */
export const SAUT_JOURS = 92;

const MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre',
  'octobre', 'novembre', 'décembre'];
const jour = (a: number, m: number, j: number) => Date.UTC(a, m - 1, j) / 86400000;

/** Premier et dernier jour (jours depuis 1970, UTC) d'une date ISO partielle. */
export function bornesDate(texte: string): [number, number] {
  const [a, m, j] = texte.split('-').map(Number);
  if (j) return [jour(a, m, j), jour(a, m, j)];
  if (m) return [jour(a, m, 1), jour(a, m + 1, 1) - 1];
  return [jour(a, 1, 1), jour(a + 1, 1, 1) - 1];
}

/** « 1789 », « juillet 1789 », « 14 juillet 1789 » ; sans l'année si `annee` est faux. */
function libelleSimple(texte: string, annee = true) {
  const [a, m, j] = texte.split('-').map(Number);
  const mots = [j ? (j === 1 ? '1er' : String(j)) : '', m ? MOIS[m - 1] : '', annee || !m ? String(a) : ''];
  return mots.filter(Boolean).join(' ');
}

/** Libellé français d'une date ou d'une durée : « 14 juillet 1789 », « 2-6 septembre 1792 »,
 *  « février-avril 1787 », « 1793-1794 », « 21 septembre – 11 décembre 1792 ». */
export function libelleDate(date: string, fin?: string) {
  if (!fin) return libelleSimple(date);
  const [a1, m1, j1] = date.split('-').map(Number);
  const [a2, m2, j2] = fin.split('-').map(Number);
  const droite = libelleSimple(fin);
  // Même mois (« 2-6 septembre 1792 »), même année en mois (« février-avril 1787 ») ou années
  // seules (« 1793-1794 ») : trait d'union ; sinon tiret demi-cadratin (« 21 septembre – 11 décembre 1792 »).
  if (a1 === a2 && m1 === m2 && j1 && j2) return `${j1 === 1 ? '1er' : j1}-${droite}`;
  if (a1 === a2 && m1 && m2 && !j1 && !j2) return `${MOIS[m1 - 1]}-${droite}`;
  if (!m1 && !m2) return `${a1}-${a2}`;
  return `${libelleSimple(date, a1 !== a2)}\u00a0– ${droite}`;
}

/** Années (première et dernière) des dates d'un acte : « juillet-octobre 1789 » → [1789, 1789]. */
const anneesActe = (dates: string) => (dates.match(/\b1[789]\d\d\b/g) ?? []).map(Number);

/**
 * Frise d'une période : bornes (du 1er janvier de la première année du premier acte au
 * 31 décembre de la dernière année du dernier acte), années, segments des actes (de la date de
 * leur première diapositive à celle de l'acte suivant) et, pour chaque diapositive, l'intervalle
 * daté (jours) et son libellé ; une diapositive sans date reprend celle de la précédente.
 * `null` si la période n'est pas datée.
 */
export function friseDe(d: Diaporama) {
  const premiere = anneesActe(d.actes[0]?.dates ?? ''), derniere = anneesActe(d.actes.at(-1)?.dates ?? '');
  if (!premiere.length || !derniere.length || !d.diapositives[0]?.date) return null;
  const a0 = Math.min(...premiere), a1 = Math.max(...derniere);
  const debut = jour(a0, 1, 1), fin = jour(a1 + 1, 1, 1);
  const frac = (j: number) => Math.round(((j - debut) / (fin - debut)) * 1e5) / 1e3; // en %
  let prec = { j0: debut, j1: debut, libelle: '' };
  const diapos = d.diapositives.map((x) => {
    if (x.date) {
      const [j0] = bornesDate(x.date);
      const j1 = bornesDate(x.date_fin ?? x.date)[1];
      prec = { j0, j1, libelle: libelleDate(x.date, x.date_fin) };
    }
    return { ...prec, x0: frac(prec.j0), x1: frac(prec.j1 + 1) };
  });
  const debutsActes = d.actes.map((a, k) => (k === 0 ? 0 : diapos[d.diapositives.findIndex((x) => x.n >= a.debut)].x0));
  for (let k = 1; k < debutsActes.length; k++) debutsActes[k] = Math.max(debutsActes[k], debutsActes[k - 1]);
  /** Une date quelconque (lecture, épisode) placée sur la même frise. */
  const dater = (date: string, dateFin?: string) => {
    const [j0] = bornesDate(date);
    const j1 = bornesDate(dateFin ?? date)[1];
    return { j0, j1, libelle: libelleDate(date, dateFin), x0: frac(j0), x1: frac(j1 + 1) };
  };
  return {
    dater,
    annees: Array.from({ length: a1 - a0 + 1 }, (_, k) => ({ a: a0 + k, x0: frac(jour(a0 + k, 1, 1)), x1: frac(jour(a0 + k + 1, 1, 1)) })),
    actes: debutsActes.map((x0, k) => ({ x0, x1: k + 1 < debutsActes.length ? debutsActes[k + 1] : 100 })),
    diapos,
  };
}

// --- Cartes de lieu et citations en surimpression (spec 12, 2026-10-07) ------------------------

/** Médaillon : ~5 s ; un lieu dit tout à la fin est montré un peu plus tôt pour rester ~4 s. */
export const DUREE_LIEU = 5;
/** Plusieurs lieux (révision du 2026-10-08) : 5 au plus ; le médaillon reste ~3 s après le
 *  dernier nom (même valeurs dans scripts/diaporamas/verifier.py). */
export const MAX_LIEUX = 5;
const APRES_LIEUX = 3;
/** Fonds du plus étroit au plus large : un médaillon à plusieurs lieux prend le plus large. */
const ORDRE_FONDS = ['paris', 'france', 'voisins', 'europe', 'monde'] as const;
/** Cadre calculé (plusieurs lieux) : rapport largeur/hauteur, part maximale occupée par les
 *  points (le reste est la marge des noms), largeur minimale (fraction du fond : la France
 *  reste reconnaissable). */
const RATIO_MULTI = 4 / 3;
const EMPRISE_POINTS = 0.6;
const LARGEUR_MIN_FOND = 0.45;

/** Point d'un médaillon à plusieurs lieux : position (%) dans le cadre et instant (s) où la
 *  voix dit le lieu. */
export interface PointLieu { nom: string; x: number; y: number; t: number }
/** Médaillon de lieu prêt pour le lecteur. Plusieurs lieux : `points` (dans l'ordre de la
 *  voix) et, sur un fond SVG, `vb` (viewBox du cadre calculé) ; `nom` est alors vide (les noms
 *  sont posés sur la carte). */
export interface LieuMedaillon {
  a: number; b: number; nom: string; fond: string; x: number; y: number; ratio: number; vue?: string; credit?: string;
  points?: PointLieu[]; vb?: string;
}

/**
 * Instants des lieux d'une diapositive : `instant` (surimpressions.py), sinon début du passage
 * `quand` au prorata ; chaque passage est cherché après le début du précédent (même règle dans
 * surimpressions.py et verifier.py).
 */
export function instantsLieux(x: Diapositive) {
  const duree = x.audio?.duree ?? 6;
  let depuis = 0;
  return (x.lieux ?? []).map((li) => {
    const pos = x.narration.indexOf(li.quand, depuis);
    if (pos >= 0) depuis = pos + 1;
    return li.instant ?? (pos < 0 ? null : instantCaractere(x.narration, pos, duree, x.audio?.phrases));
  });
}

/**
 * Médaillon à plusieurs lieux (spec 12, révision du 2026-10-08) : un seul médaillon dont le cadre,
 * calculé, englobe tous les points avec une marge. Fond : le plan de Paris si tous les lieux sont
 * à Paris (recadré sur eux), sinon le fond SVG le plus large demandé, élargi s'il le faut (un lieu
 * de Paris y devient « Paris »). Fenêtre : du premier nom à ~3 s après le dernier (5 s au moins),
 * la citation gardant la priorité comme pour un lieu seul.
 */
function medaillonMultiple(x: Diapositive, fonds: Record<string, FondCarte>, plan: PlanParis | undefined,
  fin: number, citation: null | { a: number; b: number }): LieuMedaillon | null {
  const instants = instantsLieux(x);
  const lieux = (x.lieux ?? []).map((li, k) => ({ li, t: instants[k] }))
    .filter((p): p is { li: LieuDiapo; t: number } => p.t !== null).slice(0, MAX_LIEUX);
  if (!lieux.length) return null;
  const tousParis = lieux.every((p) => p.li.fond === 'paris');
  const pc = (n: number) => `${(Math.round(n * 1000) / 10).toFixed(1)}%`;
  const r1 = (n: number) => Math.round(n * 10) / 10;
  /** Cadre [x0, y0, w, h] (unités du fond) qui englobe `pts`, au rapport RATIO_MULTI, borné au fond. */
  const cadre = (pts: [number, number][], L: number, H: number, wMin: number): [number, number, number, number] => {
    const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
    const bx0 = Math.min(...xs), bx1 = Math.max(...xs), by0 = Math.min(...ys), by1 = Math.max(...ys);
    let w = Math.max(wMin, (bx1 - bx0) / EMPRISE_POINTS, ((by1 - by0) / EMPRISE_POINTS) * RATIO_MULTI);
    w = Math.min(w, L, H * RATIO_MULTI);
    const h = w / RATIO_MULTI;
    const x0 = Math.min(L - w, Math.max(0, (bx0 + bx1) / 2 - w / 2)), y0 = Math.min(H - h, Math.max(0, (by0 + by1) / 2 - h / 2));
    return [x0, y0, w, h];
  };
  let med: Omit<LieuMedaillon, 'a' | 'b'> | null = null;
  if (tousParis && plan) {
    // Plan de Paris d'époque : positions en pixels du plan, recadrage CSS (`vue`).
    const px = lieux.map((p) => [
      (plan.calage.u[0] * p.li.lon + plan.calage.u[1] * p.li.lat + plan.calage.u[2]) * plan.largeur,
      (plan.calage.v[0] * p.li.lon + plan.calage.v[1] * p.li.lat + plan.calage.v[2]) * plan.hauteur] as [number, number]);
    const [x0, y0, w, h] = cadre(px, plan.largeur, plan.hauteur, VUE_PARIS_M / plan.calage.metres_par_pixel);
    const fw = w / plan.largeur, fh = h / plan.hauteur, fx = x0 / plan.largeur, fy = y0 / plan.hauteur;
    const points = lieux.map((p, k) => ({ nom: p.li.nom, x: r1(((px[k][0] - x0) / w) * 100), y: r1(((px[k][1] - y0) / h) * 100), t: p.t }));
    med = { nom: '', fond: 'paris', x: points[0].x, y: points[0].y, ratio: Math.round(RATIO_MULTI * 1000) / 1000, points,
      vue: `${pc(1 / fw)} auto;${pc(fw < 1 ? fx / (1 - fw) : 0)} ${pc(fh < 1 ? fy / (1 - fh) : 0)}`, credit: plan.credit };
  } else {
    // Fond SVG : le plus large demandé, élargi tant qu'un point sort de son cadre (marge de 3 %).
    let k = Math.max(1, ...lieux.map((p) => ORDRE_FONDS.indexOf(p.li.fond)));
    const dedans = (f: FondCarte) => lieux.every(({ li }) => {
      const [c0, c1, c2, c3] = f.projection.cadre, mx = (c2 - c0) * 0.03, my = (c3 - c1) * 0.03;
      return li.lon >= c0 + mx && li.lon <= c2 - mx && li.lat >= c1 + my && li.lat <= c3 - my;
    });
    while (k < ORDRE_FONDS.length - 1 && (!fonds[ORDRE_FONDS[k]] || !dedans(fonds[ORDRE_FONDS[k]]))) k++;
    const f = fonds[ORDRE_FONDS[k]];
    if (!f) return null;
    // Un lieu de Paris sur une carte plus large : « Paris », une seule fois.
    const vus = new Set<string>();
    const retenus = lieux.map((p) => ({ ...p, nom: p.li.fond === 'paris' ? 'Paris' : p.li.nom }))
      .filter((p) => (vus.has(p.nom) ? false : (vus.add(p.nom), true)));
    const { cadre: c, echelle, cx } = f.projection;
    const px = retenus.map(({ li }) => [(li.lon - c[0]) * cx * echelle, (c[3] - li.lat) * echelle] as [number, number]);
    const [x0, y0, w, h] = cadre(px, f.largeur, f.hauteur, f.largeur * LARGEUR_MIN_FOND);
    const points = retenus.map((p, j) => ({ nom: p.nom, x: r1(((px[j][0] - x0) / w) * 100), y: r1(((px[j][1] - y0) / h) * 100), t: p.t }));
    const n = (v: number) => Math.round(v * 10) / 10;
    med = { nom: '', fond: f.nom, x: points[0].x, y: points[0].y, ratio: Math.round((w / h) * 1000) / 1000, points, vb: `${n(x0)} ${n(y0)} ${n(w)} ${n(h)}` };
  }
  if (!med?.points?.length) return null;
  const t0 = med.points[0].t, tn = med.points.at(-1)!.t;
  let a = Math.max(0, Math.min(t0 - 0.1, fin - 4)), b = Math.max(tn + APRES_LIEUX, a + DUREE_LIEU);
  if (citation && a < citation.b + 0.3 && b > citation.a - 0.5) {
    // Même arbitrage qu'un lieu seul : après la citation (tous les points d'un coup), sinon avant
    // elle (les lieux dits ensuite sont omis), sinon pas de médaillon.
    if (citation.b + 0.3 + 3 <= fin) { a = citation.b + 0.3; b = a + DUREE_LIEU; }
    else if (citation.a - 0.5 - a >= 2.5) { b = citation.a - 0.5; med.points = med.points.filter((p) => p.t < b - 1); }
    else return null;
  }
  if (!med.points.length) return null;
  return { a: Math.round(a * 100) / 100, b: Math.round(b * 100) / 100, ...med };
}
/** Largeur de Paris montrée dans le médaillon (m) : le plan est zoomé sur le lieu. */
const VUE_PARIS_M = 2000;
const RATIO_PARIS = 4 / 3;
/** La citation reste ~2 s après son dernier mot. */
const APRES_CITATION = 2;

/** Fin (s) du dernier mot de la citation d'une diapositive (alignement, sinon prorata), ou null. */
function finCitation(x: Diapositive) {
  const ci = x.citations?.[0];
  const pos = ci ? x.narration.indexOf(ci.texte) : -1;
  if (!ci || pos < 0) return null;
  if (ci.mots?.length === motsLus(ci.texte).length) return ci.mots.at(-1)![1];
  return instantCaractere(x.narration, pos + ci.texte.length, x.audio?.duree ?? 6, x.audio?.phrases);
}
/**
 * Pause après la voix d'une diapositive : PAUSE (0,6 s), allongée quand la narration finit par
 * une citation en surimpression, pour qu'elle reste ~2 s après son dernier mot :
 * max(PAUSE, fin du dernier mot + 2 s − durée de la voix). Même calcul dans verifier.py.
 */
export function pauseApres(x: Diapositive) {
  const f = finCitation(x);
  const duree = x.audio?.duree ?? 6;
  return f === null ? PAUSE : Math.max(PAUSE, Math.round((f + APRES_CITATION - duree) * 100) / 100);
}

/**
 * Données du lecteur pour la carte de lieu et la citation d'une diapositive : fenêtres
 * d'affichage `[a, b)` en secondes de l'audio (la citation l'emporte : le médaillon passe après
 * elle, ou avant, ou pas du tout s'il n'y a pas la place), position du point (%) dans le fond, et
 * pour Paris la partie du plan montrée (fond CSS). Les instants viennent de surimpressions.py
 * (alignement des mots), sinon du prorata des caractères dans les phrases horodatées.
 */
export function surimpressionsDe(x: Diapositive, fonds: Record<string, FondCarte>, plan: PlanParis | undefined) {
  const duree = x.audio?.duree ?? 6;
  const phrases = x.audio?.phrases;
  const fin = duree + pauseApres(x);
  let citation: null | { a: number; b: number; mots: number[]; fin: number; texte: string; auteur: string; prudence: boolean; personne?: string } = null;
  const ci = x.citations?.[0];
  const pos = ci ? x.narration.indexOf(ci.texte) : -1;
  if (ci && pos >= 0) {
    const mots = motsLus(ci.texte);
    const aligne = ci.mots?.length === mots.length;
    const debuts = aligne ? ci.mots!.map(([t0]) => t0) : mots.map((m) => instantCaractere(x.narration, pos + m.d, duree, phrases));
    const dernier = aligne ? ci.mots!.at(-1)![1] : instantCaractere(x.narration, pos + ci.texte.length, duree, phrases);
    citation = { a: Math.max(0, debuts[0] - 0.15), b: dernier + APRES_CITATION, mots: debuts, fin: dernier, texte: ci.texte, auteur: ci.auteur, prudence: !!ci.prudence, personne: ci.personne };
  }
  const gens = portraitsDe(x, citation, fin);
  let lieu: null | LieuMedaillon = null;
  if ((x.lieux?.length ?? 0) > 1) return { lieu: medaillonMultiple(x, fonds, plan, fin, citation), citation, portraits: gens };
  const li = x.lieux?.[0];
  const t = li ? li.instant ?? instantPassage(x.narration, li.quand, duree, phrases) : null;
  if (li && t !== null) {
    let a = Math.max(0, Math.min(t - 0.1, fin - 4)), b = a + DUREE_LIEU;
    if (citation && a < citation.b + 0.3 && b > citation.a - 0.5) {
      // Gêne : après la citation s'il reste ~3 s, sinon avant si ~2,5 s tiennent, sinon pas de carte.
      if (citation.b + 0.3 + 3 <= fin) { a = citation.b + 0.3; b = a + DUREE_LIEU; }
      else if (citation.a - 0.5 - a >= 2.5) b = citation.a - 0.5;
      else a = b = -1;
    }
    if (a >= 0) {
      if (li.fond === 'paris' && plan) {
        const u = plan.calage.u[0] * li.lon + plan.calage.u[1] * li.lat + plan.calage.u[2];
        const v = plan.calage.v[0] * li.lon + plan.calage.v[1] * li.lat + plan.calage.v[2];
        // Fenêtre du plan (fractions) centrée sur le lieu, bornée à l'image.
        const w = Math.min(1, VUE_PARIS_M / plan.calage.metres_par_pixel / plan.largeur);
        const h = Math.min(1, (w * plan.largeur) / RATIO_PARIS / plan.hauteur);
        const x0 = Math.min(1 - w, Math.max(0, u - w / 2)), y0 = Math.min(1 - h, Math.max(0, v - h / 2));
        const pc = (n: number) => `${(Math.round(n * 1000) / 10).toFixed(1)}%`;
        lieu = { a, b, nom: li.nom, fond: 'paris', x: ((u - x0) / w) * 100, y: ((v - y0) / h) * 100, ratio: RATIO_PARIS,
          vue: `${pc(1 / w)} auto;${pc(w < 1 ? x0 / (1 - w) : 0)} ${pc(h < 1 ? y0 / (1 - h) : 0)}`, credit: plan.credit };
      } else if (fonds[li.fond]) {
        const f = fonds[li.fond], { cadre, echelle, cx } = f.projection;
        lieu = { a, b, nom: li.nom, fond: li.fond, x: (((li.lon - cadre[0]) * cx * echelle) / f.largeur) * 100,
          y: (((cadre[3] - li.lat) * echelle) / f.hauteur) * 100, ratio: f.largeur / f.hauteur };
      }
      if (lieu) { lieu.x = Math.round(lieu.x * 10) / 10; lieu.y = Math.round(lieu.y * 10) / 10; lieu.ratio = Math.round(lieu.ratio * 1000) / 1000; }
    }
  }
  return { lieu, citation, portraits: gens };
}

// --- Portraits des personnes nommées (spec 12, 2026-10-08) --------------------------------------

/** Rangée de portraits : 4 au plus ; elle reste ~3 s après le dernier nom, 5 s au moins (mêmes
 *  valeurs dans scripts/diaporamas/verifier.py). */
export const MAX_PORTRAITS = 4;
const APRES_PORTRAITS = 3;
const DUREE_PORTRAITS = 5;
/** Portrait montré par le lecteur : nom et dates, image, instant (s) où il paraît. */
export interface PortraitMontre { id: string; nom: string; dates: string; src: string; t: number }

/**
 * Instants des mentions d'une diapositive : `instant` (surimpressions.py), sinon début du nom au
 * prorata ; chaque nom est cherché après le précédent (comme les lieux).
 */
export function instantsPersonnes(x: Diapositive) {
  const duree = x.audio?.duree ?? 6;
  let depuis = 0;
  return (x.personnes ?? []).map((p) => {
    const pos = x.narration.indexOf(p.quand, depuis);
    if (pos >= 0) depuis = pos + 1;
    return p.instant ?? (pos < 0 ? null : instantCaractere(x.narration, pos, duree, x.audio?.phrases));
  });
}

/**
 * Rangée de portraits d'une diapositive : une personne par ovale (dans l'ordre de leur première
 * mention, 4 au plus, celles qui ont un portrait), chacune paraissant à son nom ; fenêtre [a, b)
 * du premier nom à ~3 s après le dernier (5 s au moins), prolongée jusqu'à la fin de la citation
 * quand la personne citée est dans la rangée. Les fenêtres des autres surimpressions ne changent
 * pas : la rangée coexiste avec le médaillon de lieu (coin opposé) et avec la citation (qui monte
 * au-dessus d'elle si elles se touchent, voir Diaporama.astro).
 */
export function portraitsDe(x: Diapositive, citation: null | { b: number; personne?: string }, fin: number) {
  const parId = new Map(portraits.map((p) => [p.id, p]));
  const instants = instantsPersonnes(x);
  const gens: PortraitMontre[] = [];
  let dernier = -1;
  (x.personnes ?? []).forEach((m, k) => {
    const p = parId.get(m.id), t = instants[k];
    if (!p?.fichier || t === null) return;
    if (gens.some((g) => g.id === m.id)) { dernier = Math.max(dernier, t); return; }
    if (gens.length >= MAX_PORTRAITS) return;
    gens.push({ id: p.id, nom: p.nom, dates: p.dates, src: `${base}diaporamas/${p.fichier}`, t: Math.round(t * 100) / 100 });
    dernier = Math.max(dernier, t);
  });
  if (!gens.length) return null;
  const a = Math.max(0, Math.min(gens[0].t - 0.1, fin - 4));
  let b = Math.max(dernier + APRES_PORTRAITS, a + DUREE_PORTRAITS);
  if (citation?.personne && gens.some((g) => g.id === citation.personne)) b = Math.max(b, citation.b);
  return { a: Math.round(a * 100) / 100, b: Math.round(b * 100) / 100, gens };
}
