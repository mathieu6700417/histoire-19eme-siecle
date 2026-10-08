# Spec 12 — « Le siècle en images » : diaporamas narrés

Décidé avec l'utilisateur le 2026-10-07. Nouvelle section du site : le XIXe siècle raconté par
**neuf diaporamas narrés**, un par période, chacun d'**environ 100 images** accompagnées d'une
**voix off** de synthèse.

## Décisions (ne pas rediscuter)

| Sujet | Décision |
|---|---|
| Échelle | **~100 images par période** (90 à 110), soit ~900 images au total. |
| Périodes | Les **9 périodes de la section écrivains** (`src/data/chapitres-ecrivains.ts`) : prologue (vers 1770-1789), Révolution, Consulat et Empire, Restauration, monarchie de Juillet, 1848 et IIe République, Second Empire, année terrible, IIIe République jusqu'à 1900. Mêmes slugs. |
| Voix | Fichiers audio **générés à l'avance** par script, **Gemini 3.8 Flash TTS** (`gemini-3.8-flash-tts`), **voix Charon**, par l'API Gemini directe (`GEMINI_API_KEY` dans `.env`, non versionné). |
| Rythme | **2 à 3 phrases par image, ~18 s** en moyenne (14 à 24 s, soit ~40 à 55 mots), soit ~30 à 35 min par période, ~5 h pour le siècle (révisé le 2026-10-07 : le pilote à ~10 s allait trop vite). |
| Couleur | Les images s'affichent **en couleur** (le diaporama est une visionneuse, même exception que la spec 11). Tout le reste reste monochrome : contrôles, légendes, page. |
| Lecteur | **Complet et sobre** (détail plus bas). Musique ajoutée le 2026-10-07 (voir « Musique »). |
| Images | **Tout document d'époque**, produit au XIXe siècle (ou pendant le prologue pour le chapitre 0) : tableaux, gravures, lithographies, caricatures, affiches, photographies (dès les années 1840), cartes d'époque, unes de journaux, sculptures et monuments photographiés. **Domaine public** obligatoire, source **Wikimedia Commons**. Pas de reconstitution moderne ni de carte moderne. Une toile du XIXe siècle peinte après les faits (ex. Meissonier sur 1814) est admise et sa légende précise la date de l'œuvre. |
| Production | **Un pilote d'abord** : le lecteur, la chaîne de production et le diaporama **Révolution (chapitre 1)**. L'utilisateur regarde et écoute, la spec est ajustée, puis les 8 autres périodes sont produites en parallèle. |

## Réutilisation du projet « Histoire zoomable »

