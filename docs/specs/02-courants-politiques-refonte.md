# Spec 02 — Refonte : le siècle raconté à travers chaque courant

## Pourquoi

Retour de l'utilisateur sur la première version : « je voudrais plutôt voir l'histoire
de ce siècle à travers ses courants, et pas l'inverse ». La v1 suivait les régimes et
y croisait les courants. La v2 suit chaque courant et lui fait traverser tout le siècle.

Cette spec remplace les sections 3 (récit par régime) et 4 (fiches) de la spec 01.
Les sections 1 (introduction), 2 (frise), 5 (arbre) et 6 (bibliographie) restent valables,
ainsi que toutes les contraintes d'exactitude et de niveau.

## Décisions prises avec l'utilisateur

- **Récit continu par courant** : chaque courant est raconté comme une biographie, de sa
  naissance à 1900. Les événements du siècle (1814, 1830, 1848, 1851, 1870-1871, 1877,
  1889, 1894-1899…) sont vécus depuis son point de vue. Pas de grille régime par régime.
- **Une page portail + une page par courant** (neuf pages de courant).
- **Le récit régime par régime disparaît**, remplacé sur le portail par un tableau de
  repères compact (pas de récit).
- **Chaque page de courant s'ouvre par sa fiche** (carte d'identité), puis vient le récit.

## Architecture

- Sous-pages d'une leçon : `src/content/lecons/courants-politiques/<courant>.mdx`.
  L'id de collection devient `courants-politiques/<courant>`. Le parent est le segment
  avant le `/`. Route : `src/pages/lecons/[...slug].astro` (remplace `[slug].astro`).
- Frontmatter d'une sous-page : mêmes champs que les leçons (`titre`, `theme`, `resume`,
  `ordre` = ordre parmi les frères, `periode`, `dureeLecture`), plus `courant` (optionnel,
  id du courant dans `src/data/courants-politiques.ts`, sert à la couleur du bandeau et
  à la mini-frise).
- Layout `Lecon.astro` : fil d'Ariane « Vie politique › Les courants politiques › Légitimistes »
  pour une sous-page. Navigation précédent/suivant : entre frères pour une sous-page, avec
  un lien de retour au portail ; entre leçons de premier niveau pour un portail.
- Accueil : seules les leçons de premier niveau sont listées ; sous la carte d'une leçon,
  ses sous-pages apparaissent en petits liens.
- Les liens de la frise (champ `id` des lignes) et de l'arbre (champ `lien` des nœuds)
  pointent vers les pages de courants, plus vers des ancres de fiches.
- Nouveau composant `CarteCourant.astro` : carte de la grille du portail (bandeau de la
  couleur du courant, nom, période, « en une phrase », lien vers la page).
- Le composant `Fiche.astro` doit pouvoir servir d'en-tête de page : le titre du courant
  est déjà le `h1` de la page, la fiche ne le répète pas en `h3` (prop `entete` ou
  niveau de titre paramétrable).
- Les slugs des neuf pages : `legitimistes`, `orleanistes`, `bonapartistes`, `republicains`,
  `radicaux`, `socialistes`, `anarchistes`, `catholiques`, `nationalistes`.
  Adresses : `/lecons/courants-politiques/<slug>/`.

## Portail : `src/content/lecons/courants-politiques.mdx` (dans cet ordre)

1. **Introduction** : réécrite pour annoncer la démarche (« on va traverser le siècle neuf
   fois, une fois par courant »). Garde les encadrés « Droite et gauche » et « Régime »,
   et les trois questions qui divisent (régime, Église, question sociale).
