// Générique d'ouverture (avant le premier carton, pas à une reprise) et récapitulatif de fin (après
// la dernière diapositive) : mosaïque bord à bord des images de `generique`, titre et dates écrits, indicatif
// commun (lecteur <audio> propre), passables comme un carton, comptés dans la durée. Test :
// `__generique(phase)`. Spec 12, « Générique d'ouverture et récapitulatif de fin » ; README.
import { ecrire, mouvementReduit } from './outils';
import { Chrono } from './horloge';
import type { Lecteur } from './contexte';

type Phase = 'ouverture' | 'fin';

// Minutage (s), calé sur l'indicatif Lyria (marche, accents vers 0,3, 3,3, 6,5 et 9,6 s ; accord
// final à 14,55 s, fin comptée de l'ouverture : le premier carton monte sur cet accord).
// Ouverture : vignettes en fondu, titre lettre à lettre sur le premier énoncé du motif, filet,
// dates sur l'accent de 6,5 s, passage du gris à la couleur de 3,2 à ~11 s.
const O = { apparition: 0.2, fondu: 1.4, pasApparition: 0.07, titre: 0.4, lettre: 0.1, fonduLettre: 0.5,
  dates: 6.4, couleur: 3.2, finCouleur: 9.4, dureeCouleur: 1.6, derive: 0.08 };
// Récapitulatif : la mosaïque revient en couleur, chaque vignette passe au gris à son tour, puis
// elles s'assombrissent ; « Fin » paraît sur l'accord final (`G.fin.accord`), titre et dates une seconde après.
const F = { fondu: 1.2, gris: 1.2, avantAccord: 1.6, dureeGris: 0.9, pali: 0.5, fonduFin: 0.35, titre: 1, fonduTexte: 1 };

const lisse = (x: number) => { const v = Math.max(0, Math.min(1, x)); return v * v * (3 - 2 * v); };
const entre = (t: number, a: number, d: number) => lisse((t - a) / d);

