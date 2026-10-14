# Spec 19 — « Figures du siècle » et Gracchus Babeuf

Décisions prises avec l'utilisateur le 2026-10-14.

## Objectif pédagogique

Faire connaître **les idées de Gracchus Babeuf (1760-1797)** par ses propres textes : ce qu'il
reproche à la société issue de la Révolution, la société qu'il veut à la place et les moyens
d'y parvenir, puis montrer pourquoi le XIXe siècle s'en est souvenu (Buonarroti, Blanqui, les
socialistes). Niveau lycée / culture générale. Lecture en 15 à 20 minutes.

## Place dans le site

- Nouvelle leçon-portail **« Figures du siècle »** : `src/content/lecons/xixe/figures.mdx`,
  thème `politique`, adresse `/xixe/lecons/figures/`. Courte introduction (une série de
  portraits de personnages qui ont marqué le siècle, chacun présenté par ses idées et ses
  textes) et liste des figures, générée depuis les sous-pages comme le fait le portail des
  courants politiques. Babeuf est seul pour l'instant ; d'autres figures s'ajouteront sans
  toucher au portail.
- Sous-page **Babeuf** : `src/content/lecons/xixe/figures/babeuf.mdx`, `ordre: 1`, adresse
  `/xixe/lecons/figures/babeuf/`, `periode: "1760-1797"`.
- Lien vers la page Babeuf depuis la page « Les socialistes » (paragraphe sur la conjuration
  des Égaux), et depuis le portail des courants politiques là où Babeuf est nommé : un lien
  souligné sur son nom, rien de plus. Adresses par `src/utils/adresses.ts`.

## Fil conducteur : les idées par les textes

1. **En tête, une courte vie** (3-4 paragraphes) : Roye, le commissaire à terrier (feudiste) qui voit
   de près les droits seigneuriaux, le *Cadastre perpétuel* (1789), le journaliste, le choix
   du prénom « Gracchus » (les Gracques et la loi agraire), les prisons, *Le Tribun du peuple*,
   la conjuration des Égaux (1796), l'arrestation (10 mai 1796), le procès de Vendôme,
   l'exécution (27 mai 1797). Dates prudentes en cas de doute.
2. **Une section par grande idée**, chacune appuyée sur un extrait présenté puis commenté :
   - la critique de la propriété et de l'inégalité (« la république des riches ») ;
   - le « bonheur commun » et l'égalité réelle, au-delà de l'égalité des droits
     (Manifeste des plébéiens, *Tribun du peuple* n° 35, 30 novembre 1795) ;
   - la communauté des biens et des travaux (Analyse de la doctrine de Babeuf, avril 1796) ;
   - la prise du pouvoir par une minorité organisée et la dictature transitoire (la
     conjuration, d'après Buonarroti) ;
   - le **Manifeste des Égaux**, cité avec son attribution expliquée : rédigé par Sylvain
     Maréchal, écarté par le directoire secret de la conjuration (désaccord sur la formule
     « Périssent, s'il le faut, tous les arts… »), publié par Buonarroti en 1828. Cela montre
     aussi les débats au sein de la conjuration ;
   - la défense devant la Haute Cour de Vendôme (1797) et la dernière lettre à sa femme et
     à ses enfants.
3. **Postérité** : Buonarroti, *Conspiration pour l'Égalité dite de Babeuf* (Bruxelles,
   1828), qui transmet la doctrine aux sociétés secrètes de la monarchie de Juillet,
   à Blanqui et aux premiers communistes ; le jugement de Marx et d'Engels, qui voient en lui
   un précurseur ; la place que lui donne Jaurès dans l'*Histoire socialiste*. Formulation
   prudente.
4. **Pour aller plus loin** : les éditions en ligne des textes cités (liens Gallica ou
   Wikisource).

## Extraits

- 5 à 7 extraits de **80 à 250 mots**, chacun introduit (qui, quand, où publié, pour qui)
  puis commenté. Un passage clé en exergue par extrait, comme dans les chapitres écrivains.
- Mêmes exigences que la charte 00 : chaque extrait est **vérifié mot pour mot** sur une
  édition en ligne consultable (Gallica, Wikisource, archive.org), avec sa source précise.
  Orthographe de l'édition citée. Aucun extrait de mémoire : s'il n'est pas vérifiable,
  on ne le cite pas. Réutiliser le composant `Extrait` et, si possible, l'outillage de
  `scripts/ecrivains/` (wikisource.py, verifier.py), en l'étendant sans casser
  `npm run verifier:ecrivains` ; sinon fournir un script de vérification équivalent pour
  cette page.

## Illustrations

2 ou 3 images d'époque du domaine public (portrait gravé de Babeuf, une page du *Tribun du
peuple*, le procès de Vendôme ou une gravure de la conjuration), avec légende et source.
Même traitement que les œuvres des chapitres écrivains (spec 11) : en gris dans la page,
en couleur dans la visionneuse ; réutiliser le composant `Oeuvre`. Images rangées dans
`src/assets/` sous le siècle.

## Design et forme

Design du site, strictement monochrome (CLAUDE.md). Typographie française (espaces
insécables, guillemets « »). Pas de quiz. Responsive.

## Critères d'acceptation

- `/xixe/lecons/figures/` et `/xixe/lecons/figures/babeuf/` existent ; le portail paraît sous
  « politique » sur l'accueil du XIXe.
- Tous les extraits sont vérifiés mot pour mot, avec leur source.
- Les liens depuis la page « socialistes » et le portail des courants mènent à Babeuf.
- `npm run build` et `npm run verifier:ecrivains` passent.
