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
- Détourage des objets de musée (`objets.py`) : **rembg** dans un venv ignoré par git,
  `python3 -m venv .cache/venv-rembg && .cache/venv-rembg/bin/pip install "rembg[cpu]" pillow`
  (modèle `isnet-general-use`, ~180 Mo, téléchargé au premier usage dans `~/.rembg/models`) ; et
  **scipy** (Anaconda) pour l'enveloppe convexe.
- Visages locaux (`camera.py`, 2026-10-09) : **OpenCV** dans un venv ignoré par git,
  `python3 -m venv .cache/venv-visages && .cache/venv-visages/bin/pip install opencv-python-headless numpy`,
  et le modèle YuNet (230 Ko) dans `.cache/modeles-visages/yunet.onnx` (adresse dans `visages_local.py`).

Les commandes se lancent depuis la racine du projet.

**Renumérotation.** Les états de `.cache/diaporamas/<slug>/` (images, voix, caméra) sont indexés
par numéro de diapositive ; après une insertion, `renumeroter.py` les réindexe en même temps que
les fichiers, si bien que `voix.py` ne resynthétise que les narrations nouvelles ou retouchées
(l'empreinte du texte fait foi). Ne jamais renommer `NNN.webp` / `NNN.m4a` à la main.
Depuis le 2026-10-12, il met aussi à jour les annotations de visionnage `docs/annotations/<slug>.jsonl` :
`lieu.n` et `ecran.image.fichier` passent au nouveau numéro, un champ `renumerote` (« diapositive 22 devenue 23 … »)
garde le numéro d'origine ; l'identifiant et la capture ne changent pas ; `--essai` liste les annotations concernées.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `commun.py` | Bibliothèque commune : chemins, lecture/écriture du script JSON, API Commons, licences, lexique. **Écriture sûre** (2026-10-09) : `ecrire` prend un verrou (`.cache/diaporamas/verrous/`), relit le disque et n'y reporte que les champs changés par le script depuis sa lecture (fusion à trois voies) ; même champ changé ailleurs entre-temps : refus explicite (`ConflitEcriture`, relancer le script). `voix.py`, `utile.py`, `camera.py` et `musique.py` peuvent donc tourner en parallèle (pas `renumeroter.py`). |
| `images.py` | Métadonnées et licence (API Commons), téléchargement, WebP 1600 px, vignette du portail ; portraits des lectures et fac-similés des épisodes. Aide à la recherche (`--chercher`, `--infos`, et `--lot FICHIER` : lignes `cle|requête`, seuls les fichiers libres d'au moins 1000 px, noms complets, JSON et planche-contact dans `.cache/diaporamas/lots/`). |
| `voix.py` | Synthèse Gemini (narrateur Charon ; voix de lecture pour les lectures d'époque), contrôle de fidélité, encodage m4a, durées, horodatage des phrases ; minutage mot par mot des lectures (`--mots`). Diapositives, lectures et épisodes. Options Gemini : `--budget`, `--reflexion` (transcription), `--modele` (voix), `--modele-transcription`. |
| `alignement.py` | Alignement forcé d'un audio de lecture sur son texte (wav2vec2 français, torchaudio) : instants de chaque mot. Appelé par `voix.py`. |
| `camera.py` | Caméra calée sur la narration : étapes `image.camera` proposées par Gemini Flash (vision), contrôlées, planche-contact. Visages relevés **localement** (`--visages`, gratuit ; `--visages-gemini` payant) ; `--audit` et `--reparer` sans appel (tête hors champ des portraits comprise). |
| `visages_local.py` | Détection locale des visages (YuNet, OpenCV DNN), lancée par `camera.py` dans `.cache/venv-visages` : cache `<slug>/visages-local.json`, mêmes clés et même format que `visages.json`. Mode portrait avec scores pour `portraits.py` (cadre du visage, spec 13). |
| `gemini.py` | Appel Gemini commun : modèle par tâche (`DIAPORAMAS_MODELE_<TACHE>`, `--modele`), réflexion réglée (`thinkingBudget`, défaut 256, `DIAPORAMAS_REFLEXION`, `--reflexion`), plafond de dépense par lancement (`--budget`, arrêt propre), tarifs **indicatifs** par modèle (`TARIFS`). **Solde** (spec 13) : registre des dépenses, `--crediter`, `--solde`, sonde des crédits avant le premier appel, arrêt propre sur un 402 (voir « Vérification par étape et solde Gemini »). |
| `banc_gemini.py` | Banc d'essai des modèles et budgets de réflexion pour une tâche (`camera`, `visages`, `utile`, `transcription`) sur 5 diapositives : jetons réels, coût, qualité, planche. `--essai` : plan sans appel. |
| `utile.py` | Zone utile `image.utile` de chaque image (sans liseré, marge de papier, cadre ni légende gravée) : analyse des bords (numpy) et contrôle par Gemini Flash, planche de contrôle. Options Gemini : `--budget`, `--reflexion`, `--modele`. |
| `musique.py` | Musique : enregistrements libres (Commons, Internet Archive), licences, découpe, fondus, sonie, m4a. `--indicatif` : les deux extraits de l'indicatif commun du générique. Rappelle en fin de passe les pistes absentes du registre des enregistrements. |
| `carte.py` | Fonds de carte (Natural Earth, domaine public) des épisodes et des médaillons de lieu : `src/data/diaporamas/fonds/<nom>.json` (`france`, `voisins`, `europe`, `monde`) ; plans de Paris d'époque calés (`public/diaporamas/fonds/<nom>.webp`, `src/data/diaporamas/plans/<nom>.json`). `monde` descend à -20° (Sainte-Hélène) ; `--fond NOM` ne refait que ce fond. |
| `surimpressions.py` | Cartes de lieu, citations, portraits, objets de musée, manuscrits, chiffres clés et dates républicaines en surimpression : instants calés sur la voix (alignement des mots de la narration) ; `--relever` liste les passages entre guillemets. |
| `objets.py` | Objets de musée et manuscrits : registre `objets.json` (licence par l'API, téléchargement avec cache, détourage local par rembg, webp transparent ; fac-similés des manuscrits), planche de contrôle, bilan des mentions. |
| `portraits.py` | Portraits des personnes nommées : recherche assistée (Wikidata, Commons), registre `portraits.json` (licence par l'API, téléchargement avec cache, cadre du visage par le détecteur local YuNet depuis le 2026-10-10, Gemini en repli demandé seulement, webp ovale), contrôle de visibilité des personnes sur les images (consignes au titre de la période du JSON), planche de contrôle. `--lot FICHIER` : lignes `id|nom`, Wikidata en une ligne par personne et pré-remplissage du registre (`--essai` : sans écrire). Options Gemini : `--budget`, `--reflexion`, `--modele`. |
| `ajouter_lieux.py` | Ajout idempotent des lieux des médaillons à plusieurs lieux de la Révolution (données en dur, coordonnées Wikidata) ; `--fichier` pour une copie, `--essai` pour voir sans écrire. |
| `renumeroter.py` | Insertion de diapositives et renumérotation : fichiers, renvois par numéro et états du cache recalculés, sans resynthèse. |
| `verifier.py` | Contrôle d'une période avant publication (110 à 135 diapositives pour les périodes 01 à 05 ; 135 à 160 et environ une heure à partir de la 06, avertissement hors de 55 à 65 min) ; générique : 8 à 12 images de la période, deux par acte au plus, indicatif commun (licence, fichiers, durées). Avertit d'un **dosage insuffisant** des enrichissements (avant/après < 3, mosaïques < 2, objets < 6, manuscrits < 3, chiffres et dates < 6, zéro compris), d'un épisode à visuel unique, d'un carton qui n'ouvre pas l'épisode et d'un panneau `chiffres` qui contient des années. `--etape A|B|C` (spec 13) : contrôles d’une étape, sortie résumée. |
| `tester_etapes.py` | Contrôle de `verifier.py --etape` : la réunion des étapes A, B et C égale la vérification complète. |
| `registre_musique.py` | Registre des enregistrements libres commun aux périodes (`commun/registre-musique.json`) : `chercher`, `ajouter --depuis`, `ecarter`, `possible`, `introuvable`, `--amorcer` (voir « Registre des enregistrements libres »). |
| `generation.py` | Couche générée (spec 16) : `preparer <slug>` (kit zip pour Colab : manifeste et sources JPEG réduites à la zone utile), `lancer <slug>` (session Colab par la CLI `colab`, calcul par `scripts/colab/mouvement.py`, rapatriement, arrêt), `encoder <slug> [zip|dossier]` (clips aller-retour H.264 sans son, encodés pour le site, dans `.cache/diaporamas/<slug>/generation/clips/`), `planche <slug>` (page HTML de visionnage), `publier <slug> [--seulement n,n]` (clips → `public/diaporamas/<slug>/NNN-mouvement.mp4` et champ `image.video`), `retirer <slug> --seulement n`. Lot : `src/data/diaporamas/generation/<slug>.json` (voir « Couche générée »). |
| `couleur.py` | Images colorisées par IA (spec 16) : `publier <slug> <lot.json> [--seulement 86 34b] [--sauf …] [--jugement bon] [--essai]` (retrouve chaque image par son `commons`, contrôle zone utile et taille, copie `NNN-couleur.webp` / `NNN-b-couleur.webp`, écrit `image.couleur`, consigne la recette dans `src/data/diaporamas/generation/<slug>-couleur.json`), `retirer <slug> 86 34b` (ou `--tout`), `lister <slug>` (voir « Couche générée », « Colorisation »). |
| `prononciation.yaml` | Lexique appliqué au texte envoyé à la voix (jamais aux sous-titres). |

Données et sorties :

- `src/data/diaporamas/NN-<slug>.json` : le script d'une période (source de vérité) ;
- `public/diaporamas/<slug>/NNN.webp`, `NNN.m4a`, `vignette.webp` : fichiers servis ;
  `musique/fond-<acte>-<k>.m4a` et `musique/chant-<nom>.m4a` : musique ;
- `src/data/diaporamas/commun/indicatif.json` et `public/diaporamas/commun/indicatif-ouverture.m4a`,
  `indicatif-fin.m4a` : indicatif du générique (composé avec Lyria), **commun à toute la série**
  (section « Générique ») ;
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
# Visages locaux (gratuit), audit et réparation sans appel ; passe payante plafonnée et réglée
python3 scripts/diaporamas/camera.py revolution --visages
python3 scripts/diaporamas/camera.py revolution --audit
python3 scripts/diaporamas/camera.py revolution --reparer --n 64 65
python3 scripts/diaporamas/camera.py revolution --n 12 --budget 0.50 --reflexion 256 --modele gemini-3.5-flash-lite
# Banc d'essai des modèles avant une passe de masse (--essai : plan et estimation, sans appel)
python3 scripts/diaporamas/banc_gemini.py camera consulat-empire --essai
python3 scripts/diaporamas/banc_gemini.py transcription revolution --modeles gemini-3.8-flash gemini-3.5-transcribe --reflexions 0
# Recherches par lots : images (lignes « cle|requête ») et personnes (lignes « id|nom »)
python3 scripts/diaporamas/images.py --lot recherches.txt
python3 scripts/diaporamas/portraits.py --lot personnes.txt --essai

# Musique : ce qui manque ou a changé ; --force pour tout refaire ; --sources pour
# télécharger et contrôler les licences seulement
python3 scripts/diaporamas/musique.py revolution
python3 scripts/diaporamas/musique.py revolution --piste chant-marseillaise
python3 scripts/diaporamas/musique.py revolution --sources
# Indicatif commun du générique (une fois pour toute la série)
python3 scripts/diaporamas/musique.py --indicatif

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

# Objets de musée et manuscrits : recherche, registre (détourage), planche à relire, bilan
python3 scripts/diaporamas/objets.py --chercher "assiette révolutionnaire"
python3 scripts/diaporamas/objets.py --registre               # ce qui manque (--id x y, --force)
python3 scripts/diaporamas/objets.py --planche
python3 scripts/diaporamas/objets.py revolution --relever

# Insérer des diapositives (groupes {"apres": n actuel, "diapositives": […]}) et tout renuméroter ;
# --essai affiche la correspondance sans rien écrire. Puis images.py, voix.py, camera.py.
python3 scripts/diaporamas/renumeroter.py revolution --inserer ajouts.json --essai

# Contrôle final (code de sortie 1 en cas d'erreur ; --hors-ligne : textes des lectures
# comparés au cache Wikisource au lieu de la page téléchargée à neuf)
python3 scripts/diaporamas/verifier.py revolution
python3 scripts/diaporamas/verifier.py --tous
# Contrôles d'une seule étape de production (A, B ou C), sortie résumée ; --tout : tous les avertissements
python3 scripts/diaporamas/verifier.py restauration --etape A

# Crédits Gemini : solde estimé, dépense de 7 jours par script, sonde ; après une recharge : --crediter
python3 scripts/diaporamas/gemini.py --solde
python3 scripts/diaporamas/gemini.py --crediter 10

# Registre des enregistrements libres : à consulter avant toute recherche musicale ; à compléter après musique.py
python3 scripts/diaporamas/registre_musique.py chercher mehul symphonie
python3 scripts/diaporamas/registre_musique.py ajouter --depuis restauration
```

## Procédure pour une période

0. Lire la spec 12, « Produire une période : leçons de Consulat et Empire » : enrichissements,
   épisodes, cartes animées et générique se prévoient dès l'étape 1.
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
6. Musique : pour chaque piste envisagée, d'abord `registre_musique.py chercher <mots>` (voir
   « Registre des enregistrements libres ») ; écrire `musique` dans le JSON (voir ci-dessous), lancer `musique.py <slug>`
   puis `registre_musique.py ajouter --depuis <slug>`,
   écouter les extraits, ajuster `debut`/`fin` et les paroles, puis `paroles.py <slug> --ecoute`
   et relire ses planches (voir « Paroles des chants » ci-dessous).
7. Cartes de lieu, citations, portraits, objets, manuscrits, chiffres et dates : remplir `lieux`, `citations`, `personnes`, `personnes_vues`, `objets`, `manuscrits`, `chiffres` et `dates_republicaines` (voir ci-dessous ; `portraits.py` pour le registre et la visibilité, `objets.py` pour le registre des objets), lancer
   `surimpressions.py <slug>` (à relancer après toute nouvelle voix).
8. Images mises en mouvement (spec 16, à partir de la période 05) : écrire le lot
   `src/data/diaporamas/generation/<slug>.json` (une dizaine de diapositives choisies dès l'étape 1,
   une consigne anglaise et une graine chacune), puis `generation.py preparer`, `lancer` (Colab par
   la CLI, ≈ 2 h 30 de machine par période, session arrêtée à la fin), planche de visionnage, `publier`
   (voir « Couche générée »). Zéro Gemini.
9. `verifier.py <slug>` puis `npm run build`.

Chaque agent termine son étape par `verifier.py <slug> --etape A` (ou `B`, `C`), et lance
`gemini.py --solde` avant une étape payante (voir « Vérification par étape et solde Gemini »).

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

**Visages locaux, tête hors champ, Gemini réglé (2026-10-09).** Les contrôles de visages (`--audit`,
`--reparer`, contrôle des propositions) lisent `DIAPORAMAS_VISAGES` / `--source-visages` : `union`
(défaut : relevé Gemini déjà payé s'il existe, plus les visages locaux nets d'au moins 6 % qu'il a
manqués), `local` (YuNet seul, toute nouvelle période), `gemini` (ancien relevé, appel payant si
absent). Comparaison sur 20 images (8 gravures, 6 foules, 6 peintures) : YuNet retrouve 80 % des
visages Gemini des gravures, 83 % dans les foules, 100 % ailleurs (78 à 86 % sur les 230 images) ;
il manque surtout têtes coupées, profils perdus et très petites têtes, et ajoute quelques fausses
alertes ; ~35 s par période, 0 $. Gemini reste en option (`--visages-gemini`). Nouvelles règles :
**front légèrement coupé admis** (au plus 20 % du visage) quand la vue est collée au haut de l'image
(y ≤ 0,08 : le cartouche cache le haut) ; **tête hors champ** : un portrait (deux visages au plus,
le plus grand d'au moins 8 % de la hauteur) dont aucune vue ne montre la moitié du visage principal
est signalé par `--audit` et réparé par `--reparer` (première étape recadrée sur la tête, sans
appel ; une tête plus haute qu'une vue est montrée du front au nez). Les portraits coupés par la
réparation géométrique de la passe précédente (CE 23, 52, 69, 79 ; Rév 60, 62, 64, 65, 89, 103) ont
été corrigés ainsi ou à la main (`camera_manuelle`). Tout appel Gemini passe par `gemini.py`
(réflexion à 256 jetons par défaut, `--budget` en $, `--modele`) ; mesurer d'abord avec
`banc_gemini.py` sur 5 diapositives.

**Règle du portrait (2026-10-09, CE 23 *Cadoudal*).** Cause du défaut : la caméra montrait la tête,
menton coupé ; l'audit n'y voyait qu'un « visage coupé » ordinaire (l'ancien contrôle « tête hors
champ » se contentait de la moitié du visage dans une vue), et `--reparer`, qui ne protégeait le
sujet que s'il tenait dans le cadre d'origine (il dépassait de 0,02), a retenu la bande la plus
proche où le visage était « franchement dehors » (8 % < 10 %) : le gilet. Le visage était bien
détecté (Gemini et YuNet) et la vue réelle juste. Désormais (`personne_seule`, `portrait_coupe`,
`tete_visible`, `bande_tete` dans `camera.py`) : sur le portrait d'une personne seule, **chaque
vue**, au début de la tenue et au bout du zoom lent, montre le visage principal entier (8 % du haut
du rectangle, les cheveux, peuvent être coupés ; tête plus haute qu'une vue : sans le quart haut,
menton compris ; portrait très serré : bande 40-75 % du rectangle, du front à la bouche). Portrait =
un seul visage net d'au moins 8 % de la hauteur dans le haut de l'image, ou, si le titre (« Portrait »,
nom de la seule personne de `personnes_vues`) ou le registre (même fichier Commons) l'indique, un
visage dominant (1,4 fois plus haut que les autres, trois au plus, 6 % au moins) ; sans visage net,
seconde passe YuNet à seuil bas (`visages_local.py`, mode portrait) ; à défaut, saisir
`image.visage` à la main. Deux visages sans indice (couple, fausse détection : CE 56) : règle faible
(une vue au moins montre la moitié de la tête). Le contrôle est dans `erreurs_vues` (propositions du
modèle, `--audit`, réparations) ; le visage principal n'est plus soumis au contrôle ordinaire, et
une vue qui le montre est dispensée du contrôle d'aplat (fonds de portraits). `reparer_etape`
protège ce visage même hors du cadre d'origine et essaie des cadres sur la tête ; `reparer_tete`
répare chaque étape fautive (une étape suivante irréparable est abandonnée). Passe du 2026-10-09 :
réparées CE 18, 23, 65, 73, 74, Rév 23, 38, 50, 65, 89, 113, 123, 127 ; à la main CE 33 (cadre avant
et `apres.cadre` décalés ensemble, raccord gardé), Rév 7 et 60. Restent signalées par la règle
faible (pas des personnes seules) : CE 56, Rév 98, 106.
**Assouplissement (2026-10-09, choix de l'utilisateur)** : seules la première et la dernière vue
doivent montrer le visage entier ; une vue intermédiaire peut aussi le laisser entièrement hors
champ (0 %, début de tenue et bout du zoom : `tete_dehors`, `vue_portrait_juste`) pour un gros plan
sur un détail cité par la voix ; un visage à moitié coupé reste refusé (consigne au modèle,
`erreurs_vues`, `--audit`, `reparer_etape`). Gros plans rétablis à la main (`camera_manuelle`),
avec retour au visage, détail rapproché pour que la transition tienne dans la voix : CE 18
(décret, « Ingres le peint » → « son profil orne »), 65 (bureau et Code, « David le peint debout » →
« le souverain veille »), 73 (cartes perforées), Rév 38 (Marche lugubre → « jusqu'au Panthéon »),
50 (le verre → « l'humiliation infligée »), 113 (le drapeau), 123 (l'épée → « qui a quitté
l'Égypte » ; sur téléphone, le lecteur ignore le gros plan, vue presque identique).

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
  nomme alors un élément visible. Sinon, le lecteur fait « respirer » l'image.
- **Zoom lent continu** (spec 12, « Caméra plus vivante et cadres justes », 2026-10-09 ; `souffle`) :
  pendant chaque tenue, zoom avant à sens unique de 1,2 % par seconde (0,012 en log d'échelle), 12 %
  au plus (×1,12, atteint après ~10 s de tenue), mise en route et arrêt doux de 1,2 s (la moitié
  de la tenue au plus) ; glissement vers le centre du cadre visé (le sujet), borné à la marge
  libre : la vue zoomée reste dans la vue de départ, donc dans la zone utile. `plan` compte le
  départ zoomé pour tenir les plafonds de vitesse de la transition suivante. `camera.py` refuse désormais, dès la proposition du modèle, un
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
- **Vue réelle, cause des cadres faux** (diagnostic du 2026-10-09) : la partie libre de la scène,
  sous le cartouche et au-dessus des bandeaux, est une **bande panoramique** (~2,6:1 sur ordinateur,
  ~2,3:1 en plein écran 16/9), pas un écran 16/10. Sur une image en hauteur, seule une bande de
  ~20 à 36 % de la hauteur est visible, et un cadre plus haut est montré **depuis son bord
  supérieur** : le bas du sujet disparaît (*La Thilorière* : le haut du ballon). Pire, deux cadres
  différents ainsi coupés donnent la même vue : le lecteur ignore la seconde étape
  (micro-déplacement) et la caméra ne bouge plus. L'audit du 2026-10-09 trouvait ~100 diapositives
  avec une étape ignorée et ~146 sur 241 avec au moins un défaut grave.
- **Règle des cadres justes** (`camera.py`, `VERSION = 'v3'`) : `vue_reelle` reproduit `vue` du
  lecteur (bande `RATIO_VUE = 2.5`, bandeaux de 20 % et 15 % de la vue, coupe par le haut) ; le
  modèle reçoit la zone utile, la hauteur maximale d'une vue et la liste des visages ; le contrôle
  refuse (1) un cadre dont la vue montre moins de 80 % de la hauteur ou de la largeur (sujet
  entier ; seule une vue d'ensemble de départ suivie d'autres étapes en est dispensée) ; (2) une
  dernière vue à plus de 75 % sans détail (gradient faible : ciel, fond uni, marge ; mesure
  grossière, des ciels gravés passent pour unis : relire) ; (3) **un visage coupé** : chaque
  visage de 3 % de la hauteur de l'image au moins est entier dans la vue (90 % de son aire) ou
  franchement dehors (10 % au plus), au début de la tenue et au bout du zoom lent ; (4) un
  micro-déplacement jugé sur les vues, non sur les cadres. La relecture montre au modèle les vues
  découpées telles qu'à l'écran. Une caméra v1/v2 en cache reste valable si elle passe ces
  contrôles (sauf la mesure d'aplat, faite à la relecture et par `--audit`).
- **Visages** : `camera.py <slug> --visages` les relève une fois par image (Gemini, en cache dans
  `visages.json` par empreinte du fichier ; `cadrer` le fait au besoin). Schéma à clés nommées
  (`gauche`, `haut`, `droite`, `bas`) : avec une liste `[x0, y0, x1, y1]`, Gemini rendait sa
  convention `[y0, x0, y1, x1]`. Coût réel : ~0,004 $ par image (jetons de réflexion).
- **Contrôle sans appel** : `camera.py <slug> --audit` liste les diapositives fautives (vues,
  visages, aplat, étapes que le lecteur ignorerait) ; `--planche --n 4 20` fait une planche de ces
  diapositives seules (`planche-choix-NN.jpg`). Les planches dessinent désormais les vues réelles
  en pointillé (couleur de l'étape) et les visages contrôlés en blanc : c'est la vue en pointillé
  qu'il faut juger, pas le cadre en trait plein.
- Taille minimale : porté aux proportions 16/10, un cadre fait au moins 30 % du plus grand
  côté de l'image (`camera.ajuster`) ; `verifier.py` tolère 25 % pour les corrections à la main.
- **Correction à la main** : modifier les étapes et ajouter `"camera_manuelle": true` à la
  diapositive ; `camera.py` ne la touchera plus. Les ratés signalés par l'utilisateur se
  corrigent ainsi, ou par `camera.py <slug> --n 12` si un nouvel essai du modèle suffit.
- Le cache (`camera.json`) garde la réponse du modèle par empreinte (narration, image,
  consignes) : changer les consignes demande d'incrémenter `VERSION` dans `camera.py`.
- Coût mesuré en v3 (2026-10-09) : ~0,015 à 0,02 $ par diapositive (3 à 4 appels, vues découpées
  en relecture). Ancien chiffre : ~2 appels par diapositive (proposition + relecture), environ 0,01 $ par
  diapositive, soit ~1 $ par période (tarif Gemini Flash supposé, à confirmer sur la facture).

### Entrée en scène d'une grande vue (`image.entree`, 2026-10-12)

Spec 12, « Entrée en scène des grandes vues ». Un mouvement d'arrivée propre à l'image, pensé
comme un plan de cinéma, **sans lien avec la voix**, qui finit exactement sur la première vue ;
la caméra habituelle reprend ensuite. Sans le champ, rien ne change (rien n'est écrit dans les
données du lecteur).

```jsonc
"image": { …, "camera": [ … ],
  "entree": { "cadres": [[0.15, 0.16, 0.70, 0.46], [0.33, 0.34, 0.96, 0.67]],  // 1 ou 2 cadres de départ (fractions de l'image servie)
              "duree": 5,                                                        // 4 à 7 s (absent : 5)
              "intention": "Des toits des Tuileries, on descend la façade jusqu'à la foule." } }
```

- **Où** : image d'une diapositive ou d'un plan (le mouvement part de l'instant du plan). Sans
  effet (erreur de `verifier.py`) avec `ouverture`, un avant / après ou une mosaïque ; pas sur
  les galeries ni les lectures. Mouvement réduit : pas d'entrée, premier cadre d'emblée.
- **Lecteur** (`camera.ts` : `arrivee`, `cadreArrivee` ; même profil que le recul d'ouverture,
  rampes de 40 %) : la durée demandée est **allongée** tant que la vitesse au plus fort dépasse
  les plafonds de la caméra calme, puis **bornée à 75 % de la fenêtre** de l'image (jusqu'au plan
  suivant ou la fin de la voix : `ENTREE_PART`). Deux cadres : les deux trajets se chevauchent
  sur leurs rampes, sans arrêt au milieu. La première tenue commence à la fin de l'entrée ; les
  étapes suivantes gardent leurs instants si elles tiennent encore (1 s de tenue, puis la transition).
- **Image entière** (`entier`) : l'entrée **précède** le rapprochement ; elle finit sur l'image
  entière, puis `entier_vers` joue comme d'habitude (1,2 s, rapprochement lent). Les cadres de
  départ sont montrés sans bandes noires dès qu'ils sont plus larges que hauts.
- **Choisir le cadre de départ** : c'est la **vue réelle** qui compte. Sur ordinateur, la bande
  libre est très large : tout cadre plus haut que ~45 % de l'image est montré pleine largeur, et
  deux cadres hauts donnent la même vue (aucun mouvement). Une montée ou une descente se fait
  donc à pleine largeur (30 à 35 % de la hauteur de course) ; un recul ou un travelling latéral
  demande un cadre de départ **bas et serré** (hauteur ≤ 35 %). Garder pour la fin ce que le
  spectateur doit découvrir en dernier : le vérifier sur la planche, pas sur le cadre.
- **Pièges** : une image qui ne reste que 7 à 8 s avec deux étapes de caméra perd sa deuxième
  étape derrière le plan suivant (ne pas lui donner d'entrée) ; ne pas partir du plan large si la
  caméra existante finit par s'élargir (mouvement inversé) ; zoom total ≤ ×2,4 (`verifier.py`).
- **Contrôle** : `python3 scripts/diaporamas/captures.py <slug> 8:0.1 8:1.4 8:2.8 8:4.2 8:5.5
  --dist <build> --planche` (plan b : `34:p1+0.1` … ; première diapositive d'un acte :
  `--attente 7000`). `__camera(n, t)` donne la fin de l'entrée (`plan[0].a`) et les étapes retenues.

- **Généraliser à une période** (`entree.py`, 0 $) : `plans <slug> --dist <build> --sortie plans.json`
  (étapes retenues par le lecteur, ordinateur et téléphone), `candidates <slug> --plans plans.json
  --planches <dossier>` (tri mécanique, puis tri à l'œil des lieux et des scènes sur les vignettes),
  `preparer <slug> --plans plans.json --n …` (une tâche par image, en lots ; un sous-agent Sonnet par
  lot : « Lis `<dossier>/lot-K/LISEZMOI.md` et suis-le »), `planche <dossier>` (vues de départ en
  pointillé rouge, première vue en vert : à relire), `appliquer <dossier> [--sauf …]` (n'écrit que
  `entree`), `retirer <slug> --n …`, `bilan <slug> [--detail]`. Après build : `plans` sur le nouveau
  build puis `etapes <slug> --avant … --apres …` : 0 écart attendu.
- **Règle de fenêtre** (2026-10-12) : l'entrée ne décale ni ne supprime aucune étape de caméra.
  L'image reste au moins 9 s si sa caméra a une deuxième étape, 6 s sinon ; et l'entrée finit 1 s
  avant le départ de la transition vers la deuxième étape (relevé du lecteur ; sans relevé : 3 s
  avant son `quand`). Écartées aussi : première image d'un acte (les volets sont son entrée), clip
  `video`, portrait, document. `entree.py regle <slug>` relit les entrées posées.
- **Relecture obligatoire sur le lecteur** : trois captures par image (0,1 s, mi-entrée, fin + 0,2 s).
  Ce qui ne passe pas l'écran : travelling ou recul parti d'un cadre bas et serré (vues de début et
  de fin presque identiques), montée partie du premier plan d'une foule (têtes coupées en haut).
  Les descentes et les reculs d'image entière (`entier`) sont les plus sûrs.
- **Périodes neuves** : `banc_claude.py preparer` joint la demande d'entrée à la tâche de caméra des
  grandes vues, et `appliquer` pose le champ avec la caméra (voir « Caméra proposée par Claude »).

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
  la dernière année du dernier acte (les `dates` des actes).
- Dessin (frise simplifiée du 2026-10-09), le même dans le carton et en bas de l'image : un
  filet fin, la première et la dernière année aux extrémités, une petite graduation par année
  sans étiquette, le curseur (trait fin, ou court segment pour une durée) et sa date au-dessus
  (`libelleDate`). Plus de segments d'actes ni d'années intermédiaires. Monochrome ; sur
  téléphone, même dessin pleine largeur.
- Carton d'acte (**révisé le 2026-10-11** : frise animée, voir « Images entières sur fond noir,
  repères des cartons » ; **le 2026-10-12** : période de l'acte en couleur `--c-accent`, zone teintée
  et onde, plus de dates clés) : la même frise, sans curseur ni date, avec l'intervalle de l'acte en segment
  épais (de la première à la dernière date de ses diapositives, `poserActe`), en fondu ;
  6 px au moins, centré sur l'intervalle.
- Affichage en bas de l'image : pendant 4 s (fondu, glissement ~1 s, lecture, fondu de 0,6 s) à chaque
  **changement d'année** (année de début de la date) par rapport à la diapositive précédente
  et à tout **retour en arrière** (intervalle entièrement antérieur au début du précédent) ;
  rien pendant les lectures, épisodes et chants. Mouvement réduit : fondus courts, sans
  glissement. `verifier.py` contrôle format et période, liste les retours en arrière en
  avertissement et compte les apparitions en bas de l'image (Révolution : 16 ; Consulat et
  Empire : 10) ; un retour en arrière d'une diapositive de contexte se règle souvent en omettant
  sa date ou en la datant au mois.
- Priorité : la frise **s'affiche toujours** ; elle prend le bas de l'image (au-dessus des
  autres, z-index 3) et pousse les autres surimpressions du bas qui la chevauchent en largeur
  (médaillon, portraits, objet, chiffre, date républicaine, citation ; classe `sous-frise` posée
  par `majPoussee` à chaque image tant qu'elle est là : sur ordinateur, les coins restent en
  place ; sur téléphone, tout monte) de sa hauteur plus 8 px, en douceur (500 ms), le temps
  de son passage : variable `--frise-pousse` posée sur ces éléments par `:has()` et ajoutée à leur
  `bottom`, hauteur mesurée (`--frise-h`). Elle n'entre pas dans la règle des deux
  surimpressions ; la place réservée pour la caméra l'ignore (éphémère).
- Piège corrigé le 2026-10-09 : la date républicaine des surimpressions s'appelle `dateRep`
  dans les données du lecteur ; sous le nom `date`, elle écrasait la date de la frise (carton
  sans curseur, frise du bas jamais montrée).

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

### Registre des enregistrements libres (`registre_musique.py`, spec 13)

`src/data/diaporamas/commun/registre-musique.json` garde, pour toutes les périodes, chaque
enregistrement déjà vérifié (`retenu` par une période, `possible`, ou `ecarte` avec son motif) et les
œuvres cherchées en vain (`introuvables`). **Avant toute recherche sur Commons ou l'Internet
Archive**, l'agent B interroge le registre ; il n'y cherche pas de nouveau ce qui est écarté ou
introuvable sans raison nouvelle.

```sh
python3 scripts/diaporamas/registre_musique.py chercher thill            # tous les mots, sans accents ni casse
python3 scripts/diaporamas/registre_musique.py ajouter --depuis <slug>   # après musique.py <slug>
python3 scripts/diaporamas/registre_musique.py ecarter "archive:<item>#<fichier>" "licence NC-ND" --oeuvre "…" --interprete "…"
python3 scripts/diaporamas/registre_musique.py possible "commons:File:….ogg" "<œuvre>" "<compositeur>" "<interprète>"
python3 scripts/diaporamas/registre_musique.py introuvable "<œuvre>" "<compositeur>" "Commons, IA : requêtes essayées"
```

- Une entrée par **enregistrement** (un fichier d'une source), d'identifiant
  `archive:<item>#<fichier>` ou `commons:File:<fichier>` : source et licence reprises telles quelles
  de la piste, durée de l'enregistrement entier, `structure` (passages déjà utilisés : début, fin,
  libellé), `periodes` qui l'utilisent. Le même fichier dans deux périodes fait une seule entrée.
- `chercher` porte sur l'œuvre, le compositeur et l'interprète ; une ligne par résultat (statut,
  œuvre, interprète, année, périodes, `id`), puis les introuvables qui correspondent.
- `musique.py` rappelle en fin de passe les pistes absentes du registre ; `verifier.py` (étape B)
  en fait un avertissement. `--amorcer` (idempotent) a rempli le registre depuis les périodes 01 et
  02 : 28 enregistrements pour 31 pistes, 9 introuvables de la recherche de la période 02.
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
  Poème (`poeme`, ou texte contenant des `\n`) : un vers par ligne (`.citation__vers`), retrait
  suspendu pour un vers trop long, en italique ; le surlignage mot à mot est inchangé.
- Voix de lecture (`VOIX_LECTURE` dans `voix.py`, ou `DIAPORAMAS_VOIX_LECTEUR` /
  `DIAPORAMAS_VOIX_LECTRICE`) : `Schedar` (homme) et `Aoede` (femme), **choix provisoire** ;
  essais à écouter dans `.cache/diaporamas/essais-voix-lecture/`. Changer de voix change
  l'empreinte : `voix.py` refait les lectures concernées.
- `portrait` : `diapositive` (image d'une diapositive, recadrée sur `cadre`, le visage) ou
  `commons` (fichier propre, licence relevée par `images.py`, `lectures/<id>.webp`, 640 px).
  Sans portrait, rien à sa place : le texte occupe toute la largeur (pas d'initiale).
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
  `carte` (`fond`, `cadre` facultatif [lon0, lat0, lon1, lat1] qui recadre le fond en gardant la
  taille apparente des libellés et des traits, `elements` : `ville` (`lieu` [lon, lat], `capitale`,
  `rebelle`, `position`), `fleche` (`de`, `a`), `zone` (`points`, ou `parties` : plusieurs anneaux ;
  `style` : `hachures` par défaut, `plein` gris foncé, `clair` gris moyen ; `libelle` facultatif,
  `\n` pour aller à la ligne ; `etiquette` [lon, lat] pour le placer ; la zone est **découpée sur
  les terres** du fond : ses points en mer peuvent rester larges, seules les frontières terrestres
  comptent), `trait` (`points` : ligne qui se dessine, ex. un fleuve ; `libelle`, `etiquette`),
  `legende` : `[signe, libellé]`, signes `fleche`, `rebelle`, `zone`, `plein`, `clair`, `trait`),
  `chronologie` (`titre`, `debut`, `fin`, `evenements` : `date` ISO partielle, `libelle`, `precision`,
  `quand` ; `source`) : frise propre à l'épisode, curseur qui glisse vers chaque date (1 s, `data-trace`
  pilote `--c`), bulles posées au build (côté alterné, deux rangs de chaque côté, 20 % de large, jamais
  l'une sur l'autre ; connecteurs SVG), la bulle précédente atténuée (`--p` d'un `.anim` imbriqué) ;
  sous 520 px de frise (téléphone) : frise verticale à gauche, bulles d'une ligne à droite (date et
  libellé, précision masquée), empilées au plus près de leur date. `verifier.py` : bornes, ordre,
  passages, source ; une suite d'années dans un panneau `chiffres` est signalée.
  Les pointes de `fleche` gardent leur taille à l'écran sur une carte recadrée (réduites par `k`).
  `document` (`image` Commons, licence
  relevée par `images.py`, `episodes/<id>.webp` en 2 400 px ; `lignes` : `cadre` [x0, y0, x1, y1]
  de la ligne dans l'image, `texte` exact relevé sur le fac-similé, `quand`).
- Chiffres, graphiques et cartes portent une `source` (affichée sous le visuel) ; `sources` de
  l'épisode : affichées dans le livre d'images.
- Frontières d'époque (ex. l'Europe de 1811, épisode `grand-empire`) : anneaux tracés à la main
  (20 à 80 points sur terre), assemblés à partir de **lignes de frontière partagées** (un même
  tracé pour les deux voisins : ni jour ni chevauchement), source notée dans `source` ; contrôle
  par une image des zones superposées au fond, comparée à une carte de référence.
- Fonds de carte : `carte.py` (Natural Earth 1:50 m, domaine public ; projection
  équirectangulaire corrigée, cadre et fleuves dans `FONDS`). Les éléments sont donnés en
  [longitude, latitude].

**Carte de l'empire colonial (spec 12, « Les colonies au fil du récit », 2026-10-12).** Une carte par
période, même fond et même dessin (fil rouge). Pour la carte d'une autre date :
1. Fond commun `empire` (`carte.py --fond empire` ; monde de Tahiti à la Nouvelle-Calédonie, 2 015 unités de
   large, coordonnées au dixième, métropole seule en « france ») : ne pas le refaire ni le recadrer.
2. Possessions en données : `src/data/diaporamas/commun/empire.json` (`de`/`a` : années d'entrée et de
   sortie ; `zone` ou point ; `vues` et `position` du libellé par vue). Renseigné pour 1789 : mettre `a` à
   ce qui est perdu, ajouter les acquisitions (avec `source`), une vue (`vues`) si la région manque.
   Depuis la période 02 : `periodes` ([[de, a], …]) remplace `de`/`a` pour une possession perdue puis rendue
   (perte = année de la prise ; retour = année du traité, la remise effective étant notée dans `reprise`, à
   vérifier) ; `noms` ([[année, nom], …]) donne le nom d'époque (La Réunion, île Bourbon). Renseigné de 1789 à 1815.
   Libellés avec année (« Saint-Pierre-et-Miquelon (1803) ») : trop longs à gauche ou à droite sur téléphone,
   les placer en `haut` ou en `bas` dans l'épisode (modèle : `empire-1811`, période 02).
3. `python3 scripts/diaporamas/empire.py 1811 --depuis 1802 --vue monde` (puis `--vue antilles`…) écrit le
   visuel `carte` : tenu = point plein ou zone pleine, perdu depuis = cercle vide ou hachures avec l'année,
   gagné = année d'entrée. Le coller dans `visuels` de l'épisode, ajouter les `quand`, la légende, la source.
4. Deux cartes au plus par épisode. Depuis le 2026-10-12, le tracé de chaque fond de carte d'épisode est écrit
   une seule fois par page (`svg.fonds-partages` dans `Diaporama.astro`, repris par `<use>` dans
   `EpisodeVisuels.astro`) : une carte de plus ne coûte que ses éléments. Sur la vue du monde, libellés à gauche en Amérique, pas de libellé de flèche au départ de France.
5. Contrôle : `captures.py <slug> N:s30 N:s58` (ordinateur et téléphone) ; modèle : épisode `empire-1789`.
6. Depuis la période 04 (2026-10-12) : vues `monde-pacifique` (cadre de Tahiti à l'Inde, `large` : les zones y
   deviennent des points, comme sur `monde`) et `afrique` ; acquisitions de 1830 à 1847 (`de` = année de la prise de
   possession ou du poste, le traité est dans `source` ; `statut: protectorat` à écrire à la main dans le libellé).
   Modèle : épisode `empire-1847` (`empire.py 1847 --depuis 1815 --vue monde-pacifique`, puis `--vue afrique`).
`renumeroter.py` suit depuis le 2026-10-12 les clips `NNN-mouvement.mp4`, le lot de génération et les caches
`utile`, `personnes` et `surimpressions` (le kit zip de génération garde les anciens numéros : `preparer`).

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
  29 m au plus ; Tardieu 1838 : ~12 m en moyenne, 25 m au plus). Le crédit (« Plan de Verniquet,
  1790 ») est dans le médaillon. Image servie : 2 000 px, gris, papier blanchi, ~440 Ko, chargée à
  la première diapositive qui en a besoin.
- Deux plans : `paris-1790` (Verniquet) du prologue à la Restauration ; `paris-1838` (Ambroise
  Tardieu, « Plan de Paris en 1838 », Gallica, ~540 Ko) pour `monarchie-de-juillet` et
  `deuxieme-republique` (ajout du 2026-10-11 ; la Restauration, déjà publiée, reste sur Verniquet).
  Une nouvelle période reçoit un plan en ajoutant son slug au champ `slugs`, puis `carte.py --plans`.

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
  visage par le détecteur local (voir « Cadre du visage par YuNet » ci-dessous), recadrage 4:5 où le
  visage occupe 58 % de la hauteur (son centre à 44 %) ; webp 360 × 450 px (240 × 300 avant le
  2026-10-08), ~10 à 60 Ko. Un cadre faux ou un visage non trouvé : corriger
  `cadre_visage` à la main et ajouter `"cadre_visage_manuel": true` (Révolution : Drouet, Nelson,
  Couthon). Planche de contrôle : `.cache/diaporamas/portraits/planche.jpg` (ovales et noms).
- Coût (Gemini Flash, tarif supposé) : ~0,12 $ pour la visibilité des 135 mentions de la
  Révolution ; cadres : 0 $ depuis le 2026-10-10 (~0,15 $ pour 48 portraits avec Gemini).

### Cadre du visage par YuNet (spec 13, 2026-10-10)

`portraits.py --registre` ne demande plus le cadre du visage à Gemini : il lance une fois
`visages_local.py` en mode portrait (venv `.cache/venv-visages`) sur tous les portraits à cadrer.

- **Ce qui est recalculé** : un portrait sans `cadre_visage`, ou dont le fichier Commons ou le nom a
  changé (clé du cache `cadres.json`), ou tout portrait désigné avec `--force`. Les cadres déjà au
  registre, posés par Gemini, sont gardés ; `cadre_visage_manuel: true` reste prioritaire.
- **Visage non trouvé** : « cadre à poser à la main » (code de sortie 1), ou relancer ce portrait
  avec `--repli-gemini --budget 0.05` (proposition et contrôle par Gemini, comme avant).
- **À relire** : `.cache/diaporamas/portraits/planche-a-relire.jpg` montre les seuls portraits
  nouveaux ou douteux (score sous 0,6, visage de moins de 6 % de la hauteur, visage très décentré,
  repli Gemini).
- **Étalonnage** : `portraits.py --registre --essai [--marge HAUT BAS CÔTÉS]` compare YuNet aux
  cadres du registre sans rien écrire, et dessine la planche des 10 plus gros écarts
  (`etalonnage-yunet.jpg`). Mesure du 2026-10-10 sur les 93 cadres Gemini des périodes 01 et 02 :
  visage trouvé 92 fois (Prud'hon, dessin de profil, manque), IoU médiane 0,76 (0,84 sur les
  recadrages 4:5), sans marge ajoutée. YuNet cadre un peu plus large que Gemini sur les têtes
  coiffées d'un chapeau (Toussaint Louverture, Barras).
- venv ou `yunet.onnx` absents : le script affiche les deux commandes d'installation et s'arrête.

**Instants** : `surimpressions.py <slug>` écrit `instant` (début du nom dans l'audio) comme pour les
lieux ; à relancer après toute nouvelle voix.

**Lecteur** (`portraitsDe` dans `src/utils/diaporamas.ts`, `Diaporama.astro`, styles dans
`Surimpressions.astro`) :
- rangée d'ovales **en bas à gauche** (le médaillon de lieu est en bas à droite), en couleur, bord fin
  (filet sombre et liseré clair), **sans cartouche** (révision du 2026-10-09) ; sous chaque ovale,
  une petite étiquette blanc cassé à filet fin, serrée (marge de 0,2 rem) : nom en petites capitales
  (0,86 rem ; 0,7 sur téléphone) et dates (0,74 ; 0,62) ; une personne seule : « Danton ·
  1759-1794 » sur une ligne ;
- une personne par ovale, dans l'ordre de la première mention, **4 au plus** ; chaque ovale paraît
  au nom (le premier dès l'entrée de la rangée), les précédents restent ; la rangée va du premier
  nom à 3 s après le dernier (5 s au moins ; un nom dit dans les 4 dernières secondes avance son
  entrée), prolongée jusqu'à la fin de la citation de la personne ;
- taille (**révisée le 2026-10-11** : moyenne de l'ancienne et de celle-ci, voir en fin de fichier ;
  révision du 2026-10-09) : 1,5 fois l'ancienne (25 % de la hauteur de la scène, 110 à
  180 px, 70 au moins sur téléphone), plafonnée à `COIN_H_MAX` = 30 % de la hauteur de la scène
  (`COIN_H_MAX_TEL` = 27 % sous 700 px de large ; `constantes.ts`) : 134 px à 1280 × 760 (scène
  1040 × 450), 216 px à 1920 × 1080, 105 px sur téléphone 390 × 844 ; rangée avec étiquette
  ~36 % de la hauteur sur ordinateur. Réduite, en quelques passes (les étiquettes ne rétrécissent
  pas avec l'ovale), si elle ne tient pas à côté du médaillon de lieu, ou de l'objet du coin droit
  quand leurs fenêtres se chevauchent (`tailleObjet` passe avant `taillePortraits`). Webp de
  450 px de haut : nets jusqu'à une densité d'écran de 2 pour un ovale de 225 px ; au-delà
  (écran 4K, plein écran), légèrement doux ;
- zone couverte pour la caméra : la hauteur de la rangée (étiquettes comprises, mesurée par
  `offsetHeight`) est réservée **pour toute la diapositive** qui en a une (comme le médaillon de
  lieu) ; tous les ovales sont posés d'emblée (invisibles), la rangée ne change jamais de taille ;
  à un nouveau nom, l'ovale et son étiquette paraissent en fondu (`PORTRAIT_FONDU`, 0,45 s) ; le
  « fond qui grandit » du 2026-10-08 a disparu avec le cartouche ;
- affichage dérivé de l'instant lissé de l'audio (pause, reprise, sauts justes) ; mouvement réduit :
  fondu simple de 200 ms, sans glissement ;
- **surimpressions ensemble**, par ordre de priorité : citation > portraits = médaillon de lieu >
  frise du temps. La citation exclut déjà le médaillon (arbitrage existant) ; avec des portraits,
  si elle touche la rangée, elle monte au-dessus d'elle pour toute la diapositive (rien ne bouge
  pendant la lecture) ; la frise du temps, elle, ne cède plus (révision du 2026-10-09) : elle
  pousse les autres plus haut ; sur téléphone, le
  cartouche de la musique (même bande du bas) s'efface le temps des portraits ;
- crédits : section « Portraits » de la page (nom, dates, auteur, date, lien Commons, licence).

`verifier.py` : registre (champs, fichier présent, licence, cadre du visage, œuvre postérieure de
plus de 5 ans à la mort signalée), `quand` exacts et dans l'ordre, instants présents, croissants,
dans l'audio et à jour, 4 portraits au plus, personne montrée absente de l'image (jamais dans
`personnes_vues` de la même diapositive ; désaccord avec le cache de vision en avertissement),
personne citée accompagnée de son portrait.

## Objets de musée et manuscrits

Spec 12, « Enrichissements visuels », points 1 et 2 (2026-10-08). Toujours actifs dans le lecteur ;
rien dans le livre d'images ; crédits dans la section « Objets et documents » de la page.

```json
{ "n": 22, "narration": "… il accepte la cocarde bleue et rouge de Paris, …",
  "objets": [{ "id": "assiette-cocarde", "quand": "la cocarde bleue et rouge", "instant": 5.28 }] }
{ "n": 94, "narration": "… Libéré par la Commune, il se réfugie à l'Hôtel de Ville. …",
  "manuscrits": [{ "id": "appel-section-piques", "quand": "il se réfugie à l'Hôtel de Ville", "instant": 11.25 }] }
```

**Choix.** Objet : un objet d'époque dont la voix parle ou qu'elle évoque de près (« la cocarde »,
« le bonnet rouge », « les représentants en mission », « Le litre et le gramme ») ; photo sur Commons
du domaine public, CC0, CC BY ou CC BY-SA (jamais NC ni ND), le musée noté. Les collections de Paris
Musées (Carnavalet, CC0, fond de studio) et les photos de Rama (Musée de l'Armée, CnAM, CC BY-SA, fond
blanc ou noir) se détourent bien. Manuscrit : document d'époque (lettre, acte, décret, certificat)
que la narration évoque, domaine public, métadonnées vérifiées sur la notice du musée ; `halo` sur la
signature ou la phrase, relevé à la main sur l'image quadrillée et vérifié sur la planche.
- `quand` : passage exact (première occurrence) ; `instant` écrit par `surimpressions.py` ;
  `cote` : `droite` (défaut) ou `gauche`, choisi là où l'objet gêne le moins (pas le coin d'un
  médaillon ou d'une rangée de portraits qui se montrerait en même temps).
- Registre `src/data/diaporamas/objets.json` (commun à toutes les périodes) : `nom` (légende
  courte, 50 caractères environ), `date`, `musee`, `inventaire`, `commons`, `recadrage`,
  `detourage` (`convexe` pour une assiette ou une médaille), `halo` et `passage` (manuscrit) ;
  `objets.py --registre` écrit `fichier`, `largeur`, `hauteur`, `licence`, `page`, `auteur_photo`
  (licence CC BY : crédit obligatoire).
- Détourage : rembg (`isnet-general-use`) sur l'image réduite à 2 000 px, masque durci (seuils 40
  et 215), couleurs de l'original ; pour une faïence blanche, le modèle prend le blanc pour le fond :
  `detourage: "convexe"` remplace le masque par son enveloppe convexe. Rogné sur l'objet (marge de
  2 %), 720 px au plus, webp transparent (15 à 130 Ko). Relire `.cache/diaporamas/objets/planche.jpg`
  (damier, gris, fond sombre ; halo des manuscrits en rouge). Manuscrits : webp 1 400 px au plus.

**Lecteur** (`objetsDe` dans `src/utils/diaporamas.ts`, `Diaporama.astro`, styles dans
`Surimpressions.astro`) :
- objet (révision du 2026-10-08) : coin bas, **posé directement sur l'image**, sans carte ni fond : halo
  clair diffus et ombre très douce (`drop-shadow`, pas de contour net), légende sous l'objet sur un
  voile blanc cassé léger ; objet en couleur, 1,5 fois l'ancienne taille (révision du 2026-10-09 ;
  avant : 22 % de la hauteur de la scène, 96 à 200 px, 56 au moins sur téléphone, 1,3 fois plus pour
  un objet très étroit), plafonnée à `COIN_H_MAX` = 30 % de la hauteur de la scène (27 % sur
  téléphone debout), légende en plus ; 40 % de la largeur au plus (45 % sur téléphone) ; 134 px à
  1280 × 760, 105 px sur téléphone ; plus large que ~190 px, il chevauche la frise du bas sur
  ordinateur et monte avec elle,
  légende « objet » puis « date · musée » ; fondu de 0,8 s et montée de 10 px ; ~5 s depuis le
  passage (un passage dit dans les 4 dernières secondes avance l'entrée) ; place réservée pour la
  caméra **toute la diapositive** (comme le médaillon et les portraits) ;
- manuscrit : sur un côté, entre le cartouche et le bas occupé de ce côté (72 % de la hauteur, 40 % de
  la largeur au plus), ~8 s ; 1 s après l'entrée, zoom doux (2,5 s, logarithmique, 2,4 fois au plus,
  le passage sur ~80 % de la page) puis halo en 1,2 s (même effet que `ev-doc__surligne`) ; ne
  réserve rien pour la caméra (comme la citation) ; mouvement réduit : pas de zoom, halo d'emblée ;
- **deux surimpressions au plus à la fois**, priorités : citation > manuscrit > portraits = médaillon
  de lieu > objet > frise du temps. Le manuscrit ne se montre jamais avec la citation, ni quand
  médaillon et portraits sont déjà là ensemble (raccourci à 5 s au moins ou reporté) ; l'objet cède à
  la citation, au manuscrit, à la surimpression de son coin et à tout moment où deux autres sont là
  (raccourci à 3,5 s au moins, reporté ou omis) ; la frise ne cède plus (révision du 2026-10-09) : elle pousse les autres plus haut ;
- affichage dérivé de l'instant lissé de l'audio (pause, reprise, sauts justes).

`verifier.py` : registre (champs, fichier, licence, crédit CC BY, halo, passage), mentions (une de
chaque au plus, `quand` exact, instant présent, à jour, dans l'audio), fenêtres recalculées comme
dans le lecteur (même code porté en Python : `fenetres_surimpressions`, contrôlé identique au lecteur
sur les 127 diapositives de la Révolution) : jamais plus de deux surimpressions à la fois, jamais
l'objet avec la surimpression de son coin ni le manuscrit avec la citation ; objet omis ou raccourci
en avertissement.

Révolution : 10 objets, 3 manuscrits (liste avec `objets.py revolution --relever`).
1848 et la IIe République (2026-10-12) : 11 objets (dix médailles de Carnavalet et le jeton du banquet réformiste) et
3 manuscrits (laissez-passer de Lamartine, BnF ; brouillon du décret d'abolition annoté par Schœlcher, ANOM ; note de
Hugo sur sa chambre de Bruxelles, Hauteville House).
Monarchie de Juillet (2026-10-11) : 10 objets (sept médailles et jetons de Carnavalet, pièce de 25 centimes de 1847,
chambre à daguerréotype Susse Frères, locomotive Buddicom nº 33) et 4 manuscrits (page de titre de *Notre-Dame de
Paris*, BnF NAF 13378 ; lettre aux maires de Lyon du 20 novembre 1831 ; dépêche de l'arrestation de la duchesse de
Berry ; *Histoire des Girondins*).
Consulat et Empire : 10 objets (pièces de 5 et 20 francs, main de justice, couronne dite de Charlemagne, chapeau,
épée d'Austerlitz, télégraphe Chappe, métier Jacquard, bouteille d'Appert, masque mortuaire) et 3 manuscrits
(Constitution de l'an VIII, proclamation de Golfe-Juan, Acte additionnel). Rien de libre pour une aigle de drapeau
ni une croix de la Légion d'honneur du Premier Empire (2026-10-09). Pas de pique ni de
bonnet de laine d'époque photographiés librement sur Commons ; la dernière lettre de Marie-Antoinette
n'y est qu'en fac-similé de 1872 et la narration ne l'évoque pas ; le procès-verbal du serment du Jeu
de paume n'y est qu'en 1 000 px, signatures illisibles.

## Marges des surimpressions du bas

Spec 12, « Marges des surimpressions du bas » (2026-10-08). Les cartouches du haut et toutes les
surimpressions de coin (médaillon de lieu, portraits, objet, manuscrit) partagent deux variables de
la scène : `--marge-x` (gauche et droite) et `--marge-y` (haut des cartouches, bas des coins) ;
`var(--e-2)` d'ordinaire (téléphone compris), `var(--gouttiere)` et `var(--e-3)` en plein écran. Le
bas des surimpressions suit `--surimp-bas` (posé par `majBasSurimpressions`) : hors plein écran, 0 ;
en plein écran, la hauteur des bandeaux du bas ; contrôles masqués (`inactif`), le sous-titre
descend à leur place (`--descente-st`, transition 450 ms) et les surimpressions avec lui (à la
marge du bas de l'écran si les sous-titres sont coupés) ; elles remontent en douceur (transition de
`bottom`, 500 ms) quand les contrôles reviennent. La place réservée pour la caméra ne dépend pas
des contrôles : elle compte toujours tous les bandeaux (le sous-titre est mesuré sans sa descente).

## Avant / après et mosaïques

Spec 12, « Enrichissements visuels », points 3 et 5 (2026-10-08). Toujours actifs dans le lecteur ;
dans le livre d'images, l'image après sous l'image avant et les vignettes en petite grille ; crédits
dans la section « Mosaïques et avant-après » de la page.

```json
{ "n": 20, "camera_manuelle": true,
  "image": { "commons": "File:La Bastille vers 1780 - dessin - …", "camera": [{ "cadre": [0.25, 0.2, 0.93, 0.66] }], "utile": […],
    "apres": { "fichier": "020-apres.webp", "commons": "File:The Bastille in the first days of its demolition, by Hubert Robert.jpg",
               "titre": "…", "titre_court": "…", "auteur": "Hubert Robert", "date": "1789", "technique": "…", "conservation": "…",
               "licence": "Domaine public", "utile": […], "cadre": [0.085, 0.09, 0.86, 0.58], "quand": "sa démolition commence",
               "camera": [{ "cadre": […], "quand": "passage après le volet" }] } } }
{ "n": 18, "mosaique": { "legende": "Cinq vues de la prise de la Bastille", "principale": 1,
    "vignettes": [{ "commons": "File:…", "titre": "…", "auteur": "…", "date": "1789", "technique": "…", "conservation": "…" },
                  { "commons": "<image de la diapositive>" }, …] } }
```

**Avant / après.** `image` est l'image « avant », `image.apres` l'image « après » (même lieu ou même
sujet, notice complète). `apres.quand` = passage exact qui déclenche le volet ; `apres.cadre` = vue
de l'image après au volet, choisie pour que le même lieu se superpose à la **dernière** vue de la
caméra de l'image avant (mêmes centres et même échelle en pixels : relever deux repères communs sur
les deux images quadrillées) ; `apres.camera` = étapes suivantes (après le volet). Les étapes de
`image.camera` précèdent le volet. `images.py` écrit `NNN-apres.webp` (1600 px, `recadrage` admis),
`utile.py` sa zone utile (clé « 20a »). Mettre `camera_manuelle: true`.

**Cadrage des vignettes (2026-10-09, CE 100).** `vignettes[].cadre` = visage principal de la vignette
(fractions du WebP servi) : `images.py` le remplit à chaque passe (`--vignettes` : seulement ça, local,
sans réseau) depuis les visages YuNet (cache `vignettes-visages.json`) : le plus grand visage net d'au
moins 6 % de la hauteur, un visage du bas de l'image comptant pour un tiers (l'hermine du sacre,
100-m1) ; pas de visage net (scènes de foule : Rév 18, 53, CE 89) : pas de `cadre`. Correction à la main :
`cadre` et `"cadre_manuel": true`. Le lecteur (`decalage` dans `mosaique.ts`) centre la case sur le
centre du `cadre`, borné pour que la zone utile couvre la case (sinon centre de la zone utile).
`verifier.py` (`vignettes_coupees`) : erreur si le visage principal (le `cadre` manuel, sinon le relevé
local) sort de plus de 10 % de la partie affichée, sur quatre scènes (ordinateur 1180 × 450, grand écran
1500 × 720, plein écran 1920 × 1080, téléphone 390 × 390).

**Mosaïque.** 4 à 6 vignettes (`principale` = rang de l'image de la diapositive, dont l'entrée ne
porte que `commons`) ; `legende` = la ligne du cartouche pendant la grille (60 caractères au plus).
`images.py` écrit `NNN-mK.webp` (1000 px) et complète la principale ; `utile.py` leurs zones utiles
(clés « 18m0 »…, à relire sur la planche : marges et légendes gravées). Pas sur la première
diapositive d'un acte (ouverture du carton).

**Lecteur** (`avantApres`, `VOLET`, `MOSAIQUE` dans `src/utils/diaporamas.ts` ; `apresDe`, `raccord`,
`majApres`, `plongee`, `majMosaique` dans `Diaporama.astro`) :
- avant / après : la caméra de l'image avant s'arrête en douceur (vitesse nulle) au passage ; volet
  de **3,5 s** (`clip-path` du calque après, de gauche à droite, smoothstep), bord en ligne verticale
  fine (1 px blanc cassé bordé de gris) ; les deux images sont **fixes** pendant le volet ; la vue de
  départ de l'image après est la vue finale de l'avant transportée par la correspondance des deux
  cadres (respiration comprise) ; la caméra reprend ensuite (première tenue jusqu'à la fin du volet,
  écart de 5 s compté depuis le passage). Cartouche de l'image après dès le début du volet. Mouvement
  réduit : fondu enchaîné de 1 s ;
- mosaïque : grille en 2 lignes (4 → 2 × 2 ; 5 → 2 au-dessus de 3 ; 6 → 3 × 2), filets de papier de
  4 px, chaque vignette couvrant sa case avec sa zone utile ; **révision du 2026-10-08** : la grille est
  entière dès l'entrée de la diapositive (jamais d'apparition une à une sur du blanc), puis chaque
  vignette est **mise en valeur à son tour** (0,9 s chacune depuis 1 s de voix, la principale en
  dernier, fondus de 0,4 s) : en pleine couleur et avancée (échelle 1,03, sans ombre) ; **révision du
  2026-10-09** : une vignette déjà montrée reste en pleine couleur, revenue à l'échelle 1 ; seules les
  vignettes pas encore montrées sont en gris voilé (gris à 85 %, opacité 55 % sur le fond de scène) ; la principale garde sa
  couleur et revient à l'échelle 1 avant la plongée ; tenue de 0,6 s après le dernier tour ; puis **plongée** :
  homothétie de toute la grille (zoom logarithmique, durée selon l'ampleur avec les plafonds de la
  caméra, ~5 s pour une case de la moitié de la scène), la case principale s'agrandit jusqu'à la
  scène entière et l'image principale est alors exactement à sa première vue, où sa caméra commence
  (vitesse nulle aux deux bouts). Cartouche « Cinq vues… » pendant la grille, cartouche normal dès
  le début de la plongée. Mouvement réduit : grille fixe en couleur, sans mise en valeur, puis fondu de
  0,8 s ;
- tout dérive de l'instant lissé de la voix : pause, reprise, sauts et retour au début justes ; la
  clé de reprise d'un avant / après est le fichier Commons de l'image après.

`verifier.py` : fichiers, licences relevées, métadonnées, titre court, zone utile et cadres de
l'image après, passages exacts et dans l'ordre (étapes de l'avant avant le volet, celles de l'après
après), volet tenu dans la voix ; 4 à 6 vignettes présentes et sous licence, `principale` = l'image
de la diapositive, zones utiles, pas sur une ouverture d'acte, grille et plongée tenues dans la voix ;
dosage (3 à 4 avant/après, 2 mosaïques) en avertissement. `renumeroter.py` renomme aussi les
`NNN-apres.webp` et `NNN-mK.webp`.

1848 et la IIe République (2026-10-12) : avant/après 22 (arbre de la liberté planté → abattu, 1850), 45 (la rue
Saint-Maur avant et après l'assaut, daguerréotypes de Thibault), 106 (Louis-Napoléon gravé en 1848 → par Le Gray en
1852) ; mosaïques 6 (barricades de Février) et 40 (journées de Juin).

Monarchie de Juillet (2026-10-11) : avant/après 32 (Louis-Philippe par Gérard → les croquades de Philipon : le roi
changé en poire), 51 (la place Louis XVI → l'obélisque dressé), 54 (Notre-Dame en daguerréotype → la flèche de
Viollet-le-Duc), 65 (l'éléphant de la Bastille → la colonne de Juillet) ; mosaïques 42 (attentat de Fieschi) et 70
(retour des cendres) ; raccords approchés (sujets à des échelles trop différentes pour une superposition exacte).

Consulat et Empire (2026-10-09) : avant/après 5 (David → Delaroche, la propagande et le mulet), 33 (Gros,
*Bonaparte au pont d'Arcole* → Ingres, le trône), 47 (statue de Louis XIV abattue en 1792 → colonne de la Grande
Armée), 66 (Grand Châtelet en démolition, 1802 → fontaine du Palmier) ; cadres relevés sur grille, `camera_manuelle` ;
mosaïques 89 (retraite de Russie) et 100 (cinq portraits de Napoléon, 1802-1814, plongée dans Delaroche).

Révolution : avant/après 20 (la Bastille vers 1780, Lallemand → en démolition, Hubert Robert), 57
(Louis XVI en grand costume royal, Callet → à la barre de la Convention, « Louis Capet »), 59 (la
place Louis-XV, Janinet → l'exécution du roi, Helman d'après Monnet : la guillotine prend la place de
la statue) ; mosaïques 18 (cinq vues de la prise de la Bastille) et 53 (quatre vues de la prise des
Tuileries).

## Chiffres clés et dates républicaines

Spec 12, « Enrichissements visuels », point 4 (2026-10-08). Toujours actifs dans le lecteur ; rien
dans le livre d'images.

```json
{ "n": 92, "narration": "… la loi du 22 prairial ouvre la Grande Terreur : à Paris, plus de mille trois cents exécutions en sept semaines.",
  "chiffres": [{ "quand": "plus de mille trois cents exécutions", "valeur": 1300, "prefixe": "plus de",
                 "unite": "exécutions à Paris en sept semaines",
                 "source": "Antoine Boulant, Le Tribunal révolutionnaire, 2018, p. 185 : 1 376 condamnations…", "instant": 16.91 }],
  "dates_republicaines": [{ "quand": "22 prairial", "republicain": "22 prairial an II", "gregorien": "10 juin 1794",
                            "relu": "« Deux jours plus tard » que la fête du 8 juin 1794 …", "instant": 13.11 }] }
```

**Chiffres** (un au plus par diapositive, ~8 par période) : les nombres les plus parlants **dits par la
voix**, jamais un nombre qui n'y est pas. `quand` = le passage où le nombre est dit, prudence comprise
(« plus de mille détenus ») ; `valeur` = ce nombre, contrôlé par `verifier.py` qui relit le nombre du
`quand` (chiffres ou toutes lettres : `commun.nombre_dit`) ; `prefixe` = la prudence dite (« plus de »,
« près de », « environ »…), obligatoire si elle est dite (le chiffre affiché ne doit pas être plus
affirmatif que la voix) ; `unite` = courte ligne (45 caractères au plus) ; `source` = d'où vient le
chiffre (référence vérifiée, non affichée). Un chiffre douteux ou contesté n'est pas montré.

**Dates républicaines** (une au plus par diapositive) : chaque date du calendrier républicain dite par
la voix (« 9 thermidor an II », « 18 brumaire an VIII », mais aussi « la loi du 22 prairial », « la
constitution de l'an III »). `quand` = le passage dit ; `republicain` = la date complète affichée (année
ajoutée si la voix la tait : « 22 prairial an II ») ou une année seule (« an III ») ; `gregorien` = sa
correspondance, **écrite par `surimpressions.py`** (`commun.date_republicaine`) : jour grégorien du
1er vendémiaire de l'an (an I : 22 septembre 1792, puis 365 jours, 366 après les années sextiles **III,
VII et XI** réellement appliquées, règle de l'équinoxe et tables officielles), plus 30 jours par mois
(13 pour les sans-culottides). La « règle de Romme » (sextiles multiples de 4), jamais adoptée, n'est
pas employée : elle décalerait d'un jour les dates à partir de l'an IV. Une année seule donne
« 22 septembre 1794 – 22 septembre 1795 ». `verifier.py` recalcule chaque correspondance, contrôle le
calcul sur une table de concordance (1er vendémiaire des ans I à XIV) et des dates connues, et demande
qu'elle soit confirmée par la voix, par la date de la diapositive ou par une note `relu` (pour une
année seule : la date de la diapositive doit y tomber).

**Lecteur** (`chiffresDe` dans `src/utils/diaporamas.ts`, `Diaporama.astro`, styles dans
`Surimpressions.astro`) :
- chiffre : centré dans le tiers inférieur (place de la citation), grand serif (15 % de la hauteur de
  la scène, 54 à 112 px ; 40 px au moins sur téléphone), milliers séparés par une espace fine
  insécable (« 300 000 »), prudence au-dessus et unité dessous en petites capitales, sur un voile
  blanc cassé local aux bords fondus ; fondu de 0,6 s et montée de 6 px ; il défile de 0 à sa valeur
  en 1,4 s (courbe qui ralentit, pas ronds de 1, 10 ou 1 000 selon sa grandeur) à partir de 20, sinon
  il paraît en fondu ; ~4 s depuis le passage (3 s au moins) ; il ne réserve rien pour la caméra
  (comme la citation). S'il se montre avec une surimpression de coin bas qui le toucherait, ou avec la
  date, il monte au-dessus d'elle pour toute la diapositive ; avec la frise, au-dessus d'elle.
  Chiffres elzéviriens demandés en CSS (`oldstyle-nums tabular-nums`) mais sans effet avec l'EB
  Garamond de Google Fonts, qui n'a pas ces variantes : chiffres alignés ;
- date : bandeau voilé fin au bas de l'image, au centre (place de la frise), petites capitales,
  « 9 thermidor an II · 27 juillet 1794 » ; ~5 s depuis le passage (3 s au moins) ; au-dessus de la
  frise quand elle s'affiche ; sur téléphone, le cartouche de la musique s'efface pendant le chiffre ou
  la date ;
- **priorités** : citation > manuscrit > portraits = médaillon de lieu > objet ≥ chiffre > date > frise
  du temps. Le chiffre et la date ne se montrent jamais avec la citation ; ils n'entrent pas quand deux
  autres surimpressions sont déjà là (raccourcis, reportés ou omis) ; l'objet, placé avant, garde sa
  fenêtre ; la frise ne cède plus (révision du 2026-10-09) : elle pousse les autres plus haut ;
- mouvement réduit : ni défilement ni montée, fondu de 200 ms.

Prudences reconnues par `verifier.py` (`PRUDENCES`) : « plus de », « près de », « environ », « moins de »,
« quelque », « presque », et depuis le 2026-10-11 « jusqu'à » et « au moins ».

`verifier.py` : champs, `quand` exacts, nombre du `quand` égal à `valeur`, prudence reprise, unité et
source, conversions recalculées, instants présents, à jour et dans l'audio ; fenêtres recalculées
comme dans le lecteur (même code porté en Python, contrôlé identique au lecteur sur les 127
diapositives de la Révolution, 889 fenêtres) et comptées dans la règle des deux surimpressions ;
chiffre ou date raccourcis ou omis en avertissement.

Révolution : 8 chiffres (diapositives 18, 31, 55, 61, 67, 92, 108, 122) et 7 dates (92, 94, 105, 109,
110, 116, 124) ; caméra mesurée à nouveau sur ces 14 diapositives (1280 × 720, 1920 × 1080, 390 × 844) :
rien au-dessus des plafonds, aucun à-coup, rien hors de la zone utile.

## Lecteur : carte des modules

Le script du lecteur (`src/components/Diaporama.astro` ne garde que le gabarit HTML et les styles)
est découpé en modules TypeScript dans `src/scripts/diaporama/`. Ouvrir directement le bon fichier
(chacun commence par 2 à 4 lignes : rôle, données lues, sections de la spec 12 et de ce README).

| Module | Rôle |
| --- | --- |
| `lecteur.ts` | point d'entrée : crée le contexte `lec` de chaque `.diaporama`, installe les modules dans l'ordre |
| `contexte.ts` | type `Lecteur` : état partagé et fonctions échangées entre modules |
| `types.ts` | types des données embarquées (diapositive, suites, frise, segments) |
| `constantes.ts` | réglages : caméra, entrée, ouverture du carton, frise, portraits, musique |
| `geometrie.ts` | calculs purs de caméra (homothétie, profil de vitesse, ampleur, souffle) |
| `horloge.ts` | `maintenant`, `Chrono`, `HorlogeLissee` |
| `outils.ts` | `motsLus`, `lire` / `ecrire` (localStorage protégé), `mouvementReduit`, `mmss` |
| `etat.ts` | données, éléments du DOM, durées et débuts, variables d'état (`lec.i`, `lec.joue`…) |
| `camera.ts` | taille des calques, marges couvertes, vue, plan des transitions, entrée en scène (`arrivee`), `cadreA`, intermède |
| `avant-apres.ts` | image avant / après, raccord, rendu du volet |
| `mosaique.ts` | grille, vignettes, plongée dans l'image principale |
| `plans.ts` | spec 14 : plans d'une diapositive, galerie d'un intermède, images d'une lecture (fondu croisé, caméra par image) |
| `mouvement.ts` | spec 16 : clip d'une image mise en mouvement par IA (`x.video`), posé sur la zone utile avec la transformation de l'image, fondu après l'entrée, joue avec la voix, préchargement |
| `couleur.ts` | spec 16 : version colorisée par IA d'une image (`x.coul`, `p.coul` d'un plan), posée sur la zone utile avec la transformation de l'image, fondu lent calé sur l'horloge de la voix (`opaciteCouleur`), mention du cartouche (`en-couleur`), préchargement |
| `rendu.ts` | préparation des calques, `instant`, `rendre`, boucle d'animation, `montrerImage` |
| `frise.ts` | frise du carton et du bas de l'image, poussée des surimpressions |
| `textes.ts` | cartouche (fondu croisé, estompe) et sous-titre |
| `incrustations.ts` | éléments et tailles : lieu, citation, portraits, objet, manuscrit, chiffre, date républicaine |
| `surimpressions.ts` | chargement des surimpressions d'une diapositive et mise à jour à l'instant t |
| `progression.ts` | temps écoulé, barre des actes, préchargement des images |
| `cartons.ts` | carton d'acte : minuterie, passage, ouverture en deux volets |
| `segments.ts` | segments après la voix (chant, lecture, épisode) sur le lecteur `sa` |
| `chant.ts` | paroles façon clip (`__clip()`) |
| `lectures.ts` | cartes de citation mot à mot (vers compris), éléments relevés une fois (`etats`) |
| `episodes.ts` | panneaux d'épisode (chiffres, barres, cartes, documents) |
| `navigation.ts` | `afficher`, `demarrer`, `pause`, fin de voix, `aller`, `suivant`, écouteurs audio |
| `musique.ts` | musique de fond (Web Audio, gains, fondus, bouton, volume ; `__musique()`) |
| `generique.ts` | générique d'ouverture et récapitulatif de fin : mosaïque, titre, indicatif (`__generique()`) |
| `tests.ts` | `__aller(n, segment)`, `__instant()`, `__camera(n, t)` |
| `controles.ts` | clics, barre des actes, sous-titres, plein écran, redimensionnement, clavier, balayage |
| `reprise.ts` | reprise mémorisée et premier rendu (installé en dernier) |
| `annotations.ts` | spec 15, **mode annotation seulement** (import dynamique sous `__ANNOTATIONS__`, absent du site déployé) : touche A, panneau, liste, repères ; styles injectés par le module |

