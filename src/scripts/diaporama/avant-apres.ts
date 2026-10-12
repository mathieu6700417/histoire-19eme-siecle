// Avant / après : image avant (caméra arrêtée au volet), image après (vue de raccord) et rendu du
// volet à l'instant t. Lit `x.ap`, `VOLET_S`. Spec 12, « Enrichissements visuels », point 3 ;
// README : « Avant / après et mosaïques ».
import { FONDU_APRES_REDUIT } from './constantes';
import { adoucir } from './geometrie';
import { mouvementReduit } from './outils';
import type { Diapo, Rect } from './types';
import type { Lecteur } from './contexte';

export function installerAvantApres(lec: Lecteur) {
  const { VOLET_S, cadreA, calques, couches, plan, transformation, vue } = lec;
  Object.assign(lec, { apresDe, majApres });
  // --- Avant / après et mosaïque (spec 12, « Enrichissements visuels », points 3 et 5) -----------
  // Tout dérive de l'instant de la voix (pause, reprise et sauts justes). Avant / après : la
  // caméra de l'image avant s'arrête en douceur au passage du volet ; pendant le volet (VOLET s),
  // les deux images sont fixes et superposées (même lieu au même endroit de l'écran) ; puis la
  // caméra reprend sur l'image après, depuis la vue de raccord. Mosaïque : vignettes en grille,
  // l'une après l'autre ; puis plongée (homothétie, zoom logarithmique, plafonds tenus) dans
  // l'image principale, qui occupe enfin la scène là où sa caméra commence.
  /** Image avant : sa caméra finit (vitesse nulle) au début du volet. */
  const avantDe = (x: Diapo): Diapo => (x.ap ? { ...x, duree: x.ap.t } : x);
  /** Image après : sa caméra part de la vue de raccord à la fin du volet. */
  function apresDe(x: Diapo): Diapo {
    const A = x.ap!;
    const xa: Diapo = { ...x, img: A.img, u: A.u, l: A.l, h: A.h, camera: A.camera, ouv: null, ent: null, ap: null, mos: null, t0: A.t, a0: A.t + VOLET_S };
    if (!mouvementReduit.matches) xa.v0 = raccord(x, xa);
    return xa;
  }
  /** Vue de départ sur l'image après : la vue finale de l'image avant (respiration comprise),
   *  transportée par la correspondance entre la dernière vue de l'avant et la vue du cadre de
   *  raccord de l'après (mêmes proportions : une similitude). */
  function raccord(x: Diapo, xa: Diapo): Rect {
    const xb = avantDe(x), P = plan(xb), Va = P[P.length - 1].v, Vp = vue(xa, xa.camera[0].c);
    const F = cadreA(xb, xb.duree || 6);
    const kx = (Vp[2] - Vp[0]) / (Va[2] - Va[0]), ky = (Vp[3] - Vp[1]) / (Va[3] - Va[1]);
    return [Vp[0] + (F[0] - Va[0]) * kx, Vp[1] + (F[1] - Va[1]) * ky, Vp[0] + (F[2] - Va[0]) * kx, Vp[1] + (F[3] - Va[1]) * ky];
  }
  /** Avant / après à l'instant `t` : volet (clip du calque après, ligne) et caméra de l'image après. */
  function majApres(c: HTMLElement, x: Diapo, t: number) {
    const A = x.ap!, elA = c.querySelector<HTMLElement>('.lecteur__apres')!, trait = c.querySelector<HTMLElement>('.lecteur__trait')!;
    const k = calques.indexOf(c);
    if (t < A.t) { elA.hidden = true; trait.hidden = true; couches[k].ra = null; return; }
    elA.hidden = false;
    const xa = apresDe(x), imgA = elA.querySelector('img')!;
    const ra = cadreA(xa, t);
    couches[k].ra = ra;
    imgA.style.transform = transformation(c, xa, ra, 1, imgA);
    if (mouvementReduit.matches) {
      // Fondu enchaîné, sans volet.
      elA.style.clipPath = '';
      elA.style.opacity = adoucir((t - A.t) / FONDU_APRES_REDUIT).toFixed(3);
      trait.hidden = true;
      return;
    }
    const q = adoucir((t - A.t) / VOLET_S);
    if (q < 1) {
      elA.style.clipPath = `inset(0 ${((1 - q) * 100).toFixed(3)}% 0 0)`;
      trait.hidden = false;
      trait.style.transform = `translate3d(${(q * c.clientWidth).toFixed(2)}px, 0, 0)`;
    } else {
      elA.style.clipPath = '';
      trait.hidden = true;
    }
  }
  Object.assign(lec, { avantDe });
}
