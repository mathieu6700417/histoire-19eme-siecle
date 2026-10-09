// Rendu d'une image : préparation des calques, instant courant (horloge lissée), `rendre` (caméra,
// entrée, ouverture, avant/après, mosaïque, surimpressions), boucle requestAnimationFrame,
// affichage d'une nouvelle image. Spec 12, « Animations d'entrée », « Caméra calée sur la narration ».
import { DUREE_RECUL, FONDU, FONDU_REDUIT, OUVERTURE, RECUL, REVELATION } from './constantes';
import { adoucir } from './geometrie';
import { mouvementReduit } from './outils';
import type { Diapo, Rect, SuiteChant } from './types';
import type { Lecteur } from './contexte';

export function installerRendu(lec: Lecteur) {
  const { D, apresDe, audio, cadre, cadreA, cadreIntermede, calques, chronoCarton, chronoEntree, couches,
    debutPlongee, horloge, horlogeSuite, majApres, majMosaique, placerTuiles, principal, sa,
    tempsOuverture, transformation } = lec;
  Object.assign(lec, { animer, assurerFin, instant, legendeVoulue, montrerImage, poser, rendre });
  /** Cartouche voulu à l'instant `t` : la ligne de la mosaïque pendant la grille, celui de
   *  l'image après dès le début du volet, sinon celui de l'image. */
  function legendeVoulue(x: Diapo, t: number) {
    if (x.mos && !x.ouv && t < debutPlongee(x.mos.vignettes.length)) return x.mos.legende;
    if (x.ap && t >= x.ap.t) return x.ap.legende;
    return x.legende;
  }
  /** Pose les éléments propres d'un calque (image après, grille) pour la diapositive `x`. */
  function preparerCalque(c: HTMLElement, x: Diapo) {
    const elA = c.querySelector<HTMLElement>('.lecteur__apres')!, imgA = elA.querySelector('img')!;
    const trait = c.querySelector<HTMLElement>('.lecteur__trait')!, mo = c.querySelector<HTMLElement>('.mosaique')!;
    elA.hidden = true; trait.hidden = true; elA.style.clipPath = ''; elA.style.opacity = '';
    c.querySelector('img')!.style.visibility = '';
    c.style.background = '';
    if (x.ap) { if (imgA.getAttribute('src') !== x.ap.img) imgA.src = x.ap.img; imgA.alt = x.ap.alt; } else { imgA.removeAttribute('src'); imgA.alt = ''; }
    mo.hidden = true;
    mo.style.opacity = '';
    if (x.mos && !x.ouv) {
      if (mo.dataset.n !== String(x.n)) {
        mo.replaceChildren(...x.mos.vignettes.map((v, k) => {
          const t = document.createElement('div');
          t.className = `tuile${k === x.mos!.principale ? ' tuile--principale' : ''}`;
          const im = document.createElement('img');
          im.alt = ''; im.decoding = 'async';
          im.src = k === x.mos!.principale ? x.img : v.img;
          t.append(im);
          return t;
        }));
        mo.dataset.n = String(x.n);
      }
    } else { mo.replaceChildren(); delete mo.dataset.n; }
  }
  lec.legendeMontree = '';

  /** Instant courant de la voix de la diapositive : l'audio fait foi, lissé (`horloge`). */
  function instant() {
    return D.diapos[lec.i].audio
      ? horloge.lire(audio)
      : lec.ecouleSansVoix + (lec.joue && lec.debutSansVoix ? (performance.now() - lec.debutSansVoix) / 1000 : 0);
  }

  /** Pose un calque figé sur son dernier cadre (calque sortant, ou image d'avant un carton). */
  function poser(k: number) {
    const x = couches[k].x;
    if (!x) return;
    calques[k].querySelector('img')!.style.transform = transformation(calques[k], x, couches[k].r);
    const ra = couches[k].ra;
    if (x.ap && ra) {
      const imgA = calques[k].querySelector<HTMLImageElement>('.lecteur__apres img')!;
      imgA.style.transform = transformation(calques[k], apresDe(x), ra, 1, imgA);
    }
  }

  /** Rendu de l'image visible : caméra (horloge de l'audio) × entrée (horloge propre). */
  /** Durée de l'entrée d'une image : sur un détail d'ouverture, les couleurs montent pendant
   *  toute l'ouverture des volets et la caméra fait le recul (pas d'agrandissement d'entrée). */
  const revelation = (x: Diapo) => (x.ouv ? OUVERTURE : REVELATION);
  const dureeEntree = (x: Diapo) => (mouvementReduit.matches ? FONDU_REDUIT : Math.max(FONDU, revelation(x), x.ouv ? 0 : DUREE_RECUL));

  function rendre(t = instant()) {
    lec.majVolets();
    const c = calques[lec.visible], x = couches[lec.visible].x;
    if (x !== D.diapos[lec.i]) return; // carton : l'image de la diapositive n'est pas encore entrée
    const img = c.querySelector('img')!;
    const reduit = mouvementReduit.matches;
    // Pendant l'ouverture du carton, l'entrée et la caméra suivent l'horloge du carton (figée
    // en pause) ; la caméra y vit aux instants négatifs, juste avant la voix.
    const ouv = lec.enCarton && lec.ouvre;
    const e = ouv ? tempsOuverture() : lec.enEntree ? chronoEntree.t : Infinity;
    const opacite = lec.entreeNette ? 1 : adoucir(e / (reduit ? FONDU_REDUIT : FONDU));
    const gris = reduit ? 0 : 1 - adoucir(e / revelation(x));
    const f = reduit || x.ouv ? 1 : 1 + RECUL * (1 - adoucir(e / DUREE_RECUL));
    lec.majSurimpressions(t);
    // Intermède avec un cadre : la caméra suit l'horloge de l'intermède.
    const su = x.suite;
    const tv = ouv ? tempsOuverture() - OUVERTURE : t;
    const r = su?.type === 'chant' && su.cadre && (lec.enSuite || lec.suiteFini)
      ? cadreIntermede(x, su as SuiteChant & { cadre: Rect }, lec.suiteFini ? su.duree : horlogeSuite.lire(sa))
      : cadreA(principal(x), tv);
    couches[lec.visible].r = r;
    img.style.transform = transformation(c, x, r, f);
    // Avant / après, mosaïque ; puis le cartouche voulu à cet instant (pas pendant un segment).
    if (x.ap) majApres(c, x, tv);
    if (x.mos && !x.ouv) majMosaique(c, x, tv);
    if (lec.lance && !lec.enCarton && !lec.enSuite && !lec.suiteFini) {
      const v = legendeVoulue(x, tv);
      if (v !== lec.legendeMontree) lec.changerLegende(v);
    }
    img.style.filter = gris > 0.002 ? `grayscale(${gris.toFixed(3)})` : '';
    c.style.opacity = opacite.toFixed(3);
    if (opacite >= 1 && lec.sortant >= 0) {
      calques[lec.sortant].style.opacity = '0';
      calques[lec.sortant].classList.remove('est-visible');
      lec.sortant = -1;
    }
    if (lec.enEntree && !ouv && e >= dureeEntree(x)) {
      lec.enEntree = false;
      chronoEntree.zero();
    }
  }

  lec.raf = 0;
  function boucle(ts: number) {
    horloge.image = horlogeSuite.image = ts / 1000;
    rendre();
    if (lec.enCarton) lec.majTemps();
    if (lec.enSuite) lec.majSuite();
    lec.raf = lec.joue || (lec.enEntree && chronoEntree.tourne) || chronoCarton.tourne ? requestAnimationFrame(boucle) : 0;
  }
  function animer() { if (!lec.raf) lec.raf = requestAnimationFrame(boucle); }
  // Onglet en arrière-plan (requestAnimationFrame suspendu) : l'état final de l'entrée est
  // posé quand même.
  let filet = 0;
  function assurerFin() {
    clearTimeout(filet);
    filet = window.setTimeout(() => { rendre(); if (lec.enEntree && chronoEntree.tourne) assurerFin(); }, 2000);
  }

  /** Met l'image de la diapositive courante à l'écran ; `fondu` : avec l'entrée animée. */
  function montrerImage(x: Diapo, fondu: boolean, couvert = false) {
    const ancien = lec.visible;
    const k = fondu ? 1 - lec.visible : lec.visible;
    const c = calques[k];
    const img = c.querySelector('img')!;
    cadre(c, x);
    if (img.getAttribute('src') !== x.img) img.src = x.img;
    img.alt = x.alt;
    preparerCalque(c, x);
    placerTuiles(c, x);
    couches[k] = { x, r: cadreA(principal(x), 0), ra: null };
    lec.entreeNette = fondu && couvert;
    if (lec.entreeNette) {
      // Sous un écran couvrant : l'ancienne image disparaît tout de suite (jamais d'éclair à la
      // levée de l'écran) ; la nouvelle, opaque, garde la révélation gris → couleur et le recul.
      for (const [j, a] of calques.entries()) {
        if (j === k) continue;
        a.style.opacity = '0';
        a.classList.remove('est-visible');
        a.querySelector('img')!.alt = '';
      }
      lec.sortant = -1;
    }
    if (fondu) {
      // Le calque entrant passe au-dessus ; l'ancien reste opaque dessous, figé.
      if (lec.sortant >= 0 && lec.sortant !== ancien) calques[lec.sortant].style.opacity = '0';
      const a = calques[ancien];
      a.style.zIndex = '0';
      if (!lec.entreeNette) a.style.opacity = '1';
      a.querySelector('img')!.alt = '';
      c.style.zIndex = '1';
      c.style.opacity = lec.entreeNette ? '1' : '0';
      c.classList.add('est-visible');
      lec.visible = k;
      lec.sortant = lec.entreeNette ? -1 : ancien;
      lec.enEntree = true;
      chronoEntree.zero();
      chronoEntree.relancer();
      animer();
      assurerFin();
    } else {
      lec.enEntree = false;
      chronoEntree.zero();
    }
    rendre();
  }
}