**Conventions.** Chaque module exporte `installerX(lec)`. Ce qu'il emprunte aux modules installés
avant lui est déstructuré en tête (`const { D, audio, rendre } = lec;`) ; ce qu'il expose est publié
par `Object.assign(lec, { … })` (fonctions en tête, constantes en fin) et déclaré dans
`contexte.ts`. Une fonction d'un module installé **après** s'appelle `lec.f()` ; une variable d'état
partagée se lit et s'écrit toujours `lec.x` (jamais déstructurée : elle changerait sans qu'on le
voie). L'ordre d'installation de `lecteur.ts` reproduit l'ordre d'origine des écouteurs : ne pas le
changer sans raison. `grep -n "nomDeFonction" src/scripts/diaporama/*.ts` suffit à tout retrouver.

## Générique d'ouverture et récapitulatif de fin

Spec 12, révision du 2026-10-09. Données : `"generique": ["File:…", …]` dans le JSON de la période,
8 à 12 fichiers Commons (pas des numéros : ils survivent aux renumérotations), une ou deux images
par acte au plus, dans l'ordre de la mosaïque (première moitié en haut, seconde en bas). Choix
éditorial justifié dans le journal (`docs/journal/generique.jsonl`). L'indicatif est commun :
`src/data/diaporamas/commun/indicatif.json` (source, licence, extraits `ouverture` et `fin` :
`debut`, `fin`, fondus ; `duree` et `empreinte` écrites par `musique.py --indicatif`, -16 LUFS,
128 kb/s, `mono: true` pour un pressage « stéréo » électronique), fichiers dans
`public/diaporamas/commun/`. Crédité en bas de chaque page de période et sur le portail.

