# Spec 03 — Le siècle raconté par ses écrivains, chapitre 0 : prologue, la France avant 1789

> **Charte en vigueur** : pour les règles de la section (chapitres 2 à 8 compris), [`00-charte-chapitres-ecrivains.md`](00-charte-chapitres-ecrivains.md) prévaut sur cette spec en cas de divergence. La spec ci-dessous garde l'historique des décisions.

Complète la spec 02 (cadre de la section), dont toutes les règles s'appliquent : extraits
copiés mot pour mot depuis Wikisource (Gallica à défaut) et vérifiés contre l'URL du lien,
lien « Lire le chapitre complet » vers la page la plus précise possible, appareil (contexte,
fiche auteur, mots expliqués, regard critique) replié par défaut, texte mis en valeur.

## Objectif

Faire comprendre **pourquoi la Révolution éclate** : la France des années 1770-1789 vue par des
écrivains du XIXe siècle (ou ayant vécu au XIXe siècle). Bornes : vers 1770-1774 (fin du règne
de Louis XV, avènement de Louis XVI) jusqu'à la convocation des États généraux (1788) — le
chapitre 1 commence en janvier 1789 avec Sieyès.

## Format

- **5 à 8 extraits**, même longueur que le chapitre 1 : 1 à 2 pages (400 à 900 mots) chacun.
  Lecture en 30 à 45 minutes. Ordre : du tableau de la société vers la crise finale.
- Pas de découpage en parties obligatoire (le sommaire replié reste en place).
- Introduction et conclusion courtes ; la conclusion mène au chapitre 1.

## Thèmes à couvrir (au moins la plupart)

- La société d'ordres et les privilèges ; la noblesse de province ; les campagnes.
- La centralisation monarchique, l'administration, les intendants.
- Les Lumières et l'esprit public ; la cour, Versailles, la reine.
- Les tentatives de réforme (Turgot, Necker) et la crise financière.
- 1787-1788 : assemblée des notables, révolte des parlements, convocation des États généraux.

## Pistes d'extraits (à vérifier sur Wikisource)

- Tocqueville, *L'Ancien Régime et la Révolution* (1856) : texte central (centralisation ;
  la Révolution éclate quand la situation s'améliore ; état des campagnes). Plusieurs extraits possibles.
- Chateaubriand, *Mémoires d'outre-tombe* : enfance à Combourg, noblesse de province.
- Staël, *Considérations…* : ministère de Necker, crise financière, convocation des États généraux.
- Michelet, *Histoire de la Révolution française*, introduction.
- Romans ou mémoires évoquant l'avant-1789 (Balzac, Stendhal, Mme de Genlis, Mme Vigée Le Brun
  *Souvenirs*, Mme Campan *Mémoires* sur Marie-Antoinette, Talleyrand *Mémoires*) — vérifier
  disponibilité et que l'auteur a bien vécu au XIXe siècle.

