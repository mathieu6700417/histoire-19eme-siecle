// Outils pour les leçons, rangées par siècle (src/content/lecons/<siecle>/…, spec 18).
// L'id d'une entrée commence par son siècle (« xixe/courants-politiques ») ; dans le siècle,
// une entrée dont le chemin contient un « / » est une sous-page, et son parent est le
// segment avant le « / » (ex. xixe/courants-politiques/legitimistes).
import { decouperId, urlLecon } from './adresses';

interface AvecId { id: string; data: { ordre: number } }

export const siecleDeLecon = (id: string) => decouperId(id).siecle;
const cheminDe = (id: string) => decouperId(id).chemin;

export const estSousPage = (id: string) => cheminDe(id).includes('/');

/** Id complet du parent d'une sous-page (« xixe/courants-politiques »). */
export const parentDe = (id: string): string | undefined => {
  const { siecle, chemin } = decouperId(id);
  return chemin.includes('/') ? `${siecle}/${chemin.slice(0, chemin.indexOf('/'))}` : undefined;
};

export const parOrdre = <T extends AvecId>(a: T, b: T) => a.data.ordre - b.data.ordre;

/** Leçons (et sous-pages) d'un siècle. */
export const leconsDuSiecle = <T extends AvecId>(lecons: T[], siecle: string): T[] =>
  lecons.filter((l) => siecleDeLecon(l.id) === siecle);

/** Sous-pages directes d'une leçon, triées par `ordre`. */
export const enfantsDe = <T extends AvecId>(lecons: T[], id: string): T[] =>
  lecons.filter((l) => parentDe(l.id) === id).sort(parOrdre);

/** Leçons de premier niveau, triées par `ordre`. */
export const premierNiveau = <T extends AvecId>(lecons: T[]): T[] =>
  lecons.filter((l) => !estSousPage(l.id)).sort(parOrdre);

/** Adresse d'une leçon ou d'une sous-page (d'après son id complet). */
export const lienLecon = (id: string) => {
  const { siecle, chemin } = decouperId(id);
  return urlLecon(siecle, chemin);
};

/** Chemin de la leçon dans son siècle (paramètre de page). */
export const cheminLecon = cheminDe;

/** Titre court pour le fil d'Ariane : retire une période finale (« , 1789-1900 »). */
export const titreCourt = (titre: string) => titre.replace(/,\s*\d{4}\s*[-–]\s*\d{4}$/, '');