- Valeurs retenues : thème original composé avec Lyria (`lyria-3.5`, candidat 08 « marche, plus de
  cordes », généré le 2026-10-09 ; morceau brut, consigne et découpe : `.cache/diaporamas/
  indicatif-original/`, `docs/journal/indicatif-original.jsonl`). `indicatif.json` porte `credit`
  (« Indicatif composé avec Lyria (Google DeepMind) », exigé par Google, affiché tel quel) et
  `licence` (« Création originale générée par IA pour le site »), la consigne et, par extrait,
  `accord` (instant de l'accord final). Ouverture : 16,8 s, comptée jusqu'à l'accord (14,55 s) :
  le premier carton monte dessus, la résonance continue sans fondu. Récapitulatif : 15,7 s, « Fin »
  sur l'accord (10,25 s). `musique.py --indicatif` ne fait rien pour une source `lyria`.
- Lecteur : `Generique.astro` (gabarit, styles ; images en `data-src`, chargées au lancement) et
  `generique.ts`. Enfant de `.lecteur` (pas de la scène) : mosaïque bord à bord en trois rangées,
  voile sombre, titre et dates en grand (unités `cqw`/`cqh`) ; `caler()` arrête le bas à la barre
  des actes (0 en plein écran, où il passe sous les bandeaux). L'ouverture remplace le premier `afficher(0)` de `lancer` (pas à une reprise),
  puis `aller(0)` : le premier carton monte pendant que le générique s'efface. Le récapitulatif
  part de `suivantAuto` après la dernière diapositive, finit par la pause et l'oubli de la position.
  Passables comme un carton (→, clic, Entrée). Tout saut (`aller`, `afficher`) les quitte.
  Comptés dans la durée : `etat.ts` décale `debuts` de l'ouverture, le premier acte de la barre
  commence à 0 et le dernier finit après le récapitulatif ; la musique de fond se cale sur
  `debuts[bornes[a].de]` (et non `t0`). Pendant le générique, la musique de fond se tait.
- Minutage (constantes `O` et `F` de `generique.ts`, calées sur l'indicatif) : vignettes en fondu
  (0,2 s), titre lettre à lettre (dès 0,4 s), filet, dates (6,4 s), couleur vignette par vignette
  (3,2 à ~11 s), dérive de 8 % de la largeur ; récapitulatif : retour en couleur, passage au gris
  de 1,2 s à 1,6 s avant l'accord, assombrissement, « Fin » sur l'accord, titre et dates 1 s après. Mouvement réduit :
  pas de dérive, fondus courts. Changer d'indicatif : revoir ces constantes et les `accord`.
- Captures : instants `o:T` et `f:T` ; les autres instants passent l'ouverture sans temps écoulé.

## Vérification par étape et solde Gemini (spec 13)

**`verifier.py <slug> --etape A|B|C`** n'exécute et n'affiche que les contrôles d'une étape de
production : une ligne de bilan par famille, les erreurs, puis 15 avertissements au plus (`--tout`
pour tous). Code de sortie 1 s'il y a des erreurs de l'étape. Sans `--etape`, rien ne change.

| Étape | Familles de contrôles |
| --- | --- |
| A (texte, images, prévus) | structure, images, narration, dates, dosage (enrichissements, lectures et épisodes prévus), richesse des épisodes, générique |
| B (voix, zone utile, caméra, musique) | audio, ouverture, zone utile, caméra, musique, registre musical, lectures et épisodes, boucles |
| C (surimpressions, vérification) | surimpressions, portraits, objets et manuscrits, chiffres et dates, avant/après et mosaïques, puis **tout** (vérification complète, sortie résumée) |

À l'étape A, les lectures ne sont pas comparées à Wikisource (contrôle de l'étape B, sans réseau en A).
Contrôle de la répartition : `python3 scripts/diaporamas/tester_etapes.py consulat-empire` (la
réunion des messages de A, B et C doit égaler la vérification complète ; A et B sans message commun).

**Solde Gemini.** L'API ne donne pas le solde des crédits prépayés : `gemini.py` le tient.

- Chaque appel est ajouté à `.cache/diaporamas/gemini-depenses.jsonl` (date, script, tâche, modèle,
  jetons, dollars estimés).
- Après une recharge : `gemini.py --crediter 10` (le crédit disponible à cet instant) ;
  solde estimé = crédit − dépenses depuis. C'est une **estimation** (tarifs indicatifs).
- `gemini.py --solde` : solde estimé, dépense des 7 derniers jours par script, et **sonde** (un
  appel d'un jeton). Code 0 : crédits disponibles ; 2 : crédits épuisés ; 1 : pas de réponse.
  Fonctionne sans crédit déclaré (dépenses et sonde seulement).
- Tout script payant (`voix.py`, `utile.py`, `camera.py`, `portraits.py`, `paroles.py`,
  `banc_gemini.py`) sonde une fois avant son premier appel, et refuse de démarrer si les crédits
  sont épuisés ou si `--budget` dépasse le solde estimé. `--sans-sonde` saute ce contrôle.
  `surimpressions.py` n'appelle pas Gemini.
- Un 402 en cours de route arrête le script comme le plafond `--budget` : ce qui est fait est écrit.
- Essai sans dépense : `DIAPORAMAS_GEMINI_SIMULER=402 python3 scripts/diaporamas/utile.py <slug> --n 5 --budget 0.05`.

## Plans, lectures illustrées et galeries (spec 14)

Deux fois plus d'images à narration identique (spec 14). Quatre champs, tous facultatifs : une
période qui n'en a aucun se joue exactement comme avant. Partout, `image` a le format de l'image
d'une diapositive (`commons`, `titre`, `titre_court`, `auteur`, `date`, `technique`, `conservation`,
puis `fichier`, `licence`, `largeur`, `hauteur`, `utile`, `camera` écrits par la chaîne ; `recadrage`
et `utile_manuel` admis).

```jsonc
// 1. Plans : sur une diapositive (1 ou 2 ; pas avec image.apres ni mosaique). Fichiers NNN-b.webp, NNN-c.webp.
"plans": [{ "quand": "Des toits pleuvent les tuiles", "instant": 9.58, "image": { … } }]
// 2a. Lecture illustrée : dans lectures[] (2 à 4 images ; `quand` = mots du texte lu, facultatif
//     sinon réparties également ; la première est là dès le début). Fichiers lectures/<id>-<k>.webp.
"images": [{ "image": { … } }, { "quand": "Georges la Fayette passa un drapeau", "image": { … } }]
// 2b. Panneau d'épisode : dans episodes[].visuels, jamais en premier. Fichier episodes/<id>-<k>.webp.
{ "type": "image", "quand": "La Chambre nouvelle est dissoute", "legende": "Phrase facultative.",
  "position": "50% 35%", "image": { … } }
// 3a. Galerie d'un intermède existant : dans musique.intermedes[] (3 à 5 images, réparties sur
//     l'extrait ; `instant` facultatif, en s de l'extrait). Fichiers galeries/<id>-<k>.webp.
"galerie": [{ "image": { … } }, { "image": { … } }, { "image": { … } }]
// 3b. Galerie nouvelle sans voix : un intermède instrumental de plus, avec `theme` (20 à 30 s).
{ "id": "galerie-barricades", "apres": 101, "fichier": "musique/galerie-barricades.m4a",
  "titre": "…", "auteur": "…", "date": "…", "interprete": "…", "enregistrement": "…",
  "source": { … du registre ou d'une piste de fond … }, "licence": "…", "debut": 96, "fin": 121,
  "fondu_entree": 1.5, "fondu_sortie": 2.5, "instrumental": true, "paroles": [],
  "cartouche": { "oeuvre": "…", "compositeur": "…" },
  "theme": "Paris en armes : les barricades de juillet 1830", "galerie": [ … ] }
```

**Ordre des scripts** (tous idempotents ; seuls `utile.py` et `camera.py` paient Gemini, `--budget`
obligatoire ; ~0,002 $ par zone utile, ~0,005 $ par image cadrée par le modèle) :

```sh
python3 scripts/diaporamas/images.py restauration --n 100,102,106      # téléchargement, licence, notice
python3 scripts/diaporamas/utile.py restauration --budget 0.10         # zone utile des images nouvelles
python3 scripts/diaporamas/musique.py restauration                     # galerie nouvelle : son extrait
python3 scripts/diaporamas/surimpressions.py restauration              # `instant` des plans (avant camera.py)
python3 scripts/diaporamas/camera.py restauration --n 100 102 --budget 0.20   # « 100 » : l'image et ses plans
python3 scripts/diaporamas/camera.py restauration --audit              # puis --reparer --n … (gratuit)
python3 scripts/diaporamas/verifier.py restauration --etape C --hors-ligne
python3 scripts/diaporamas/captures.py restauration 100:p1+0.4 100:p1+3 109:g2+5 101:g3 --planche
```

- **Plans.** `quand` : mots exacts de la narration, cherchés après le plan précédent ; choisir le
  **début d'une phrase**. `surimpressions.py` écrit `instant` : 0,3 s avant le passage, ou avant le
  début de la phrase si le passage est dit dans les 1,5 s qui le suivent (le fondu de 0,8 s tombe
  dans le silence). Chaque image reste **5 s au moins** (`verifier.py`, étape C : erreur) : la
  première aussi, donc pas de plan sur une phrase qui commence avant 5,3 s, ni à moins de ~5 s de la
  fin de la voix ; trois images demandent ~16 s et deux coupures bien placées (rare). Un plan qui
  commence pendant une citation ou un chiffre affiché est signalé (avertissement).
- **Caméra d'une diapositive à plans.** `camera.py` travaille sur des « vues » (`commun.vues_camera`) :
  l'image principale n'est cadrée que sur la narration dite avant le premier plan (sa caméra est
  donc **refaite** quand on ajoute un plan : empreinte changée), chaque plan (« 100b ») sur la
  narration de sa fenêtre, minutage compté depuis son début. Les `quand` de la caméra d'un plan sont
  pris dans cette fenêtre ; le lecteur les cherche à partir du début du plan. Clés de cache et de
  planche : `100`, `100b`, `100c`. `--audit` et `--reparer` connaissent les plans. Un plan a son
  `camera_manuelle` (dans l'entrée du plan, à côté de `quand`).
- **Images sans narration** (lecture, galerie) : `camera.py` leur écrit **un seul cadre**, local et
  gratuit (toute la largeur de la zone utile, bande posée sur les visages YuNet ; sinon un peu
  au-dessus du centre), dès que `utile` existe ; `--n galerie:<id>:2` ou `--force` le refait. Le
  corriger à la main si le sujet est coupé (le cadre n'est pas réécrit tant qu'il existe).
- **Zone utile.** Clés `100b`, `lecture:dumas:1`, `galerie:<id>:2` (`utile.py --n` les accepte). Une
  estampe à grandes marges est souvent **refusée** (zone < 50 %) : ne pas saisir une petite zone,
  mais écrire `recadrage` (la zone proposée par le modèle, lue dans la sortie), relancer `images.py`
  puis `utile.py` : l'image servie est nette. Le fichier pèse alors plus (jusqu'à ~800 Ko).
- **Doublons.** Une image de la spec 14 déjà employée dans la période (diapositive, image après,
  vignette, autre image de la spec 14) est une erreur ; `"reprise": true` dans l'entrée (à côté de
  `image`) l'admet pour un détail voulu. État des licences : `.cache/…/images.json`, clés
  `spec14:<genre>:<fichier Commons>`.
