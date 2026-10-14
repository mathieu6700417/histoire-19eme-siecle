# Bilan de production — diaporama 05 « 1848 et la IIe République »

Production du 2026-10-12, ≈ 2 h 45 pour le diaporama (dont ≈ 1 h 05 pour l'agent A et ≈ 55 min
pour l'agent B), puis ≈ 3 h de machine Colab pour les images mises en mouvement.
Session principale `27b3c99a-07a9-4b7a-9e12-ad49e3361a4d`. Chaîne : A (texte, images, plans de la
spec 14, enrichissements prévus, candidats au mouvement), V (vérification des faits avant les voix,
en parallèle du début de B), B (zone utile, musique, voix, préparation de la caméra), caméra par
sous-agents Sonnet (`banc_claude.py` : 12 lots, puis second tour sur 64 retours), C (caméras
restantes, images entières, registres, surimpressions, vérification, build, captures), et pour la
première fois la couche générée (spec 16) par `generation.py lancer`, en parallèle de C.
Journal brut : `diaporama-05-deuxieme-republique.jsonl`.

## Résultat

115 diapositives, 8 actes (3 repères chacun), 47,0 min (voix 41,0 min) ; 207 images (115
principales, 68 plans, 21 de galerie, 3 panneaux d'épisode) ; 6 lectures (non illustrées),
4 épisodes (« Neuf millions d'électeurs », « Quatre jours de juin », « Le 10 décembre 1848 »,
« La province se soulève » avec carte), 10 fonds, 6 intermèdes (1 chant, 2 musicaux, 3 galeries
nouvelles) ; 41 lieux, 15 citations, 12 chiffres, 11 objets, 3 manuscrits, 23 personnes montrées
(10 entrées nouvelles au registre), 3 avant/après, 2 mosaïques, 115 images entières sur fond noir,
générique de 12 images ; **10 clips « mouvement »** (diapositives 1, 13, 25, 37, 42, 55, 67, 71, 85, 110 ; 38 Mo).
`verifier.py deuxieme-republique` et `--tous` : 0 erreur ; `npm run build` passe.
Gemini : ≈ 1,5 $ (voix 1,23 ; zone utile 0,23 ; visibilité 0,04 ; paroles 0,01). Caméra : 0 $.
Colab : ≈ 14,5 unités (A100, ≈ 12 min par clip de 190 à 240 images).
Non commité : en attente du visionnage.

## Tokens (`tokens.py`)

| Fil | Requêtes | Cache écrit | Cache lu |
|---|---|---|---|
| A — texte, images, plans (63 min) | 83 | 0,99 M | 26,4 M |
| V — faits (8 min) | 23 | 0,18 M | 2,9 M |
| B — utile, musique, voix (55 min) | 94 | 0,64 M | 18,3 M |
| Caméra, premier tour (12 agents Sonnet, 5 min) | 133 | 1,15 M | 7,4 M |
| Caméra, second tour (4 agents Sonnet, 10 min) | 56 | 0,41 M | 3,8 M |
| C — caméra, registres, vérif (23 min) | 72 | 0,26 M | 12,3 M |
| Orchestration (dont lot de mouvement) | 61 | 0,37 M | 9,0 M |
| **Total** | **522** | **4,0 M** | **80 M** |

Comparable à la période 04 (420 requêtes hors premier tour de caméra, 4,5 M écrits, 78 M lus),
en deux fois moins de temps d'horloge : A a écrit plus vite (modèle et scripts de la 04 repris),
aucune panne.

## Ce qui a bien marché

- **Chiffres sourcés à l'écriture** (`sources-chiffres.md`, 48 lignes avec adresse, puis la liste
  des affirmations « de mémoire ») : V a pu relire les sources au lieu de tout rechercher ;
  15 narrations et 1 épisode corrigés avant toute voix, une seule voix refaite ensuite (33).
- **Caméra par Sonnet** : 172 vues sur 178 en deux tours, 246 étapes, 0 $.
- **`generation.py lancer`** a tourné de bout en bout par la CLI (session créée, kit envoyé, clips
  rapatriés, session arrêtée) ; les lectures du journal de bord échouent parfois (ReadTimeout) sans
  conséquence.
- Tocqueville est passé au filtre de la synthèse vocale ; aucun audio périmé dans les périodes 01 à 04.

## Problèmes relevés

- **Second tour de caméra : cadres d'évitement.** Pour satisfaire le contrôle des visages, les
  sous-agents ont rendu des cadres pauvres (détail de col en 049b, bandes sans visage, marges) :
  18 vues relues par C, la plupart réglées par l'image entière. Les tâches ne disent toujours pas la
  vue réelle (resserrement de 12 %, haut repoussé de 0,2 × la hauteur de vue) : les agents l'ont
  redécouverte à la main. Une tâche est encore créée pour les images qui passeront en image entière.
- **Images introuvables** : *La République* de Daumier (fichier libre de 900 px), l'insurrection de
  province (médaille de propagande à la place), le pendule de Foucault (portrait de 1878 et planche
  de 1895). Non traités : Rude, Nadar, Berlioz.
- **Musique** : *Le Chant des Girondins* introuvable en libre (repli sur *La Marseillaise* de Thill,
  narration 33 retouchée deux fois, plan 33b remplacé) ; un seul intermède chanté ; Internet Archive
  instable (`musique.py` sans nouvel essai sur 5xx) ; placements à l'aveugle (page d'écoute
  `.cache/diaporamas/deuxieme-republique/ecoute-musique.html`).