2. **Repères du siècle** : un tableau compact des régimes (colonnes : régime, dates,
   comment il naît, comment il tombe), huit lignes (Révolution, Consulat/Empire,
   Restauration, monarchie de Juillet, IIe République, Second Empire, IIIe République
   jusqu'en 1900 ; la Révolution peut être découpée en 1789-1792 et 1792-1799). Puis une
   liste de 12 à 15 grandes dates à connaître. Aucun récit : c'est l'ossature que le
   lecteur garde en tête avant d'entrer dans les récits.
3. **Frise** (existante, inchangée dans sa forme ; vérifier que les noms de courants
   mènent aux pages).
4. **Les neuf courants** : grille de `CarteCourant`, dans l'ordre : légitimistes,
   orléanistes, bonapartistes, républicains, radicaux, socialistes, anarchistes,
   catholiques, nationalistes. Une phrase d'accroche avant la grille explique que chaque
   page raconte le siècle depuis ce courant.
5. **Arbre généalogique** (existant) avec son texte de filiations.
6. **Pour aller plus loin** (existant).

Durée de lecture du portail visée : 10 à 15 minutes.

## Page de courant (× 9)

1. **Carte d'identité** : la fiche existante (contenu v1 repris et relu), en tête de page.
2. **Mini-frise** : la ligne du courant seule, avec les bandes de régimes, pour le situer
   d'un coup d'œil (composant `Frise` réutilisé avec une seule ligne, ou option
   `compacte`). Doit rester lisible sur mobile.
3. **Récit** : 1 500 à 2 500 mots, en 4 à 7 sections `h2` aux titres évocateurs et datés,
   par exemple « Le refus de la Révolution (1789-1799) ». Le récit suit le courant de sa
   naissance à 1900 et raconte les événements du siècle depuis son point de vue. Chaque
   chapitre doit faire sentir une dramaturgie (naissance, apogée, chute, recomposition)
   et dire qui sont les adversaires et alliés du moment, avec un lien vers leur page.
   Les termes techniques sont définis à leur première apparition **dans la page** (via
   `Encadre` ou en une phrase), car une page de courant peut être lue seule.
4. **« Et après 1900 »** : 3 à 6 lignes sur le devenir. Puis navigation précédent/suivant.

Chaque page a son `resume` (une phrase) et sa `dureeLecture`.

## Plan indicatif des récits (à ajuster si l'histoire l'exige)

**Légitimistes** — Le refus (1789-1799 : émigration, Vendée, chouannerie, Quiberon) ·
Sous Napoléon : ralliements et complots (Cadoudal 1804) · La revanche (1814-1830 : Charte,
Cent-Jours, Terreur blanche, Chambre introuvable, Decazes, duc de Berry 1820, Villèle,
Charles X, sacre 1825, lois de 1825, Polignac, ordonnances) · La fidélité dans l'opposition
(1830-1848 : refus de Louis-Philippe, duchesse de Berry 1832, Berryer) · Dans le parti de
l'Ordre et sous l'Empire (1848-1870 : loi Falloux, fusion manquée, Chambord) · L'occasion
manquée (1871-1879 : Assemblée monarchiste, drapeau blanc octobre 1873, Ordre moral,
septennat, lois de 1875, 16 mai) · La dispersion (1883-1900 : mort de Chambord, Orléans
ou « blancs d'Espagne », Ralliement, vers l'Action française).

**Orléanistes** — Monarchiens et libéraux (1789-1814 : Mounier, Constant, Mme de Staël) ·
Les doctrinaires (1814-1830 : Royer-Collard, Guizot, Decazes, « juste milieu », les 221,
Trois Glorieuses, « roi des Français ») · Le règne (1830-1848 : Résistance contre Mouvement,
Perier, lois de septembre 1835, « enrichissez-vous », Guizot 1840-1848, banquets, février
1848) · Dans le parti de l'Ordre (1848-1852 : Thiers, Falloux, 2 décembre, exil) · Opposition
libérale à l'Empire (Broglie, Prévost-Paradol, Empire libéral) · La République des ducs
(1871-1877 : Thiers « la République sera conservatrice ou ne sera pas », Broglie, Ordre moral,
amendement Wallon, 16 mai) · Vers la droite républicaine (1877-1900 : ralliement progressif,
centre droit, Méline).

**Bonapartistes** — Le général et le Consul (1795-1804 : Vendémiaire, Italie, Brumaire,
Code civil, Concordat, plébiscites) · L'Empire (1804-1815, Cent-Jours) · La légende
(1815-1848 : Mémorial, Béranger, demi-soldes, Hugo, retour des cendres 1840, Strasbourg 1836,
Boulogne 1840, « Des idées napoléoniennes » 1839, « Extinction du paupérisme » 1844) · Le
prince-président (1848-1851 : 10 décembre 1848, conflit avec l'Assemblée, 2 décembre 1851,
plébiscite) · Le Second Empire (1852-1870 : candidatures officielles, prospérité, Haussmann,
Crimée, Italie, libéralisation 1860-1870, Ollivier, plébiscite de mai 1870, Sedan) · Après
Sedan (1870-1900 : Rouher, Appel au peuple, mort de Napoléon III 1873, Prince impérial 1879,
jérômistes et victoriens, boulangisme, dilution dans le nationalisme plébiscitaire).

**Républicains** — Naissance (1789-1799 : Cordeliers, Varennes, Champ-de-Mars, 10 août,
21 septembre 1792, Girondins et Montagnards, Terreur, Thermidor, Directoire) · L'éclipse
(1799-1830 : Charbonnerie, quatre sergents de La Rochelle 1822, déception de 1830) · Sociétés
secrètes et barricades (1830-1848 : Société des droits de l'homme, juin 1832, avril 1834,
lois de septembre 1835, Le National, La Réforme, banquets) · La République de 1848 (gouvernement
provisoire, suffrage universel, Lamartine, élections d'avril, Juin, Cavaignac, parti de
l'Ordre, loi du 31 mai 1850, 2 décembre, Baudin, exils) · L'opposition à l'Empire (1852-1870 :
les Cinq, Favre, Simon, 1863, Belleville 1869, Rochefort) · Fonder la République (1870-1879 :
4 septembre, Défense nationale, Commune vue des républicains, Thiers, lois de 1875, 16 mai,
les 363, « se soumettre ou se démettre », 1879, Marseillaise et 14 juillet 1880) · La République
opportuniste (1879-1900 : Ferry, école, libertés de 1881 et 1884, colonies, scission des
radicaux, Boulanger, Panama, Dreyfus, Waldeck-Rousseau 1899).

**Radicaux** — Racines jacobines (1793-1848 : Ledru-Rollin, démoc-socs, 13 juin 1849) ·
Belleville (1869) · Clemenceau contre les opportunistes (1876-1885 : La Justice, Tunisie,
Tonkin, programme : séparation, impôt sur le revenu, Sénat) · L'épreuve de Boulanger et de
Panama (1886-1893 : soutien puis combat, Clemenceau battu en 1893) · Le retour par Dreyfus
(1894-1900 : Bourgeois 1895 et le solidarisme, L'Aurore, « J'accuse… ! », Brisson, Waldeck) ·
Et après : parti radical 1901, Combes, 1905.

**Socialistes** — Précurseurs (1796-1840 : Babeuf, Saint-Simon, Fourier, Cabet, Considerant) ·
Le réveil ouvrier (1830-1848 : canuts 1831 et 1834, Proudhon 1840, Louis Blanc 1839, Blanqui) ·
1848 (commission du Luxembourg, ateliers nationaux créés par le gouvernement provisoire, 15 mai,
Juin, démoc-socs 1849, répression) · Sous l'Empire (exil, Manifeste des Soixante 1864,
Internationale 1864, Tolain, Varlin, grèves 1869-1870) · La Commune et ses suites (1871 :
programme, Semaine sanglante, déportation, amnistie 1880) · Renaissance (1876-1890 : congrès
ouvriers, Guesde, Marseille 1879, Parti ouvrier 1882, possibilistes, allemanistes 1890,
blanquistes de Vaillant, Malon) · Vers Jaurès (1890-1900 : Fourmies 1891, Carmaux 1892,
élections de 1893, Jaurès, Millerand et Saint-Mandé 1896, Dreyfus, « cas Millerand » 1899) ·
Et après : 1905.

