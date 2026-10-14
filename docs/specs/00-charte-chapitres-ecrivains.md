# Charte — section « Le siècle raconté par ses écrivains » (chapitres 2 à 8)

Source unique des règles **en vigueur** pour écrire un chapitre de la section. Elle consolide
les specs 02 (cadre et chapitre 1) et 03 (prologue), qui gardent l'historique des décisions :
**en cas de divergence, la présente charte prévaut.** Les règles générales du site
(`CLAUDE.md` : français, typographie, niveau, design, git) s'appliquent en plus.

Le prologue (`00-prologue`, 21 extraits) et le chapitre 1 (`01-revolution`, 28 extraits) sont
les modèles de référence : en cas de doute sur une forme, faire comme eux.

---

## 1. Objet et démarche

Une histoire de la France de 1789 à 1900 **portée par les textes** des écrivains. Le lecteur
traverse le siècle comme une anthologie commentée : les extraits passent d'abord, de courtes
transitions font avancer le récit, et un appareil replié (contexte, mots expliqués, regard
critique, fiche auteur) aide à les lire comme des **sources, avec leurs biais**. Niveau lycée /
culture générale. Périmètre : la France (les faits racontés se passent en France ou concernent
directement la France ; textes écrits en français, pas de traductions).

### Découpage : prologue + 8 chapitres, un par régime

| N° | Slug conseillé | Titre (`chapitres-ecrivains.ts`) | Période | État |
| --- | --- | --- | --- | --- |
| 0 | `00-prologue` | La France avant 1789 | 1774-1788 | écrit |
| 1 | `01-revolution` | La Révolution | 1789-1799 | écrit |
| 2 | `02-consulat-empire` | Consulat et Empire | 1799-1815 | écrit |
| 3 | `03-restauration` | La Restauration | 1814-1830 | écrit |
| 4 | `04-monarchie-de-juillet` | La monarchie de Juillet | 1830-1848 | écrit |
| 5 | `05-deuxieme-republique` | 1848 et la IIe République | 1848-1852 | écrit |
| 6 | `06-second-empire` | Le Second Empire | 1852-1870 | écrit |
| 7 | `07-annee-terrible` | L'année terrible : guerre et Commune | 1870-1871 | écrit |
| 8 | `08-troisieme-republique` | La IIIe République jusqu'à 1900 | 1871-1900 | écrit |

Un chapitre est « écrit » dès qu'un fichier de `src/content/ecrivains/xixe/` porte son `numero` ;
les autres apparaissent grisés (« à venir ») sur l'accueil de la section. La navigation
précédent / suivant, l'accueil de la section et l'index des auteurs se mettent à jour seuls.
Le slug est libre, mais il commence par le numéro sur deux chiffres.

---

## 2. Choix des textes

### Qui peut figurer

**Règle générale (chapitres 2 à 8) : des écrivains ayant vécu au XIXe siècle**, c'est-à-dire
morts après 1800. « Écrivain » s'entend largement : romanciers, poètes, dramaturges,
mémorialistes, historiens, journalistes, orateurs, essayistes, à condition que le texte ait une
valeur littéraire ou de témoignage. Les documents anonymes ou collectifs (cahiers, rapports,
textes de loi) sont écartés.

