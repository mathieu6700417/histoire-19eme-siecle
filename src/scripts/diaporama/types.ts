// Types des données du lecteur (JSON embarqué par Diaporama.astro, voir src/utils/diaporamas.ts) :
// diapositive, suites (chant, lecture, épisode), frise, données d'un segment affiché.
export type Rect = [number, number, number, number];
export interface Diapo {
  /** `u` : zone utile (fractions de l'image) ; `l` × `h` : ses dimensions (px). Les cadres de la
   *  caméra, l'ouverture et le cadre d'un intermède sont en fractions de la zone utile. */
  n: number; cle: string; img: string; g?: string; u: Rect; l: number; h: number; alt: string; legende: string; texte: string;
  audio: string; duree: number; pause: number; camera: { c: Rect; t: number }[];
  /** Détail zoomé sur lequel s'ouvre le carton d'acte (spec 12, « Sortie du carton d'acte »). */
  ouv: Rect | null;
  /** Entrée en scène (spec 12, « Entrée en scène des grandes vues ») : cadres de départ `c` (un ou
   *  deux, fractions de la zone utile) parcourus avant d'arriver à la première vue, en `d` s. */
  ent?: Entree | null;
  /** Avant / après (point 3) : image après (zone utile, dimensions), cartouche, instant du volet,
   *  étapes de la caméra sur l'image après (la première : cadre de raccord, à l'instant du volet). */
  ap: { img: string; u: Rect; l: number; h: number; alt: string; legende: string; t: number; camera: { c: Rect; t: number }[] } | null;
  /** Mosaïque (point 5) : cartouche de la grille, rang de l'image principale, vignettes (`c` : visage
   *  principal, fractions de l'image, sur lequel la case est centrée ; null : centre de la zone utile). */
  mos: { legende: string; principale: number; vignettes: { img: string; u: Rect; l: number; h: number; c: Rect | null }[] } | null;
  /** Caméra (usage interne, vues dérivées) : instant et fin de la première tenue (`t0`, `a0`),
   *  et vue de départ imposée (`v0`). */
  t0?: number; a0?: number; v0?: Rect;
  /** Image entière sur fond noir (spec 12, « Retours du visionnage de la Restauration ») : l'image
   *  est montrée en entier, bandes noires de côté, puis la caméra s'approche lentement du sujet
   *  `v` (fractions de la zone utile ; null : centre), jusqu'au zoom `z` au plus. */
  en?: Entier | null;
  /** Frise : jours (depuis 1970) du premier et du dernier jour daté, positions en %, libellé. */
  date: DateFrise | null;
  /** Plans (spec 14) : images suivantes de la diapositive, chacune à son instant de la voix. */
  plans?: Plan[] | null;
  /** Mise en mouvement par IA (spec 16) : clip muet de 10 s joué une fois (dernière image tenue), aux
   *  proportions de la zone utile, posé sur elle avec la transformation de l'image (mouvement.ts). */
  video?: { src: string; duree: number } | null;
  /** Ambiance sonore du clip (spec 17) : fichier et durée (s). */
  amb?: { src: string; duree: number } | null;
  /** Colorisation par IA (spec 16) : version colorisée de l'image, posée sur sa zone utile après un
   *  fondu lent (couleur.ts). */
  coul?: Couleur | null;
  /** Fond prolongé de l'image entière (spec 17) : posé sous elle, flouté, même transformation (fond.ts). */
  fond?: Fond | null;
  /** Segment joué après la voix (et sa pause) : intermède chanté, lecture ou épisode. */
  suite: Suite | null;
  /** Carte de lieu : fenêtre [a, b) (s de l'audio), point (%) dans le fond, partie du plan de
   *  Paris montrée (`vue` : taille ; position du fond CSS). */
  lieu: { a: number; b: number; nom: string; fond: string; x: number; y: number; ratio: number; vue?: string; credit?: string; points?: unknown[] } | null;
  /** Citation : fenêtre [a, b), début de chaque mot, fin du dernier, HTML des mots, auteur. */
  citation: { a: number; b: number; fin: number; mots: number[]; html: string; auteur: string } | null;
  /** Portraits des personnes nommées : fenêtre [a, b) de la rangée, et pour chaque personne
   *  (4 au plus) son nom, ses dates, l'image et l'instant où l'ovale paraît. */
  portraits: { a: number; b: number; gens: { id: string; nom: string; dates: string; src: string; t: number }[] } | null;
  /** Objet de musée détouré (coin bas `cote`) : fenêtre [a, b), image, proportions, légende. */
  objet: Objet | null;
  /** Manuscrit (côté `cote`) : même chose, plus le halo [x0, y0, x1, y1] (fractions de l'image). */
  manuscrit: (Objet & { halo: Rect }) | null;
  /** Chiffre clé (point 4) : fenêtre [a, b), valeur, texte final, prudence, unité, défilement. */
  chiffre: { a: number; b: number; valeur: number; texte: string; prefixe: string; unite: string; defile: boolean } | null;
  /** Date républicaine et sa correspondance grégorienne : fenêtre [a, b). */
  dateRep: { a: number; b: number; republicain: string; gregorien: string } | null;
}
/** Image d'une série (spec 14 : plan d'une diapositive, image d'une galerie ou d'une lecture) :
 *  zone utile, dimensions, cartouche, instant `t` (s de la voix ou du segment) où elle paraît en
 *  fondu croisé, étapes de la caméra (fractions de la zone utile, instants de la même horloge). */
