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

- **Lot** : `src/data/diaporamas/xixe/generation/revolution.json`, 8 diapositives de la Révolution à
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
- **Journal** : `docs/journal/xixe/generation-mouvement.jsonl`.

## Visionnage et intégration (2026-10-12)

Verdict de l'utilisateur sur la planche des 8 clips : « ça rend bien, je garde ». Décisions prises
pour l'intégration (les points laissés ouverts le 2026-10-11 sont tranchés ici) :

| Sujet | Décision |
|---|---|
| Données | `image.video` `{ fichier, type, duree, largeur, hauteur, modele, genere_le }`, écrit par `generation.py publier` ; la consigne et la graine restent dans le lot `src/data/diaporamas/xixe/generation/<slug>.json`. Fichier `public/xixe/diaporamas/<slug>/NNN-mouvement.mp4` (aller-retour de 10 s, H.264 yuv420p, sans son). |
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
4. Ambiance sonore de chaque clip gardé (spec 17 : champ `ambiance` du lot, `ambiance.py`, page
   d'écoute jugée par l'utilisateur) : tout clip publié a son ambiance.
5. `generation.py publier <slug>`, `verifier.py <slug>`, `npm run build`, visionnage dans le lecteur ;
   `generation.py retirer <slug> --seulement n` pour un clip qui déplaît après coup.

## Transformation en photographie (décidé le 2026-10-12)

Annotations de visionnage de la période 05 (diapositives 82 et 86) : coloriser les photographies,
transformer les gravures en « photo moderne », et montrer la transition dans le diaporama. Essai de
quatre images sur Colab le 2026-10-12 (planche `.cache/diaporamas/essais-colorisation/planche.html`,
journal `docs/journal/xixe/generation-colorisation.jsonl`) : DDColor, FLUX.2 klein 4B (dont une variante
« couleur seule », fidèle au trait) et Qwen-Image-Edit-2509. L'agent d'essai recommandait la
colorisation « couleur seule » et déconseillait la transformation des gravures (coiffures,
drapeaux, gestes et visages inventés). **Décisions de l'utilisateur, après avoir vu la planche :**

| Sujet | Décision |
|---|---|
| Usage | **Pas de colorisation.** Photographies et gravures sont **transformées en photographie** (rendu photographique en couleur de la même scène), avec une **transition** de l'original vers la photo dans le diaporama. |
| Modèle | **Qwen-Image-Edit-2509** (Apache 2.0), dans tous les cas (≈ 96 s par image sur A100, 40 pas). |
| Pilote | **Période 05 d'abord** : toutes ses gravures, lithographies et photographies qui montrent une scène ou un lieu ; jugé dans le diaporama avant de décider pour les autres périodes. Le plafond de 8 reconstitutions par période ne s'applique pas à ce pilote. |
| Visages | **Scènes oui, portraits non** : on transforme une scène même si une personne nommée y figure de loin (Lamartine à la tribune, le prince à cheval) ; on ne transforme ni les portraits ni les photographies de personnes, où le visage est le sujet. Le garde-fou « jamais de visage régénéré d'une personne nommée » est assoupli d'autant. |
| Exclus aussi | Les photographies montrées pour leur technique ou comme œuvre photographique (annotation 82), les peintures déjà en couleur, les documents, cartes, caricatures, objets et manuscrits. |
| Signalement | Obligatoire : cartouche « transformée en photo par IA » tant que la photo est à l'écran, crédits et livre d'images ; l'original est toujours montré d'abord. |

### Révision du même jour : la colorisation « couleur seule » remplace la transformation

Le lot de la période 05 (56 gravures, lithographies et photographies de scènes ; journal
`docs/journal/xixe/generation-colorisation.jsonl`, planches dans
`.cache/diaporamas/photos-qwen/deuxieme-republique/`) a été jugé par l'utilisateur :

- **Transformation en photo : abandonnée.** FLUX.2 klein 4B (2,9 s par image) : 7 bonnes, 36 avec
  défaut, 13 ratées ; Qwen-Image-Edit-2509 (97 s par image, 4 images faites) tient mieux la
  composition mais invente aussi. Verdict de l'utilisateur : « ça invente trop de trucs ».
  Les décisions du tableau ci-dessus sur l'usage, le modèle et les visages ne s'appliquent plus.
