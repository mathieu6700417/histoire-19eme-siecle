// Carton de changement d'acte : lancement, minuterie, passage, ouverture en deux volets sur le
// détail zoomé (`x.ouv`), fin. Lit `lec.chronoCarton`, `lec.enCarton`, `lec.ouvre`.
// Spec 12, « Cartouches lisibles et cartons plus longs » (sortie en deux volets).
import { OUVERTURE } from './constantes';
import { mouvementReduit } from './outils';
import type { Lecteur } from './contexte';

export function installerCartons(lec: Lecteur) {
  const { animer, assurerFin, calques, chronoCarton, chronoEntree, elCarton, lecteur, majTemps, prelude,
    quandPrete, rendre, tempsOuverture } = lec;
  Object.assign(lec, { finirVolets, lancerCarton, majVolets, passerCarton, retablirWillChange });
  // --- Carton de changement d'acte ---------------------------------------------------------
  function lancerCarton() {
    if (!lec.enCarton || chronoCarton.tourne) return;
    chronoCarton.relancer();
    programmerCarton();
    animer();
  }
  /** Volets possibles (sinon, fondu court à la fin du carton). */
  const voletsPossibles = () => !mouvementReduit.matches && typeof elCarton.animate === 'function';
  /** Prochaine échéance du carton qui tourne : début de l'ouverture, puis fin du carton. */
  function programmerCarton() {
    lec.arreterMinuterie();
    if (!lec.enCarton || !chronoCarton.tourne) return;
    const t = chronoCarton.t, debut = prelude[lec.i] - OUVERTURE;
    if (!lec.ouvre && voletsPossibles()) {
      if (t < debut) { lec.minuterie = window.setTimeout(commencerOuverture, (debut - t) * 1000); return; }
      return commencerOuverture();
    }
    lec.minuterie = window.setTimeout(finCarton, Math.max(0, prelude[lec.i] - t) * 1000);
  }
  /** Début de l'ouverture (dernières secondes du carton) : l'image est posée sous le carton,
   *  cadrée sur son détail d'ouverture s'il y en a un ; les volets s'écartent une fois l'image
   *  décodée, au rythme de l'horloge du carton. */
  function commencerOuverture() {
    if (!lec.enCarton || lec.ouvre) return;
    lec.ouvre = true;
    programmerCarton();
    lec.entrerImage(true, true);
    chronoEntree.zero(); // l'entrée suit l'horloge du carton (cf. rendre)
    // Sans `will-change` pendant l'ouverture, Chrome rastérise l'image à l'échelle où elle est
    // posée (le zoom le plus fort) au lieu de garder celle de l'image d'avant ; il est rétabli
    // au début du recul (`finCarton`), qui ne fait que dézoomer.
    calques[lec.visible].querySelector('img')!.style.willChange = 'auto';
    const k = lec.i;
    quandPrete(calques[lec.visible].querySelector('img')!, () => {
      if (k !== lec.i || !lec.enCarton || !lec.ouvre) return; // saut ou carton passé entre-temps
      ouvrirCarton();
      rendre();
      animer();
    });
  }
  /** Passer le carton (→, clic, Entrée) : l'ouverture se joue tout de suite (l'horloge du
   *  carton saute à son début, et tourne même en pause), la voix démarre à sa fin. Passé
   *  pendant l'ouverture : le carton finit aussitôt. */
  function passerCarton() {
    if (lec.enGenerique) return lec.passerGenerique(); // le générique se passe comme un carton
    if (!lec.enCarton) return;
    if (lec.ouvre || !voletsPossibles()) return finCarton();
    chronoCarton.figer();
    chronoCarton.ecoule = Math.max(chronoCarton.ecoule, prelude[lec.i] - OUVERTURE);
    chronoCarton.relancer();
    programmerCarton();
    animer();
  }
  /** Fin du carton (fin de l'ouverture, ou passé) : la voix démarre si la lecture est en cours. */
  function retablirWillChange() { for (const c of calques) c.querySelector('img')!.style.willChange = ''; }
  function finCarton() {
    if (!lec.enCarton) return;
    retablirWillChange();
    lec.arreterMinuterie();
    const ouvert = lec.ouvre, e = tempsOuverture();
    lec.enCarton = false;
    lec.ouvre = false;
    chronoCarton.zero();
    elCarton.setAttribute('aria-hidden', 'true');
    if (ouvert) {
      // L'image est déjà là : la caméra passe de l'horloge du carton à celle de l'audio sans
      // rupture (instant 0). Ouverture écourtée : l'entrée finit sur son horloge propre.
      finirVolets();
      lecteur.classList.remove('en-carton');
      chronoEntree.zero();
      chronoEntree.ecoule = e;
      chronoEntree.relancer();
      animer();
      assurerFin();
      if (lec.joue) lec.demarrer();
      rendre();
      majTemps();
      lec.musique();
      return;
    }
    // Sans volets (prefers-reduced-motion) : l'image est posée sous le carton, qui s'efface
    // une fois l'image décodée.
    lec.entrerImage(true, true);
    const k = lec.i;
    quandPrete(calques[lec.visible].querySelector('img')!, () => {
      if (k !== lec.i || lec.enCarton) return; // saut entre-temps
      ouvrirCarton();
      chronoEntree.zero();
      chronoEntree.relancer();
      animer();
      assurerFin();
      if (lec.joue) lec.demarrer();
      majTemps();
      lec.musique();
    });
  }

  // Volets (spec 12, « Sortie du carton d'acte en deux volets ») : deux copies du carton,
  // coupées à mi-hauteur par clip-path, s'écartent vers le haut et vers le bas et découvrent
  // l'image déjà posée et décodée dessous. Le vrai carton disparaît d'un coup sous les volets
  // (son fondu se verrait entre eux). Animation en transform seul, tenue en pause et placée à
  // chaque image sur l'horloge du carton (figée en pause, juste après un saut).
  const COURBE_VOLETS = 'cubic-bezier(0.45, 0, 0.2, 1)'; // départ doux, longue fin apaisée
  let volets: { els: HTMLElement[]; anims: Animation[] } | null = null;
  function finirVolets() {
    if (!volets) return;
    for (const a of volets.anims) a.cancel();
    for (const el of volets.els) el.remove();
    volets = null;
  }
  function majVolets() {
    if (!volets || !lec.enCarton) return;
    const ms = tempsOuverture() * 1000;
    for (const a of volets.anims) a.currentTime = ms;
  }
  function ouvrirCarton() {
    finirVolets();
    if (!voletsPossibles()) {
      lecteur.classList.remove('en-carton'); // fondu court (CSS)
      return;
    }
    lec.majFriseCarton(); // la frise animée, à son état du moment, est copiée dans les volets
    const els = (['haut', 'bas'] as const).map((cote) => {
      const v = elCarton.cloneNode(true) as HTMLElement;
      v.classList.add('lecteur__volet', `lecteur__volet--${cote}`);
      v.removeAttribute('data-action');
      v.removeAttribute('title');
      v.setAttribute('aria-hidden', 'true');
      for (const n of v.querySelectorAll('[id]')) n.removeAttribute('id');
      return v;
    });
    elCarton.after(...els);
    elCarton.style.transition = 'none';
    lecteur.classList.remove('en-carton');
    void elCarton.offsetWidth;
    elCarton.style.transition = '';
    const anims = els.map((v, k) => v.animate(
      [{ transform: 'translate3d(0, 0, 0)' }, { transform: `translate3d(0, ${k ? 51 : -51}%, 0)` }],
      { duration: OUVERTURE * 1000, easing: COURBE_VOLETS, fill: 'forwards' }));
    for (const a of anims) a.pause();
    volets = { els, anims };
    majVolets();
  }
}
