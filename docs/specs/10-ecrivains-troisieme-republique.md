# Spec 10 — Le siècle raconté par ses écrivains, chapitre 8 : la IIIe République jusqu'à 1900 (1871-1900)

Suit la **charte** `docs/specs/00-charte-chapitres-ecrivains.md`, qui fixe toutes les règles
communes (choix des textes, format, exactitude, appareil, convention MDX, procédure, checklist).
Cette spec ne fixe que ce qui est propre au chapitre. Slug : `08-troisieme-republique` ;
`numero: 8` ; `titre: "La IIIe République jusqu'à 1900"` ; `periode: "1871-1900"`.

Spec rédigée le 2026-10-06 sans questions préalables à l'utilisateur (session autonome, écrite en
même temps que les specs 08 et 09 des chapitres 6 et 7) : les choix marqués « par défaut »
peuvent être revus.

## Objectif

Raconter, par les textes, comment une République née par défaut devient le régime durable de la
France : la République conservatrice de Thiers, l'« ordre moral » et l'espoir d'une restauration
monarchique, la victoire des républicains (1877-1879), les grandes lois de la décennie 1880
(école, presse, syndicats), le culte de la Révolution et des grands hommes (funérailles de Hugo),
la colonisation, la revanche et le nationalisme, le boulangisme, Panama, les anarchistes et la
question sociale, jusqu'à l'affaire Dreyfus qui coupe la France en deux et l'Exposition universelle
de 1900 qui clôt le siècle. C'est le dernier chapitre de la section : sa conclusion referme le
siècle ouvert en 1789.

## Bornes et articulation avec les chapitres voisins

- **Début** : après la Semaine sanglante (fin mai 1871) : Thiers chef du pouvoir exécutif puis
  président, la libération du territoire (1873). La guerre, la Commune et sa répression immédiate
  sont au chapitre 7 : un rappel d'une phrase dans l'introduction. Les procès et déportations de
  communards peuvent être évoqués à travers l'amnistie de 1880.
- **Fin** : l'année 1900 (Exposition universelle d'avril-novembre 1900 ; la fin de l'affaire
  Dreyfus avec la grâce de septembre 1899 et la loi d'amnistie de décembre 1900). Des textes
  écrits après 1900 sur des faits de 1871-1900 sont admis (regard rétrospectif : Péguy,
  *Notre jeunesse*, 1910 ; Barrès, *Leurs figures*, 1902), à condition que l'auteur soit mort
  après 1800 (toujours vrai ici). Rien sur des faits postérieurs à 1900 : la conclusion peut
  seulement les évoquer d'une phrase (séparation des Églises et de l'État, 1905).
- Ne pas réutiliser une page Wikisource déjà citée dans les chapitres 0 à 5 (voir les JSON de
  `scripts/ecrivains/chapitres/`), ni une page qui porte sur le Second Empire (chapitre 6) ou sur
  1870-1871 (chapitre 7), écrits en parallèle. *La Débâcle* et *L'Année terrible* sont réservées
  au chapitre 7.

## Parties prévues (par défaut ; 4 parties, 4 à 9 extraits chacune)

1. **1871-1879 : la République sans républicains** — Thiers et la libération du territoire ;
   l'Assemblée monarchiste ; le comte de Chambord et le drapeau blanc (1873) ; Mac-Mahon et
   l'ordre moral (le Sacré-Cœur) ; les lois constitutionnelles de 1875 (amendement Wallon) ;
   la crise du 16 mai 1877 (« se soumettre ou se démettre », Gambetta) ; la démission de
   Mac-Mahon (1879).
2. **1879-1889 : la République des républicains** — le retour des Chambres à Paris, *La Marseillaise*
   et le 14 Juillet (1880) ; l'amnistie des communards (1880) ; l'école de Jules Ferry (1881-1882 ;
   *Lettre aux instituteurs*, 1883) ; la liberté de la presse (1881) ; les syndicats (1884) ; la
   colonisation (débat Ferry-Clemenceau, juillet 1885) ; les funérailles de Victor Hugo
   (1er juin 1885) ; la presse et l'argent (*Bel-Ami*) ; Germinal-Decazeville et la condition
   ouvrière ; le boulangisme (1886-1889).
