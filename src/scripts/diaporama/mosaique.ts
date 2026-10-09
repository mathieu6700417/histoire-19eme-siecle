// Mosaïque : cases de la grille, vignettes, plongée dans l'image principale, rendu à l'instant t.
// Lit `x.mos`, `MOSAIQUE_T`. Spec 12, « Enrichissements visuels », point 5 ;
// README : « Avant / après et mosaïques ».
import { DUREE_MIN, FONDU_MOSAIQUE_REDUIT, MISE_EN_ROUTE, MISE_EN_VALEUR, VISE_GLISSE, VISE_ZOOM } from './constantes';
import { adoucir, ampleur, melanger, profil } from './geometrie';
import { mouvementReduit } from './outils';
import type { Diapo, Rect } from './types';
import type { Lecteur } from './contexte';

export function installerMosaique(lec: Lecteur) {
  const { MOSAIQUE_T, avantDe, css, debutPlongee, parametres, scene, vue } = lec;
  Object.assign(lec, { majMosaique, placerTuiles, plongee, principal });
  /** Cases de la grille (px de la scène) : 4 → 2 × 2 ; 5 → 2 au-dessus de 3 ; 6 → 3 × 2. Filets
   *  de GOUTTIERE px entre les cases ; la grille couvre la scène. */
  const GOUTTIERE = 4;
  function cases(n: number, W: number, H: number): Rect[] {
    const haut = Math.floor(n / 2), lignes = [haut, n - haut], g = GOUTTIERE / 2, R: Rect[] = [];
    lignes.forEach((m, j) => {
      for (let k = 0; k < m; k++) {
        const x0 = (W * k) / m, x1 = (W * (k + 1)) / m, y0 = (H * j) / 2, y1 = (H * (j + 1)) / 2;
        R.push([x0 + (k ? g : 0), y0 + (j ? g : 0), x1 - (k < m - 1 ? g : 0), y1 - (j ? 0 : g)]);
      }
    });
    return R;
  }
  /** Taille CSS de l'image principale posée par `cadre` (sans lire le DOM). */
  function tailleImage(x: { u: Rect; l: number; h: number }, W: number, H: number) {
    const s = Math.max(W / x.l, H / x.h);
    return { IW: (x.l * s) / (x.u[2] - x.u[0]), IH: (x.h * s) / (x.u[3] - x.u[1]) };
  }
  /** Géométrie de la mosaïque à la taille courante : cases, transformation finale de l'image
   *  principale (`B` : sa première vue, là où sa caméra commence) et celle de la grille (`G` : la
   *  même image réduite dans sa case, couvrante), début et durée de la plongée, fin (`a0`). */
  function plongee(x: Diapo) {
    const W = scene.clientWidth, H = scene.clientHeight, M = x.mos!;
    const C = cases(M.vignettes.length, W, H), c = C[M.principale] ?? C[0];
    const cw = c[2] - c[0], ch = c[3] - c[1], sigma = Math.max(cw / W, ch / H);
    const { IW, IH } = tailleImage(x, W, H);
    const B = parametres(W, H, IW, IH, x.u, vue(x, x.camera[0].c));
    const cx = (c[0] + c[2]) / 2, cy = (c[1] + c[3]) / 2;
    const G = { tx: cx + sigma * (B.tx - W / 2), ty: cy + sigma * (B.ty - H / 2), s: sigma * B.s };
    // Vues de la scène entière dans la zone utile de l'image (au départ, bien plus grande que
    // l'image) : la durée suit l'ampleur, comme une transition de la caméra (mêmes plafonds).
    const iw = IW * (x.u[2] - x.u[0]), ih = IH * (x.u[3] - x.u[1]);
    const rect = (p: typeof B): Rect => {
      const x0 = (-p.tx / p.s - x.u[0] * IW) / iw, y0 = (-p.ty / p.s - x.u[1] * IH) / ih;
      return [x0, y0, x0 + W / p.s / iw, y0 + H / p.s / ih];
    };
    const { zoom, glisse } = ampleur(rect(G), rect(B));
    const u = Math.max(zoom / VISE_ZOOM, glisse / VISE_GLISSE);
    const d = mouvementReduit.matches ? 0 : Math.max(DUREE_MIN, u <= 2 * MISE_EN_ROUTE ? 1.5 * u : u + MISE_EN_ROUTE);
    const t0 = debutPlongee(M.vignettes.length);
    return { C, k: M.principale, c, sigma, B, G, W, H, IW, IH, t0, d, m: Math.min(d / 3, MISE_EN_ROUTE), a0: t0 + d, cx, cy };
  }
  /** Image principale d'une diapositive pour la caméra : arrêtée au volet d'un avant / après,
   *  ou partant de la fin de la plongée d'une mosaïque. */
  function principal(x: Diapo): Diapo {
    if (x.ap) return avantDe(x);
    if (x.mos && !x.ouv) return { ...x, a0: plongee(x).a0 };
    return x;
  }
  /** Place les vignettes dans leurs cases (taille de la scène) : chacune couvre sa case avec sa
   *  zone utile, centrée ; la principale est posée à chaque image (majMosaique). */
  function placerTuiles(c: HTMLElement, x: Diapo) {
    const mo = c.querySelector<HTMLElement>('.mosaique')!;
    if (!x.mos || x.ouv || mo.dataset.n !== String(x.n)) return;
    const W = scene.clientWidth, H = scene.clientHeight, C = cases(x.mos.vignettes.length, W, H);
    [...mo.children].forEach((el, k) => {
      if (k === x.mos!.principale) return;
      const v = x.mos!.vignettes[k], r = C[k], w = r[2] - r[0], h = r[3] - r[1];
      Object.assign((el as HTMLElement).style, { left: `${r[0]}px`, top: `${r[1]}px`, width: `${w}px`, height: `${h}px` });
      const s = Math.max(w / v.l, h / v.h), IW = (v.l * s) / (v.u[2] - v.u[0]), IH = (v.h * s) / (v.u[3] - v.u[1]);
      const im = el.querySelector('img')!;
      im.style.width = `${IW}px`; im.style.height = `${IH}px`;
      im.style.transform = `translate3d(${(w / 2 - (v.u[0] + v.u[2]) / 2 * IW).toFixed(2)}px, ${(h / 2 - (v.u[1] + v.u[3]) / 2 * IH).toFixed(2)}px, 0)`;
    });
  }
  /** Mosaïque à l'instant `t` : vignettes qui paraissent, puis plongée dans l'image principale. */
  function majMosaique(c: HTMLElement, x: Diapo, t: number) {
    const mo = c.querySelector<HTMLElement>('.mosaique')!, img = c.querySelector('img')!;
    const g = plongee(x), reduit = mouvementReduit.matches;
    const fin = reduit ? g.t0 + FONDU_MOSAIQUE_REDUIT : g.a0;
    if (t >= fin) { mo.hidden = true; img.style.visibility = ''; c.style.background = ''; return; }
    mo.hidden = false;
    c.style.background = 'var(--c-scene, #f1efea)';
    // Avant le fondu de la grille (mouvement réduit), l'image principale reste cachée.
    img.style.visibility = reduit && t >= g.t0 ? '' : 'hidden';
    const tuiles = [...mo.children] as HTMLElement[];
    // Grille entière dès l'entrée ; puis mise en valeur à tour de rôle (révision du 2026-10-08) :
    // les autres vignettes d'abord, dans l'ordre de la grille, la principale en dernier. La
    // vignette en cours est en pleine couleur et s'avance (×1,03), les autres sont en gris voilé ;
    // fondus croisés de `fondu` s. La principale garde sa couleur après son tour et revient à
    // l'échelle 1 avant la plongée (qui part ainsi exactement de sa case).
    const F = MOSAIQUE_T.fondu, ordre = [...tuiles.keys()].filter((k) => k !== g.k).concat(g.k);
    const voile = reduit ? 0 : adoucir((t - MOSAIQUE_T.apparition) / F);
    tuiles.forEach((el, k) => {
      const a = MOSAIQUE_T.apparition + ordre.indexOf(k) * MOSAIQUE_T.pas, b = a + MOSAIQUE_T.pas;
      const monte = reduit ? 0 : adoucir((t - a) / F), en = monte - (reduit ? 0 : adoucir((t - b) / F));
      const v = 1 - voile * (1 - (k === g.k ? monte : en)); // 1 : pleine couleur, 0 : gris voilé
      el.style.opacity = (1 - 0.45 * (1 - v)).toFixed(3);
      el.style.transform = en > 0.001 ? `scale(${(1 + MISE_EN_VALEUR * en).toFixed(5)})` : '';
      el.style.zIndex = en > 0.001 ? '2' : '';
      const im = el.querySelector('img')!;
      im.style.filter = v < 0.998 ? `grayscale(${(0.85 * (1 - v)).toFixed(3)})` : '';
    });
    // Plongée : homothétie de la grille, de G (départ) à B (image principale en place).
    const pr = reduit ? 0 : profil(t - g.t0, g.d, g.m);
    const r = 1 / g.sigma, s = g.G.s * Math.pow(r, pr), k = s / g.G.s;
    const Fx = (g.sigma * g.B.tx - g.G.tx) / (g.sigma - 1), Fy = (g.sigma * g.B.ty - g.G.ty) / (g.sigma - 1);
    const tx = Fx + k * (g.G.tx - Fx), ty = Fy + k * (g.G.ty - Fy);
    mo.style.transform = `translate3d(${(tx - k * g.G.tx).toFixed(2)}px, ${(ty - k * g.G.ty).toFixed(2)}px, 0) scale(${k.toFixed(6)})`;
    mo.style.opacity = reduit ? (1 - adoucir((t - g.t0) / FONDU_MOSAIQUE_REDUIT)).toFixed(3) : '';
    // Case de la principale (repère de la grille) : de sa case à toute la scène réduite.
    const M: Rect = [g.cx - (g.sigma * g.W) / 2, g.cy - (g.sigma * g.H) / 2, g.cx + (g.sigma * g.W) / 2, g.cy + (g.sigma * g.H) / 2];
    const R = melanger(g.c, M, pr);
    const el = tuiles[g.k], im = el.querySelector('img')!;
    Object.assign(el.style, { left: `${R[0]}px`, top: `${R[1]}px`, width: `${R[2] - R[0]}px`, height: `${R[3] - R[1]}px` });
    im.style.width = `${g.IW}px`; im.style.height = `${g.IH}px`;
    im.style.transform = css({ tx: g.G.tx - R[0], ty: g.G.ty - R[1], s: g.G.s });
  }
}
