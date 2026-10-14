# Bilan de production — diaporama 06 « Le Second Empire »

Production du 2026-10-14 (nuit et matinée), ≈ 11 h d'horloge dont ≈ 4 h 30 de chaîne (A 1 h 20, V 11 min,
B 50 min, caméra 10 min, C 55 min) et le reste en calcul Colab. Session principale
`53d07ec2-b467-48ef-9f5e-5b678fbdf900`. Chaîne : outillage (pistes du bilan 05) en parallèle de A ;
V et B en parallèle ; caméra par 8 + 1 sous-agents Sonnet ; C ; puis fonds prolongés (agent dédié),
clips « mouvement » et ambiances sonores sur Colab. Première période à viser une heure (spec 12,
« Durée visée », « Ce qui manquait au récit »). Journal brut : `diaporama-06-second-empire.jsonl`.

## Résultat

153 diapositives en 10 actes, **59,7 min** (voix 52,2 min) ; 257 images (153 principales, 84 plans,
19 de galerie, 1 d'épisode) ; 6 lectures (toutes en voix de femme, décision confirmée par l'utilisateur
le 2026-10-14), 6 épisodes dont « L'empire en 1870 », 8 intermèdes (1 chanté) ; 141 images entières,
130 fonds prolongés (14 en flou fort), **12 clips « mouvement » avec leur ambiance** (40 Mo), 15 entrées
en scène, 3 avant/après, 2 mosaïques. Familles : campagnes 12, pourquoi matériel 12, femmes 8 et vie
ordinaire 9, Europe 5, colonies 11 + carte. `verifier.py second-empire` et `--tous` : 0 erreur ;
`npm run build` passe. Gemini : ≈ 1,9 $ (voix 1,55 ; zone utile 0,26 ; visibilité 0,06). Caméra 0 $.
Colab : ≈ 27 unités (531,8 → 504,2), dont ≈ 10 perdues (voir plus bas).
**Colorisation** (devenue règle le 2026-10-14, faite après coup) : 61 images (37 diapositives, 24 plans, 24 Mo), 0,8 unité Colab ; script `scripts/colab/couleur.py`.
Non commité : en attente du visionnage.

## Tokens (`tokens.py`)

| Fil | Requêtes | Cache écrit | Cache lu |
|---|---|---|---|
| A — texte, images | 97 | 1,33 M | 35,0 M |
| V — faits | 28 | 0,23 M | 4,8 M |
| B — utile, musique, voix | 95 | 0,68 M | 19,2 M |
| Caméra (8 lots + second tour, Sonnet) | 114 | 0,89 M | 6,8 M |
| C — caméra, registres, vérif | 85 | 0,47 M | 18,4 M |
| Fonds prolongés | 74 | 2,51 M | 10,4 M |
| Outillage | 34 | 0,20 M | 4,8 M |
| Orchestration et divers | 93 | 0,57 M | 18,1 M |
| **Total** | **620** | **6,9 M** | **118 M** |

Plus que la période 05 (4,0 M écrits, 80 M lus) pour un tiers de diapositives en plus et la couche
Colab complète ; l'agent des fonds pèse lourd (planches d'images regardées).

## Ce qui a bien marché

- **Caméra** : avec la vue réelle dans la tâche et la réponse « image entière », 104 vues bonnes sur
  112 au premier tour, 103 posées après un second tour de 10 vues, plus de cadres d'évitement.
- **Durée** : 59,7 min du premier coup avec 153 diapositives.
- **Chaîne parallèle** : V et B ensemble, caméra pendant le calcul des clips, fonds pendant C.

## Problèmes relevés

- **Session Colab des clips perdue** (« not found ») vers le onzième clip, pendant que l'agent des fonds
  ouvrait ses sessions L4 : `generation.py` ne rapatriait qu'à la fin, tout a été recalculé (≈ 2 h 15 et
  ≈ 10 unités de plus). Corrigé : rapatriement de chaque clip fini, arrêt du suivi sur session perdue.
  Règle d'orchestration : **une seule session Colab à la fois**.
- **Vérification des faits partielle** : V a relu toutes les narrations et les nombres affichés, pas les
  185 affirmations une à une (restent sans source lue : réseau ferré « cinq fois plus », 3 000 soldats
  au Creusot, ordre des villes du choléra de 1865).
- Deux fausses identités de portrait (Sainte-Claire Deville, André Léo), trouvées par C.
- La carte « L'empire en 1870 » ne montrait jamais l'Asie (chronologie trop tôt) : rien ne l'a détecté
  avant les captures.
- « Partant pour la Syrie » introuvable en libre (intermède retiré) ; un seul chant.
- Lecture Pinard refusée par le filtre de la synthèse, faite par morceaux.

## À juger au visionnage

Clips 19 (soldats du premier plan) et 115 (chevaux de Manet) ; les 12 ambiances (publiées sans page
d'écoute, à la demande de l'utilisateur) ; placements musicaux (`.cache/diaporamas/second-empire/ecoute-musique.html`) ;
médaille couchée en 146 ; carte de l'empire illisible sur téléphone ; dessin pâle de 151b ; Rochefort
collégien en 136b ; 14 fonds en flou fort ; raccord de la lecture Pinard.

## Pistes pour la période 07 (L'année terrible)

1. Une seule session Colab à la fois ; lancer les fonds après les clips, ou dans la même session.
2. `verifier.py` : élément de carte dont le `quand` tombe après le visuel suivant ; `commun.nombre_dit`
   « et demi » ; `images.py` : rotation.
3. Agent A : `portraits.py --lot --essai` dès le relevé, seuil de 500 px pour les portraits en ovale,
   lire la description Commons de chaque portrait.
4. `fond.py` : toile grise d'office sur les décors sombres et photographiques ; nouvel essai sur 503.
5. V : donner une durée plus longue ou deux agents pour relire toutes les affirmations de mémoire.
