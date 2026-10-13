// Images mises en mouvement par IA (spec 16) : le clip muet d'une diapositive (`x.video`, dérivé de
// son image par un modèle à poids ouverts, 10 s) est posé dans une boîte de la taille de l'image, sur
// sa zone utile, et reçoit la même transformation que l'image : la caméra calée sur la narration
// continue de travailler, sur une image qui vit. Le clip est calé sur l'horloge de la voix : il
// paraît en fondu à DEBUT_CLIP (l'image fixe d'abord, l'entrée finie) ou juste après la plongée
// d'une mosaïque, est joué **une seule fois** (ni boucle ni aller-retour : retour de l'utilisateur
// du 2026-10-12), puis sa dernière image reste tenue jusqu'à la fin de la diapositive. Pause, sauts
// et reprise le recalent sur la voix ; il s'efface sous un plan (spec 14) et s'arrête avec le
// calque. Préférence « réduire les animations » : jamais de clip, l'image reste fixe.
// README : « Couche générée ».
import { DEBUT_CLIP, DEBUT_CLIP_MOSAIQUE, DERIVE_CLIP, FONDU_PLAN } from './constantes';
import { mouvementReduit } from './outils';
import type { Diapo } from './types';
import type { Lecteur } from './contexte';

export function installerMouvement(lec: Lecteur) {
  Object.assign(lec, { arreterVideo, debutClip: (x: Diapo) => debutDe(x), majVideo, poserVideo, prechargerVideo, preparerVideo, taillerVideo });
  const boite = (c: HTMLElement) => c.querySelector<HTMLElement>('.lecteur__video')!;
  const videoDe = (c: HTMLElement) => boite(c).querySelector('video')!;

  /** Pose le clip de la diapositive dans le calque (ou le retire) ; rien avec le mouvement réduit. */
  function preparerVideo(c: HTMLElement, x: Diapo) {
    const b = boite(c), v = videoDe(c);
    // La classe est retirée sans transition : le clip n'a pas à s'effacer en fondu dans un calque
    // qui change d'image.
    b.style.transition = 'none';
    b.classList.remove('est-vivante');
    void b.offsetWidth;
    b.style.transition = '';
    if (!x.video || mouvementReduit.matches) {
      if (v.getAttribute('src')) { v.pause(); v.removeAttribute('src'); v.load(); }
      b.hidden = true;
      return;
    }
    if (v.getAttribute('src') !== x.video.src) { v.src = x.video.src; v.load(); }
    else { v.pause(); caler(v, 0); }
    b.hidden = false;
    taillerVideo(c, x);
  }

  /** Même boîte que l'image (taille posée par `cadre`), le clip sur la zone utile : la transformation
   *  de l'image s'applique telle quelle à la boîte. Le clip a les proportions de la zone utile (le
   *  modèle a reçu l'image étirée à ses dimensions : l'étirer en retour la recouvre exactement). */
  function taillerVideo(c: HTMLElement, x: Diapo) {
    if (!x.video) return;
    const b = boite(c), v = videoDe(c), img = c.querySelector('img')!;
    if (b.hidden) return;
    const IW = parseFloat(img.style.width) || 0, IH = parseFloat(img.style.height) || 0;
    b.style.width = `${IW}px`;
    b.style.height = `${IH}px`;
    v.style.left = `${IW * x.u[0]}px`;
    v.style.top = `${IH * x.u[1]}px`;
    v.style.width = `${IW * (x.u[2] - x.u[0])}px`;
    v.style.height = `${IH * (x.u[3] - x.u[1])}px`;
  }

  /** Instant de la voix où le clip part : l'entrée de l'image finie, ou la plongée d'une mosaïque. */
  const debutDe = (x: Diapo) => (x.mos && !x.ouv ? (lec.principal(x).a0 ?? 0) + DEBUT_CLIP_MOSAIQUE : DEBUT_CLIP);
  /** Recale le clip (sans seek redondant pendant qu'un seek est en cours). */
  function caler(v: HTMLVideoElement, pos: number) {
    if (v.seeking || Math.abs(v.currentTime - pos) <= DERIVE_CLIP) return;
    try { v.currentTime = pos; } catch { /* pas encore chargé */ }
  }

  /** À chaque rendu du calque visible, à l'instant `t` de la voix : même transformation que
   *  l'image ; le clip paraît (fondu CSS) dès son instant de départ, une fois l'entrée finie
   *  (`entree`) et sa première image décodée, tant qu'un plan ne le couvre pas ; il joue avec la
   *  voix (recalé après une pause ou un saut) et tient sa dernière image une fois fini. */
  function majVideo(c: HTMLElement, x: Diapo, transformation: string, t: number, entree: boolean) {
    const b = boite(c);
    if (b.hidden || !x.video) return;
    const v = videoDe(c);
    b.style.transform = transformation;
    const pos = t - debutDe(x), fin = v.duration || x.video.duree;
    const couvert = Boolean(x.plans?.length) && t >= x.plans![0].t + FONDU_PLAN;
    const vivante = entree && pos >= 0 && !couvert && v.readyState >= 2;
    if (b.classList.contains('est-vivante') !== vivante) b.classList.toggle('est-vivante', vivante);
    if (!vivante || pos >= fin - 0.05) {
      // Avant le départ : prêt sur sa première image ; après la fin : la dernière, tenue.
      if (!v.paused) v.pause();
      caler(v, pos >= fin - 0.05 ? fin : 0);
      return;
    }
    const joue = lec.joue && !lec.enCarton;
    if (joue && (v.paused || v.ended)) { caler(v, pos); v.play().catch(() => {}); }
    else if (!joue && !v.paused) v.pause();
    else if (joue) caler(v, pos); // dérive après un saut de la voix
  }

  /** Calque figé (sortant d'un fondu, image sous un carton) : le clip suit l'image et s'arrête. */
  function poserVideo(c: HTMLElement, transformation: string) {
    const b = boite(c);
    if (b.hidden) return;
    b.style.transform = transformation;
    arreterVideo(c);
  }

  function arreterVideo(c: HTMLElement) {
    const v = boite(c).querySelector('video');
    if (v && !v.paused) v.pause();
  }

  // Clips des diapositives à venir mis en cache d'avance (éléments gardés en vie, deux au plus).
  const amorces = new Map<string, HTMLVideoElement>();
  function prechargerVideo(x: Diapo) {
    if (!x.video || mouvementReduit.matches || amorces.has(x.video.src)) return;
    const v = document.createElement('video');
    v.muted = true; v.preload = 'auto'; v.src = x.video.src; v.load();
    amorces.set(x.video.src, v);
    for (const cle of amorces.keys()) if (amorces.size > 2) { amorces.get(cle)!.removeAttribute('src'); amorces.delete(cle); }
  }
}
