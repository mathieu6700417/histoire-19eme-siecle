// Musique de fond (Web Audio) : deux lecteurs en fondu, gain selon l'état (voix, respiration,
// carton, chant), position dans l'acte, bouton et volume. Test : `__musique()`.
// Spec 12, « Musique » ; README : « Musique : format et sources ».
import { CLE_MUSIQUE, CLE_VOLUME, FONDU_ACTE, FONDU_PISTE, GAINS, VOLUME_DEFAUT, type EtatMusique } from './constantes';
import { ecrire, lire } from './outils';
import type { Lecteur } from './contexte';

export function installerMusique(lec: Lecteur) {
  const { D, acteDe, audio, bornes, btnMusique, debuts, curseurVolume, elMusique, estomperPlusTard, racine, sa,
    tempsCourant, total } = lec;
  Object.assign(lec, { appliquerEtat, basculerMusique, deverrouillerAudio, musique });
  // --- Musique de fond (Web Audio API) ---------------------------------------------------------
  // Deux lecteurs <audio> (fondu enchaîné entre deux pistes) passent chacun par un gain de
  // fondu, puis par un gain commun de « ducking » réglé selon l'état du diaporama (voix,
  // respiration, carton, intermède, arrêt) et le volume choisi. L'AudioContext est créé et
  // débloqué au premier clic (« Lancer », lecture) : exigence d'iOS. Sans Web Audio, le
  // volume des éléments est réglé directement (sans rampe).
  // Position : les pistes d'un acte s'enchaînent depuis le début de l'acte (et bouclent) ;
  // après un saut vers un autre acte, la piste et l'instant sont déduits du temps du
  // diaporama. Dans un même acte, la musique continue sans à-coup (pause, sauts, reprise).
  const aFond = D.fond.some((l) => l.length > 0);
  let musiqueOn = lire(CLE_MUSIQUE) !== 'non';
  let volume = (() => { const v = Number(lire(CLE_VOLUME)); return lire(CLE_VOLUME) !== null && v >= 0 && v <= 1 ? v : VOLUME_DEFAUT; })();
  interface LecteurFond { el: HTMLAudioElement; g: GainNode | null; acte: number; piste: number; v: number; enchaine: boolean; arret: number }
  const fonds: LecteurFond[] = [0, 1].map(() => {
    const el = new Audio();
    el.preload = 'auto';
    return { el, g: null, acte: -1, piste: -1, v: 0, enchaine: false, arret: 0 };
  });
  let courant = -1;            // lecteur de fond actif (-1 : aucun)
  let ctx: AudioContext | null = null;
  let maitre: GainNode | null = null;
  let duck = 0;                 // gain de ducking visé (repli sans Web Audio)
  let etatMusique: EtatMusique = 'arret';
  let arretMusique = 0;
  let deverrouille = false;

  function deverrouillerAudio() {
    if (deverrouille) { void ctx?.resume(); return; }
    deverrouille = true;
    if (aFond) {
      try {
        const AC = window.AudioContext || (window as any).webkitAudioContext;
        ctx = new AC();
        maitre = ctx.createGain();
        maitre.gain.value = 0;
        maitre.connect(ctx.destination);
        for (const f of fonds) {
          f.g = ctx.createGain();
          f.g.gain.value = 0;
          ctx.createMediaElementSource(f.el).connect(f.g).connect(maitre);
        }
        void ctx.resume();
      } catch { ctx = null; maitre = null; fonds.forEach((f) => (f.g = null)); }
    }
    // iOS : chaque élément <audio> doit avoir été lancé une fois pendant un geste de
    // l'utilisateur. On amorce, en silence, le second lecteur de fond et celui des chants.
    const amorcer = (el: HTMLAudioElement, src: string | undefined) => {
      if (!src || !el.paused) return;
      if (!el.getAttribute('src')) el.src = src;
      el.muted = true;
      el.play().then(() => { if (el !== sa || !lec.enSuite) el.pause(); el.muted = false; }).catch(() => { el.muted = false; });
    };
    amorcer(sa, D.diapos.find((x) => x.suite)?.suite?.src);
    lec.amorcerAmbiance();   // ambiance des clips (spec 17)
    amorcer(fonds[1].el, D.fond.find((l) => l.length > 1)?.[1]?.src ?? D.fond.find((l) => l.length)?.[0]?.src);
  }

  function etatCourant(): EtatMusique {
    if (!lec.lance || !lec.joue || lec.enGenerique) return 'arret'; // générique : l'indicatif seul
    if (lec.enSuite) {
      // Intermède : la musique de fond se tait ; lecture et épisode : baissée comme sous la voix.
      if (D.diapos[lec.i].suite?.type === 'chant') return 'chant';
      return !sa.paused && !sa.ended ? 'voix' : 'respiration';
    }
    if (lec.enCarton) return 'carton';
    if (D.diapos[lec.i].audio && !audio.paused && !audio.ended) return 'voix';
    return 'respiration';
  }

  /** Gain d'un lecteur de fond (fondu enchaîné), en rampe linéaire sur `duree` secondes. */
  function fondre(f: LecteurFond, cible: number, duree: number) {
    if (ctx && f.g) {
      const t = ctx.currentTime, g = f.g.gain;
      g.cancelScheduledValues(t);
      g.setValueAtTime(g.value, t);
      g.linearRampToValueAtTime(cible, t + Math.max(0.02, duree));
    }
    f.v = cible;
    if (!ctx) f.el.volume = Math.min(1, Math.max(0, cible * duck));
  }

  /** Cartouche de la musique de fond (en haut à droite) : visible tant qu'une piste de fond
   *  est en cours et la musique activée ; masqué pendant un chant (son propre cartouche). */
  function afficherMusique() {
    const f = courant >= 0 ? fonds[courant] : null;
    const p = f && f.acte >= 0 ? D.fond[f.acte]?.[f.piste] : null;
    const oui = Boolean(p && musiqueOn && lec.lance && !lec.enGenerique && !(lec.enSuite && D.diapos[lec.i].suite?.type === 'chant'));
    if (p && elMusique.dataset.src !== p.src) {
      elMusique.dataset.src = p.src;
      elMusique.classList.remove('est-visible');
      void elMusique.offsetWidth;
      elMusique.innerHTML = p.info;
      estomperPlusTard(elMusique);
    }
    elMusique.classList.toggle('est-visible', oui);
  }

  /** Ducking : gain commun selon l'état (voix, respiration, carton, intermède, arrêt). À
   *  l'arrêt (pause, musique coupée), les lecteurs sont mis en pause après le fondu. */
  function appliquerEtat() {
    if (!aFond) return;
    const avant = etatMusique;
    etatMusique = etatCourant();
    afficherMusique();
    const cible = musiqueOn ? Math.min(1, GAINS[etatMusique] * (volume / VOLUME_DEFAUT)) : 0;
    const baisse = cible < duck;
    duck = cible;
    if (ctx && maitre) {
      const t = ctx.currentTime, g = maitre.gain;
      g.cancelScheduledValues(t);
      g.setValueAtTime(g.value, t);
      // La musique s'efface vite quand la voix entre, remonte plus doucement ensuite ; à la
      // sortie d'un carton d'acte (musique au premier plan), la descente est un fondu (~2 s).
      g.setTargetAtTime(cible, t, baisse ? (avant === 'carton' ? 0.6 : 0.12) : 0.5);
    } else {
      fonds.forEach((f) => (f.el.volume = Math.min(1, Math.max(0, f.v * duck))));
    }
    clearTimeout(arretMusique);
    if (cible === 0) {
      arretMusique = window.setTimeout(() => { if (duck === 0) fonds.forEach((f) => f.el.pause()); }, 700);
    }
  }

  /** Piste et instant de fond pour l'instant `t` du diaporama (acte de la diapositive courante). */
  function positionFond(t: number) {
    const a = acteDe[lec.i], liste = D.fond[a];
    if (!liste?.length) return null;
    const total = liste.reduce((s, p) => s + p.duree, 0);
    let o = Math.max(0, t - debuts[bornes[a].de]) % total, j = 0;
    while (j < liste.length - 1 && o >= liste[j].duree) { o -= liste[j].duree; j++; }
    return { a, j, o: Math.min(o, Math.max(0, liste[j].duree - FONDU_PISTE - 0.5)) };
  }

  function jouerPiste(a: number, j: number, o: number, fondu: number) {
    const sortant = courant >= 0 ? fonds[courant] : null;
    const k = courant >= 0 ? 1 - courant : 0;
    const f = fonds[k], p = D.fond[a][j];
    clearTimeout(f.arret);
    f.acte = a; f.piste = j; f.enchaine = false;
    if (f.el.getAttribute('src') !== p.src) f.el.src = p.src;
    const caler = () => { try { f.el.currentTime = o; } catch { /* pas encore prêt */ } };
    if (f.el.readyState >= 1) caler(); else f.el.addEventListener('loadedmetadata', caler, { once: true });
    if (ctx && f.g) { f.g.gain.cancelScheduledValues(ctx.currentTime); f.g.gain.setValueAtTime(0, ctx.currentTime); }
    f.v = 0;
    f.el.play().catch(() => { /* bloqué ou interrompu : resynchronisé au prochain geste */ });
    fondre(f, p.volume, fondu);
    if (sortant) {
      fondre(sortant, 0, fondu);
      clearTimeout(sortant.arret);
      sortant.arret = window.setTimeout(() => { if (fonds[courant] !== sortant) sortant.el.pause(); }, fondu * 1000 + 150);
    }
    courant = k;
    afficherMusique();
  }

  /** Musique à jour : état (ducking), piste de l'acte courant, lecture ou arrêt. */
  function musique() {
    if (!aFond) return;
    appliquerEtat();
    if (!musiqueOn || !lec.lance || !lec.joue || lec.enGenerique) return;
    const cur = courant >= 0 ? fonds[courant] : null;
    if (cur && cur.acte === acteDe[lec.i] && cur.el.getAttribute('src')) {
      // Même acte : la musique continue (ou reprend là où elle s'était arrêtée).
      if (cur.el.paused) { cur.el.play().catch(() => {}); fondre(cur, D.fond[cur.acte][cur.piste].volume, 0.3); }
      return;
    }
    const pos = positionFond(tempsCourant());
    if (!pos) {
      if (cur) { fondre(cur, 0, FONDU_ACTE); cur.acte = -1; }
      afficherMusique();
      return;
    }
    jouerPiste(pos.a, pos.j, pos.o, cur && !cur.el.paused ? FONDU_ACTE : 0.6);
  }

  // Fin d'une piste : la suivante de l'acte (ou la première, en boucle) en fondu enchaîné.
  fonds.forEach((f, k) => {
    const suite = () => {
      if (k !== courant || f.enchaine || f.acte < 0 || !lec.joue) return;
      const liste = D.fond[f.acte];
      if (!liste?.length) return;
      f.enchaine = true;
      jouerPiste(f.acte, (f.piste + 1) % liste.length, 0, FONDU_PISTE);
    };
    f.el.addEventListener('timeupdate', () => {
      if (f.el.duration && f.el.duration - f.el.currentTime < FONDU_PISTE) suite();
    });
    f.el.addEventListener('ended', suite);
  });

  function basculerMusique(oui = !musiqueOn) {
    if (!btnMusique) return;
    musiqueOn = oui;
    btnMusique.setAttribute('aria-pressed', String(oui));
    if (curseurVolume) curseurVolume.disabled = !oui;
    ecrire(CLE_MUSIQUE, oui ? 'oui' : 'non');
    if (oui) deverrouillerAudio();
    musique();
  }
  if (btnMusique) basculerMusique(musiqueOn);
  if (curseurVolume) {
    curseurVolume.value = String(Math.round(volume * 100));
    curseurVolume.addEventListener('input', () => {
      volume = Number(curseurVolume.value) / 100;
      ecrire(CLE_VOLUME, String(volume));
      appliquerEtat();
    });
  }
  // Pour les tests (onglet en arrière-plan : on lit l'état et les gains calculés).
  (racine as any).__musique = () => ({
    etat: etatMusique, duck, musiqueOn, volume, courant, ctx: ctx?.state ?? null,
    maitre: maitre?.gain.value ?? null, enSuite: lec.enSuite, suiteFini: lec.suiteFini, suite: D.diapos[lec.i].suite?.type ?? null, i: lec.i, t: tempsCourant(), total,
    fonds: fonds.map((f) => ({ src: f.el.getAttribute('src'), acte: f.acte, piste: f.piste, v: f.v, g: f.g?.gain.value ?? null, paused: f.el.paused, t: f.el.currentTime })),
  });
}
