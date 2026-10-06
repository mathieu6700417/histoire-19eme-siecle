// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { satteri } from '@astrojs/markdown-satteri';
import { pluginTypographie } from './src/utils/plugin-typographie.mjs';

// https://astro.build/config
export default defineConfig({
  site: 'https://histoire-19eme-siecle.mathieu6700417.workers.dev',
  integrations: [mdx()],
  markdown: {
    // Typographie française appliquée à tout le texte Markdown/MDX
    // (espaces insécables, apostrophes courbes).
    processor: satteri({ mdastPlugins: [pluginTypographie] }),
  },
});