export function installerGenerique(lec: Lecteur) {
  const { CLE_POS, D, N, arreterMinuterie, curseurVolume, btnMusique, genFin, genOuverture, lecteur,
    majTemps, racine } = lec;
  lec.enGenerique = null;
  const G = D.generique;
  const el = racine.querySelector<HTMLElement>('.generique');
  if (!G || !el) {
    // Sans générique : appels neutres.
    const rien = () => {};
    Object.assign(lec, { figerGenerique: rien, lancerRecapitulatif: () => false, ouvrirGenerique: () => false,
      passerGenerique: rien, quitterGenerique: rien, reprendreGenerique: rien, tempsGenerique: () => null });
    return;
  }
  Object.assign(lec, { figerGenerique, lancerRecapitulatif, ouvrirGenerique, passerGenerique,
    quitterGenerique, reprendreGenerique, tempsGenerique });
  const rails = [...el.querySelectorAll<HTMLElement>('.generique__rail')];
  const vignettes = [...el.querySelectorAll<HTMLElement>('.generique__vignette')].map((v) => ({ v, k: Number(v.dataset.k) }));
  const lettresTitre = [...el.querySelectorAll<HTMLElement>('.generique__titre .l')];
  const lettresDates = [...el.querySelectorAll<HTMLElement>('.generique__dates .l')];
  const filet = el.querySelector<HTMLElement>('.generique__filet')!;
  const titres = el.querySelector<HTMLElement>('.generique__titres')!;
  const elFin = el.querySelector<HTMLElement>('.generique__fin')!;
  const n = G.images;
  const chrono = new Chrono();
  let phase: Phase = 'ouverture';
  let raf = 0;
  let charge = false;
  const son = new Audio();
  son.preload = 'none';
  let amorce = false;
  let resonner = false;

  const duree = () => (phase === 'ouverture' ? genOuverture : genFin);
  /** Musique coupée (bouton « Musique ») et volume choisi : l'indicatif les suit. */
  const musiqueActive = () => !btnMusique || btnMusique.getAttribute('aria-pressed') !== 'false';
  function reglerSon() {
    son.muted = !musiqueActive();
    const v = curseurVolume ? Number(curseurVolume.value) / 100 : 0.8;
    son.volume = Math.max(0, Math.min(1, v / 0.8));
  }
  function charger() {
    if (charge) return;
    charge = true;
    for (const im of el!.querySelectorAll<HTMLImageElement>('img[data-src]')) im.src = im.dataset.src!;
  }

  /** Image du générique à l'instant `t` de la phase en cours (styles posés directement : mêmes
   *  pixels à chaque passage, horloge factice des captures comprise). */
  function rendre(t: number) {
    const reduit = mouvementReduit.matches;
    const w = el!.clientWidth;
    // Dérive lente des deux rangées, en sens contraires (aucune en mouvement réduit).
    const p = reduit ? 0 : (phase === 'ouverture' ? t / genOuverture : 1 + t / genFin);
    rails.forEach((r, j) => {
      const dx = O.derive * w * p;
      r.style.transform = `translateX(${(j % 2 ? dx - O.derive * w * 2 : -dx).toFixed(1)}px)`;
    });
    if (phase === 'ouverture') {
      for (const { v, k } of vignettes) {
        const a = reduit ? entre(t, 0.2, 0.6) : entre(t, O.apparition + k * O.pasApparition, O.fondu);
        const c = reduit ? entre(t, O.couleur + 1, 0.5) : entre(t, O.couleur + k * (O.finCouleur - O.couleur) / Math.max(1, n), O.dureeCouleur);
        v.style.opacity = a.toFixed(3);
        v.style.filter = c >= 1 ? '' : `grayscale(${(1 - c).toFixed(3)})`;
      }
      titres.style.opacity = '1';
      elFin.style.opacity = '0';
      lettresTitre.forEach((l, i) => (l.style.opacity = (reduit ? entre(t, O.titre, 0.5) : entre(t, O.titre + i * O.lettre, O.fonduLettre)).toFixed(3)));
      const t1 = O.titre + lettresTitre.length * O.lettre + 0.3;
      filet.style.transform = `scaleX(${(reduit ? entre(t, t1, 0.3) : entre(t, t1, 0.8)).toFixed(3)})`;
      const t2 = Math.max(O.dates, t1 + 0.8);
      lettresDates.forEach((l, i) => (l.style.opacity = (reduit ? entre(t, t2, 0.5) : entre(t, t2 + i * 0.12, O.fonduLettre)).toFixed(3)));
    } else {
      const accord = G!.fin.accord, finGris = accord - F.avantAccord;
      const pas = (finGris - F.gris) / Math.max(1, n);
      const pali = 1 - (1 - F.pali) * entre(t, finGris + 0.2, 1);
      for (const { v, k } of vignettes) {
        const g = entre(t, F.gris + k * pas, reduit ? 0.4 : F.dureeGris);
        v.style.opacity = (entre(t, 0, F.fondu) * pali).toFixed(3);
        v.style.filter = g <= 0 ? '' : `grayscale(${g.toFixed(3)})`;
      }
      // « Fin », puis le titre et les dates : en fondu.
      elFin.style.opacity = entre(t, accord - 0.05, F.fonduFin).toFixed(3);
      const a = entre(t, accord + F.titre, F.fonduTexte);
      titres.style.opacity = a.toFixed(3);
      lettresTitre.forEach((l) => (l.style.opacity = '1'));
      filet.style.transform = 'scaleX(1)';
      lettresDates.forEach((l) => (l.style.opacity = '1'));
    }
  }
  function boucle() {
    raf = 0;
    if (!lec.enGenerique) return;
    rendre(Math.min(chrono.t, duree()));
    majTemps();
    reglerSon();
    if (chrono.tourne) raf = requestAnimationFrame(boucle);
  }

  /** Hors plein écran, le générique couvre le lecteur jusqu'à la barre des actes (titre d'acte et
   *  sous-titres compris) ; en plein écran, tout l'écran, sous les bandeaux. */
  const barre = racine.querySelector<HTMLElement>('.lecteur__progression');
  function caler() {
    const plein = document.fullscreenElement === lecteur;
    el!.style.bottom = !barre || plein ? '0' : `${Math.max(0, lecteur.clientHeight - barre.offsetTop)}px`;
  }
  new ResizeObserver(caler).observe(lecteur);
  document.addEventListener('fullscreenchange', caler);

  function montrer(ph: Phase) {
    phase = ph;
    charger();
    caler();
    el!.classList.toggle('generique--fin', ph === 'fin');
    el!.setAttribute('aria-hidden', 'false');
    el!.classList.add('est-visible');
    lecteur.classList.add('en-generique');
    chrono.zero();
    rendre(0);
    reglerSon();
    son.src = ph === 'ouverture' ? G!.ouverture.src : G!.fin.src;
  }
  /** Lancement (geste de l'utilisateur) : l'ouverture si l'on part du début ; sinon le lecteur
   *  de l'indicatif est seulement amorcé (iOS), pour le récapitulatif. Vrai si l'ouverture joue. */
  function ouvrirGenerique(k: number) {
    if (k !== 0) {
      if (!amorce) {
        amorce = true;
        son.src = G!.fin.src;
        son.muted = true;
        son.play().then(() => { if (!lec.enGenerique) son.pause(); son.muted = false; }).catch(() => { son.muted = false; });
      }
      return false;
    }
    amorce = true;
    lec.i = 0;
    lec.enGenerique = 'ouverture';
    montrer('ouverture');
    lec.demarrer();
    return true;
  }
  /** Après la dernière diapositive : le récapitulatif (faux sans générique). */
  function lancerRecapitulatif() {
    arreterMinuterie();
    lec.audio.pause();
    lec.sa.pause();
    lec.enGenerique = 'fin';
    montrer('fin');
    lec.musique();
    lec.demarrer();
    return true;
  }
  function reprendreGenerique() {
    chrono.relancer();
    arreterMinuterie();
    const reste = Math.max(0, duree() - chrono.t);
    lec.minuterie = window.setTimeout(finPhase, reste * 1000);
    reglerSon();
    if (son.paused && chrono.t < duree() - 0.05) {
      try { son.currentTime = chrono.t; } catch { /* pas encore chargé */ }
      son.play().catch(() => { /* bloqué : le générique continue sans musique */ });
    }
    if (!raf) raf = requestAnimationFrame(boucle);
  }
  function figerGenerique() {
    if (!lec.enGenerique) return;
    chrono.figer();
    son.pause();
    rendre(Math.min(chrono.t, duree()));
  }
  function finPhase() {
    lec.minuterie = 0;
    if (lec.enGenerique === 'ouverture') {
      lec.enGenerique = null;
      resonner = true; // l'accord final résonne sous le carton (pas de fondu de sortie)
      lec.aller(0); // premier carton ; le générique s'efface dessus (quitterGenerique)
    } else if (lec.enGenerique === 'fin') {
      chrono.figer();
      chrono.ecoule = genFin;
      rendre(genFin);
      lec.enGenerique = null;
      // Dernière image tenue ; la position mémorisée est oubliée (diaporama fini).
      lec.pause();
      ecrire(CLE_POS, null);
    }
  }
  /** → , clic, Entrée : l'ouverture laisse place au premier carton ; le récapitulatif va à sa fin. */
  function passerGenerique() {
    if (lec.enGenerique === 'fin') {
      son.pause();
      return finPhase();
    }
    finPhase();
  }
  /** Saut ailleurs (ou fin de l'ouverture) : le générique s'efface, son indicatif en fondu. */
  function quitterGenerique() {
    if (!lec.enGenerique && !el!.classList.contains('est-visible')) return;
    lec.enGenerique = null;
    chrono.figer();
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
    el!.classList.remove('est-visible');
    el!.setAttribute('aria-hidden', 'true');
    lecteur.classList.remove('en-generique');
    const laisser = resonner;
    resonner = false;
    if (!son.paused && !laisser) {
      const v0 = son.volume, t0 = performance.now();
      const baisser = () => {
        const p = (performance.now() - t0) / 600;
        if (p >= 1 || son.paused) { son.pause(); return; }
        son.volume = v0 * (1 - p);
        requestAnimationFrame(baisser);
      };
      requestAnimationFrame(baisser);
    }
  }
  /** Instant du diaporama pendant le générique (barre de progression, temps écoulé). */
  function tempsGenerique(): number | null {
    if (!lec.lance) return lec.i === 0 ? 0 : null;
    if (lec.enGenerique === 'ouverture') return Math.min(chrono.t, genOuverture);
    if (lec.enGenerique === 'fin' || el!.classList.contains('est-visible') && phase === 'fin') {
      return lec.total - genFin + Math.min(chrono.t, genFin);
    }
    return null;
  }

  // Tests et captures : passer, ou aller au récapitulatif (en lecture depuis son début).
  (racine as any).__generique = (quoi: 'passer' | 'fin') => {
    if (quoi === 'passer') { if (lec.enGenerique) passerGenerique(); return; }
    lec.aller(N - 1);
    lancerRecapitulatif();
  };
}