**Exceptions, chacune limitée à son périmètre** (aucune ne s'étend aux chapitres 2 à 8) :

| Exception | Périmètre exact | Conditions |
| --- | --- | --- |
| Auteurs morts avant 1800 | **prologue et chapitre 1 seulement** | Texte écrit pendant la période (Beaumarchais, Chamfort, Gouges, Saint-Just, Robespierre, Condorcet, Chénier…). Signalé dans l'introduction du chapitre et sur la fiche (champ `exception` de `auteurs.ts`). |
| Textes fondateurs antérieurs à 1770 | **prologue seulement**, partie « Les sensibilités politiques avant 1789 » | Textes que lisent les hommes de 1789 (Montesquieu 1748, Rousseau 1762, Voltaire 1764, Diderot 1751, Moreau 1757). Date bien visible ; le chapeau explique leur présence ; pas de prop `regard` ; `faits` = année de publication (ils comptent donc parmi les témoins). |

Pour les chapitres 2 à 8, un auteur mort avant 1801 ou un texte antérieur à la période du
chapitre n'est pas admis. Un texte écrit avant la période mais qui l'annonce, ou un auteur
étranger, demande l'accord explicite de l'utilisateur, consigné dans la spec du chapitre.

### Contemporains et rétrospectifs : environ deux tiers / un tiers

- **Texte contemporain** (`regard="contemporain"`) : écrit pendant les faits ou dans les quelques
  années qui suivent (en pratique moins de dix ans ; le plus éloigné des modèles est
  La Rochejaquelein, écrit 5 à 7 ans après). Mémoires rédigés sur le moment, journaux,
  correspondances, articles, discours, poèmes et romans écrits « à chaud ».
- **Regard rétrospectif** (`regard="retrospectif"`) : souvenir écrit des décennies plus tard,
  histoire, roman historique.
- **Cible pour les chapitres 2 à 8 : environ deux tiers de textes contemporains et un tiers de
  regards rétrospectifs.** (Le chapitre 1, écrit avant cette règle, en a 11 sur 28 ; on ne le
  modifie pas.) Les romans, pièces et poèmes contemporains des faits sont les bienvenus.

### Équilibre des camps et des genres

- **Camps** : un chapitre ne doit pas être vu par un seul bord. Au moins trois sensibilités
  politiques de l'époque, chacune nommée dans un chapeau ou un regard critique, et aucune ne
  fournit plus de la moitié des extraits. Pour chaque grand épisode, chercher au moins une voix
  favorable et une voix hostile.
- **Genres** : au moins quatre des sept genres dans le chapitre, dont au moins un genre de fiction
  ou de poésie. Les sept genres (`src/data/genres.ts`), avec le libellé affiché :

| id | Libellé affiché | Pour |
| --- | --- | --- |
| `temoignage` | Témoignage | mémoires, souvenirs, journaux, correspondances, choses vues |
| `roman` | Roman (fiction) | romans et nouvelles, toujours signalés comme fiction |
| `theatre` | Théâtre | scènes de pièces |
| `poesie` | Poésie | poèmes (avec la prop `poeme`) |
| `presse` | Presse / discours | articles, pamphlets, brochures, discours, déclarations |
| `histoire` | Récit historique | historiens (Michelet, Lamartine…), même quand ils ont connu l'époque |
| `essai` | Essai | réflexion politique, philosophique ou morale (Tocqueville, Maistre, Rousseau…) |

Un nouveau genre ne s'ajoute que si aucun des sept ne convient (voir § 7).

---

## 3. Format d'un chapitre

| Élément | Règle |
| --- | --- |
| Nombre d'extraits | **au moins 20** (modèles : 21 et 28 ; viser 20 à 30). |
| Texte complet | **400 à 900 mots** par extrait : une scène ou un épisode complet, 1 à 2 pages. Seule exception : la poésie, sans minimum (la plus courte des modèles fait 370 mots). Le théâtre peut faire un peu moins de 400 mots si la scène est complète (accord à consigner dans la spec). |
| Passage clé | **150 à 350 mots** (viser 200 à 300) : une suite **contiguë** de paragraphes ou de strophes du texte complet, prise telle quelle, **sans coupure `[…]`**, pas forcément au début. C'est la version affichée par défaut. |
| Ordre | chronologique des **faits racontés** (pas des dates d'écriture). |
| Parties | 3 à 5 parties (`<Partie>`), chronologiques en général (« 1792 : la guerre et la chute de la monarchie »), de 4 à 9 extraits chacune. Thématiques seulement si le chapitre s'y prête (prologue). |
| Introduction | 1 paragraphe dans `<div class="introduction">` : bornes, enjeu, et les noms des auteurs contemporains et rétrospectifs réunis. |
| Transitions | 1 à 3 phrases par transition, dans `<div class="transition">`, **juste avant l'extrait qu'elle introduit** (voir ci-dessous). Pas de transition avant le premier extrait. |
| Conclusion | 1 paragraphe sous `<h2 id="conclusion">Conclusion</h2>`, qui ouvre sur le chapitre suivant (le lien « chapitre suivant » est ajouté par la mise en page). |
| Durée de lecture | `dureeLecture` (minutes) = durée en mode « Tous », textes complets et appareil compris : environ 150 mots des textes complets par minute, arrondi à 5 minutes (modèles : 105 et 130). Viser 1 h 30 à 2 h 15. La page la recalcule au prorata des mots visibles selon le filtre. |

### Transitions et filtre à trois modes

Le filtre de chaque chapitre propose trois modes, avec ces libellés de boutons : **« Témoins ·
Postérieurs · Tous »** (infobulles « Auteurs qui ont vécu les faits » et « Auteurs des générations
suivantes »), et un compteur « N textes sur M ». Le mode par défaut est **Témoins**. Le choix est
mémorisé pour tous les chapitres (`localStorage`, clé `ecrivains-filtre`). Un extrait masqué
disparaît avec la transition qui le précède immédiatement, avec sa ligne du sommaire et, si
elle est vide, avec sa partie ; la numérotation est recalculée.

Conséquence pour la rédaction : **chaque transition doit se lire dans les trois modes.**
- Elle ne raconte que ce qui mène à l'extrait **qui la suit** ; elle disparaît avec lui.
- Elle ne nomme pas l'auteur ou le texte précédent et ne dit pas « comme on vient de le voir »,
  « ce même Chateaubriand », « en réponse à Michelet » : le texte précédent peut être masqué.
- Elle ne doit pas être la seule à donner un fait indispensable pour comprendre la suite du
  chapitre ; si elle l'est, reporter ce fait dans le chapeau de l'extrait concerné.
- Avant de finir, lire le chapitre dans les trois modes (voir § 8) et neutraliser toute phrase
  qui suppose un texte masqué.

---

## 4. Exactitude

- **Sources** : Wikisource (fr.wikisource.org) d'abord. Gallica seulement si Wikisource n'a pas
  le texte, et avec l'accord de l'utilisateur : le vérificateur ne sait contrôler que Wikisource
  (un extrait Gallica y échouera et doit être vérifié à la main, avec `source="Gallica"`).
- **Mot pour mot** : chaque texte est extrait par script (`scripts/ecrivains/`), jamais recopié
  de mémoire ni retapé, jamais paraphrasé entre guillemets. Orthographe et ponctuation de
  l'édition conservées (« 1o » de l'édition devient `1<sup>o</sup>`, seule retouche admise).
  Les appels de note `[n]` et les numéros de page de l'édition sont retirés.
- **Coupures** : signalées par `[…]` dans un paragraphe à part (segment `"CUT"`). Le moins
  possible, jamais dans le passage clé.
- **Lien** « Lire le chapitre complet » : vers la page **la plus précise possible** (chapitre,
  lettre, poème, article), jamais vers la page d'accueil de l'œuvre. Construit automatiquement
  à partir du champ `page` de la spécification JSON.
- **Vérification** : `npm run verifier:ecrivains` télécharge à neuf chaque page à l'URL du lien
  et contrôle (1) HTTP 200, (2) chaque paragraphe ou vers présent mot pour mot, (3) texte de
  400 à 900 mots (pas de minimum pour un poème), (4) un seul passage clé, de 150 à 350 mots,
  contenu dans le texte complet. Tout doit être « ok ».
- **Source introuvable** : si le texte n'est pas sur Wikisource (ou pas dans l'édition voulue),
  ou si la page ne se laisse pas vérifier, **l'extrait n'est pas publié** : choisir un autre
  passage, une autre œuvre ou un autre auteur, et le signaler dans le compte rendu.
