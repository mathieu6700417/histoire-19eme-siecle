# Spec 11 — Illustrer les chapitres « écrivains » par des œuvres d'art

Décidé avec l'utilisateur le 2026-10-06. S'applique à toute la section « Le siècle raconté
par ses écrivains ». Première livraison : **prologue et chapitres 1 à 5** (six fichiers déjà
écrits). Les chapitres 6 à 8 suivront la même règle quand ils seront écrits.

## Objet

Accompagner les textes d'**œuvres de l'époque** : peintures, gravures, caricatures,
lithographies, sculptures, monuments et constructions, objets. L'image est traitée comme une
**source**, au même titre que les extraits : on dit qui l'a faite, quand, pour qui, et quel est
son parti pris.

## Choix des œuvres

- **Densité** : environ **6 à 10 œuvres par chapitre**. Chaque `<Partie>` s'ouvre sur une œuvre
  (frontispice, juste après le titre de partie), et **2 à 5 autres** sont placées près des
  extraits qu'elles éclairent directement (ex. *Le Sacre de Napoléon* de David près du récit du
  sacre). Pas d'association forcée : si aucune œuvre ne parle vraiment au texte, on s'abstient.
- **Contemporaines en majorité, rétrospectives admises** : surtout des œuvres produites pendant
  la période du chapitre ; on admet des œuvres postérieures (XIXe siècle de préférence) quand
  elles ont façonné l'image de l'événement (ex. une toile de 1880 sur la Terreur). Varier les
  types : pas seulement des tableaux d'histoire, aussi de la caricature, de l'estampe
  populaire, de l'architecture (Arc de triomphe, Madeleine, colonne Vendôme, colonne de
  Juillet…), de la sculpture (Rude), des portraits d'écrivains cités.
- **Équilibre des camps**, comme pour les textes : propagande officielle et caricature
  d'opposition, art de cour et estampe populaire.
- **Périmètre** : œuvres françaises ou faites en France, ou représentant directement la France
  du chapitre. Domaine public obligatoire.
- **Exactitude** : artiste, titre, date, technique, lieu de conservation vérifiés sur la
  notice du musée ou sur Wikimedia Commons. En cas de doute (attribution, date), formulation
  prudente (« attribué à », « vers 1795 »).

## Classement témoin / postérieur (même filtre que les textes)

Les œuvres s'affichent selon le filtre « Témoins · Postérieurs · Tous » du chapitre, avec la
**même règle** que les extraits : une prop `faits` (année des faits représentés) et la date de
naissance de l'artiste ; l'œuvre est « témoin » si l'artiste est né au moins dix ans avant les
faits. Un monument sans artiste unique (ou un objet anonyme) est classé par sa date de
réalisation : témoin s'il est réalisé pendant la période du chapitre. La notice indique aussi
« œuvre contemporaine des faits » ou « œuvre rétrospective » (prop `regard`), comme pour les
extraits.

Le script de filtre de `Chapitre.astro` masque les œuvres comme les extraits. Une partie dont
tous les extraits sont masqués est masquée avec ses œuvres. Les œuvres ne comptent ni dans la
numérotation des textes, ni dans le sommaire, ni dans la durée de lecture.

## Affichage

- **Dans la page : niveaux de gris** (filtre CSS `grayscale(1)`), pour respecter la charte
  monochrome. Cadre : filet fin gris, pas d'ombre, pas de fond coloré.
- **Au clic : visionneuse plein écran en couleur** : l'œuvre en grand, en couleur, sur fond
  blanc cassé, avec sa légende ; zoom par pincement sur téléphone ; fermeture par Échap, par
  un bouton « Fermer » ou par un clic hors de l'image. Accessible (`<dialog>`, focus rendu à
  l'image à la fermeture). Sans JavaScript : l'image est un lien vers le fichier en grand.
  Un petit libellé en petites capitales grises (« voir en couleur ») signale la possibilité.
- **Légende visible** (notice) : artiste (dates), *titre*, date, technique, lieu de
  conservation ; mention « contemporaine / rétrospective ». Typographie de notice d'édition
  savante (petites capitales, gris).
- **« Lire l'image »** : bloc replié (`<details>`, même style que les blocs repliés des
  extraits), **80 à 150 mots** : ce qu'on y voit, le lien avec les textes voisins, et le parti
  pris de l'œuvre (commande officielle, propagande, caricature, mise en scène, anachronismes).
- **Crédits** : lien vers la page Wikimedia Commons du fichier (et vers la notice du musée si
  disponible).
- Responsive : pleine largeur de colonne sur téléphone ; sur grand écran, largeur de la colonne
  de texte (pas de débordement). Les frontispices de partie peuvent être un peu plus larges si
  la mise en page le permet sans casser la colonne.

## Technique

- **Composant** `src/components/Oeuvre.astro` (nom libre mais unique, réutilisable par les
  chapitres 6 à 8), documenté en tête comme `Extrait.astro`. Props au minimum : `id`, `image`
  (import), `artiste`, `titre`, `date`, `technique`, `lieu`, `faits`, `regard`, `commons`
  (URL), `musee` (URL facultative), `alt` ; slot « lire » (Markdown) pour « Lire l'image ».
- **Artistes** : leurs dates de naissance doivent être connues au build pour le classement.
  Soit un fichier `src/data/xixe/artistes.ts` (id, nom, naissance, mort), soit des props
  `naissance` ; préférer le fichier de données si l'artiste revient dans plusieurs chapitres.
  Ne pas mélanger avec `auteurs.ts` (l'index des auteurs ne doit pas lister les peintres),
  sauf pour un écrivain qui serait aussi l'auteur d'une image (ex. dessin de Hugo).
- **Fichiers** : téléchargés depuis **Wikimedia Commons** (domaine public), stockés dans
  `src/assets/oeuvres/xixe/<chapitre>/<id>.<ext>` et passés par `astro:assets` (`<Image>` /
  `getImage`) : WebP, tailles adaptées (vignette de colonne + grande version pour la
  visionneuse, environ 2000 px max sur le grand côté). Télécharger une résolution raisonnable
  (≤ 2500 px de large) pour ne pas alourdir le dépôt. Pas de lien direct vers
  upload.wikimedia.org dans les pages.
- Le texte alternatif (`alt`) décrit l'image pour un lecteur qui ne la voit pas (une phrase).
- Typographie française partout (fonction `typographie`).
- **Fichiers partagés** (`Chapitre.astro`, éventuellement `Base.astro`, styles globaux) :
  modifications ciblées, jamais de réécriture complète ; une autre session peut travailler sur
  les chapitres 6 à 8.
- `npm run build` sans erreur ni avertissement nouveau ; `npm run verifier:ecrivains` toujours
  vert (les œuvres ne doivent pas perturber la vérification des extraits).

## Hors périmètre (pour l'instant)

- Pas de page d'index des œuvres ou des artistes (pourra venir plus tard).
- Pas de couleur dans la page elle-même ; la couleur n'apparaît que dans la visionneuse.
