// Segments joués après la voix (chant, lecture, épisode) : lancement sur le lecteur `sa`, fin,
// arrêt, mise à jour à chaque instant. Lit `x.suite`, `lec.enSuite`, `lec.ov`.
// Spec 12, « Lectures d'époque et épisodes » ; README : « Lectures d'époque et épisodes ».
import type { Diapo } from './types';
import type { Lecteur } from './contexte';

export function installerSegments(lec: Lecteur) {
  const { D, animer, cacherFrise, changerCartouche, changerSousTitre, chargerSurimpressions, lecteur,
    majTemps, racine, sa } = lec;
  Object.assign(lec, { arreterSuite, finSuite, lancerSuite, majSuite });
  // --- Segments après la voix : intermède chanté, lecture d'époque, épisode -----------------------
  // La voix s'est tue. Intermède : le chant est joué au premier plan sur l'image du moment (la
  // musique de fond se tait), avec son cartouche et ses paroles façon clip au centre de l'image
  // voilée (majParoles). Lecture : la carte
  // de citation couvre l'image (floue, voilée, immobile) et le texte y apparaît mot par mot au
  // rythme de la voix de lecture. Épisode : un panneau couvre la scène et ses visuels suivent la narration. L'horloge
  // est `sa.currentTime` (pause, reprise et sauts justes). → passe le segment.
  const cartes = new Map([...racine.querySelectorAll<HTMLElement>('.citation--lecteur')].map((e) => [e.dataset.lecture!, e]));
  const panneaux = new Map([...racine.querySelectorAll<HTMLElement>('.episode--lecteur')].map((e) => [e.dataset.episode!, e]));
  lec.ov = null; // carte ou panneau affiché
  const CLASSES_SUITE = { chant: 'en-chant', lecture: 'en-citation', episode: 'en-episode' } as const;
  function lancerSuite() {
    const c = D.diapos[lec.i].suite!;
    lec.enSuite = true;
    lec.suiteFini = false;
    lecteur.classList.add(CLASSES_SUITE[c.type]);
    if (sa.getAttribute('src') !== c.src) sa.src = c.src;
    try { sa.currentTime = 0; } catch { /* métadonnées pas encore chargées */ }
    if (c.type === 'chant') {
      changerCartouche({ legende: c.galerie?.[0]?.legende ?? c.legende } as Diapo);
      chargerSurimpressions(null);
      // Intermède musical (œuvre instrumentale) : pas de paroles, sous-titre masqué.
      lecteur.classList.toggle('en-instrumental', c.instrumental);
      // Chant : paroles façon clip au centre de l'image voilée, sans sous-titre ni frise.
      if (!c.instrumental && c.paroles.length) {
        lec.preparerClip(c);
        lecteur.classList.add('en-clip');
        changerSousTitre('');
        cacherFrise();
      }
    } else {
      lec.ov = (c.type === 'lecture' ? cartes : panneaux).get(c.id) ?? null;
      if (lec.ov) { lec.preparer(lec.ov, c); lec.ov.classList.add('est-visible'); lec.ov.setAttribute('aria-hidden', 'false'); }
      changerSousTitre('');
      chargerSurimpressions(null);
      // Pas de frise en surimpression : la carte ou le panneau en tient lieu ; la date du
      // segment (champ `date`) reste celle de son récit, et la frise reprend à la diapositive
      // suivante, comparée à celle-ci.
      cacherFrise();
    }
    majSuite();
    lec.musique();
    if (lec.joue) sa.play().catch((e) => { if (e?.name !== 'AbortError') finSuite(); });
    animer();
    majTemps();
  }
  /** Fin naturelle du segment (ou erreur) : pause, puis diapositive suivante. La carte ou le
   *  panneau reste, complet, jusqu'au fondu vers l'image suivante. */
  function finSuite() {
    if (!lec.enSuite) return;
    lec.enSuite = false;
    lec.suiteFini = true;
    lecteur.classList.remove('en-chant', 'en-instrumental', 'en-clip');
    majSuite();
    lec.musique();
    majTemps();
    if (lec.joue) { lec.arreterMinuterie(); lec.minuterie = window.setTimeout(lec.suivantAuto, D.pause * 1000); }
  }
  /** Sortie du segment par un saut (le cartouche et le sous-titre sont alors remplacés). */
  function arreterSuite(garderCarte = false) {
    if (!lec.enSuite && !lec.suiteFini) return;
    lec.enSuite = false;
    lec.suiteFini = false;
    sa.pause();
    lecteur.classList.remove('en-chant', 'en-instrumental', 'en-clip', 'en-citation', 'en-episode');
    // `garderCarte` : la carte reste affichée jusqu'à ce que l'image suivante soit prête (afficher).
    if (lec.ov && !garderCarte) { lec.ov.classList.remove('est-visible'); lec.ov.setAttribute('aria-hidden', 'true'); }
    lec.ov = null;
  }
  /** Mise à jour du segment en cours d'après l'horloge de son audio. */
  function majSuite() {
    const c = D.diapos[lec.i].suite;
    if (!c || (!lec.enSuite && !lec.suiteFini)) return;
    const t = lec.suiteFini ? c.duree + 2 : sa.currentTime || 0;
    if (c.type === 'chant') { if (lec.enSuite) lec.majParoles(); return; }
    // Lecture illustrée (spec 14) : hors boucle d'animation (saut en pause), l'image de fond suit.
    if (c.type === 'lecture' && c.images && !lec.raf) lec.rendre();
    if (!lec.ov) return;
    if (c.type === 'lecture') lec.majCitation(lec.ov, c, t);
    else lec.majEpisode(lec.ov, c, t);
  }
}
