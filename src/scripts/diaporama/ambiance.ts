// Ambiance sonore d'une image mise en mouvement (spec 17) : un son d'ambiance généré (`x.amb`, modèle
// à poids ouverts, normalisé à -23 LUFS) accompagne le clip de la diapositive (`x.video`), bien sous
// la voix (AMBIANCE_DB). Comme le clip, il est calé sur l'horloge de la voix : il part avec lui (fondu
// d'entrée dans le fichier), se fige en pause, se recale après un saut, s'efface quand un plan couvre
// le clip, au carton, pendant un segment (chant, lecture, épisode) et au changement de diapositive ;
// la voix finie, il va seul à son terme (fondu de sortie dans le fichier) pendant la pause. Il suit le
// bouton « Musique » et le curseur de volume du lecteur. Préférence « réduire les animations » : pas
// de clip, donc pas d'ambiance. Signalement : crédits de la page et livre d'images, pas le cartouche.
// README : « Ambiances sonores (spec 17) ».
import { AMBIANCE_DB, DERIVE_CLIP, FONDU_AMBIANCE, FONDU_PLAN, VOLUME_DEFAUT } from './constantes';
import { mouvementReduit } from './outils';
import type { Diapo } from './types';
import type { Lecteur } from './contexte';

export function installerAmbiance(lec: Lecteur) {
  Object.assign(lec, { amorcerAmbiance, arreterAmbiance, majAmbiance, prechargerAmbiance });
  const { D, racine } = lec;
  const btnMusique = racine.querySelector<HTMLButtonElement>('[data-action="musique"]');
  const curseur = racine.querySelector<HTMLInputElement>('.lecteur__volume');
  const son = new Audio();
  son.preload = 'auto';
  const BASE = Math.pow(10, AMBIANCE_DB / 20);
  let cible = 0;            // gain voulu (0 : silence), atteint en FONDU_AMBIANCE s
  let gain = 0, dernier = 0, raf = 0;

  /** Niveau réglé par le lecteur : coupé avec la musique, proportionnel au curseur de volume. */
  function niveau() {
    if (btnMusique && btnMusique.getAttribute('aria-pressed') === 'false') return 0;
    const v = curseur ? Number(curseur.value) / 100 : VOLUME_DEFAUT;
    return Math.min(1, BASE * (v / VOLUME_DEFAUT));
  }
  /** Rampe du gain vers la cible (hors de la boucle de rendu : elle finit aussi lecteur en pause). */
  function rampe(maintenant: number) {
    const dt = Math.min(0.1, (maintenant - dernier) / 1000);
    dernier = maintenant;
    const pas = dt / FONDU_AMBIANCE;
    gain = cible > gain ? Math.min(cible, gain + pas) : Math.max(cible, gain - pas);
    son.volume = Math.min(1, Math.max(0, gain * niveau()));
    if (gain === 0 && cible === 0 && !son.paused) son.pause();
    raf = gain !== cible ? requestAnimationFrame(rampe) : 0;
  }
  function viser(v: number, net = false) {
    cible = v;
    if (net) gain = v;
    son.volume = Math.min(1, Math.max(0, gain * niveau()));
    if (!raf && gain !== cible) { dernier = performance.now(); raf = requestAnimationFrame(rampe); }
    else if (gain === 0 && cible === 0 && !son.paused) son.pause();
  }
  function caler(pos: number) {
    if (son.seeking || Math.abs(son.currentTime - pos) <= DERIVE_CLIP) return;
    try { son.currentTime = pos; } catch { /* pas encore chargé */ }
  }

  /** À chaque rendu de la diapositive visible, à l'instant `t` de la voix (`entree` : l'entrée de
   *  l'image est finie, comme pour le clip). Sans ambiance, ou hors de sa fenêtre : silence. */
  function majAmbiance(x: Diapo | null, t: number, entree: boolean) {
    if (!x?.amb || !x.video || mouvementReduit.matches) { arreterAmbiance(); return; }
    const pos = t - lec.debutClip(x), fin = x.amb.duree;
    const couvert = Boolean(x.plans?.length) && t >= x.plans![0].t + FONDU_PLAN;
    const dedans = entree && pos >= 0 && pos < fin - 0.05 && !couvert && !lec.enCarton && !lec.enSuite && !lec.suiteFini;
    if (!dedans) { arreterAmbiance(); return; }
    if (!son.src.endsWith(x.amb.src)) { son.src = x.amb.src; gain = 0; }
    if (!lec.joue) {
      // Pause : figée net, à sa place (la reprise repart du même point, sans fondu).
      if (!son.paused) son.pause();
      caler(pos);
      return;
    }
    // La voix finie (pause avant la diapositive suivante), l'horloge ne court plus : l'ambiance va
    // seule à son terme, sans être recalée.
    const voixFinie = t >= x.duree - 0.05;
    if (son.paused && !son.ended) { caler(pos); son.play().catch(() => {}); }
    else if (!voixFinie) caler(pos);
    viser(1, gain > 0 && son.volume > 0);
    son.volume = Math.min(1, Math.max(0, gain * niveau()));
  }

  /** Silence (fondu court, puis arrêt) : carton, segment, plan qui couvre le clip, autre diapositive. */
  function arreterAmbiance() {
    if (son.paused && gain === 0) return;
    if (son.paused) { gain = cible = 0; return; }
    viser(0);
  }

  function prechargerAmbiance(x: Diapo) {
    if (!x.amb || mouvementReduit.matches) return;
    const a = new Audio();
    a.preload = 'auto';
    a.src = x.amb.src;
  }

  /** iOS : l'élément doit avoir été lancé une fois pendant un geste (appelé par `deverrouillerAudio`). */
  function amorcerAmbiance() {
    const src = D.diapos.find((x) => x.amb)?.amb?.src;
    if (!src || mouvementReduit.matches || son.getAttribute('src')) return;
    son.src = src;
    son.muted = true;
    son.play().then(() => { son.pause(); son.muted = false; }).catch(() => { son.muted = false; });
  }

  // Pour les tests : état de l'ambiance.
  (racine as any).__ambiance = () => ({ src: son.getAttribute('src'), t: son.currentTime, paused: son.paused, volume: son.volume, gain, cible, niveau: niveau() });
}
