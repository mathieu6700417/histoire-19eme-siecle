// Registre des siècles du site « Histoire de France » (spec 18).
// Ajouter un siècle = ajouter une entrée ici, puis ranger ses contenus sous son identifiant :
// src/content/lecons/<id>/, src/content/ecrivains/<id>/, src/data/diaporamas/<id>/,
// public/<id>/diaporamas/… Seuls les siècles déclarés apparaissent sur le site.
import type { ChapitrePrevu } from './types';
import { chapitresPrevus as chapitresXixe } from './xixe/chapitres-ecrivains';

/** Sections facultatives d'un siècle (les leçons existent toujours). */
export type Section = 'lecons' | 'ecrivains' | 'images';

export interface Siecle {
  /** Identifiant, premier segment des adresses (« xixe » → /xixe/). */
  id: string;
  /** Chiffre romain en minuscules, affiché en petites capitales (« xix »). */
  romain: string;
  /** Libellé en texte brut, pour les titres d'onglet (« XIXe siècle »). */
  libelle: string;
  /** Bornes de la période traitée (un siècle peut déborder ses bornes calendaires). */
  debut: number;
  fin: number;
  /** Chapeau d'une ou deux phrases (sommaire des siècles, accueil du siècle). */
  chapeau: string;
  /** Présentation complémentaire sur l'accueil du siècle. */
  presentation?: string;
  /** Sections disponibles, dans l'ordre de la navigation. */
  sections: Section[];
  /** Plan des chapitres de la section « écrivains », repris par la section « images »
   *  (une période de diaporama par chapitre). */
  chapitres?: ChapitrePrevu[];
}

const declares: Siecle[] = [
  {
    id: 'xixe',
    romain: 'xix',
    libelle: 'XIXe siècle',
    debut: 1789,
    fin: 1900,
    chapeau:
      "De la prise de la Bastille à l'Exposition universelle de 1900, la France connaît trois monarchies, deux empires et trois républiques, et invente les grandes familles politiques, les révolutions industrielles et la société que nous connaissons encore.",
    presentation:
      "Ce site propose des leçons courtes et illustrées, de niveau lycée, pour se repérer dans ce siècle foisonnant : chaque terme technique y est expliqué, chaque date vérifiée. De nouvelles leçons s'ajoutent au fil du temps.",
    sections: ['lecons', 'ecrivains', 'images'],
    chapitres: chapitresXixe,
  },
];

/** Les siècles déclarés, dans l'ordre chronologique. */
export const siecles: Siecle[] = [...declares].sort((a, b) => a.debut - b.debut);

export const NOM_SITE = 'Histoire de France';

export function siecle(id: string): Siecle {
  const s = siecles.find((x) => x.id === id);
  if (!s) throw new Error(`Siècle inconnu : ${id} (voir src/data/siecles.ts)`);
  return s;
}

export const aSection = (s: Siecle | string, section: Section) =>
  (typeof s === 'string' ? siecle(s) : s).sections.includes(section);

/** Siècles qui possèdent une section (pour les getStaticPaths des pages de section). */
export const sieclesAvec = (section: Section) => siecles.filter((s) => s.sections.includes(section));