Équilibre des sensibilités (nostalgiques de l'Ancien Régime / critiques) et des genres.

## Intégration

- Le chapitre 0 apparaît **avant** le chapitre 1 sur l'accueil de la section, libellé « Prologue ».
- Adapter le schéma (`numero` accepte 0) et le plan des chapitres ; navigation : prologue → chapitre 1.
- Nouveaux auteurs ajoutés aux données centralisées ; l'index se met à jour.

## Critères d'acceptation

- `npm run build` passe.
- 5 à 8 extraits vérifiés mot pour mot, liens valides, 400-900 mots chacun (poésie exceptée).
- Appareil replié, cohérent avec le chapitre 1.
- Le chapitre 1 n'est pas modifié (sauf le lien « chapitre précédent » éventuel).

## Révision du 2026-10-06 : textes d'époque

Demande de l'utilisateur : davantage de textes **qui racontent l'époque**, y compris des scènes de
roman ou de théâtre, **écrits pendant la période elle-même** (vers 1770-1789, au plus tard
autour de 1789-1795), et pas des reconstitutions du XIXe siècle.

- **Ajout** de 6 à 8 extraits d'époque aux 8 existants, qui sont conservés. Total : 14 à 16
  extraits, lecture d'environ 1 h 15. On reprend le découpage en parties du chapitre 1 :
  par exemple « La société et la vie quotidienne », « Les Lumières et l'esprit public »,
  « La cour et la crise ». Ordre : du tableau vers la crise.
- **Exception à la règle « écrivains ayant vécu au XIXe siècle », valable pour le prologue
  seulement** : on admet des auteurs morts avant 1800 si le texte date de la période. On
  l'indique dans l'introduction du prologue et sur la fiche auteur.
- Chaque extrait d'époque affiche clairement sa **date d'écriture ou de publication**, et le
  chapeau replié précise que c'est un texte contemporain des faits, et non un souvenir.
- Pistes, à vérifier sur Wikisource : Louis-Sébastien Mercier, *Tableau de Paris* (1781-1788) ;
  Restif de la Bretonne, *La Vie de mon père* (1779), *Les Nuits de Paris* ; Beaumarchais,
  *Le Mariage de Figaro* (1784 ; le monologue de Figaro, acte V, scène 3) ; Laclos, *Les Liaisons
  dangereuses* (1782) ; Bernardin de Saint-Pierre ; Marmontel, *Mémoires* ; Chamfort, *Maximes
  et anecdotes* ; Mme de Genlis ; Rivarol ; cahiers de doléances de 1789 (à écarter s'ils ne
  sont pas l'œuvre d'un écrivain).
- Même format : texte complet de 400 à 900 mots (le théâtre peut faire un peu moins si la scène
  est complète), passage clé de 150 à 350 mots, appareil replié, vérification mot pour mot.

## Révision du 2026-10-06 : les sensibilités politiques avant 1789

L'utilisateur demande des textes qui montrent **les différentes sensibilités politiques
qui existaient avant la Révolution**.

- **Nouvelle partie** du prologue, « Les sensibilités politiques avant 1789 », de 6 à 8
  extraits, placée entre « Les Lumières et l'esprit public » et « La cour et la crise »,
  ou bien juste avant la crise si l'ordre de lecture s'en trouve plus clair. Les 14 extraits
  existants sont conservés.
- **Les textes fondateurs antérieurs à 1770 sont admis** (Montesquieu 1748, Rousseau 1762,
  Voltaire), puisque ce sont eux que lisent les hommes de 1789. Leur date est bien visible,
  et le chapeau explique pourquoi ils figurent ici malgré leur ancienneté.
- **Sensibilités à couvrir**, au moins 5, chacune nommée dans le titre ou le chapeau :
  1. la monarchie absolue de droit divin et l'alliance du trône et de l'autel (apologistes,
     anti-philosophes : Jacob-Nicolas Moreau, Linguet, Fréron, Barruel, *Les Helviennes*,
     1781, etc.) ;
  2. la monarchie tempérée et les corps intermédiaires : Montesquieu, et l'opposition
     parlementaire (Malesherbes, *Remontrances de la Cour des aides*, 1775) ;
  3. le réformisme éclairé et les physiocrates : Turgot, Necker (*Compte rendu au roi*, 1781),
     le despotisme éclairé ;
  4. la souveraineté du peuple et l'égalité : Rousseau, *Du contrat social* ; Mably,
     *Des droits et des devoirs du citoyen* ;
  5. la critique radicale et anticléricale : Voltaire, Raynal et Diderot (*Histoire des deux
     Indes*), Marat (*Les Chaînes de l'esclavage*, 1774) ;
  6. 1788, l'heure des choix : Sieyès, *Essai sur les privilèges* ; d'Antraigues, *Mémoire
     sur les états généraux* ; ou un texte défendant les ordres privilégiés (le *Mémoire des
     princes*, décembre 1788).
- Le regard critique de chaque extrait situe le texte : qui le lisait, quelle influence
  il a eue, et qui il ne représente pas.
- Même format et même rigueur : texte complet de 400 à 900 mots, passage clé de 150 à 350 mots,
  appareil replié, vérification mot pour mot. Durée de lecture et sommaire mis à jour.
