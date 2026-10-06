import { typographie } from './typographie.mjs';

// Plugin mdast pour Sätteri (processeur Markdown par défaut d'Astro) :
// corrige la typographie française des nœuds de texte, jamais du code
// ni des attributs JSX.
export const pluginTypographie = {
  name: 'typographie-francaise',
  /** @param {any} noeud @param {any} ctx */
  text(noeud, ctx) {
    const corrige = typographie(noeud.value);
    if (corrige !== noeud.value) ctx.setProperty(noeud, 'value', corrige);
  },
};
