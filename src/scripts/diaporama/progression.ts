// Barre de progression et temps écoulé (carton + voix + segment), préchargement des images à
// venir. Spec 12, « Lecteur (`Diaporama.astro`) ».
import { mmss } from './outils';
import type { Lecteur } from './contexte';

export function installerProgression(lec: Lecteur) {
  const { D, bornes, chronoCarton, debuts, elEcoule, elPlan, instant, prechargerVideo, prelude, sa, segments, suiteEtPause,
    total, voixEtPause } = lec;
  Object.assign(lec, { majTemps, precharger, tempsCourant });
  /** Instant courant dans tout le diaporama (cartons, voix, pauses, intermèdes). */
  function tempsCourant() {
    const g = lec.tempsGenerique?.();  // ouverture, récapitulatif (generique.ts, installé après)
    if (g != null) return g;
    if (!lec.lance) return debuts[lec.i];
    if (lec.enCarton) return debuts[lec.i] + Math.min(chronoCarton.t, prelude[lec.i]);
    const base = debuts[lec.i] + prelude[lec.i];
    if (lec.enSuite || lec.suiteFini) {
      const c = lec.suiteFini ? suiteEtPause[lec.i] : Math.min(sa.currentTime || 0, suiteEtPause[lec.i]);
      return base + voixEtPause[lec.i] + c;
    }
    return base + Math.min(instant(), voixEtPause[lec.i]);
  }

  function majTemps() {
    const t = tempsCourant();
    elEcoule.textContent = mmss(Math.min(total, t));
    bornes.forEach((b, k) => {
      const p = Math.max(0, Math.min(1, (t - b.t0) / (b.t1 - b.t0)));
      (segments[k].firstElementChild as HTMLElement).style.transform = `scaleX(${p})`;
      segments[k].classList.toggle('est-courant', lec.i >= b.de && lec.i < b.fin);
    });
  }

  // Images à venir décodées d'avance (gardées en vie, sinon le décodage est perdu) : le fondu
  // d'entrée ne commence pas par un décodage de la grande image, qui ferait sauter des images.
  const decodees = new Map<string, HTMLImageElement>();
  function precharger(k: number) {
    for (const j of [k, k + 1, k + 2]) {
      const x = D.diapos[j];
      if (!x) continue;
      if (!decodees.has(x.img)) {
        const im = new Image();
        im.src = x.img;
        im.decode().catch(() => {});
        decodees.set(x.img, im);
        for (const cle of decodees.keys()) if (decodees.size > 4) decodees.delete(cle);
      }
      if (x.lieu?.fond === 'paris' && elPlan?.dataset.src) new Image().src = elPlan.dataset.src;
      for (const g of x.portraits?.gens ?? []) new Image().src = g.src;
      if (x.objet) new Image().src = x.objet.src;
      if (x.manuscrit) new Image().src = x.manuscrit.src;
      if (x.ap) new Image().src = x.ap.img;
      // Plans, galerie d'intermède, images d'une lecture (spec 14).
      for (const p of [...(x.plans ?? []), ...(lec.galerieDe(x) ?? [])]) new Image().src = p.img;
      for (const v of x.mos?.vignettes ?? []) new Image().src = v.img;
      // Clip d'une image mise en mouvement (spec 16) : la suivante seulement, il est lourd.
      if (j <= k + 1) prechargerVideo(x);
      if (j <= k + 1) lec.prechargerCouleur(x);
      if (j > k && x.audio) { const a = new Audio(); a.preload = 'auto'; a.src = x.audio; }
      if (x.suite && j <= k + 1) { const a = new Audio(); a.preload = 'auto'; a.src = x.suite.src; }
    }
  }
}
