# Bilan de production — diaporama 03 « La Restauration »

Production du 2026-10-10, de 13:51 à ≈ 17:50 UTC (≈ 4 h, dont ≈ 30 min d'attente des recherches
Commons). Session principale `b5236241-626a-493c-895a-a74ec7891d5c`, trois sous-agents Opus
successifs : A (texte, images, enrichissements prévus), B (voix, zone utile, caméra, musique),
C (surimpressions, exactitude, vérification, build). Journal brut : `diaporama-03-restauration.jsonl`.

## Résultat

114 diapositives, 7 actes, 37,1 min de voix ; 6 lectures, 4 épisodes (2 cartes animées), 7 fonds
et 4 intermèdes ; 49 lieux, 6 citations, 80 portraits affichés (35 nouveaux au registre),
10 objets, 3 manuscrits, 11 chiffres, 3 avant/après, 2 mosaïques, générique de 11 images.
`verifier.py restauration --etape C` et `--tous` : 0 erreur (15 avertissements) ; `npm run build`
passe. Gemini : ≈ 2,2 $ (voix 1,2 ; caméra 0,8 ; zone utile 0,1 ; visibilité 0,07), sans panne
de crédits. Non commité à cette date : en attente du visionnage.

## Tokens (`tokens.py`)

| Fil | Requêtes | Cache écrit | Cache lu |
|---|---|---|---|
| A — texte et images (65 min) | 47 | 1,30 M | 11,2 M |
| B — voix, caméra, musique (31 min) | 71 | 0,24 M | 11,9 M |
| C — surimpressions, vérif (26 min) | 55 | 0,24 M | 9,6 M |
| Orchestration | 15 | 0,09 M | 1,2 M |
| **Total** | **188** | **1,9 M** | **33,9 M** |

Période 02 : 326 requêtes, 2,0 M écrits, 54 M lus. Gain ≈ 40 % sur les tours et les lectures :
vérification par étape, outils par lots, registre musical, YuNet, `captures.py`, scripts en
parallèle. Les phases les plus chères restent **portraits (C, 9,2 M)**, **caméra (B, 7,7 M)**
et **plan + images (A, 11 M ; 1,2 M écrits, surtout des planches regardées)**.

## Problèmes relevés

- **Caméra plus statique** que la période 02 (82 diapositives à une étape contre 64) : Gemini
  propose des cadres plus hauts que la bande de vue sur près d'une image sur deux, puis repli.
- **Têtes au bord supérieur** de la zone utile cachées par le bandeau du haut (17, 89).
- **Lexique de prononciation global** : une entrée ajoutée pour 03 (« Henri IV ») périmait un
  audio de 01 ; `--etape B` ne le voit pas, seul `--tous` le voit.
- **Chiffres et lieux de conservation écrits de mémoire** par A, vérifiés seulement par C
  (une image fausse : Lazare Carnot pour Sadi Carnot).
- **Guillemets des citations** absents des narrations de A : 6 voix refaites par C.
- Recherche Commons à plusieurs mots peu productive (≈ 330 requêtes, 30 min) ; `images.py --n`
  n'accepte qu'un numéro ; pas de `--proposer-recadrage` (script maison de A, 42 justes sur 57).
- Chants : *La Parisienne* introuvable en libre ; transcription d'un chant bloquée par Gemini ;
  un seul intermède chanté.
- Pas de fond « Paris » pour les cartes d'épisode ; plan de Verniquet (1790) réemployé pour 1830.

## Pistes pour la période 04 (monarchie de Juillet)

1. Consigne de A : **sourcer chiffres et lieux de conservation à l'écriture** (notice Commons lue
   par script), guillemets « » autour de toute citation, vérifier l'identité des portraits.
2. `verifier.py --etape B` : contrôler aussi la péremption des audios des **autres** périodes
   après un changement du lexique.
3. Caméra : contraindre le cadre demandé à la hauteur de la bande de vue dans la consigne Gemini.
4. Zone utile ou bandeau : marge haute quand un visage touche le bord supérieur.
5. `images.py --n 3,7,12`, `--proposer-recadrage`.
6. Un plan de Paris des années 1820-1840 calé une fois (servira aux périodes 03 à 05) et un fond
   « Paris » pour les cartes d'épisode (journées de 1830, 1832, 1848).