- **Colorisation « couleur seule » : retenue** (36 bonnes, 18 avec défaut, 2 ratées sur 56).
  Méthode : FLUX.2 klein 4B (Apache 2.0) reçoit l'image et une consigne stricte de colorisation ;
  **on ne garde que la chrominance de sa sortie, posée sur la luminance de l'original**. Aucun
  trait n'est redessiné, le fondu est exact au pixel. Les coloriseurs dédiés DDColor (7 bonnes)
  et DeOldify (3 bonnes) ne donnent qu'un voile sépia : écartés.
- **Rendu** : une gravure colorisée ressemble à une estampe rehaussée à la main, pas à une photo.
- **Consigne** : texte commun neutre (ni drapeaux, ni costumes, ni personnages cités) ; une phrase
  par image pour ce qui y figure vraiment, avec les couleurs à respecter (drapeau tricolore,
  uniformes) ; saturation modérée.
- **Champ** : gravures, lithographies et photographies monochromes de scènes et de lieux. Exclus :
  les estampes déjà coloriées (gain nul), les photographies montrées pour leur technique ou comme
  œuvre, les portraits et photographies de personnes, les peintures, documents, cartes, caricatures.
- **Relecture obligatoire image par image avant publication** : les couleurs sont plausibles, pas
  documentées (un drapeau teint en rouge en 1848 serait un contresens).
- **Dans le diaporama** : l'original d'abord, puis un fondu vers la version colorisée ; mention
  « colorisée par IA » au cartouche tant qu'elle est à l'écran, crédits et livre d'images.
- **Pilote** : période 05 (accord de l'utilisateur du 2026-10-12 : les 36 bonnes telles quelles,
  relance des 18 à défaut avec saturation réduite et couleurs précisées, fondu dans le lecteur).
  Les autres périodes après son visionnage.

**Mise en œuvre (2026-10-12).** Champ `image.couleur` `{ fichier, largeur, hauteur, modele, genere_le }`
(image d'une diapositive ou d'un plan), fichier `NNN-couleur.webp` / `NNN-b-couleur.webp` aux
dimensions exactes de la zone utile ; `couleur.py publier | retirer | lister` (clé : `commons`),
recettes dans `src/data/diaporamas/xixe/generation/<slug>-couleur.json`, suivi par `renumeroter.py`,
famille « couleur (spec 16) » de `verifier.py`.

| Sujet | Décision |
|---|---|
| Rendu | `couleur.ts` : la version colorisée est posée sur la zone utile avec la transformation de l'image (caméra, entrée en scène, image entière, plans). Opacité calculée à chaque rendu d'après l'horloge de la voix, sans transition CSS : pause, saut et reprise justes. |
| Temps | **Révisé le 2026-10-12 après visionnage (« la transition devrait arriver plus vite ») : fondu de 2 s, dès 1,5 s après l'apparition de l'image** (0,5 s après la fin d'une entrée en scène). Première version : fondu de 2,8 s, sans lien avec les mots : départ au tiers de la fenêtre de l'image (jusqu'au plan suivant ou la fin de la voix), au plus tôt à 2,5 s et 0,5 s après l'entrée en scène, fini 2 s avant la fin si la fenêtre le permet (moins de 7,3 s : `verifier.py` avertit). |
| Mouvement réduit | L'original seul : ni version colorisée ni mention (le plus sobre, comme pour les clips). |
| Signalement | Ligne « colorisée par IA » du cartouche, dépliée tant que la couleur est à l'écran ; livre d'images (version colorisée sous l'original) ; section « Images colorisées » de la page. |
| Incompatibilités | Clip `video`, avant / après, mosaïque : refusés. Galeries, lectures illustrées, épisodes : hors champ pour l'instant. |

**Pilote publié** : période 05, lot final de 48 images, **46 publiées** (30 images de diapositives,
16 plans ; 24 Mo), 2 refusées par incompatibilité (40 : mosaïque ; 89 : clip). Écartées à la
fabrication : 5 estampes déjà coloriées et 3 ratées. À juger au visionnage.

## Reste à décider

- ~~Colorisation « couleur seule » : extension aux autres périodes~~ **décidée le 2026-10-14** par
  l'utilisateur : la colorisation devient une règle pour toutes les périodes, à partir de la 06
  (faite à la suite de sa production) ; les périodes 01 à 04 sont à rattraper. Méthode, champ et
  exclusions : ceux du pilote, ci-dessus.
- Suite de la couche générée (ambiances sonores des clips, fonds prolongés des images entières,
  netteté) : spec 17. L'état de chaque étape pour les prochaines périodes est tenu dans le tableau
  « Couche calculée sur Colab » de la spec 12.
