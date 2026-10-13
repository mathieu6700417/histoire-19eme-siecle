# Spec 17 — Trois essais sur Colab : relief, ambiances sonores, netteté (essais)

Décidé avec l'utilisateur le 2026-10-12, après la question « en quoi d'autre utiliser mon abonnement
Colab Pro pour rendre les diaporamas plus sympas ? ». Trois pistes retenues pour un **essai**, dans
le cadre de la spec 16 (modèles à poids ouverts, rien d'inventé, signalement), puis une quatrième
(fonds prolongés). **État au 2026-10-14 : relief abandonné ; ambiances sonores et fonds prolongés
devenus des règles ; netteté appliquée à la Révolution seulement, suspendue ailleurs.**

## Règles communes

| Sujet | Décision |
|---|---|
| Portée | **Essais seulement** : planches et pages d'écoute dans `.cache/diaporamas/essais-colab/`, jugées par l'utilisateur. **Rien n'est intégré** au lecteur, aux données des périodes ni à `public/` ; rien n'est commité ni déployé. |
| Période d'essai | La Révolution (slug `revolution`), sauf mention contraire. |
| Calcul | Colab Pro, piloté par la **CLI officielle `colab`** (script Python autonome, `/content/in` → `/content/out`, suivi par `colab exec` courts, `colab stop` à la fin, puis `colab sessions` pour vérifier qu'il ne reste rien). **Une seule session**, réutilisée pour les trois essais. **Plafond : 10 unités** pour l'ensemble. |
| Licences | Avant tout calcul, relever la licence de chaque modèle sur sa fiche (poids et code) et la noter dans le journal et sur la planche. Précédent de la spec 16 : les licences **non commerciales** et celles qui excluent l'Union européenne sont écartées pour une publication. Un modèle à licence douteuse peut figurer dans l'essai (privé) s'il est **marqué « licence à valider »** ; il ne sera pas publié sans accord. |
| Gemini | 0 $ : aucun appel. |
| Journal | `docs/journal/essais-colab.jsonl` (`scripts/journal/noter.py`). |

## Essai 1 — Relief par carte de profondeur (nouvel essai de parallaxe)

La parallaxe 2,5D a été **essayée puis abandonnée le 2026-10-08** (spec 12, « Enrichissements
visuels », point 6 ; commits `c38ea01` et `d8e3d09`) : Depth Anything V2 Small en local, image
découpée en 3 plans, comblement OpenCV, glissement de 0,9 à 1,5 % de la scène. Le motif du refus
n'a pas été consigné. L'utilisateur accepte le 2026-10-12 de **réessayer autrement** :

- **Profondeur plus fine**, calculée sur Colab par un ou deux modèles à licence libre (à comparer).
- **Relief continu** : déplacement pixel par pixel d'après la carte de profondeur (maillage ou
  shader WebGL), **sans découpe en calques ni comblement** ; la caméra existante garde la main.
- **Images** : les quatre du banc d'octobre (Pils, Valmy, Hubert Robert, Lejeune : diapositives
  47, 56, 81, 122 alors, **51, 60, 85, 127** dans la numérotation du 2026-10-12), plus deux
  gravures (36 et 102).
- **Planche** : page autonome, chaque image avec son mouvement de caméra réel, sans relief et avec
  relief, à deux amplitudes (discrète et marquée) ; la carte de profondeur visible à la demande.
- **À surveiller** : étirements aux bords des objets proches, visages déformés, vibration du trait
  sur les gravures. `prefers-reduced-motion` : pas de relief.

## Essai 2 — Ambiances sonores

Une couche de sons d'ambiance discrète sous la voix (foule, canon, cloches, feu, vent, mer).

- **Champ** : les **8 diapositives de la Révolution déjà mises en mouvement** (18, 28, 37, 57, 60,
  89, 97, 115 dans la numérotation du 2026-10-12 ; la spec 16 les cite sous leurs anciens numéros) :
  le son accompagne ce qui bouge.
- **Deux sources comparées** pour chaque diapositive :
  1. **générée sur Colab** par un modèle audio à poids ouverts (texte → son, ou clip → son) ;
  2. **banque de sons libres**, enregistrements réels sous **CC0** (ou domaine public), source et
     auteur notés.
- **Page d'écoute** : par diapositive, le clip avec la **narration**, la musique de la diapositive
  si elle en a une, et l'ambiance au choix (aucune / générée / banque), niveau réglable ; niveau
  proposé par défaut bien sous la voix.
- **Garde-fous** : aucun son de voix intelligible, aucune musique dans l'ambiance, rien
  d'anachronique (ni moteur ni sirène) ; le son illustre, il ne prouve rien.
