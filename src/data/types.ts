// Types partagés par les composants Frise et Arbre (réutilisables
// d'une leçon à l'autre).

export type Statut = 'existe' | 'pouvoir' | 'declin';

export interface Repere {
  annee: number;
  libelle: string;
}

/** Bande de fond (régime, période) affichée au-dessus de la frise. */
export interface Periode {
  debut: number;
  fin: number;
  libelle: string;
  /** Libellé court utilisé si le libellé complet ne tient pas. */
  court?: string;
}

export interface Segment {
  debut: number;
  fin: number;
  statut: Statut;
  libelle: string;
}

export interface LigneFrise {
  nom: string;
  couleur: string;
  /** Identifiant de la ligne (sert aussi d'ancre par défaut, sans #). */
  id: string;
  /** Adresse vers laquelle pointe le nom (par défaut : #id). */
  lien?: string;
  segments: Segment[];
}

export interface NoeudArbre {
  id: string;
  libelle: string;
  /** Année de naissance du courant : bord gauche du nœud. */
  annee: number;
  /** Rangée (0 = en haut). */
  rangee: number;
  couleur: string;
  /** Texte de l'infobulle. */
  detail: string;
  /** Lien facultatif : adresse (« /… ») ou ancre (« #… » ou id seul). */
  lien?: string;
}

export interface AreteArbre {
  de: string;
  vers: string;
  type: 'filiation' | 'scission';
}

/** Chapitre prévu de la section « écrivains » d'un siècle (son plan sert aussi aux diaporamas). */
export interface ChapitrePrevu {
  numero: number;
  titre: string;
  periode: string;
}

/** Bande d'une frise de récit (FriseJournees) : régime ou partie, dates ISO (« 1789-06-17 »). */
export interface BandeFrise {
  debut: string;
  fin: string;
  libelle: string;
  /** Libellé court utilisé si le libellé complet ne tient pas. */
  court?: string;
  /** Remplissage monochrome : 0 uni clair, 1 hachures, 2 points, 3 uni moyen. */
  motif?: 0 | 1 | 2 | 3;
  /** Ancre (« #… ») ou adresse vers laquelle mène la bande. */
  lien?: string;
  /** Dates affichées dans le détail (par défaut : années de début et de fin). */
  dates?: string;
}

/** Tranche d'une frise à échelle par segments (FriseJournees, spec 21) : années debut → fin
 *  (fin exclue), largeur d'une année en px, pas des graduations (1 : chaque année). */
export interface TrancheFrise {
  debut: number;
  fin: number;
  pxParAn: number;
  pas?: number;
  /** Description de l'échelle (infobulle de l'axe : « un siècle pour 150 px »). */
  libelle?: string;
}

/** Repère daté d'une frise de récit (FriseJournees) : une grande journée. */
export interface JourneeFrise {
  /** Date ISO (« 1789-07-14 »). */
  date: string;
  /** Libellé affiché sur la frise (un ou deux mots). */
  court: string;
  /** Libellé complet (infobulle, ligne de détail). */
  libelle: string;
  lien?: string;
}

// --- Carte de France (CarteFrance, spec 21) ---

export type MotifZone = 'blanc' | 'clair' | 'moyen' | 'fonce' | 'hachures' | 'points' | 'hors';

/** Fond projeté produit par un script de scripts/cartes/ (chemins SVG, projection). */
export interface FondCarte {
  source: string;
  projection: { cadre: number[]; echelle: number; cx: number };
  largeur: number;
  hauteur: number;
  voisins: string;
  france: string;
  fleuves?: string;
  zones: Record<string, string>;
}

export interface ZoneCarte {
  libelle: string;
  motif: MotifZone;
  /** Texte du détail (survol). */
  detail?: string;
}

export interface LieuCarte {
  id: string;
  nom: string;
  lon: number;
  lat: number;
  /** Repère principal (cercle plein), secondaire (cercle vide), autre (carré vide), hors (croix). */
  type: 'principal' | 'secondaire' | 'autre' | 'hors';
  /** Seconde ligne du libellé (date de création…). */
  date?: string;
  detail?: string;
  /** Position du libellé autour du point (défaut : est). */
  position?: 'n' | 's' | 'e' | 'o' | 'ne' | 'no' | 'se' | 'so';
  /** Lien (ancre ou adresse). */
  lien?: string;
  /** Affiché dans la liste sous la carte. */
  liste?: boolean;
}