/** Version colorisée d'une image : `u` = rectangle qu'elle recouvre (fractions de l'image servie :
 *  la zone utile arrondie au pixel, comme à la fabrication). */
export interface Couleur { src: string; u: Rect }
/** Fond prolongé d'une image entière (spec 17, fond.ts) : `b` = boîte de l'image dans le fichier de
 *  fond (fractions du fond) ; `fort` : flou fort (le fond net montre une invention à cacher). */
export interface Fond { src: string; b: Rect; fort: boolean }
export interface Entier { v: Rect | null; z: number }
export interface Entree { c: Rect[]; d: number }
export interface Plan { img: string; g?: string; u: Rect; l: number; h: number; alt: string; legende: string; t: number; camera: { c: Rect; t: number }[]; en?: Entier | null; ent?: Entree | null; coul?: Couleur | null; fond?: Fond | null }
export interface Objet { a: number; b: number; src: string; ratio: number; nom: string; legende: string; cote: 'gauche' | 'droite' }
/** Intermède chanté : paroles [instant, vers, début de chaque mot (`motsLus`) ou null : vers
 *  entier à son début]. */
export interface SuiteChant { type: 'chant'; src: string; duree: number; legende: string; paroles: [number, string, number[] | null][]; instrumental: boolean; cadre: Rect | null;
  /** Galerie (spec 14) : images montrées pendant l'extrait (instants du segment). */
  galerie?: Plan[] | null }
/** Lecture d'époque : instant de début de chaque mot (alignement forcé, ou prorata) et, pour
 *  chaque phrase, [début (s), premier mot, mot suivant le dernier]. */
export interface SuiteLecture { type: 'lecture'; id: string; src: string; duree: number; mots: number[]; phrases: [number, number, number][]; date: DateFrise | null;
  /** Lecture illustrée (spec 14) : images de fond derrière la carte (instants du segment). */
  images?: Plan[] | null }
/** Épisode : phrases [début, fin (s), texte du sous-titre]. */
export interface SuiteEpisode { type: 'episode'; id: string; src: string; duree: number; phrases: [number, number, string][]; date: DateFrise | null }
export type Suite = SuiteChant | SuiteLecture | SuiteEpisode;
export interface Piste { src: string; duree: number; volume: number; info: string }
export interface DateFrise { j0: number; j1: number; x0: number; x1: number; libelle: string }
export interface Donnees {
  slug: string; pause: number; carton: number; volet: number;
  mosaique: { apparition: number; pas: number; fondu: number; tenue: number };
  actes: { titre: string; dates: string; debut: number }[]; diapos: Diapo[];
  /** Musique de fond : les pistes de chaque acte. */
  fond: Piste[][];
  /** Générique d'ouverture et récapitulatif de fin (generique.ts) ; null sans `generique`. */
  generique: Generique | null;
}
/** Générique : images de la mosaïque (k : rang dans la liste, les copies d'une rangée le
 *  partagent), extraits de l'indicatif commun. */
export interface Generique {
  ouverture: { src: string; duree: number };
  /** `accord` : instant de l'accord final, où paraît « Fin ». */
  fin: { src: string; duree: number; accord: number };
  images: number;
}

// Éléments de chaque carte et panneau, relevés une fois (à leur premier affichage).
export interface Anim { el: Element & ElementCSSInlineStyle; t: number; d: number; p: number }
export interface EtatSegment {
  mots?: HTMLElement[][]; zone?: HTMLElement; defile?: HTMLElement; lu?: number; cour?: number; y?: number; hz?: number;
  ev?: { el: HTMLElement; t: number }[]; anims?: Anim[]; actif?: number; phrase?: number;
  traces?: { el: SVGRectElement; l: number; trace: [number, number][]; x: number }[];
  docs?: { el: HTMLElement; page: HTMLElement; l: number; h: number; vues: number[][] }[];
}