- **Faits donnés de mémoire** : l'appareil (chapeau, notes, regard critique, fiche, transitions)
  est rédigé sans source citée. Dates et noms exacts ; en cas de doute, formulation prudente
  (« vers 1798-1800 », « selon ses Mémoires »). Tout fait dont on n'est pas sûr est vérifié
  ou retiré, et ceux qu'on n'a pas pu vérifier sont **listés dans le compte rendu**.
- **Références** : chaque extrait porte auteur, œuvre, partie / livre / chapitre (`reference`),
  date d'écriture et de publication en clair (`date`), et l'édition si elle diffère de
  l'originale (« texte de l'édition de 1888 »).

---

## 5. Appareil d'un extrait

Visibles par défaut : titre de l'extrait, ligne de référence (genre · auteur · œuvre · date ·
contemporain / rétrospectif · témoin / génération suivante), passage clé avec « Voir plus »,
référence et lien. Tout le reste est replié dans des `<details>`.

| Bloc | Contenu |
| --- | --- |
| Titre (`titre`) | Ce que montre le texte et la date des faits entre parenthèses : « La Bastille, les têtes au bout des piques (juillet-août 1789) ». Pas de guillemet droit `"` dedans. |
| **Contexte** (slot `chapeau`, 3 à 6 phrases) | Commence par l'étiquette et l'écart : « Texte contemporain : publié en janvier 1789, au moment même où… » ou « Regard rétrospectif : écrit en 1821, trente-deux ans après les faits. » ; pour un texte fondateur : « Texte antérieur à la période (1748), retenu parce que… ». Puis ce qui se passe, qui parle, d'où il parle. Pour un roman : « Roman : … ». |
| **Mots expliqués** (prop `notes`) | Mots, allusions, noms propres difficiles ; une note brève par entrée, dans l'ordre du texte. Rien si inutile. |
| **Regard critique** (slot `critique`, 2 à 4 phrases) | Ce que le texte montre, en quoi il est partial ou limité (camp de l'auteur, fiction ou témoignage, recul, ce qu'il ne dit pas) ; pour un texte d'idées : qui le lisait, son influence, qui il ne représente pas. |
| **Fiche auteur** (prop `fiche`) | « Qui est X ? » : à la **première apparition** de l'auteur dans le chapitre, et là seulement (le build avertit sinon). Données dans `auteurs.ts`. |

