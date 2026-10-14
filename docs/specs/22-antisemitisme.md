# Spec 22 — « L'antisémitisme en France au XIXe siècle »

Décisions prises avec l'utilisateur le 2026-10-14.

## Objectif pédagogique

Comprendre **comment s'est formé l'antisémitisme moderne en France au XIXe siècle** : d'où il
vient (l'antijudaïsme chrétien), quelles familles idéologiques l'ont porté, avec quels
arguments et quels mécanismes rhétoriques, et comment ces familles ont convergé dans les années
1880-1890 jusqu'à l'affaire Dreyfus. Niveau lycée / culture générale. Lecture en **30 à 35
minutes** (environ 7 000 à 8 000 mots de texte, hors encadrés, glossaire et fiches).

Le sujet est sensible : ton sobre, rigoureux, sans complaisance ni pathos. Les thèses
antisémites sont **exposées pour être comprises et déconstruites**, jamais reprises à son
compte ; chaque affirmation fausse qu'elles contiennent est identifiée comme telle.

## Place dans le site

- Leçon autonome : `src/content/lecons/xixe/antisemitisme.mdx`, thème `societe`,
  adresse `/xixe/lecons/antisemitisme/`, `periode: "1789-1906"`, `dureeLecture` réel,
  `ordre` cohérent avec les leçons existantes du thème.
- Une seule page pour l'instant, conçue pour accueillir plus tard des sous-pages
  (ex. une page sur l'affaire Dreyfus) dans `src/content/lecons/xixe/antisemitisme/` :
  liste des sous-pages invisible tant qu'il n'y en a pas (`ListeSousPages`), ancres
  stables et lisibles.

## Fil conducteur : par familles d'antisémitisme

1. **Ouverture — Les Juifs de France et l'émancipation** (contexte, assez bref) : environ
   40 000 Juifs en 1789 (communautés séfarades du Sud-Ouest, ashkénazes d'Alsace-Lorraine,
   « Juifs du pape » du Comtat), décrets du 28 janvier 1790 et du 27 septembre 1791, la formule
   de Clermont-Tonnerre (à vérifier mot pour mot), Napoléon : Assemblée des notables, Grand
   Sanhédrin (1807), consistoires (1808), « décret infâme » (1808) ; puis intégration,
   « israélites » français, franco-judaïsme, figures (Crémieux, les Rothschild, Rachel…),
   suppression du serment *more judaico* (1846). Démographie prudente.
2. **L'antijudaïsme catholique** : le vieux fond chrétien (peuple « déicide », accusation de
   meurtre rituel, affaire de Damas 1840), l'hostilité à la Révolution et à l'émancipation,
   puis la presse catholique de la fin du siècle (*La Croix* des assomptionnistes, qui se dit
   « le journal le plus antijuif de France »), l'abbé Chabauty ; mais aussi les catholiques
   qui s'y opposent. Formulation nuancée.
3. **L'antisémitisme socialiste et anticapitaliste** : l'assimilation du Juif au banquier et
   au capital, Fourier, Toussenel (*Les Juifs, rois de l'époque*, 1845), Proudhon (carnets),
   Blanquistes (Tridon) ; le mythe des Rothschild ; puis le reflux, quand une partie des
   socialistes (Jaurès après hésitations, Guesde, Allemane) rejoint le camp dreyfusard.
   Formulation prudente (ex. la phrase attribuée à Bebel sur « le socialisme des imbéciles »,
   à présenter comme attribuée si non vérifiable).
4. **L'antisémitisme « racial » et pseudo-scientifique** : le vocabulaire des races
   (Renan, sémites et aryens — avec la nuance qu'il le récuse en partie en 1883), Gobineau
   (*Essai sur l'inégalité des races humaines*, 1853-1855, qui n'est pas d'abord antisémite :
   le dire), Vacher de Lapouge ; naissance du mot « antisémitisme » (Wilhelm Marr, Allemagne,
   vers 1879) et son arrivée en France. Expliquer pourquoi la notion de race appliquée aux
   Juifs est fausse.
5. **L'antisémitisme nationaliste** : la défaite de 1870 et la quête de l'ennemi intérieur,
   le Juif présenté comme « étranger » ou « allemand », Barrès ; Algérie : décret Crémieux
   (1870), antisémitisme colonial, Max Régis, émeutes d'Alger (1898), Drumont député d'Alger.
6. **La convergence (1880-1898)** : krach de l'Union générale (1882) et son exploitation,
   **Édouard Drumont**, *La France juive* (1886), immense succès, *La Libre Parole* (1892),
   Ligue antisémitique (Morès, Jules Guérin), affaire de Panama ; comment Drumont fond les
   quatre familles en une synthèse.
7. **L'affaire Dreyfus, point d'aboutissement (1894-1899)** : arrestation et condamnation
   (1894), dégradation (5 janvier 1895), rôle de *La Libre Parole*, Esterhazy, « J'accuse… ! »
   (13 janvier 1898), émeutes antisémites de 1898 en France et en Algérie, deux France qui
   s'affrontent, Rennes (1899), grâce. Les dreyfusards et ceux qui combattent l'antisémitisme
   (Bernard Lazare, Zola, Jaurès, Clemenceau, la Ligue des droits de l'homme, Anatole Leroy-
   Beaulieu). Une partie, pas un récit exhaustif.
8. **Épilogue (1899-1906)** : réhabilitation de Dreyfus (12 juillet 1906) ; ce que le
   XIXe siècle lègue au XXe (l'Action française, le vocabulaire, les réseaux), en quelques
   lignes prudentes, sans anticiper le récit du XXe siècle.

Chaque partie s'ouvre par une question « pourquoi » et se ferme par un « À retenir ».

## Textes et citations

- **Extraits courts** (une à quatre phrases) des auteurs antisémites, **un ou deux par
  famille** : authentiques, **vérifiés mot pour mot** sur une édition en ligne (Gallica,
  Wikisource, archive.org), source précise (titre, date, page ou numéro). Chacun est
  **présenté** (qui, quand, quel public, quel tirage) puis **commenté et déconstruit**
  immédiatement (procédé rhétorique, fausseté factuelle, fonction politique). Pas d'extrait
  gratuitement injurieux, pas de citation isolée de son commentaire.
- **Voix opposées en regard** : Clermont-Tonnerre (1789), Abbé Grégoire, Crémieux, Bernard
  Lazare, Zola (« J'accuse… ! »), Jaurès, Leroy-Beaulieu (*L'Antisémitisme*, 1897), etc.,
  vérifiées de la même façon.
- Aucune citation de mémoire ; une formule douteuse est écartée ou présentée comme attribuée.

## Éléments d'appui

Réutiliser les composants des pages Révolution et parlements (`FriseJournees`, `Citation`,
`Question`, `Glossaire`, `Personnages`, `Encadre` type `historiens`, `Oeuvre`,
`ListeSousPages`) :
- **Frise** 1789-1906 en tête, monochrome, cliquable : émancipation, Sanhédrin, consistoires,
  affaire de Damas, *Les Juifs rois de l'époque*, décret Crémieux, mot « antisémitisme »,
  Union générale, *La France juive*, *La Libre Parole*, Panama, Dreyfus (1894, 1898, 1899,
  1906). Les familles peuvent y figurer comme bandes en gris/motifs.
- **Encadrés « À retenir »** à la fin de chaque partie.
- **Deux ou trois encadrés « Ce qu'en disent les historiens »**, sans trancher : continuité ou
  rupture entre antijudaïsme et antisémitisme ; la France fin de siècle plus antisémite que
  ses voisins ? (Allemagne, Autriche, Russie) ; un « antisémitisme de gauche » ? Historiens
  réels uniquement (Winock, Birnbaum, Sternhell, Poliakov, Wilson, Kauffmann, Joly…).
- **Glossaire** (20 à 30 termes) : antijudaïsme, antisémitisme, judéophobie, émancipation,
  israélite, consistoire, Grand Sanhédrin, séfarade, ashkénaze, meurtre rituel, déicide,
  *more judaico*, décret Crémieux, « sémite » / « aryen » (notions fausses, expliquées comme
  telles), nationalisme, ligue, dreyfusard, antidreyfusard, révision, bordereau…
- **Personnages** (14 à 18 fiches) : abbé Grégoire, Clermont-Tonnerre, Adolphe Crémieux,
  James de Rothschild, Toussenel, Gobineau, Renan, Drumont, Morès, Jules Guérin, Max Régis,
  Barrès, Alfred Dreyfus, Bernard Lazare, Zola, Jaurès, Picquart, Esterhazy…

## Illustrations

**4 à 6 documents d'époque du domaine public** : couverture ou page de *La France juive*,
une de *La Libre Parole* ou caricature antisémite, une de *L'Aurore* (« J'accuse… ! »),
dégradation de Dreyfus (*Le Petit Journal*, 13 janvier 1895), portrait de Bernard Lazare ou
de Crémieux. Les documents antisémites sont présentés **comme des sources**, avec une
légende qui en explique le procédé (stéréotypes visuels) ; pas d'image choquante sans
commentaire. Wikimedia Commons ou Gallica, domaine public, lien source. Composant `Oeuvre`
(gris dans la page, couleur dans la visionneuse), images sous `src/assets/oeuvres/xixe/`.

## Liens vers le reste du site

Renvois discrets : courants politiques (catholiques, socialistes, nationalistes, et
radicaux/républicains pour le camp dreyfusard), page Révolution (émancipation, partie 3),
chapitres écrivains pertinents (Troisième République : Zola, Barrès…), diaporama de la
Troisième République s'il existe. Adresses via `src/utils/adresses.ts`.

## Design et forme

Design du site, strictement monochrome. Typographie française. Pas de quiz. Responsive.

## Exigences historiques

Chiffres prudents (« environ », « selon les estimations ») : population juive (environ
40 000 en 1789, environ 80 000 vers 1880 en métropole, plus ceux d'Algérie), tirages de
*La France juive* et de *La Libre Parole*. Dates exactes. Ne pas projeter la Shoah sur le
XIXe siècle : pas de téléologie, mais un épilogue qui signale la continuité des idées.

## Critères d'acceptation

- La page paraît à `/xixe/lecons/antisemitisme/` et dans l'accueil du XIXe (thème société).
- Ouverture sur l'émancipation, une partie par famille, convergence, affaire Dreyfus,
  épilogue jusqu'en 1906 ; chaque partie ouverte par sa question et close par un « À retenir ».
- Chaque extrait antisémite présenté puis déconstruit ; voix opposées en regard ;
  toutes les citations vérifiées avec source.
- Frise, encadrés historiens, glossaire, personnages, 4 à 6 documents légendés.
- Aucune couleur hors gris ; typographie française respectée.
- `npm run build` passe sans erreur ; aucune autre page cassée.
