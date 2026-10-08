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
- Paroles des chants calées au mot (`paroles.py`) : **torch / torchaudio** (comme `alignement.py` ;
  séparation de la voix par Hybrid Demucs de torchaudio, ~320 Mo téléchargés une fois),
  **soundfile**, et **matplotlib** pour les planches de contrôle.
- `GEMINI_API_KEY` dans `.env` à la racine (fichier non versionné).

Les commandes se lancent depuis la racine du projet.

**Renumérotation.** Les états de `.cache/diaporamas/<slug>/` (images, voix, caméra) sont indexés
par numéro de diapositive ; après une insertion, `renumeroter.py` les réindexe en même temps que
les fichiers, si bien que `voix.py` ne resynthétise que les narrations nouvelles ou retouchées
(l'empreinte du texte fait foi). Ne jamais renommer `NNN.webp` / `NNN.m4a` à la main.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `commun.py` | Bibliothèque commune : chemins, lecture/écriture du script JSON, API Commons, licences, lexique. |
| `images.py` | Métadonnées et licence (API Commons), téléchargement, WebP 1600 px, vignette du portail ; portraits des lectures et fac-similés des épisodes. Aide à la recherche (`--chercher`, `--infos`). |
| `voix.py` | Synthèse Gemini (narrateur Charon ; voix de lecture pour les lectures d'époque), contrôle de fidélité, encodage m4a, durées, horodatage des phrases ; minutage mot par mot des lectures (`--mots`). Diapositives, lectures et épisodes. |
| `alignement.py` | Alignement forcé d'un audio de lecture sur son texte (wav2vec2 français, torchaudio) : instants de chaque mot. Appelé par `voix.py`. |
| `camera.py` | Caméra calée sur la narration : étapes `image.camera` proposées par Gemini Flash (vision), contrôlées, planche-contact. |
| `utile.py` | Zone utile `image.utile` de chaque image (sans liseré, marge de papier, cadre ni légende gravée) : analyse des bords (numpy) et contrôle par Gemini Flash, planche de contrôle. |
| `musique.py` | Musique : enregistrements libres (Commons, Internet Archive), licences, découpe, fondus, sonie, m4a. |
| `carte.py` | Fonds de carte (Natural Earth, domaine public) des épisodes et des médaillons de lieu : `src/data/diaporamas/fonds/<nom>.json` (`france`, `voisins`, `europe`, `monde`) ; plans de Paris d'époque calés (`public/diaporamas/fonds/<nom>.webp`, `src/data/diaporamas/plans/<nom>.json`). |
| `surimpressions.py` | Cartes de lieu, citations et portraits en surimpression : instants calés sur la voix (alignement des mots de la narration) ; `--relever` liste les passages entre guillemets. |
| `portraits.py` | Portraits des personnes nommées : recherche assistée (Wikidata, Commons), registre `portraits.json` (licence par l'API, téléchargement avec cache, cadre du visage proposé par Gemini Flash puis contrôlé, webp ovale), contrôle de visibilité des personnes sur les images, planche de contrôle. |
| `ajouter_lieux.py` | Ajout idempotent des lieux des médaillons à plusieurs lieux de la Révolution (données en dur, coordonnées Wikidata) ; `--fichier` pour une copie, `--essai` pour voir sans écrire. |
| `renumeroter.py` | Insertion de diapositives et renumérotation : fichiers, renvois par numéro et états du cache recalculés, sans resynthèse. |
| `verifier.py` | Contrôle d'une période avant publication (110 à 130 diapositives depuis la révision « Arts et techniques »). |
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
# Seulement les diapositives dont la caméra tient plus de 7 s un même cadre
python3 scripts/diaporamas/camera.py revolution --tenues

# Musique : ce qui manque ou a changé ; --force pour tout refaire ; --sources pour
# télécharger et contrôler les licences seulement
python3 scripts/diaporamas/musique.py revolution
python3 scripts/diaporamas/musique.py revolution --piste chant-marseillaise
python3 scripts/diaporamas/musique.py revolution --sources

# Paroles des intermèdes chantés calées au mot (après musique.py) ; --ecoute : écoute ciblée par
# Gemini ; --essai : n'écrit rien ; --chant <id> : un seul chant. Relire les planches ensuite.
python3 scripts/diaporamas/paroles.py revolution --ecoute

# Lectures et épisodes : voix (tout ce qui manque ou a changé, ou un segment précis)
python3 scripts/diaporamas/voix.py revolution --segments lecture:sieyes episode:dette
# Lectures : minutage mot par mot des audios existants (fait aussi après chaque synthèse de
# lecture) ; --segments lecture:<id> pour une seule
python3 scripts/diaporamas/voix.py revolution --mots
# Fonds de carte (épisodes, médaillons de lieu) et plans de Paris d'époque ; --plans : plans seuls
python3 scripts/diaporamas/carte.py
# Cartes de lieu et citations : instants calés sur la voix (après voix.py) ; --relever : aide
python3 scripts/diaporamas/surimpressions.py revolution
python3 scripts/diaporamas/surimpressions.py revolution --relever
# Médaillons à plusieurs lieux de la Révolution (idempotent), puis instants des lieux nouveaux
python3 scripts/diaporamas/ajouter_lieux.py && python3 scripts/diaporamas/surimpressions.py revolution

# Portraits des personnes nommées : recherche, registre, visibilité, bilan (voir « Portraits »)
python3 scripts/diaporamas/portraits.py --chercher "Charles Alexandre de Calonne"
python3 scripts/diaporamas/portraits.py --registre            # tout le registre (--id x y, --force)
python3 scripts/diaporamas/portraits.py revolution --visibilite
python3 scripts/diaporamas/portraits.py revolution --relever

# Insérer des diapositives (groupes {"apres": n actuel, "diapositives": […]}) et tout renuméroter ;
# --essai affiche la correspondance sans rien écrire. Puis images.py, voix.py, camera.py.
python3 scripts/diaporamas/renumeroter.py revolution --inserer ajouts.json --essai

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
5. `utile.py <slug>`, puis relire la planche de contrôle (`.cache/diaporamas/<slug>/utile-*.jpg`)
   et corriger à la main les zones fausses (voir « Zone utile » ci-dessous).
   `camera.py <slug>`, puis relire les planches-contact (`.cache/diaporamas/<slug>/planche-*.jpg`)
   et corriger à la main les cadres faux (voir ci-dessous).
6. Musique : écrire `musique` dans le JSON (voir ci-dessous), lancer `musique.py <slug>`,
   écouter les extraits, ajuster `debut`/`fin` et les paroles, puis `paroles.py <slug> --ecoute`
   et relire ses planches (voir « Paroles des chants » ci-dessous).
7. Cartes de lieu, citations et portraits : remplir `lieux`, `citations`, `personnes` et `personnes_vues` (voir ci-dessous ; `portraits.py` pour le registre et la visibilité), lancer
   `surimpressions.py <slug>` (à relancer après toute nouvelle voix).
8. `verifier.py <slug>` puis `npm run build`.

## Cartouches et graphiques

- `image.titre_court` (60 caractères au plus) : titre rédigé du cartouche du lecteur (trois
  lignes : titre court, auteur, « date · technique ») ; le titre officiel `image.titre` reste
  dans le livre d'images et l'`alt`. Pour un titre déjà court, le recopier.
- `cartouche: { oeuvre, compositeur }` dans chaque piste de fond et chaque intermède, rédigé à
  la main (« Symphonie nº 87, menuet » / « Joseph Haydn, 1785 ») : deux lignes, sans troncature.
- Courbes d'épisode : `unite` est dite une fois sous le titre ; chaque repère est étiqueté
  automatiquement « date · valeur en clair » (`unite_point`, ou `libelle` rédigé en clair comme
  « moins d'une demi-livre »), placé sans toucher la courbe ni les axes ; le dernier point a son
  repère. `verifier.py` contrôle ces trois points.

## Zone utile : format et pièges

- `image.utile` : `[x0, y0, x1, y1]` (fractions de l'image **servie**, après `recadrage`), la partie
  qui est l'œuvre. Le lecteur ne montre jamais rien en dehors (spec 12, « Sans bordures ») :
  l'image est agrandie pour que la zone couvre la scène (pas de bandes, même en plein écran 16/9 ou
  16/10), et tous les cadres (caméra, ouverture, intermède), qui restent exprimés dans l'image
  entière, sont convertis dans la zone et ramenés dedans (déplacés s'ils y tiennent, sinon réduits
  à leur partie commune : `versUtile` dans `src/utils/diaporamas.ts`).
- `utile.py <slug>` : (1) analyse des bords : depuis chaque bord, les lignes « de bord » sont
  retirées (bande unie et neutre : étendue des gris sous 10, saturation faible ; ou papier clair :
  moyenne au-dessus de 140, étendue sous 24, saturation sous 80) ; un trait fin (cuvette, filet)
  suivi de papier est franchi ; 30 % au plus par côté. Un fond peint sombre ou un ciel n'est pas
  un bord. (2) Gemini Flash voit l'image avec une grille et rend le rectangle de l'œuvre sans marges,
  cadre, ni légende gravée ou imprimée. On garde l'intersection des deux (la plus prudente), plus
  une garde de 0,4 % sur les côtés rognés ; une zone de moins de 50 % de l'image ou un bord rentré
  de plus de ~30 % est refusé (repli sur l'autre proposition, ou l'image entière).
- **Relire la planche** : les refus concernent souvent des estampes à grande marge et légende
  (portrait en médaillon au-dessus d'un cartouche gravé), dont la vraie zone fait 30 à 45 % de
  l'image ; on la saisit à la main. Pièges vus sur la Révolution : un dessin au trait sur fond
  blanc (la planche technique de la guillotine) pris pour du papier, des gouttes de sang sur une
  marge claire coupées, un objet photographié sur fond de studio (le fond fait partie de la photo :
  zone entière), un médaillon rond (on garde le rectangle de la scène, coins de papier compris).
- **Correction à la main** : écrire `utile` et ajouter `"utile_manuel": true` dans `image` ;
  `utile.py` ne la touchera plus. Cache : `.cache/diaporamas/<slug>/utile.json` (empreinte du
  fichier servi et de `VERSION`).
- Coût : un appel par image, ~0,35 $ pour 127 images (tarif Gemini Flash supposé).
- `verifier.py` contrôle la présence et la validité de `utile` (25 % de l'image au moins ; moins de
  50 % sans `utile_manuel` : avertissement) et que chaque cadre (caméra, ouverture, intermède) est
  dans la zone à 50 % au moins (avertissement sous 75 % ; la vue d'ensemble `[0, 0, 1, 1]` est
  toujours admise).

## Caméra : format et pièges

- `image.camera` : 1 à 4 étapes `{"cadre": [x0, y0, x1, y1], "quand": "passage exact"}`, en
  fractions de l'image **servie** (le WebP, donc après `recadrage`). La première étape n'a pas
  de `quand`. Le lecteur situe chaque passage au prorata dans sa phrase horodatée
  (`audio.phrases`).
- **Rendu calme** (spec 12, « Caméra calme et lente » ; `plan`, `profil`, `trajet`, `souffle`
  dans `Diaporama.astro`) : le lecteur **ignore** une étape dont le passage suit le précédent
  retenu (ou le début) de moins de 5 s, une étape dont la vue diffère à peine de la précédente
  (zoom et déplacement sous 0,12) et une étape dont la transition ne tient plus avant la fin de
  la voix ; les données restent intactes. Transition : durée selon l'ampleur (3 à 6 s, plus pour
  un long glissement le long d'une image très large), vitesse plafonnée (0,22 en log d'échelle
  par seconde, 0,3 scène par seconde au plus fort), arrivée visée 1 s après le passage (plus
  tard si le plafond l'impose) ; zoom logarithmique couplé au déplacement (homothétie : pas
  d'arc) ; vitesse constante entre une mise en route et un arrêt doux. `__camera(n, t)` donne
  aussi les étapes retenues (`plan`, `effectives`) pour les tests.
- `image.ouverture` (première diapositive d'un acte seulement, saisi à la main) : détail
  `[x0, y0, x1, y1]` (un visage, un geste, un objet) sur lequel s'ouvrent les volets du carton
  d'acte, avant un recul de 5 s vers le premier cadre. Le cadrer au rapport ~2,4:1 en pixels et
  sur ~40 % de la largeur de l'image (zoom ×2 au moins sur ordinateur, sans flou). Instants
  négatifs de `__camera(n, t)` (−3,5 à 0) : l'ouverture, avant la voix.
- **Tenues longues** : une tenue de plus de 7 s sur un même cadre déclenche une relance du
  modèle (texte dit pendant la tenue à l'appui) pour une étape de plus, seulement si la voix
  nomme alors un élément visible. Sinon, le lecteur fait « respirer » l'image : resserrement à
  sens unique de 4 % au plus (0,5 % par seconde au plus), glissement d'un tiers de la marge,
  arrêt doux en fin de tenue. `camera.py` refuse désormais, dès la proposition du modèle, un
  passage à moins de 5 s du précédent et un micro-déplacement (contrôles hors empreinte : les
  caméras en cache ne sont pas recalculées).
- Le lecteur montre le cadre en entier **sous le cartouche** (en haut à gauche) et, en plein
  écran, au-dessus des bandeaux du bas ; un cadre trop haut pour l'écran est montré depuis son
  bord supérieur (on garde les têtes). L'image couvre toujours toute la scène : un grand cadre
  peut donc passer en partie sous le cartouche. Les zones couvertes sont **constantes pendant une
  diapositive** : la place du médaillon de lieu est réservée pour toute la diapositive qui en a un
  (une zone qui varie en cours de route faisait bouger la caméra d'un coup).
- **Horloge lissée** : la caméra et les surimpressions suivent `audio.currentTime` lissé
  (`HorlogeLissee` dans `Diaporama.astro`) : entre deux mises à jour de l'audio, l'instant avance
  avec `performance.now()` × `playbackRate` ; l'écart est résorbé en modulant la vitesse de ±5 % au
  plus ; jamais de recul ni de saut ; en pause, après un saut ou au départ, l'instant de l'audio
  exactement. `__instant()` donne l'instant lissé et brut (tests).
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
  `filtres: "microsillon"` (premiers 33 tours, années 1950) : coupe-bas doux, craquements ôtés
  (`adeclick`), souffle à peine réduit, sans coupe-haut. Les fichiers des microsillons de
  l'Internet Archive (`lp_…`, `disc1/…`) portent une image de pochette : `musique.py` l'ignore (`-vn`).
- Sonie : fond à -20 LUFS (le lecteur le baisse encore), chants à -16 LUFS (la voix est vers
  -19,5 LUFS). AAC stéréo 96 kb/s (fond), 128 kb/s (chants).
- Fond : 1 à 3 pistes par acte, jouées dans l'ordre depuis le début de l'acte, enchaînées en
  fondu, en boucle si l'acte est plus long. Ne garder (`fin`) que la durée utile de l'acte :
  c'est le gros du poids (~25 Mo par période).
  Aucun morceau ne doit boucler dans un acte (retours du 2026-10-07) : `verifier.py` avertit quand
  un acte dure plus que ses pistes enchaînées (fondus de 3 s déduits) ; allonger `fin` ou ajouter
  une piste.
- Intermèdes musicaux (spec 12, « Arts et techniques ») : 1 ou 2 par période, en plus des chants,
  après une diapositive qui présente une œuvre instrumentale ; `"instrumental": true` et
  `"paroles": []` : le lecteur masque le sous-titre et le livre d'images dit « Intermède musical ».
- Intermèdes : 3 à 6 par période, 15 à 25 s, après la diapositive `apres`, dont la narration
  annonce le chant (son titre y figure : `verifier.py` le contrôle) ; le lecteur l'insère
  dans la durée et la barre de progression. `paroles` : `[instant dans l'extrait, vers]`,
  texte exact vérifié sur une source fiable et **tel qu'il est chanté sur l'enregistrement**
  (couplets et reprises réellement chantés) ; pour caler les instants, faire écouter
  l'extrait (une transcription horodatée par Gemini aide, à relire), puis `paroles.py` cale
  chaque mot (section suivante).

### Paroles des chants calées au mot (`paroles.py`, 2026-10-08)

Format (compatible avec l'ancien) : `"calage": "mot"` et chaque vers devient
`[début du vers, vers, [[début, fin], …]]`, un couple par mot de `commun.mots_lus(vers)` (la
ponctuation suit le mot) ; le début du vers est celui de son premier mot. Repli (`"calage":
"vers"`) : `[début, vers]` seulement, le lecteur montre le vers entier en fondu à son début.

Méthode : voix isolée par séparation de sources (Hybrid Demucs, `HDEMUCS_HIGH_MUSDB_PLUS` de
torchaudio, sur le fichier joué : mêmes instants), puis alignement forcé wav2vec2 (alignement.py)
du texte entier sur tout l'extrait, sur la voix isolée et, pour contrôle, sur le mélange.
Contrôles : mots dans l'ordre, durées de 0,05 à 4 s, dans l'extrait ; écart voix isolée / mélange
au-delà de 0,35 s signalé ; `--ecoute` : Gemini transcrit chaque vers découpé selon le calage et sa
première moitié (signalé, pas bloquant : sur des découpes de 1 à 2 s, il invente parfois). Planche
(spectrogramme de la voix, une rangée par 8 s, débuts des mots en traits pleins, ceux du mélange en
pointillés) : `.cache/diaporamas/<slug>/paroles/<id>.png`.

Corrections après relecture (dans l'intermède) : `calage_fenetres` (une fenêtre `[t0, t1]` par
vers, ou `null`) quand l'alignement d'ensemble avale une note tenue et glisse un mot dans le vers
suivant ; `calage_retouches` (`[[vers, mot, début], …]`, rangs à partir de 1) pour un mot faux ;
`calage_force: "vers"` impose le repli.

Pièges : sur le chant, wav2vec2 (entraîné sur la parole) place bien les consonnes d'attaque mais
peut avaler une longue note tenue (le mot suivant part trop tôt) ; relire chaque mot sur la planche
en suivant la mélodie (une syllabe par note, notes tenues sur les temps forts), et départager à
l'oreille (whisper large-v3 sur la voix isolée ou Gemini sur une découpe) quand voix isolée et
mélange divergent. Whisper seul hallucine sur certains 78 tours (« Sous-titrage MFP » pour la
Marseillaise) : il ne sert qu'au contrôle.
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

## Cartes de lieu et citations en surimpression

Spec 12, « Cartes de lieu et citations en surimpression » (2026-10-07). Toujours actives dans le
lecteur ; rien dans le livre d'images.

```json
{ "n": 56, "narration": "Le 20 septembre 1792, à Valmy, …",
  "lieux": [{ "nom": "Valmy", "quand": "à Valmy", "lon": 4.76737, "lat": 49.07972, "fond": "france", "instant": 1.5 }],
  "citations": [{ "texte": "De ce lieu et de ce jour date une nouvelle époque de l'histoire du monde.",
                  "auteur": "Goethe", "mots": [[16.82, 16.95], …] }] }
```

**Lieux** (un médaillon au plus par diapositive, 1 à 5 lieux) : villes, régions, champs de bataille et lieux de
Paris, à leur première mention dans la période (pas à chaque « à Paris ») ; ~40 à 50 par période.
- `quand` : passage exact de la narration ; le médaillon (en bas à droite, ~5 s) entre quand la
  voix l'attaque (`instant`, écrit par `surimpressions.py` ; à défaut, prorata des phrases). Un
  lieu dit dans les toutes dernières secondes est montré un peu plus tôt pour rester ~4 s.
- `lon`, `lat` : coordonnées vérifiées (Wikidata, propriété P625, plutôt que de mémoire ; pour
  un édifice disparu, sa position relevée sur le plan d'époque, ex. la forteresse de la
  Bastille, 48,8532 N, 2,3680 E, à l'ouest de l'actuelle colonne).
- `fond` : `france` (lieu en France), `voisins` (Belgique, Rhénanie, Italie du Nord : Fleurus,
  Arcole, Campo-Formio), `europe` (Égypte, Russie, Algérie), `monde` (Antilles, Guyane, Afrique
  de l'Ouest), `paris` (plan d'époque zoomé sur ~2 km). La France est toujours repérée.
  `verifier.py` contrôle le cadre (et avertit d'un lieu en France sur un autre fond).
- Plans de Paris : `PLANS` dans `carte.py` (fichier Commons, recadrage, points de calage) ; un plan
  sert les périodes de son champ `slugs`. Calage : 6 à 10 monuments repérés sur l'original
  (pixels lus sur des agrandissements quadrillés) et leurs coordonnées Wikidata, transformation
  affine par moindres carrés ; `carte.py` affiche l'écart (Verniquet 1790 : ~15 m en moyenne,
  29 m au plus). Le crédit (« Plan de Verniquet, 1790 ») est dans le médaillon. Image servie :
  2 000 px, gris, papier blanchi, ~440 Ko, chargée à la première diapositive qui en a besoin.

**Plusieurs lieux sur une diapositive** (révision du 2026-10-08) : quand la voix nomme plusieurs
lieux utiles sur un même écran (départ des Tuileries et arrestation à Varennes ; Lyon, Marseille,
Bordeaux, Toulon…), `lieux` en porte jusqu'à 5, **dans l'ordre de la narration** (chaque `quand`
est cherché après le début du précédent : « de Dunkerque à Barcelone » puis « à Barcelone »).
- Un seul médaillon, au **cadre calculé** (`medaillonMultiple`, `src/utils/diaporamas.ts`) : les
  points occupent au plus 60 % du cadre (le reste est la marge des noms), rapport 4/3. Tous les
  lieux à Paris : le plan d'époque recadré sur eux (2 km de large au moins). Sinon : le fond SVG
  le plus large demandé (`france` < `voisins` < `europe` < `monde`), élargi si un point en sort,
  recadré sans descendre sous 45 % de sa largeur (la France reste reconnaissable) ; un lieu de
  Paris y devient le point « Paris » (un seul : deux lieux de Paris s'y confondraient). Dans les
  données, un lieu de Paris mêlé à la province s'écrit d'ailleurs `nom: "Paris"`, `fond: "france"`.
- Chaque point paraît avec son nom quand la voix le dit (`instant` de chaque lieu), les précédents
  restent, le dernier pulse ; le médaillon s'ouvre au premier nom et reste ~3 s après le dernier
  (5 s au moins). Pas de nom sous la carte : les noms sont posés sur la carte, sans chevauchement
  (à droite, à gauche, au-dessus, en dessous, en biais, puis plus loin avec un filet fin).
- Rendu : le lecteur (`Diaporama.astro`) pose le fond, la fenêtre et la zone couverte comme pour un
  lieu seul ; `Surimpressions.astro` ajoute points et noms d'après l'instant de l'audio (pause,
  reprise et sauts justes), et refait la disposition des noms quand le médaillon change de taille.
- `verifier.py` : 5 lieux au plus, passages dans l'ordre, instants croissants, fond cohérent
  (fond élargi signalé, deux lieux de Paris sur une carte plus large refusés), points dans le
  cadre calculé, avertissement si deux points se touchent.

**Citations** : chaque citation courte (≈ 20 mots, 25 au plus) attribuée à une personne et dite
entre « » ; pas les cris d'une foule ni les titres d'œuvres. `texte` : sous-chaîne exacte de la
narration, sans les guillemets (attention aux espaces insécables avant `? ; ! :` du texte) ;
`prudence: true` quand la narration dit « aurait dit », « dit-on » : l'attribution devient
« — attribué à … ». Les mots s'inscrivent un à un au rythme de la voix (`mots`, alignement), le
sous-titre est masqué, l'auteur paraît après le dernier mot ; la citation reste ~2 s. Quand elle
finit la narration, la pause après la voix est allongée d'autant (max(0,6 s, fin du dernier mot
+ 2 s − durée de la voix), `pauseApres` / `pause_apres`), comptée dans la durée totale, la barre
de progression et l'enchaînement ; la citation s'efface en fondu avec l'image. Mouvement réduit :
la citation entière d'un coup.

**Arbitrage** (fait au build, `surimpressionsDe` dans `src/utils/diaporamas.ts`) : une citation et
un médaillon ne se montrent jamais ensemble ; le médaillon passe après la citation s'il reste
~3 s, sinon avant s'il tient ~2,5 s, sinon il est omis. Le médaillon est une zone couverte pour
la caméra (prise et rendue en ~0,9 s) ; sur téléphone, il masque le temps de son passage le
cartouche de la musique (même coin) ; il monte au-dessus de la frise quand elle s'affiche.

**Chaîne** : `surimpressions.py <slug>` aligne chaque narration concernée (texte dit, lexique
compris, modèle d'alignement des lectures, ~0,5 s par diapositive), écrit `instant` et `mots`, et
garde en cache (`.cache/diaporamas/<slug>/surimpressions.json`) les instants des mots avec
l'empreinte de l'audio : après une nouvelle voix, `verifier.py` signale les instants périmés.

## Portraits des personnes nommées

Spec 12, « Portraits des personnes nommées » (2026-10-08). Toujours actifs dans le lecteur ; rien
dans le livre d'images.

```json
{ "n": 125, "narration": "Lucien fait entrer les grenadiers, … trois consuls : Bonaparte, Sieyès et Roger Ducos. …",
  "personnes": [{ "id": "lucien-bonaparte", "quand": "Lucien", "instant": 0.2 },
                { "id": "sieyes", "quand": "Sieyès", "instant": 8.53 },
                { "id": "roger-ducos", "quand": "Roger Ducos", "instant": 9.57 }],
  "personnes_vues": [{ "id": "bonaparte", "quand": "Bonaparte" }] }
```

**Relevé** (à la main, dans l'ordre de la narration) : chaque mention d'une personne par son nom
(« Robespierre », « le duc de Brunswick », « Lucien » ; pas « le roi » ni « la reine ») ; `quand` =
le nom tel qu'il est dit, cherché après le précédent (une personne nommée deux fois a deux
mentions). Les personnages antiques ou légendaires sujets d'une œuvre (Brutus, les Horaces,
Hersilie) et les titres de chants (« Ô Richard ») ne comptent pas.
- `personnes` : la personne **n'est pas visible** sur l'image ; `personnes_vues` : elle l'est (pas
  de portrait ; gardé pour mémoire et pour `verifier.py`). « Visible » = représentée de façon
  reconnaissable : sujet de l'œuvre, figure nettement identifiable (titre, légende gravée,
  composition), ou œuvre dans l'œuvre (portrait sur un chevalet, buste) ; une silhouette
  indistincte dans une foule, un cercueil, une œuvre de la personne ne comptent pas.
- `portraits.py <slug> --visibilite` : Gemini Flash voit l'image, sa notice et la narration, et dit
  pour chaque personne nommée si elle est visible ; le script liste les désaccords avec les
  données, à trancher en regardant l'image (cache `.cache/diaporamas/<slug>/personnes.json`).
  Sur la Révolution, deux verdicts du modèle ont été renversés après relecture : Calonne (2 : le
  médaillon de l'estampe n'est pas identifié) et Barras (111 : un des cinq directeurs, indistinct).
- `citations[].personne` : l'identifiant de la personne citée ; si elle n'est pas visible, elle doit
  être dans `personnes` (son portrait accompagne la citation).

**Registre** `src/data/diaporamas/portraits.json` (commun à toutes les périodes ; seules les
personnes montrées au moins une fois y sont) : `{ id, nom, dates, commons, page, fichier, auteur,
date, licence, cadre_visage }`. `nom` est le nom affiché (court : « Danton », « Madame Roland »,
« Comte d'Artois »), `dates` « 1759-1794 ».
- Choix du portrait : œuvre **d'époque**, faite du vivant de la personne ou peu après, **identifiée
  sans doute** (notice du musée, titre explicite ; jamais un « portrait présumé »), domaine public ou
  CC0 sur Commons (la licence est relevée par l'API ; CC BY refusé). `--chercher` aide : entité
  Wikidata (dates, image P18 avec sa notice Commons) puis recherche Commons. Préférer une peinture
  en couleur à une gravure, un original à une copie ; une copie d'un portrait d'après nature est
  admise en le disant dans `auteur` (« Copie d'après Joseph-Marie Vien (original avant 1809) »).
- `auteur` et `date` sont rédigés pour les crédits (les champs Commons sont souvent bruts).
- **Sans portrait fiable** : l'entrée garde `id`, `nom`, `dates` et une `note` (pourquoi), sans
  `commons` ni `fichier` ; le lecteur ne montre rien. Révolution : Réveillon, Méchain, Amar,
  Lagrange, Claude Chappe, Pussin (voir leurs notes).
- `portraits.py --registre` : licence par l'API (refus sinon), original téléchargé dans
  `.cache/diaporamas/portraits/` (vignette de 2 400 px pour un très grand fichier), cadre du
  visage proposé par Gemini Flash sur l'image quadrillée, recadrage 4:5 où le visage occupe 58 % de
  la hauteur (son centre à 44 %), contrôle du recadrage par le modèle (« un seul visage entier,
  centré ») ; webp 240 × 300 px, ~10 Ko. Un refus est signalé « à relire » : corriger
  `cadre_visage` à la main et ajouter `"cadre_visage_manuel": true` (Révolution : Drouet, Nelson,
  Couthon). Planche de contrôle : `.cache/diaporamas/portraits/planche.jpg` (ovales et noms).
- Coût (Gemini Flash, tarif supposé) : ~0,12 $ pour la visibilité des 135 mentions de la
  Révolution, ~0,15 $ pour les cadres et contrôles de 48 portraits.

**Instants** : `surimpressions.py <slug>` écrit `instant` (début du nom dans l'audio) comme pour les
lieux ; à relancer après toute nouvelle voix.

**Lecteur** (`portraitsDe` dans `src/utils/diaporamas.ts`, `Diaporama.astro`, styles dans
`Surimpressions.astro`) :
- rangée d'ovales **en bas à gauche** (le médaillon de lieu est en bas à droite), en couleur, bord fin
  (filet sombre et liseré clair), nom en petites capitales et dates dessous ; une personne seule :
  « Danton · 1759-1794 » sur une ligne ;
- une personne par ovale, dans l'ordre de la première mention, **4 au plus** ; chaque ovale paraît
  au nom (le premier dès l'entrée de la rangée), les précédents restent ; la rangée va du premier
  nom à 3 s après le dernier (5 s au moins ; un nom dit dans les 4 dernières secondes avance son
  entrée), prolongée jusqu'à la fin de la citation de la personne ;
- taille : ovales de 17 % de la hauteur de la scène (78 à 118 px de haut sur ordinateur, 50 sur
  téléphone), réduits si la rangée ne tient pas à côté du médaillon de lieu ;
- zone couverte pour la caméra : la hauteur de la rangée est réservée **pour toute la diapositive**
  qui en a une (comme le médaillon de lieu) ; tous les ovales sont posés d'emblée (invisibles), la
  rangée ne change jamais de taille ;
- affichage dérivé de l'instant lissé de l'audio (pause, reprise, sauts justes) ; mouvement réduit :
  fondu simple de 200 ms, sans glissement ;
- **surimpressions ensemble**, par ordre de priorité : citation > portraits = médaillon de lieu >
  frise du temps. La citation exclut déjà le médaillon (arbitrage existant) ; avec des portraits,
  si elle touche la rangée, elle monte au-dessus d'elle pour toute la diapositive (rien ne bouge
  pendant la lecture) ; la frise du temps cède (masquée) quand médaillon et portraits sont là
  ensemble, et sinon les portraits montent au-dessus d'elle comme le médaillon ; sur téléphone, le
  cartouche de la musique (même bande du bas) s'efface le temps des portraits ;
- crédits : section « Portraits » de la page (nom, dates, auteur, date, lien Commons, licence).

`verifier.py` : registre (champs, fichier présent, licence, cadre du visage, œuvre postérieure de
plus de 5 ans à la mort signalée), `quand` exacts et dans l'ordre, instants présents, croissants,
dans l'audio et à jour, 4 portraits au plus, personne montrée absente de l'image (jamais dans
`personnes_vues` de la même diapositive ; désaccord avec le cache de vision en avertissement),
personne citée accompagnée de son portrait.
