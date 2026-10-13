# Spec 17 — Trois essais sur Colab : relief, ambiances sonores, netteté (essais)

Décidé avec l'utilisateur le 2026-10-12, après la question « en quoi d'autre utiliser mon abonnement
Colab Pro pour rendre les diaporamas plus sympas ? ». Trois pistes retenues pour un **essai**, dans
le cadre de la spec 16 (modèles à poids ouverts, rien d'inventé, signalement). **État : essais jugés le
2026-10-12 ; relief abandonné, netteté et ambiances sonores à intégrer** (voir « Verdict et intégration »).

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

## Essai 4 — Compléter les images entières (demandé le 2026-10-12)

Demande de l'utilisateur : les images montrées **en entier sur fond noir** (spec 12, « Images
entières sur fond noir » : images en hauteur ou trop petites pour remplir la scène) laissent du noir
autour d'elles. Essayer de **compléter l'image au-delà de ses bords** par un modèle sur Colab, et
d'afficher **la partie complétée derrière un filtre un peu flou**, l'image d'époque restant nette et
intacte au centre. **État : essai jugé le 2026-10-12, retenu** (voir « Fonds prolongés : verdict et
intégration »).

- **Principe** : le modèle prolonge la scène jusqu'au format de la scène (16:9) ; seul le
  prolongement est généré, l'image d'origine n'est jamais retouchée. Le flou cache ce que le
  modèle invente : le prolongement sert d'ambiance, pas de document.
- **Images** : 8 images entières de la Restauration (la période qui en a le plus), variées :
  tableaux et gravures, en hauteur et petites, dont un portrait et une image à marge de papier.
- **Modèles** : un ou deux modèles à poids ouverts et licence libre (règles de licence de cette
  spec), capables de prolonger une image.
- **Variantes sur la planche**, à la taille de la scène, pour chaque image :
  1. aujourd'hui (fond noir) ;
  2. **témoin sans IA** : la même image agrandie et floutée en fond (procédé classique), pour voir
     ce que la génération apporte de plus ;
  3. prolongement généré, **net** (pour juger ce que le modèle invente) ;
  4. prolongement généré **flouté**, à deux forces de flou, légèrement assombri, avec un raccord
     doux au bord de l'image.
- **À surveiller** : personnages, visages ou textes inventés dans le prolongement, raccord visible
  au bord de l'image, fond qui attire l'œil plus que l'image, marges de papier et cadres prolongés
  tels quels, lisibilité des surimpressions (cartouche, sous-titres) sur le fond.
