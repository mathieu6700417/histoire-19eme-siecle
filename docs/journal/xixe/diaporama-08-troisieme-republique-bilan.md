# Bilan de production — diaporama 08 « La IIIe République jusqu'à 1900 »

Production du 2026-10-20, ≈ 7 h 30 d'horloge (2 h 03 → 9 h 35, heure de Paris), session principale
`dbc63182-7196-42c2-afb5-88fe8c5eacec`. Chaîne : A (texte, images) ∥ outillage (pistes du bilan 07) ;
V puis B (B a fait zone utile et musique en attendant `faits-verifies.ok`) ; caméra par 7 sous-agents
Sonnet (+ 1 second tour sur 8 réponses) ∥ clips sur Colab ; C ; puis la couche restante (fonds, couleur,
dessins, netteté) dans une seule session L4. Journal brut : `diaporama-08-troisieme-republique.jsonl`.

## Résultat

149 diapositives en 10 actes, **61,1 min** (voix ≈ 54 min) ; 210 images (149 principales, 34 plans,
16 de galerie, 9 vignettes de mosaïque, 2 « après ») ; 6 lectures (Louise Michel, Hubertine Auclert,
Ferry, Liard-Courtois, Maupassant, Zola ; toutes en voix de femme), 6 épisodes de 49 à 64 s (« L'école de
la République », « Le phylloxéra », « De Tunis à Hanoï », « La France des grèves », « L'empire en 1900 »,
« Douze ans d'Affaire »), 7 intermèdes dont un chanté (Habanera, Marthe Chenal 1915) ; 3 avant/après (49,
130, 143), 2 mosaïques (78, 94). Fin : 2 diapositives de bilan de la période et 2 de bilan du siècle.
Familles : campagnes 19, pourquoi matériel 19, femmes 21, vie ordinaire 23, Europe 12, arts 20,
techniques 20, colonies 22 et 4 cartes d'outre-mer. Fonds de carte `tunisie`, `indochine`, `madagascar`
ajoutés à `carte.py` ; plan `paris-1870` repris. Registres : 64 portraits (2 notes sans portrait),
12 objets, 3 manuscrits ; `degas-1876` et `mac-mahon-1873` propres à la période.
Couche Colab : **11 clips** (4 refaits une fois : 75, 99, 110, 147) + 11 ambiances, 106 fonds prolongés
(8 en flou fort), 43 images colorisées, 29 dessins traversants (145 écarté), netteté (81 variantes,
18 par Real-ESRGAN après 4 retraits). Médias de la période : 248 Mo.
`verifier.py troisieme-republique` et `--tous` : 0 erreur ; `npm run build` passe. Non commité : en
attente du visionnage.

Coûts : Gemini ≈ 1,96 $ (voix 1,64 ; zone utile 0,24 ; visibilité 0,08). Caméra 0 $. Colab ≈ 19,7 unités
(477,00 → 457,31), dont ≈ 16 pour les clips (≈ 2 h 50 d'A100, premier passage et 4 reprises).

## Tokens (`tokens.py`)

| Fil | Requêtes | Cache écrit | Cache lu |
|---|---|---|---|
| A — texte, images | 150 | 0,89 M | 60,6 M |
| Outillage | 37 | 0,09 M | 2,4 M |
| V — faits | 24 | 0,15 M | 3,1 M |
| B — utile, musique, voix | 104 | 0,29 M | 21,7 M |
| Caméra (7 lots + second tour, Sonnet) | 104 | 0,81 M | 6,7 M |
| C — caméra, registres, vérif | 181 | 0,40 M | 45,4 M |
| Clips et ambiances (+ début de la suite) | 163 | 3,68 M | 31,9 M |
| Couleur, fonds, dessins, netteté | 99 | 1,72 M | 13,6 M |
| Orchestration | 95 | 0,34 M | 13,9 M |
| **Total** | **957** | **8,4 M** | **199 M** |

## Ce qui a bien marché

- **Durée tenue dès l'écriture** (piste 2 du bilan 07) : 149 diapositives et épisodes de 45 s visés,
  61,1 min sans allongement par C ; l'estimation de `verifier.py --etape A` (58,6 min) était juste à 2,5 min près.
- **Fonds de carte d'outre-mer dès l'écriture** (piste 4) : aucune carte refaite par C.
- **V en 7 min**, B sans attente : zone utile et musique faites avant le marqueur.
- **Session A100 tenue** pendant 2 h 50 (le garde de `generation.py` n'a pas eu à jouer).
- Cache lu en baisse : 199 M contre 236 M en 07 ; l'agent A passe de 92 à 61 M (piste 1).

## Problèmes relevés

- **Agent Colab interrompu deux fois** (contexte trop chargé après 3 h 40 et 370 k tokens de sous-agent :
  rendu exigé par le harnais) : la seconde partie a été confiée à un agent neuf, à partir de son rapport.
  Piste : un agent pour les clips et ambiances, un **autre** pour fonds, couleur, dessins, netteté.
- Caméra Sonnet lente au départ (3 réponses en 30 min, puis les lots finis en 2 à 6 min chacun) ;
  8 réponses fautives sur 79 au premier tour.
- Erreur de fait vue par C après V : la rue du Caire de 1889 placée aux Invalides (diapositive 96).
- `build.py` hérité de la 07 fusionnait des phrases (minuscule en tête) : fusion désactivée par A.
- Ambiances publiées sans page d'écoute jugée avant (comme en 06 et 07).

## À juger au visionnage

Les 11 clips (35 : la foule peinte lève les bras ; 75 : le fanion grandit ; 110 : petite fumée ajoutée) et
leurs ambiances (page : `python3 .cache/diaporamas/essais-colab/servir.py`, puis
`http://127.0.0.1:8017/sons/ecoute-troisieme-republique.html`) ; placements musicaux
(`.cache/diaporamas/troisieme-republique/ecoute-musique.html`) ; raccord approché du pont Alexandre-III (143) ;
caméras manuelles des clips 75 et 147 et des mosaïques 78 et 94 ; libellés serrés de la carte du Tonkin ;
couleurs 32b (Liberté en cuivre), 149 (tour en rouge de Venise), 132, 3, 93b ; fonds en flou fort et
jonction de 106-b ; dessins 129, 55, 73, 19 ; netteté un peu cireuse sur 64, 34b, 36, 136, 106b ;
portraits tardifs (Buisson 1914, Marguerite Durand 1910 ; Bienvenüe sans portrait).

## Pistes

1. Couche Colab en deux agents successifs (clips + ambiances ; le reste), chacun léger en contexte.
2. Agent C : ne pas relire le README par grandes tranches (1,1 M de poids traîné pour une seule lecture).
3. Un troisième manuscrit pour tenir le dosage (avertissement restant).
