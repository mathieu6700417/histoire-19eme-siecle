import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

export const THEMES = ['politique', 'societe', 'economie', 'culture', 'international', 'sciences'] as const;

// Contenus rangés par siècle (spec 18) : src/content/lecons/<siecle>/<slug>.mdx, sous-pages dans
// <siecle>/<slug>/<sous>.mdx. L'id commence par le siècle (« xixe/courants-politiques ») ; les
// adresses se calculent dans src/utils/adresses.ts.
const lecons = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/lecons' }),
  schema: z.object({
    titre: z.string(),
    theme: z.enum(THEMES),
    resume: z.string(),
    ordre: z.number(),
    periode: z.string(),
    dureeLecture: z.number().int().positive().optional(),
    // id d'un courant de src/data/xixe/courants-politiques.ts (couleur d'accent, sous-pages).
    courant: z.string().optional(),
  }),
});

// Section « Le siècle raconté par ses écrivains » : un fichier par chapitre,
// nommé <siecle>/NN-<slug>.mdx (ex. xixe/01-revolution.mdx).
const ecrivains = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/ecrivains' }),
  schema: z.object({
    titre: z.string(),
    numero: z.number().int().min(0).max(8),
    periode: z.string(),
    resume: z.string(),
    dureeLecture: z.number().int().positive(),
  }),
});

export const collections = { lecons, ecrivains };
