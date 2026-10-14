# Spec 20 — « La Révolution française » (récit 1787-1799)

Décisions prises avec l'utilisateur le 2026-10-14.

## Objectif pédagogique

Raconter **la Révolution française de 1787 à 1799**, de la crise de la monarchie au coup d'État
du 18 Brumaire, de façon à ce que le lecteur comprenne non seulement *ce qui se passe* mais
*pourquoi ça bascule* à chaque étape : déclenchement, construction d'une monarchie
constitutionnelle, chute du roi, guerre et radicalisation, Terreur, retour à l'ordre,
prise du pouvoir par l'armée. Niveau lycée / culture générale. Lecture en **25 à 35 minutes**
(environ 6 000 à 8 000 mots de récit, hors encadrés, glossaire et fiches).

## Place dans le site

- Une **seule page** pour l'instant : `src/content/lecons/xixe/revolution-francaise.mdx`,
  thème `politique`, adresse `/xixe/lecons/revolution-francaise/`, `periode: "1787-1799"`,
  `dureeLecture` réel (≈ 30), `ordre` après les leçons existantes du thème.
- **Pensée pour devenir un portail** : l'utilisateur ajoutera plus tard des sous-pages
  (une journée, une période, une notion à approfondir) dans
  `src/content/lecons/xixe/revolution-francaise/<sous>.mdx`. La page doit donc pouvoir
  accueillir ces sous-pages sans réécriture : prévoir en fin de page l'emplacement d'une liste
  générée depuis les sous-pages (`ListeSousPages`, comme les portails existants), qui ne
  s'affiche pas tant qu'il n'y en a aucune. Les ancres des parties et des grandes journées
  doivent être stables et lisibles (ex. `#14-juillet-1789`, `#la-terreur`) pour pouvoir y
  rattacher ces futures pages.
- Le prologue 1787-1789 déborde les bornes du siècle (1789) : c'est admis par CLAUDE.md
  (prologue sur la fin de l'Ancien Régime).

## Fil conducteur : récit chronologique expliqué

Le récit suit les événements dans l'ordre. Chaque partie s'ouvre par la question à laquelle
elle répond (« Pourquoi le roi convoque-t-il les états généraux ? », « Pourquoi la monarchie
constitutionnelle échoue-t-elle ? »…) et montre les enchaînements de causes. Plan indicatif
(l'agent peut l'ajuster, en gardant la progression) :

0. **Ouverture** : ce qu'était la France de 1787 (société d'ordres, monarchie absolue,
   privilèges, Lumières), en quelques paragraphes seulement.
1. **La crise de la monarchie (1787-1789)** : faillite des finances (guerre d'Amérique),
   Calonne et l'assemblée des notables, Brienne, révolte des parlements, journée des Tuiles
   (Grenoble, 1788), Vizille, convocation des états généraux, cahiers de doléances, Sieyès,
   doublement du tiers, crise frumentaire de 1788-1789.
2. **1789, l'année où tout bascule** : ouverture des états généraux (5 mai), Assemblée
   nationale (17 juin), serment du Jeu de paume (20 juin), 14 juillet, Grande Peur, nuit du
   4 août, Déclaration des droits de l'homme et du citoyen (26 août), journées d'octobre.
3. **Construire une monarchie constitutionnelle (1789-1791)** : départements, biens du
   clergé et assignats, Constitution civile du clergé et schisme, fête de la Fédération,
   fuite à Varennes, fusillade du Champ-de-Mars, Constitution de 1791.
4. **La guerre et la chute du roi (1791-1792)** : Assemblée législative, Girondins,
   déclaration de guerre (20 avril 1792), « la patrie en danger », 10 août 1792, massacres
   de Septembre, Valmy, proclamation de la République (21-22 septembre 1792).
5. **La Convention, la République en guerre (1792-1794)** : procès et exécution de Louis XVI
   (21 janvier 1793), Girondins contre Montagnards, chute des Girondins (2 juin 1793),
   guerre de Vendée, insurrections fédéralistes, Constitution de l'an I (jamais appliquée),
   Comité de salut public, **la Terreur** (loi des suspects, maximum, déchristianisation),
   victoires militaires, élimination des hébertistes et des indulgents, Grande Terreur,
   **9 Thermidor**.
6. **La République thermidorienne et le Directoire (1794-1799)** : réaction thermidorienne,
   journées de Prairial, Constitution de l'an III, Vendémiaire, Directoire et ses coups
   d'État (Fructidor, Floréal, Prairial), conjuration des Égaux, campagnes de Bonaparte,
   **18 Brumaire an VIII** (9 novembre 1799).
7. **Conclusion : ce que la Révolution laisse** au XIXe siècle (ce qui est irréversible,
   ce qui divise durablement les Français), en transition vers le reste du site.

## Éléments d'appui

- **Frise chronologique** monochrome 1787-1799 en tête de page : les régimes (bandes en
  nuances de gris ou motifs, avec libellés) et les grandes journées (repères), chacune
  **cliquable vers la partie ou l'ancre correspondante**. Réutiliser `Frise.astro` si son API
  le permet ; sinon l'étendre sans casser ses usages existants, ou créer un composant dédié
  réutilisable.
- **Encadrés « À retenir »** à la fin de chaque partie : 3 ou 4 points essentiels, en petites
  capitales grises et filet fin (composant `Encadre` existant si adapté).
- **Citations d'époque** : 6 à 10 citations courtes et célèbres (Sieyès, *Qu'est-ce que le
  tiers état ?* ; Déclaration de 1789, articles 1 et 2 ; Mirabeau le 23 juin 1789 avec sa
  formule réelle et la version légendaire signalée comme telle ; Danton « De l'audace… » ;
  Saint-Just ou Robespierre sur la vertu et la terreur ; Vergniaud ; etc.). **Chacune vérifiée
  mot pour mot** sur une source en ligne consultable (Gallica, Wikisource, archive.org,
  Archives parlementaires), avec sa source précise (texte, date, édition). Pas de citation
  de mémoire ; une phrase apocryphe ou douteuse est soit écartée, soit présentée comme
  attribuée/légendaire. Réutiliser `Extrait` ou `CarteCitation` selon la longueur.
