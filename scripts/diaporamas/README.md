# Scripts de la section « Le siècle en images »

Chaîne de production des diaporamas narrés (une période = ~100 images + voix off). Les
décisions et les règles d'écriture sont dans `docs/specs/12-siecle-en-images.md` ; ce
fichier ne décrit que les outils.

## Dépendances

- Python 3.10 ou plus récent ; bibliothèque standard, plus **Pillow** (`pip install pillow`)
  pour l'écriture des WebP.
- **ffmpeg** (`brew install ffmpeg`) pour l'encodage AAC des voix.
- Accès réseau à `commons.wikimedia.org` et à l'API Gemini.
- Musique (`musique.py`) : bibliothèque standard et **ffmpeg** seulement.
- `GEMINI_API_KEY` dans `.env` à la racine (fichier non versionné).

Les commandes se lancent depuis la racine du projet.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `commun.py` | Bibliothèque commune : chemins, lecture/écriture du script JSON, API Commons, licences, lexique. |
| `images.py` | Métadonnées et licence (API Commons), téléchargement, WebP 1600 px, vignette du portail ; portraits des lectures et fac-similés des épisodes. Aide à la recherche (`--chercher`, `--infos`). |
| `voix.py` | Synthèse Gemini (narrateur Charon ; voix de lecture pour les lectures d'époque), contrôle de fidélité, encodage m4a, durées, horodatage des phrases ; minutage mot par mot des lectures (`--mots`). Diapositives, lectures et épisodes. |
| `alignement.py` | Alignement forcé d'un audio de lecture sur son texte (wav2vec2 français, torchaudio) : instants de chaque mot. Appelé par `voix.py`. |
| `camera.py` | Caméra calée sur la narration : étapes `image.camera` proposées par Gemini Flash (vision), contrôlées, planche-contact. |
| `musique.py` | Musique : enregistrements libres (Commons, Internet Archive), licences, découpe, fondus, sonie, m4a. |
| `carte.py` | Fonds de carte des épisodes (Natural Earth, domaine public) : `src/data/diaporamas/fonds/<nom>.json`. |
| `verifier.py` | Contrôle d'une période avant publication. |
| `prononciation.yaml` | Lexique appliqué au texte envoyé à la voix (jamais aux sous-titres). |

Données et sorties :

- `src/data/diaporamas/NN-<slug>.json` : le script d'une période (source de vérité) ;
- `public/diaporamas/<slug>/NNN.webp`, `NNN.m4a`, `vignette.webp` : fichiers servis ;
  `musique/fond-<acte>-<k>.m4a` et `musique/chant-<nom>.m4a` : musique ;
- `.cache/diaporamas/` (ignoré par git) : originaux téléchargés (`originaux/`), licences et
  métadonnées relevées (`<slug>/images.json`), empreintes, transcriptions et scores de
  fidélité des voix (`<slug>/voix.json`), réponses du modèle de vision (`<slug>/camera.json`)
  et planches-contact de la caméra (`<slug>/planche-NN.jpg`) ; licences et empreintes de la
  musique (`<slug>/musique.json`) ; `musique/sources/` : enregistrements téléchargés. (Les
  autres dossiers de `musique/`, rendus, échantillons et essais MIDI, sont des restes de
  l'essai abandonné du rendu MIDI.)

## Commandes

```sh
# Chercher une image, lire ses métadonnées complètes
python3 scripts/diaporamas/images.py --chercher "prise de la Bastille" 15
python3 scripts/diaporamas/images.py --infos "File:Prise de la Bastille clean.jpg"

# Images d'une période (toutes, ou une seule ; --force refait les WebP)
python3 scripts/diaporamas/images.py revolution
python3 scripts/diaporamas/images.py revolution --n 12

# Voix : ce qui manque ou dont la narration a changé ; --n pour refaire une diapositive
python3 scripts/diaporamas/voix.py revolution
python3 scripts/diaporamas/voix.py revolution --n 12 37

# Horodatage des phrases des audios existants (sans resynthèse ; fait aussi par voix.py)
python3 scripts/diaporamas/voix.py revolution --horodater

# Caméra : ce qui manque ou a changé ; --n pour refaire ; --planche pour relire
python3 scripts/diaporamas/camera.py revolution
python3 scripts/diaporamas/camera.py revolution --n 12 37
python3 scripts/diaporamas/camera.py revolution --planche

# Musique : ce qui manque ou a changé ; --force pour tout refaire ; --sources pour
# télécharger et contrôler les licences seulement
python3 scripts/diaporamas/musique.py revolution
python3 scripts/diaporamas/musique.py revolution --piste chant-marseillaise
python3 scripts/diaporamas/musique.py revolution --sources

# Lectures et épisodes : voix (tout ce qui manque ou a changé, ou un segment précis)
python3 scripts/diaporamas/voix.py revolution --segments lecture:sieyes episode:dette
# Lectures : minutage mot par mot des audios existants (fait aussi après chaque synthèse de
# lecture) ; --segments lecture:<id> pour une seule
python3 scripts/diaporamas/voix.py revolution --mots
# Fonds de carte des épisodes
python3 scripts/diaporamas/carte.py

# Contrôle final (code de sortie 1 en cas d'erreur ; --hors-ligne : textes des lectures
# comparés au cache Wikisource au lieu de la page téléchargée à neuf)
python3 scripts/diaporamas/verifier.py revolution
python3 scripts/diaporamas/verifier.py --tous
```

## Procédure pour une période

1. Écrire `src/data/diaporamas/NN-<slug>.json` (format dans la spec 12) : actes, narrations,
   fichiers Commons (vérifiés avec `--infos`), métadonnées de notice.
   Chaque acte porte `dates` (« 1787-1789 », « juillet-octobre 1789 » : trait d'union sans
   espaces, dates prudentes), montrées par le carton de changement d'acte du lecteur et dans le
   livre d'images ; `verifier.py` contrôle leur présence et leur forme.
   Chaque diapositive porte `date` (et `date_fin` pour une durée) pour la frise du temps
   (voir ci-dessous).
   Champ facultatif `image.recadrage` : `[x0, y0, x1, y1]` (fractions de l'original) pour
   retirer les grandes marges de papier des estampes BnF et Carnavalet ; il est appliqué au
   WebP, la légende reste celle de l'œuvre entière.
2. Relire les images sur une planche-contact (vignettes numérotées) : marges, cadres de
   musée photographiés, reflets, sujet réellement représenté.
3. `images.py <slug>` : refuse toute licence autre que domaine public / CC0 ; complète les
   champs vides depuis Commons (à relire : les champs Commons sont souvent bruts).
4. Tester une voix (`voix.py <slug> --n 1`) puis lancer le reste.
5. `camera.py <slug>`, puis relire les planches-contact (`.cache/diaporamas/<slug>/planche-*.jpg`)
   et corriger à la main les cadres faux (voir ci-dessous).
6. Musique : écrire `musique` dans le JSON (voir ci-dessous), lancer `musique.py <slug>`,
   écouter les extraits, ajuster `debut`/`fin` et les paroles.
7. `verifier.py <slug>` puis `npm run build`.

## Caméra : format et pièges

- `image.camera` : 1 à 3 étapes `{"cadre": [x0, y0, x1, y1], "quand": "passage exact"}`, en
  fractions de l'image **servie** (le WebP, donc après `recadrage`). La première étape n'a pas
  de `quand`. Le lecteur situe chaque passage au prorata dans sa phrase horodatée
  (`audio.phrases`) et lance la transition ~0,6 s avant ; une seule étape donne un zoom lent.
- Le lecteur montre le cadre en entier **sous le cartouche** (en haut à gauche) et, en plein
  écran, au-dessus des bandeaux du bas ; un cadre trop haut pour l'écran est montré depuis son
  bord supérieur (on garde les têtes). L'image couvre toujours toute la scène : un grand cadre
  peut donc passer en partie sous le cartouche.
- Taille minimale : porté aux proportions 16/10, un cadre fait au moins 30 % du plus grand
  côté de l'image (`camera.ajuster`) ; `verifier.py` tolère 25 % pour les corrections à la main.
- **Correction à la main** : modifier les étapes et ajouter `"camera_manuelle": true` à la
  diapositive ; `camera.py` ne la touchera plus. Les ratés signalés par l'utilisateur se
  corrigent ainsi, ou par `camera.py <slug> --n 12` si un nouvel essai du modèle suffit.
- Le cache (`camera.json`) garde la réponse du modèle par empreinte (narration, image,
  consignes) : changer les consignes demande d'incrémenter `VERSION` dans `camera.py`.
- Coût indicatif : ~2 appels par diapositive (proposition + relecture), environ 0,01 $ par
  diapositive, soit ~1 $ par période (tarif Gemini Flash supposé, à confirmer sur la facture).

## Frise du temps : dates des diapositives

- `date` : date des **faits racontés** (pas de l'œuvre), ISO partiel `AAAA`, `AAAA-MM` ou
  `AAAA-MM-JJ` ; `date_fin` (même format, postérieure) pour une durée : le curseur devient un
  court segment. En cas de doute, la précision la plus prudente (année ou mois plutôt que
  jour). Une diapositive de contexte sans date propre omet `date` et reprend celle de la
  précédente ; la diapositive 1 doit être datée.
- Libellés produits par le lecteur (`libelleDate` dans `src/utils/diaporamas.ts`) :
  « 14 juillet 1789 », « 2-6 septembre 1792 », « février-avril 1787 », « 1793-1794 »,
  « 21 septembre – 11 décembre 1792 ». Préférer des bornes de même précision
  (`1793-06` → `1793-10` plutôt que `1793-06` → `1793-10-09`).
- Échelle de la frise : du 1er janvier de la première année du premier acte au 31 décembre de
  la dernière année du dernier acte (les `dates` des actes). Segments des actes : de la date de
  leur première diapositive à celle de l'acte suivant.
- Affichage : dans chaque carton d'acte (glissement depuis la date précédente) et en
  surimpression 3,6 s quand la date saute de plus de 92 jours en avant ou revient en arrière
  (intervalle entièrement antérieur au début du précédent). `verifier.py` contrôle format et
  période, liste les retours en arrière en avertissement et compte les surimpressions : en
  viser peu (une dizaine par période) ; un retour en arrière d'une diapositive de contexte
  se règle souvent en omettant sa date ou en la datant au mois.

## Voix : pièges connus

- **Aucune consigne** n'est envoyée à Gemini TTS avec le texte : il la lit à voix haute
  (constaté dans le projet « Histoire zoomable »). La langue passe par `languageCode: fr-FR`.
- La transcription de contrôle **n'impose aucune langue** : une consigne lue en anglais doit
  apparaître et faire échouer le contrôle. Comparaison **mot à mot** (sans accents ni casse,
  chaque nombre réduit à un jeton) ; sous 0,9, trois essais, puis échec signalé.
- Les numéros de rois, siècles et années du calendrier républicain passent par le lexique
  (« Louis XVI » → « Louis seize », « an II » → « an deux ») ; le sous-titre garde la graphie
  du script.
- Les silences de début et de fin de chaque audio sont retirés ; le lecteur ajoute 0,6 s de
  pause entre deux diapositives, et un carton de 2 s avant la première image de chaque acte
  (la voix démarre après). Les deux comptent dans la durée totale (`PAUSE` et `CARTON` dans
  `src/utils/diaporamas.ts`, mêmes valeurs dans `verifier.py`).
- Coût indicatif : ~0,027 $ par minute d'audio produite (Gemini 3.8 Flash TTS), soit
  ~0,9 $ par période de 30 à 35 minutes, transcriptions comprises à quelques centimes près.

## Musique : format et sources

Règle de droits (spec 12) : l'œuvre **et** l'enregistrement doivent être libres. Domaine
public, CC0, CC BY et CC BY-SA admis (crédit affiché, lien vers la licence) ; NC et ND
toujours refusés. **Uniquement de vrais enregistrements** (décision du 2026-10-07) : aucun
rendu MIDI ni partition jouée par ordinateur ; `verifier.py` refuse une source `midi`.
Œuvres composées pendant la période ou peu avant ; compositeurs français d'abord, sinon
européens contemporains (le dire dans `note`). Un arrangement n'est admis que si
l'arrangeur est identifié (étiquette du disque, catalogue) et dans le domaine public.

```json
"musique": {
  "note": "Faute d’enregistrement libre des œuvres françaises de la période, …",
  "fond": [
    { "id": "fond-crise-1", "acte": "crise", "fichier": "musique/fond-crise-1.m4a",
      "titre": "Les Noces de Figaro (d’après Beaumarchais), ouverture",
      "compositeur": "Wolfgang Amadeus Mozart (compositeur autrichien)", "date": "1786",
      "interprete": "Musopen Symphony (enregistrement de 2012)",
      "source": { "type": "commons", "fichier": "File:Mozart - Le nozze di Figaro, K492 - Overture (Musopen Symphony).flac" },
      "licence": "Domaine public (Musopen)", "debut": 0, "volume": 1 },
    { "id": "fond-thermidor-1", "acte": "thermidor", "fichier": "musique/fond-thermidor-1.m4a",
      "titre": "La Rosière républicaine, suite de ballet : Danse légère, Contredanse",
      "compositeur": "André Grétry, suite arrangée par Selmar Meyrowitz (1875-1941)", "date": "1794",
      "interprete": "Grand Orchestre philharmonique de Paris, direction Selmar Meyrowitz (…)",
      "source": { "type": "archive", "id": "78_la-rosiere-republicaine-…", "fichier": "LB_27_CPT_1706-1.flac",
                  "publication": "1935" },
      "licence": "Domaine public en Europe (78 tours publié avant 1963)", "filtres": "78tours", "debut": 0 }
  ],
  "intermedes": [
    { "id": "chant-marseillaise", "apres": 43, "fichier": "musique/chant-marseillaise.m4a",
      "titre": "La Marseillaise", "auteur": "Rouget de Lisle", "date": "1792",
      "interprete": "Georges Thill, ténor, …", "enregistrement": "Columbia, 1931",
      "source": { "type": "commons", "fichier": "File:La Marseillaise Georges THILL….ogg" },
      "licence": "Domaine public", "filtres": "78tours", "debut": 18.8, "fin": 42.7,
      "paroles": [[2.2, "Allons enfants de la Patrie,"], [6.4, "Le jour de gloire est arrivé !"]] }
  ]
}
```

- `source.type` : `commons` (licence relevée par l'API ; pour un fichier « YouTube CC-BY »,
  vérifier sur la vidéo que la chaîne est bien celle de l'interprète) ou `archive` (Internet
  Archive : `id`, `fichier`, `publication` = année de publication du disque, **avant 1963**,
  vérifiée ; licence de l'item ni NC ni ND). Pas d'autre type.
- `note` (facultatif) : phrase affichée sous les crédits (ex. pourquoi des compositeurs
  étrangers).
- `duree` est écrite par `musique.py`. `debut`/`fin` : extrait (s) dans la source.
  `fondu_entree`/`fondu_sortie` (s) : 3 s pour le fond, 0,4 et 1,2 s pour les chants par
  défaut. `filtres: "78tours"` : coupe-bas, coupe-haut, débruitage léger.
- Sonie : fond à -20 LUFS (le lecteur le baisse encore), chants à -16 LUFS (la voix est vers
  -19,5 LUFS). AAC stéréo 96 kb/s (fond), 128 kb/s (chants).
- Fond : 1 à 3 pistes par acte, jouées dans l'ordre depuis le début de l'acte, enchaînées en
  fondu, en boucle si l'acte est plus long. Ne garder (`fin`) que la durée utile de l'acte :
  c'est le gros du poids (~25 Mo par période).
- Intermèdes : 3 à 6 par période, 15 à 25 s, après la diapositive `apres`, dont la narration
  annonce le chant (son titre y figure : `verifier.py` le contrôle) ; le lecteur l'insère
  dans la durée et la barre de progression. `paroles` : `[instant dans l'extrait, vers]`,
  texte exact vérifié sur une source fiable ; pour caler les instants, faire écouter
  l'extrait (une transcription horodatée par Gemini aide, à relire).
- Le lecteur (`Diaporama.astro`) mixe par Web Audio : fond à ~-20 dB sous la voix, ~-10 dB
  dans les respirations, ~-4 dB pendant les cartons d'acte, silencieux pendant un intermède
  (constantes `GAINS`) ; bouton « Musique » (M) et volume mémorisés (localStorage).

Pièges : IMSLP protège ses téléchargements par une vérification anti-robot, que les scripts ne
contournent pas (ses enregistrements libres sont souvent aussi sur Commons). Les fichiers
Commons « Public domain » d'enregistrements des années 1950 (PD-EU-audio) sont admis : publiés
avant 1963, ils sont libres en Europe. Les 78 tours gardent un souffle que le filtre `78tours` atténue sans le
supprimer.

## Lectures d'époque et épisodes

Spec 12, section « Lectures d'époque et épisodes ». Deux listes dans le JSON de la période ;
chaque élément est un segment joué **après la voix** de la diapositive `apres` (comme un
intermède chanté : une seule chose après une diapositive donnée), compté dans la durée, la
barre de progression et les sauts. `voix.py` les synthétise et les horodate, `verifier.py` les
contrôle.

```json
"lectures": [
  { "id": "sieyes", "apres": 6, "date": "1789-01",
    "auteur": { "nom": "Emmanuel-Joseph Sieyès", "dates": "1748-1836", "voix": "homme" },
    "nature": "Pamphlet", "oeuvre": "Qu’est-ce que le tiers état ?", "annee": "janvier 1789",
    "reference": "chapitre premier, …",
    "source": { "page": "Qu’est-ce_que_le_tiers_état_?_(Champion,_1888)/Qu’est-ce_que_le_tiers_état_?",
                "edition": "texte de l’édition de 1888" },
    "ecrivains": "tiers-etat",
    "texte": ["Qui donc oserait dire …", "[…]", "…"],
    "portrait": { "diapositive": 6, "cadre": [0.3, 0.1, 0.78, 0.52] } }
],
"episodes": [
  { "id": "dette", "apres": 2, "titre": "La dette du roi", "date": "1788",
    "narration": "Que pèse cette dette ? …",
    "visuels": [
      { "type": "chiffres", "items": [{ "valeur": "629", "unite": "millions de livres", "libelle": "de dépenses", "quand": "six cent vingt-neuf millions" }], "source": "…" },
      { "type": "barres", "quand": "Le premier poste", "titre": "…", "unite": "millions de livres", "max": 629,
        "barres": [{ "libelle": "Dette", "valeur": 318, "affichage": "318", "note": "la moitié", "quand": "…", "accent": true }], "source": "…" },
      { "type": "carton", "quand": "faire payer les privilégiés", "texte": "Faire payer les privilégiés", "sous": "…" }
    ],
    "sources": ["Compte rendu au roi, mars 1788", "…"] }
]
```

**Lectures.**
- `texte` : paragraphes (strophes : vers séparés par `\n`), copiés **par script** depuis
  Wikisource (outils de `scripts/ecrivains/`, ex. `wikisource.paragraphes(page)`), jamais
  retapés ; une coupure est un élément `"[…]"` seul. Un paragraphe peut commencer ou finir au
  milieu d'une phrase. `verifier.py` télécharge la page publique et cherche chaque paragraphe
  (chaque vers) mot pour mot, comme `npm run verifier:ecrivains`. Reprendre d'abord les extraits
  du chapitre écrivains de la période (`ecrivains` : id de l'extrait, pour mémoire).
- Texte lu (`texte_lu`, `texteLu`) : paragraphes sans les coupures, joints par une espace, vers
  joints par une espace : les positions de caractères sont celles de l'affichage.
- **Minutage mot par mot** (`audio.mots` : `[[début, fin], …]` en secondes, un couple par mot
  de `mots_lus(texte_lu)` / `motsLus(texteLu)` : suites sans espace contenant une lettre ou un
  chiffre ; la ponctuation isolée suit le mot voisin). `voix.py --mots` (et `voix.py` après
  chaque synthèse de lecture) aligne l'audio sur le texte par **alignement forcé CTC** : modèle
  d'alignement français de whisperx (`VOXPOPULI_ASR_BASE_10K_FR`, wav2vec2, ~360 Mo téléchargés
  une fois dans `~/.cache/torch/hub/checkpoints`) et `torchaudio.functional.forced_align`, sans
  la pile transformers de whisperx (elle ne se charge pas dans l'Anaconda de la machine :
  paquets compilés pour numpy 1.x) ; `python3` (Anaconda : torch, torchaudio 2.8) suffit, rien
  à installer ; ailleurs, un venv dans `.cache/` (voir `alignement.py`). Le texte aligné est le
  texte dit (lexique appliqué mot par mot). ~1 s par lecture sur le processeur. Contrôle sur le
  pilote (6 lectures) : écart médian de 0,03 à 0,04 s avec les instants de mots de
  faster-whisper `medium`, 90 % sous 0,12 s. `verifier.py` contrôle un couple par mot, dans
  l'ordre et dans la durée de l'audio ; sans `audio.mots` (avertissement), le lecteur situe
  chaque mot au prorata des caractères dans sa phrase horodatée.
- **Carte de citation** (lecteur, « journal télévisé ») : fond = image de la diapositive
  `apres`, floue, en gris, voilée ; portrait grand à gauche (couleur atténuée, entrée en fondu
  glissé) ; grand guillemet ouvrant ; texte en gros révélé **mot par mot au rythme de la voix**
  (mot en cours noir, mots lus gris foncé, suivants invisibles mais à leur place ; défilement
  doux si le texte dépasse) ; bandeau inférieur (nom, dates, nature, *œuvre*, année, crédit du
  portrait). Mouvement réduit : apparition par phrase. Téléphone : portrait en vignette au-dessus.
- Voix de lecture (`VOIX_LECTURE` dans `voix.py`, ou `DIAPORAMAS_VOIX_LECTEUR` /
  `DIAPORAMAS_VOIX_LECTRICE`) : `Schedar` (homme) et `Aoede` (femme), **choix provisoire** ;
  essais à écouter dans `.cache/diaporamas/essais-voix-lecture/`. Changer de voix change
  l'empreinte : `voix.py` refait les lectures concernées.
- `portrait` : `diapositive` (image d'une diapositive, recadrée sur `cadre`, le visage) ou
  `commons` (fichier propre, licence relevée par `images.py`, `lectures/<id>.webp`, 640 px).
  Sans portrait, la carte montre l'initiale.
- Durée visée : 20 à 40 s (60 à 100 mots environ).

**Épisodes.**
- `narration` : mêmes règles que les diapositives (phrases de 25 mots au plus, ni parenthèses ni
  abréviations, chiffres prudents), voix du narrateur ; 45 s à 1 min 30 (120 à 200 mots).
  Attention : une phrase qui finit par une citation (`… capital. »`) n'est pas coupée avant la
  suivante (même découpage que la caméra).
- `visuels` : le premier commence avec l'épisode, les suivants à leur `quand` (passage exact
  de la narration, première occurrence) ; à l'intérieur, chaque élément a son `quand` ou entre
  en cascade. Types : `carton` (`texte`, `sous`), `chiffres` (`items` : `valeur`, `unite`,
  `libelle`, `accent`), `barres` (`max`, `barres` : `valeur`, `affichage`, `note`, `accent`),
  `courbe` (`points` [date ISO, valeur], `ymax`, `reperes` : `date` d'un point, `libelle`,
  `etiquette` [dx, dy], `ancre` ; le tracé atteint chaque repère quand la voix le nomme),
  `carte` (`fond`, `elements` : `ville` (`lieu` [lon, lat], `capitale`, `rebelle`, `position`),
  `fleche` (`de`, `a`), `zone` (`points`), `legende`), `document` (`image` Commons, licence
  relevée par `images.py`, `episodes/<id>.webp` en 2 400 px ; `lignes` : `cadre` [x0, y0, x1, y1]
  de la ligne dans l'image, `texte` exact relevé sur le fac-similé, `quand`).
- Chiffres, graphiques et cartes portent une `source` (affichée sous le visuel) ; `sources` de
  l'épisode : affichées dans le livre d'images.
- Fonds de carte : `carte.py` (Natural Earth 1:50 m, domaine public ; projection
  équirectangulaire corrigée, cadre et fleuves dans `FONDS`). Les éléments sont donnés en
  [longitude, latitude].

**Lecteur.** Carte de citation (`CarteCitation.astro`) et panneaux (`EpisodeVisuels.astro`)
sont rendus au build, cachés sur la scène ; le lecteur les montre après la voix, règle leurs
animations sur `currentTime` du lecteur de segments (variable CSS `--p` de chaque élément), et
les retire au saut suivant. Musique baissée comme sous la voix. Un clic dans la barre de
progression sur la part d'un segment y mène directement. Le livre d'images (sans JavaScript)
montre les cartes et les visuels, statiques, avec les sources. Pour les tests :
`document.querySelector('.diaporama').__aller(n, true)` saute au segment de la diapositive `n`.
