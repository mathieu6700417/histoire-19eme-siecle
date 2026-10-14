// Type du contexte `lec` partagé par les modules : état mutable (`lec.i`, `lec.enCarton`…) et
// fonctions qu'un module expose aux autres. Généré au découpage ; à tenir à jour à la main
// quand un module expose un nouveau membre (Object.assign(lec, …) en tête ou en fin de module).
import type { Couleur, DateFrise, Fond, Diapo, Donnees, EtatSegment, Plan, Rect, SuiteChant, SuiteEpisode, SuiteLecture } from './types';
import type { Chrono, HorlogeLissee } from './horloge';

/** Contexte d'un lecteur : état partagé et fonctions que les modules s'échangent. */
export interface Lecteur {
  racine: HTMLElement;
  // etat
  D: Donnees;
  $: <T extends HTMLElement = HTMLElement>(s: string) => T;
  lecteur: HTMLElement;
  scene: HTMLElement;
  calques: HTMLElement[];
  audio: HTMLAudioElement;
  sa: HTMLAudioElement;
  elActe: HTMLElement;
  elLegende: HTMLElement;
  elSt: HTMLElement;
  elMusique: HTMLElement;
  elClipTexte: HTMLElement;
  elActeTitre: HTMLElement;
  elActeDates: HTMLElement;
  elCarton: HTMLElement;
  elCartonTitre: HTMLElement;
  elCartonDates: HTMLElement;
  elN: HTMLElement;
  elEcoule: HTMLElement;
  depart: HTMLElement;
  btnReprendre: HTMLButtonElement;
  btnLecture: HTMLButtonElement;
  btnSt: HTMLButtonElement;
  btnPe: HTMLButtonElement;
  btnMusique: HTMLButtonElement | null;
  curseurVolume: HTMLInputElement | null;
  segments: HTMLButtonElement[];
  CLE_POS: string;
  VOLET_S: number;
  MOSAIQUE_T: { apparition: number; pas: number; fondu: number; tenue: number; };
  debutPlongee: (n: number) => number;
  N: number;
  acteDe: number[];
  prelude: number[];
  voixEtPause: number[];
  suiteEtPause: number[];
  debuts: number[];
  total: number;
  genOuverture: number;
  genFin: number;
  bornes: { de: number; fin: number; t0: number; t1: number; }[];
  horloge: HorlogeLissee;
  horlogeSuite: HorlogeLissee;
  i: number;
  lance: boolean;
  joue: boolean;
  visible: number;
  sortant: number;
  minuterie: number;
  debutSansVoix: number;
  ecouleSansVoix: number;
  couches: { x: Diapo | null; r: Rect; ra?: Rect | null | undefined; tp?: number; tg?: number; }[];
  enCarton: boolean;
  chronoCarton: Chrono;
  ouvre: boolean;
  tempsOuverture: () => number;
  enEntree: boolean;
  chronoEntree: Chrono;
  entreeNette: boolean;
  quandPrete: (img: HTMLImageElement, fn: () => void) => void;
  enSuite: boolean;
  suiteFini: boolean;
  // camera
  cadre: (c: HTMLElement, x: Diapo) => void;
  basCotes: { gauche: number; droite: number; };
  hautBrut: number;
  majBasSurimpressions: () => void;
  mesurerMarges: () => void;
  transformation: (c: HTMLElement, x: Diapo, r: Rect, f?: number, img?: HTMLImageElement) => string;
  css: (p: { tx: number; ty: number; s: number; }) => string;
  parametres: (W: number, H: number, IW: number, IH: number, u: Rect, r: Rect, f?: number, entier?: boolean) => { tx: number; ty: number; s: number; };
  vue: (x: Diapo, r: Rect) => Rect;
  plan: (x: Diapo) => { v: Rect; c: Rect; t: number; de: number; a: number; }[];
  cadreA: (x: Diapo, t: number) => Rect;
  cadreIntermede: (x: Diapo, c: SuiteChant & { cadre: Rect; }, ts: number) => Rect;
  // avant-apres
  avantDe: (x: Diapo) => Diapo;
  apresDe: (x: Diapo) => Diapo;
  majApres: (c: HTMLElement, x: Diapo, t: number) => void;
  // mosaique
  plongee: (x: Diapo) => { C: Rect[]; k: number; c: Rect; sigma: number; B: { tx: number; ty: number; s: number; }; G: { tx: number; ty: number; s: number; }; W: number; H: number; IW: number; IH: number; t0: number; d: number; m: number; a0: number; cx: number; cy: number; };
  principal: (x: Diapo) => Diapo;
  placerTuiles: (c: HTMLElement, x: Diapo) => void;
  majMosaique: (c: HTMLElement, x: Diapo, t: number) => void;
  // plans
  galerieDe: (x: Diapo) => Plan[] | null;
  planDe: (x: Diapo, p: Plan, fin: number) => Diapo;
  preparerPlans: (c: HTMLElement, x: Diapo) => void;
  taillerPlans: (c: HTMLElement, x: Diapo) => void;
  majPlans: (c: HTMLElement, x: Diapo, t: number, gris?: number) => number;
  majGalerie: (c: HTMLElement, x: Diapo, ts?: number) => number;
  poserPlans: (k: number) => void;
  legendeGalerie: (x: Diapo, k: number) => string | null;
  // mouvement
  preparerVideo: (c: HTMLElement, x: Diapo) => void;
  taillerVideo: (c: HTMLElement, x: Diapo) => void;
  majVideo: (c: HTMLElement, x: Diapo, transformation: string, t: number, entree: boolean) => void;
  poserVideo: (c: HTMLElement, transformation: string) => void;
  arreterVideo: (c: HTMLElement) => void;
  prechargerVideo: (x: Diapo) => void;
  debutClip: (x: Diapo) => number;
  // ambiance
  majAmbiance: (x: Diapo | null, t: number, entree: boolean) => void;
  arreterAmbiance: () => void;
  prechargerAmbiance: (x: Diapo) => void;
  amorcerAmbiance: () => void;
  // couleur
  preparerCouleur: (c: HTMLElement, x: Diapo) => void;
  majCouleur: (c: HTMLElement, x: Diapo, transformation: string, t: number, filtre: string) => number;
  poserCouleur: (c: HTMLElement, x: Diapo, transformation: string) => void;
  opaciteCouleur: (xv: Diapo, a: number, b: number, t: number) => number;
  teinter: (el: HTMLImageElement, base: HTMLImageElement, coul: Couleur, transformation: string, o: number, filtre: string) => number;
  marquerCouleur: (o: number) => void;
  prechargerCouleur: (x: Diapo) => void;
  // fond prolongé des images entières (spec 17)
  preparerFond: (c: HTMLElement, x: Diapo) => void;
  majFond: (c: HTMLElement, x: Diapo, transformation: string, gris?: number) => void;
  placerFond: (el: HTMLElement, base: HTMLImageElement, fond: Fond, u: Rect, transformation: string, gris?: number) => void;
  creerFond: (fond: Fond) => HTMLElement;
  prechargerFond: (x: Diapo) => void;
  // dessins traversants sous les images entières (spec 17, essai 5)
  creerVignette: (k?: number) => HTMLElement;
  preparerVignette: (c: HTMLElement, x: Diapo) => void;
  majVignette: (c: HTMLElement, x: Diapo, t: number) => number;
  marquerVignette: (o: number) => void;
  prechargerVignette: (x: Diapo) => void;
  // rendu
  legendeVoulue: (x: Diapo, t: number) => string;
  legendeMontree: string;
  instant: () => number;
  poser: (k: number) => void;
  rendre: (t?: number) => void;
  raf: number;
  animer: () => void;
  assurerFin: () => void;
  montrerImage: (x: Diapo, fondu: boolean, couvert?: boolean) => void;
  // frise
  friseCarton: HTMLElement | null;
  derniere: number;
  changeFrise: (de: DateFrise, a: DateFrise) => boolean;
  poserActe: (f: HTMLElement, k: number) => void;
  majFriseCarton: (t?: number) => void;
  cacherFrise: () => void;
  majPoussee: () => void;
  montrerFrise: (de: DateFrise, a: DateFrise) => void;
  ajusterFrises: () => void;
  // textes
  estomperPlusTard: (el: HTMLElement, delai?: number) => void;
  revelerCartouches: () => void;
  changerCartouche: (x: Diapo) => void;
  changerLegende: (html: string) => void;
  changerSousTitre: (texte: string) => void;
  // incrustations
  elLieu: HTMLElement | null;
  elPlan: HTMLElement | null;
  elMots: HTMLElement | null;
  elPortraits: HTMLElement | null;
  portraitsEls: HTMLElement[];
  portraitsEtat: string;
  motsEls: HTMLElement[][];
  motsDits: number;
  tailleLieu: () => void;
  taillePortraits: () => void;
  elObjet: HTMLElement | null;
  elManuscrit: HTMLElement | null;
  msHalo: HTMLElement | null;
  msEtat: string;
  tailleObjet: () => void;
  tailleManuscrit: () => void;
  majManuscrit: (t: number) => void;
  elChiffre: HTMLElement | null;
  elDate: HTMLElement | null;
  tailleChiffre: () => void;
  chiffreTexte: string;
  majChiffre: (t: number) => void;
  // surimpressions
  chargerSurimpressions: (x: Diapo | null) => void;
  majSurimpressions: (t: number) => void;
  // progression
  tempsCourant: () => number;
  majTemps: () => void;
  precharger: (k: number) => void;
  // cartons
  lancerCarton: () => void;
  passerCarton: () => void;
  retablirWillChange: () => void;
  finirVolets: () => void;
  majVolets: () => void;
  // segments
  ov: HTMLElement | null;
  lancerSuite: () => void;
  finSuite: () => void;
  arreterSuite: (garderCarte?: boolean) => void;
  majSuite: () => void;
  // chant
  preparerClip: (c: SuiteChant) => void;
  majParoles: () => void;
  // lectures
  etats: WeakMap<HTMLElement, EtatSegment>;
  preparer: (el: HTMLElement, c: SuiteLecture | SuiteEpisode) => void;
  majCitation: (el: HTMLElement, c: SuiteLecture, t: number) => void;
  // episodes
  majEpisode: (el: HTMLElement, c: SuiteEpisode, t: number) => void;
  // navigation
  arreterMinuterie: () => void;
  entrerImage: (fondu: boolean, couvert?: boolean) => void;
  demarrer: () => void;
  allerSuite: (j: number) => void;
  suivantAuto: () => void;
  lancer: (k?: number) => void;
  basculer: () => void;
  aller: (k: number) => void;
  suivant: () => void;
  pause: () => void;
  // musique
  deverrouillerAudio: () => void;
  appliquerEtat: () => void;
  musique: () => void;
  basculerMusique: (oui?: boolean) => void;
  // generique
  enGenerique: 'ouverture' | 'fin' | null;
  ouvrirGenerique: (k: number) => boolean;
  lancerRecapitulatif: () => boolean;
  reprendreGenerique: () => void;
  figerGenerique: () => void;
  passerGenerique: () => void;
  quitterGenerique: () => void;
  tempsGenerique: () => number | null;
  // controles
  montrerControles: () => void;
}