- **Lecteur** (`plans.ts`) : les images d'une série sont posées dans `.lecteur__plans` du calque
  (créées par le script : leurs styles sont en `:global`, comme la mosaïque). Plans : horloge de la
  voix, fondu `FONDU_PLAN` (0,8 s) qui **commence à `instant`** ; galeries et lectures : horloge du
  segment, `FONDU_GALERIE` (1,2 s). Chaque image est une vue dérivée (`planDe`) : sa zone utile, sa
  caméra, sa fenêtre ; sa tenue a commencé `ELAN_PLAN` s plus tôt (elle entre en mouvement). Le
  cartouche suit l'image (`legendeVoulue`, `legendeGalerie`). Lecture illustrée : carte
  `citation--illustree` (voile translucide, légende `.citation__image`), et l'image suivante entre
  en fondu enchaîné ordinaire (la carte ne couvre plus). Mouvement réduit : cadre fixe, fondu 0,3 s.
- **Renumérotation** : `renumeroter.py` renomme `NNN-b.webp` ; relancer `images.py` ensuite.
- **`verifier.py`** : famille « plans et galeries » aux étapes A (fichiers, licences, notices,
  doublons, passages), B (zone utile, caméra), C (instants, durées) ; ligne « Images : n dont p
  plan(s)… » ; avertissement de dosage sous 200 images (période ≥ 3 ou déjà enrichie).
