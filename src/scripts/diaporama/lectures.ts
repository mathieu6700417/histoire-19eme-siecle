// Lectures d'époque : préparation d'une carte ou d'un panneau (éléments relevés une fois, `etats`)
// et carte de citation mot à mot (vers compris). Spec 12, « Lectures » ;
// README : « Lectures d'époque et épisodes ».
import { mouvementReduit } from './outils';
import type { Anim, EtatSegment, SuiteEpisode, SuiteLecture } from './types';
import type { Lecteur } from './contexte';

export function installerLectures(lec: Lecteur) {
  Object.assign(lec, { majCitation, preparer });
  const etats = new WeakMap<HTMLElement, EtatSegment>();
  function preparer(el: HTMLElement, c: SuiteLecture | SuiteEpisode) {
    let e = etats.get(el);
    if (!e) {
      e = {};
      if (c.type === 'lecture') {
        e.zone = el.querySelector<HTMLElement>('.citation__texte')!;
        e.defile = el.querySelector<HTMLElement>('.citation__defile')!;
        // Éléments de chaque mot (rang `data-k` ; la ponctuation et les coupures suivent un mot).
        e.mots = c.mots.map(() => []);
        el.querySelectorAll<HTMLElement>('[data-k]').forEach((x) => e!.mots![Number(x.dataset.k)]?.push(x));
        // Fond flou : l'image du moment, chargée seulement à la première lecture.
        const f = el.querySelector<HTMLElement>('.citation__fond[data-fond]');
        if (f?.dataset.fond && !f.style.backgroundImage) f.style.backgroundImage = `url("${f.dataset.fond}")`;
      } else {
        e.ev = [...el.querySelectorAll<HTMLElement>('.ev')].map((x) => ({ el: x, t: Number(x.dataset.t) }));
        e.anims = [...el.querySelectorAll<HTMLElement>('.anim')].map((x) => ({ el: x, t: Number(x.dataset.t), d: Number(x.dataset.d || 1), p: -1 }));
        e.traces = [...el.querySelectorAll<SVGRectElement>('[data-trace]')].map((x) => ({ el: x, l: Number(x.dataset.l), trace: JSON.parse(x.dataset.trace!), x: -1 }));
        e.docs = [...el.querySelectorAll<HTMLElement>('.ev-doc[data-vues]')].map((x) => ({
          el: x, page: x.querySelector<HTMLElement>('.ev-doc__page')!, l: Number(x.dataset.l), h: Number(x.dataset.h), vues: JSON.parse(x.dataset.vues!) }));
      }
      etats.set(el, e);
    }
    // Remise à zéro : tout sera recalculé au premier rendu.
    e.lu = -1; e.cour = -1; e.y = -1; e.hz = -1; e.actif = -1; e.phrase = -2;
    e.mots?.forEach((l) => l.forEach((x) => x.classList.remove('est-lu', 'est-courant')));
    if (e.defile) e.defile.style.transform = '';
    e.anims?.forEach((a) => (a.p = -1));
    e.traces?.forEach((x) => (x.x = -1));
    if (e.zone) e.zone.scrollTop = 0;
  }

  /** Lecture : le texte apparaît mot par mot au rythme exact de la voix (instants de
   *  l'alignement forcé) : le mot en cours en noir, les mots lus en gris foncé, les suivants
   *  invisibles mais à leur place. Mouvement réduit : par phrase. Le texte qui dépasse la place
   *  défile en douceur pour garder la ligne en cours dans le bas de la zone. */
  const AVANCE_MOT = 0.06; // s : le mot paraît au moment où la voix l'attaque
  function majCitation(el: HTMLElement, c: SuiteLecture, t: number) {
    const e = etats.get(el)!;
    const N = c.mots.length;
    let lu = 0, cour = 0; // mots [0, lu) lus, [lu, cour) en cours, la suite invisible
    if (lec.suiteFini) { lu = N; cour = N; }
    else if (mouvementReduit.matches) {
      for (const [t0, k0, k1] of c.phrases) if (t0 <= t + AVANCE_MOT) { lu = k0; cour = k1; }
    } else {
      while (cour < N && c.mots[cour] <= t + AVANCE_MOT) cour++;
      lu = Math.max(0, cour - 1);
    }
    if (lu !== e.lu || cour !== e.cour) {
      e.mots!.forEach((els, k) => {
        const etat = k < lu ? 1 : k < cour ? 2 : 0;
        for (const x of els) {
          x.classList.toggle('est-lu', etat === 1);
          x.classList.toggle('est-courant', etat === 2);
        }
      });
      e.lu = lu; e.cour = cour;
    }
    // Défilement : recalculé aussi quand la zone change de taille (plein écran, rotation).
    const z = e.zone!, hz = z.clientHeight;
    const repere = e.mots![Math.max(0, Math.min(N - 1, cour - 1))]?.[0];
    const H = e.defile!.offsetHeight;
    let y = 0;
    if (repere && H > hz + 1 && cour > 0) {
      const bas = repere.offsetTop + repere.offsetHeight;
      y = Math.max(0, Math.min(H - hz, bas - hz * 0.74));
      // Dépassement infime (marge, jambages) : on ne bouge pas pour si peu.
      if (y < repere.offsetHeight * 0.4) y = 0;
    }
    y = Math.round(y);
    if (y !== e.y || hz !== e.hz) {
      e.defile!.style.transform = y ? `translateY(${-y}px)` : '';
      z.classList.toggle('deborde', y > 0);
      e.y = y; e.hz = hz;
    }
  }
  Object.assign(lec, { etats });
}
