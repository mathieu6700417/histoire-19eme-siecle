// État de base d'un lecteur : données (JSON), éléments du DOM, durées et débuts de chaque
// diapositive, bornes des actes, variables d'état partagées (`lec.i`, `lec.joue`, `lec.enCarton`…).
// Spec 12, « Lecteur (`Diaporama.astro`) ».
import { OUVERTURE } from './constantes';
import { Chrono, HorlogeLissee } from './horloge';
import { mmss } from './outils';
import type { Diapo, Donnees, Rect } from './types';
import type { Lecteur } from './contexte';

export function installerEtat(lec: Lecteur) {
  const { racine } = lec;
  Object.assign(lec, { quandPrete });
  const D: Donnees = JSON.parse(racine.querySelector('.diaporama__donnees')!.textContent!);
  const $ = <T extends HTMLElement = HTMLElement>(s: string) => racine.querySelector(s) as T;
  const lecteur = $('.lecteur');
  const scene = $('.lecteur__scene');
  const calques = [...racine.querySelectorAll<HTMLElement>('.lecteur__calque')];
  const audio = $<HTMLAudioElement>('.lecteur__audio');
  const sa = $<HTMLAudioElement>('.lecteur__suite'); // lecteur des segments (chant, lecture, épisode)
  const elActe = $('.lecteur__acte'), elLegende = $('.lecteur__legende'), elSt = $('.lecteur__soustitre');
  const elMusique = $('.lecteur__musique');
  const elClipTexte = $('.clip__texte');
  const elActeTitre = $('.lecteur__acte-titre'), elActeDates = $('.lecteur__acte-dates');
  const elCarton = $('.lecteur__carton'), elCartonTitre = $('.lecteur__carton-titre'), elCartonDates = $('.lecteur__carton-dates');
  const elN = $('.lecteur__n'), elEcoule = $('.lecteur__ecoule'), elTotal = $('.lecteur__total');
  const depart = $('.lecteur__depart'), btnReprendre = $<HTMLButtonElement>('.lecteur__reprendre');
  const btnLecture = $<HTMLButtonElement>('.lecteur__btn--lecture');
  const btnSt = $<HTMLButtonElement>('[data-action="sous-titres"]');
  const btnPe = $<HTMLButtonElement>('[data-action="plein-ecran"]');
  const btnMusique = racine.querySelector<HTMLButtonElement>('[data-action="musique"]');
  const curseurVolume = racine.querySelector<HTMLInputElement>('.lecteur__volume');
  const segments = [...racine.querySelectorAll<HTMLButtonElement>('.lecteur__segment')];
  const CLE_POS = `diaporama:${D.slug}`;
  const VOLET_S = D.volet, MOSAIQUE_T = D.mosaique;
  const debutPlongee = (n: number) => MOSAIQUE_T.apparition + n * MOSAIQUE_T.pas + MOSAIQUE_T.tenue;
  const N = D.diapos.length;

  // Acte de chaque diapositive ; un carton précède la première diapositive de chaque acte.
  const acteDe = D.diapos.map((x) => { let a = 0; D.actes.forEach((y, k) => { if (y.debut <= x.n) a = k; }); return a; });
  const prelude = D.diapos.map((_, k) => (k === 0 || acteDe[k] !== acteDe[k - 1] ? D.carton : 0));

  // Durées : chaque diapositive dure son carton éventuel + sa voix + la pause (6 s si la
  // voix manque).
  const voixEtPause = D.diapos.map((x) => (x.duree || 6) + x.pause);
  // Segment éventuel après la voix (intermède chanté, lecture, épisode), suivi lui aussi de la pause.
  const suiteEtPause = D.diapos.map((x) => (x.suite ? x.suite.duree + D.pause : 0));
  const durees = D.diapos.map((_, k) => prelude[k] + voixEtPause[k] + suiteEtPause[k]);
  const debuts: number[] = [];
  durees.reduce((s, x, i) => ((debuts[i] = s), s + x), 0);
  const total = debuts[N - 1] + durees[N - 1];
  elTotal.textContent = mmss(total);

  // Barre de progression : un segment par acte, de largeur proportionnelle à sa durée.
  const bornes = D.actes.map((a, i) => {
    const de = D.diapos.findIndex((x) => x.n >= a.debut);
    const fin = i < D.actes.length - 1 ? D.diapos.findIndex((x) => x.n >= D.actes[i + 1].debut) : N;
    return { de, fin, t0: debuts[de], t1: fin < N ? debuts[fin] : total };
  });
  segments.forEach((s, i) => (s.style.flexGrow = String(bornes[i].t1 - bornes[i].t0)));

  const horloge = new HorlogeLissee(), horlogeSuite = new HorlogeLissee();
  lec.i = 0;            // diapositive courante (index)
  lec.lance = false;    // le diaporama a-t-il démarré ?
  lec.joue = false;     // lecture en cours ?
  lec.visible = 0;      // calque visible (au-dessus)
  lec.sortant = -1;     // calque qui s'efface pendant un fondu enchaîné (-1 : aucun)
  lec.minuterie = 0;    // carton, pause entre deux diapositives, ou durée sans voix
  lec.debutSansVoix = 0; lec.ecouleSansVoix = 0;
  // Ce que montre chaque calque : la diapositive et le dernier cadre rendu.
  // `ra` : dernier cadre rendu de l'image après d'un avant / après (null : pas encore découverte).
  const couches: { x: Diapo | null; r: Rect; ra?: Rect | null }[] = [{ x: D.diapos[0], r: [0, 0, 1, 1] }, { x: null, r: [0, 0, 1, 1] }];
  // Carton d'acte en cours (horloge figée par la pause).
  lec.enCarton = false;
  const chronoCarton = new Chrono();
  // Ouverture du carton en cours (ses dernières secondes) : l'image est posée dessous, les volets
  // s'écartent au rythme de l'horloge du carton.
  lec.ouvre = false;
  /** Secondes écoulées dans l'ouverture du carton (0 à OUVERTURE). */
  const tempsOuverture = () => Math.min(OUVERTURE, Math.max(0, chronoCarton.t - (prelude[lec.i] - OUVERTURE)));
  // Entrée de l'image visible (fondu, gris → couleur, recul).
  lec.enEntree = false;
  const chronoEntree = new Chrono();
  // Entrée sous un écran couvrant (carton d'acte, carte de lecture, panneau d'épisode) : pas de
  // fondu enchaîné depuis l'ancienne image (elle réapparaîtrait pendant que l'écran s'efface) ;
  // la nouvelle est posée opaque dessous et l'écran ne se lève qu'une fois l'image décodée.
  lec.entreeNette = false;
  /** Attend que l'image soit décodée (au plus ~1,5 s) avant de lever l'écran qui la couvre. */
  function quandPrete(img: HTMLImageElement, fn: () => void) {
    let fait = false;
    const une = () => { if (!fait) { fait = true; fn(); } };
    window.setTimeout(une, 1500);
    (img.complete && img.naturalWidth ? img.decode() : new Promise((ok) => {
      img.addEventListener('load', ok, { once: true });
      img.addEventListener('error', ok, { once: true });
    }).then(() => img.decode())).catch(() => {}).then(une);
  }
  // Segment après la voix (intermède chanté, lecture, épisode) : en cours, ou terminé (pause
  // avant la diapositive suivante).
  lec.enSuite = false; lec.suiteFini = false;
  Object.assign(lec, { $, CLE_POS, D, MOSAIQUE_T, N, VOLET_S, acteDe, audio, bornes, btnLecture,
    btnMusique, btnPe, btnReprendre, btnSt, calques, chronoCarton, chronoEntree, couches, curseurVolume,
    debutPlongee, debuts, depart, elActe, elActeDates, elActeTitre, elCarton, elCartonDates, elCartonTitre,
    elClipTexte, elEcoule, elLegende, elMusique, elN, elSt, horloge, horlogeSuite, lecteur, prelude, sa,
    scene, segments, suiteEtPause, tempsOuverture, total, voixEtPause });
}