- **Signalement** (si l'essai est retenu) : à décider.

## Fonds prolongés : verdict et intégration (2026-10-12)

Essai fait le 2026-10-12 (planche `.cache/diaporamas/essais-colab/fond/planche.html`, ≈ 0,5 unité
Colab) : FLUX.2 klein 4B (Apache 2.0, toile préremplie d'un flou, 22 s par image sur L4) donne de
bons prolongements ; SDXL inpainting rate les 8 images. Verdict de l'utilisateur : « franchement
c'est top, ça vaut le coup de prolonger, et il ne faut pas beaucoup de flou, encore moins que le flou
faible de la page ». L'agent d'essai recommandait au contraire le flou fort et les seuls tableaux à
décor ; les décisions de l'utilisateur prévalent :

| Sujet | Décision |
|---|---|
| Modèle | **FLUX.2 klein 4B**, toile préremplie ; sortie accordée en couleur sur l'original avant d'être posée ; l'image d'époque (zone utile) est recollée intacte, au pixel près. |
| Flou | **Environ 0,5 % de la largeur de la scène** (le « flou faible » de la planche valait 0,9 %, le « fort » 2,6 %), fond légèrement assombri, raccord doux au bord. Valeurs en CSS, réglables d'un seul endroit. |
| Champ | **Toutes les images entières** (tableaux, gravures, portraits, documents) : plus de fond noir. |
| Inventions | **Relecture de chaque fond, net.** Un fond qui montre un personnage, un visage, un texte, un cachet ou un anachronisme (essai : immeubles haussmanniens derrière l'Hôtel de Ville de 1830, faux cachet près de Louis XVIII) n'est pas rejeté : **il passe en flou fort (≈ 2,5 %)**, qui cache l'invention. Le niveau de flou est donc une donnée par image. Planche des cas passés en flou fort remise à l'utilisateur. |
| Taille du fond | Assez grande pour 0,5 % de flou (1 280 px à l'essai pesaient 63 à 430 ko ; à mesurer : la plus petite taille sans perte visible à ce flou) ; les fonds en flou fort peuvent être en 640 px. |
| Lecteur | Le fond suit la transformation de l'image (rapprochement lent, entrée en scène, fondus entre diapositives, plans et galeries) ; téléphone et scène presque carrée (bandes en haut et en bas) à traiter ; `prefers-reduced-motion` : le fond reste (il est fixe). |
| Signalement | **Crédits de la page et livre d'images seulement** ; le livre d'images montre l'image d'époque seule. |
| Pilote | **Restauration d'abord** (57 images entières), visionnée dans le lecteur avant de généraliser. |

### Retours sur la planche des fonds de la Restauration (2026-10-12)

Lot de la Restauration : 101 images entières (57 images de diapositive et 44 plans), 98 en flou
faible et 3 en flou fort (105, 113, 113b). Retours de l'utilisateur sur la planche :

- **« C'est bien sur les côtés mais pas en haut et en bas »** : le modèle ne prolongeait que les
  côtés (avec les quatre côtés d'un coup, il peignait une pièce où le tableau est posé debout) ; le
  haut et le bas étaient faits sans IA, en étirant le bord. **À refaire avec un vrai prolongement**,
  essai en deux passes (côtés, puis haut et bas à partir de l'image élargie), d'abord sur 8 images.
- **« Le flou faible est encore fort et trop foncé »** : le flou faible passe de 0,5 % à **0,25 %**
  de la largeur de la scène, la luminosité du fond de 72 % à **80 %**. Ces valeurs remplacent celles
  du tableau ci-dessus. Le flou fort (≈ 2,5 %) ne change pas. Conséquences : taille des fonds à
  remesurer (640 px avait été retenu pour 0,5 %), relecture à refaire à l'échelle réelle.

**Suite du même jour.** Haut et bas refaits en **deux passes** (côtés, puis haut et bas à partir de
l'image élargie, marge de 25 %, consigne nommant le dessus et le dessous ; bandes de papier continues
sans modèle pour les fonds « papier » et « uni ») : plus de tableau posé dans une pièce. Fonds en
**1 024 px** pour le flou faible (640 px en flou fort), 4,4 Mo pour la période. Relecture refaite à
0,25 % : **9 fonds en flou fort** (4b, 28, 100, 105, 105b, 106b, 112, 113, 113b). Défaut connu : une
jonction horizontale entre côtés et bandes, qui se devine sur les fonds à décor (23, 58b ; halo sur
21). Verdict de l'utilisateur sur la comparaison et le lecteur : **« c'est bien, ça donne bien »** ;
le nouveau jeu est publié dans la Restauration, sauf la Girafe (76), ratée dans ce jeu, qui garde
son premier fond. Lecteur : module `fond.ts`, réglages dans `constantes.ts` (`FOND_*`).

### Généralisation aux périodes 04 et 05 (2026-10-14)

Pilote validé par l'utilisateur dans le lecteur (« c'est nickel avec les fonds ») : les fonds
prolongés deviennent une règle (tableau « Couche calculée sur Colab » de la spec 12). Produits et
publiés dans l'arbre de travail le 2026-10-14, ≈ 2,6 unités Colab estimées pour les deux périodes :

| Période | Images entières | Flou faible | Flou fort |
|---|---|---|---|
| 04 monarchie de Juillet | 106 | 100 | 6 (23, 38b, 70b, 75, 117, 121) |
| 05 IIe République | 103 | 93 | 10 (5, 9, 10, 49b, 72b, 79, 84, 103, 103b, 116b) |

Leçons (détail dans le README des scripts) : choisir le genre « papier » ou « décor » d'après la
zone utile (une feuille à marge classée « décor » est posée debout dans une pièce) ; champ `teinte`
du lot quand un bord de l'image est pris dans des hachures ou un cadre ; un dossier distant par
période sur Colab. Les périodes 01 et 02 n'ont pas d'image entière.

**Images entières colorisées (période 05, 17 images)** : le fond est tiré de l'original gris alors
que l'image passe en couleur ; visible sur les décors (69, 16…). Essai non publié de fonds tirés de
la version colorisée (planche `fonds-deuxieme-republique-couleur`). **À décider par l'utilisateur.**

## Reste à décider

- Netteté : généralisation aux périodes 02 à 05 après le visionnage du pilote ; seuil et plafond de poids.
- Ambiances sonores : extension aux périodes sans clip (01 à 04 n'ont de clips que la Révolution), dose.
- Fonds prolongés : généralisation aux autres périodes après le visionnage du pilote.