- **Piège de capture (élucidé le 2026-10-11)** : sur la diapositive 99 (mosaïque, après la plongée), la même
  capture donnait deux images sur un **même** build, y compris celui d'avant la spec 14 : la photo
  « pleine page » de Playwright redimensionne la fenêtre émulée, et le lecteur redessine l'image
  pendant la prise (transformation modifiée en cours de photo). Ce n'était pas une régression du
  conteneur `.lecteur__plans` (état du DOM identique dans les deux builds). `captures.py` photographie
  désormais la fenêtre quand le lecteur y tient (résultat stable, identique à l'ancien hors de ce cas).
- **Plan d'une diapositive qui ouvre un acte** (1, 14, 40, 59…) : l'ouverture en volets suit le temps
  réel ; capturer avec `--attente 9000`, sinon l'image principale est encore à l'écran.
- **Poids** : une image de la spec 14 ne dépasse pas ~400 Ko (`POIDS_MAX_SUP` d'`images.py` : qualité
  abaissée par paliers jusqu'à 56, puis taille réduite par paliers de 10 %, jamais sous 1 200 px).
- **Portraits serrés** : l'écran ne montre qu'une bande d'environ un tiers de la hauteur d'une image
  en hauteur ; un portrait dont le visage occupe plus du tiers de l'image ne peut pas être montré
  entier (plans retirés pour cette raison en période 03 : David par Navez, Musset, Charles X par
  Tardif). Préférer les portraits en buste ou en pied, ou cadrer à la main (`camera_manuelle`).

## Captures (contrôle visuel et non-régression)

`captures.py` photographie le lecteur à des instants précis, avec une horloge entièrement factice
(`page.clock` de Playwright pour `performance.now`, les minuteries et `requestAnimationFrame`, et un
faux moteur audio qui avance avec elle) : deux passages sur le même build donnent les mêmes pixels.

```sh
npx astro build --outDir dist-xxx            # ou npm run build (dossier dist)
python3 scripts/diaporamas/captures.py revolution 1:c5 2:12.5 20:5.5 7:s20 --dist dist-xxx \
  --appareil les-deux --sortie /chemin/avant --planche
# … modification, nouveau build …
python3 scripts/diaporamas/captures.py revolution 1:c5 2:12.5 20:5.5 7:s20 --dist dist-xxx \
  --appareil les-deux --sortie /chemin/apres --comparer /chemin/avant
```

- Plan : `n` ou `n:t` (voix de la diapositive n à t s, 2 par défaut, en pause), `n:sT` (segment après
  la voix, à T s), `n:cT` (carton de l'acte qui commence à n, T s après son début), `o:T` et `f:T`
  (générique d'ouverture, récapitulatif de fin) ; `n:pK`, `n:pK+D`, `n:pK-D` (plan K de la diapositive n, D s après
  son instant, 2 par défaut ; `+0.4` : milieu du fondu) et `n:gK+D` (image K de la galerie ou de la lecture
  illustrée jouée après n) : spec 14. Depuis le générique, la barre de progression et
  le temps écoulé diffèrent d'un build antérieur (décalés de l'ouverture) : comparer les autres zones.
- `--appareil ordinateur|telephone|les-deux` (1280 × 760, 390 × 844) ; fichiers `o-<n_t>.png`,
  `t-<n_t>.png` ; `--planche` : `planche.png` (3 colonnes, légendées) ; `--attente` : ms d'horloge
  factice avant de poser l'instant (2 500 par défaut : entrée finie, frise du bas encore là).
- `--comparer DOSSIER` : différence pixel à pixel avec les PNG de même nom, `ecart-<nom>.png` pour
  chaque écart, code de sortie 1 s'il y en a. Ne regarder que les écarts.
- Serveur statique intégré sur un port libre (`astro preview` refuse une seconde instance) ;
  Chromium du cache Playwright trouvé automatiquement (le plus récent ; `PLAYWRIGHT_BROWSERS_PATH`
  respecté). Chaque capture se fait dans un onglet neuf (pas de reprise mémorisée ; « date
  précédente » de la frise : la diapositive 1).
- Limites connues : l'ouverture en volets (dernières 3,5 s d'un carton, et les images d'un début
  d'acte juste après) passe par des Web Animations en temps réel, donc non reproductibles ; quelques
  pixels de la barre de progression peuvent varier dans les captures de carton (bruit mesuré entre
  deux passages identiques : 1 à 70 px). Faire deux passages de référence pour connaître le bruit.
- Plan de non-régression du découpage du lecteur (32 captures ; instants `n:sT` revus le 2026-10-12
  après les renumérotations : un `n:sT` sur une diapositive sans segment fait planter tout le
  passage) : Révolution `1:c5 15:c7 4:4 4:11 2:12.5 5:4 14:10.5 21:12 94:12 92:13.8 92:17.5 20:5.5
  18:3 7:s20 61:s30 76:s15 97:s10 109:s20` (+ téléphone `1:c5 2:12.5 7:s20 20:5.5`) ; Consulat et
  Empire `1:c6 89:3.5 90:s15 116:s20 67:s25 3:s10 107:5 109:s30` (+ téléphone `67:s25 90:s15`).
  `76:s15` (Révolution) varie de quelques dizaines de pixels entre deux passages du même build.
  Diapositives à segment d'une période : les `apres` de ses lectures, épisodes et intermèdes.

## Caméra proposée par Claude (banc_claude.py)

`banc_claude.py` fait proposer la caméra par des sous-agents Claude (Sonnet retenu, à partir de la
période 04), sans API : il écrit des fichiers de tâche qu'un agent lit (image comprise, par son
outil Read) et auxquels il répond par un JSON ; les réponses passent par les contrôles de
`camera.py`. 0 $. Seuls `appliquer` et `restaurer` écrivent dans le JSON de la période et dans
`.cache/diaporamas/<slug>/camera.json` ; le reste tient dans `.cache/diaporamas/banc-claude/<horodatage>/`.

Procédure pour une période (après `utile.py` et `surimpressions.py`, qui fixent zones utiles et `instant` des plans) :

1. `python3 scripts/diaporamas/banc_claude.py preparer <slug> --toutes --etiquette sonnet`
   (`--statiques` : seulement les vues sans caméra ou qui tiennent un cadre plus de 7 s ; `--n 12 100 100b` :
   ces vues ; `--lot 15` : taille des lots). Une tâche par vue de `commun.vues_camera` (chaque image
   d'une diapositive à plans a la narration et le minutage de sa fenêtre : `tache-100.md`, `tache-100b.md`),
   en lots `lot-K/` avec chacun son `LISEZMOI.md`. Exclus : `camera_manuelle`, plans sans `instant`,
   avant/après, image principale d'une mosaïque ; lectures et galeries restent à `camera.py`.
2. Un sous-agent par lot : « Lis `<dossier>/lot-K/LISEZMOI.md` et suis-le » ; il écrit `reponse-NNN.sonnet.json`.
3. Second tour (facultatif) : `… relire <dossier>/lot-K [--fautives]` écrit `retour-NNN.sonnet.md`
   (erreurs à corriger, ou relance des tenues longues et relecture des cadres dessinés) ; l'agent
   relit et réécrit sa réponse.
4. `… noter <dossier>` : `comparatif.md`, `comparatif.json`, `planche-NN.jpg` (caméra du JSON et de
   chaque étiquette ; mesure de `banc_gemini.py` : vues, visages, tête hors champ, étapes ignorées, repli).
5. `… appliquer <dossier> --essai` puis sans `--essai` : pose les caméras acceptées ou réparées, sans
   erreur ni repli, d'au moins autant d'étapes que l'actuelle (`--strict` : plus d'étapes ou tenue plus
   courte), sur les vues inchangées depuis la préparation. Sauvegarde `sauvegarde-<horodatage>.json` ;
   `… restaurer <dossier>` remet les caméras remplacées (celles changées depuis sont laissées, sauf `--force`).

Entrée en scène (2026-10-12) : la tâche d'une image qui peut en recevoir une (ni portrait, ni document,
ni `ouverture`, ni avant/après, ni mosaïque, ni clip, ni première image d'un acte) porte une section
« Entrée en scène » (répertoire de mouvements, règle de fenêtre) et attend un champ `entree` (ou
null) dans la réponse ; `appliquer` le pose avec la caméra s'il passe `entree.depuis_camera` (règle de
fenêtre contre la caméra retenue, mouvement perceptible, zoom ≤ ×2,4, durée permise). Relire ensuite
sur planche (`captures.py`) et vérifier par `entree.py plans` / `etapes`.

