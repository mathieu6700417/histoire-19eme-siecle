# Spec 02 — Le siècle raconté par ses écrivains (cadre + chapitre 1 : la Révolution)

> **Charte en vigueur** : pour les règles de la section (chapitres 2 à 8 compris), [`00-charte-chapitres-ecrivains.md`](00-charte-chapitres-ecrivains.md) prévaut sur cette spec en cas de divergence. La spec ci-dessous garde l'historique des décisions.

## Objectif

Créer une **nouvelle section** du site, distincte des leçons thématiques : une histoire de la
France de 1789 à 1900 **portée par les textes** d'écrivains qui ont vécu au XIXe siècle.
Les extraits passent d'abord : le lecteur traverse le siècle comme une anthologie commentée,
avec de courtes transitions entre les textes. Niveau lycée / culture générale.

Cette itération livre **le cadre de la section + le chapitre 1 (Révolution, 1789-1799)**.
Les chapitres suivants seront ajoutés un par un, chacun avec sa propre spec, sans toucher au cadre.

## Découpage du parcours (par régime, 8 chapitres)

1. La Révolution (1789-1799) — **livré dans cette itération**
2. Consulat et Empire (1799-1815)
3. La Restauration (1814-1830)
4. La monarchie de Juillet (1830-1848)
5. 1848 et la IIe République (1848-1852)
6. Le Second Empire (1852-1870)
7. L'année terrible : guerre et Commune (1870-1871)
8. La IIIe République jusqu'à 1900 (1871-1900)

La page d'accueil de la section affiche les 8 chapitres ; ceux qui ne sont pas encore écrits
apparaissent grisés avec la mention « à venir ».

## Règle absolue : exactitude des extraits

- Tous les textes sont du domaine public. **Chaque extrait est copié mot pour mot depuis
  Wikisource (fr.wikisource.org) en priorité, Gallica à défaut.** Aucune citation de mémoire,
  aucune paraphrase présentée entre guillemets.
- Les coupures internes sont signalées par `[…]`. Orthographe de l'édition source conservée.
- Si un extrait ne peut pas être vérifié à la source, il n'est **pas** publié.
- Chaque extrait porte sa référence précise : auteur, œuvre, partie / livre / chapitre,
  date d'écriture ou de publication.
