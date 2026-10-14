// Adresses du site (spec 18) : toutes les URL internes sont construites ici, à partir du
// siècle. Aucune page ni composant n'écrit d'adresse à la main.
//   /                                   sommaire des siècles
//   /<siecle>/                          accueil du siècle (#lecons : liste des leçons)
//   /<siecle>/lecons/<slug>/[<sous>/]   leçon, sous-page (figures du siècle : lecons/figures/<slug>/)
//   /<siecle>/ecrivains/[<chapitre>/]   section « écrivains », /auteurs/ : index des auteurs
//   /<siecle>/diaporamas/[<slug>/]      section « images » ; médias dans le même dossier
//                                       (public/<siecle>/diaporamas/<slug>/…)
import { siecles } from '../data/siecles';

const base = import.meta.env.BASE_URL;

export const urlSommaire = base;
export const urlSiecle = (siecle: string) => `${base}${siecle}/`;
export const urlLecons = (siecle: string) => `${urlSiecle(siecle)}#lecons`;
export const urlTheme = (siecle: string, theme: string) => `${urlSiecle(siecle)}#theme-${theme}`;
/** `chemin` : chemin de la leçon dans son siècle (« courants-politiques/legitimistes »). */
export const urlLecon = (siecle: string, chemin: string) => `${urlSiecle(siecle)}lecons/${chemin}/`;
/** Portrait de la leçon « Figures du siècle » (sous-page `figures/<slug>`, spec 19). */
export const urlFigure = (siecle: string, slug: string) => urlLecon(siecle, `figures/${slug}`);
export const urlEcrivains = (siecle: string) => `${urlSiecle(siecle)}ecrivains/`;
export const urlAuteurs = (siecle: string) => `${urlEcrivains(siecle)}auteurs/`;
export const urlChapitreEcrivains = (siecle: string, slug: string) => `${urlEcrivains(siecle)}${slug}/`;
export const urlDiaporamas = (siecle: string) => `${urlSiecle(siecle)}diaporamas/`;
export const urlDiaporama = (siecle: string, slug: string) => `${urlDiaporamas(siecle)}${slug}/`;
/** Fichier servi depuis public/<siecle>/diaporamas/ (« portraits/x.webp », « revolution/001.webp »). */
export const urlMediaDiaporamas = (siecle: string, chemin: string) => `${urlDiaporamas(siecle)}${chemin}`;

/** Siècle d'une adresse de page (premier segment après la base), ou undefined (sommaire, 404). */
export function siecleDeChemin(chemin: string): string | undefined {
  const reste = chemin.startsWith(base) ? chemin.slice(base.length) : chemin.replace(/^\//, '');
  const premier = reste.split('/')[0];
  return siecles.some((s) => s.id === premier) ? premier : undefined;
}

/** Identifiant d'une entrée de collection rangée par siècle (« xixe/courants-politiques ») :
 *  le siècle (premier segment) et le chemin dans le siècle. */
export function decouperId(id: string): { siecle: string; chemin: string } {
  const i = id.indexOf('/');
  if (i < 0) throw new Error(`Entrée hors d'un dossier de siècle : ${id}`);
  return { siecle: id.slice(0, i), chemin: id.slice(i + 1) };
}