Pièges :
- Une réponse refusée par le contrôle n'est pas renvoyée au modèle (sauf `relire`) : elle est réparée
  comme par `camera.py --reparer`, sinon repli sur une étape (jamais appliqué).
- Les narrations n'ont pas de minutage par mot (`audio.mots` n'existe que pour les lectures) : la tâche
  donne l'instant de chaque mot au prorata dans sa phrase, comme `camera.instants` (ce que vérifie le contrôle).
- Protection : `appliquer` remplace l'entrée de la vue dans le cache `camera.json` (empreinte actuelle,
  `source: "claude:<étiquette>"`) ; `camera.py <slug>` ne refait donc pas ces caméras, mais
  `camera.py --force` les referait. Ne pas lancer `appliquer` / `restaurer` pendant qu'un `camera.py`
  tourne sur la période (il réécrit son cache en entier).
- Banc d'essai (comparaison à Gemini) : `preparer camera consulat-empire` sans option reprend les
  diapositives du dernier `banc_gemini.py camera` et y ajoute cinq autres ; `… factice <dossier>` écrit
  des réponses d'essai tirées du JSON.

## Annotations de visionnage (spec 15)

Outil **local** : l'utilisateur regarde un diaporama, note d'une touche ce qu'il faut corriger ;
Claude relit ces notes avec leur contexte. **Avant de retoucher un diaporama, lire
`python3 scripts/diaporamas/annotations.py lister <slug> --a-faire`.**