### Étiquettes de la ligne de référence

- **Contemporain / rétrospectif** : saisi à la main (prop `regard`, § 2). Affiché « texte
  contemporain des faits » ou « regard rétrospectif ». Omis seulement pour les textes fondateurs
  du prologue.
- **Témoin / génération suivante** : **calculé au build**, jamais saisi. Critère : l'auteur est
  **né au moins 10 ans avant l'année des faits** racontés (`naissance.annee + 10 <= faits`).
  Avec une plage (`faits="1792-1797"`), on retient la première année. Affiché « témoin » ou
  « regard d'une génération suivante ». Un auteur témoin peut écrire tard (Chateaubriand en
  1821 est « regard rétrospectif · témoin »).
- La prop `faits` est donc **obligatoire** (le build avertit si elle manque).
- Si un même auteur est témoin pour un extrait et non témoin pour un autre, vérifier que sa fiche
  reste visible dans chaque mode (sinon, le signaler : la fiche n'apparaît qu'une fois).

---

## 6. Convention MDX

Fichier `src/content/ecrivains/xixe/<slug>.mdx`, généré par `scripts/ecrivains/generer.py` à partir de
`scripts/ecrivains/chapitres/xixe/<slug>.gabarit.mdx` et `<slug>.json` (voir le README des scripts).
On rédige le **gabarit**, où le texte et le lien de chaque extrait sont les marques `@@T:id@@`
et `@@L:id@@` ; le script y insère les textes exacts, le passage clé et les appels de note.

### Frontmatter et en-tête

```mdx
---
titre: "Consulat et Empire"
numero: 2
periode: "1799-1815"
resume: "Une ou deux phrases : ce que racontent les textes, et les principaux auteurs."
dureeLecture: 120
---
import Extrait from '../../../components/Extrait.astro';
import Appel from '../../../components/Appel.astro';
import Partie from '../../../components/Partie.astro';

<div class="introduction">

Un paragraphe : bornes, enjeu, auteurs contemporains et rétrospectifs réunis.

</div>

<Partie id="partie-1799" titre="1799-1804 : le Consulat" />
```

Schéma (`src/content.config.ts`) : `titre`, `numero` (entier de 0 à 8), `periode`, `resume`,
`dureeLecture` (entier positif). Le `titre` et la `periode` reprennent ceux de
`chapitres-ecrivains.ts`.

### Modèle d'extrait (gabarit, prêt à copier)