`~/ai-projects/histoire-19eme-siecle` fait déjà de la synthèse Gemini pour un documentaire du
XIXe siècle. On **copie** (on ne l'importe pas, les projets restent indépendants) :

- `pipeline/histoire/gemini.py` : appel TTS (pas de consigne de ton : **Gemini lit la consigne à
  voix haute**, voir le docstring), sortie PCM16 mono 24 kHz, transcription de contrôle ;
- le **contrôle de fidélité** : chaque audio est retranscrit puis comparé mot à mot au texte ;
  sous 0,9, on recommence (trois essais), puis on signale l'échec ;
- `collections/xix-france/prononciation.yaml` : le lexique des noms propres (Talleyrand →
  Tal-ran…), appliqué au texte avant la synthèse seulement (jamais aux sous-titres) ;
- `pipeline/histoire/images/commons.py` : recherche et métadonnées Commons, en guise d'inspiration ;
- la valeur de `GEMINI_API_KEY` : à recopier de son `.env` vers le `.env` de ce projet.

## Organisation

```
docs/specs/12-siecle-en-images.md
src/data/diaporamas/<NN>-<slug>.json        # le script d'une période (source de vérité)
public/diaporamas/<slug>/<NNN>.webp         # images redimensionnées (1600 px max, webp ~q80)
public/diaporamas/<slug>/<NNN>.m4a          # voix d'une diapositive (AAC mono ~64 kb/s)
src/pages/diaporamas/index.astro            # portail : les 9 périodes
src/pages/diaporamas/[slug].astro           # le lecteur d'une période
src/components/Diaporama.astro              # le lecteur (HTML + CSS + script vanilla)
scripts/diaporamas/                         # chaîne de production (Python, comme scripts/ecrivains)
  README.md
  images.py      # télécharge/redimensionne depuis Commons, remplit les métadonnées
  voix.py        # synthèse Gemini + contrôle de fidélité + durées
  verifier.py    # contrôle d'une période : fichiers présents, licences, durées, comptes
  prononciation.yaml
```

Les images et les audios sont dans `public/` (pas `astro:assets`) : ~900 images traitées au
build ralentiraient tout, et on les prépare une fois pour toutes par script. Poids visé :
~250 Ko par image et ~100 Ko par audio, soit ~35 Mo par période. Limites Cloudflare Workers
(20 000 fichiers, 25 Mio par fichier) : on reste très en dessous.

### Format du script d'une période (`src/data/diaporamas/01-revolution.json`)

```json
{
  "slug": "revolution",
  "numero": 1,
  "titre": "La Révolution",
  "periode": "1789-1799",
  "resume": "…",
  "actes": [
    { "id": "etats-generaux", "titre": "Les états généraux", "debut": 1 }
  ],
  "diapositives": [
    {
      "n": 1,
      "narration": "Le 5 mai 1789, à Versailles, s'ouvrent les états généraux…",
      "image": {
        "fichier": "001.webp",
        "commons": "File:Ouverture des États généraux à Versailles, 5 mai 1789.jpg",
        "titre": "Ouverture des états généraux à Versailles, 5 mai 1789",
        "auteur": "Isidore-Stanislas Helman, d'après Charles Monnet",
        "date": "1790",
        "technique": "gravure",
        "conservation": "musée de la Révolution française, Vizille",
        "licence": "Domaine public",
        "camera": [
          { "cadre": [0, 0, 1, 1] },
          { "cadre": [0.3, 0.2, 0.7, 0.55], "quand": "s'ouvrent les états généraux" }
        ]
      },
      "audio": { "fichier": "001.m4a", "duree": 11.8, "phrases": [[0, 5.2], [5.9, 11.8]] }
    }
  ]
}
```

`camera` : étapes de caméra (voir « Caméra calée sur la narration »), remplies par `camera.py`.
Les durées et les phrases horodatées sont remplies par `voix.py`.

**Actes** : 6 à 10 par période, ce sont les sous-chapitres affichés sur la barre de progression.

## Écriture de la narration

- **Langue** : charte du site (français soigné, typographie française). Niveau lycée/culture
  générale ; un terme technique est expliqué la première fois.
- **Fil continu** : les phrases s'enchaînent d'une diapositive à l'autre comme un seul récit
  documentaire. Chaque diapositive reste compréhensible à l'oreille seule.
- **L'image et la voix se répondent** : la narration parle de ce qu'on voit ou de ce que l'image
  illustre directement. Pas de « comme on le voit ici » systématique, mais on peut désigner un
  détail (« au premier plan, les gardes françaises… »).
- **Pas de notice dans la voix** : la narration ne dit pas qui a fait l'image, quand, ni où elle
  est conservée (« peint par Callet », « gravure de 1790 », « au musée Carnavalet ») : le
  cartouche à l'écran le montre. Elle peut dire la nature de l'image quand cela compte pour le
  sens (« cette caricature », « une estampe de propagande »). Le temps gagné sert à raconter
  davantage : causes, conséquences, acteurs, chiffres, citations courtes.
- **Exactitude** : dates, noms et chiffres exacts ; en cas de doute, formulation prudente (charte
  du site). Quand une image est une propagande ou une caricature, on le dit.
- **Pour l'oreille** : phrases de 25 mots au plus, pas de parenthèses ni d'abréviations, siècles
  et numéros de rois écrits pour être bien lus (« Louis seize » dans le texte envoyé à la voix si
  nécessaire, via le lexique ; le sous-titre garde « Louis XVI »).
- **Équilibre** : politique, mais aussi société, économie, culture, sciences de la période. Les
  camps opposés sont présentés avec leurs propres images (propagande royaliste et
  révolutionnaire, etc.).
- **Ouverture et clôture** : la diapositive 1 pose la période (dates, enjeu) ; la dernière fait
  le lien avec la période suivante.

## Choix des images

- ~100 images **différentes** par période (une même œuvre peut revenir avec un autre cadrage,
  2 fois au plus).
- **Métadonnées vérifiées** sur la page Commons (et la notice du musée quand elle est liée) :
  auteur, titre, date, technique, lieu de conservation, licence. En cas de doute : « attribué
  à », « vers 1795 ».
- **Licence** : domaine public seulement (`PD-old`, `PD-Art`, etc.), relevée par script depuis
  l'API Commons. Toute autre licence est refusée.
- **Variété** : on ne met pas 30 portraits à la suite ; on alterne les scènes, les portraits,
  les caricatures, les documents, les lieux et la vie quotidienne.
- **Qualité** : 1 000 px de large au minimum, sans filigrane ni recadrage maladroit.

## Lecteur (`Diaporama.astro`)

Page `/diaporamas/<slug>/`, dans la mise en page commune (`Base.astro`), style édition savante.

- **Image** : en couleur, elle **couvre toute la scène** (recadrée, jamais de bandes vides ;
  décision de l'utilisateur du 2026-10-07). Mouvement de caméra lent en CSS (transform), calé
  sur la narration (section « Caméra calée sur la narration »). Fondu enchaîné court (~600 ms)
  entre deux images. Le mouvement est désactivé si
  `prefers-reduced-motion`.
- **Cartouche en haut à gauche** de l'image, en surimpression sur un fond blanc cassé voilé :
  *titre* (italique), auteur, date (petites capitales grises). Il reste visible en permanence,
  y compris en plein écran. La notice complète (technique, conservation, lien Commons) reste
  dans le livre d'images sans JavaScript.
- **Sous-titre** : le texte de la narration, sous la légende ou en surimpression sobre (noir sur
  blanc cassé, pas de bandeau coloré). Bouton « Sous-titres » pour l'activer ou le désactiver
  (choix mémorisé).
- **Contrôles** : lecture/pause, précédent, suivant, compteur « 12 / 104 », temps écoulé/total.
  **Barre de progression découpée en actes** (filets fins, titre de l'acte au survol et affiché
  en petites capitales au-dessus de l'image), cliquable pour sauter.
- **Enchaînement** : à la fin de l'audio d'une diapositive, courte pause (~0,6 s) puis diapositive
  suivante. Précharger l'image et l'audio des 2 suivantes.
- **Clavier** : espace (lecture/pause), ← → (précédent/suivant), F (plein écran), S (sous-titres).
- **Plein écran** via l'API Fullscreen : l'image occupe **tout l'écran** ; l'acte (en haut), la
  cartouche (en haut à gauche), le sous-titre (compact, centré) et les contrôles se
  superposent en bandeaux blanc cassé légèrement voilés. Les contrôles s'effacent après
  quelques secondes d'inactivité ; le cartouche et le sous-titre restent (retours de
  l'utilisateur, 2026-10-07).
- **Reprise** : position (période, diapositive) mémorisée en `localStorage` (lectures/écritures
  dans un try/catch) ; « Reprendre à la diapositive 37 » proposé au retour.
- **Démarrage** : rien ne joue sans clic (politique des navigateurs) ; un bouton « Lancer le
  diaporama » sobre au-dessus de la première image.
- **Téléphone** : image pleine largeur, contrôles sous l'image, cibles tactiles de 44 px,
  balayage gauche/droite pour changer de diapositive. Pas de défilement horizontal.
- **Accessibilité** : boutons étiquetés (`aria-label`), annonce de la diapositive courante
  (`aria-live="polite"` sur le compteur), texte alternatif = titre de l'œuvre.
- **Sans JavaScript** : la page affiche la liste des diapositives (image, légende, narration) et
  reste lisible comme un livre d'images.
- **Navigation entre périodes** : liens « ← période précédente / période suivante → » en bas,
  comme pour les chapitres écrivains, et un lien vers le chapitre écrivains de la même période
  (et réciproquement, un lien discret depuis chaque chapitre écrivains vers son diaporama, une
  ligne dans `Chapitre.astro`, seulement si le diaporama existe).

## Caméra calée sur la narration (révision du 2026-10-07)

Retour de l'utilisateur sur le pilote : le balayage par défaut (toute la partie rognée, de haut
en bas) « ne fait pas toujours sens ». Décision : la caméra montre **ce dont la voix parle, au
moment où elle en parle**, sur le modèle de la §6.5 du projet « Histoire zoomable »
(`~/ai-projects/histoire-19eme-siecle/pipeline/histoire/steps/cadrer.py`, à relire et adapter).

- **Étapes de caméra** : chaque diapositive porte `image.camera`, une liste de 1 à 3 étapes.
  Chaque étape est un **cadre** `[x0, y0, x1, y1]` (rectangle normalisé de 0 à 1 dans l'image).
  La première étape n'a pas de `quand` : c'est le cadre de départ (en général le sujet
  principal ou une vue d'ensemble). Les suivantes portent `quand`, un **passage exact** de la
  narration (sous-chaîne littérale) : la caméra rejoint ce cadre quand la voix le prononce.
- **Rendu** : le lecteur montre le cadre visé **en entier** tout en couvrant la scène (pas de
  bandes : si le cadre n'a pas les proportions de l'écran, on montre un peu plus autour, borné
  aux limites de l'image). Transition douce (ease-in-out, ~2,5 s) qui commence un peu avant le
  passage ; entre deux étapes, une dérive très lente (zoom ~3 %) pour que l'image reste vivante.
  Une seule étape : zoom lent et léger vers ce cadre pendant toute la diapositive.
  `prefers-reduced-motion` : premier cadre, fixe, puis coupe sèche vers les suivants.
- **Instants** : `voix.py` (ou un script dédié) horodate chaque phrase de chaque audio, d'après
  les pauses (ffmpeg `silencedetect`), avec un repli au prorata des caractères ; résultat dans
  `audio.phrases` (`[[début, fin], …]`). Un passage `quand` est situé au prorata dans sa phrase.
- **Choix des cadres** : `scripts/diaporamas/camera.py <slug> [--n 12]` envoie l'image et la
  narration à un modèle de vision (Gemini Flash, `GEMINI_API_KEY`) et obtient les étapes en JSON.
  Consignes : cadrer ce qui est nommé ou décrit (personnage, groupe, objet, inscription) ; ne pas
  zoomer à l'excès (cadre d'au moins ~30 % de la largeur de l'image, pour éviter le flou) ; pas
  de mouvement gratuit : si la narration ne désigne rien de précis, une seule étape sur le sujet
  principal. Validation par script : `quand` présent mot pour mot dans la narration, cadres dans
  [0, 1], taille minimale ; en cas d'échec, nouvel essai puis repli sur une étape unique.
- **Corrections manuelles** : une diapositive marquée `"camera_manuelle": true` n'est jamais
  réécrite par `camera.py`. L'utilisateur signale les ratés par leur numéro.
- **Contrôle** : `camera.py --planche` produit une planche-contact (vignettes avec les cadres
  numérotés dessinés) pour relire d'un coup d'œil, hors du site (dans `.cache/`).
- Le champ `cadrage` (de/à) et le balayage par défaut sont **supprimés** ; `recadrage` (marges
  de papier) est conservé.

## Animations d'entrée (révision du 2026-10-07)

Demande de l'utilisateur : plus d'animation à l'apparition d'une image, « discret mais sympa ».
Les quatre effets sont retenus et se cumulent :

1. **Révélation gris → couleur** : fondu enchaîné d'environ 1,2 s ; la nouvelle image entre en
   niveaux de gris et ses couleurs montent en 1,5 à 2 s (filtre `grayscale`), comme une photo
   qui se développe (clin d'œil à la charte monochrome).
2. **Léger recul d'entrée** : l'image arrive agrandie d'environ 4 % et recule en ~1,5 s jusqu'à
   son premier cadre de caméra ; la caméra calée sur la narration prend ensuite le relais sans
   à-coup (le recul se compose avec les étapes, il ne les décale pas).
3. **Cartouche et sous-titre décalés** : le cartouche apparaît en fondu avec un petit
   glissement (quelques pixels), ~0,6 s après l'image ; le sous-titre change en fondu croisé
   au lieu d'un remplacement sec.
4. **Carton de changement d'acte** : à l'entrée dans un nouvel acte (y compris le premier), un
   carton sobre ~2 s sur fond blanc cassé : titre de l'acte en petites capitales, filet fin,
   dates de l'acte (nouveau champ `dates` des actes, ex. « 1787-1789 »). La première image de
   l'acte apparaît ensuite, et sa voix démarre après le carton. Le carton compte dans la durée
   totale et la barre de progression. Un saut manuel (flèches, clic sur un acte) l'affiche
   aussi mais il est passable d'un clic ou d'une touche.

`prefers-reduced-motion` : fondus simples et courts, pas de recul ni de glissement ; le carton
d'acte reste (c'est une information), sans animation.

## Frise du temps (révision du 2026-10-07)

Demande de l'utilisateur : une frise qui s'affiche de temps en temps et montre le curseur se
déplacer. Décisions :

- **Échelle** : **la période seule** (pour la Révolution, du début du premier acte à la fin du
  dernier, ex. 1787-1799), graduée par année (étiquettes d'années en chiffres elzéviriens ou
  lining selon le reste du lecteur), les **actes en segments** (filets d'épaisseur ou de gris
  différents, libellés au besoin) et un **curseur** (trait vertical fin + date en petites
  capitales, ex. « 14 juillet 1789 »). Strictement monochrome.
- **Quand** :
  1. dans **chaque carton d'acte**, sous le titre et les dates : le curseur glisse (~1 s,
     ease-in-out) de la date précédente jusqu'au début du nouvel acte ;
  2. entre deux cartons, en **surimpression 3 à 4 s** quand la date fait un **saut notable** par
     rapport à la diapositive précédente : plus de 3 mois vers l'avant, ou tout retour en
     arrière (retour sur un événement antérieur). Le curseur glisse de l'ancienne à la nouvelle
     date, puis la frise s'efface en fondu. Pas d'affichage en dessous de ce seuil.
- **Placement de la surimpression** : bandeau blanc cassé voilé, fin, centré en bas de l'image
  (au-dessus des bandeaux du bas en plein écran), sans masquer le cartouche. Il est éphémère,
  la caméra n'a pas à l'éviter. Sur téléphone : pleine largeur, graduation allégée (une
  étiquette toutes les 2 ou 5 années selon la place).
- **Données** : chaque diapositive porte `date` (date des **faits racontés**, pas de l'œuvre),
  au format ISO partiel `AAAA`, `AAAA-MM` ou `AAAA-MM-JJ`, et facultativement `date_fin` pour
  une durée (le curseur devient alors un court segment). Une diapositive de contexte sans date
  propre reprend la date de la précédente. Libellé affiché en français (« juillet 1789 »,
  « 14 juillet 1789 », « 1793-1794 »). `verifier.py` contrôle le format, l'appartenance à la
  période et signale les retours en arrière (pour relecture, ce n'est pas une erreur).
- `prefers-reduced-motion` : pas de glissement ; la frise apparaît et disparaît en fondu court.

## Musique (révision du 2026-10-07)

Demande de l'utilisateur : de la musique, avec des œuvres pertinentes. Décisions :

- **Droits** : le site est déployé publiquement, donc **uniquement des enregistrements libres**
  (même règle que le projet « Histoire zoomable », §6.7 : l'œuvre ET l'enregistrement doivent
  être libres). Pas de Qobuz, pas de YouTube. Sources : Musopen, Wikimedia Commons, IMSLP
  (enregistrements sous licence libre), Internet Archive (78 tours publiés avant 1963, domaine
  public en Europe ; vérifier la date de publication). Licence et source notées pour chaque
  morceau ; CC BY / BY-SA admis avec crédit, NC et ND refusés.
- **Pas de rendu MIDI** (décision du 2026-10-07, après un banc d'essai jugé insuffisant à
  l'oreille) : uniquement de **vrais enregistrements libres**.
- **Choix des œuvres** : composées pendant la période (ou peu avant), en lien avec l'acte.
  Priorité aux compositeurs et chants **français** quand un enregistrement libre existe ; sinon,
  compositeurs **européens de la même époque** (Mozart, Haydn, Boccherini, Clementi… pour la
  Révolution), en le disant dans les crédits. Pas d'œuvre composée après la période. Équilibre
  des camps pour les chants (royalistes aussi). Arrangements : l'arrangeur doit être identifié
  et dans le domaine public, sinon on s'abstient.
- **Fond continu, bas** : 1 à 3 morceaux par acte, enchaînés en fondu (pas de coupure sèche),
  **très bas sous la voix** (ducking automatique, environ −20 dB sous la narration), un peu
  plus présent dans les respirations entre diapositives, et qui **remonte pendant les cartons
  d'acte**. Changement de morceau de préférence au carton d'acte.
- **Intermèdes chantés** : **3 à 6 par période, 15 à 25 s chacun**. La narration s'arrête, le
  chant est joué **fort** (premier plan), sur l'image du moment (ou une image dédiée), avec les
  **paroles en sous-titre** et un cartouche « *titre*, auteur, date » comme pour les images. Ils
  tombent aux moments forts, juste après une narration qui annonce le chant (adapter cette
  narration si besoin, puis régénérer sa voix). Ils comptent dans la durée et la barre de
  progression, et on peut les passer (→). Ce doivent être des enregistrements **chantés** réels
  et libres (le MIDI ne chante pas) ; si aucun n'existe pour un chant, on y renonce.
- **Données** : `musique` dans le JSON de la période : pistes de fond par acte (fichier, titre,
  compositeur, date, interprète, source, licence, début/fin d'extrait, volume relatif) et
  `intermedes` (`apres` = n° de diapositive, fichier, extrait, paroles, cartouche). Fichiers
  dans `public/diaporamas/<slug>/musique/` (m4a AAC ~96-128 kb/s stéréo, normalisés en
  sonie, ~-16 LUFS pour les chants, le fond se règle dans le lecteur).
- **Chaîne** : `scripts/diaporamas/musique.py` : téléchargement (cache), contrôle de licence,
  découpe, fondus, normalisation (ffmpeg loudnorm) ; `verifier.py`
  contrôle fichiers, licences, crédits.
- **Cartouche de la musique** (révisé le 2026-10-07) : en **haut à droite**, **une seule
  ligne fine** sans encadré plein (fond voilé léger, filet en dessous), nettement distincte du
  cartouche de l'image : ♪ *titre court* · Compositeur, année (nom de famille seul, sans
  parenthèses ni mouvement). L'interprète n'apparaît qu'au survol (et dans les crédits).
  Masqué pendant un intermède chanté. Téléphone : en bas à droite de l'image.
- **Estompage des cartouches** (image et musique) : pleinement visibles ~5 s après chaque
  changement, puis presque effacés (opacité ~15 %) ; le survol de la souris ou la pause les
  ramènent. Pas de césure dans les cartouches.
- **Lecteur** : mixage dans le navigateur (Web Audio API : gain de la musique automatisé
  d'après l'état voix/silence/carton/intermède). Bouton **« Musique »** (activé par défaut,
  choix mémorisé) et réglage discret du volume de la musique. La musique suit pause, sauts,
  reprise. Le portail et la page de la période créditent les musiques (section « Musiques »
  en bas de page, sobre).

## Lectures d'époque et épisodes (révision du 2026-10-07)

Demande de l'utilisateur : des séquences où l'on **lit des textes contemporains**, et des
**épisodes qui racontent l'important que les images ne montrent pas**. Dose par période :
**4 à 6 lectures** de 20 à 40 s et **3 à 5 épisodes** de 45 s à 1 min 30 (la Révolution passe
d'environ 35 à 45 min). Ce sont des segments insérés **entre deux diapositives** (`apres` =
n° de diapositive), comptés dans la durée, la barre de progression et la frise, passables (→),
avec pause, reprise et sauts justes. La musique de fond est baissée comme sous la voix.

### Lectures
- **Textes** : d'abord les extraits **déjà vérifiés** du chapitre écrivains de la période
  (`src/content/ecrivains/NN-<slug>.mdx`, `src/data/auteurs.ts`, outils de `scripts/ecrivains/`) ;
  sinon d'autres textes de l'époque (discours, lois, journaux, lettres, mémoires) pris sur
  Wikisource et **vérifiés mot pour mot** de la même façon. Jamais de texte rédigé ou retouché :
  coupes signalées par « […] ». Variété des voix et des camps (comme la charte 00).
- **Voix de lecture** : une seconde voix Gemini TTS, nettement distincte du narrateur,
  masculine ou féminine selon l'auteur (le projet « Histoire zoomable » utilise Iapetus et
  Aoede : à réévaluer à l'écoute). Même contrôle de fidélité. Graphies anciennes : lexique.
  Le narrateur peut introduire la lecture d'une demi-phrase dans la diapositive précédente.
- **Visuel : carte de citation** : l'image du moment reste derrière, pâlie (voile blanc cassé)
  et immobile ; devant, sobrement : portrait d'époque de l'auteur s'il existe (Commons, domaine
  public ; sinon son initiale), nom et dates, nature du texte et source (*œuvre*, année), puis
  le texte, qui **s'écrit au rythme de la voix** (phrases horodatées comme la narration).
  Typographie d'édition savante, guillemets français.

**Révision « journal télévisé » (2026-10-07)** : la carte de citation adopte le style d'une
citation de journal télévisé, en restant sobre et monochrome :
- **fond** : l'image du moment, floue et voilée de blanc cassé, immobile ;
- **portrait grand**, sur un côté, en pleine hauteur de la zone utile (recadré sur le visage),
  qui entre par un léger fondu glissé ; à défaut de portrait, une grande initiale ;
- **grand guillemet ouvrant** décoratif et **texte en gros caractères**, qui apparaît **mot par
  mot en fondu, au rythme exact de la voix** : le mot en cours est en noir, les mots déjà lus
  en gris foncé, les suivants invisibles ; quand le passage dépasse la place, il défile en
  douceur (le haut s'efface en dégradé) ;
- **bandeau inférieur fin** (« lower third ») : NOM en petites capitales, dates, puis *œuvre*,
  année ; filet fin au-dessus ; crédit du portrait en très petit ;
- **minutage des mots** : alignement forcé de l'audio sur le texte (ex. whisperx et un modèle
  d'alignement français, s'il est disponible sur la machine), enregistré dans les données de la
  lecture ; repli au prorata des caractères dans chaque phrase horodatée ;
- téléphone : portrait en vignette au-dessus du texte, bandeau compact ;
  `prefers-reduced-motion` : apparition par phrase, sans glissement.

### Épisodes
Un épisode = une courte narration (voix du narrateur) sur un sujet que les images ne montrent
pas (dette et finances, idées, lois et institutions, économie, guerre vue d'ensemble, chiffres
de la Terreur…), avec un **visuel animé synchronisé sur la voix** (déclencheurs `quand` = passage
exact de la narration, comme la caméra). Un petit titre d'épisode en petites capitales
(« La dette du roi »). Quatre familles de visuels, toutes **monochromes** (gris, hachures,
traits), rendues en SVG/HTML par le lecteur à partir de données (pas de vidéo) :
1. **Cartes animées** : France de l'époque (provinces, 88 puis 83 départements, frontières,
   fronts, Vendée…), tracés qui se dessinent, zones qui se remplissent, libellés qui
   apparaissent. Fonds de carte libres (licence notée), simplifiés.
2. **Chiffres et graphiques animés** : gros chiffre qui apparaît, courbe qui se trace (ex.
   valeur de l'assignat), barres ; **source indiquée** sous le graphique. Chiffres exacts et
   sourcés ; fourchettes prudentes quand les historiens divergent.
3. **Documents d'époque surlignés** : fac-similé (Commons, Gallica) d'un texte (Déclaration,
   décret, journal) ; la ligne citée se **surligne** (trait gris ou soulignement) pendant que la
   voix la lit, avec un léger zoom dessus.
4. **Cartons typographiques** : une idée ou un mot clé mis en page en grand, comme une page de
   titre ; avec parcimonie.

Un épisode peut combiner plusieurs visuels (ex. carte puis chiffre). Exactitude stricte et
formulations prudentes (charte du site).

### Données et chaîne
`lectures` et `episodes` dans le JSON de la période ; `voix.py` synthétise aussi ces voix et
les horodate ; `verifier.py` contrôle extraits (mot pour mot), sources, licences, `quand`
exacts, données des graphiques sourcées ; README à jour.

## Arbitrages après le pilote (2026-10-07)

Décisions de l'utilisateur, relayées par la session qui a produit le pilote :

- **Œuvres conservées hors de France admises** (le sujet reste la France ; le lieu de
  conservation n'est pas un critère).
- **Images violentes gardées** quand elles documentent les faits (massacres, exécutions), sans
  complaisance dans la narration.
- **Lectures d'époque à voix de femme** (Gemini, voix Aoede) par défaut dans `voix.py`.
- **Production des 8 autres périodes une par une**, pas en parallèle : chacune est regardée
  par l'utilisateur avant la suivante.

## Arts et techniques (révision du 2026-10-07)

Constat de l'utilisateur après le pilote : l'histoire des **techniques** et celle des **arts**
ne sont pas couvertes. Décisions (ne pas rediscuter) :

- **Intégrées aux diaporamas existants**, **mêlées à la narration** : pas d'acte à part, pas de
  section séparée.
- **Dose** : **~20 diapositives par période** (~10 d'arts, ~10 de techniques), **ajoutées** au
  récit politique, qui garde son ampleur. Chaque période passe de ~100 à **~120 diapositives**
  (fourchette admise : 110 à 130 ; `verifier.py` est mis à jour en conséquence).
- **Placement au fil du récit** : chaque diapositive entre là où elle tient à l'histoire (le
  télégraphe Chappe avec la guerre de 1794, le *Serment des Horaces* avec la crise de 1789, le
  Louvre avec les biens nationaux et les saisies). Groupes de **1 à 3 diapositives d'affilée au
  plus**. Les narrations voisines sont retouchées pour que les transitions coulent (fil continu).
- **Aucun repère visuel** : ni étiquette « arts » ou « techniques » dans le cartouche, ni marque
  propre sur la frise. Ces diapositives se fondent dans le récit (la frise reçoit seulement les
  événements qu'elle aurait reçus de toute façon, avec le style ordinaire).
- **Arts** : peinture, sculpture, gravure, et leurs institutions (Salon, Académie, Louvre et
  musées, prix de Rome) ; architecture et urbanisme ; musique et spectacle (opéra, compositeurs,
  théâtre, fêtes) ; arts décoratifs et mode (mobilier, costume, affiche, styles). On montre
  l'œuvre elle-même, et la caméra va sur le détail dont parle la voix.
- **Techniques** : machines et industrie (vapeur, textile, métallurgie, chemin de fer,
  navigation, moteurs, électricité) ; communication et image (télégraphes, presse, lithographie,
  photographie, téléphone, cinéma) ; sciences et médecine (système métrique, chimie, Pasteur,
  hygiène) ; vie quotidienne et agriculture (éclairage, conserve, engrais, grands magasins).
- **Profondeur technique** : **le principe en une phrase, puis l'effet** (ce que ça change pour
  l'économie, la guerre, la vie quotidienne). On s'appuie volontiers sur des **planches
  techniques d'époque** (Encyclopédie et son recueil de planches, brevets, Figuier *Les
  Merveilles de la science* pour une technique antérieure à sa date de parution, relevés
  d'ingénieurs), dont la caméra suit les pièces. Règle des images inchangée : documents
  d'époque, domaine public, Commons. Une planche publiée après la période est admise comme une
  toile peinte après les faits, si elle est du XIXe siècle et si la légende donne sa date.
- **Musique des œuvres** : quand une diapositive parle d'une œuvre musicale, on la fait
  entendre par un **intermède musical** de 15 à 25 s joué juste après (même mécanique que les
  intermèdes chantés : premier plan, cartouche, passable, compté dans la durée), **1 ou 2 par
  période, en plus** des 3 à 6 intermèdes chantés. Seulement s'il existe un enregistrement
  libre (mêmes règles de droits que la section « Musique ») ; sinon, on en parle sans la faire
  entendre. Pour une œuvre instrumentale, pas de paroles en sous-titre : le sous-titre est
  masqué pendant l'intermède.
- **Équilibre et exactitude** : mêmes règles que le reste de la narration. On dit quand un art
  sert la propagande (David et les fêtes révolutionnaires, par exemple).
- **Pilote** : on enrichit d'abord **la Révolution** (107 → ~127), l'utilisateur juge, puis la
  règle s'applique aux 8 autres périodes. L'insertion **renumérote** les diapositives : les
  fichiers `NNN.webp` / `NNN.m4a`, les `apres` des lectures, épisodes et intermèdes, les
  débuts d'actes, la frise et tout autre renvoi par numéro sont recalculés par script, sans
  régénérer les voix inchangées (l'empreinte du texte fait foi).

### Retours sur la Révolution enrichie (2026-10-07)

- **Formules prudentes gardées** (Lagrange « aurait dit », « mi-août 1794 » pour le Quesnoy,
  « un mot qu'il dit avoir inventé » pour Grégoire). La citation de Lagrange est donnée **en
  entier** (« … et cent années peut-être ne suffiront pas pour en reproduire une semblable »).
- **Un seul intermède musical** dans la Révolution (Méhul) ; pas de second.
- **Images à remplacer** quand Commons offre mieux : la guillotine (diapositive 48, estampe d'une
  machine imaginée à hache) par une vraie gravure d'exécution de 1792-1793 ; le ballon de Fleurus
  (diapositive 93, livre anglais de 1870) par une estampe d'époque. Métadonnées incertaines :
  « attribué à » ou lieu de conservation omis plutôt qu'avancé sans source.
- **Musique de fond** : un acte plus long que ses pistes reçoit un morceau de plus (même règle
  de droits et d'époque, enchaîné en fondu) plutôt que de boucler. Vaut pour toutes les périodes.
- **Reprise** : la position est mémorisée par une clé stable de la diapositive (son image
  Commons), pas par son numéro, pour survivre aux renumérotations.

### Moins de tenues statiques (2026-10-07)

Retour de l'utilisateur : l'image paraît statique quand la caméra reste longtemps sur la même
partie. Décision, en deux volets :

- **Respiration dans le lecteur** : au-delà de ~5 s de tenue sur un même cadre, la dérive de 3 %
  laisse place à un mouvement lent et continu : resserrement puis léger recul (~8 % d'amplitude
  au total), avec un petit glissement latéral ou vertical, sans jamais sortir du cadre visé ni
  des bords de l'image, toujours doux (pas d'à-coup, vitesse constante ou ease-in-out long).
  Désactivé si `prefers-reduced-motion`.
- **Étapes supplémentaires** : `camera.py` peut proposer **jusqu'à 4 étapes** ; une tenue
  prévue de plus de ~7 s appelle une étape de plus, calée sur un passage de la narration (un
  détail, un personnage, un objet dont parle la voix). On ne crée pas d'étape sans lien avec la
  voix : dans ce cas, la respiration suffit.

### Cartouches lisibles et cartons plus longs (2026-10-07)

Retours de l'utilisateur : les cartouches de l'image et de la musique sont « peu lisibles et pas
assez bien formatés au niveau du contenu » ; et au changement d'acte, « y rester plus longtemps
pour écouter un peu de musique ». Ces décisions remplacent ce qui précède sur ces points.

- **Cartouche de l'image, contenu** : trois lignes.
  1. un **titre court rédigé** (`image.titre_court`, 60 caractères au plus, en italique),
     fidèle à l'œuvre mais lisible (« La guillotine place du Carrousel » pour « Guillotine élevée
     en place du Carrousel, le 13 août 1792, servant à punir… ») ; le titre officiel reste dans
     `image.titre`, affiché dans le livre d'images et en `alt` ; pour un titre déjà court, le
     titre court est le titre même ;
  2. l'**auteur** (« d'après … » peut passer sur la ligne suivante proprement ; « anonyme » en
     minuscule et l'éditeur à part si utile) ;
  3. **date · technique** (« 1792 · estampe »).
- **Cartouche de la musique, contenu** : deux lignes, **rédigées à la main** pour chaque piste
  (`cartouche: { oeuvre, compositeur }` dans la piste), **sans troncature automatique** ni points
  de suspension : « ♪ Symphonie nº 87, menuet » / « Joseph Haydn, 1785 ». L'interprète reste
  dans les crédits et au survol. Même chose pour les intermèdes (titre court rédigé).
- **Style des deux cartouches** (même famille) : fond blanc cassé presque opaque (~95 %), filet
  fin, titre en noir à ~1 rem, lignes 2 et 3 en gris foncé lisible (petites capitales, jamais
  de gris pâle), interlignage aéré, pas de césure. **Disparition** (révisé le même jour) : pleinement
  visibles **~12 s** après chaque changement, puis **disparition complète** en fondu lent
  (opacité 0). Le **survol du coin haut gauche** (image) ou **haut droit** (musique) les fait
  réapparaître : zone de survol invisible un peu plus large que le cartouche, qui reste active
  même quand il est caché. La pause les ramène aussi. Téléphone : un toucher sur l'image les
  ramène quelques secondes. Téléphone : taille
  plancher lisible, aucune troncature.
- **Guillotine (diapositive 48), nouveau retour** : l'estampe du Carrousel montre mal la
  machine (« on voit pas trop »). La remplacer par une image d'époque où la guillotine est
  **grande et nette** (gravure ou dessin centré sur la machine, ou exécution vue de près), de
  bonne définition ; caméra sur la machine.
- **Documents d'époque des épisodes** (retour du 2026-10-08) : la ligne lue n'est plus surlignée par un rectangle gris et un trait, mais **éclairée d'un halo doux aux bords flous** (papier éclairci, texte plus contrasté, ellipse qui déborde un peu de la ligne), qui apparaît en fondu.
- **Graphiques des épisodes** (retour sur la courbe des assignats) : chaque point mis en valeur
  porte une étiquette **date · valeur en clair** (« janv. 1791 · 91,5 livres », « juil. 1795 ·
  moins d'une demi-livre »), jamais en notation d'époque non expliquée (l. s. d.) ; l'unité est
  dite une fois sous le titre ; les étiquettes ne chevauchent jamais la courbe ni les axes ; le
  dernier point a la sienne. Règle valable pour tous les graphiques de toutes les périodes.
- **Carton d'acte** (retour du 2026-10-08) : le **titre s'écrit lettre par lettre** (~120 ms par lettre, fondu de 0,6 s par lettre, mots insécables, figé en pause), puis le filet et les dates ; le **cartouche de la musique reste visible** au-dessus du carton, sans estompage.
- **Sortie du carton d'acte en deux volets** (2026-10-08) : le carton se coupe à mi-hauteur ; la moitié haute glisse vers le haut, la basse vers le bas (~1,4 s, ease-in-out doux, `transform` seul, filet fin gris au bord de la coupe) et découvrent l'image déjà posée et décodée dessous. Même animation si l'on passe le carton (→, clic, Entrée) ; figée en pause ; `prefers-reduced-motion` : fondu court (0,3 s).
  **Révision du 2026-10-08** : ouverture **beaucoup plus longue (~3,5 s)**, qui découvre un **détail zoomé bien choisi** de la première image de l'acte (un visage, un geste, un objet fort : champ `image.ouverture`, cadre `[x0, y0, x1, y1]` sur la première diapositive de chaque acte). Ensuite la caméra **recule lentement (~5 s)** vers le premier cadre de la diapositive pendant que la voix commence (exception admise au plafond de vitesse pour ce recul, toujours doux aux deux bouts). Sans `ouverture`, comportement précédent, avec des volets eux aussi à 3,5 s.
  *Minutage* : les 3,5 s d'ouverture sont **prises sur les 12 s du carton** (≈ 8,5 s de carton fixe, puis l'ouverture, qui finit au bout des 12 s, quand la voix commence) : durée totale, barre de progression et minutage inchangés. Passé (→, clic, Entrée), le carton joue aussitôt son ouverture (l'horloge du carton saute à son début, même en pause) et la voix démarre à sa fin ; passé une seconde fois pendant l'ouverture, il finit tout de suite. Volets et entrée suivent l'horloge du carton : figés en pause, justes après une reprise.
  *Valeurs retenues* : volets 3,5 s, courbe `cubic-bezier(0.45, 0, 0.2, 1)` (départ doux, longue fin apaisée). Sur un détail : l'image est posée sous le carton déjà cadrée sur le détail ; pendant l'ouverture, poussée de 2,5 % (départ et arrêt doux) et révélation gris → couleur étalée sur les 3,5 s (pas de recul d'entrée de 4 %) ; puis recul de 5 s (au plus la moitié de la voix) vers la première vue, en homothétie, rampes de 2 s à chaque bout : position et vitesse continues à la fin de l'ouverture (vitesse nulle) et à la fin du recul, où la respiration prend le relais. Aucune étape de caméra ne commence pendant le recul (la tenue minimale court à partir de sa fin). Détail cadré au rapport ~2,4:1 (proportions de la zone utile sur ordinateur) et ~40 % de la largeur de l'image : zoom ×2,1 à ×2,5 sur ordinateur, ×1,5 à ×2,3 sur téléphone, sans flou (~640 px de l'original pour ~1 000 px d'écran). `prefers-reduced-motion` : fondu court et premier cadre directement. `verifier.py` contrôle le cadre (valide, seulement sur la première diapositive d'un acte ; avertissement s'il est très serré ou zoome moins de ×1,6).
- **Carton d'acte : ~12 s** au lieu de 2 s, **musique au premier plan** (gain plein, fondu de
  descente quand la voix reprend). Passable (→, clic). Compté dans la durée et la barre de
  progression. `prefers-reduced-motion` : même durée, sans animation.

### Cartes de lieu et citations en surimpression (2026-10-07)

Demandes de l'utilisateur : « quand un lieu est mentionné dans la narration, faire apparaître
une carte qui montre où cela se passe » ; « quand une citation courte de quelqu'un est faite,
que ses mots s'ajoutent en gros en surimpression sur l'image ». Les deux sont **toujours
actifs** (pas de bouton).

**Cartes de lieu (médaillon)**
- **Forme** : un médaillon (environ un quart de la hauteur de la scène) qui apparaît en fondu
  **en bas à droite** au moment où la voix prononce le lieu : fond de carte monochrome, un point
  qui pulse doucement, le nom du lieu en petites capitales. Il reste ~5 s puis s'efface. L'image
  et la caméra continuent derrière ; la caméra tient compte du médaillon (zone couverte) comme
  des autres bandeaux. Une carte au plus par diapositive. Téléphone : médaillon réduit, lisible.
- **Quels lieux** : villes, régions, champs de bataille **et lieux de Paris** (Bastille,
  Tuileries, Champ-de-Mars, place de la Révolution…), à leur **première mention** dans la
  période ; pas à chaque « à Paris ». Environ 40 à 50 par période.
- **Fonds** :
  - **France et étranger** : le fond SVG simplifié des épisodes (`carte.py`, Natural Earth),
    avec un **cadre adapté au lieu** : France seule, France et voisins pour un lieu proche
    (Fleurus, Mayence, Turin), Europe-Méditerranée avec la France repérée pour un lieu lointain
    (Égypte, Moscou, Algérie), monde si nécessaire (Mexique). On voit toujours où c'est par
    rapport à la France.
  - **Paris** : un **plan d'époque du domaine public** (Commons), choisi pour la période
    (plan de Verniquet, vers 1790, pour la Révolution ; plans des années 1830, 1860 et 1890
    ensuite), désaturé en gris, recadré et zoomé sur le lieu, avec le point. Le plan est
    crédité (cartouche discret dans le médaillon ou crédits de la page).
- **Données** : `lieux` dans la diapositive : `{ nom, quand, lon, lat, fond }` (`quand` =
  passage exact de la narration ; `fond` = `paris`, `france`, `voisins`, `europe` ou `monde`).
  Coordonnées vérifiées ; pour Paris, position sur le plan d'époque (calage du plan documenté
  dans le script). `verifier.py` contrôle les `quand` exacts, les coordonnées et une carte au
  plus par diapositive.

- **Plusieurs lieux sur une diapositive** (révision du 2026-10-08) : la règle « une carte au plus
  par diapositive » devient « **un médaillon au plus** ». Quand la voix nomme plusieurs lieux
  (jusqu'à 4 ou 5), le médaillon a un cadre qui **les englobe tous** (calculé, avec une marge) ;
  chaque point apparaît avec son nom **au moment où la voix le dit**, les précédents restent. Le
  médaillon reste ~3 s après le dernier nom. Si Paris et la province se mêlent, on prend la
  carte de France (ou le cadre plus large qui convient) ; les noms ne se chevauchent pas.

**Citations en surimpression**
- **Quand** : chaque citation courte (en gros 20 mots au plus) **attribuée à une personne** et
  dite entre guillemets « » dans la narration. On garde la prudence du texte (« aurait dit » :
  l'attribution porte alors « attribué à »).
- **Rendu** : les mots s'inscrivent **mot à mot, calés sur la voix** (alignement des mots,
  comme les lectures d'époque), en grand (serif italique, guillemets « », noir sur un voile
  blanc cassé léger), centrés dans le tiers inférieur ; puis l'auteur en petites capitales
  (« — Mirabeau »). La citation reste ~2 s après le dernier mot puis s'efface. Le sous-titre est
  masqué pendant ce temps. Un médaillon de carte et une citation ne se montrent jamais en même
  temps sans place pour les deux (la citation l'emporte, le médaillon attend ou passe).
- **Données** : `citations` dans la diapositive : `{ texte, auteur, prudence? }` (le `texte`
  est une sous-chaîne exacte de la narration) ; instants des mots calculés par la chaîne
  (`alignement.py`). `prefers-reduced-motion` : la citation apparaît entière, sans animation.
- **Pause allongée** (décision de l'utilisateur, 2026-10-07) : quand la narration se termine par
  une citation en surimpression, la pause après la voix passe de 0,6 s à ~2 s, calculée sans
  rien fixer par diapositive : max(0,6 s, fin du dernier mot de la citation + 2 s − durée de la
  voix). Elle compte dans la durée totale, la barre de progression et l'enchaînement
  (`pauseApres` dans `src/utils/diaporamas.ts`, même calcul dans `verifier.py`).

### Musique : compositeurs français d'abord (2026-10-08)

Demande de l'utilisateur : de la musique de compositeurs français de l'époque plutôt que Mozart
ou Haydn. Décisions, qui précisent la section « Musique » :

- **Compositeurs** : ceux **actifs en France** pendant la période : Français (pour la Révolution :
  Gossec, Méhul, Grétry, Dalayrac, Boieldieu, Lesueur, Catel, Devienne, le chevalier de
  Saint-Georges, Kreutzer…) et étrangers qui font leur carrière à Paris (Cherubini, Viotti,
  Pleyel). Un compositeur d'ailleurs (Mozart, Haydn) n'est gardé qu'en **dernier recours**,
  quand aucun enregistrement libre d'un compositeur actif en France ne convient pour l'acte.
- **Enregistrements anciens admis, et préférés à un compositeur étranger** : disques publiés
  **avant 1963** (domaine public en Europe ; vérifier l'année de publication), son mono accepté,
  nettoyé légèrement (filtre du souffle et des craquements sans dénaturer, normalisation).
  Sources : Internet Archive (78 tours et premiers microsillons), Commons, IMSLP, Musopen,
  Gallica (si la réutilisation est libre). Les règles de droits restent strictes (œuvre ET
  enregistrement libres, arrangeur identifié et dans le domaine public, ni NC ni ND, pas de MIDI).
- Les crédits de la page nomment l'interprète et l'année de l'enregistrement.

### Caméra calme et lente (2026-10-08)

Retour de l'utilisateur : les mouvements sont « un peu rapides et saccadés parfois », ils
« donnent un peu le mal de mer ». Décisions, qui remplacent les valeurs de « Caméra calée sur la
narration » et de « Moins de tenues statiques » quand elles diffèrent :

- **Transitions** : durée **proportionnelle à l'ampleur** du mouvement (rapport de zoom et
  distance parcourue), **3 à 6 s**, commencée assez tôt pour arriver au passage ; courbe
  ease-in-out douce. **Vitesse maximale plafonnée** (zoom et déplacement), quitte à arriver un
  peu après le passage.
- **Zoom logarithmique** : l'échelle est interpolée en logarithme (vitesse perçue constante),
  et le déplacement est couplé au zoom pour que le point visé avance régulièrement (pas d'arc
  ni d'accélération en fin de course).
- **Respiration à sens unique** : plus d'aller-retour. Une seule direction par tenue, zoom de
  **4 % au plus**, glissement latéral réduit (environ un tiers de la marge libre), vitesse très
  faible et constante après une mise en route douce.
- **Étapes** : **au moins 5 s** entre deux étapes ; une étape trop proche de la précédente ou
  dont le cadre diffère très peu (micro-déplacement) est ignorée par le lecteur (filtre au
  rendu, les données restent intactes).
- **Fluidité** : animation composée par le GPU (`transform` seul, `will-change`, pas de filtre
  coûteux recalculé à chaque image pendant le mouvement) ; mesure des images par seconde.
- `prefers-reduced-motion` : inchangé.
- **Valeurs retenues** (lecteur, `plan` et `souffle`) : plafonds 0,22 en log d'échelle par seconde
  et 0,3 scène par seconde (au plus fort) ; arrivée visée 1 s après le passage ; rampes de mise
  en route et d'arrêt d'un tiers de la transition (2,5 s au plus) ; micro-déplacement : zoom et
  déplacement sous 0,12 ; respiration de 0,5 % par seconde au plus (4 % au plus). Un long
  glissement le long d'une image très large peut dépasser 6 s pour tenir le plafond.

### Sans bordures, et médaillon plus grand (2026-10-08)

- **Bordures** : retour de l'utilisateur, en plein écran sur ordinateur « les images montrent
  souvent les bordures ». On ne montre **jamais rien qui ne soit pas l'image** : liserés de
  numérisation (blancs ou noirs), cadres de tableau photographiés, marges de papier des gravures,
  et la **légende gravée** sous les estampes (le titre est déjà dans le cartouche). Chaque image
  porte une **zone utile** `image.utile: [x0, y0, x1, y1]`, détectée par script (analyse des bords :
  bandes uniformes, papier, cadre ; puis contrôle par un modèle de vision pour les marges de
  papier et les légendes gravées) et relue. Le lecteur borne toute vue (caméra, respiration,
  ouverture, cadres d'intermède) à cette zone, quelle que soit la forme de l'écran (plein écran
  16/9 ou 16/10 compris) ; un cadre qui en déborde est ramené dedans. Les cadres existants
  restent exprimés dans l'image entière.
- **Médaillon de carte à plusieurs lieux** : agrandi (~240 × 180 px sur ordinateur, au lieu de
  160 × 120), lisible sur téléphone ; un médaillon à un seul lieu garde sa taille.
- **Horloge lissée** : la caméra suit `audio.currentTime`, qui avance par crans irréguliers ;
  l'instant est lissé (interpolation par l'horloge de l'écran entre deux mises à jour de l'audio,
  recalée sans saut) pour que tout mouvement soit parfaitement fluide.
- **Valeurs retenues** (mise en œuvre du 2026-10-08) :
  - zone utile : `scripts/diaporamas/utile.py` (analyse des bords puis Gemini Flash, intersection
    des deux, garde de 0,4 % ; zone de moins de 50 % de l'image ou bord rentré de plus de ~30 %
    refusés puis saisis à la main après relecture de la planche, `utile_manuel: true`) ; sur la
    Révolution, 100 images rognées sur 127, 24 % de l'aire retirés en moyenne ; les portraits en
    médaillon au-dessus d'un cartouche gravé descendent à 30-45 % de l'image ; un médaillon rond
    garde le rectangle de sa scène (coins de papier compris) ; un objet photographié sur fond de
    studio garde son fond. Les fac-similés des épisodes (montrés en entier) et les portraits des
    lectures ne passent pas par la caméra : pas de zone utile.
  - lecteur : les cadres restent exprimés dans l'image entière ; ils sont convertis dans la zone
    utile et ramenés dedans (déplacés s'ils y tiennent, sinon réduits à leur partie commune) ; la
    zone couvre toujours la scène. `verifier.py` exige qu'un cadre recouvre la zone à 50 % au
    moins (avertissement sous 75 %).
  - **zones couvertes constantes** : la place du médaillon de lieu est réservée pour toute la
    diapositive qui en a un (et non plus prise et rendue en 0,9 s autour de son affichage : ce
    changement de zone en cours de route recalculait la caméra et la faisait bondir, jusqu'à dix
    fois le plafond de vitesse ; c'était la principale cause des à-coups signalés).
  - **recul de l'ouverture** : 5 s, allongé si l'ampleur l'exige pour rester sous les plafonds
    au plus fort (la moitié de la voix au plus).
  - **horloge lissée** : vitesse corrigée de ±5 % au plus, écart filtré à chaque mise à jour de
    l'audio (résorbé en ~1 s) ; l'instant de l'audio exactement en pause, au départ (attente du
    premier pas de l'audio) et après un saut de plus de 0,3 s.
  - médaillon à plusieurs lieux : 1,5 fois la taille d'un médaillon simple (~240 × 180 px au lieu
    de 160 × 120 sur ordinateur), 300 px de haut au plus, dans la limite de 40 % de la hauteur et
    de la moitié de la largeur de la scène (téléphone compris).

### Portraits des personnes nommées (2026-10-08)

Demande de l'utilisateur : quand une personne est nommée par la narration mais que l'image ne la
montre pas, montrer son portrait. Décisions :

- **Forme** : **médaillon ovale** à bord fin (façon camée ou miniature), recadré sur le visage,
  **en couleur** (exception des images du diaporama) ; dessous, le **nom** en petites capitales
  et les **dates** (« Danton · 1759-1794 »), monochromes.
- **Qui** : **à chaque mention** d'une personne, **si elle n'est pas visible sur l'image**
  (contrôle par modèle de vision, relu). Un portrait d'époque fiable doit exister : œuvre du
  domaine public sur Commons, faite du vivant de la personne ou peu après, identifiée sans doute
  (sinon, pas de portrait). Le même portrait sert à toutes les mentions de la personne.
- **Où et quand** : **en bas à gauche** (symétrique de la carte, peut coexister avec elle),
  apparition en fondu au moment où la voix dit le nom. **Plusieurs personnes** : une **rangée
  d'ovales** côte à côte, chacun paraissant à son nom, les précédents restent, **4 au plus** ;
  la rangée reste ~3 s après le dernier nom (5 s au moins). Une citation de la personne
  s'accompagne de son portrait. La zone est réservée pour la caméra sans la faire bouger
  brusquement (voir la correction de la régression de caméra). Téléphone : ovales plus petits,
  en rangée.
- **Données** : `personnes` dans la diapositive : `{ id, quand }` (passage exact) ; un registre
  par période ou commun, `src/data/diaporamas/portraits.json` : `{ id, nom, dates, fichier,
  commons, auteur, date, cadre_visage }` ; images recadrées en webp dans
  `public/diaporamas/portraits/`. Crédits des portraits sur la page. `verifier.py` : `quand`
  exacts, licences, 4 au plus, instants croissants, personne absente de l'image.
- **Valeurs retenues** (mise en œuvre du 2026-10-08 ; détail dans `scripts/diaporamas/README.md`,
  « Portraits ») :
  - relevé : `personnes` (personne non visible, portrait) et `personnes_vues` (visible, pas de
    portrait) dans chaque diapositive, `{ id, quand, instant }` ; « visible » = reconnaissable
    (sujet, figure identifiable par le titre ou la composition, œuvre dans l'œuvre), pas une
    silhouette dans une foule. Contrôle par Gemini Flash (`portraits.py --visibilite`), désaccords
    tranchés à la main. Une citation porte `personne` : son portrait l'accompagne.
  - registre : seules les personnes montrées ; une personne sans portrait fiable garde une `note`
    et rien n'est montré. Pas de « portrait présumé ». Webp 360 × 450 px recadrée (visage à 58 %
    de la hauteur ; 240 × 300 avant le 2026-10-08), ovale tracé par le lecteur.
  - lecteur : ovales de 25 % de la hauteur de la scène (110 à 180 px sur ordinateur, 70 px sur
    téléphone ; agrandis d'environ 1,5 fois le 2026-10-08, nom et dates un peu plus grands), réduits si la rangée ne tient pas à côté du médaillon de lieu ; une personne par
    ovale (première mention), le premier dès l'entrée de la rangée ; rangée du premier nom à 3 s
    après le dernier, 5 s au moins, prolongée jusqu'à la fin de la citation de la personne ; zone
    réservée pour toute la diapositive ; une personne seule : « Danton · 1759-1794 » sur une ligne.
  - **priorités quand tout tombe ensemble** : citation > portraits = médaillon de lieu > frise du
    temps. La citation exclut le médaillon (règle existante) et, si elle touche la rangée, monte
    au-dessus d'elle pour toute la diapositive ; la frise cède quand médaillon et portraits sont là
    ensemble (deux surimpressions au plus, sous-titre masqué pendant une citation) ; sur
    téléphone, le cartouche de la musique s'efface le temps des portraits.
  - Révolution : 135 mentions relevées, 58 visibles sur l'image, 71 avec portrait (48 personnes) ;
    pas de portrait fiable pour Réveillon, Méchain, Amar, Lagrange, Claude Chappe et Pussin.

### Paroles des chants façon clip (2026-10-08)

Demande de l'utilisateur : pendant un intermède chanté (la Marseillaise par exemple), les mots
s'affichent « un peu comme dans un clip, en gros au milieu par-dessus l'image ». Décisions, qui
remplacent les paroles en sous-titre pendant les intermèdes chantés :

- **Vers par vers, mot à mot** : chaque vers s'inscrit en grand au centre de l'image, mot après
  mot au rythme du chant (serif, grande taille, guillemets inutiles) ; le vers suivant remplace
  le précédent en fondu. Pas de sous-titre en bas pendant ce temps.
- **Blanc cassé sur voile sombre**, toujours : l'image s'assombrit doucement pendant le chant
  (voile noir semi-transparent, l'image reste visible derrière, la caméra continue), texte
  blanc cassé. Retour au normal en fondu à la fin. Monochrome.
- **Calage** : instants de chaque mot chanté, calculés automatiquement (alignement forcé sur
  l'enregistrement, en isolant la voix si utile) puis **vérifiés et corrigés** ; données dans
  l'intermède (`paroles` : vers avec leurs mots horodatés). Si le calage au mot est impossible
  pour un chant, repli : vers entiers en fondu à leur début.
- Pause, reprise, sauts et passage (→) justes ; `prefers-reduced-motion` : vers entiers sans
  animation. Téléphone : taille adaptée, aucune coupure de mot. Les intermèdes instrumentaux ne
  changent pas.
- **Valeurs retenues** (mise en œuvre du 2026-10-08 ; détail dans `scripts/diaporamas/README.md`,
  « Paroles des chants calées au mot ») :
  - calage : `scripts/diaporamas/paroles.py` (voix isolée par Hybrid Demucs de torchaudio, puis
    alignement forcé wav2vec2 du texte entier sur l'extrait ; contrôle sur le mélange, écoute
    ciblée par Gemini, planches relues, corrections `calage_fenetres` / `calage_retouches`) ;
    données : `calage: "mot"` et `[début, vers, [[début, fin], …]]` (repli : `calage: "vers"`,
    `[début, vers]`).
  - lecteur : voile noir à 56 %, fondu de 1,4 s à l'entrée comme à la sortie (début et fin du chant,
    saut, passage) ; vers en italique blanc cassé, de 1,45 rem à 3,6 rem selon la scène (7 % de
    sa largeur, 9,5 % de sa hauteur au plus), centré sous le cartouche, équilibré sur ses lignes,
    jamais coupé dans un mot ; chaque mot paraît (fondu de 0,4 s, montée de 0,12 em) 0,08 s avant
    son début chanté ; le vers suivant remplace le précédent (qui s'efface en 0,45 s) ; tous les mots
    du vers ont leur place dès le début (rien ne bouge quand ils paraissent).
  - autres surimpressions : carte, portraits et citation sont déjà retirés pendant un intermède ;
    la frise du temps est masquée au début du chant ; le cartouche de l'image (titre du chant)
    reste au-dessus du voile ; celui de la musique de fond reste masqué ; pas de sous-titre.
  - les paroles s'affichent même quand les sous-titres sont coupés (retour de l'utilisateur) ; le bouton « Sous-titres » ne les masque pas.

### Enrichissements visuels (2026-10-08)

Demande de l'utilisateur : « intéresser un peu plus visuellement ». Pistes retenues, toutes dans
la règle des documents d'époque du domaine public (Commons), monochromes hors images :

1. **Objets de musée** : photo d'un objet d'époque (cocarde, bonnet, assignat, pique, montre
   décimale, faïence révolutionnaire, maquette de la Bastille taillée dans une de ses pierres…),
   **détouré** sur fond neutre, posé en surimpression quand la voix en parle, avec une légende
   courte (objet, date, musée). Photo d'objet du domaine public ou sous licence libre admise
   (CC BY / BY-SA avec crédit ; l'objet est d'époque, la photo peut être récente).
   **Révision du 2026-10-08** : l'objet détouré est **posé directement sur l'image**, sans
   carte ni fond opaque ; il se détache par une ombre très douce ou un halo clair diffus (pas
   de contour net), la légende courte en dessous sur un voile léger.
2. **Manuscrits et signatures** : une lettre, un acte ou un registre d'époque en surimpression,
   avec zoom et halo doux sur la signature ou la phrase dont parle la voix (même halo que les
   documents d'épisode).
3. **Avant / après** : volet glissant lent entre deux images d'un même lieu ou d'un même sujet à
   deux moments (place Louis-XV / place de la Révolution, Sainte-Geneviève / Panthéon…), avec le
   cartouche de chacune.
4. **Chiffres clés et dates** : un nombre en grand qui s'écrit sur l'image quand la voix le dit
   (« 7 prisonniers »), et la correspondance d'une date du calendrier républicain (« 9 thermidor
   an II » → « 27 juillet 1794 »), discrète. Chiffres exacts et sourcés.
5. **Mosaïque puis plongée** : 4 à 6 images d'un même événement apparaissent en grille, puis la
   caméra plonge dans l'une d'elles, qui devient l'image de la diapositive.
   **Révision du 2026-10-08** : les vignettes sont **toutes présentes dès le début** (jamais d'apparition une à une sur du blanc) ; elles sont ensuite **mises en valeur une par une** (la vignette en cours en pleine couleur et légèrement avancée, les autres atténuées en gris voilé), puis la caméra plonge dans l'image principale.
6. **Parallaxe 2,5D** : les plans d'un tableau séparés par estimation de profondeur glissent très
   lentement l'un sur l'autre. **Banc d'essai d'abord** sur 3 ou 4 images de la Révolution ; on
   ne généralise (une par acte) que si l'utilisateur valide le rendu.

**Dosage, par période** : ~10 objets, ~8 chiffres ou dates, 3 à 4 avant/après, 3 à 4
manuscrits, 2 mosaïques, ~8 parallaxes (si validées). **Deux surimpressions au plus à la fois** ;
l'image reste le sujet. Les zones couvertes ne font jamais bouger la caméra brusquement.

**Valeurs retenues, points 1 et 2** (mise en œuvre du 2026-10-08 ; détail dans
`scripts/diaporamas/README.md`, « Objets de musée et manuscrits ») :
- données : `objets` et `manuscrits` dans la diapositive, `{ id, quand, instant, cote }` (un de chaque
  au plus) ; registre commun `src/data/diaporamas/objets.json` ; `scripts/diaporamas/objets.py`
  (licence par l'API : domaine public, CC0, CC BY, CC BY-SA ; détourage local par rembg
  `isnet-general-use`, enveloppe convexe pour les faïences et médailles ; webp transparent de 720 px
  au plus) ; crédits « Objets et documents » sur la page ;
- objet : coin bas (droite par défaut), cartouche blanc cassé à filet fin, objet en couleur de 22 % de
  la hauteur de la scène (96 à 200 px), légende « objet » / « date · musée » ; fondu de 0,8 s, montée
  de 10 px ; ~5 s depuis le passage ; place réservée pour la caméra toute la diapositive ;
- manuscrit : sur un côté, sous le cartouche, 72 % de la hauteur au plus ; ~8 s ; zoom doux 1 s après
  l'entrée (2,5 s, 2,4 fois au plus), puis halo en 1,2 s, le même que les documents d'épisode ; ne
  réserve rien pour la caméra ;
- **priorités** : citation > manuscrit > portraits = médaillon de lieu > objet > frise ; jamais plus de
  deux à la fois (contrôlé par `verifier.py`) ; l'élément de rang inférieur est raccourci, reporté ou
  omis, la frise masquée ;
- Révolution : 10 objets (Carnavalet, Musée de l'Armée, Archives nationales) et 3 manuscrits
  (certificat de civisme de Brest, décret d'abolition de l'esclavage, appel à la section des Piques
  signé « Ro ») ; caméra mesurée à nouveau sur ces 13 diapositives (1280 × 720, 1920 × 1080, 390 × 844) :
  rien au-dessus des plafonds, aucun saut.

**Valeurs retenues, point 4** (mise en œuvre du 2026-10-08 ; détail dans `scripts/diaporamas/README.md`,
« Chiffres clés et dates républicaines ») :
- données : `chiffres` `{ quand, valeur, prefixe?, unite, source, instant }` et `dates_republicaines`
  `{ quand, republicain, gregorien, relu?, instant }` dans la diapositive, un de chaque au plus ; seuls des
  nombres dits par la voix, avec leur prudence (« plus de ») et une source vérifiée ; conversion par les
  tables officielles (1er vendémiaire an I = 22 septembre 1792, années sextiles III, VII, XI ; pas la
  règle de Romme), écrite par `surimpressions.py`, recalculée et confirmée par `verifier.py` ;
- chiffre : centré dans le tiers inférieur, grand serif (15 % de la hauteur de la scène, 54 à 112 px),
  « 300 000 » avec espace fine, prudence au-dessus et unité dessous en petites capitales, voile blanc
  cassé local aux bords fondus ; défile de 0 à sa valeur en 1,4 s à partir de 20, sinon fondu ; ~4 s
  (3 s au moins) ; ne réserve rien pour la caméra ; monte au-dessus d'une surimpression de coin ou de la
  date qui se montre avec lui, pour toute la diapositive. Chiffres elzéviriens impossibles avec l'EB
  Garamond de Google Fonts (pas de variante `onum`) : chiffres alignés ;
- date : bandeau voilé fin en petites capitales au bas de l'image, au centre, « 9 thermidor an II ·
  27 juillet 1794 » ; ~5 s (3 s au moins) ; au-dessus de la frise ;
- **priorités** : citation > manuscrit > portraits = médaillon de lieu > objet ≥ chiffre > date > frise ;
  jamais plus de deux à la fois ; ni le chiffre ni la date avec la citation ;
- Révolution : 8 chiffres (7 prisonniers à la Bastille, 83 départements, plus de 1 000 détenus massacrés
  en septembre 1792, 300 000 hommes à lever, 29 députés girondins arrêtés, plus de 1 300 exécutions de la
  Grande Terreur, plus de 700 fusillés après Quiberon, plus de 150 savants en Égypte) et 7 dates
  (22 prairial an II, 9 thermidor an II, 1er prairial an III, an III, 13 vendémiaire an IV, 18 fructidor
  an V, 18 brumaire an VIII) ; caméra mesurée à nouveau sur ces 14 diapositives : rien au-dessus des
  plafonds, aucun à-coup.

**Valeurs retenues, points 3 et 5** (mise en œuvre du 2026-10-08 ; détail dans
`scripts/diaporamas/README.md`, « Avant / après et mosaïques ») :
- avant / après : `image.apres` `{ fichier, commons, titre, titre_court, auteur, date, technique,
  conservation, licence, utile, cadre, quand, camera? }` (l'image de la diapositive est l'« avant ») ;
  volet glissant de 3,5 s (de gauche à droite, smoothstep), bord en ligne verticale fine, au passage
  `quand` ; caméra de l'avant arrêtée en douceur au passage, les deux images fixes pendant le volet et
  superposées par leurs cadres correspondants (vue de départ de l'après = vue finale de l'avant
  transportée par la correspondance des deux cadres), puis caméra de l'après ; cartouche de l'après dès
  le début du volet ; mouvement réduit : fondu enchaîné de 1 s ;
- mosaïque : `mosaique` `{ legende, vignettes: [{ fichier, commons, titre, auteur, date, technique?,
  conservation?, licence, utile }], principale }` ; grille en 2 lignes (2 × 2, 2 sur 3, 3 × 2), filets de
  papier de 4 px ; vignettes en fondu gris → couleur (0,8 s), une toutes les 0,5 s ; grille tenue 1 s ;
  plongée par homothétie de la grille (zoom logarithmique, plafonds de la caméra : ~5 s, 95 % du plafond
  de zoom au plus fort), la case principale grandit jusqu'à la scène et l'image principale arrive
  exactement sur sa première vue ; cartouche d'une ligne pendant la grille, normal dès la plongée ;
  mouvement réduit : grille fixe puis fondu de 0,8 s ; crédits de toutes les vignettes sur la page ;
- Révolution : avant/après 20 (Bastille, Lallemand vers 1780 → Hubert Robert 1789), 57 (Louis XVI,
  Callet → « Louis Capet » à la barre), 59 (place Louis-XV, Janinet vers 1787 → place de la Révolution,
  Helman d'après Monnet) ; narrations 20 et 59 retouchées pour annoncer le changement ; mosaïques 18
  (cinq vues de la prise de la Bastille) et 53 (quatre vues de la prise des Tuileries). Caméra mesurée
  (1280 × 720, 1920 × 1080, 390 × 844, plein écran 1920 × 1080, mouvement réduit) : rien au-dessus des
  plafonds, aucun à-coup, rien hors de la zone utile.

**Valeurs retenues, révision du point 1** (2026-10-08) : objet sans carte ni fond, `filter:
drop-shadow(0 0 7px` blanc cassé à 75 %`) drop-shadow(0 3px 9px` noir à 35 %`)`, légende sur un voile
blanc cassé à 82 % ; taille, coin et place réservée inchangés ; lisible sur image claire (22, 104, 120)
comme plus sombre (23).

**Valeurs retenues, révision du point 5** (2026-10-08) : grille entière dès l'entrée de la diapositive ;
mise en valeur à tour de rôle, 0,9 s par vignette depuis 1 s de voix, les autres d'abord dans l'ordre de
la grille et la principale en dernier, fondus croisés de 0,4 s ; vignette en cours en pleine couleur,
échelle 1,03 (sans ombre), au-dessus des autres ; autres en gris voilé (`grayscale` 85 %, opacité 55 %
sur le fond de scène) ; avant le premier tour, toutes en couleur ; la principale garde sa couleur après
son tour et revient à l'échelle 1 avant la plongée ; tenue de 0,6 s, puis plongée inchangée (5 vignettes :
plongée à 6,1 s de voix au lieu de 4,1). Cartouche d'une ligne pendant la grille. Mouvement réduit :
grille fixe en couleur, sans mise en valeur, puis fondu de 0,8 s. Mesuré (18 et 53, 1280 × 720 et
1920 × 1080) : plongée à 95 % du plafond de zoom au plus fort, aucun à-coup.

**Valeurs retenues, point 6, banc d'essai** (mise en œuvre du 2026-10-08 ; détail dans
`scripts/diaporamas/README.md`, « Parallaxe 2,5D ») — **en attente de validation par l'utilisateur** :
- données : `image.parallaxe` `{ plans: [fond, …, premier plan], amplitude }` (2 ou 3 webp dans
  `public/diaporamas/<slug>/parallaxe/`, amplitude 0,005 à 0,02), écrit par
  `scripts/diaporamas/parallaxe.py` : profondeur par Depth Anything V2 Small (libre, local), seuils
  d'Otsu, alpha en rampe de profondeur (net sur les occlusions, fondu sur les surfaces continues),
  comblement OpenCV (Telea) sous les plans proches, couleurs de bord démêlées (composition au repos =
  l'image), planche de contrôle ; ignoré sur un avant / après ou une mosaïque ;
- lecteur : les plans prennent la caméra ; premier plan jusqu'à l'amplitude, plan moyen de moitié,
  fond fixe ; glissement seulement pendant les tenues de la caméra, à partir de 2 s de voix (l'entrée
  gris → couleur est finie : décalage nul jusque-là), rampes de 2,5 s, vitesse de croisière constante
  plafonnée à 0,25 % de la scène par seconde (amplitude réduite au besoin), à sens unique, figé dans
  les transitions de caméra et le fondu vers la diapositive suivante ; jamais de bord de calque ni rien
  hors de la zone utile (sens vers la plus grande marge, agrandissement du plan proportionnel à
  l'avancement si la marge manque) ; relève invisible image → plans au décalage nul, abandon si les
  plans arrivent trop tard ; `prefers-reduced-motion` : pas de parallaxe ;
- banc d'essai : 47 (Pils), 56 (Vernet, Valmy), 81 (Hubert Robert, Saint-Denis), 122 (Lejeune,
  Pyramides), 3 plans, amplitude 0,015 (retenue 0,9 à 1,5 % selon les tenues) ; mesuré (1280 × 720,
  1920 × 1080, 390 × 844, mouvement réduit) : caméra inchangée et sous les plafonds, aucun saut, vitesse
  relative des plans de 0,13 à 0,30 % de la scène par seconde au plus fort, continue, aucun bord de zone
  utile visible ; plans : 815 Ko pour les quatre (1,6 fois l'image).

### Marges des surimpressions du bas (2026-10-08)

Retour de l'utilisateur : les surimpressions du bas (portraits, médaillon de carte, objets,
manuscrits, et toute surimpression de coin) doivent avoir **les mêmes marges que les cartouches
du haut** : même retrait à gauche et à droite (alignées avec le cartouche de l'image et celui de
la musique), et en bas le même retrait par rapport au bord de l'image. **En plein écran**, quand
les contrôles sont masqués, elles descendent à cette marge du bas de l'écran au lieu de rester
au-dessus de la barre de lecture invisible ; quand les contrôles réapparaissent, elles remontent
en douceur juste au-dessus d'eux (ou les contrôles passent par-dessus sans les masquer, selon ce
qui est le plus sobre). La zone réservée pour la caméra reste constante (pas de mouvement de
caméra lié à l'apparition des contrôles).

**Valeurs retenues** (mise en œuvre du 2026-10-08) : variables `--marge-x` / `--marge-y` de la scène,
partagées par les cartouches du haut et les surimpressions de coin (`var(--e-2)` d'ordinaire,
téléphone compris ; `var(--gouttiere)` et `var(--e-3)` en plein écran) ; en plein écran, contrôles
masqués, le sous-titre descend à leur place (450 ms) et les surimpressions avec lui (à la marge du
bas de l'écran quand les sous-titres sont coupés), puis remontent en douceur (500 ms) au retour des
contrôles ; la place réservée pour la caméra compte toujours tous les bandeaux (mesurée sans la
descente) : aucun mouvement de caméra lié aux contrôles (mesuré en plein écran 1920 × 1080, contrôles
qui apparaissent et disparaissent).

## Portail (`/diaporamas/`)

Titre « Le siècle en images ». Une courte présentation (voix de synthèse, images du domaine
public de Wikimedia Commons, durée totale), puis les 9 périodes : numéro, titre, dates,
durée, une image-vignette en gris (charte) et le résumé. Une période pas encore produite est
listée en gris sans lien (« à venir »). Ajouter la section à la page d'accueil et à la
navigation commune, par petites touches.

## Chaîne de production (`scripts/diaporamas/`)

1. **Écriture** (agent) : le JSON de la période (actes, narrations, choix des fichiers Commons et
   cadrages). C'est le travail de fond, fait avec recherche sur Commons.
2. `images.py <slug>` : pour chaque diapositive, interroge l'API Commons (`imageinfo`,
   `extmetadata`), **refuse** une licence non libre, télécharge l'original (cache dans
   `.cache/`, déjà ignoré par git), redimensionne en 1600 px webp et complète les métadonnées
   manquantes. User-Agent explicite, débit raisonnable.
3. `voix.py <slug> [--n 12]` : applique le lexique, synthétise chaque diapositive (Gemini,
   Charon), contrôle de fidélité, encode en m4a (ffmpeg), écrit `audio.duree`. Ne refait que ce
   qui manque ou dont la narration a changé (empreinte du texte enregistrée dans un fichier
   d'état de `.cache/`).
4. `verifier.py <slug>` : nombre de diapositives (90 à 110), chaque image et audio présents,
   licences libres, métadonnées complètes, durée totale, narrations de 25 mots au plus par phrase.

## Critères de fin du pilote

- `/diaporamas/` et `/diaporamas/revolution/` fonctionnent, sur ordinateur et téléphone.
- Diaporama Révolution complet : ~100 diapositives, toutes avec image, légende et audio vérifiés.
- `python3 scripts/diaporamas/verifier.py revolution` passe ; `npm run build` passe.
- Un compte rendu à l'utilisateur : durée, coût approximatif de synthèse, images douteuses ou
  remplacées, échecs de fidélité, points à trancher avant la production en série.