- **Les six lectures ont la même voix** (réglage unique de `voix.py`, voix de femme) : Tocqueville,
  Lamartine, Hugo et Louis-Napoléon sont dits par la voix de Daniel Stern et de George Sand.
- **Outils** : `commun.phrases` ne coupe pas après « . » » (phrase de 40 mots vue trop tard, en C) ;
  `objets.py --registre` vide encore `auteur_photo` d'une entrée existante ; `utile.py` prend un
  ciel de calotype ou du papier nu pour une marge ; `paroles.py retoucher()` borne mal la fin d'un
  mot ; `captures.py` reste sur le carton quand la diapositive ouvre un acte ; `camera.py --audit`
  signale des images entières.
- **Mouvement** : 4 clips ratés sur 11 au premier jet (drapeau qui grossit en 13 malgré la consigne,
  personnages nouveaux en 67, fumée apparue dans le ciel en 85, personnage qui se déforme en 97) :
  le jugement s'est fait sur trois images par clip (début, milieu, fin), pas en lecture.
  13, 67 et 85 refaits avec une consigne adoucie (bons au second jet), 97 abandonné. Quatre clips dépassent 4,5 Mo (37, 55, 67, 85 : 4,6 à 5,7 Mo). Les clips n'ont pas été regardés en lecture dans le lecteur.
- A a livré 208 images pour un objectif de 220, et 42 narrations à quatre phrases.

## Pistes pour la période 06 (Second Empire)

1. `banc_claude.py` : donner la vue réelle dans la tâche, pas de tâche pour une image entière,
   proposer d'office l'image entière pour un groupe de visages serrés ; avant/après dans le banc.
2. `commun.phrases` : couper après « . » » ; sinon le dire à l'agent A.
3. `voix.py` : voix d'homme et voix de femme pour les lectures, choisies par lecture.
4. `objets.py --registre` : ne pas réécrire les entrées existantes ; `musique.py` : nouvel essai sur 5xx.
5. Agent A : pas de lieu parisien hors du plan, dix médailles au plus, texte surligné des manuscrits,
   viser 220 images ; chercher les chants en libre **avant** de les nommer dans une narration.
6. Mouvement : consignes sans « flags », sans « procession climbs » ni fumée lointaine ; « every
   figure stays in its place » sur les foules ; éviter les gravures sur bois à personnages proches ;
   prévoir 12 candidats pour une dizaine de clips gardés.
7. Lancer le lot de mouvement dès la fin de B (zone utile et voix suffisent), en parallèle de la caméra.
