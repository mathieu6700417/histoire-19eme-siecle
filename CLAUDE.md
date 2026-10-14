# Histoire de France — site d'apprentissage

Site statique Astro construit page par page pour apprendre l'histoire de France, siècle par
siècle (spec 18). Le premier siècle est le XIXe (`xixe`, de la Révolution de 1789 à 1900), qui
porte tout le contenu actuel ; un autre siècle s'ajoute par une entrée du registre
`src/data/siecles.ts` et ses propres dossiers. Chaque leçon est une page ajoutée au fil de
l'eau ; le site doit rester simple à étendre sans toucher aux pages existantes.

## Décisions prises (ne pas rediscuter)

- **Stack** : Astro (site statique), intégration MDX pour les leçons, aucun framework UI.
  Gestionnaire de paquets : npm. Pas de TypeScript strict imposé ; du TS léger est accepté.
- **Langue** : tout en français, avec accents et typographie française
  (espaces insécables avant `:` `;` `?` `!`, guillemets « »).
- **Périmètre** : France uniquement, sauf mention explicite dans une leçon. Chaque siècle définit
  ses bornes dans le registre (le XIXe : 1789-1900).
  Un prologue sur la fin de l'Ancien Régime (vers 1770-1789) est admis pour éclairer les causes
  de la Révolution (ex. chapitre 0 de la section « écrivains »).
- **Nom du site** : « Histoire de France » (spec 18). Adresses préfixées par le siècle
  (`/xixe/…`) ; `/` est le sommaire des siècles ; les anciennes adresses (`/lecons/*`,
  `/ecrivains/*`, `/diaporamas/*`) redirigent en 301 vers `/xixe/…` (`public/_redirects`).
- **Niveau** : lycée / culture générale. Clair, précis, sans jargon non expliqué.
  Dates et noms exacts ; en cas de doute historique, préférer la formulation prudente.
- **Design** (révisé le 2026-10-06) : style d'**édition savante**, sobre, minimaliste, presque
  académique (esprit Pléiade / Garnier), **strictement monochrome** : noir, gris et blanc cassé,
  aucune couleur, même pour les liens (soulignés) et même dans la frise et l'arbre (les courants
  y sont distingués par des nuances de gris, des motifs ou des styles de trait, et par leurs
  libellés). Une seule **couleur d'accent** existe dans le thème (`--c-accent`, rouge de rubrique,
  décidée le 2026-10-12) : elle ne s'emploie que là où l'utilisateur l'a demandé ; inemployée
  depuis le 2026-10-14 (la frise des cartons est repassée en noir et gris). Seule autre couleur : l'**eau des
  cartes** de diaporama (`--c-eau` pour les mers, `--c-eau-trait` pour les fleuves, bleu-gris pâle,
  décidé le 2026-10-14). Pas de fonds colorés, pas d'ombres, pas de badges pleins : on utilise des petites
  capitales grises et des filets fins. Typographie serif élégante. Exception : les œuvres d'art
  des chapitres écrivains s'affichent en gris dans la page et en couleur dans la visionneuse
  (spec 11).
  Pas de mode sombre pour l'instant. Responsive (lecture confortable sur téléphone).
- **Pas de quiz** pour l'instant (pourra être ajouté plus tard).
- **Structure** : sommaire des siècles à la racine ; pour chaque siècle, un accueil listant les
  leçons par thème, puis ses sections facultatives (« Écrivains », « Images ») ; navigation du
  siècle dans l'en-tête.
  Thèmes prévus : `politique`, `societe`, `economie`, `culture`, `international`, `sciences`.
