// Constantes de réglage du lecteur : caméra (spec 12, « Caméra calme et lente », « Caméra plus
// vivante »), entrée des images, ouverture du carton, frise, portraits, musique (« Musique »).
// README : « Caméra : format et pièges », « Musique : format et sources ».
// Caméra (spec 12, « Caméra calme et lente ») : chaque étape retenue est rejointe par une
// transition dont la durée suit l'ampleur du mouvement (3 à 6 s, vitesse plafonnée), arrivée
// peu après le passage ; entre deux transitions, la vue « respire » dans un seul sens.
// Toutes les vues sont des rectangles aux proportions de la zone utile (cf. `vue`) : entre deux
// d'entre elles, le chemin est une homothétie (zoom logarithmique, déplacement couplé), sans arc.
export const VITESSE_ZOOM = 0.22;   // plafond, en log d'échelle par seconde (au plus fort)
export const VITESSE_GLISSE = 0.3;  // plafond, en fraction de la scène par seconde (au plus fort)
// Les durées visent 5 % sous les plafonds : l'horloge lissée peut accélérer de 5 % pour
// rattraper l'audio, la vitesse réelle reste ainsi sous le plafond.
export const VISE_ZOOM = VITESSE_ZOOM / 1.05, VISE_GLISSE = VITESSE_GLISSE / 1.05;
export const DUREE_MIN = 3;         // s : une transition dure de 3 à 6 s selon son ampleur (plafonds ci-dessus)
export const RETARD = 1;            // s : arrivée visée, après le passage
export const TENUE_MIN = 1;         // s : arrêt minimal entre deux transitions
export const ECART_MIN = 5;         // s : moins entre deux passages → l'étape est ignorée
export const MICRO = 0.12;          // écart de zoom (log) et de position (fraction de la scène) en deçà duquel l'étape est ignorée
// Zoom lent continu pendant les tenues (spec 12, « Caméra plus vivante et cadres justes ») :
// zoom avant à sens unique, ~1,2 % par seconde (en log d'échelle), 12 % au plus (×1,12), avec un
// glissement vers le centre du cadre visé (le sujet), borné à la marge libre : le sous-cadre
// reste dans la vue, donc dans la zone utile. Vitesse constante après une mise en route douce
// (et arrêt doux, pour se raccorder sans à-coup à la transition suivante ou à la fin de la voix).
export const SOUFFLE = Math.log(1.12);  // zoom maximal d'une tenue (log d'échelle)
export const SOUFFLE_VITESSE = 0.012;   // log d'échelle par seconde (~1,2 %/s) : une tenue courte zoome moins
export const RAMPE_SOUFFLE = 1.2;       // s : mise en route (et arrêt) du zoom de tenue, courte pour qu'il se voie tôt
export const MISE_EN_ROUTE = 2.5;       // s (mise en route, et arrêt)
// Entrée d'une image (spec 12, « Animations d'entrée ») : fondu enchaîné, révélation
// gris → couleur, recul de ~4 % jusqu'au cadre de la caméra. Horloge propre à l'entrée,
// indépendante de l'audio : la caméra n'est jamais décalée. L'entrée est une transition
// visuelle courte : elle va toujours à son terme, même en pause (jamais d'image à demi
// entrée bloquée si la voix ne démarre pas).
export const FONDU = 1.2;        // s
export const REVELATION = 1.8;   // s : les couleurs montent
export const RECUL = 0.04;       // agrandissement de départ
export const DUREE_RECUL = 1.5;  // s
export const FONDU_REDUIT = 0.3; // s, prefers-reduced-motion : fondu simple, ni recul ni gris
// Avant / après et mosaïque, prefers-reduced-motion : fondu enchaîné vers l'image après, et
// fondu de la grille (complète d'emblée) vers l'image principale.
export const FONDU_APRES_REDUIT = 1;
export const FONDU_MOSAIQUE_REDUIT = 0.8;
export const MISE_EN_VALEUR = 0.03; // mosaïque : avancée de la vignette mise en valeur (échelle 1,03)
// Sortie du carton d'acte (spec 12, « Sortie du carton d'acte en deux volets », révision du
// 2026-10-08) : les volets s'ouvrent pendant les dernières secondes du carton (sa durée totale ne
// change pas) ; la voix commence à la fin de l'ouverture. Si la diapositive a un détail
// d'ouverture (`ouv`), l'image est découverte cadrée sur ce détail, avec une très légère
// poussée, puis la caméra recule lentement vers son premier cadre pendant que la voix commence.
export const OUVERTURE = 3.5;        // s : ouverture des volets (prise sur la fin du carton)
export const POUSSEE = 0.025;        // resserrement pendant l'ouverture (arrêt doux à la fin)
export const RECUL_OUVERTURE = 5;    // s : recul du détail vers le premier cadre (après l'ouverture)
export const RAMPE_RECUL = 0.4;      // part du recul en mise en route (et autant en arrêt)
// Frise du temps en bas de l'image : 4 s en tout, fondu de sortie compris (le curseur glisse de
// 0,5 à 1,5 s, cf. CSS).
export const DUREE_FRISE = 4;   // s
export const FONDU_FRISE = 0.6; // s (transition de sortie, cf. CSS)
// Rangée de portraits : fondu de l'ovale et de son étiquette quand la voix dit le nom (s).
export const PORTRAIT_FONDU = 0.45;
// Portraits et objets du bas (révision du 2026-10-09 : 1,5 fois plus grands) : hauteur de l'ovale
// ou de l'objet plafonnée à cette part de la hauteur de la scène (étiquette ou légende en plus).
export const COIN_H_MAX = 0.3;      // ordinateur (et téléphone couché)
export const COIN_H_MAX_TEL = 0.27; // téléphone debout (scène de moins de 700 px de large)
export const CLE_ST = 'diaporamas-sous-titres';
export const CLE_MUSIQUE = 'diaporamas-musique';
export const CLE_VOLUME = 'diaporamas-musique-volume';
// Musique de fond (spec 12, « Musique ») : gain selon l'état du lecteur, relatif au volume
// réglé (80 % par défaut = valeurs ci-dessous). Fichiers normalisés à -20 LUFS, voix vers
// -19,5 LUFS : sous la voix, la musique est ~20 dB plus bas ; un peu plus présente dans les
// respirations ; elle remonte pendant les cartons d'acte et se tait pendant un intermède chanté.
export const GAINS = { arret: 0, chant: 0, voix: 0.1, respiration: 0.3, carton: 1 } as const;
export type EtatMusique = keyof typeof GAINS;
export const VOLUME_DEFAUT = 0.8;
export const FONDU_PISTE = 3;   // s : enchaînement de deux pistes d'un même acte (fondus inclus dans les fichiers)
export const FONDU_ACTE = 2;