```sh
npm run annoter                      # build en mode annotation (dist-annotations/) + serveur local, port libre affiché
python3 scripts/diaporamas/annoter.py --port 4330 [--sans-build] [--sans-capture]
python3 scripts/diaporamas/annotations.py lister restauration [--a-faire] [--categorie cadrage]
python3 scripts/diaporamas/annotations.py lister restauration --detail 142512-037   # tout le contexte + chemin de la capture
python3 scripts/diaporamas/annotations.py traiter 142512-037 "tête recadrée (camera_manuelle)"
python3 scripts/diaporamas/annotations.py bilan restauration
```

- **Rien dans le site déployé.** `astro.config.mjs` définit `__ANNOTATIONS__` (vrai seulement si
  `ANNOTATIONS=1`, posé par `annoter.py`) ; `lecteur.ts` n'importe `annotations.ts` que sous cette
  condition, éliminée au build normal (pas de module, pas de style : `grep -ri annot dist/` ne trouve
  que du contenu éditorial, « Johannot »). Le build d'annotation va dans `dist-annotations/`
  (ignoré par git) : `dist/` et `astro preview` ne sont pas touchés.
- **Serveur** (`annoter.py`, bibliothèque standard) : `127.0.0.1` seulement, fichiers statiques avec
  requêtes Range, point d'écriture `/__annotations/<slug>[/<id>]` (GET, POST, PUT, DELETE ; même
  origine exigée) qui n'écrit que sous `docs/annotations/` ; écritures atomiques (`annotations.py`).
- **Raccourcis** (mode annotation) : **A** pause + panneau ; catégorie par **1…7 tant que le champ
  est vide**, **Alt+1…7**, **Tab / Maj+Tab** ou clic (1 image, 2 cadrage, 3 texte, 4 voix, 5 musique,
  6 surimpression, 7 autre ; défaut : autre) ; **Entrée** enregistre et reprend, **Maj+Entrée** saut
  de ligne, **Échap** annule et reprend (texte vide : rien d'écrit). **L** (ou clic sur le compteur) :
  liste ; ↑ ↓, **Entrée** ou clic saute à l'instant annoté en pause, **E** modifie, **Suppr** supprime
  après confirmation (Entrée ou O), **Échap** ferme. Tant que le panneau ou la liste est ouvert, les
  raccourcis du lecteur sont suspendus (écouteur en phase de capture sur `window`).
- **Format** : `docs/annotations/<slug>.jsonl`, une ligne par annotation (spec 15) ; `id` =
  `AAAAMMJJ-HHMMSS-NNN` (heure du navigateur, NNN = diapositive ; `annotations.py` accepte la fin de
  l'identifiant s'il est unique). Le lecteur relève `lieu` et `ecran` à l'instant de la pause ; le
  serveur complète l'identifiant de l'acte, `image.commons` / `titre_court` et la `phrase` exacte de
  la narration (`audio.phrases`). Champs nuls selon l'état : `camera` hors diapositive et plan ;
  `image` pendant un carton, un générique ou un épisode ; `phrase` pendant un carton, un générique,
  une galerie instrumentale ; `n` et `acte` pendant le générique et le récapitulatif. `lieu.type` :
  `chant` pour un intermède à paroles (même illustré : `image_galerie` renseigné), `galerie` pour une
  série d'images sur un extrait instrumental. `sous_titre` : texte affiché (toute la narration de la
  diapositive), `null` si les sous-titres sont coupés.
