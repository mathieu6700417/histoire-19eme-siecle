// Images colorisées par IA (spec 16, « la colorisation couleur seule ») : la version colorisée d'une
// image (`x.coul`, ou `p.coul` pour un plan : même trait, seule la chrominance change, aux dimensions
// exactes de la zone utile) est posée sur la zone utile de l'image et reçoit la même transformation
// qu'elle : caméra, entrée en scène, image entière sur fond noir, recul d'entrée. L'original paraît
// d'abord ; la couleur monte ensuite en fondu lent et reste jusqu'à la fin de l'image.
// Tout dérive de l'instant de la voix (aucune transition CSS) : pause, saut, reprise et horloge
// factice des captures donnent la même image. Pendant l'entrée de l'image, le calque couleur suit
// son fondu et son gris. Préférence « réduire les animations » : jamais de couleur, l'original seul.
// README : « Couche générée », « Colorisation ».
import { COULEUR_APRES_ENTREE, COULEUR_FIN, COULEUR_FONDU, COULEUR_MIN, COULEUR_PART, COULEUR_SEUIL, FONDU_PLAN } from './constantes';
import { adoucir } from './geometrie';
import { mouvementReduit } from './outils';
import type { Couleur, Diapo } from './types';
import type { Lecteur } from './contexte';

export function installerCouleur(lec: Lecteur) {
  Object.assign(lec, { majCouleur, marquerCouleur, opaciteCouleur, poserCouleur, prechargerCouleur, preparerCouleur, teinter });
  const calque = (c: HTMLElement) => c.querySelector<HTMLImageElement>(':scope > .lecteur__couleur')!;

  /** Opacité de la couleur à l'instant `t` pour une image montrée de `a` à `b` (s de la voix) ;
   *  `xv` : sa vue dérivée pour la caméra (`principal(x)`, `planDe(…)`), dont la première tenue
   *  commence à la fin de l'entrée en scène (ou du recul d'ouverture). Le fondu part vers
   *  `COULEUR_PART` de la fenêtre, jamais avant `COULEUR_MIN` ni avant la fin de l'entrée, et il
   *  est avancé pour finir `COULEUR_FIN` s avant la fin de l'image (si la fenêtre le permet). */
  function opaciteCouleur(xv: Diapo, a: number, b: number, t: number) {
    const pret = Math.max(a + COULEUR_MIN, lec.plan(xv)[0].a + COULEUR_APRES_ENTREE);
    const debut = Math.max(pret, Math.min(a + (b - a) * COULEUR_PART, b - COULEUR_FIN - COULEUR_FONDU));
    return adoucir((t - debut) / COULEUR_FONDU);
  }

  /** Pose le calque couleur `el` sur la zone utile de `base` (dont `tr` est la transformation). */
  function placer(el: HTMLImageElement, base: HTMLImageElement, u: Couleur['u'], tr: string) {
    const IW = parseFloat(base.style.width) || 0, IH = parseFloat(base.style.height) || 0;
    el.style.width = `${IW * (u[2] - u[0])}px`;
    el.style.height = `${IH * (u[3] - u[1])}px`;
    el.style.transform = `${tr} translate(${(IW * u[0]).toFixed(3)}px, ${(IH * u[1]).toFixed(3)}px)`;
  }
  /** Calque couleur `el` de l'image `base` à l'opacité `o` (0 : masqué), avec le même filtre. Rend
   *  l'opacité réellement montrée (0 tant que le fichier n'est pas chargé). */
  function teinter(el: HTMLImageElement, base: HTMLImageElement, coul: Couleur, tr: string, o: number, filtre: string) {
    if (o <= 0 || !el.complete || !el.naturalWidth) {
      if (el.style.visibility !== 'hidden') el.style.visibility = 'hidden';
      return 0;
    }
    placer(el, base, coul.u, tr);
    el.style.opacity = o.toFixed(3);
    el.style.filter = filtre;
    el.style.visibility = '';
    return o;
  }

  /** Pose la version colorisée de l'image de la diapositive dans le calque (ou la retire). */
  function preparerCouleur(c: HTMLElement, x: Diapo) {
    const el = calque(c);
    el.style.visibility = 'hidden';
    if (!x.coul || mouvementReduit.matches) {
      if (el.getAttribute('src')) el.removeAttribute('src');
      el.hidden = true;
      return;
    }
    if (el.getAttribute('src') !== x.coul.src) el.src = x.coul.src;
    el.hidden = false;
  }

  /** À chaque rendu du calque visible, à l'instant `t` de la voix : la couleur de l'image de la
   *  diapositive, avec la transformation `tr` et le filtre de l'image ; elle disparaît une fois
   *  l'image couverte par un plan (spec 14). Rend son opacité. */
  function majCouleur(c: HTMLElement, x: Diapo, tr: string, t: number, filtre: string) {
    const el = calque(c);
    if (el.hidden || !x.coul) return 0;
    const fin = x.plans?.[0]?.t ?? (x.duree || 6);
    const couvert = Boolean(x.plans?.length) && t >= x.plans![0].t + FONDU_PLAN;
    return teinter(el, c.querySelector('img')!, x.coul, tr, couvert ? 0 : opaciteCouleur(lec.principal(x), 0, fin, t), filtre);
  }

  /** Calque figé (sortant d'un fondu, image sous un carton) : la couleur suit l'image, à son opacité. */
  function poserCouleur(c: HTMLElement, x: Diapo, tr: string) {
    const el = calque(c);
    if (el.hidden || !x.coul || el.style.visibility === 'hidden') return;
    placer(el, c.querySelector('img')!, x.coul.u, tr);
  }

  /** Mention « colorisée par IA » du cartouche : montrée tant que la couleur est à l'écran. */
  let marque = false;
  function marquerCouleur(o: number) {
    const oui = o > COULEUR_SEUIL;
    if (oui !== marque) { marque = oui; lec.lecteur.classList.toggle('en-couleur', oui); }
  }

  // Versions colorisées des diapositives à venir, chargées d'avance.
  function prechargerCouleur(x: Diapo) {
    if (mouvementReduit.matches) return;
    for (const i of [x, ...(x.plans ?? [])]) if (i.coul) new Image().src = i.coul.src;
  }
}
