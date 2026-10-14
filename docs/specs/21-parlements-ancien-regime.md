# Spec 21 — « Les parlements d'Ancien Régime » (sous-page de la Révolution)

Décisions prises avec l'utilisateur le 2026-10-14.

## Objectif pédagogique

Expliquer **ce qu'étaient les parlements de l'Ancien Régime** — non pas des assemblées élues,
mais des **cours de justice souveraines** — et raconter **leur histoire du XIIIe siècle à leur
suppression en 1790** : comment des juges du roi sont devenus ses principaux opposants, au
point de déclencher la crise de 1787-1788, puis ont disparu avec la Révolution. Niveau lycée /
culture générale. Lecture en **30 à 35 minutes** (environ 7 000 à 8 000 mots de texte, hors
encadrés, glossaire et fiches).

Dès l'ouverture, lever le contresens : le mot « parlement » ne désigne pas ici le Parlement
au sens moderne (assemblée qui vote les lois) ; dire en une phrase pourquoi le mot a changé
de sens (influence anglaise au XVIIIe et au XIXe siècle).

## Place dans le site

- **Première sous-page de la leçon « La Révolution française »** (spec 20) :
  `src/content/lecons/xixe/revolution-francaise/parlements.mdx`, thème `politique`,
  `ordre: 1`, `periode` du type `"XIIIe siècle-1790"` (format à aligner sur ce qu'accepte
  et affiche le site), `dureeLecture` réel.
  Adresse : `/xixe/lecons/revolution-francaise/parlements/`.
- Elle doit apparaître automatiquement dans la liste des sous-pages de la page Révolution
  (`ListeSousPages`), sans modifier cette page.
- Ajouter dans la page Révolution un **renvoi discret** vers cette sous-page dans la partie 1
  (révolte des parlements, 1787-1788), et éventuellement au moment de leur suppression
  (1790), via `src/utils/adresses.ts`. C'est la seule modification admise sur la page
  Révolution. Si une fiche de glossaire « parlement » existe dans les données de la page
  Révolution, y ajouter le lien.
- La page remonte bien avant 1789 : c'est assumé, elle éclaire les causes de la Révolution
  (prologue admis par CLAUDE.md, élargi ici avec l'accord de l'utilisateur).

## Fil conducteur : l'institution, puis le bras de fer avec le roi

### Première partie — Comprendre l'institution (environ un tiers du texte)

Une vraie partie explicative, avec des sous-sections :
- **Origines** : la *Curia regis*, la cour du roi siégeant « en parlement » sous Saint Louis,
  la fixation à Paris (palais de la Cité), l'ordonnance de 1345 ; justice déléguée et
  justice retenue. Dates prudentes.
- **Le Parlement de Paris et les parlements de province** : création échelonnée (Toulouse,
  Grenoble, Bordeaux, Dijon, Rouen, Aix, Rennes, Pau, Metz, Besançon, Douai, Nancy…) et
  conseils souverains ; immensité du ressort de Paris (environ un tiers du royaume).
- **Organisation** : Grand-Chambre, chambres des enquêtes et des requêtes, Tournelle
  (criminel), premier président, présidents à mortier, conseillers, gens du roi (procureur
  général, avocats généraux).
- **Les magistrats** : offices achetés (vénalité), paulette (1604), hérédité de fait,
  épices, **noblesse de robe**, dynasties parlementaires, mode de vie et culture (jansénisme,
  gallicanisme, droit).
- **Les pouvoirs** : juger en dernier ressort, **enregistrer** les ordonnances et édits,
  **remontrances**, arrêts de règlement, police (au sens large) ; la riposte royale :
  lettres de jussion, **lit de justice**, exil, cassation par le Conseil du roi.
- La « théorie » parlementaire : le Parlement gardien des lois fondamentales, la thèse de
  l'union des classes (tous les parlements ne formant qu'un corps), la prétention à
  représenter la nation.

### Seconde partie — Le bras de fer avec le roi (récit chronologique)