**Anarchistes** — Proudhon (1840-1865 : propriété, mutuellisme, fédéralisme) · Bakounine et
l'Internationale (1864-1872 : rupture avec Marx, La Haye) · Après la Commune (Fédération
jurassienne, propagande par le fait 1881, Kropotkine, procès de Lyon 1883, Louise Michel) ·
Les attentats (1892-1894 : Ravachol, Vaillant, Henry, Caserio ; lois « scélérates », procès des
Trente 1894) · Le tournant syndical (1892-1900 : Pelloutier, Bourses du travail, CGT 1895,
grève générale) · Et après : charte d'Amiens 1906.

**Catholiques** — L'Église et la Révolution (1789-1814 : constitution civile du clergé,
réfractaires, Concordat 1801) · Trône et autel (1814-1830 : Congrégation, missions, loi sur
le sacrilège 1825, anticléricalisme et 1830) · Lamennais et la liberté (1830-1834 : L'Avenir,
Mirari vos) · Le parti catholique (1840-1850 : Montalembert, Lacordaire, liberté de
l'enseignement, loi Falloux) · Sous l'Empire (soutien puis rupture après l'Italie 1859-1860,
Veuillot contre Dupanloup, Syllabus 1864, Vatican I 1870) · Ordre moral et combat scolaire
(1871-1889 : Sacré-Cœur, pèlerinages, décrets de 1880 contre les congrégations, lois Ferry) ·
Catholicisme social et Ralliement (1871-1900 : de Mun, La Tour du Pin, Rerum Novarum 1891,
toast d'Alger 1890, Au milieu des sollicitudes 1892, La Croix et l'affaire Dreyfus, Sillon
1894) · Et après : 1905.

**Nationalistes** — La nation en armes (1789-1815 : Valmy, patriotisme jacobin, levée en
masse) · Un nationalisme de gauche (1815-1870 : contre les traités de 1815, Michelet, Quinet,
printemps des peuples 1848, Hugo) · La blessure de 1871 (Alsace-Lorraine, revanche, Gambetta
« y penser toujours, n'en parler jamais ») · Déroulède et la Ligue des patriotes (1882) ·
Le boulangisme (1886-1889 : revanche, révision, plébiscite ; 27 janvier 1889 ; fuite ; 1891) ·
L'antisémitisme (Drumont 1886, La Libre Parole 1892, Panama) · L'affaire Dreyfus et le
basculement (1894-1900 : Barrès, Ligue antisémitique, Ligue de la patrie française, Fort
Chabrol 1899, Action française 1899) · Et après : Maurras et les ligues.

## Contraintes

- Tout ce qui existait dans les fiches v1 et dans le récit par régime v1 doit être réutilisé
  ou réécrit, pas perdu : relire les deux avant d'écrire.
- Pas de doublon entre pages : un même événement peut apparaître dans plusieurs récits,
  mais raconté depuis le point de vue du courant concerné.
- `npm run build` passe sans erreur ; 11 pages générées (accueil, portail, 9 courants).
