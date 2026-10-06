// Outils pour les leçons à sous-pages.
// Une entrée dont l'id contient un « / » est une sous-page ; son parent
// est le segment avant le « / » (ex. courants-politiques/legitimistes).

interface AvecId { id: string; data: { ordre: number } }

export const estSousPage = (id: string) => id.includes('/');

export const parentDe = (id: string): string | undefined =>
  estSousPage(id) ? id.slice(0, id.indexOf('/')) : undefined;

export const parOrdre = <T extends AvecId>(a: T, b: T) => a.data.ordre - b.data.ordre;

/** Sous-pages directes d'une leçon, triées par `ordre`. */
export const enfantsDe = <T extends AvecId>(lecons: T[], id: string): T[] =>
  lecons.filter((l) => parentDe(l.id) === id).sort(parOrdre);

/** Leçons de premier niveau, triées par `ordre`. */
export const premierNiveau = <T extends AvecId>(lecons: T[]): T[] =>
  lecons.filter((l) => !estSousPage(l.id)).sort(parOrdre);

/** Adresse d'une leçon ou d'une sous-page. */
export const lienLecon = (id: string) => `${import.meta.env.BASE_URL}lecons/${id}/`;

/** Titre court pour le fil d'Ariane : retire une période finale (« , 1789-1900 »). */
export const titreCourt = (titre: string) => titre.replace(/,\s*\d{4}\s*[-–]\s*\d{4}$/, '');
