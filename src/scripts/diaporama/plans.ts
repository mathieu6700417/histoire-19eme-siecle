// Plans, lectures illustrées et galeries (spec 14) : plusieurs images sur une même diapositive
// (`x.plans`, horloge de la voix) et série d'images pendant un segment (`suite.galerie` d'un
// intermède, `suite.images` d'une lecture ; horloge du segment). Chaque image a sa zone utile et sa
// caméra sur sa fenêtre de temps ; fondu croisé, tout dérive de l'instant (pause et sauts justes).
// README : « Plans, lectures illustrées et galeries (spec 14) ».
import { ELAN_PLAN, FONDU_GALERIE, FONDU_PLAN, FONDU_REDUIT } from './constantes';
import { adoucir } from './geometrie';
import { mouvementReduit } from './outils';
import type { Diapo, Plan } from './types';
import type { Lecteur } from './contexte';

export function installerPlans(lec: Lecteur) {
  const { cadreA, calques, couches, horlogeSuite, sa, scene, transformation } = lec;
  Object.assign(lec, { galerieDe, legendeGalerie, majGalerie, majPlans, planDe, poserPlans, preparerPlans, taillerPlans });
  const boite = (c: HTMLElement) => c.querySelector<HTMLElement>('.lecteur__plans')!;
  const images = (c: HTMLElement) => boite(c).querySelectorAll<HTMLImageElement>('img:not(.lecteur__couleur)');
  /** Version colorisée d'un plan (spec 16) : l'élément qui suit son image, s'il y en a une. */
  const teinte = (im: HTMLImageElement) => (im.nextElementSibling?.classList.contains('lecteur__couleur') ? (im.nextElementSibling as HTMLImageElement) : null);
  /** Série d'images du segment joué après la voix (galerie d'un intermède, images d'une lecture). */
  function galerieDe(x: Diapo): Plan[] | null {
    const s = x.suite;
    return (s?.type === 'chant' ? s.galerie : s?.type === 'lecture' ? s.images : null) ?? null;
  }
  const toutes = (x: Diapo) => [...(x.plans ?? []), ...(galerieDe(x) ?? [])];
  /** Vue dérivée d'une image de série pour la caméra : sa zone utile, ses étapes, sa fenêtre de
   *  temps [p.t, fin] ; la tenue a commencé un peu avant (`ELAN_PLAN`) : l'image entre déjà en
   *  mouvement. Avec une entrée en scène (`p.ent`), son mouvement d'arrivée part de `p.t`. */
  function planDe(x: Diapo, p: Plan, fin: number): Diapo {
    const t0 = p.ent ? p.t : p.t - ELAN_PLAN;
    return { ...x, img: p.img, u: p.u, l: p.l, h: p.h, camera: p.camera, en: p.en ?? null, ent: p.ent ?? null, ouv: null, ap: null, mos: null, plans: null,
      suite: null, t0, a0: t0, v0: undefined, duree: fin };
  }
  /** Pose les images de la série dans le calque (une fois par diapositive). */
  function preparerPlans(c: HTMLElement, x: Diapo) {
    const b = boite(c), P = toutes(x);
    if (!P.length) { if (b.childElementCount) b.replaceChildren(); b.hidden = true; delete b.dataset.n; return; }
    if (b.dataset.n !== String(x.n)) {
      // Image entière (`p.en`) : un fond noir la précède et suit son fondu (bandes de côté).
      b.replaceChildren(...P.flatMap((p) => {
        const im = document.createElement('img');
        im.alt = ''; im.decoding = 'async'; im.src = p.img;
        im.style.visibility = 'hidden';
        const els: HTMLElement[] = [im];
        if (p.en) {
          const fond = document.createElement('i');
          fond.className = 'lecteur__noir';
          fond.style.visibility = 'hidden';
          els.unshift(fond);
        }
        // Version colorisée par IA (spec 16, couleur.ts) : au-dessus de l'image, même transformation.
        if (p.coul && !mouvementReduit.matches) {
          const co = document.createElement('img');
          co.className = 'lecteur__couleur';
          co.alt = ''; co.decoding = 'async'; co.src = p.coul.src;
          co.style.visibility = 'hidden';
          els.push(co);
        }
        return els;
      }));
      b.dataset.n = String(x.n);
    }
    b.hidden = false;
    taillerPlans(c, x);
  }
  /** Taille de chaque image : sa zone utile couvre la scène (comme `cadre`). */
  function taillerPlans(c: HTMLElement, x: Diapo) {
    const W = scene.clientWidth, H = scene.clientHeight, els = images(c);
    toutes(x).forEach((p, k) => {
      const im = els[k] as HTMLImageElement | undefined;
      if (!im) return;
      const s = Math.max(W / p.l, H / p.h);
      im.style.width = `${(p.l * s) / (p.u[2] - p.u[0])}px`;
      im.style.height = `${(p.h * s) / (p.u[3] - p.u[1])}px`;
      const u = p.u;
      im.style.clipPath = p.en && !(u[0] <= 0 && u[1] <= 0 && u[2] >= 1 && u[3] >= 1)
        ? `inset(${(u[1] * 100).toFixed(3)}% ${((1 - u[2]) * 100).toFixed(3)}% ${((1 - u[3]) * 100).toFixed(3)}% ${(u[0] * 100).toFixed(3)}%)` : '';
    });
  }
  /** Opacité de la version colorisée du plan montré (0 : aucune), posée par `serie`. */
  let couleurCourante = 0;
  /** Rend la série `P` (images `els[de…]`) à l'instant `t` de son horloge ; `fin` : fin de la
   *  dernière fenêtre. Rend le rang de l'image montrée (-1 : aucune). */
  function serie(c: HTMLElement, x: Diapo, P: Plan[], de: number, t: number, fin: number, fondu: number, gris: number) {
    const els = images(c), d = mouvementReduit.matches ? FONDU_REDUIT : fondu;
    let courant = -1;
    couleurCourante = 0;
    P.forEach((p, k) => {
      const im = els[de + k] as HTMLImageElement | undefined;
      if (!im) return;
      const o = adoucir((t - p.t) / d);
      if (t >= p.t) { courant = k; couleurCourante = 0; }
      const fond = p.en ? (im.previousElementSibling as HTMLElement | null) : null;
      // Invisible avant son instant, et une fois couverte par la suivante.
      if (o <= 0 || (k + 1 < P.length && t >= P[k + 1].t + d)) {
        if (im.style.visibility !== 'hidden') { im.style.visibility = 'hidden'; if (fond) fond.style.visibility = 'hidden'; const co = teinte(im); if (co) co.style.visibility = 'hidden'; }
        return;
      }
      if (fond) { fond.style.visibility = ''; fond.style.opacity = o.toFixed(3); }
      const xp = planDe(x, p, k + 1 < P.length ? P[k + 1].t + d : fin);
      im.style.visibility = '';
      im.style.opacity = o.toFixed(3);
      im.style.transform = transformation(c, xp, cadreA(xp, t), 1, im);
      im.style.filter = gris > 0.002 ? `grayscale(${gris.toFixed(3)})` : '';
      // Version colorisée (spec 16) : sur la fenêtre du plan, de son instant au plan suivant.
      const co = p.coul ? teinte(im) : null;
      if (co) {
        const oc = lec.teinter(co, im, p.coul!, im.style.transform, lec.opaciteCouleur(xp, p.t, k + 1 < P.length ? P[k + 1].t : fin, t), im.style.filter);
        if (k === courant) couleurCourante = oc;
      }
    });
    return courant;
  }
  /** Plans de la diapositive à l'instant `t` de la voix. Rend l'opacité de la version colorisée
   *  du plan montré (spec 16 ; 0 : aucune), ou -1 avant le premier plan. */
  function majPlans(c: HTMLElement, x: Diapo, t: number, gris = 0) {
    if (!x.plans) return -1;
    const k = serie(c, x, x.plans, 0, t, x.duree || 6, FONDU_PLAN, gris);
    couches[calques.indexOf(c)].tp = t;
    return k < 0 ? -1 : couleurCourante;
  }
  /** Instant du segment en cours (-1 hors segment). */
  const instantSuite = (x: Diapo) => (lec.suiteFini ? x.suite!.duree : lec.enSuite ? horlogeSuite.lire(sa) : -1);
  /** Galerie du segment à son instant (rien hors du segment) ; rend le rang de l'image montrée. */
  function majGalerie(c: HTMLElement, x: Diapo, ts = instantSuite(x)) {
    const G = galerieDe(x);
    if (!G) return -1;
    couches[calques.indexOf(c)].tg = ts;
    return serie(c, x, G, x.plans?.length ?? 0, ts < 0 ? -Infinity : ts, x.suite!.duree, FONDU_GALERIE, 0);
  }
  /** Calque figé (sortant, ou sous un carton) : ses images reposées à leur dernier instant. */
  function poserPlans(k: number) {
    const x = couches[k].x;
    if (!x) return;
    if (x.plans && couches[k].tp != null) serie(calques[k], x, x.plans, 0, couches[k].tp!, x.duree || 6, FONDU_PLAN, 0);
    const G = galerieDe(x);
    if (G && couches[k].tg != null && couches[k].tg! >= 0) serie(calques[k], x, G, x.plans?.length ?? 0, couches[k].tg!, x.suite!.duree, FONDU_GALERIE, 0);
  }
  /** Cartouche pendant une galerie : celui de l'image montrée (intermède) ; pour une lecture, la
   *  légende de l'image est écrite dans la carte (rend alors null : le cartouche est masqué). */
  let legendeCarte = '';
  function legendeGalerie(x: Diapo, k: number): string | null {
    const G = galerieDe(x);
    if (!G || k < 0) return null;
    if (x.suite!.type === 'chant') return G[k].legende;
    const el = lec.ov?.querySelector<HTMLElement>('.citation__image');
    if (el && (legendeCarte !== G[k].legende || !el.firstChild)) { el.innerHTML = G[k].legende; legendeCarte = G[k].legende; }
    return null;
  }
}
