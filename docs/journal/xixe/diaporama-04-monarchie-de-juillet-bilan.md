# Bilan de production — diaporama 04 « La monarchie de Juillet »

Production du 2026-10-11, ≈ 5 h 30 (dont ≈ 1 h 35 pour l'agent A et ≈ 1 h 05 pour l'agent B).
Session principale `0f796479-8e93-4451-a2a7-b6a6fae88697`. Chaîne : A (texte, images, plans de la
spec 14, enrichissements prévus), V (vérification des faits avant les voix, en parallèle du début
de B), B (zone utile, musique, voix, préparation de la caméra), caméra par sous-agents Sonnet
(`banc_claude.py` : 13 lots, puis second tour sur 73 retours), C (caméras restantes, images
entières, registres, surimpressions, vérification, build, captures). En parallèle de A : plan de
Paris de 1838. Journal brut : `diaporama-04-monarchie-de-juillet.jsonl`.

## Résultat

116 diapositives, 8 actes (3 repères chacun), 46,0 min ; 219 images (116 principales, 75 plans,
23 de galerie, 5 panneaux d'épisode) ; 6 lectures (non illustrées), 4 épisodes (cartes de
l'Algérie, de l'étoile de Legrand, de la crise), 9 fonds, 7 intermèdes (1 chant, 3 musicaux,
3 galeries nouvelles) ; 48 lieux (plan de Tardieu, 1838), 5 citations, 16 chiffres, 10 objets,
4 manuscrits, 40 personnes montrées (32 entrées nouvelles au registre), 4 avant/après,
2 mosaïques, 115 images entières sur fond noir, générique de 12 images.
`verifier.py monarchie-de-juillet` et `--tous` : 0 erreur ; `npm run build` passe.
Gemini : ≈ 1,7 $ (voix 1,37 ; zone utile 0,22 ; visibilité 0,06 ; paroles 0,01). **Caméra : 0 $.**
Non commité : en attente du visionnage.

## Tokens (`tokens.py`)

| Fil | Requêtes | Cache écrit | Cache lu |
|---|---|---|---|
| A — texte, images, plans (95 min) | 94 | 2,20 M | 31,1 M |
| V — faits (8 min) | 21 | 0,19 M | 3,2 M |
| B — utile, musique, voix (65 min) | 80 | 0,86 M | 13,8 M |
| Caméra, second tour (6 agents Sonnet) | 83 | 0,62 M | 5,0 M |
| C — caméra, registres, vérif (32 min) | 87 | 0,34 M | 18,3 M |
| Plan de Paris de 1838 (6 min) | 21 | 0,09 M | 1,7 M |
| Orchestration | 34 | 0,18 M | 5,2 M |
| **Total (hors premier tour de caméra)** | **420** | **4,5 M** | **78 M** |

Premier tour de caméra (13 agents Sonnet, hors de ce tableau) : 1,15 M tokens, 4,5 min.
Période 03 à 114 images : 188 requêtes, 1,9 M écrits, 34 M lus ; il avait fallu ensuite une
production séparée pour passer à 220 images. Ici les 219 images sont écrites d'emblée : A coûte
près de trois fois plus (planches regardées), le reste est comparable.

## Ce qui a bien marché

- **Vérification des faits avant les voix**, en parallèle du début de B (fichier-signal
  `faits-verifies.ok`, écritures par `commun.ecrire`) : 6 narrations et 4 notices corrigées sans
  refaire une seule voix.
- **Caméra par Sonnet** : 176 vues sur 185 posées en deux tours (159 telles quelles, 17 réparées),
  243 étapes, audit sans défaut, 0 $ et ≈ 12 min d'horloge.
- **Plan de Paris de 1838** fait pendant l'étape A (12 m d'écart moyen), sert aussi la période 05.
- Aucune panne de crédits ; aucun changement des périodes 01 à 03.

## Problèmes relevés

- **A a encore écrit des chiffres de mémoire** malgré la consigne (prix du blé, kilomètres de
  rails, effectifs) : rattrapé par V, mais la relecture d'ensemble de V reste elle-même « de
  mémoire » hors points listés.
- **Caméra** : les tâches ne décrivent pas toute la vue réelle (resserrement de 12 % pendant la
  tenue, haut de l'image caché par le cartouche) ; faux visages imposés au modèle (tampons de
  bibliothèque, rectangle géant) ; têtes de portrait plus hautes que la vue : cause des 9 replis
  et d'une bonne part des 73 retours. Avant/après et mosaïques restent posés à la main par C.
- **Tête coupée par un `recadrage`** de A (64, Méhémet Ali) passée par tous les contrôles ; six
  autres têtes collées au bord.
- **Musique** : *Le Chant des ouvriers* introuvable en libre (remplacé par *Les Bœufs*, narration
  100 retouchée avant la voix ; le plan 100b montre encore la couverture du *Chant des ouvriers*) ;
  *Les Huguenots* seulement en version chantée de 1909 ; un seul intermède chanté ; placements à
  l'aveugle (page d'écoute `.cache/diaporamas/monarchie-de-juillet/ecoute-musique.html`).
- **Gemini TTS a refusé six fois la lecture de Tocqueville** (« resembles existing copyrighted
  works ») : synthèse phrase par phrase par un script maison de B.
- `verifier.py` ignorait les prudences « jusqu'à » et « au moins » (ajoutées par C) ;
  `objets.py --registre` a vidé `auteur_photo` d'une entrée existante (rétabli à la main, cause
  non cherchée).
- Cartes d'épisode : libellés qui se chevauchent ou trop petits sur une France entière.

## Pistes pour la période 05 (1848 et la IIe République)

1. Consigne de A : tout chiffre avec l'adresse de la page lue, sinon pas de chiffre ; `recadrage`
   avec ≈ 3 % d'air au-dessus des têtes ; `verifier.py` : visage au bord supérieur d'une image
   recadrée.
2. `banc_claude.py` : vue réelle complète dans la tâche, faux visages écartés, pas de tâche pour
   un portrait qui passera en image entière (lancer `--entiers` avant `preparer`), avant/après et
   mosaïques dans le banc.
3. `voix.py` : repli phrase par phrase quand le filtre refuse une lecture.
4. `objets.py --registre` : ne pas réécrire les entrées existantes.
5. Cartes : taille minimale et contrôle de chevauchement des libellés.
6. Intermède chanté : pouvoir porter sa propre image ; chercher les chants de 1848 tôt
   (*Le Chant des Girondins*, *La Casquette du père Bugeaud* gardés en réserve).
7. Garder l'agent V et le lancer dès la fin de A ; lui faire lire les sources de tous les
   chiffres, pas seulement les doutes déclarés.
