// Point d'entrée du lecteur de diaporamas : crée le contexte `lec` de chaque .diaporama et
// installe les modules dans l'ordre (l'ordre compte : écouteurs enregistrés dans l'ordre d'origine).
// Carte des modules : scripts/diaporamas/README.md, « Lecteur : carte des modules ».
import { installerEtat } from './etat';
import { installerCamera } from './camera';
import { installerAvantApres } from './avant-apres';
import { installerMosaique } from './mosaique';
import { installerPlans } from './plans';
import { installerMouvement } from './mouvement';
import { installerAmbiance } from './ambiance';
import { installerCouleur } from './couleur';
import { installerFond } from './fond';
import { installerRendu } from './rendu';
import { installerFrise } from './frise';
import { installerTextes } from './textes';
import { installerIncrustations } from './incrustations';
import { installerSurimpressions } from './surimpressions';
import { installerProgression } from './progression';
import { installerCartons } from './cartons';
import { installerSegments } from './segments';
import { installerChant } from './chant';
import { installerLectures } from './lectures';
import { installerEpisodes } from './episodes';
import { installerNavigation } from './navigation';
import { installerMusique } from './musique';
import { installerGenerique } from './generique';
import { installerTests } from './tests';
import { installerControles } from './controles';
import { installerReprise } from './reprise';
import type { Lecteur } from './contexte';

/** Vrai seulement dans le build de `npm run annoter` (astro.config.mjs) ; faux, la branche et son
 *  module disparaissent du site construit (spec 15 : rien de l'outil dans le site déployé). */
declare const __ANNOTATIONS__: boolean;

function monter(racine: HTMLElement) {
  const lec = { racine } as Lecteur;
  installerEtat(lec);
  installerCamera(lec);
  installerAvantApres(lec);
  installerMosaique(lec);
  installerPlans(lec);
  installerMouvement(lec);
  installerAmbiance(lec);
  installerCouleur(lec);
  installerFond(lec);
  installerRendu(lec);
  installerFrise(lec);
  installerTextes(lec);
  installerIncrustations(lec);
  installerSurimpressions(lec);
  installerProgression(lec);
  installerCartons(lec);
  installerSegments(lec);
  installerChant(lec);
  installerLectures(lec);
  installerEpisodes(lec);
  installerNavigation(lec);
  installerMusique(lec);
  installerGenerique(lec);
  installerTests(lec);
  installerControles(lec);
  installerReprise(lec);
  if (__ANNOTATIONS__) import('./annotations').then((m) => m.installerAnnotations(lec));
}

for (const r of document.querySelectorAll<HTMLElement>('.diaporama')) monter(r);
