# Bilan de production — diaporama 07 « L'année terrible »

Production du 2026-10-18, ≈ 11 h d'horloge (8 h 57 → 19 h 40, heure de Paris), session principale
`f0734358-ec34-4900-be3e-46f68e727914`. Chaîne : A (texte, images) en parallèle de l'outillage (pistes du
bilan 06) ; V et B en parallèle (B attend le marqueur `faits-verifies.ok` pour les voix) ; clips sur Colab
dès la voix finie, en parallèle de la caméra (9 + 1 sous-agents Sonnet) et de C ; puis un seul agent pour
la couche restante (fonds, colorisation, dessins, netteté) dans une seule session L4. Journal brut :
`diaporama-07-annee-terrible.jsonl`.

## Résultat

138 diapositives en 10 actes, **55,6 min** (voix ≈ 48 min) ; 209 images (138 principales, 55 plans,
15 de galerie, 1 d'épisode), 148 œuvres ; 6 lectures (toutes en voix de femme), 6 épisodes de 49 à 59 s
(dont « L'empire et l'Algérie en 1871 »), 5 intermèdes instrumentaux, **aucun chant** (*La Canaille*,
*Le Temps des cerises* : pas d'enregistrement ancien libre) ; 3 avant/après (43, 121, 122 ; la colonne
Vendôme, 105, est passée en diapositive à plan), 2 mosaïques (118, 135), 78 images entières.
Familles : arts et techniques 32, colonies 7 + carte, campagnes 9, pourquoi matériel 15, femmes 15 et vie
ordinaire 16, Europe 8, bilan 2. Plan de Paris de 1870 (Vuillemin, `paris-1870`) et fond de carte
`algerie` ajoutés. Portraits : 49 entrées au registre (12 sans portrait), `hugo-1870` et `thiers-1870`
propres à la période.
Couche Colab : **11 clips** + 11 ambiances (47,9 Mo ; 14 écarté : texte lisible), 81 fonds prolongés
(13 en flou fort), 62 images colorisées (25 Mo), 21 dessins traversants, netteté (90 variantes tirées des
originaux, 26 par Real-ESRGAN, 47 colorisées ; ≈ 102 Mo). Médias de la période : 295 Mo.
`verifier.py annee-terrible` et `--tous` : 0 erreur ; `npm run build` passe. Non commité : en attente du
visionnage.

Coûts : Gemini ≈ 1,85 $ (voix 1,58 ; zone utile 0,20 ; visibilité 0,06). Caméra 0 $. Colab ≈ 19,6 unités
(496,65 → 477,00), dont ≈ 10 pour la première session des clips, perdue après le 8e clip.

## Tokens (`tokens.py`)

| Fil | Requêtes | Cache écrit | Cache lu |
|---|---|---|---|
| A — texte, images | 189 | 2,27 M | 92,2 M |
| V — faits | 49 | 0,28 M | 8,9 M |
| B — utile, musique, voix | 100 | 0,59 M | 21,4 M |
| Caméra (9 lots + second tour, Sonnet) | 112 | 1,11 M | 6,9 M |
| C — caméra, registres, durée, vérif | 191 | 0,41 M | 47,6 M |
| Clips et ambiances | 65 | 0,76 M | 5,3 M |
| Fonds, couleur, dessins, netteté | 138 | 2,51 M | 32,7 M |
| Outillage | 60 | 0,16 M | 5,9 M |
| Orchestration | 97 | 0,18 M | 15,0 M |
| **Total** | **1 001** | **8,3 M** | **236 M** |

L'agent A pèse le double de la 06 en cache lu (lectures larges de la spec 12 et du README, scripts de la
06 relus en entier, fichiers de recherche écrits par `cat >`).

## Ce qui a bien marché

- **Vérification des faits complète** (piste 5 du bilan 06) : V a relu les 138 narrations une à une en
  13 min ; 17 narrations et 12 notices corrigées, chiffres disputés attribués à leurs sources.
- **Une seule session Colab pour toute la couche restante** (fonds, couleur, dessins, netteté) : 3,3 unités.
- Caméra : 103 vues posées sur 114 en deux tours, 16 réponses fautives reprises par un seul agent.
- Outillage du bilan 06 livré en 8 min (rotation, « et demi », éléments d'épisode « jamais montrés »,
  toile grise d'office, garde « une seule session »).

## Problèmes relevés

- **Session A100 des clips perdue** après le 8e clip, sans autre session ouverte : `generation.py` ne l'a
  pas vu pendant 30 min (sortie en tampon, abandon seulement sur « not found » ou 10 échecs). Corrigé :
  `colab sessions` consulté dès qu'une lecture du journal distant échoue.
- **Attente de l'agent des fonds** : sa boucle n'a pas vu la voie libre (≈ 50 min perdues) ; relancé par
  message. Piste : attendre une notification de l'orchestrateur plutôt qu'une boucle de sondage.
- Deux calculs FLUX lancés en même temps sur la même L4 : mémoire insuffisante, passe 2 des fonds refaite.
- Durée à 53 min après B : C a allongé les épisodes (28-38 s → 49-59 s) et la lecture d'André Léo.
- Carte d'Algérie de l'agent A sur le fond Europe agrandi : refaite par C (nouveau fond `algerie`).
- Boucles d'attente `until ! pgrep -f "images.py …"` de l'agent A jamais terminées (le motif trouve la
  boucle elle-même) : arrêtées à la main.
- `objets.py --planche` plante sur « œ ».

## À juger au visionnage

Les 11 ambiances (page d'écoute : `python3 .cache/diaporamas/essais-colab/servir.py`, puis
`http://127.0.0.1:8017/sons/ecoute-annee-terrible.html`) ; placements musicaux
(`.cache/diaporamas/annee-terrible/ecoute-musique.html`, extraits choisis à l'aveugle) ; clips 126
(Père-Lachaise : poses qui changent), 71 (visages adoucis) et 1 (foule) ; raccords des avant/après 43, 121,
122 ; diapositive 1 (trois petits visages coupés par la caméra) ; 13 fonds en flou fort ; photographies
colorisées 84 et 105 (aspect carte postale) ; agrandissements Real-ESRGAN un peu « peints » ; portraits
tardifs (Monet 1899, Pissarro vers 1900, Vaillant 1912) ; lecture d'André Léo à 45,6 s sans portrait.

## Pistes pour la période 08 (IIIe République jusqu'à 1900)

1. Agent A : lire seulement les sections utiles de la spec 12 et du README (index par `grep -n "^#"`),
   ne pas relire en entier les scripts de la période précédente.
2. Durée : viser 145 diapositives ou des épisodes de 45 s dès l'écriture (138 diapositives → 53 min).
3. Orchestration Colab : un seul agent pour toute la couche (clips compris), sessions enchaînées ; pas de
   boucle d'attente entre agents.
4. Fond de carte adapté dès l'écriture pour toute carte d'outre-mer (Tunisie, Tonkin, Madagascar).
5. Corriger `objets.py --planche` (police) ; poids des clips (6 au-dessus de 4,5 Mo).