- **Lien « Lire le chapitre complet »** sous chaque extrait, pointant vers la page précise
  du chapitre (ou de la lettre, du poème, de l'article) sur Wikisource — pas vers la page
  d'accueil de l'œuvre. Gallica seulement si Wikisource n'a pas le texte. Ouverture dans
  un nouvel onglet.

## Genres retenus

Tous, avec un libellé visible sur chaque extrait :
- **Témoignage** (mémoires, journaux, correspondances, choses vues)
- **Roman** (toujours signalé comme fiction)
- **Poésie**
- **Presse / discours**

On privilégie la diversité des voix et des camps politiques dans chaque chapitre
(un chapitre ne doit pas être vu par un seul bord).

## Format d'un chapitre

- Introduction très courte (1 paragraphe) : bornes, enjeu du chapitre.
- **Au moins 20 extraits** (révision du 2026-10-06, après relecture du chapitre 1) de
  **1 à 2 pages chacun, soit environ 40 à 80 lignes / 400 à 900 mots** : une scène ou un épisode
  complet. La poésie peut être plus courte si le poème est complet. Ordre chronologique des
  **faits racontés** (pas des dates d'écriture). Lecture en 1 h 30 à 2 h.
- Entre les extraits : transitions courtes (1-3 phrases) qui font avancer l'histoire.
- Conclusion très courte (1 paragraphe) + lien vers le chapitre suivant.

### Appareil autour de chaque extrait (composant `Extrait`)

**Version courte / version longue** (révision du 2026-10-06) : par défaut, chaque extrait
n'affiche que son **passage clé**, le moment fort (~200-300 mots, 15-30 lignes), choisi
éditorialement et pas forcément au début. Un bouton « Voir plus » (accessible, `aria-expanded`)
déplie le texte complet (400-900 mots), avec ce qui précède et ce qui suit ; dans la version
dépliée, le passage clé reste repérable (filet ou fond discret). Un bouton « Voir moins »
replie et ramène au début de l'extrait. Sans JavaScript, le texte complet s'affiche.
Le passage clé est un sous-ensemble contigu, mot pour mot, du texte complet.

**Les textes d'abord** : seuls restent visibles par défaut le titre de l'extrait, le badge de
genre, une ligne de référence (auteur, œuvre, date), **le texte** et le lien « Lire le chapitre
complet ». Tout le reste (chapeau, mots expliqués, regard critique, fiche auteur) est **replié
par défaut**, dans des blocs `<details>`/`<summary>` sobres et discrets, accessibles au clavier.
Les appels de note dans le texte restent discrets ; cliquer dessus ouvre le bloc des notes
et y conduit.

1. **Chapeau de contexte** (2-3 phrases) : ce qui se passe, qui parle, et **quand le texte
   a été écrit** par rapport aux faits (ex. Hugo écrit *Quatrevingt-treize* en 1874).
2. **Le texte** : mis en valeur typographiquement (citation longue, serif, filet coloré),
   avec le badge de genre.
3. **Mots expliqués** : notes discrètes sur mots, allusions, noms propres difficiles
   (appel de note dans le texte + note sous l'extrait ; ou infobulle accessible au clavier
   et au toucher — sur mobile, les notes doivent rester lisibles sans survol).
4. **Regard critique** (1-2 phrases) : ce que le texte montre, et en quoi il est partial ou
   limité (position politique de l'auteur, fiction vs témoignage, recul temporel).
5. **Référence + lien** « Lire le chapitre complet ».

### Fiche auteur

- À la **première apparition** d'un auteur dans un chapitre : mini-portrait (dates de
  naissance et mort, position politique, œuvre(s) citée(s), 2-3 phrases). Réutiliser /
  adapter le composant `Fiche` existant si pertinent.
- Les données auteurs sont centralisées (ex. collection ou fichier de données `auteurs`)
  pour être réutilisées dans les chapitres suivants et dans l'index.

## Pages à créer

- **Accueil de la section** (ex. `/xixe/ecrivains/`) : titre, courte présentation de la démarche
  (les textes comme sources, avec leurs biais), liste des 8 chapitres.
- **Page chapitre** (ex. `/xixe/ecrivains/<slug>/`) rendue depuis une nouvelle collection
  de contenu MDX (ex. `src/content/ecrivains/xixe/01-revolution.mdx`), schéma : titre, numéro,
  période, résumé, dureeLecture.
- **Index des auteurs** (ex. `/xixe/ecrivains/auteurs/`) : chaque auteur, ses dates, sa fiche,
  et la liste des chapitres où il est cité (généré automatiquement).
- Lien vers la section dans la **navigation commune** et un bloc dédié sur l'accueil du site.
  Ne pas casser les leçons existantes.

## Chapitre 1 — La Révolution (1789-1799) : pistes d'extraits

Indicatives, à vérifier et compléter sur Wikisource. Viser l'équilibre des genres et des camps.
- Chateaubriand, *Mémoires d'outre-tombe* (la prise de la Bastille, les têtes au bout des piques ;
  l'émigration).
- Michelet, *Histoire de la Révolution française* (la Fédération, 14 juillet 1790 ; la Bastille).
- Hugo, *Quatrevingt-treize* (la Convention ; la Vendée) — roman.
- Balzac, *Les Chouans* — roman (la chouannerie).
- Joseph de Maistre, *Considérations sur la France* (1797) — regard contre-révolutionnaire.
- Madame de Staël, *Considérations sur les principaux événements de la Révolution française*.
- Lamartine, *Histoire des Girondins* (les Girondins, la Terreur).
- Vigny, *Stello* (la mort d'André Chénier) — fiction ; éventuellement André Chénier lui-même
  (*La Jeune Captive*, *Iambes*) — poésie écrite en prison en 1794.
- Discours révolutionnaires si l'auteur est aussi écrivain ou si cela sert le récit
  (à justifier : la règle est « écrivains ayant vécu au XIXe siècle » — Chénier, mort en 1794,
  est une exception à signaler, ou à écarter).

Couvrir au moins : 1789 (Bastille, nuit du 4 août ou Déclaration), la fête de la Fédération,
la chute de la monarchie et l'exécution du roi, la Terreur, la Vendée / chouannerie,
Thermidor et le Directoire, et ouvrir sur Bonaparte.

## Design

Respecter le design existant (CLAUDE.md) : fond clair, serif, palette ocre / bordeaux /
bleu nuit. Les extraits doivent être le cœur visuel de la page. Badge de genre de couleur
discrète et distincte par genre. Responsive, confortable sur téléphone.

## Critères d'acceptation

- `npm run build` passe sans erreur.
- Chaque extrait du chapitre 1 a été récupéré sur Wikisource/Gallica et son lien mène au
  bon chapitre ; aucun lien mort.
- Au moins 20 extraits, 40-80 lignes chacun (hors poésie), au moins 3 genres et au moins 2 sensibilités politiques.
- Chaque extrait a chapeau, mots expliqués (si utile), regard critique, référence, lien.
- Index des auteurs généré et à jour.
- Typographie française (espaces insécables, guillemets « »).
- Les pages existantes ne sont pas modifiées, sauf la navigation et l'accueil (ajout d'un lien).

## Révision du 2026-10-06 : sommaire fixe à gauche sur ordinateur

Sur un écran large (à partir d'environ 1200 px), le sommaire du chapitre devient une **colonne
fixe à gauche** (`position: sticky`) qui reste visible pendant la lecture. Il est groupé par
parties, avec le numéro, le titre et l'auteur. Le texte en cours de lecture est surligné
(IntersectionObserver), et la colonne défile elle-même si elle dépasse la hauteur de l'écran.
La colonne de lecture garde sa largeur (`--l-lecture`). Sous 1200 px, rien ne change : le
sommaire reste replié en haut du chapitre, avec les liens « Retour au sommaire ». Ces liens
sont masqués sur ordinateur, où ils ne servent plus.

## Révision du 2026-10-06 : textes contemporains des faits (tous les chapitres)

Demande de l'utilisateur : dans **chaque chapitre**, faire une large place à des textes qui
racontent l'époque, y compris des scènes de roman, de théâtre ou de poésie, **écrits pendant la
période ou peu après** (quelques années au plus), à côté des regards rétrospectifs (Michelet,
Tocqueville, Lamartine, Hugo, etc.).

- **Ajout** de 6 à 8 extraits contemporains aux extraits existants, qui sont conservés.
  Pour les chapitres à venir : viser environ un tiers d'extraits rétrospectifs et deux tiers
  d'extraits contemporains.
- **Exception à la règle « écrivains ayant vécu au XIXe siècle »** pour le prologue et le
  chapitre 1 : on admet des auteurs morts avant 1800 si leur texte date de la période
  (Desmoulins, Mme Roland, Condorcet, Chénier, Olympe de Gouges, Robespierre, Saint-Just,
  Marat…). On le signale dans l'introduction et sur la fiche auteur.
- Chaque extrait indique de façon bien visible sa date d'écriture ou de publication. Le chapeau
  replié précise s'il s'agit d'un texte **contemporain** ou d'un **regard rétrospectif**,
  et l'écart en années avec les faits.
- Pistes pour le chapitre 1 : Desmoulins, *Le Vieux Cordelier* (1793-1794) et *La France libre*
  (1789) ; Mme Roland, *Mémoires* (écrits en prison, 1793) ; Chénier, *Iambes* (1794) ;
  Condorcet, *Esquisse* (1793-1794) ; Olympe de Gouges, *Déclaration des droits de la femme*
  (1791) ; discours de Robespierre, de Danton, de Vergniaud ou de Saint-Just ; Marat,
  *L'Ami du peuple* ; Hébert, *Le Père Duchesne* ; Mercier, *Le Nouveau Paris* (1798, déjà présent) ;
  Arthur Young non retenu (étranger).

## Révision du 2026-10-06 : filtre « Témoins de l'époque »

Sur chaque page de chapitre, une option permet de choisir quels textes afficher :
- **« Témoins de l'époque »** (par défaut) : seuls les textes dont l'auteur a vécu les faits
  racontés, **même s'il écrit plus tard** (Chateaubriand, Staël…) ;
- **« Postérieurs »** : seulement les textes des générations suivantes (Michelet, Hugo,
  Tocqueville, Dumas…), qui n'ont pas vécu les faits ;
- **« Tous les textes »** : les deux ensemble.
(Trois choix, révision du 2026-10-06 ; le mode « Témoins » reste le mode par défaut.)

**Critère, appliqué extrait par extrait** : l'auteur est né au moins 10 ans avant l'année des
faits racontés (assez âgé pour s'en souvenir). Chaque extrait porte l'année des faits (prop
`faits`, ou une plage d'années, auquel cas on retient la première) ; l'année de naissance vient
de `auteurs.ts`. Le statut est calculé au moment du build, pas saisi à la main ; un avertissement
s'affiche au build si l'année des faits manque. Pour les textes fondateurs antérieurs à la période
(Montesquieu, Rousseau…), qui ne racontent pas des faits, on les compte parmi les témoins : ce
sont des voix de l'époque, pas des regards rétrospectifs.

**Interface**
- Un sélecteur à trois options, sobre (deux liens ou boutons en petites capitales, l'option
  active soulignée), placé en haut du chapitre et en tête du sommaire fixe sur ordinateur. Il
  porte un compteur : « 14 textes sur 28 ».
- Le choix est mémorisé (`localStorage`, avec try/catch) et s'applique à tous les chapitres.
- Les extraits masqués disparaissent aussi du sommaire. Une partie qui n'a plus aucun extrait
  visible est masquée. La numérotation est recalculée sur les textes visibles. La durée de
  lecture affichée suit le filtre.
- **Les transitions** entre extraits doivent rester lisibles dans les deux modes : une transition
  liée à un extrait masqué disparaît avec lui. On relit les transitions qui renvoient à un texte
  qu'un mode peut masquer, et on les rend neutres si nécessaire.
- Dans la ligne de référence, un discret « témoin » ou « regard d'une génération suivante »
  complète l'étiquette contemporain / rétrospectif.
- Sans JavaScript, tous les textes s'affichent.
- Si on arrive sur l'ancre d'un extrait masqué, le filtre passe sur « Tous les textes ».
