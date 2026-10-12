# Spec 16 — Couche générée : images d'époque mises en mouvement (essai)

Décidé avec l'utilisateur le 2026-10-11, après la proposition d'une « couche générée » pour les
diaporamas (photos de reconstitution, mises en mouvement, colorisation), calculée sur son
abonnement **Google Colab Pro** avec des modèles à poids ouverts. **État : mouvement intégré au lecteur
(2026-10-12)** ; reconstitution et colorisation restent à décider.

## Décisions

| Sujet | Décision |
|---|---|
| Règle « documents d'époque » de la spec 12 | **Amendée** : une image générée est admise si elle est **dérivée d'un document d'époque déjà dans la période**, **signalée à l'écran** (cartouche) et plafonnée (ci-dessous). L'original reste visible ou accessible (livre d'images, crédits). |
| Usage essayé en premier | **Mouvement seulement** : le modèle reçoit l'image d'époque et une consigne de mouvement, rend un clip muet de 5 s qui remplace le mouvement de caméra sur la diapositive. Les deux autres usages (reconstitution photo d'après gravure, colorisation des vraies photographies) attendent le résultat de cet essai. |
| Plafond par période | **15 clips et 8 reconstitutions** au plus ; le document d'époque reste la règle. **Dose visée : une dizaine de clips par période** (décision du 2026-10-12, un par diapositive). |
| Veo (API Gemini) | **Non, pas pour l'instant** : modèles ouverts sur Colab seulement. |
| Modèle | **Wan 2.2 TI2V-5B** (Apache 2.0), image → vidéo 720p, 24 images/s, 121 images (5 s). Exclus : la famille Hunyuan (licence excluant l'Union européenne) et FLUX Kontext dev (non commercial). Plan B si trop lent : LTX-2.3 quantifié. |
| Carte Colab | L4 24 Go (déchargement CPU des composants) ou A100 (tout sur la carte). T4 refusé par le carnet. |
| Garde-fous | Jamais de visage régénéré d'une personne nommée ; rien de nouveau n'apparaît (consignes « nothing new appears, no text ») ; le clip illustre, il ne prouve rien que la narration ne dise. |

## Essai (2026-10-11)

- **Lot** : `src/data/diaporamas/generation/revolution.json`, 8 diapositives de la Révolution à
  scènes animables (Bastille 18, marche sur Versailles 28, fête de la Fédération 35, 10 août 53,
  Valmy 56, incendie de Toulon 85, fête de l'Être suprême 92, Vendémiaire 110), une consigne de
  mouvement en anglais par image (fumée, drapeaux, foule, lent travelling ; style de l'œuvre conservé),
  consigne négative commune, graine fixe.
- **Chaîne** : `generation.py preparer` (sources = image servie réduite à sa zone utile, JPEG, kit zip)
  → `generation.py lancer` : session Colab ouverte, suivie, rapatriée et arrêtée par la **CLI
  officielle `colab`** (script `scripts/colab/mouvement.py` ; essai rapide de la première image en
  832×480, puis les 8 en 1280×704, 40 pas) → `generation.py encoder` (aller-retour 10 s, H.264 sans
  son, ~2 Mo) → `planche-mouvement.html` (original, clip brut, clip aller-retour, narration audio)
  pour le jugement. Le carnet `mouvement.ipynb` reste la voie manuelle de secours.
- **Premier lot (2026-10-11)** : calculé dans l'interface Colab pilotée par Chrome, A100 40 Go, ≈ 5,3 min
  par clip, ≈ 4 unités ; la CLI a été rappelée par l'utilisateur en cours de route (« il y a une CLI »,
  déjà employée sur un autre projet) et devient la voie normale.
- **Coût attendu** : ≈ 45 min d'A100 par lot de 8, soit ≈ 4 unités ; 0 $ Gemini.
- **Journal** : `docs/journal/generation-mouvement.jsonl`.

## Visionnage et intégration (2026-10-12)

Verdict de l'utilisateur sur la planche des 8 clips : « ça rend bien, je garde ». Décisions prises
pour l'intégration (les points laissés ouverts le 2026-10-11 sont tranchés ici) :

| Sujet | Décision |
|---|---|
| Données | `image.video` `{ fichier, type, duree, largeur, hauteur, modele, genere_le }`, écrit par `generation.py publier` ; la consigne et la graine restent dans le lot `src/data/diaporamas/generation/<slug>.json`. Fichier `public/diaporamas/<slug>/NNN-mouvement.mp4` (aller-retour de 10 s, H.264 yuv420p, sans son). |
| Rendu | Le clip est posé dans une boîte de la taille de l'image, **étiré sur la zone utile** (le modèle a reçu l'image étirée à des dimensions multiples de 32 ; l'étirement inverse la recouvre exactement) et reçoit la **même transformation que l'image : la caméra calée sur la narration continue** de travailler. Plutôt que de figer la caméra : le mouvement généré est discret et la caméra lente ; figer aurait perdu les cadres liés à la narration. **Image fixe d'abord** (entrée ordinaire : fondu, gris → couleur, recul), puis le clip paraît en fondu de 1,2 s à 1,8 s de voix (ou 0,3 s après la plongée d'une mosaïque), **joué une seule fois, puis sa dernière image reste tenue** jusqu'à la fin de la diapositive (retour de l'utilisateur du 2026-10-12 : « ça va pas que ça fasse des allers-retours et que ça boucle » ; la première version bouclait un aller-retour de 10 s). Calé sur l'horloge de la voix : figé en pause, recalé après un saut ; s'efface sous un plan (spec 14), s'arrête avec le calque. |
| Mouvement réduit | `prefers-reduced-motion` : aucun clip chargé, image fixe, ligne du cartouche masquée. |
| Signalement | Cartouche : quatrième ligne « mise en mouvement par IA ». Livre d'images (sans JavaScript) : le clip sous l'image, avec sa mention et le modèle. Page de la période : section « Images mises en mouvement » (principe, modèle, liste des diapositives, originaux sur Commons). |
| Encodage | **Ralenti de moitié** (retour de l'utilisateur du 2026-10-12 : « deux fois plus lentement ») par interpolation de mouvement à l'encodage (ffmpeg `minterpolate`, images intermédiaires calculées : 10 s à 24 images/s, fluides, sans artefact visible sur fumées et foules, ≈ 20 s de calcul par clip ; préféré à `playbackRate` 0,5 dans le lecteur, qui donnerait 12 images/s), sans son, crf 27, **débit plafonné à 3,2 Mbit/s** : gravures très détaillées 4,2 Mo (10 à 12 Mo sans plafond, aucune perte visible à l'échelle 1), tableaux 1,2 à 2,5 Mo ; `verifier.py` avertit au-delà de 4,5 Mo. Le clip de la diapositive suivante est mis en cache d'avance. |
| Longueur | **Le clip couvre toute la diapositive** (retour de l'utilisateur du 2026-10-12 : il ne doit pas s'arrêter avant le changement). `generation.py preparer` calcule par diapositive le nombre d'images à générer (4k + 1, de 121 à 289, soit 5 à 12 s générées, 10 à 24 s ralenties) d'après la durée de la voix et de sa pause, moins le départ (1,8 s, ou la fin de la plongée d'une mosaïque) ; `mouvement.py` génère cette longueur (au-delà des 121 images d'entraînement du modèle ; repli automatique sur une aire réduite si la mémoire manque) ; `verifier.py` avertit d'un clip plus court que la diapositive. Révolution : 121 images pour les mosaïques (Bastille, Tuileries), 189 à 249 pour les autres. **Mesure** (Valmy, 2026-10-12, A100 80 Go) : 241 images en 1184 × 736 en 12,1 min, contre 5,3 min pour 121 images ; une dizaine de clips par période ≈ 2 h de machine ≈ 13 unités. |
| Incompatibilités | Jamais sur un avant / après (autre calque) ni une image entière (le clip ne couvre que la zone utile). Compatible avec les mosaïques (Bastille, Tuileries : le clip paraît après la plongée) et les plans. |
| `verifier.py` | Famille « mouvement (spec 16) », étape C : fichier, dimensions, durée, codec (ffprobe), proportions de la zone utile (erreur au-delà de 6 % : source changée), modèle, usage, entrée dans le lot, plafond de 15, poids, incompatibilités. |

**Lot publié** : Révolution, 8 clips (diapositives 18, 28, 35, 53, 56, 85, 92, 110 ; 22 Mo en tout,
0,9 à 4,2 Mo chacun), modèle Wan 2.2 TI2V-5B, calculés le 2026-10-11. Contrôlé le 2026-10-12 dans le
vrai Chrome par Playwright : image fixe d'abord, clip aligné au pixel sur la zone utile avec la
transformation de l'image, joué une fois puis tenu, figé en pause, après la plongée sur une
mosaïque, arrêté avec le calque. Valmy (56) est gardé bien qu'un drapeau grossisse à la fin du clip ;
à refaire avec une consigne adoucie (sans « flags flutter ») au prochain lot, qui servira aussi de
premier essai réel de `generation.py lancer` (CLI). Réserve : 7 clips avant le plafond de 15.

## Procédure d'un lot (périodes suivantes)

1. Choisir une dizaine de diapositives à scène animable (fumées, drapeaux, foule, eau, ciel), une ou
   deux par acte, plutôt longues ; jamais un portrait, jamais une inscription lisible ; écrire le lot
   (consigne anglaise, graine).
2. `generation.py preparer <slug>` puis `generation.py lancer <slug>` (A100, ≈ 5 min et ≈ 0,5 unité
   par clip ; la session est arrêtée par le script).
3. Ouvrir la planche, juger ; retirer du lot ou relancer avec `--seulement` les ratés.
4. `generation.py publier <slug>`, `verifier.py <slug>`, `npm run build`, visionnage dans le lecteur ;
   `generation.py retirer <slug> --seulement n` pour un clip qui déplaît après coup.

## Reste à décider

- Les deux autres usages (reconstitution photo d'après gravure, colorisation des vraies
  photographies) et leur pilote ; `verifier.py` n'admet pour l'instant que l'usage `mouvement`.
