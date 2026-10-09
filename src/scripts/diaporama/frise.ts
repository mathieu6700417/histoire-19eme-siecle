// Frise du temps : curseur et date dans le carton d'acte et au bas de l'image (4 s à chaque
// changement d'année), surimpressions poussées au-dessus. Lit `x.date`, `lec.derniere`.
// Spec 12, « Frise du temps », « Frise simplifiée » ; README : « Frise du temps ».
import { DUREE_FRISE, FONDU_FRISE } from './constantes';
import { mouvementReduit } from './outils';
import type { DateFrise } from './types';
import type { Lecteur } from './contexte';

export function installerFrise(lec: Lecteur) {
  const { D, acteDe, racine, scene } = lec;
  Object.assign(lec, { ajusterFrises, cacherFrise, majPoussee, montrerFrise, poserActe });
  // --- Frise du temps -----------------------------------------------------------------------
  const friseCarton = racine.querySelector<HTMLElement>('.frise-t--carton');
  const friseSur = racine.querySelector<HTMLElement>('.frise-t--surimpression');
  lec.derniere = -1;     // dernière diapositive affichée : sa date est la « date précédente »
  let minuterieFrise = 0;

  /** Frise du bas (révision du 2026-10-09) : à chaque changement d'année (année de début) par
   *  rapport à la diapositive précédente, et à tout retour en arrière (intervalle entièrement
   *  antérieur au début du précédent). Même règle que verifier.py. */
  const anneeDe = (j: number) => new Date(j * 86400000).getUTCFullYear();
  const changeFrise = (de: DateFrise, a: DateFrise) => a.j1 < de.j0 || anneeDe(a.j0) !== anneeDe(de.j0);

  /** Date du curseur, centrée sur lui mais gardée dans la piste. */
  function placerDate(f: HTMLElement, dt: DateFrise) {
    const el = f.querySelector<HTMLElement>('.frise-t__date')!, piste = el.parentElement!;
    const w = piste.clientWidth, demi = w ? (el.offsetWidth / 2 / w) * 100 : 0;
    el.style.left = `${Math.min(100 - demi, Math.max(demi, (dt.x0 + dt.x1) / 2)).toFixed(3)}%`;
  }
  /** Curseur sur `dt` (trait, ou court segment pour une durée). */
  function poserCurseur(f: HTMLElement, dt: DateFrise, transition: boolean) {
    const c = f.querySelector<HTMLElement>('.frise-t__curseur')!, el = f.querySelector<HTMLElement>('.frise-t__date')!;
    c.style.transition = el.style.transition = transition ? '' : 'none';
    c.style.left = `${dt.x0}%`;
    c.style.width = `${Math.max(0, dt.x1 - dt.x0)}%`;
    el.textContent = dt.libelle;
    placerDate(f, dt);
  }
  /** Intervalle de chaque acte sur la frise (%) : du début de la première date de ses
   *  diapositives à la fin de la dernière (dates reprises comprises). */
  const intervallesActes = D.actes.map((_, k) => {
    const ds = D.diapos.filter((_, j) => acteDe[j] === k).map((x) => x.date).filter((x): x is DateFrise => Boolean(x));
    return ds.length ? { x0: Math.min(...ds.map((x) => x.x0)), x1: Math.max(...ds.map((x) => x.x1)) } : null;
  });
  /** Carton d'acte : segment de l'acte `k` (largeur minimale en CSS, centré sur l'intervalle). */
  function poserActe(f: HTMLElement, k: number) {
    const el = f.querySelector<HTMLElement>('.frise-t__acte'), iv = intervallesActes[k];
    if (!el) return;
    el.hidden = !iv;
    if (!iv) return;
    el.style.left = `${((iv.x0 + iv.x1) / 2).toFixed(3)}%`;
    el.style.width = `${(iv.x1 - iv.x0).toFixed(3)}%`;
  }
  /** Le curseur glisse de `de` à `a` (CSS, ~1 s, ease-in-out). */
  function glisser(f: HTMLElement, de: DateFrise, a: DateFrise) {
    poserCurseur(f, de, false);
    void f.offsetWidth;
    const bouge = !mouvementReduit.matches && (de.x0 !== a.x0 || de.x1 !== a.x1);
    poserCurseur(f, a, bouge);
  }
  function cacherFrise() {
    clearTimeout(minuterieFrise);
    friseSur?.classList.remove('est-visible');
  }
  /** Poussée (retour du 2026-10-09) : seules montent les surimpressions du bas qui chevauchent
   *  la frise en largeur (sur ordinateur, médaillon et portraits dans les coins restent en
   *  place ; sur téléphone, la frise est pleine largeur : tout monte). Recalculé à chaque image
   *  tant que la frise est là (tailles et contenus changent en cours de diapositive). */
  const pousses = [...scene.querySelectorAll<HTMLElement>(':scope > .lieu, :scope > .portraits, :scope > .objet, :scope > .chiffre, :scope > .date-rep, :scope > .mots')];
  function majPoussee() {
    if (!friseSur?.classList.contains('est-visible')) return;
    const f = friseSur.getBoundingClientRect();
    for (const el of pousses) {
      const r = el.getBoundingClientRect();
      el.classList.toggle('sous-frise', r.width > 0 && r.left < f.right - 1 && r.right > f.left + 1);
    }
  }
  /** Surimpression de 4 s au bas de l'image (fondu, glissement ~1 s, lecture, fondu) ; elle
   *  s'affiche toujours et pousse les autres surimpressions du bas plus haut (--frise-pousse,
   *  CSS) ; horloge murale (éphémère, indépendante de la voix : une pause ne la fige pas). */
  function montrerFrise(de: DateFrise, a: DateFrise) {
    if (!friseSur) return;
    clearTimeout(minuterieFrise);
    friseSur.classList.remove('est-visible');
    void friseSur.offsetWidth;
    friseSur.classList.add('est-visible');
    glisser(friseSur, de, a);
    scene.style.setProperty('--frise-h', `${friseSur.offsetHeight}px`);
    majPoussee();
    minuterieFrise = window.setTimeout(cacherFrise, (DUREE_FRISE - FONDU_FRISE) * 1000);
  }
  /** Après un redimensionnement : date recalée (le curseur est en %) et hauteur remesurée. */
  function ajusterFrises() {
    for (const f of [friseCarton, friseSur]) {
      if (!f) continue;
      const x = D.diapos[lec.i].date;
      if (x && f.querySelector('.frise-t__date')!.textContent) placerDate(f, x);
    }
    if (friseSur) scene.style.setProperty('--frise-h', `${friseSur.offsetHeight}px`);
  }
  Object.assign(lec, { changeFrise, friseCarton });
}
