# Spec 01 — Les courants politiques en France, 1789-1900

> **Remplacée en partie par la spec 02** (`02-courants-politiques-refonte.md`) : le récit
> par régime et les fiches sur une seule page sont abandonnés au profit d'une page par
> courant. Les sections 1, 2, 5 et 6 ci-dessous restent valables.

## Objectif pédagogique

Donner au lecteur (niveau lycée / culture générale) une carte mentale claire des grandes
familles politiques françaises, de la Révolution à la fin du XIXe siècle : qui elles sont,
d'où elles viennent, ce qu'elles veulent, quand elles dominent, et comment elles se
transforment ou disparaissent. Lecture complète en 30 à 45 minutes.

## Structure de la page (dans cet ordre)

1. **Introduction** (2-3 paragraphes) : pourquoi le XIXe siècle français est le siècle
   où s'inventent les familles politiques modernes ; les trois questions qui les divisent
   (quel régime ? quelle place pour l'Église ? quelle réponse à la question sociale ?).

2. **Frise chronologique 1789-1900** : vue d'ensemble visuelle. Une ligne par courant,
   avec des segments montrant quand le courant existe, quand il est au pouvoir, quand il
   est en déclin. Bornes de régimes en repères verticaux (1789, 1792, 1799, 1804, 1814/15,
   1830, 1848, 1852, 1870, 1875, 1900). Interactive a minima : survol d'un segment =
   infobulle avec le libellé de la période ; clic sur le nom d'un courant = saut vers sa fiche.
   Doit rester lisible sur mobile (défilement horizontal acceptable).

3. **Récit chronologique par régime** : pour chaque régime, un court texte expliquant
   qui s'oppose à qui et sur quoi. Régimes :
   - 1789-1799 Révolution (patriotes/aristocrates, Feuillants, Girondins, Montagnards,
     Terreur, Thermidor, Directoire)
   - 1799-1814 Consulat et Empire (ralliement, opposition royaliste et libérale, Cent-Jours)
   - 1814-1830 Restauration (ultras, doctrinaires, libéraux ; Chambre introuvable,
     Villèle, Polignac, Trois Glorieuses)
   - 1830-1848 Monarchie de Juillet (Mouvement vs Résistance, Thiers vs Guizot,
     légitimistes, républicains et sociétés secrètes, tentatives bonapartistes,
     premiers socialistes, campagne des banquets)
   - 1848-1852 IIe République (républicains modérés, démoc-socs, parti de l'Ordre,
     juin 1848, élection de Louis-Napoléon, loi Falloux, coup d'État du 2 décembre)
   - 1852-1870 Second Empire (empire autoritaire puis libéral, les Cinq, Ollivier,
     tiers parti, plébiscite de 1870, Sedan)
   - 1870-1900 IIIe République (Commune, République des ducs, 16 mai 1877,
     opportunistes vs radicaux, lois Ferry, boulangisme, Ralliement, Panama,
     anarchisme, affaire Dreyfus)

4. **Fiches par courant** : une fiche structurée par courant, toutes sur le même modèle :
   - Bandeau coloré (couleur propre au courant, reprise dans la frise et l'arbre)
   - En une phrase : ce qu'ils veulent
   - Idées clés (3-5 puces)
   - Figures (3-5 noms avec un mot de contexte chacun)
   - Moments clés (3-6 dates)
   - Devenir (comment le courant se transforme ou disparaît à la fin du siècle)

   Courants à traiter :
   - Contre-révolutionnaires → ultras → légitimistes
   - Monarchistes constitutionnels : doctrinaires → orléanistes
   - Bonapartistes (Ier et Second Empire, légende napoléonienne, après 1870)
   - Républicains (de 1792 aux opportunistes : jacobins, sociétés secrètes,
     1848, Gambetta, Ferry)
   - Radicaux (Ledru-Rollin, programme de Belleville, Clemenceau)
   - Socialistes (utopiques, Louis Blanc, Blanqui, Commune, Guesde, possibilistes, Jaurès)
   - Anarchistes (Proudhon, Bakounine, propagande par le fait, lois scélérates,
     anarcho-syndicalisme)
   - Catholiques en politique (Lamennais, Montalembert, catholicisme social,
     Rerum Novarum, Ralliement de 1892)
   - Nationalistes de la fin du siècle (Ligue des patriotes, boulangisme, Drumont,
     Barrès, Action française naissante ; le glissement du nationalisme de gauche vers la droite)

5. **Arbre généalogique des courants** : schéma SVG inline montrant les filiations et
   scissions depuis 1789 (ex. jacobins → républicains → opportunistes / radicaux ;
   babouvistes → Blanqui → socialistes → guesdistes / possibilistes / anarchistes ;
   contre-révolution → ultras → légitimistes ; monarchiens → doctrinaires → orléanistes ;
   Empire → bonapartistes → boulangisme → nationalisme). Mêmes couleurs que les fiches.
   Texte court sous le schéma expliquant les principales filiations.

6. **Pour aller plus loin** : 4-6 références (livres accessibles, manuels), sans lien externe
   obligatoire.

## Contraintes

- Exactitude historique : vérifier chaque date et chaque attribution. En cas de doute,
  formulation prudente plutôt qu'affirmation fausse.
- Niveau lycée : chaque terme technique (ultra, doctrinaire, opportuniste, possibiliste…)
  est défini à sa première apparition.
- Le contenu de la leçon vit dans `src/content/lecons/courants-politiques.mdx`.
  Les données de la frise et de l'arbre peuvent vivre dans un fichier de données séparé
  (JSON/TS) importé par les composants.
- Les composants Frise, Fiche, Arbre doivent être réutilisables pour de futures leçons.
- `npm run build` passe sans erreur ni avertissement bloquant.
