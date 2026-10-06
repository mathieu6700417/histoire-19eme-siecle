// Outils partagés par les pages de la section « Le siècle raconté par ses écrivains ».
import { getCollection, type CollectionEntry } from 'astro:content';
import { chapitresPrevus } from '../data/chapitres-ecrivains';

export type Chapitre = CollectionEntry<'ecrivains'>;

const base = import.meta.env.BASE_URL;

export const urlSection = `${base}ecrivains/`;
export const urlAuteurs = `${base}ecrivains/auteurs/`;
export const urlChapitre = (c: Chapitre) => `${base}ecrivains/${c.id}/`;

export async function chapitresEcrits(): Promise<Chapitre[]> {
  return (await getCollection('ecrivains')).sort((a, b) => a.data.numero - b.data.numero);
}

/** Les 8 chapitres prévus, avec le chapitre écrit correspondant s'il existe. */
export async function planComplet() {
  const ecrits = await chapitresEcrits();
  return chapitresPrevus.map((p) => ({ ...p, chapitre: ecrits.find((c) => c.data.numero === p.numero) }));
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
