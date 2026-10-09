// Navigation et lecture : afficher une diapositive, démarrer, pause, fin de voix, enchaînement
// (suivant, aller, segment), écouteurs des deux lecteurs audio. Écrit `lec.i`, `lec.joue`, `lec.lance`.
// Spec 12, « Lecteur (`Diaporama.astro`) ».
import { ecrire, mouvementReduit } from './outils';
import type { Lecteur } from './contexte';

export function installerNavigation(lec: Lecteur) {
  const { CLE_POS, D, N, acteDe, animer, arreterSuite, audio, btnLecture, cacherFrise, calques,
    changeFrise, changerCartouche, changerSousTitre, chargerSurimpressions, chronoCarton, chronoEntree,
    depart, elActeDates, elActeTitre, elCarton, elCartonDates, elCartonTitre, elLegende, elN,
    estomperPlusTard, finSuite, finirVolets, friseCarton, lancerCarton, lancerSuite, lecteur, majSuite,
    majTemps, mesurerMarges, montrerFrise, montrerImage, passerCarton, poserActe, precharger, prelude,
    quandPrete, rendre, retablirWillChange, sa, voixEtPause } = lec;
  Object.assign(lec, { aller, allerSuite, arreterMinuterie, basculer, demarrer, entrerImage, lancer,
    pause, suivant, suivantAuto });
  // --- Lecture -----------------------------------------------------------------------------
  function arreterMinuterie() { clearTimeout(lec.minuterie); lec.minuterie = 0; }

  /** Cartouche, sous-titre puis image de la diapositive courante (marges mesurées entre-temps). */
  function entrerImage(fondu: boolean, couvert = false) {
    const x = D.diapos[lec.i];
    changerCartouche(x);
    changerSousTitre(x.texte);
    chargerSurimpressions(x);
    mesurerMarges();
    montrerImage(x, fondu, couvert);
  }

  function afficher(k: number, fondu = true) {
    lec.quitterGenerique();
    finirVolets();
    retablirWillChange();
    // Écran couvrant l'image avant le changement : carton d'acte, carte ou panneau d'un segment.
    // (Pendant l'ouverture des volets, l'image est déjà découverte : fondu enchaîné ordinaire.)
    const sousCarton = lec.enCarton && !lec.ouvre;
    const carte = lec.ov && (lec.enSuite || lec.suiteFini) ? lec.ov : null;
    arreterMinuterie();
    arreterSuite(Boolean(carte));
    /** Retire la carte (ou le panneau) gardée pendant le changement, sauf si elle a resservi. */
    const leverCarte = () => {
      if (carte && carte !== lec.ov) { carte.classList.remove('est-visible'); carte.setAttribute('aria-hidden', 'true'); }
    };
    lec.i = Math.max(0, Math.min(N - 1, k));
    const x = D.diapos[lec.i];
    const a = D.actes[acteDe[lec.i]];
    // Date précédente : celle de la dernière diapositive affichée (sauts manuels compris).
    const datePrec = lec.derniere >= 0 ? D.diapos[lec.derniere].date : null;
    if (lec.lance) lec.derniere = lec.i;
    elActeTitre.textContent = a.titre;
    elActeDates.textContent = a.dates;
    elN.textContent = String(x.n);
    audio.pause();
    if (x.audio) audio.src = x.audio; else audio.removeAttribute('src');
    lec.ecouleSansVoix = 0; lec.debutSansVoix = 0;
    if (lec.lance) ecrire(CLE_POS, x.cle);
    precharger(lec.i);
    chronoCarton.zero();
    lec.ouvre = false;
    if (lec.lance && prelude[lec.i]) {
      // Carton d'acte : il couvre la scène ; l'image d'avant reste figée dessous.
      lec.enCarton = true;
      lec.enEntree = false;
      chronoEntree.zero();
      // Titre écrit lettre par lettre (mots insécables : pas de coupure au milieu d'un mot).
      let n = 0;
      elCartonTitre.replaceChildren(...a.titre.split(/(\s+)/).map((m) => {
        if (/^\s+$/.test(m)) return document.createTextNode(m);
        const mot = document.createElement('span');
        mot.className = 'mot';
        for (const c of m) { const l = document.createElement('span'); l.textContent = c; l.style.setProperty('--i', String(n++)); mot.append(l); }
        return mot;
      }));
      elCartonTitre.setAttribute('aria-label', a.titre);
      elCarton.style.setProperty('--lettres', String(n));
      elCartonDates.textContent = a.dates;
      elCarton.setAttribute('aria-hidden', 'false');
      cacherFrise();
      chargerSurimpressions(null);
      // Frise du carton : l'intervalle de l'acte (segment épais, en fondu), sans curseur ni date.
      if (friseCarton) poserActe(friseCarton, acteDe[lec.i]);
      // Retirer puis remettre la classe relance l'animation des textes du carton.
      lecteur.classList.remove('en-carton');
      void elCarton.offsetWidth;
      lecteur.classList.add('en-carton');
      // La carte d'un segment reste le temps que le carton monte (pas d'éclair de l'image dessous).
      if (carte) window.setTimeout(leverCarte, 500);
      majTemps();
      if (lec.joue) demarrer();
      lec.musique();
      return;
    }
    lec.enCarton = false;
    elCarton.setAttribute('aria-hidden', 'true');
    const couvert = sousCarton || Boolean(carte);
    entrerImage(fondu, couvert);
    if (couvert && fondu) {
      // L'écran couvrant ne se lève qu'une fois la nouvelle image décodée, posée dessous.
      const j = lec.i;
      quandPrete(calques[lec.visible].querySelector('img')!, () => {
        leverCarte();
        if (j === lec.i && !lec.enCarton) lecteur.classList.remove('en-carton');
      });
    } else {
      leverCarte();
      lecteur.classList.remove('en-carton');
    }
    // Entre deux cartons : la frise en bas de l'image à chaque changement d'année ou retour en arrière.
    if (lec.lance && datePrec && x.date && changeFrise(datePrec, x.date)) montrerFrise(datePrec, x.date);
    else cacherFrise();
    majTemps();
    if (lec.joue) demarrer();
    lec.musique();
  }

  function demarrer() {
    const x = D.diapos[lec.i];
    lec.joue = true;
    lecteur.classList.add('en-lecture');
    btnLecture.setAttribute('aria-label', 'Pause');
    animer();
    lec.musique();
    if (lec.enGenerique) return lec.reprendreGenerique();
    if (lec.enCarton) return lancerCarton();
    if (lec.enSuite) {
      sa.play().catch((e) => { if (e?.name !== 'AbortError') finSuite(); });
      return;
    }
    if (lec.suiteFini) {
      lec.minuterie = window.setTimeout(suivantAuto, D.pause * 1000);
      return;
    }
    if (x.audio) {
      if (audio.ended) return finDeVoix();
      if (audio.error) return finDeVoix();
      // AbortError : la source a changé avant le début de la lecture (saut rapide).
      audio.play().catch((e) => { if (e?.name !== 'AbortError') pause(); });
    } else {
      lec.debutSansVoix = performance.now();
      lec.minuterie = window.setTimeout(suivantAuto, (voixEtPause[lec.i] - lec.ecouleSansVoix) * 1000);
    }
  }
  function pause() {
    lec.joue = false;
    lecteur.classList.remove('en-lecture');
    btnLecture.setAttribute('aria-label', 'Lecture');
    audio.pause();
    sa.pause();
    if (lec.minuterie && lec.debutSansVoix && !lec.enCarton) lec.ecouleSansVoix += (performance.now() - lec.debutSansVoix) / 1000;
    lec.debutSansVoix = 0;
    arreterMinuterie();
    chronoCarton.figer();
    lec.figerGenerique();
    if (lec.raf && !(lec.enEntree && chronoEntree.tourne)) { cancelAnimationFrame(lec.raf); lec.raf = 0; }
    rendre();
    majTemps();
    lec.montrerControles();
    lec.musique();
  }
  function finDeVoix() {
    if (!lec.joue || lec.enCarton || lec.enSuite) return;
    arreterMinuterie();
    lec.minuterie = window.setTimeout(apresVoix, D.diapos[lec.i].pause * 1000);
  }
  /** Après la voix et sa pause : l'intermède chanté s'il y en a un, sinon la suite. */
  function apresVoix() {
    lec.minuterie = 0;
    const c = D.diapos[lec.i].suite;
    if (c && !lec.suiteFini) return lancerSuite();
    suivantAuto();
  }
  /** Saut direct vers le segment d'une diapositive (clic dans la barre de progression) : la
   *  diapositive s'affiche, sans sa voix ni son carton, puis le segment commence. */
  function allerSuite(j: number) {
    aller(j);
    if (lec.enCarton) {
      arreterMinuterie();
      lec.enCarton = false;
      lec.ouvre = false;
      finirVolets();
      chronoCarton.zero();
      lecteur.classList.remove('en-carton');
      elCarton.setAttribute('aria-hidden', 'true');
      entrerImage(false);
    }
    arreterMinuterie();
    audio.pause();
    try { audio.currentTime = Math.max(0, D.diapos[lec.i].duree - 0.05); } catch { /* pas encore chargé */ }
    lancerSuite();
  }
  function suivantAuto() {
    lec.minuterie = 0;
    if (lec.i >= N - 1) {
      if (lec.lancerRecapitulatif()) return; // il finit par la pause et l'oubli de la position
      pause(); ecrire(CLE_POS, null); return;
    }
    afficher(lec.i + 1);
  }
  function lancer(k = 0) {
    lec.deverrouillerAudio();
    lec.lance = true;
    depart.hidden = true;
    lec.joue = true;
    // Générique d'ouverture au tout début (pas à une reprise), sinon la diapositive k.
    if (!lec.ouvrirGenerique(k)) afficher(k, k !== lec.i);
    estomperPlusTard(elLegende);
    btnLecture.focus({ preventScroll: true });
    // Le lecteur entier à l'écran, s'il dépasse.
    const r = lecteur.getBoundingClientRect();
    if (r.top < 0 || r.bottom > window.innerHeight) lecteur.scrollIntoView({ behavior: mouvementReduit.matches ? 'auto' : 'smooth', block: 'start' });
  }
  function basculer() {
    lec.deverrouillerAudio();
    if (!lec.lance) return lancer(lec.i);
    lec.joue ? pause() : demarrer();
  }
  function aller(k: number) {
    k = Math.max(0, Math.min(N - 1, k));
    if (!lec.lance) { lec.lance = true; depart.hidden = true; }
    lec.quitterGenerique();
    if (k === lec.i && !prelude[lec.i] && !lec.enCarton) {
      // Retour au début de la diapositive courante (sans carton).
      arreterMinuterie();
      if (lec.enSuite || lec.suiteFini) {
        arreterSuite();
        changerCartouche(D.diapos[lec.i]);
        changerSousTitre(D.diapos[lec.i].texte);
      }
      audio.currentTime = 0; lec.ecouleSansVoix = 0; lec.debutSansVoix = 0;
      rendre(0);
      lec.musique();
      if (lec.joue) demarrer();
      majTemps();
      return;
    }
    afficher(k);
  }
  /** « Suivant » : passe le carton s'il est affiché, sinon diapositive suivante. */
  function suivant() {
    if (lec.enGenerique) return lec.passerGenerique();
    if (lec.enCarton) return passerCarton();
    aller(lec.i + 1);
  }

  audio.addEventListener('ended', finDeVoix);
  for (const ev of ['play', 'playing', 'pause', 'ended', 'waiting']) audio.addEventListener(ev, () => lec.appliquerEtat());
  sa.addEventListener('ended', finSuite);
  for (const ev of ['play', 'playing', 'pause', 'ended', 'waiting']) sa.addEventListener(ev, () => lec.appliquerEtat());
  sa.addEventListener('error', () => { if (lec.enSuite && sa.getAttribute('src')) finSuite(); });
  sa.addEventListener('timeupdate', () => { majSuite(); majTemps(); });
  sa.addEventListener('seeked', () => majSuite());
  // timeupdate (et seeked) recalent aussi la caméra : utile après un saut en pause, et quand
  // requestAnimationFrame est suspendu (onglet en arrière-plan).
  audio.addEventListener('timeupdate', () => { if (!lec.enCarton) { majTemps(); rendre(); } });
  audio.addEventListener('seeked', () => rendre());
  audio.addEventListener('error', () => { if (lec.joue && !lec.enCarton && audio.getAttribute('src')) finDeVoix(); });
}
