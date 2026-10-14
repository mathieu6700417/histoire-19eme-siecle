# Spec 14 — Diaporamas : deux fois plus d'images, à narration identique

Décidé avec l'utilisateur le 2026-10-11, après visionnage de la période 03 (« C'est pas mal. Je
voudrais beaucoup plus d'illustrations, même si l'on garde la même narration »). Révise la spec 12
sur deux points : « ~100 images par période » devient **~220 à 260 images**, et « ~18 s par image »
devient **une image toutes les 7 à 12 s** en moyenne. Tout le reste de la spec 12 demeure
(documents d'époque, domaine public, Commons, monochrome hors images, caméra calme).

## Décisions

| Sujet | Décision |
|---|---|
| Narration | **Inchangée** : aucun texte, aucune voix n'est refait pour cette spec. |
| Densité | On **double** : ~110 à 140 images ajoutées par période. Pas de quota par diapositive : une image par phrase **quand une bonne image d'époque existe**. |
| Trois mécanismes | (1) plusieurs images par diapositive (« plans »), (2) lectures et épisodes illustrés, (3) galeries pendant la musique. |
| Ordre | Mécanisme et pilote sur la **Restauration** (période 03) ; les périodes 01 et 02 seront enrichies ensuite, sur demande ; les périodes suivantes sont écrites directement ainsi. |
| Compatibilité | Une période sans les nouveaux champs se joue **exactement comme avant** (`captures.py --comparer` sur 01 et 02 : identique au pixel). |

## 1. Plusieurs images par diapositive (`plans`)

- Une diapositive garde `image` (première image, montrée dès le début) et peut porter
  `plans` : 1 ou 2 images supplémentaires (3 images au plus par diapositive), chacune
  `{ "quand": "<mots de la narration qui la déclenchent>", "image": { … même format qu'`image` … } }`.
  Fichiers `NNN-b.webp`, `NNN-c.webp`.
- `instant` de chaque plan : calculé par `surimpressions.py` d'après `quand` et l'horodatage de la
  voix (comme les chiffres et les citations), de préférence au **début d'une phrase**. Aucun plan ne
  dure moins de **5 s** ; la première image non plus (`verifier.py` : erreur).
- Chaque image a sa **zone utile** et sa **caméra**, calculées sur la fenêtre de temps où elle est à
  l'écran (la caméra d'un plan court peut n'avoir qu'un cadre : lent mouvement d'ampleur).
- Passage d'une image à l'autre : **fondu croisé** d'environ 0,8 s, sans carton ni effet ; la
  caméra de l'image entrante est déjà en mouvement.
- Le **cartouche** (titre court, auteur, date) suit l'image affichée ; le **livre d'images** et les
  crédits listent toutes les images ; la frise ne bouge pas (date de la diapositive).
- **Surimpressions** : elles restent calées sur la voix. Ce qui dépend de l'image (« personne
  visible sur l'image », visage à ne pas couvrir, marges) se juge sur l'image à l'écran à cet
  instant. Un plan ne commence pas pendant qu'une citation ou un chiffre est affiché si l'on peut
  l'éviter (décaler à la phrase suivante).
- Pas de `plans` sur une diapositive à **avant/après** ou à **mosaïque** (elles ont déjà plusieurs
  images).
- Choix des images : ce que la phrase **nomme ou décrit** (lieu, personne, scène, œuvre, objet,
  document, caricature) ; jamais une image décorative sans rapport ; pas deux fois la même image
  dans la période (sauf détail d'une œuvre déjà montrée, compté comme réutilisation voulue).

## 2. Lectures et épisodes illustrés

- **Lectures** : champ `images` (2 à 4 images, même format, `quand` facultatif sinon réparties
  également) affichées en fond derrière la carte de lecture, en fondu croisé, avec un mouvement
  lent ; la carte, le portrait et le texte mot à mot restent lisibles (image assombrie ou voilée
  de gris si nécessaire, sans couleur ajoutée). Légende courte de l'image visible.
- **Épisodes** : un nouveau type de panneau `image` (une image d'époque plein cadre avec légende)
  utilisable entre deux panneaux existants ; 1 à 2 par épisode quand le sujet s'y prête.

## 3. Galeries pendant la musique

- **Intermèdes existants** : champ `galerie` (3 à 5 images liées à l'œuvre entendue : décors,
  costumes, interprètes, partition, salle), réparties sur la durée de l'extrait, fondu croisé.
  Un chant à paroles façon clip garde ses paroles par-dessus.
- **Galeries nouvelles** : 2 à 3 par période, sans voix, 20 à 30 s chacune, sur un extrait
  musical déjà au registre ou sur le fond de l'acte (pas de nouvelle recherche musicale
  obligatoire) : un thème que la narration vient d'évoquer (le Salon, les caricatures du roi, les
  modes, les barricades). Un cartouche donne le thème. La durée totale de la période augmente d'au
  plus 2 min.

## Chaîne

- `images.py`, `utile.py`, `camera.py`, `surimpressions.py`, `verifier.py`, `captures.py` et le
  livre d'images connaissent les nouvelles images. `images.py --n` accepte une liste (`3,7,12`).
- `verifier.py` : licences, métadonnées, durées minimales, pas de doublon, `quand` présent dans la
  narration ; bilan « images : n dont p plans, l lectures, g galeries » ; avertissement de dosage
  sous 200 images pour une période produite après cette spec.
- Lecteur : modules concernés `rendu.ts`, `camera.ts`, `textes.ts`, `surimpressions.ts`,
  `segments.ts`, `lectures.ts`, `episodes.ts`, `progression.ts` (préchargement), nouveau module
  si utile. Poids : ~250 Ko par image, soit +30 à 40 Mo par période.
- Gemini : zone utile et caméra seulement (~0,007 $ par image), `--budget` obligatoire.
- Journal : `docs/journal/xixe/plus-d-images.jsonl`.

## Précisions d'implémentation (2026-10-11, mécanisme et jeu d'essai)

Écarts et précisions décidés en construisant le lecteur et la chaîne (détail : README des scripts,
« Plans, lectures illustrées et galeries (spec 14) ») :

- **Galerie nouvelle** : pas de nouveau type de segment. C'est un **intermède instrumental** de
  `musique.intermedes` (extrait découpé par `musique.py` dans un enregistrement du registre) qui porte
  `galerie` et `theme` ; le thème remplace l'œuvre en tête du cartouche (la musique reste au survol
  et dans les crédits). Elle se place donc « après n », sur une diapositive sans autre segment.