3. **1889-1897 : crises et inquiétudes de fin de siècle** — l'Exposition de 1889 et la tour Eiffel ;
   la fusillade de Fourmies (1er mai 1891) ; le scandale de Panama (1892-1893) ; les attentats
   anarchistes (Ravachol, Vaillant, l'assassinat de Sadi Carnot en 1894) et les « lois
   scélérates » ; l'essor du socialisme (Jaurès, Guesde) ; le ralliement des catholiques ; la
   « décadence » et le nationalisme (Barrès).
4. **1894-1900 : l'Affaire et la fin du siècle** — la condamnation et la dégradation de Dreyfus
   (1894-1895) ; « J'accuse… ! » (13 janvier 1898) et le procès Zola ; dreyfusards et
   antidreyfusards (Ligue des droits de l'homme, Ligue de la patrie française) ; le procès de
   Rennes et la grâce (1899) ; l'Exposition universelle de 1900.

## Sensibilités à représenter (au moins trois, aucune au-delà de la moitié)

- **Républicains opportunistes et radicaux** : Gambetta, Jules Ferry, Clemenceau, Hugo (sénateur),
  Zola (dreyfusard), Anatole France.
- **Socialistes et anarchistes** : Jaurès (*Les Preuves*, 1898 ; discours), Jules Guesde, Paul
  Lafargue (*Le Droit à la paresse*, 1880), Vallès (*Le Cri du peuple*, 1883-1885), Louise Michel,
  Jean Grave, Octave Mirbeau.
- **Monarchistes et conservateurs** : le comte de Chambord (manifeste du 27 octobre 1873, s'il est
  sur Wikisource sous son nom), le duc de Broglie, Albert de Mun.
- **Catholiques** : Louis Veuillot (mort en 1883), Léon Bloy, Albert de Mun, Brunetière.
- **Nationalistes et antidreyfusards** : Paul Déroulède, Maurice Barrès (*Les Déracinés*, 1897 :
  « La vertu sociale d'un cadavre » sur les funérailles de Hugo ; *Scènes et doctrines du
  nationalisme*, 1902), Brunetière (*Après le procès*, 1898). Édouard Drumont est admissible
  comme **source à charge** d'un antisémitisme alors puissant, à condition que le regard critique
  le dise clairement ; ne retenir alors qu'un passage où l'antisémitisme est explicite mais sans
  appel au meurtre, et le replacer dans le contexte de l'Affaire. Par défaut, préférer Barrès ou
  Brunetière ; Drumont seulement si aucune autre voix antidreyfusarde n'est disponible.
- **Regards d'écrivains** : Maupassant, Daudet, les Goncourt, Huysmans, Verlaine, Mallarmé.
- Hugo, Zola, Vallès, Renan, Flaubert déjà fichés dans `auteurs.ts` : compléter seulement
  `oeuvres`.

Pour chaque grand épisode (l'ordre moral et le 16 mai, l'école laïque, la colonisation, le
boulangisme, l'Affaire), chercher au moins une voix favorable et une voix hostile.

Aucune exception demandée : tous les auteurs sont morts après 1800 ; aucun auteur étranger, aucune
traduction. Les débats sur les colonies sont admis parce qu'ils se déroulent en France (Chambre
des députés, presse) : pas de récit des campagnes coloniales elles-mêmes.

## Pistes d'extraits (indicatives, à vérifier sur Wikisource ; viser 24 à 30 extraits)

### Textes contemporains (cible : environ deux tiers)

- Gambetta, discours de Lille (15 août 1877 : « se soumettre ou se démettre ») ; discours de
  Grenoble (1872, les « nouvelles couches sociales »).
- Hugo, *Actes et paroles — Depuis l'exil* (discours sur l'amnistie, 1876-1880) ; *Choses vues*
  des années 1870-1885.
- Jules Ferry, *Lettre aux instituteurs* (17 novembre 1883) ; discours du 28 juillet 1885 sur la
  colonisation ; réponse de Clemenceau (30 juillet 1885).
- Maupassant, *Bel-Ami* (1885) ; chroniques (*Gil Blas*, *Le Gaulois*) ; *La Vie errante* (1890),
  « Lassitude » : la tour Eiffel. Fiction pour *Bel-Ami* : le signaler.
- Zola, *Germinal* (1885 ; l'action se passe sous l'Empire : à éviter ici), « J'accuse… ! »
  (*L'Aurore*, 13 janvier 1898), *Lettre à la France* (1898), *La Vérité en marche* (1901).
- Barrès, *Les Déracinés* (1897), *L'Appel au soldat* (1900) : le boulangisme.
- Anatole France, *Monsieur Bergeret à Paris* (1901) ou *L'Anneau d'améthyste* (1899) : l'Affaire
  vue par un dreyfusard ironique.
- Jaurès, *Les Preuves* (1898) ; discours sur Fourmies ou sur les lois scélérates.
- Lafargue, *Le Droit à la paresse* (1880) ; Vallès, articles ; Louise Michel, *Mémoires* (1886).
- Goncourt, *Journal* (1871-1896) : les funérailles de Hugo, l'Exposition de 1889.
- Verlaine, *Jadis et naguère* (1884) ; Huysmans, *À rebours* (1884) ; Déroulède, *Chants du
  soldat* (1872) ou *Nouveaux chants du soldat* (1875).
- Brunetière, *Après le procès* (1898) ; Péguy, articles de 1898-1900 (*Revue blanche*,
  *Cahiers de la quinzaine*, 1900).
- Daudet, *L'Immortel* (1888), *Numa Roumestan* (1881 : la politique méridionale).

### Témoins qui écrivent tard (rétrospectif · témoin)

- Péguy, *Notre jeunesse* (1910) : la mystique dreyfusarde ; Péguy (né en 1873) est témoin de
  l'Affaire.
- Barrès, *Leurs figures* (1902) : Panama.
- Léon Blum, *Souvenirs sur l'Affaire* (1935) seulement s'il est sur Wikisource (droits).
- Daudet (Léon), Jules Renard (*Journal*, pour des faits de 1887-1900, contemporain).

## Thèmes à couvrir (au moins la plupart)

La République conservatrice ; le drapeau blanc ; l'ordre moral ; le 16 mai ; l'école laïque ; le
14 Juillet et *La Marseillaise* ; l'amnistie ; la colonisation ; les funérailles de Hugo ; la presse
et l'argent ; le boulangisme ; l'Exposition de 1889 ; Fourmies et la question sociale ;
Panama ; les anarchistes ; l'Affaire Dreyfus ; l'Exposition de 1900.

## Critères d'acceptation propres au chapitre

En plus de la checklist de la charte :
- Les bornes ci-dessus sont respectées (rien sur la guerre de 1870 ni la Commune sauf un rappel ;
  aucun fait postérieur à 1900 sauf une phrase de la conclusion).
- Au moins une voix favorable et une voix hostile pour l'école laïque, la colonisation et l'Affaire.
- Au moins un texte de fiction et un de poésie.
- La conclusion, en un paragraphe, referme la section entière (de 1789 à 1900) au lieu d'annoncer
  un chapitre suivant ; vérifier que la mise en page ne cherche pas un chapitre 9 (lien
  « chapitre suivant » absent ou remplacé par un retour à l'accueil de la section : si un
  composant partagé doit changer, le faire par une petite touche et le signaler).
- Le compte rendu liste les pistes écartées faute de source sur Wikisource.

## Écarts constatés (rédaction du chapitre, 2026-10-06)

- **Parties** : les quatre parties ont été redécoupées pour équilibrer les extraits :
  « 1871-1879 : la République sans républicains » (4), « 1879-1885 : la République des
  républicains » (8), « 1886-1893 : la tour, le général et les scandales » (6), « 1894-1900 :
  l'Affaire et la fin du siècle » (8). Le ralliement (Brunetière, 1894-1895) ouvre la dernière partie.
- **26 extraits**, 17 contemporains et 9 rétrospectifs ; seuls deux extraits (Bainville) sont
  « postérieurs » au sens du filtre : les historiens nés après 1880 et libres de droits sont rares.
- La page Wikisource de l'Histoire de France de Bainville (chapitre XXI) est citée deux fois
  (deux passages distincts : le 16 mai ; Tunisie et Tonkin).
- **Voix antidreyfusardes** : Brunetière (« Après le procès ») ; Drumont n'a pas été retenu. Les
  passages antisémites rencontrés (Barrès sur Panama, Léon Daudet, insultes rapportées par Reinach,
  clichés de Bel-Ami) sont signalés dans les regards critiques ; chez Léon Daudet, le paragraphe
  contenant l'injure a été laissé hors de l'extrait.
- **Pistes écartées** faute de source exploitable sur Wikisource : manifeste du comte de Chambord
  (1873), discours de Gambetta à Grenoble (1872), discours de Ferry et de Clemenceau sur la
  colonisation (juillet 1885), Barrès, *Scènes et doctrines du nationalisme* (« La parade de
  Judas »), Verlaine, « Langueur » (passage clé trop court) ; Déroulède, *Chants du soldat*, et
  Rimbaud sont réservés au chapitre 7.
- **Mise en page** : `Chapitre.astro` affiche « Tous les chapitres → » à la place du lien
  « chapitre suivant » quand il n'y a pas de chapitre suivant (chapitre 8).