Chaque section s'ouvre par une question « pourquoi » et se ferme par un « À retenir ».
Plan indicatif, l'agent peut l'ajuster :
1. **Du XIVe au XVIe siècle** : un corps au service du roi qui s'affirme ; guerres de
   Religion et Ligue (le Parlement et l'arrêt Lemaistre de 1593 sur la loi salique).
2. **Le XVIIe siècle** : régences et Fronde parlementaire (1648, arrêt d'Union, chambre
   Saint-Louis), puis la mise au pas par Louis XIV (déclaration de 1673 : enregistrement
   d'abord, remontrances ensuite).
3. **La revanche de 1715** : cassation du testament de Louis XIV, rétablissement du droit de
   remontrance préalable par le Régent.
4. **Le siècle des conflits (1715-1770)** : bulle *Unigenitus* et jansénisme, affaire des
   billets de confession, conflits fiscaux (vingtièmes), expulsion des jésuites (1762-1764),
   affaire de Bretagne (La Chalotais, d'Aiguillon) ; la **séance de la Flagellation** (3 mars
   1766).
5. **Le « coup de majesté » de Maupeou (1771-1774)** : exil des parlementaires, conseils
   supérieurs, suppression de la vénalité, opinion publique divisée ; rappel des parlements
   par Louis XVI en 1774 et ses conséquences.
6. **Les parlements contre les réformes (1774-1788)** : Turgot, puis Calonne et Brienne ;
   exil à Troyes (1787), arrêté du **3 mai 1788** sur les lois fondamentales, édits de
   Lamoignon (mai 1788), journée des Tuiles et Vizille ; le roi cède et convoque les états
   généraux.
7. **La chute (1788-1790)** : l'arrêt du 25 septembre 1788 (forme de 1614) qui ruine la
   popularité des parlements, mise en vacances (novembre 1789), suppression par la
   Constituante (loi des 16-24 août 1790, dernières séances en 1790), nouvelle organisation
   judiciaire. Dates à vérifier précisément.

### Épilogue

Ce qui en reste : méfiance durable envers le « gouvernement des juges », interdiction faite
aux juges de s'immiscer dans le pouvoir législatif (loi de 1790), Cour de cassation, le
Palais de justice ; et le glissement du mot « parlement » vers les assemblées au XIXe siècle.
Quelques paragraphes seulement.

## Éléments d'appui

Mêmes principes que la page Révolution (spec 20), en **réutilisant ses composants**
(`FriseJournees`, `Citation`, `Question`, `Glossaire`, `Personnages`, `Encadre` type
`historiens`, `Oeuvre`), généralisés si besoin sans casser la page Révolution :
- **Frise chronologique** XIIIe siècle-1790 en tête, monochrome, cliquable vers les parties
  et grandes dates. L'échelle doit rester lisible malgré cinq siècles (échelle par segments
  ou compression des siècles anciens, à signaler visuellement).
- **Carte des parlements** : nouvelle carte SVG monochrome de la France (frontières de 1789
  approximatives), les parlements et conseils souverains placés sur leur ville, avec date de
  création ; ressorts approximatifs en nuances de gris ou motifs, mention « ressorts
  simplifiés ». Créer un composant réutilisable. Le fond de carte doit venir d'une source
  libre et être cité ; ne pas dessiner de contours fantaisistes. Pas d'eau colorée (la
  couleur d'eau est réservée aux cartes de diaporama) : rester en gris.
- **Citations et extraits** (6 à 10), **vérifiés mot pour mot** sur une source en ligne
  (Wikisource, Gallica, archive.org), avec la source précise : par exemple discours de la
  Flagellation (1766), remontrances (Malesherbes, Cour des aides 1775, à signaler comme
  cour voisine si utilisé), arrêté du 3 mai 1788, édit de 1771 ou préambule de Maupeou,
  ordonnance de 1673, un passage de Saint-Simon ou du cardinal de Retz sur la Fronde.
  Pas de citation de mémoire ; formule douteuse écartée ou présentée comme attribuée.
- **Encadrés « À retenir »** à la fin de chaque section du récit et de la partie institution.
- **Deux encadrés « Ce qu'en disent les historiens »**, sans trancher : les parlements,
  défenseurs des libertés ou des privilèges ? ; ont-ils provoqué la Révolution (thèse de la
  « révolte nobiliaire » / « pré-révolution », débats autour d'Egret, Doyle, Swann, Bell,
  Van Kley…) ? Formulation prudente ; ne citer que des historiens et ouvrages réels.
- **Glossaire** (20 à 30 termes) : parlement, cour souveraine, office, vénalité, paulette,
  épices, noblesse de robe, présidents à mortier, enregistrement, remontrances, lettres de
  jussion, lit de justice, arrêt de règlement, ressort, Grand-Chambre, Tournelle, gens du roi,
  jansénisme, gallicanisme, *Unigenitus*, billets de confession, vingtième, lois
  fondamentales, conseils supérieurs…
- **Personnages** (12 à 16 fiches) : Saint Louis, Mathieu Molé, Broussel, Louis XIV, le
  Régent, Louis XV, Maupeou, La Chalotais, Malesherbes, Louis XVI, Brienne, Lamoignon,
  d'Eprémesnil, Barnave ou Mounier (Vizille)…
- **Dates** : dates exactes, formulation prudente en cas de doute.

## Illustrations

**4 à 6 œuvres d'époque du domaine public** : un lit de justice (par ex. celui de Louis XV
en 1715 ou la majorité de Louis XV, 1723), le Palais de justice / la Grand-Chambre, portraits
(Maupeou, Molé, Malesherbes), une gravure de la Fronde ou de la journée des Tuiles.
Réutiliser d'abord les images déjà présentes dans le dépôt (diaporama de la Révolution,
chapitres écrivains, page Révolution) ; sinon télécharger depuis Wikimedia Commons, domaine
public uniquement, avec lien source. Composant `Oeuvre` : gris dans la page, couleur dans la
visionneuse ; images rangées sous `src/assets/oeuvres/xixe/`.

## Liens

- Page Révolution (parente) : lien de retour naturel par la navigation des sous-pages, et
  renvois depuis le récit si pertinent.
- Chapitre écrivains 0 (prologue sur la fin de l'Ancien Régime) si les parlements y sont
  évoqués.
- Adresses via `src/utils/adresses.ts` uniquement.

## Design et forme

Design du site, strictement monochrome (CLAUDE.md). Typographie française (espaces
insécables avant `:` `;` `?` `!`, guillemets « »). Pas de quiz. Responsive : frise et carte
lisibles sur téléphone.

## Critères d'acceptation

- La page paraît à `/xixe/lecons/revolution-francaise/parlements/` et dans la liste des
  sous-pages de la page Révolution, sans modification de la page Révolution autre que les
  renvois discrets.
- Contresens sur le mot « parlement » levé dès l'ouverture.
- Partie institution complète, puis récit XIIIe siècle-1790, chaque section ouverte par sa
  question et close par un « À retenir » ; épilogue.
- Frise, carte, citations vérifiées avec sources, deux encadrés historiens, glossaire,
  personnages, 4 à 6 œuvres.
- Aucune couleur hors gris ; typographie française respectée.
- `npm run build` passe sans erreur ; la page Révolution s'affiche toujours correctement.