- **Instant d'un plan** : le fondu croisé (0,8 s) commence 0,3 s avant le passage `quand` ; si ce
  passage est dit dans les 1,5 s qui suivent le début de sa phrase, 0,3 s avant ce début.
- **Doublons** : une image de la spec 14 déjà employée dans la période est une erreur, sauf
  `"reprise": true` sur son entrée (détail voulu d'une œuvre déjà montrée).
- **Lecture illustrée** : la carte devient un voile de papier translucide (60 %) avec un halo plus
  dense derrière le texte ; la légende de l'image est en haut à gauche (absente sur téléphone, le
  livre d'images la donne). À faire juger au visionnage.
- **Panneau `image`** d'un épisode : recadré par CSS (`position`), sans zone utile ni caméra ; retirer
  les marges de papier par `recadrage`.
- **Images sans narration** (lecture, galerie) : un seul cadre, calculé localement (visages YuNet),
  sans appel Gemini ; seuls les plans passent par le modèle, sur la narration de leur fenêtre.
- **Estampes à marges** : préférer `recadrage` (image nette) à une petite zone utile ; le fichier
  peut alors dépasser les ~250 Ko visés ; `images.py` le plafonne à ~400 Ko (qualité puis taille
  réduites par paliers, intégration du 2026-10-11).

## Acceptation

- Périodes 01 et 02 : rendu identique (captures comparées), `verifier.py --tous` sans erreur.
- Restauration : ≥ 220 images, `verifier.py restauration` sans erreur, build qui passe, planche de
  captures montrant un changement de plan, une lecture illustrée, une galerie.
- Visionnage par l'utilisateur avant commit et déploiement.

## Retour de l'utilisateur après visionnage (2026-10-11)

- **Rythme** : « c'est mieux » avec les plans ; on garde.
- **Lectures illustrées refusées** : l'utilisateur n'aime pas les images de fond derrière la carte
  de lecture (« c'était mieux avant »). Les 17 images de lecture de la Restauration sont retirées
  (champ `images` des lectures supprimé, fichiers effacés) ; la carte de lecture redevient celle de
  la spec 12. **Ne plus illustrer les lectures** dans les périodes suivantes ; le code du lecteur
  qui lit `images` reste en place, inutilisé. La période 03 compte 220 images.