- **Encadrés « Ce qu'en disent les historiens »** : deux ou trois, aux points chauds
  (les causes de la Révolution ; la Terreur, « bloc » ou « dérapage » ; la Vendée et le
  débat sur le mot « génocide »). Formulation prudente, présentation des positions
  (Michelet, Jaurès, Mathiez, Lefebvre, Soboul, Furet, Richet, Martin…) **sans trancher**.
- **Glossaire** en fin de page : 20 à 30 termes (tiers état, ordres, privilèges, cahiers de
  doléances, assignat, biens nationaux, prêtre réfractaire / jureur, sans-culottes, sections,
  club des Jacobins, Feuillants, Girondins, Montagnards, la Plaine, Comité de salut public,
  loi des suspects, maximum, calendrier républicain, émigrés, chouans, muscadins…).
  Les termes du glossaire peuvent être reliés depuis le texte par une ancre discrète.
- **Personnages** en fin de page : fiches courtes (3-4 lignes, dates de vie, rôle) d'une
  quinzaine d'acteurs : Louis XVI, Marie-Antoinette, Necker, Sieyès, Mirabeau, La Fayette,
  Brissot, Danton, Marat, Robespierre, Saint-Just, Hébert, Barras, Bonaparte, Charlotte
  Corday ou Olympe de Gouges… Réutiliser `Fiche` ou `FicheAuteur` si adapté.
- **Dates** : pour les dates de l'an II et suivantes, donner la date républicaine suivie de
  la date grégorienne (« 9 thermidor an II (27 juillet 1794) ») ; expliquer le calendrier
  républicain une fois, au moment de son adoption (octobre 1793).

## Illustrations

**5 à 8 œuvres d'époque du domaine public** aux moments clés (ex. : *Le Serment du Jeu de
paume* de David, une prise de la Bastille, la fête de la Fédération, l'exécution de Louis XVI,
*La Mort de Marat* de David, une scène de la Terreur ou de Vendée, *Bonaparte au conseil des
Cinq-Cents* de Bouchot). **Réutiliser en priorité les images déjà présentes pour le diaporama
de la Révolution** (`public/xixe/diaporamas/…`, `src/data/diaporamas/xixe/01-revolution.json`)
ou les œuvres des chapitres écrivains, plutôt que d'en télécharger de nouvelles. Même
traitement que les œuvres des chapitres écrivains (spec 11) : en gris dans la page, en couleur
dans la visionneuse ; composant `Oeuvre`, légende, date, lieu de conservation, source.

## Liens vers le reste du site

Renvois **discrets** aux endroits pertinents (une ligne « Voir aussi » sobre ou un lien
souligné sur un nom, rien de plus) :
- page Babeuf (partie Directoire, conjuration des Égaux) ;
- courants politiques (là où naissent républicains, royalistes/légitimistes, etc.) ;
- chapitres écrivains 0 (prologue) et 1 (Révolution) ;
- diaporama de la Révolution.
Plus un bloc final « Pour aller plus loin sur le site » (`BlocDiaporamas`, `BlocEcrivains`
si adaptés). Toutes les adresses via `src/utils/adresses.ts`.

## Design et forme

Design du site, strictement monochrome (CLAUDE.md) : pas d'accent rouge, pas de fond coloré.
Typographie française (espaces insécables avant `:` `;` `?` `!`, guillemets « »).
Sommaire de la page (parties) en tête ou en marge, cohérent avec les autres leçons.
Pas de quiz. Responsive (frise lisible sur téléphone : défilement horizontal interne ou
version verticale).

## Exigences historiques

Dates et noms exacts ; en cas de doute, formulation prudente. Chiffres (victimes de la
Terreur, de la Vendée, des massacres de Septembre) donnés en ordres de grandeur avec la
précision « selon les estimations ». Pas d'anachronisme de vocabulaire non expliqué.

## Critères d'acceptation

- La page paraît à `/xixe/lecons/revolution-francaise/` et dans l'accueil du XIXe (thème
  politique).
- Récit complet 1787 → 18 Brumaire, chaque partie ouverte par sa question et close par un
  « À retenir ».
- Frise en tête, cliquable vers les ancres ; glossaire et personnages en fin de page.
- Citations et extraits vérifiés mot pour mot, source donnée pour chacun.
- 5 à 8 œuvres, en gris dans la page, en couleur dans la visionneuse.
- Ajout futur d'une sous-page dans `revolution-francaise/` possible sans modifier la page.
- Aucune couleur hors gris ; typographie française respectée.
- `npm run build` passe sans erreur ; aucune page existante modifiée, hormis l'ajout de
  liens discrets éventuels vers cette page.
