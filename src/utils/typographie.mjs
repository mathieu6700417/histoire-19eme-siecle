// Règles de typographie française appliquées automatiquement au texte.
// - espace insécable (U+00A0) avant « : » et à l'intérieur des guillemets « »
// - espace fine insécable (U+202F) avant ; ? !
// - apostrophe droite remplacée par l'apostrophe typographique
// On ne transforme que des espaces déjà présentes : « 12:30 » ou une URL
// restent intactes.

const NBSP = ' ';
const NNBSP = ' ';

/** @param {string} texte */
export function typographie(texte) {
  if (!texte) return texte;
  return texte
    .replace(/'/g, '’')
    .replace(/[   ]+:/g, NBSP + ':')
    .replace(/[   ]+([;?!])/g, NNBSP + '$1')
    .replace(/«[   ]+/g, '«' + NBSP)
    .replace(/[   ]+»/g, NBSP + '»');
}
