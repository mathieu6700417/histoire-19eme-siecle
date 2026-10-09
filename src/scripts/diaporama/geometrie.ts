// Calculs purs de la caméra sur des rectangles [x0, y0, x1, y1] : adoucissement, homothétie
// (zoom logarithmique), profil de vitesse, ampleur d'un mouvement, souffle des tenues.
// Spec 12, « Caméra calme et lente » et « Caméra plus vivante et cadres justes ».
import { RAMPE_SOUFFLE, SOUFFLE, SOUFFLE_VITESSE } from './constantes';
import type { Rect } from './types';
export const adoucir = (t: number) => { const u = Math.min(1, Math.max(0, t)); return u * u * (3 - 2 * u); };
export const melanger = (a: Rect, b: Rect, t: number) => a.map((v, k) => v + (b[k] - v) * t) as Rect;
/** Le cadre agrandi (k > 1) ou resserré (k < 1) autour de son centre. */
export function echelle([x0, y0, x1, y1]: Rect, k: number): Rect {
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, w = ((x1 - x0) * k) / 2, h = ((y1 - y0) * k) / 2;
  return [cx - w, cy - h, cx + w, cy + h];
}
/** Avancement (0 → 1) d'un mouvement de `d` secondes à l'instant `t` : vitesse constante, avec
 *  mise en route et arrêt de `m` secondes (rampes en smoothstep : vitesse et accélération
 *  continues). La vitesse au plus fort vaut 1 / (d − m). */
export function profil(t: number, d: number, m: number) {
  if (t <= 0 || d <= 0) return t >= d ? 1 : 0;
  if (t >= d) return 1;
  m = Math.min(m, d / 2);
  const I = (u: number) => u * u * u - (u * u * u * u) / 2; // ∫ smoothstep, I(1) = 1/2
  const tot = d - m;
  if (t < m) return (m * I(t / m)) / tot;
  if (t <= d - m) return (m / 2 + t - m) / tot;
  return 1 - (m * I((d - t) / m)) / tot;
}
/** Entre deux vues de mêmes proportions : rapport de largeur `r`, et la part `s` (0 → 1) du
 *  zoom logarithmique ramenée sur l'interpolation linéaire des bords (homothétie : le point
 *  fixe reste immobile à l'écran, le centre avance à vitesse constante). */
export const partLog = (r: number, s: number) => (Math.abs(r - 1) < 1e-4 ? s : (1 - Math.pow(r, s)) / (1 - r));
export const trajet = (a: Rect, b: Rect, s: number) => melanger(a, b, partLog((b[2] - b[0]) / (a[2] - a[0]), s));
/** Ampleur d'un trajet : zoom (|log du rapport d'échelle|) et déplacement du centre de l'écran
 *  (en fraction de la scène, constant le long du trajet). */
export function ampleur(a: Rect, b: Rect) {
  const wa = a[2] - a[0], ha = a[3] - a[1], r = (b[2] - b[0]) / wa, lr = Math.log(r);
  const k = Math.abs(r - 1) < 1e-4 ? 1 : lr / (r - 1);
  const g = Math.max(Math.abs((b[0] + b[2] - a[0] - a[2]) / 2) / wa, Math.abs((b[1] + b[3] - a[1] - a[3]) / 2) / ha) * k;
  return { zoom: Math.abs(lr), glisse: g };
}
/** Vue après `t` secondes d'une tenue de `d` secondes sur la vue `c` : zoom avant lent et
 *  continu (log d'échelle à vitesse constante, SOUFFLE au plus), glissement vers le centre du
 *  cadre visé `cible` (le sujet ; sans cible, zoom centré) borné à la marge libre. Le sous-cadre
 *  reste dans `c` (et donc dans la zone utile). */
export function souffle(c: Rect, t: number, d: number, cible?: Rect): Rect {
  const m = Math.min(RAMPE_SOUFFLE, d / 2);
  const lz = Math.min(SOUFFLE, SOUFFLE_VITESSE * Math.max(0, d - m));
  if (lz <= 0) return c;
  const serre = 1 - Math.exp(-lz), r = echelle(c, 1 - serre);
  const mx = (serre * (c[2] - c[0])) / 2, my = (serre * (c[3] - c[1])) / 2;
  const borne = (v: number, b: number) => Math.min(b, Math.max(-b, v));
  const ox = cible ? borne((cible[0] + cible[2] - c[0] - c[2]) / 2, mx) : 0;
  const oy = cible ? borne((cible[1] + cible[3] - c[1] - c[3]) / 2, my) : 0;
  return trajet(c, [r[0] + ox, r[1] + oy, r[2] + ox, r[3] + oy], profil(t, d, m));
}
