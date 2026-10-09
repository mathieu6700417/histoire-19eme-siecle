// Paroles des intermèdes chantés façon clip : préparation des vers et mots, affichage calé sur
// l'instant du chant. Test : `__clip()`. Spec 12, « Paroles des chants façon clip » ;
// README : « Paroles des chants calées au mot ».
import { motsLus, mouvementReduit } from './outils';
import type { SuiteChant } from './types';
import type { Lecteur } from './contexte';

export function installerChant(lec: Lecteur) {
  const { D, elClipTexte, horlogeSuite, lecteur, racine, sa } = lec;
  Object.assign(lec, { majParoles, preparerClip });
  // --- Paroles des chants façon clip (spec 12, 2026-10-08) -------------------------------------
  // Chaque vers est posé d'avance au centre de l'image (mots invisibles, place réservée : rien ne
  // bouge quand ils paraissent) ; le vers en cours est visible, ses mots paraissent à leur instant
  // chanté. L'affichage dérive de l'horloge lissée de l'intermède : pause, reprise, sauts justes.
  // Sans calage au mot (repli) ou en mouvement réduit, le vers entier paraît à son début.
  const AVANCE_CLIP = 0.08; // s : le mot paraît un rien avant d'être chanté (attaque de la note)
  let clipVers: HTMLElement[][] = [], clipEls: HTMLElement[] = [], vers = -2, versMots = -1;
  function preparerClip(c: SuiteChant) {
    clipEls = []; clipVers = [];
    for (const [, v] of c.paroles) {
      const p = document.createElement('p');
      p.className = 'clip__vers';
      const mots: HTMLElement[] = [];
      const bornes = motsLus(v);
      bornes.forEach((b, k) => {
        // Un mot emporte la ponctuation qui le suit (« roi ! ») ; l'espace reste entre les mots.
        const bout = v.slice(k ? b.d : 0, k + 1 < bornes.length ? bornes[k + 1].d : v.length);
        const span = document.createElement('span');
        span.className = 'clip__mot';
        span.textContent = bout.trimEnd();
        p.append(span, bout.slice(span.textContent.length));
        mots.push(span);
      });
      elClipTexte.append(p);
      clipEls.push(p);
      clipVers.push(mots);
    }
    vers = -2; versMots = -1;
  }
  function majParoles() {
    const c = D.diapos[lec.i].suite;
    if (!lec.enSuite || !c || c.type !== 'chant' || !clipEls.length) return;
    const t = horlogeSuite.lire(sa) + AVANCE_CLIP;
    let k = -1;
    while (k + 1 < c.paroles.length && c.paroles[k + 1][0] <= t) k++;
    if (k !== vers) {
      clipEls.forEach((e, j) => e.classList.toggle('est-courant', j === k));
      vers = k; versMots = -1;
    }
    if (k < 0) return;
    const mots = c.paroles[k][2];
    let n = clipVers[k].length;
    if (mots && !mouvementReduit.matches) { n = 0; while (n < mots.length && mots[n] <= t) n++; }
    if (n === versMots) return;
    clipVers[k].forEach((e, j) => e.classList.toggle('est-chante', j < n));
    versMots = n;
  }
  // Paroles façon clip (tests) : instant de l'intermède (brut, lissé), vers et mots affichés.
  (racine as any).__clip = () => ({ brut: sa.currentTime, lisse: horlogeSuite.t, paused: sa.paused, vers, mots: versMots, clip: lecteur.classList.contains('en-clip') });
}
