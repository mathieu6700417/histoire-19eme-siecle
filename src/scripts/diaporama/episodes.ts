// Épisodes : panneaux de chiffres, barres, cartes, documents, calés sur l'instant du segment
// (`--p` de chaque élément). Spec 12, « Épisodes », « Chronologie animée » ;
// README : « Lectures d'époque et épisodes ».
import { adoucir, melanger } from './geometrie';
import { mouvementReduit } from './outils';
import type { Rect, SuiteEpisode } from './types';
import type { Lecteur } from './contexte';

export function installerEpisodes(lec: Lecteur) {
  const { changerSousTitre, etats } = lec;
  Object.assign(lec, { majEpisode });
  /** Épisode : visuel actif, éléments animés (--p), tracés, zoom du document, sous-titre. */
  const AVANCE_EPISODE = 0.3; // s : l'œil devance un peu l'oreille
  function majEpisode(el: HTMLElement, c: SuiteEpisode, t: number) {
    const e = etats.get(el)!;
    const reduit = mouvementReduit.matches;
    const ta = t + AVANCE_EPISODE;
    let k = 0;
    e.ev!.forEach((v, j) => { if (v.t <= ta) k = j; });
    if (k !== e.actif) { e.ev!.forEach((v, j) => v.el.classList.toggle('est-actif', j === k)); e.actif = k; }
    for (const a of e.anims!) {
      const p = reduit ? (ta >= a.t ? 1 : 0) : adoucir((ta - a.t) / a.d);
      if (Math.abs(p - a.p) > 0.002) { a.el.style.setProperty('--p', p.toFixed(3)); a.p = p; }
    }
    for (const x of e.traces!) {
      const tr = x.trace;
      let f = 0;
      if (ta >= tr[0][0]) {
        let j = 0;
        while (j + 1 < tr.length && tr[j + 1][0] <= ta) j++;
        f = j + 1 < tr.length && !reduit ? tr[j][1] + (tr[j + 1][1] - tr[j][1]) * ((ta - tr[j][0]) / Math.max(0.001, tr[j + 1][0] - tr[j][0])) : tr[j][1];
      }
      if (Math.abs(f - x.x) > 0.0005) { x.el.setAttribute('width', (f * x.l).toFixed(1)); x.x = f; }
    }
    for (const doc of e.docs!) majDocument(doc, ta, reduit);
    // Sous-titre : la phrase en cours.
    let ph = -1;
    c.phrases.forEach(([t0], j) => { if (t0 <= t + 0.1) ph = j; });
    if (lec.suiteFini) ph = -1;
    if (ph !== e.phrase) { e.phrase = ph; changerSousTitre(ph >= 0 ? c.phrases[ph][2] : ''); }
  }
  /** Document : la page entière, puis un zoom doux (1,4 s) sur chaque ligne lue. */
  function majDocument(doc: { el: HTMLElement; page: HTMLElement; l: number; h: number; vues: number[][] }, ta: number, reduit: boolean) {
    const W = doc.el.clientWidth, H = doc.el.clientHeight;
    if (!W || !H) return;
    const s0 = Math.min(W / doc.l, H / doc.h);
    const pw = doc.l * s0, ph = doc.h * s0;
    const entiere: Rect = [0, 0, 1, 1];
    let k = -1;
    doc.vues.forEach((v, j) => { if (v[0] <= ta + 0.4) k = j; });
    let r = entiere;
    if (k >= 0) {
      const de = (k > 0 ? doc.vues[k - 1].slice(1) : entiere) as Rect;
      const a = doc.vues[k].slice(1) as Rect;
      r = reduit ? a : melanger(de, a, adoucir((ta + 0.4 - doc.vues[k][0]) / 1.4));
    }
    const rw = (r[2] - r[0]) * pw, rh = (r[3] - r[1]) * ph;
    const z = Math.min(W / rw, H / rh);
    const tx = W / 2 - z * ((r[0] + r[2]) / 2) * pw, ty = H / 2 - z * ((r[1] + r[3]) / 2) * ph;
    doc.page.style.width = `${pw.toFixed(1)}px`;
    doc.page.style.height = `${ph.toFixed(1)}px`;
    doc.page.style.transform = `translate(${tx.toFixed(1)}px, ${ty.toFixed(1)}px) scale(${z.toFixed(4)})`;
  }
}