- **Angle narratif** : chaque leçon choisit son fil conducteur dans sa spec. Pour la leçon
  sur les courants politiques, l'utilisateur a demandé de raconter le siècle *à travers*
  chaque courant (une page par courant, traversant tout le siècle) plutôt que régime par
  régime ; d'autres sections peuvent être découpées autrement (ex. par régime).
  Une leçon peut donc être un portail (vue d'ensemble) avec des sous-pages.

## Organisation du code

```
src/
  data/siecles.ts                         # registre des siècles (id, libellé, bornes, chapeau, sections)
  utils/adresses.ts                       # toutes les adresses internes, calculées depuis le siècle
  content/lecons/<siecle>/<slug>.mdx      # une leçon (ou le portail d'une leçon à sous-pages)
  content/lecons/<siecle>/<slug>/<sous>.mdx  # sous-page (id : <siecle>/<slug>/<sous>)
  content/ecrivains/<siecle>/NN-<slug>.mdx   # chapitres de la section « écrivains »
  content.config.ts                       # schéma des leçons (titre, thème, résumé, ordre, période)
  data/<siecle>/                          # données propres à un siècle (xixe : auteurs, artistes,
                                          #   chapitres-ecrivains, courants-politiques)
  data/diaporamas/<siecle>/               # scripts des périodes, registres, lots (section « images »)
  assets/oeuvres/<siecle>/                # œuvres des chapitres écrivains
  layouts/                                # Base.astro (html, head, en-tête du siècle), Lecon, Chapitre
  components/                             # composants partagés par tous les siècles
  pages/index.astro                       # sommaire des siècles
  pages/[siecle]/index.astro              # accueil d'un siècle : leçons groupées par thème
  pages/[siecle]/lecons/[...slug].astro   # rendu d'une leçon ou d'une sous-page
  pages/[siecle]/ecrivains/, diaporamas/  # sections facultatives (seulement si le siècle les a)
  styles/                                 # variables CSS (couleurs, typo), styles globaux
public/<siecle>/diaporamas/<slug>/        # médias servis à côté de la page /<siecle>/diaporamas/<slug>/
public/_redirects                         # 301 des anciennes adresses
docs/specs/                               # cahier des charges de chaque page, numéroté
docs/annotations/<siecle>/, docs/journal/<siecle>/  # annotations de visionnage, journaux
```

Aucune adresse interne ne s'écrit à la main : passer par `src/utils/adresses.ts` (ou les
fonctions de `utils/lecons.ts`, `utils/ecrivains.ts`, `utils/diaporamas.ts` qui s'y appuient).

## Pour ajouter une leçon

1. Écrire la spec dans `docs/specs/NN-<slug>.md`.
2. Créer `src/content/lecons/<siecle>/<slug>.mdx` avec le frontmatter attendu par `content.config.ts`.
   Pour une sous-page : `src/content/lecons/<siecle>/<slug>/<sous>.mdx`, `ordre` = rang parmi les frères.
   La page paraît à `/<siecle>/lecons/<slug>/`.
3. Réutiliser les composants existants avant d'en créer de nouveaux.
4. `npm run build` doit passer sans erreur avant de considérer la page finie.

Pour ajouter un siècle : une entrée dans `src/data/siecles.ts` (sections disponibles, plan des
chapitres s'il a des écrivains ou des images), puis ses dossiers `<siecle>/` (contenus, données,
médias). Scripts de production : `--siecle <id>` (défaut `xixe`).

Section « Le siècle raconté par ses écrivains » : suivre `docs/specs/00-charte-chapitres-ecrivains.md`
(règles et procédure, qui prévalent sur les specs 02 et 03) et les scripts de `scripts/ecrivains/`.
`npm run verifier:ecrivains` doit confirmer tous les extraits mot pour mot avant de finir un chapitre.

Diaporamas (« Le siècle en images ») : pour produire une période, suivre `docs/specs/12-siecle-en-images.md`
(« Produire une période », « Chaîne de production » et son tableau « Couche calculée sur Colab »), les specs 14 à 17,
la procédure de `scripts/diaporamas/README.md` et le bilan de la période précédente dans `docs/journal/xixe/`.
Calculs GPU : abonnement Colab Pro piloté par la CLI officielle `colab`, session arrêtée à la fin.
Production journalisée (`scripts/journal/noter.py`), budget Gemini explicite (`--budget`).

Diaporamas : avant de retoucher un diaporama, lire `python3 scripts/diaporamas/annotations.py lister <slug> --a-faire`
(annotations de visionnage de l'utilisateur, spec 15 ; `traiter <id> "<ce qui a été fait>"` une fois corrigé).

## Git

Ne pas committer ni pousser sans demande explicite de l'utilisateur.
