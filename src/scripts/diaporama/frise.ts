// Frise du temps : curseur et date dans le carton d'acte et au bas de l'image (4 s à chaque
// changement d'année), surimpressions poussées au-dessus. Lit `x.date`, `lec.derniere`.
// Spec 12, « Frise du temps », « Frise simplifiée » ; README : « Frise du temps ».
import { CARTON_ACTE_DUREE, CARTON_ACTE_MAX, CARTON_ACTE_MIN, CARTON_NET_DUREE, CARTON_TRACE, CARTON_TRACE_DUREE, DUREE_FRISE, FONDU_FRISE } from './constantes';
import { adoucir } from './geometrie';
import { mouvementReduit } from './outils';
import type { DateFrise } from './types';
import type { Lecteur } from './contexte';

export function installerFrise(lec: Lecteur) {
  const { D, acteDe, chronoCarton, elCartonDates, racine, scene } = lec;
  Object.assign(lec, { ajusterFrises, cacherFrise, majFriseCarton, majPoussee, montrerFrise, poserActe });
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
  /** Intervalle de chaque acte sur la frise (%) : ses dates annoncées (annotations du
   *  2026-10-14) ; à défaut, du début de la première date de ses diapositives à la fin de la
   *  dernière (dates reprises comprises). */
  const intervallesActes = D.actes.map((a, k) => {
    if (a.periode) return a.periode;
    const ds = D.diapos.filter((_, j) => acteDe[j] === k).map((x) => x.date).filter((x): x is DateFrise => Boolean(x));
    return ds.length ? { x0: Math.min(...ds.map((x) => x.x0)), x1: Math.max(...ds.map((x) => x.x1)) } : null;
  });
  // --- Frise animée du carton (retour du 2026-10-11, « la frise se dessine ») ----------------
  // Tout dérive de l'horloge du carton (figée en pause, avancée quand on passe le carton) : le
  // filet se trace de gauche à droite (graduations et actes déjà vus, en gris, au passage du
  // tracé), puis le segment de l'acte avance de sa première à sa dernière date en s'épaississant
  // pendant que les années défilent sous le titre. Révision du 2026-10-12 (annotations de
  // visionnage) : plus de dates clés sous la frise ; la période de l'acte est en couleur
  // (--c-accent) : segment et zone teintée qui s'étend avec lui. Révision du 2026-10-14 : plus
  // d'onde ni de rouge ; segment en dégradé du gris au noir, zone en gris dégradé (CSS).
  // Mouvement réduit : état final d'emblée.
  let carton: { k: number; debut: number; annees: [number, number] | null; passes: { el: HTMLElement; x0: number; x1: number }[] } | null = null;
  /** Carton d'acte : prépare la frise de l'acte `k` (actes passés, période de l'acte). */
  function poserActe(f: HTMLElement, k: number) {
    const piste = f.querySelector<HTMLElement>('.frise-t__piste')!, acte = f.querySelector<HTMLElement>('.frise-t__acte');
    if (!acte) return;
    for (const el of piste.querySelectorAll('.frise-t__passe')) el.remove();
    const passes = intervallesActes.slice(0, k).flatMap((iv) => {
      if (!iv) return [];
      const el = document.createElement('span');
      el.className = 'frise-t__passe';
      el.style.left = `${iv.x0.toFixed(3)}%`;
      piste.querySelector('.frise-t__zone')!.before(el);
      return [{ el, x0: iv.x0, x1: iv.x1 }];
    });
    // Les années défilent si les dates de l'acte sont « AAAA-AAAA » (sinon le texte est fixe).
    const m = /^(\d{4})-(\d{4})$/.exec(D.actes[k].dates);
    const lettres = [...D.actes[k].titre].filter((c) => !/\s/.test(c)).length;
    // Le segment part quand les dates sont là (après le titre, écrit lettre par lettre).
    const debut = Math.min(CARTON_ACTE_MAX, Math.max(CARTON_ACTE_MIN, 1.6 + 0.12 * lettres));
    carton = { k, debut, annees: m ? [Number(m[1]), Number(m[2])] : null, passes };
    for (const el of piste.querySelectorAll<HTMLElement>('.frise-t__acte, .frise-t__zone')) el.hidden = !intervallesActes[k];
    majFriseCarton(0);
  }
  /** Frise du carton à l'instant `t` de son horloge. */
  function majFriseCarton(t = chronoCarton.t) {
    if (!friseCarton || !carton) return;
    if (mouvementReduit.matches) t = Infinity;
    const filet = friseCarton.querySelector<HTMLElement>('.frise-t__filet')!, acte = friseCarton.querySelector<HTMLElement>('.frise-t__acte')!;
    const zone = friseCarton.querySelector<HTMLElement>('.frise-t__zone')!;
    const bornes = friseCarton.querySelectorAll<HTMLElement>('.frise-t__borne');
    // 1. Tracé : avancée régulière, départ et arrêt doux.
    const q = adoucir((t - CARTON_TRACE) / CARTON_TRACE_DUREE), X = q * 100;
    filet.style.transform = `scaleX(${q.toFixed(4)})`;
    for (const c of friseCarton.querySelectorAll<HTMLElement>('.frise-t__cran')) c.style.opacity = X + 0.01 >= parseFloat(c.style.left) ? '1' : '0';
    if (bornes[1]) bornes[1].style.opacity = adoucir((t - CARTON_TRACE - CARTON_TRACE_DUREE + 0.3) / 0.4).toFixed(3);
    for (const p of carton.passes) p.el.style.width = `${Math.max(0, Math.min(p.x1, X) - p.x0).toFixed(3)}%`;
    // 2. Segment de l'acte : il avance et s'épaissit ; les années défilent.
    const iv = intervallesActes[carton.k], p = adoucir((t - carton.debut) / CARTON_ACTE_DUREE);
    // 3. Mise au point (annotations du 2026-10-18) : le segment arrivé, le halo se resserre et
    // s'efface, le dégradé passe au noir plein : la période finit nette.
    const n = adoucir((t - carton.debut - CARTON_ACTE_DUREE) / CARTON_NET_DUREE);
    if (iv) {
      const w = (iv.x1 - iv.x0) * p;
      acte.style.left = `${(iv.x0 + w / 2).toFixed(3)}%`;
      acte.style.width = `${w.toFixed(3)}%`;
      acte.style.height = `${(2 + 3 * p).toFixed(2)}px`;
      acte.style.opacity = t >= carton.debut ? '1' : '0';
      acte.style.setProperty('--net', n.toFixed(3));
      // Zone teintée : elle s'étend avec le segment, un peu plus large que lui.
      zone.style.left = `${(iv.x0 + w / 2).toFixed(3)}%`;
      zone.style.width = `calc(${w.toFixed(3)}% + ${(40 * p * (1 - n)).toFixed(1)}px)`;
      zone.style.opacity = (0.3 * p * (1 - n)).toFixed(3);
    }
    if (carton.annees) {
      const [a0, a1] = carton.annees, a = a0 + Math.round(p * (a1 - a0));
      const texte = p >= 1 ? D.actes[carton.k].dates : a > a0 ? `${a0}-${a}` : String(a0);
      if (elCartonDates.textContent !== texte) elCartonDates.textContent = texte;
    }
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
