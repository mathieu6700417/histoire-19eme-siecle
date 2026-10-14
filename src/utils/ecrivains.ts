// Outils partagés par les pages de la section « Le siècle raconté par ses écrivains ».
// Les chapitres sont rangés par siècle (src/content/ecrivains/<siecle>/NN-<slug>.mdx, spec 18) ;
// le plan des chapitres prévus est déclaré dans le registre des siècles.
import { getCollection, type CollectionEntry } from 'astro:content';
import { siecle as trouverSiecle } from '../data/siecles';
import { decouperId, urlAuteurs, urlChapitreEcrivains, urlEcrivains } from './adresses';

export type Chapitre = CollectionEntry<'ecrivains'>;

export const urlSection = (siecle: string) => urlEcrivains(siecle);
export { urlAuteurs };
export const siecleDeChapitre = (c: Chapitre) => decouperId(c.id).siecle;
/** Slug du chapitre dans son siècle (« 01-revolution »). */
export const slugChapitre = (c: Chapitre) => decouperId(c.id).chemin;
export const urlChapitre = (c: Chapitre) => urlChapitreEcrivains(siecleDeChapitre(c), slugChapitre(c));

/** Libellé court d'un chapitre : « Prologue » pour le numéro 0, « Chapitre N » sinon. */
export const libelleChapitre = (numero: number) => (numero === 0 ? 'Prologue' : `Chapitre ${numero}`);

/** Plan des chapitres prévus d'un siècle (vide s'il n'a pas de section « écrivains »). */
export const chapitresPrevus = (siecle: string) => trouverSiecle(siecle).chapitres ?? [];

export async function chapitresEcrits(siecle: string): Promise<Chapitre[]> {
  return (await getCollection('ecrivains'))
    .filter((c) => siecleDeChapitre(c) === siecle)
    .sort((a, b) => a.data.numero - b.data.numero);
}

/** Les chapitres prévus du siècle, avec le chapitre écrit correspondant s'il existe. */
export async function planComplet(siecle: string) {
  const ecrits = await chapitresEcrits(siecle);
  return chapitresPrevus(siecle).map((p) => ({ ...p, chapitre: ecrits.find((c) => c.data.numero === p.numero) }));
}

/**
 * Identifiants des auteurs cités dans un chapitre, dans l'ordre de
 * première apparition (lu dans le source MDX : attribut auteur="…" des <Extrait>).
 */
export function auteursCites(c: Chapitre): string[] {
  const ids: string[] = [];
  for (const m of (c.body ?? '').matchAll(/<Extrait\b[^>]*?\bauteur="([^"]+)"/g)) {
    if (!ids.includes(m[1])) ids.push(m[1]);
  }
  return ids;
}
