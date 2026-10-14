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