- **Signalement** (si l'essai est retenu, à confirmer) : son généré mentionné dans les crédits.

## Essai 3 — Netteté des sources (super-résolution)

Agrandir les images trop petites pour que la caméra plonge sans flou.

- **Choix des images** : mesurer, sur la Révolution, les images où le zoom le plus serré de la
  caméra dépasse la résolution de la source (pixels d'écran par pixel d'image à 1920 × 1080) ;
  prendre les **8 pires**, en mêlant tableaux et gravures.
- **Modèles** : deux modèles de super-résolution à licence libre, comparés (un fidèle, un plus
  « restaurateur » si la licence le permet).
- **Planche** : pour chaque image, le **cadre le plus serré de la caméra** à l'échelle 1, original
  contre chaque modèle, côte à côte, plus un volet glissant.
- **À surveiller** : trait lissé ou redessiné sur les gravures, visages modifiés, textures
  inventées, poids du fichier.
- **Signalement** (décidé le 2026-10-12) : **dans les crédits de la page et le livre d'images
  seulement** (« image agrandie par IA », modèle), **pas au cartouche** : le contenu ne change pas.

## Verdict et intégration (2026-10-12)

Essais faits le 2026-10-12 (0,61 unité Colab, journal `docs/journal/essais-colab.jsonl`, pages dans
`.cache/diaporamas/essais-colab/`, servies par `servir.py` sur le port 8017). Verdict de l'utilisateur
après visionnage et écoute :

| Essai | Verdict |
|---|---|
| 1. Relief | **Abandonné une seconde fois** (« je suis pas convaincu »), malgré le relief continu et la profondeur plus fine. Ne plus le proposer. |
| 2. Ambiances sonores | **Retenu, avec EzAudio** (s3_xl, licence MIT, code et poids). La banque de sons libres et TangoFlux (non commercial) ne sont pas retenus. |
| 3. Netteté | **Retenu, avec Real-ESRGAN** (x4plus, BSD-3) « quand on n'a pas une image de bonne qualité », contre la recommandation de l'agent d'essai (SwinIR, plus fidèle au trait) : l'utilisateur trouve que Real-ESRGAN « donne bien ». |

### Netteté : règles d'intégration

Plafond de taille et seuil de besoin **révisés le 2026-10-14** (« Netteté : poids, et généralisation »,
plus bas), qui prévalent ; la netteté n'est appliquée qu'à la Révolution.

| Sujet | Décision |
|---|---|
| Ordre | **D'abord un fichier plus grand tiré de l'original de Commons**, sans IA (l'essai a montré que les 132 images, servies à 1 600 px au plus, sont toutes sous la résolution de l'écran au cadre le plus serré, et que l'original suffit pour 82 d'entre elles). **Real-ESRGAN seulement quand l'original ne suffit pas.** |
| Seuil | Mesure au cadre le plus serré de la caméra, en plein écran 1920 × 1080 : on vise au plus 1 pixel d'écran par pixel d'image ; Real-ESRGAN si l'original laisse plus de 1,25. Grand côté plafonné à 3 200 px ; poids par image et poids total de la période rapportés (choix de mise en œuvre du 2026-10-12, à réviser au visionnage). |
| Portraits | **Inclus** (décision de l'utilisateur) : le garde-fou de la spec 16 « jamais de visage régénéré d'une personne nommée » est **assoupli pour la seule super-résolution**. Il reste entier pour les clips et toute autre génération. |
| Champ | Image principale des diapositives et plans (spec 14). Mosaïques, objets, médaillons, cartes : hors pilote. |
| Dérivés | Une image qui porte un clip (`image.video`) ou une version colorisée (`image.couleur`) doit rester alignée : mêmes proportions de zone utile ; `verifier.py` doit rester au vert. |
| Signalement | **Crédits de la page et livre d'images seulement** (« image agrandie par IA », modèle), pas au cartouche. Champ de données qui garde la trace (modèle, date, source). |
| Pilote | **Révolution d'abord**, visionnée dans le lecteur avant de généraliser aux périodes 02 à 05. |

### Ambiances sonores : règles d'intégration

| Sujet | Décision |
|---|---|
| Champ | **Tous les clips existants** : les 8 de la Révolution et les 10 de la période 05. Règle : toute diapositive mise en mouvement a son ambiance ; pas d'ambiance sur une image fixe. |
| Modèle | EzAudio s3_xl ; consigne en anglais par diapositive, gardée dans le lot de génération à côté de celle du clip ; rien que la narration ne dise (la pluie a été retirée des diapositives 28 et 37 pendant l'essai). |
| Niveau | **−12 dB, soit environ 16 dB sous la voix** (réglé par l'utilisateur à l'écoute ; l'essai proposait −14 dB). Fichiers normalisés comme à l'essai (≈ −23 LUFS, crête −1 dBTP). |
| Durée | L'ambiance couvre le clip : elle entre en fondu avec lui et sort en fondu à la fin de la diapositive ; pas de boucle audible. |
| Lecteur | Calée sur l'horloge de la voix comme le clip : figée en pause, recalée après un saut, coupée avec le calque ; suit le volume et la sourdine du lecteur. |
| Mouvement réduit | Pas de clip, donc pas d'ambiance. |
| Signalement | **Crédits de la page et livre d'images seulement** (décision de l'utilisateur) ; la ligne du cartouche « mise en mouvement par IA » ne change pas. |
| Garde-fous | Ni voix intelligible, ni musique, ni son anachronique. Les agents ne peuvent pas écouter : **page d'écoute obligatoire** pour tout nouveau lot, jugée par l'utilisateur avant publication. |

### Netteté : poids, et généralisation (2026-10-14)

Pilote de la Révolution validé (« c'est tout nickel »), mais lourd : 132 variantes, 117 Mo de plus.
Décisions de l'utilisateur avant de généraliser :

| Sujet | Décision |
|---|---|
| Plafond | Grand côté à **2 560 px** au lieu de 3 200 (l'utilisateur ne voit pas de différence ; −22 % mesuré sur échantillon). Qualité WebP 74 inchangée. |
| Besoin | **Pas de variante pour toutes les images** : seulement quand l'image servie manque vraiment de finesse au cadre le plus serré, c'est-à-dire plus de **1,3 pixel d'écran par pixel d'image** en plein écran 1920 × 1080 (seuil choisi à la mise en œuvre, à réviser). Real-ESRGAN, comme avant, seulement si l'original de Commons laisse plus de 1,25. |
| Champ | **Rien n'est appliqué pour l'instant** (décisions de l'utilisateur du 2026-10-14 : « n'étends pas la netteté des autres périodes pour l'instant », puis « qu'il ne touche à rien pour l'instant »). La Révolution reste telle que commitée (132 variantes, plafond 3 200 px) ; les deux réglages ci-dessus sont décidés mais **pas encore mis en œuvre** dans `nettete.py`. Ne rien relancer sans sa demande. |

## Fonds prolongés des images entières (essai 4, règle depuis le 2026-10-12)

Cette section donne **l'état final** ; l'historique des essais et des retours est résumé à la fin.
Mode d'emploi des outils : `scripts/diaporamas/README.md`, « Fonds prolongés des images entières ».

**Demande de l'utilisateur (2026-10-12)** : les images montrées **en entier** (spec 12, « Images
entières sur fond noir » : images en hauteur ou trop petites pour remplir la scène) laissaient du
noir autour d'elles. On **prolonge l'image au-delà de ses bords** par un modèle sur Colab et on
montre ce prolongement **derrière un léger flou**, l'image d'époque restant nette et intacte.
Verdicts : « franchement c'est top, ça vaut le coup de prolonger » (essai), « c'est nickel avec
les fonds » (pilote de la Restauration dans le lecteur).

### Règles

| Sujet | Décision |
|---|---|
| Statut | **Règle pour toutes les périodes** : toute image entière a son fond prolongé (image principale et plans). |
| Principe | Seul le prolongement est généré. L'image d'époque (sa zone utile) n'est jamais retouchée ; elle est posée intacte par-dessus le fond. Le fond est une ambiance, pas un document. |
| Modèle | **FLUX.2 klein 4B** (Apache 2.0), toile préremplie d'un flou de l'image, sortie accordée en couleur sur l'original. SDXL inpainting : écarté (rate toutes les images). |
| Méthode | **Deux passes.** Passe 1 : les côtés, à hauteur d'image. Passe 2 : le haut et le bas, à partir de l'image déjà élargie (marge de 25 %), avec une consigne qui nomme ce qu'il y a au-dessus et au-dessous. Pour les images sur papier ou à fond uni : bandes de papier continues, sans modèle. |
| Flou | **0,25 % de la largeur de la scène** (« flou faible »), constant à l'écran quel que soit le zoom. |
| Luminosité | **80 %** de celle de l'image. Raccord doux au bord de l'image (0,3 %). |
| Inventions | **Relecture de chaque fond, net, à l'échelle de génération.** Un fond qui montre un personnage, un visage, un texte, une plaque, une enseigne, un drapeau inventé, un anachronisme (immeubles haussmanniens avant 1853, réverbère moderne, poteaux) ou un reflet du sujet sous l'image : un ou deux tirages de plus ; si le défaut persiste, le fond n'est pas rejeté, **il passe en flou fort (2,5 %)**, qui le cache. Le niveau de flou est une donnée par image (`image.fond.flou`). Un fond simplement raté suit la même règle. |
| Taille | **1 024 px** de large en flou faible, **640 px** en flou fort ; WebP. De 4 à 5 Mo par période. |
| Lecteur | Module `fond.ts` : le fond est sous l'image et sous les plans, suit la transformation de l'image (rapprochement, entrée en scène, fondus croisés). Réglages en un seul endroit : `FOND_FLOU_FAIBLE`, `FOND_FLOU_FORT`, `FOND_LUMIERE`, `FOND_RACCORD` dans `constantes.ts`. Une image entière sans `fond` garde le fond noir. `prefers-reduced-motion` : le fond reste (il est fixe). |
| Signalement | **Crédits de la page seulement** (section « Fonds prolongés ») ; rien au cartouche ; le livre d'images montre l'image d'époque seule. |
| Coût | ≈ 1 h de L4 et 1,5 à 2 unités Colab par période d'une centaine d'images entières ; 0 $ Gemini. |

### État par période (2026-10-14)

| Période | Images entières | Flou faible | Flou fort |
|---|---|---|---|
| 01 Révolution, 02 Consulat et Empire | 0 | | |
| 03 Restauration | 101 | 92 | 9 (4b, 28, 100, 105, 105b, 106b, 112, 113, 113b) |
| 04 monarchie de Juillet | 106 | 100 | 6 (23, 38b, 70b, 75, 117, 121) |
| 05 IIe République | 103 | 93 | 10 (5, 9, 10, 49b, 72b, 79, 84, 103, 103b, 116b) |

Exception : la Girafe (Restauration, 76), ratée en deux passes, garde un fond à bandes étirées.

### Limites connues et points ouverts

- **Jonction horizontale** entre les côtés et les bandes du haut et du bas : elle se devine sur une
  partie des fonds à décor (Restauration 21, 23, 58b ; une dizaine en 04 et 05). Piste non faite :
  passe 2 avec recouvrement, ou fondu en domaine de gradient.
- **Le bord de l'image reste visible** (image nette sur fond flou), et le fond reste gris autour
  des images très claires.
- **Images entières colorisées** (période 05, 17 images) : le fond est tiré de l'original gris alors
  que l'image passe en couleur ; visible sur les décors (69, 16). Essai non publié de fonds tirés de
  la version colorisée (planche `fonds-deuxieme-republique-couleur`). **À décider par l'utilisateur.**
- Non vérifié : plein écran d'un téléphone tenu debout, Safari iOS.

### Leçons de fabrication

- Choisir le genre « papier » ou « décor » **d'après la zone utile** : une feuille à marge classée
  « décor » est peinte debout dans une pièce, avec son cachet reflété.
- Ne jamais demander les quatre côtés en une passe (même effet de tableau posé dans une pièce) ; ne
  pas étirer le bord pour faire le haut et le bas (refusé par l'utilisateur) ; pas de consigne
  générique (paysages de rivière autour des intérieurs, bandes restées floues).
- Champ `teinte` du lot quand un bord de l'image est pris dans des hachures, une reliure ou un cadre.
- Un dossier distant par période sur Colab ; fermer la session pendant les relectures.

### Historique (pour mémoire, valeurs remplacées)

- Essai du 2026-10-12 sur 8 images de la Restauration, avec un témoin sans IA (la même image
  agrandie et floutée) : le généré l'emporte sur les tableaux à décor. L'agent d'essai recommandait
  le flou fort et les seuls tableaux à décor ; l'utilisateur a voulu peu de flou et toutes les images.
- Flou faible : d'abord 0,9 % (planche), puis 0,5 %, puis **0,25 %** (« encore fort »). Luminosité :
  72 %, puis **80 %** (« trop foncé »). Taille : 640 px, puis **1 024 px** pour ce flou.
- Haut et bas : d'abord étirés sans IA (« c'est bien sur les côtés mais pas en haut et en bas »),
  puis générés en seconde passe (« c'est bien, ça donne bien »).
- Flous forts de la Restauration : 3 à la première relecture (flou 0,5 %), 9 à la relecture à 0,25 %.

## Reste à décider

- Ambiances sonores : extension à des diapositives sans clip, dose.
- Fonds prolongés : fonds des images entières colorisées (période 05) ; atténuation de la jonction.
- Netteté : mise en œuvre des deux réglages de poids et extension aux périodes 02 à 05, quand
  l'utilisateur le demandera.