- **Capture** : faite **par le serveur**, en tâche de fond (quelques secondes), en rejouant le lecteur sans tête au
  même instant avec `captures.capturer` (horloge factice, fenêtre de l'utilisateur, sous-titres comme
  chez lui, lecteur sans l'outil), puis JPEG de 1 280 px au plus dans `docs/annotations/<slug>/<id>.jpg`
  et champ `capture` complété (`null` en attendant, ou si Playwright manque). Pas de capture dans le
  navigateur : redessiner le DOM (transformations, calques, flous) demanderait une bibliothèque lourde
  et infidèle, et la capture d'onglet une autorisation à chaque page. Limites : c'est une reconstitution
  (pas le plein écran, pas l'état exact d'un fondu d'entrée ni de l'ouverture en volets, frise du bas
  calculée depuis la diapositive 1). Les captures manquantes sont retentées au lancement suivant.
- **Panne du serveur** : message dans le panneau, qui reste ouvert ; copie de secours dans
  `localStorage` (`annotations-secours:<slug>`), renvoyée à l'annotation suivante ou au rechargement
  (même `id` : pas de doublon) ; le compteur indique « n en attente d'envoi ».
- **Saut depuis la liste** : diapositive, plan et segment à l'instant exact ; carton, générique et
  récapitulatif à leur début (carton de l'acte, première ou dernière diapositive).
- **Marquer traité** : `annotations.py traiter` ; le lecteur l'affiche (repère gris clair, ligne
  grisée avec le traitement) après rechargement ou réouverture de la liste.

## Images entières sur fond noir, repères des cartons (retours du 2026-10-11)

Spec 12, « Retours du visionnage de la Restauration (2026-10-11) ».

**Image entière (`image.entier`).** Valable pour l'image d'une diapositive, d'un plan et d'une
galerie ; sans effet sur un avant / après ou une mosaïque ; pas sur les images de lecture.

```jsonc
"image": { …, "entier": true,                       // image entière, bandes noires de côté
  "entier_vers": [0.18, 0.03, 0.68, 0.55],          // sujet du rapprochement (fractions de l'image servie)
  "entier_zoom": 1.15,                              // zoom final (1 à 2 ; absent : 1,3)
  "entier_manuel": true }                           // réglage à la main : le script n'y touche plus
```

```sh
python3 scripts/diaporamas/camera.py restauration --entiers             # pose ou retire le drapeau (gratuit)
python3 scripts/diaporamas/camera.py revolution --entiers --simuler     # compte seulement, n'écrit rien
python3 scripts/diaporamas/camera.py restauration --entiers --n 22 54b --seuil 0.55
```

- **Règle** (`entier_propose`) : entier si la bande bord à bord (`RATIO_VUE` 2,5:1) montre moins de
  `SEUIL_ENTIER` (50 %) de la hauteur de la zone utile, ou si la tête d'un portrait d'une personne
  seule (`TETE_ENTIER` : 1,35 hauteur de visage) ne tient pas dans la bande. `entier_vers` : la tête
  du portrait (`sujet_portrait`, visage agrandi) ; sinon le dernier cadre de `image.camera` s'il est
  plus petit que la zone utile ; sinon rien (centre). `entier_zoom` : 1,3, abaissé par pas de 0,05
  tant qu'un visage d'au moins 6 % de la hauteur n'est pas entier dans la vue finale, pour cinq
  formes de scène (`SCENES_ENTIER` : téléphone, ordinateur, plein écran avec sous-titres).
- **Idempotent** : relancer après `utile.py` et `camera.py` (la zone utile et les cadres servent à
  la règle) ; une image qui ne répond plus à la règle perd son drapeau. `entier_manuel: true` la
  protège (pour forcer bord à bord : `"entier": false, "entier_manuel": true`).
- **À relire sur planche** : un portrait dont `recadrage` ou `utile` rogne la tête reste rogné
  (39 et 40 de la Restauration : recadrage et zone utile repris à la main) ; un zoom à 1 (image
  fixe) signale un visage au bord de l'image.
- **Lecteur** : `camera.ts` (`zoneEntier`, `vueZoom`, `vueEntier`, `finEntier`, `cadreEntier`, branche
  `entier` de `parametres`), `plans.ts` (fond `.lecteur__noir` d'une image de série), `rendu.ts`
  (fond noir du calque), constantes `ENTIER_*`. `image.camera` reste exigé par `verifier.py` mais
  n'est pas joué. `verifier.py` (étape A, « repères et images entières ») contrôle les champs.
- **Périodes 01 et 02** : aucun drapeau posé (décision de l'utilisateur attendue) ; la règle en
  basculerait 52 sur 122 (Révolution) et 39 sur 108 (Consulat et Empire) ; 73 et 55 au seuil de 55 %.

**Dates clés d'un acte (`actes[].reperes`).** **Plus affichées depuis le 2026-10-12** (annotations
de visionnage : la période de l'acte est mise en couleur à la place, `frise.ts` : `poserActe`,
`majFriseCarton` ; constantes `CARTON_*`). Le champ reste admis et contrôlé, sans effet à l'écran.
Facultatif, 2 ou 3 par acte.

```jsonc
{ "id": "ultras", "titre": "Les ultras au pouvoir", "dates": "1820-1824", "debut": 40,
  "reperes": [ { "date": "1821-12", "libelle": "Ministère Villèle" },
               { "date": "1830-07-27", "date_fin": "1830-07-29", "libelle": "Les Trois Glorieuses" } ] }
```

Dates au format des diapositives (`AAAA`, `AAAA-MM`, `AAAA-MM-JJ`), prises dans la narration de
l'acte ; libellé de 36 caractères au plus (avertissement au-delà). Le compteur d'années ne défile
que si `dates` vaut « AAAA-AAAA ».

**Médaillons de portrait** : hauteur moyenne entre l'ancienne taille et celle du 2026-10-09
(`taillePortraits` dans `incrustations.ts`) ; `COIN_H_MAX` ne règle plus que le plafond de la
grande taille et les objets.

**Captures** : `captures.py --fenetre 1512x945` (taille de la fenêtre de l'ordinateur) et
`--reduit` (prefers-reduced-motion).

## Couche générée : images mises en mouvement (spec 16)

Le calcul se fait sur **Google Colab Pro** (abonnement de l'utilisateur, aucun appel Gemini) avec le
modèle à poids ouverts Wan 2.2 TI2V-5B, piloté depuis le Mac par la **CLI officielle `colab`**
(google-colab-cli, `uv tool install google-colab-cli`, déjà installée ; `colab usage` donne le solde
d'unités). Rien ne tourne ici : le Mac prépare le kit, ouvre une session, suit le journal de bord,
rapatrie, arrête la session, encode, montre, puis publie.

Procédure d'un lot (une dizaine de diapositives à scène animable, décision du 2026-10-12, plafond
15 : fumées, drapeaux, foule, eau, ciel ; jamais un portrait, jamais une inscription lisible) :

```sh
# 1. Le lot : src/data/diaporamas/generation/<slug>.json (n, type « mouvement », prompt anglais, graine ;
#    « negatif » et « modele » communs). Consigne : les mouvements voulus, « Keep exactly the look of
#    this … », « nothing new appears, no text » ; « flags flutter » avec parcimonie (Valmy : drapeau démesuré).
python3 scripts/diaporamas/generation.py preparer revolution     # .cache/diaporamas/revolution/generation/kit-mouvement.zip
python3 scripts/diaporamas/generation.py lancer revolution        # session A100 (--high-mem : 80 Go), 5 min (121 images) à 12 min (241) par clip
#   --seulement 18,56  --profil rapide  --sans-essai  --garder (laisse la session ouverte)  --session nom
open .cache/diaporamas/revolution/generation/planche-mouvement.html   # juger ; retirer du lot ou relancer (--seulement) les ratés
python3 scripts/diaporamas/generation.py publier revolution       # clips → public/, champ image.video (--seulement n,n)
python3 scripts/diaporamas/verifier.py revolution && npm run build
# Un clip qui déplaît après coup : generation.py retirer revolution --seulement 56
```

Voie manuelle de secours (sans CLI) : `scripts/colab/mouvement.ipynb` dans l'interface Colab
(Fichier › Importer le notebook, GPU L4 ou A100, Exécution › Tout exécuter, envoyer le kit quand il est
demandé ; `resultats-mouvement.zip` téléchargé à la fin), puis
`generation.py encoder revolution ~/Downloads/resultats-mouvement.zip`. Le 2026-10-11, l'import du
.ipynb par l'extension Chrome est resté bloqué (« Uploading… ») : les cellules ont été collées une à
une par le presse-papiers ; à ne plus faire, la CLI suffit.

Mesures du 2026-10-11 (A100 40 Go, tout sur la carte) : modèle chargé en ≈ 3 min (22 Go), clip
« rapide » 704×512 × 81 images en 1,2 min, clip 1280×704 (aire équivalente) × 121 images × 40 pas en
≈ 5,3 min (≈ 6 s par pas) ; 8 clips ≈ 45 min ≈ 4 unités (5,3 unités/h). Pièges : `pip uninstall torchao`
avant diffusers (ImportError `FqnToConfig` sinon) ; `torch_dtype` déprécié au profit de `dtype` ; pas
de secret HF nécessaire (modèle public ; l'interface Colab propose d'accorder `HF_TOKEN`, refuser).
Premier lot réel par la CLI le 2026-10-12 (Valmy, 241 images, 12,1 min sur A100 80 Go) : une session
restée longtemps inactive répond parfois en retard au premier `colab exec` (les appels se relancent
d'eux-mêmes, `essais`), et une session ouverte par un autre travail bloque toute nouvelle allocation
(« Allocation refused ») : `lancer --session <nom> --reprendre` la réutilise dans `/content/mouvement`
(dossier propre), `--garder` la laisse ouverte ; finir par `colab sessions` et arrêter ce qui reste.

- Le lot `src/data/diaporamas/generation/<slug>.json` donne, par élément, la diapositive `n`, le
  `type` (`mouvement`), la consigne `prompt` (anglais : mouvements voulus, « nothing new appears,
  no text », style de l'œuvre conservé) et la `graine` ; `negatif` et `modele` sont communs au lot.
- **Longueur par diapositive** (retour de l'utilisateur du 2026-10-12 : le clip ne doit pas s'arrêter
  avant la fin) : `preparer` écrit dans le manifeste le nombre d'images à générer, `images_clip(s)`
  = 4k + 1 entre 121 et 289, pour que le clip ralenti ×2 couvre `besoin_clip(s)` = durée de la voix +
  pause − départ (1,8 s, ou fin de la plongée d'une mosaïque au plus tard). Au-delà des 121 images
  d'entraînement, le temps de calcul croît plus que linéairement (attention) ; `mouvement.py` réduit
  l'aire (×0,7, deux fois au plus) si la mémoire manque. `verifier.py` avertit d'un clip plus court
  que sa diapositive.
- Les sources sont l'image servie (`public/…/NNN.webp`, recadrage déjà appliqué) réduite à sa zone
  utile `image.utile` : pas de marge de papier dans le clip.
- Le carnet produit `<id>.mp4` (5 s, 24 images/s, 1280×704 ou proportion équivalente : le modèle
  reçoit l'image **étirée** à des dimensions multiples de 32 d'aire constante ; le lecteur l'étire en
  retour sur la zone utile, qu'il recouvre donc exactement) et un `journal.jsonl` (dimensions, pas,
  durée de calcul, carte) ; `ESSAI_RAPIDE` fait d'abord un clip en 832×480 de la première image pour
  valider la chaîne. `encoder` **ralentit le clip de moitié** par interpolation de mouvement (ffmpeg
  `minterpolate`, images intermédiaires calculées : 10 s à 24 images/s, ≈ 20 s de calcul par clip ;
  retour de l'utilisateur du 2026-10-12, « deux fois plus lentement ») et l'encode **comme pour le
  site** (sans son, H.264 yuv420p, crf 27, débit plafonné à 3,2 Mbit/s : sans plafond les gravures
  très détaillées font 10 à 12 Mo, avec 4,2 Mo sans perte visible à l'échelle 1 ; les tableaux 1,2 à
  2,5 Mo). Ni boucle ni aller-retour (autre retour du même jour, après une première version en
  aller-retour bouclé) : le lecteur le joue une fois puis tient sa dernière image. La planche montre
  ce que verra le lecteur, avec le poids.
- La planche montre côte à côte la source, les clips et la narration audio de la diapositive.
- `publier` copie `clips/<id>.mp4` en `public/diaporamas/<slug>/NNN-mouvement.mp4` et écrit
  `image.video` : `fichier`, `type`, `duree`, `largeur`, `hauteur` (ffprobe), `modele` (du lot),
  `genere_le` (date du brut). Jamais sur un avant / après (ignoré) ni une image entière
  (`verifier.py` refuse). Compatible avec les mosaïques (le clip paraît après la plongée) et les
  plans de la spec 14 (il s'efface sous le premier plan).
- **Lecteur** (`mouvement.ts`) : la boîte `.lecteur__video` de chaque calque a la taille de l'image
  et reçoit sa transformation à chaque rendu (`rendu.ts`), le clip étiré sur la zone utile ; la
  **caméra calée sur la narration continue** de travailler sur l'image qui vit. L'image fixe entre
  comme d'habitude (fondu, gris → couleur, recul), puis le clip paraît en fondu CSS de 1,2 s à
  `DEBUT_CLIP` (1,8 s de voix, l'entrée finie) ou `DEBUT_CLIP_MOSAIQUE` après la plongée, **joué une
  fois** puis tenu sur sa dernière image. Il est calé sur l'horloge de la voix (position = voix −
  départ, recalé au-delà de `DERIVE_CLIP`) : pause, sauts et reprise restent justes ; il s'arrête
  avec le calque sortant. `prefers-reduced-motion` : aucun clip chargé, image fixe, ligne du
  cartouche masquée. Le clip de la diapositive suivante est mis en cache d'avance
  (`progression.ts`). Cartouche : quatrième ligne « mise en mouvement par IA » ; livre d'images : le
  clip sous l'image avec sa mention ; page de la période : section « Images mises en mouvement ».
- `verifier.py`, famille « mouvement (spec 16) » (étape C) : fichier, dimensions, durée et codec par
  ffprobe, proportions de la zone utile (erreur au-delà de 6 % : source changée), modèle, usage,
  entrée dans le lot, plafond de 15 clips par période, poids (avertissement au-delà de 4,5 Mo),
  incompatibilités.

### Colorisation (spec 16, « la colorisation couleur seule »)

Gravures, lithographies et photographies monochromes de scènes : le lecteur montre l'original, puis
un fondu lent vers une version colorisée (seule la chrominance change, le trait est celui de
l'original). Pilote : période 05, 46 images (2026-10-12).

```bash
# Lot fabriqué et jugé hors du site (Colab ; .cache/diaporamas/photos-qwen/<slug>/final-couleur.json)
python3 scripts/diaporamas/couleur.py publier deuxieme-republique .cache/diaporamas/photos-qwen/deuxieme-republique/final-couleur.json --essai
python3 scripts/diaporamas/couleur.py publier deuxieme-republique .cache/diaporamas/photos-qwen/deuxieme-republique/final-couleur.json
python3 scripts/diaporamas/couleur.py lister deuxieme-republique
python3 scripts/diaporamas/couleur.py retirer deuxieme-republique 86 34b     # ou --tout
python3 scripts/diaporamas/verifier.py deuxieme-republique && npm run build
```

- **Données** : `image.couleur` `{ fichier, largeur, hauteur, modele, genere_le }` sur l'image d'une
  diapositive ou d'un plan ; fichier `public/diaporamas/<slug>/NNN-couleur.webp` ou
  `NNN-b-couleur.webp`, **exactement aux dimensions de la zone utile en pixels** (arrondi de chaque
  bord, `couleur.zone_px`). Recette (consigne, graine, saturation, méthode) dans
  `src/data/diaporamas/generation/<slug>-couleur.json`, par fichier Commons.
- **Publication** : la clé est `commons` (elle survit aux renumérotations) ; `publier` refuse une
  image dont la zone utile a changé depuis la fabrication ou dont le WebP n'a pas la bonne taille,
  et les incompatibilités. Les cibles de `--seulement`, `--sauf` et `retirer` sont des numéros
  actuels (`86`, `34b`). `renumeroter.py` suit fichiers et champs.
- **Incompatibilités** : jamais avec un clip `video`, un avant / après ou une mosaïque ; galeries,
  lectures illustrées et épisodes hors champ (`verifier.py` refuse).
- **Lecteur** (`couleur.ts`) : un `<img class="lecteur__couleur">` par image colorisée (dans le
  calque après l'image ; dans `.lecteur__plans` après l'image du plan), à la taille de la zone
  utile, avec la transformation de l'image suivie d'une translation vers la zone utile : caméra,
  entrée en scène, image entière, recul d'entrée s'appliquent tels quels. L'opacité dérive de
  l'instant de la voix, sans transition CSS (pause, saut, reprise, captures : même image) ;
  pendant l'entrée de l'image, le calque couleur suit son fondu et son gris (après un saut au
  milieu d'une diapositive, l'image arrive déjà colorisée).
- **Règle de temps** (`constantes.ts`, `COULEUR_*`) : fenêtre de l'image = de son apparition au plan
  suivant ou à la fin de la voix ; le fondu (2 s depuis le 2026-10-12, 2,8 s avant) part dès 1,5 s (au tiers de la fenêtre et au plus tôt 2,5 s avant cette date)
  après l'apparition et 0,5 s après la fin de l'entrée en scène, avancé au besoin pour finir 2 s
  avant la fin de la fenêtre. Fenêtre de moins de 5,5 s (7,3 s avant le 2026-10-12) : le fondu part à 1,5 s et finit avec
  l'image (`verifier.py` avertit).
- **Signalement** : cartouche, ligne « colorisée par IA » repliée puis dépliée tant que la couleur
  est à l'écran (classe `en-couleur` du lecteur, seuil `COULEUR_SEUIL`) ; livre d'images : la
  version colorisée sous l'image, avec sa mention et le modèle ; page de la période : section
  « Images colorisées ».
- **`prefers-reduced-motion`** : aucune version colorisée chargée, l'original seul, pas de mention.
- `verifier.py`, famille « couleur (spec 16) » (étape C) : champs, nom et présence du fichier,
  WebP, dimensions déclarées et réelles = zone utile, incompatibilités, recette, poids
  (avertissement au-delà de 900 ko), fenêtre trop courte (avertissement).
