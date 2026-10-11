// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { satteri } from '@astrojs/markdown-satteri';
import { pluginTypographie } from './src/utils/plugin-typographie.mjs';

// https://astro.build/config
export default defineConfig({
  site: 'https://histoire-19eme-siecle.mathieu6700417.workers.dev',
  integrations: [mdx()],
  // Annotations de visionnage (spec 15) : outil local, embarqué seulement par `npm run annoter`
  // (ANNOTATIONS=1). Sans la variable, la condition est fausse et le module est éliminé du build.
  vite: { define: { __ANNOTATIONS__: JSON.stringify(process.env.ANNOTATIONS === '1') } },
  markdown: {
    // Typographie française appliquée à tout le texte Markdown/MDX
    // (espaces insécables, apostrophes courbes).
    processor: satteri({ mdastPlugins: [pluginTypographie] }),
  },
});
