// Petits outils sans état : mots lus (même découpage que src/utils/diaporamas.ts), stockage
// local protégé (lire / ecrire), préférence de mouvement réduit, format m:ss.
 // x0, y0, x1, y1 (fractions de l'image)
/** Mots d'un texte (même découpage que `motsLus` de src/utils/diaporamas.ts et `commun.mots_lus`). */
export const motsLus = (texte: string) => [...texte.matchAll(/\S+/g)].filter((m) => /[\p{L}\p{N}]/u.test(m[0])).map((m) => ({ d: m.index!, f: m.index! + m[0].length }));    // s : changement d'acte (pendant le carton) ou saut vers un autre acte
export const lire = (cle: string) => { try { return localStorage.getItem(cle); } catch { return null; } };
export const ecrire = (cle: string, v: string | null) => {
  try { v === null ? localStorage.removeItem(cle) : localStorage.setItem(cle, v); } catch { /* stockage indisponible */ }
};
export const mouvementReduit = window.matchMedia('(prefers-reduced-motion: reduce)');

export function mmss(s: number) {
  s = Math.max(0, Math.floor(s));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = String(s % 60).padStart(2, '0');
  return h ? `${h}:${String(m).padStart(2, '0')}:${sec}` : `${m}:${sec}`;
}
