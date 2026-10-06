# Histoire du XIXe siècle — site d'apprentissage

Site statique Astro construit page par page pour apprendre l'histoire du XIXe siècle
(cadre : France, de la Révolution de 1789 à 1900). Chaque leçon est une page ajoutée
au fil de l'eau ; le site doit rester simple à étendre sans toucher aux pages existantes.

## Décisions prises (ne pas rediscuter)

- **Stack** : Astro (site statique), intégration MDX pour les leçons, aucun framework UI.
  Gestionnaire de paquets : npm. Pas de TypeScript strict imposé ; du TS léger est accepté.
- **Langue** : tout en français, avec accents et typographie française
  (espaces insécables avant `:` `;` `?` `!`, guillemets « »).
- **Périmètre** : France uniquement, sauf mention explicite dans une leçon.
  Un prologue sur la fin de l'Ancien Régime (vers 1770-1789) est admis pour éclairer les causes
  de la Révolution (ex. chapitre 0 de la section « écrivains »).
- **Niveau** : lycée / culture générale. Clair, précis, sans jargon non expliqué.
  Dates et noms exacts ; en cas de doute historique, préférer la formulation prudente.
- **Design** (révisé le 2026-10-06) : style d'**édition savante**, sobre, minimaliste, presque
  académique (esprit Pléiade / Garnier), **strictement monochrome** : noir, gris et blanc cassé,
  aucune couleur, même pour les liens (soulignés) et même dans la frise et l'arbre (les courants
  y sont distingués par des nuances de gris, des motifs ou des styles de trait, et par leurs
  libellés). Pas de fonds colorés, pas d'ombres, pas de badges pleins : on utilise des petites
  capitales grises et des filets fins. Typographie serif élégante. Exception : les œuvres d'art
  des chapitres écrivains s'affichent en gris dans la page et en couleur dans la visionneuse
  (spec 11).
  Pas de mode sombre pour l'instant. Responsive (lecture confortable sur téléphone).
- **Pas de quiz** pour l'instant (pourra être ajouté plus tard).
- **Structure** : page d'accueil listant les leçons par thème + navigation commune.
  Thèmes prévus : `politique`, `societe`, `economie`, `culture`, `international`, `sciences`.
- **Angle narratif** : chaque leçon choisit son fil conducteur dans sa spec. Pour la leçon
  sur les courants politiques, l'utilisateur a demandé de raconter le siècle *à travers*
  chaque courant (une page par courant, traversant tout le siècle) plutôt que régime par
  régime ; d'autres sections peuvent être découpées autrement (ex. par régime).
  Une leçon peut donc être un portail (vue d'ensemble) avec des sous-pages.

## Organisation du code

```
src/
  content/lecons/<slug>.mdx           # une leçon (ou le portail d'une leçon à sous-pages)
  content/lecons/<slug>/<sous>.mdx    # sous-page d'une leçon (id : <slug>/<sous>)
  content.config.ts             # schéma des leçons (titre, thème, résumé, ordre, période)
  layouts/                      # Base.astro (html, head, nav), Lecon.astro (mise en page d'une leçon)
  components/                   # composants réutilisables (Frise, Fiche, Arbre, Encadré…)
  pages/index.astro             # accueil : leçons groupées par thème
  pages/lecons/[...slug].astro  # rendu d'une leçon ou d'une sous-page
  styles/                       # variables CSS (couleurs, typo), styles globaux
docs/specs/                     # cahier des charges de chaque page, numéroté
```

## Pour ajouter une leçon

1. Écrire la spec dans `docs/specs/NN-<slug>.md`.
2. Créer `src/content/lecons/<slug>.mdx` avec le frontmatter attendu par `content.config.ts`.
   Pour une sous-page : `src/content/lecons/<slug>/<sous>.mdx`, `ordre` = rang parmi les frères.
3. Réutiliser les composants existants avant d'en créer de nouveaux.
4. `npm run build` doit passer sans erreur avant de considérer la page finie.

Section « Le siècle raconté par ses écrivains » : suivre `docs/specs/00-charte-chapitres-ecrivains.md`
(règles et procédure, qui prévalent sur les specs 02 et 03) et les scripts de `scripts/ecrivains/`.
`npm run verifier:ecrivains` doit confirmer tous les extraits mot pour mot avant de finir un chapitre.

## Git

Ne pas committer ni pousser sans demande explicite de l'utilisateur.
