// Outils partagés par la section « Le siècle en images » (spec 12) : chargement des scripts
// de src/data/diaporamas/*.json, plan des neuf périodes (celles de la section écrivains),
// durées et adresses.
import { chapitresPrevus } from '../data/chapitres-ecrivains';

export interface ImageDiapo {
  fichier: string;
  commons: string;
  titre: string;
  auteur?: string;
  date?: string;
  technique?: string;
  conservation?: string;
  licence?: string;
  largeur?: number;
  hauteur?: number;
  /** Marges de papier retirées du WebP : [x0, y0, x1, y1] en fractions de l'original. */
  recadrage?: [number, number, number, number];
  /** Caméra calée sur la narration : 1 à 3 étapes (la première sans `quand`). */
  camera?: EtapeCamera[];
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
}
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
}
/** Piste de fond d'un acte ; les pistes d'un acte s'enchaînent en fondu (et bouclent). */
export interface PisteFond extends PisteCommune {
  acte: string;
  compositeur: string;
  /** Volume relatif (1 par défaut), appliqué par le lecteur. */
  volume?: number;
}
/** Intermède chanté joué au premier plan après la diapositive `apres`. `paroles` :
 *  [instant (s, dans l'extrait), vers]. */
export interface Intermede extends PisteCommune {
  apres: number;
  auteur: string;
  enregistrement: string;
  paroles: [number, string][];
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
  | ({ type: 'courbe'; titre: string; unite: string; ymax: number; points: [string, number][]; reperes: ({ date: string; libelle: string; etiquette?: [number, number]; ancre?: string } & Quand)[]; source: string } & Quand)
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
export const CARTON = 2;

const fichiers = import.meta.glob<{ default: Diaporama }>('../data/diaporamas/*.json', { eager: true });

/** Les diaporamas écrits, par numéro de période. */
export const diaporamas: Diaporama[] = Object.values(fichiers)
  .map((m) => m.default)
  .sort((a, b) => a.numero - b.numero);

export const diaporamaDe = (numero: number) => diaporamas.find((d) => d.numero === numero);

/** Durée totale en secondes (voix + pauses + cartons d'acte + intermèdes chantés, lectures et
 *  épisodes, chacun suivi d'une pause). */
export const dureeTotale = (d: Diaporama) =>
  d.diapositives.reduce((s, x) => s + (x.audio?.duree ?? 0) + PAUSE, 0) + CARTON * d.actes.length
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