Les valeurs sont des exemples à remplacer (« 18.. », « … » : à établir d'après la source).

```mdx
<Extrait auteur="chateaubriand" fiche id="sacre" titre="Le sacre (2 décembre 1804)" regard="retrospectif" genre="temoignage" faits="1804" oeuvre="Mémoires d'outre-tombe" ecrit="écrit en 18.." reference="… partie, livre …" date="écrit en 18.. ; publication posthume en 1848-1850" lien="@@L:sacre@@"
  notes={[
    { mot: "Notre-Dame", texte: "la cathédrale de Paris, où a lieu la cérémonie." },
    { mot: "Pie VII", texte: "pape de 1800 à 1823, venu de Rome pour la cérémonie." },
  ]}>
<div slot="chapeau">

Regard rétrospectif : écrit en 18.., N ans après les faits. Ce qui se passe, qui parle, d'où il parle.

</div>
<div slot="texte">

@@T:sacre@@

</div>
<div slot="critique">

Ce que le texte montre, et en quoi il est partial ou limité.

</div>
</Extrait>

<div class="transition">

Une à trois phrases qui mènent au texte suivant, lisibles même si le texte précédent est masqué.

</div>
```

**Règles de forme (lues par des scripts : les respecter à la lettre)**
- **`auteur` en premier**, suivi de **`fiche`** quand c'est la première apparition de l'auteur ;
  puis `id` et `titre` tout de suite après (le sommaire les lit dans les 800 premiers caractères).
  Ordre conseillé ensuite : `regard`, `genre`, `faits`, `poeme`, `oeuvre`, `ecrit`, `reference`,
  `date`, `lien`, `source`, `notes`.
- Toutes les props sur la ligne d'ouverture, valeurs entre guillemets droits `"…"`, sans `"`
  à l'intérieur (guillemets français « » dans les titres).
- `id` : court, en minuscules, sans accent, unique dans le chapitre (`sacre`, `austerlitz`).
- `ecrit` : date courte affichée (« 1838 », « écrit en 1838 », « janvier 1789 », « vers 1798-1800 »).
- `faits` : année (`"1804"`) ou plage (`"1792-1797"`).
- `poeme` : pour les vers (garde les retours à la ligne). `source="Gallica"` si le lien n'est
  pas Wikisource (Wikisource par défaut).
- `notes` : un objet par ligne, `{ mot: "…", texte: "…" }` **avec des guillemets doubles**
  (le générateur les lit ainsi), dans l'ordre d'apparition dans le texte ; `mot` est le mot tel
  qu'il figure dans le texte (apostrophe droite admise). Sinon, donner l'ancre dans `ancres`.
- Chaque `<div slot="…">` et chaque `<div class="…">` est suivi et précédé d'une **ligne vide**
  (sinon le Markdown n'est pas interprété).
- `<Partie id="partie-…" titre="…" />` sur sa propre ligne, entre deux extraits.

### Ce que produit le générateur dans le slot `texte`

```mdx
<div slot="texte">

Paragraphe avant le passage clé.

[…]

<div class="cle">

Premier paragraphe du passage clé, avec un appel de note après le mot Notre-Dame<Appel ex="sacre" n={1} /> expliqué.

Dernier paragraphe du passage clé.

</div>

Paragraphe après le passage clé.

</div>
```

- `<div class="cle">` : une ligne vide après l'ouverture et avant la fermeture ; un seul par extrait.
- Appel de note : `<Appel ex="<id de l'extrait>" n={<numéro>} />`, collé au mot, numéroté
  à partir de 1 dans l'ordre de `notes`.
- Vers : une ligne par vers, une ligne vide entre les strophes.
- Ne jamais retoucher ce slot à la main : corriger la spécification JSON et regénérer.

---

## 7. Données

### Ajouter un auteur (`src/data/xixe/auteurs.ts`)

Une entrée par auteur dans `liste`, à la fin ou près des auteurs du même chapitre :

```ts
  {
    id: 'constant',                      // identifiant de la prop auteur, sans accent
    nom: 'Benjamin Constant',            // nom complet (titre de la fiche)
    court: 'Constant',                   // nom court des références
    tri: 'Constant',                     // clé de tri alphabétique (nom de famille)
    naissance: { annee: 1767, lieu: 'Lausanne' },
    mort: { annee: 1830, lieu: 'Paris' },
    position: 'Libéral ; opposant à Napoléon, puis député sous la Restauration',
    couleur: c.orleanistes.couleur,       // courant le plus proche (gris : site monochrome)
    oeuvres: ['Adolphe (1816)'],          // œuvres citées dans la section, avec leur date
    portrait: "Deux ou trois phrases : origine, rôle, œuvres, ce qui éclaire le texte.",
    // exception: "…",                    // seulement prologue / chapitre 1 (auteur mort avant 1800)
  },
```

- `couleur` : `c.<courant>.couleur`, où `<courant>` est l'une des clés de
  `src/data/xixe/courants-politiques.ts` (`legitimistes`, `orleanistes`, `bonapartistes`,
  `republicains`, `radicaux`, `socialistes`, `anarchistes`, `catholiques`, `nationalistes`).
  Ce sont des niveaux de gris : ne pas y mettre de couleur.
- `naissance.annee` est indispensable : elle décide du statut témoin.
- Pour un auteur déjà présent, **compléter `oeuvres`** avec la nouvelle œuvre citée.
- `exception` : n'a plus d'usage dans les chapitres 2 à 8 (§ 2).

### Ajouter un genre (`src/data/genres.ts`)

Seulement si aucun des sept ne convient, et avec l'accord de l'utilisateur :
`nouveau: { id: 'nouveau', libelle: 'Libellé' }`. Pas de couleur. Le type `IdGenre` suit
automatiquement ; un genre inconnu fait échouer le build.

### Le chapitre dans `src/data/xixe/chapitres-ecrivains.ts`

Les neuf chapitres (0 à 8) y sont déjà déclarés (`numero`, `titre`, `periode`). Il n'y a rien
à ajouter pour un nouveau chapitre ; ne modifier titre ou période qu'avec l'accord de
l'utilisateur, et alors aussi dans le frontmatter.

---

## 8. Style

Les règles de design sont celles de `CLAUDE.md` : **édition savante, strictement monochrome**
(noir, gris, blanc cassé), une seule famille serif, liens soulignés, petites capitales grises et
filets fins, ni fonds colorés, ni ombres, ni badges pleins. **Ne pas réintroduire de couleur**,
ni par les genres, ni par les courants, ni dans un composant. Un chapitre n'a besoin d'aucun CSS
propre : n'utiliser que les composants existants (`Extrait`, `Appel`, `Partie`) et les classes
`introduction`, `transition`, `cle`.

Typographie française : guillemets « », apostrophe typographique dans les textes cités (ceux de
Wikisource l'ont déjà). Dans la prose de l'appareil, on peut taper les espaces normales avant
`:` `;` `?` `!` et l'apostrophe droite : le plugin de typographie du site les convertit.

### Illustrations

Chaque chapitre est illustré d'œuvres d'art de l'époque selon `docs/specs/11-ecrivains-illustrations.md`
(qui fait foi) : 6 à 10 œuvres, une en tête de chaque `<Partie>` (prop `frontispice`), les autres
juste après l'extrait qu'elles éclairent ; composant `Oeuvre` (`src/components/Oeuvre.astro`,
documenté en tête), artistes dans `src/data/xixe/artistes.ts`, images Wikimedia Commons (domaine
public ou CC0) dans `src/assets/oeuvres/xixe/<NN>/<id>.jpg` (≤ 2000 px, JPEG). Seule exception à la
règle monochrome : gris dans la page, couleur dans la visionneuse.
- Placer une `<Oeuvre>` **entre deux blocs** : après un `</Extrait>` ou juste après une
  `<Partie … />`, jamais entre une transition et l'extrait qu'elle introduit, ni dans un extrait.
- `id` de l'œuvre **différent de tous les id d'extraits** du chapitre ; pas de prop `lien`.
- Les insérer **dans le gabarit** puis `generer.py`, ou dans le MDX puis
  `python3 scripts/ecrivains/gabarit.py <slug>` (sinon une régénération les efface). Contrôler
  ensuite que `generer.py <slug> --sortie /tmp/x.mdx` redonne le MDX à l'identique, puis
  `npm run verifier:ecrivains` (les œuvres n'y entrent pas) et `npm run build`.
- « Lire l'image » ne renvoie à un texte voisin que s'il a le même statut témoin / postérieur
  que l'œuvre (sinon l'un des deux peut être masqué par le filtre).

---

## 9. Procédure pour un nouveau chapitre

Les chapitres du XIXe sont rangés sous `xixe/` (spec 18) et paraissent à `/xixe/ecrivains/<slug>/` ;
pour un autre siècle, remplacer `xixe` par son identifiant et passer `--siecle <id>` aux scripts.

1. **Spec** : écrire `docs/specs/NN-ecrivains-<slug>.md` (numéro suivant), qui renvoie à cette
   charte et ne fixe que ce qui est propre au chapitre : bornes, parties prévues, épisodes à
   couvrir, pistes d'extraits, sensibilités à représenter, exceptions accordées.
2. **Repérage** : `chercher.py` et `voir.py` pour trouver les pages Wikisource ; choisir au moins
   20 extraits, environ deux tiers contemporains, en équilibrant camps et genres. Écarter tout
   texte absent de Wikisource.
3. **Spécification JSON** : `scripts/ecrivains/chapitres/xixe/<slug>.json` (page, segments, passage
   clé). Contrôler avec `python3 scripts/ecrivains/extraits.py <slug>` : textes de 400 à 900
   mots, passages clés de 150 à 350. Lire chaque extrait (`extraits.py <slug> <id>`).
4. **Auteurs** : ajouter les nouveaux dans `auteurs.ts`, compléter `oeuvres` des autres.
5. **Gabarit** : `scripts/ecrivains/chapitres/xixe/<slug>.gabarit.mdx` (frontmatter, introduction,
   parties, extraits sur le modèle du § 6, transitions, conclusion). Mettre `fiche` à la
   première apparition de chaque auteur, `faits` et `regard` partout.
6. **Génération** : `python3 scripts/ecrivains/generer.py <slug>` (corriger marqueurs, ancres ou
   ordre des notes jusqu'à ce qu'il passe).
7. **Vérification** : `npm run verifier:ecrivains` ; tous les extraits « ok », y compris ceux des
   chapitres existants.
8. **Build** : `npm run build` sans erreur ni avertissement `[Extrait …]` ou `[<slug>]`
   (année des faits manquante, rubrique manquante, fiche absente ou répétée).
9. **Durée** : calculer `dureeLecture` (§ 3), regénérer.
10. **Test navigateur** sur le build (`npx astro preview`, ou un serveur statique sur `dist/`) :
    - la page s'affiche, le sommaire liste les parties et les extraits ; sur un écran d'au moins
      1200 px il est fixe à gauche et suit la lecture ;
    - « Voir plus » / « Voir moins » sur quelques extraits ; les blocs repliés s'ouvrent ; un appel
      de note ouvre les notes et y conduit ;
    - le filtre dans les trois modes : compteur juste, numérotation recalculée, parties vides
      masquées, durée qui change, **transitions lisibles** dans chaque mode ; ancre vers un
      extrait masqué → mode « Tous » ;
    - l'accueil de la section (chapitre plus grisé), l'index des auteurs et les liens
      précédent / suivant ;
    - à 390 px de large : pas de défilement horizontal, lecture confortable.
11. **Compte rendu** : nombre d'extraits (contemporains / rétrospectifs, témoins / postérieurs),
    genres et camps représentés, extraits écartés faute de source, faits non vérifiés.
    Ne pas committer : c'est l'utilisateur qui le fait.

### Checklist d'acceptation

- [ ] Spec du chapitre écrite, qui renvoie à la charte.
- [ ] Au moins 20 extraits, chronologiques, en 3 à 5 parties ; environ 2/3 contemporains.
- [ ] Auteurs tous morts après 1800 (ou exception accordée et consignée).
- [ ] Au moins 4 genres dont un de fiction ou de poésie ; au moins 3 sensibilités, aucune
      au-delà de la moitié.
- [ ] Chaque extrait : texte de 400 à 900 mots (poésie exceptée), passage clé de 150 à 350 mots
      sans `[…]`, `regard`, `faits`, `reference`, `date`, lien vers la page précise, chapeau
      commençant par l'étiquette et l'écart, regard critique, notes si utiles.
- [ ] `fiche` à la première apparition de chaque auteur, et là seulement.
- [ ] Nouveaux auteurs dans `auteurs.ts`, `oeuvres` complétées.
- [ ] Introduction et conclusion d'un paragraphe ; transitions neutres, lisibles dans les 3 modes.
- [ ] `dureeLecture` cohérente (~150 mots/min, arrondi à 5).
- [ ] `npm run verifier:ecrivains` : tous les extraits « ok ».
- [ ] `npm run build` : sans erreur ni avertissement sur le chapitre.
- [ ] Test navigateur fait (ordinateur et 390 px), filtre testé dans les trois modes.
- [ ] Aucune couleur ajoutée ; aucun fichier partagé modifié sans nécessité.
- [ ] Faits de l'appareil non vérifiés listés dans le compte rendu ; rien de commité.
