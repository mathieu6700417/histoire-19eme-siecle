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
