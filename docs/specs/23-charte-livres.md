# Spec 23 — Charte des « livres » : enquêtes lettrées illustrées

Décidée le 2026-10-20 par questions une par une. Cette charte fixe la **méthode** (comment on
trouve ce qu'un livre va démontrer) et le **format** (comment il se lit). Elle vaut pour tous les
livres ; chaque livre a ensuite sa propre spec (`docs/specs/NN-livre-<slug>.md`), qui renvoie ici
et ne fixe que ce qui lui est propre. Premier livre : George Sand et Frédéric Chopin (spec 24).

Sujets envisagés dès le départ, qui ont servi à éprouver la charte (§ 10) : industrie, technique
et science du XVIe au XIXe siècle ; le désir d'inversion des rôles du XVIe au XIXe ; histoire
sociale des conditions de vie au XIXe ; George Sand et Chopin.

---

## 1. Objet

Un **livre** est un texte continu d'environ **trois heures de lecture** (30 000 à 35 000 mots),
accompagné de 80 à 110 **documents d'époque** et, quand le sujet s'y prête, de pièces sonores.
Il ne raconte pas : il **instruit une hypothèse** choisie avec l'utilisateur, la soumet aux sources
et conclut qu'elle tient, qu'elle vacille ou qu'elle est réfutée. Le lecteur doit pouvoir juger de
la preuve.

Trois ruptures avec le reste du site, propres à ce format et à lui seul :

- **Niveau** : universitaire ou lettré, pas lycée. Aucune simplification ; mais chaque notion
  technique est définie à sa première occurrence, et le texte reste une prose, pas un appareil.
- **Couleur** : les documents s'affichent **en couleur dans la page** (le site est monochrome
  partout ailleurs ; les chapitres écrivains grisent leurs œuvres, spec 11). Le reste du design
  ne change pas : serif, filets, petites capitales, pas de fond coloré.
- **Thèse** : le livre défend une idée précise, et peut conclure par sa réfutation.

Ce qui ne change pas : français soigné et typographie française, dates et noms exacts, citations
mot pour mot vérifiées par script, rien de commité par les agents.

---

## 2. Place dans le site

- Nouvelle section **« Livres »** du siècle, après « Images » dans la navigation : valeur `livres`
  du type `Section` de `src/data/siecles.ts`. Un siècle l'a dès qu'un livre le déclare.
- Un livre déclare un **siècle principal** (son adresse : `/<siecle>/livres/<slug>/`) et des
  **siècles associés** : il est listé dans la section « Livres » de chacun des siècles déclarés
  qui existent dans le registre, avec la même adresse (une seule page, pas de doublon). Un livre
  sur quatre siècles paraît donc dans quatre sections quand ces siècles existeront.
- Adresses : `urlLivres(siecle)`, `urlLivre(siecle, slug)`, `urlChapitreLivre(siecle, slug, n)`
  dans `src/utils/adresses.ts`, jamais écrites à la main.
- Chaque siècle qui a des livres les présente sur son accueil (bloc après les leçons, comme
  « Écrivains » et « Images »), avec le niveau annoncé en une ligne : « Enquêtes de niveau
  universitaire, illustrées. »

---

## 3. La méthode, en six étapes

La méthode précède l'écriture. Elle se mène **en séance avec l'utilisateur, une question à la
fois** (AskUserQuestion, jamais en rafale), et laisse une trace écrite à chaque étape dans
`docs/livres/<slug>/`. Les sous-agents (modèle Opus) lisent et rédigent ; les choix sont de
l'utilisateur.

### Étape 0 — Cabinet des lentilles

Avant toute pièce, proposer **8 à 10 cadres théoriques** candidats, un par un. Gabarit d'une
lentille :

| Champ | Contenu |
| --- | --- |
| Nom | Le cadre et ses auteurs de référence (deux ou trois, avec l'ouvrage) |
| Ce qu'elle rend visible | Sur **un exemple concret du sujet** (une lettre, une œuvre, un chiffre), ce que cette lentille y fait voir qu'on ne verrait pas sans elle |
| Usage classique | Un travail connu qui l'a appliquée à un objet voisin |
| Risque | Anachronisme, jargon, réduction, ce que la lentille ne sait pas voir |

L'utilisateur en garde **3 ou 4**. Fichier : `docs/livres/<slug>/lentilles.md` (toutes les
lentilles présentées, celles retenues, la raison).

### Étape 1 — Séminaire sur pièces

**10 à 15 pièces**, une à la fois, en autant de séances qu'il faut. Une pièce est un document
primaire de toute nature : lettre, page d'un livre, manuscrit, image, objet, partition, son,
tableau de chiffres. Elle est choisie pour sa **charge de tension** (contradiction, silence,
détail qui ne colle pas), toujours citée mot pour mot avec sa référence, jamais résumée de mémoire.

Chaque pièce arrive avec **ce qu'une des lentilles retenues y voit** (trois à six phrases) ; la
pièce peut à son tour mettre la lentille en défaut, et on le note. Puis une seule question :
« Qu'est-ce qui t'intrigue ou te résiste ici ? » La réaction est reformulée en une ou plusieurs
questions, soumises à l'utilisateur pour accord.

Les pièces visuelles et sonores ne se voient pas dans le terminal : les présenter dans une page
privée (artefact) ou sur le site en local, le texte de la pièce restant dans la séance.

Fichiers : `docs/livres/<slug>/pieces/NN-<id>.md` (la pièce, sa référence, la lecture par la
lentille, la réaction) et `docs/livres/<slug>/questions.md` (gabarit : numéro, question, pièce
d'origine, lentille, formulation initiale de l'utilisateur, reformulation, état).

### Étape 2 — Débat contradicteur

Une question à la fois. Je plaide **contre** (déjà tranchée par les spécialistes ? intestable
avec les sources libres ? triviale ? mal posée ?) puis **pour**, pièces à l'appui. L'utilisateur
décide : garder, reformuler, fusionner, abandonner. Le verdict et sa raison vont dans
`questions.md`. Une vérification historiographique rapide (recensions, articles en ligne,
tables des biographies) est admise ici pour étayer le « contre » ; elle ne remplace pas la
lecture des sources.

### Étape 3 — Lecture du corpus

**Corpus en cercles concentriques**, défini par une règle indépendante du sujet :

| Cercle | Définition | Lecture |
| --- | --- | --- |
| Noyau | Sources **produites par les acteurs mêmes** du sujet (ce qu'ils ont écrit, composé, fabriqué, mesuré) | En entier |
| Deuxième | Ce que les **contemporains** en ont dit (témoins, correspondants, critiques, rapports) | Ciblée, guidée par les questions |
| Troisième | **Contexte** : presse, actes administratifs, statistiques, cartes, prix | Sur demande, pour arbitrer |

Sources **libres et vérifiables** seulement : Wikisource, Projet Gutenberg, Gallica, Internet
Archive, Commons, bibliothèques numériques publiques. Une source qu'on ne peut pas relire en ligne
n'entre pas au corpus (elle peut figurer en bibliographie).

**Protocole à double entrée.** Chaque source est lue (par un sous-agent Opus, une source ou un
tome par agent) :

1. avec la **grille** des questions retenues : pour chaque question, ce que la source répond,
   citation exacte et référence (édition, tome, page, lettre, URL précise) ;
2. en **relevé libre** : contradictions entre sources, silences, dates qui ne collent pas, mots
   récurrents, détails matériels, tout ce qui résiste.

Dossier par source : `docs/livres/<slug>/lecture/<source>.md` (en-tête : édition, URL, cercle,
agent, date ; puis grille, relevé libre, pistes de pièces à montrer). Toute citation est
recopiée par script ou par copier-coller depuis la source, jamais de mémoire, et sera contrôlée
par `scripts/livres/verifier.py` (§ 7).

### Étape 4 — Hypothèses et pré-enquête

À partir des dossiers de lecture et des questions, rédiger **6 à 8 hypothèses**
(`docs/livres/<slug>/hypotheses.md`). Gabarit :

| Champ | Contenu |
| --- | --- |
| Énoncé | Une phrase affirmative, testable |
| Ce qui la confirmerait / la réfuterait | Les observations attendues dans chaque cas |
| Sources à lire | Dans le corpus, avec les tomes ou lettres |
| Documents montrables | Pièces d'époque qui la porteraient |
| Ce qu'elle ajoute | Position par rapport aux travaux existants (vérification historiographique rapide) |
| Lentilles | Celles qui l'instruiraient |

L'utilisateur en retient **une ou deux**. Un sous-agent mène une **pré-enquête** par hypothèse
(`docs/livres/<slug>/pre-enquete-<n>.md`) : relecture ciblée du corpus, pièces pour et contre,
verdict provisoire **tient / vacille / réfutée**, et ce qu'il faudrait pour trancher. L'utilisateur
choisit l'hypothèse du livre. Une hypothèse réfutée peut rester celle du livre, si la réfutation
vaut d'être écrite.

### Étape 5 — Plan et écriture

Plan de 10 à 12 chapitres, validé par l'utilisateur (ordre chronologique ou par pièces, selon
l'hypothèse ; durée visée par chapitre ; pièces et sons prévus). Puis **un chapitre à la fois** :

1. écriture par un sous-agent Opus muni de l'hypothèse, du plan, des dossiers de lecture et de
   la charte ;
2. vérification des faits datés (chaque date, nom, chiffre sourcé en note ou formulé avec
   prudence) ;
3. `scripts/livres/verifier.py` : toutes les citations « ok » ;
4. **lecture contradictoire** par un second agent : le chapitre prouve-t-il ce qu'il avance ?
   que cache-t-il ? rapport écrit, corrections ;
5. validation par l'utilisateur. Le chapitre suivant ne commence qu'après.

Voix **impersonnelle** : ni « je » ni « nous », pas d'adresse au lecteur, pas de question
rhétorique ; des phrases pleines, des pièces citées longuement, chaque terme technique défini.
L'avant-dernier ou le dernier chapitre est l'**état de la preuve** : ce qui est établi, probable,
réfuté, et ce que les sources ne permettent pas de dire.

### Étape 6 — Appareil, build, compte rendu

Cahier des pièces, chronologie, bibliographie, cahier d'écoute (§ 5), `npm run build`, test
navigateur, compte rendu (pièces écartées faute de source libre, faits non vérifiés). Ne pas
committer.

---

## 4. Journal et trace

Chaque étape laisse ses fichiers dans `docs/livres/<slug>/` ; les décisions de l'utilisateur y
sont consignées avec leur raison. Les agents notent début, fin, problèmes et idées avec
`scripts/journal/noter.py --siecle livres <slug> …` dans `docs/journal/livres/<slug>.jsonl`, et un bilan est écrit à la fin
de chaque étape longue (lecture, écriture), comme pour les diaporamas.

---

## 5. Format du livre

### Pages

- **Couverture** (`/<siecle>/livres/<slug>/`) : titre, sous-titre, argument (l'hypothèse en
  dix lignes et ce que le livre conclut), sommaire avec durée par chapitre, durée totale,
  siècles couverts, méthode en un paragraphe (corpus, lentilles, vérification), accès au cahier
  des pièces, à la chronologie, à la bibliographie et au cahier d'écoute.
- **Chapitres** (`/<siecle>/livres/<slug>/<nn>-<chapitre>/`) : 10 à 12, de 15 à 20 minutes
  chacun (2 500 à 3 500 mots), précédent / suivant, rappel du sommaire. Pas de filtre
  témoin / postérieur : un livre n'est pas une anthologie.
- **Appareil** (pages de fin) : cahier des pièces (chaque document et chaque extrait cité, avec
  provenance et lien), chronologie, bibliographie commentée (sources, puis études), cahier
  d'écoute, état de la preuve si ce n'est pas un chapitre.

### Notes

Chaque citation et chaque fait daté renvoie à une **note en marge** (sur grand écran, dans la
marge droite au niveau de l'appel ; sous 1 000 px, dépliable sous le paragraphe). Une note donne
la référence précise : auteur, œuvre, édition, tome, page ou numéro de lettre, lien vers le texte
libre. Les notes sont numérotées par chapitre.

### Documents

- **Seulement des pièces authentiques** : portraits, manuscrits, lettres, partitions, éditions
  originales, lieux, objets, presse, tableaux de chiffres d'époque. Pas de figure dessinée, pas
  d'image générée, pas de carte moderne (une carte d'époque est un document).
- **En couleur dans la page**, à la largeur du texte ou en pleine largeur pour les grandes
  pièces ; un clic ouvre la pièce en grand (visionneuse plein écran, comme `Oeuvre.astro`).
- **Densité** : une pièce pour 300 à 400 mots, soit 80 à 110 pièces pour un livre.
- **Légende savante** : créateur, titre, date, technique, lieu de conservation, provenance
  (Commons, Gallica, bibliothèque), et deux ou trois phrases sur ce que la pièce montre et ce
  qu'elle fait à l'hypothèse. Toute pièce est un document cité : elle figure au cahier des
  pièces avec son identifiant (`P-nn`).
- Fichiers : `src/assets/livres/<slug>/`, servis optimisés par Astro ; licence et source notées
  dans `src/data/livres/<slug>/pieces.json`.

### Sons

Quand le sujet a une musique ou un son d'époque : **lecteur discret au fil du texte**, à
l'endroit même où l'œuvre est discutée (extrait ou intégrale, interprète crédité, licence
vérifiée), avec en regard une page de l'édition originale ou du manuscrit. Les enregistrements
viennent du registre de musique des diaporamas (`src/data/diaporamas/<siecle>/commun/registre-musique.json`),
étendu au besoin. Un **cahier d'écoute** en fin de livre récapitule les œuvres dans l'ordre du
texte, avec les renvois aux chapitres.

### Composants (à créer au premier livre, réutilisés ensuite)

Mise en page `Livre.astro` (couverture) et `ChapitreLivre.astro` ; composants `Piece.astro`
(document en couleur, légende savante, visionneuse), `Note.astro` (note en marge), `Ecoute.astro`
(lecteur et partition), `CahierPieces.astro`, `Chronologie` réutilisable. Contenu en MDX dans
`src/content/livres/<slug>/` (`00-couverture.mdx`, `NN-<chapitre>.mdx`, `annexes/*.mdx`),
schéma dans `content.config.ts` (titre, sous-titre, siècle principal, siècles, hypothèse, état,
durée, ordre). Registre des livres : `src/data/livres.ts`.

---

## 6. Style

- Prose d'étude : phrases complètes, paragraphes de 80 à 200 mots, pas de liste à puces dans le
  corps du texte, pas de gras. Les pièces sont citées longuement (jusqu'à 300 mots d'un coup)
  et commentées après, jamais paraphrasées entre guillemets.
- Le texte dit toujours **d'où il tient ce qu'il affirme** ; un fait sans source est formulé
  comme une conjecture.
- Pas de psychologie gratuite : une lentille théorique s'applique explicitement, avec ses
  limites, ou pas du tout.
- Typographie française (espaces insécables, guillemets « »), accents partout, titres d'œuvres
  en italique, dates en toutes lettres pour les mois.

---

## 7. Exactitude

- **Citations** : mot pour mot, orthographe et ponctuation de l'édition conservées, coupures
  signalées par `[…]`. Chaque citation porte en note son édition et son lien.
- **Vérification par script** : `scripts/livres/verifier.py <slug>` télécharge à neuf chaque
  source citée (Wikisource, Gutenberg, Internet Archive en texte brut, Gallica en mode texte
  quand il existe) et contrôle que chaque citation y figure mot pour mot. Les sources et leurs
  URL sont déclarées dans `src/data/livres/<slug>/sources.json`. Tout doit être « ok » avant la
  validation d'un chapitre. Une citation introuvable en ligne n'est pas publiée.
- **Faits** : dates, noms, chiffres exacts et sourcés ; en cas de doute, formulation prudente et
  mention dans le compte rendu.
- **Traductions** : une citation traduite (lettres polonaises de Chopin, par exemple) indique le
  traducteur et l'édition ; si la traduction n'est pas libre de droits, citer court (moins de
  50 mots) et renvoyer à l'original.
- **Droits** : documents et enregistrements libres (domaine public, CC0, CC BY) ; la licence est
  notée pièce par pièce. Une édition récente d'un texte ancien peut être protégée (appareil,
  traduction) : citer alors l'édition ancienne libre.

---

## 8. Organisation des fichiers

```
docs/specs/23-charte-livres.md             # cette charte
docs/specs/NN-livre-<slug>.md              # spec d'un livre
docs/livres/<slug>/                        # trace de la méthode
  lentilles.md  pieces/NN-<id>.md  questions.md  lecture/<source>.md
  hypotheses.md  pre-enquete-<n>.md  plan.md  contradictions/<nn>.md
docs/journal/livres/<slug>.jsonl, -bilan.md
src/data/livres.ts                         # registre (slug, titre, siècle principal, siècles, état)
src/data/livres/<slug>/sources.json        # sources citées et leurs URL (vérificateur)
src/data/livres/<slug>/pieces.json         # pièces : fichier, légende, provenance, licence
src/content/livres/<slug>/*.mdx            # couverture, chapitres, annexes
src/assets/livres/<slug>/                  # images des pièces
scripts/livres/                            # verifier.py, pieces.py (téléchargement et légendes)
```

---

## 9. Procédure pour un nouveau livre

1. **Spec** : `docs/specs/NN-livre-<slug>.md`, qui renvoie à cette charte : sujet, bornes,
   siècle principal et siècles associés, corpus pressenti par cercle avec les sources libres
   repérées, lentilles candidates, pièces candidates pour le séminaire, sons disponibles.
2. **Étapes 0 à 4** en séance, une question à la fois, fichiers dans `docs/livres/<slug>/`.
3. **Plan** validé (étape 5), puis chapitres un par un, chacun vérifié, contredit et validé.
4. **Appareil et build** (étape 6), test navigateur (grand écran et 390 px : notes en marge et
   dépliées, visionneuse, lecteur audio, sommaire), compte rendu. Pas de commit.

### Checklist d'acceptation

- [ ] Spec du livre écrite, qui renvoie à la charte ; siècles déclarés.
- [ ] Lentilles retenues, pièces du séminaire, questions et verdicts du débat consignés.
- [ ] Dossiers de lecture pour tout le noyau et les sources ciblées du deuxième cercle.
- [ ] Hypothèses rédigées au gabarit, pré-enquête(s) menée(s), hypothèse du livre choisie
      par l'utilisateur.
- [ ] 10 à 12 chapitres de 15 à 20 minutes, voix impersonnelle, chacun validé après vérification
      des faits, script des citations et lecture contradictoire.
- [ ] 80 à 110 pièces authentiques en couleur, légendées, au cahier des pièces avec licence.
- [ ] Sons au fil du texte quand le sujet s'y prête, cahier d'écoute, licences vérifiées.
- [ ] Notes en marge sur chaque citation et fait daté ; chronologie ; bibliographie commentée ;
      état de la preuve.
- [ ] `scripts/livres/verifier.py <slug>` : tout « ok » ; `npm run build` sans erreur.
- [ ] Test navigateur fait ; aucune couleur ajoutée hors des pièces ; rien de commité.

---

## 10. Tableau d'épreuve : la méthode sur les quatre sujets

Chaque ligne instancie une étape sur les quatre sujets envisagés. Les hypothèses données pour les
trois sujets non engagés sont de simples illustrations de forme ; pour Sand et Chopin, l'hypothèse
sort de la méthode, pas de ce tableau.

| Étape | Sand et Chopin (1836-1849) | Industrie, technique, science (XVIe-XIXe) | Désir d'inversion des rôles (XVIe-XIXe) | Conditions de vie (XIXe) |
| --- | --- | --- | --- | --- |
| Siècles | xixe | xvie, xviie, xviiie, xixe (principal à choisir) | xvie à xixe | xixe |
| Noyau du corpus | Lettres, mémoires, romans de Sand ; lettres et œuvres de Chopin | Traités, planches de l'Encyclopédie, mémoires d'académies, brevets, livres de comptes de manufactures | Pièces de théâtre, estampes du « monde renversé », chansons, procès, récits de carnaval, romans à travestissement | Enquêtes (Villermé, Buret, Le Play), budgets ouvriers, mémoires d'ouvriers (Nadaud, Perdiguier, Truquin), règlements d'atelier |
| Deuxième cercle | Delacroix, Liszt, Marie d'Agoult, Balzac, Heine, Viardot, Fontana, Grzymała | Voyageurs, inspecteurs des manufactures, correspondances savantes, rapports d'exposition | Prédicateurs, moralistes, police, critiques dramatiques | Médecins, prêtres, juges, romanciers, presse ouvrière |
| Troisième cercle | Revue et gazette musicale, Revue des deux mondes, presse de 1848 | Prix, tarifs douaniers, statistiques de production, cartes | Almanachs, images d'Épinal, registres de censure | Statistique générale de la France, prix du pain, recensements, plans de villes |
| Pièces du séminaire | Une lettre, une page de Majorque, un manuscrit de partition, un portrait, une œuvre à écouter | Une planche de machine, une page de traité, un brevet, un tableau de prix, un objet de musée | Une estampe du monde à l'envers, une scène de Marivaux, une chanson, un procès | Un budget de famille, une page d'enquête, une photographie de logement, un règlement, un menu |
| Lentilles candidates | Psychanalyse, affects spinozistes, sociologie de l'art, critique génétique, histoire des émotions, études de genre, musicologie, histoire de la maladie | Histoire des techniques (Gille, Daumas), Kuhn, Latour, « savoir utile » (Mokyr), Simondon, histoire économique | Bakhtine, Natalie Zemon Davis, Foucault, Butler, anthropologie du rite (Turner), histoire des représentations | Marx, E. P. Thompson, histoire sociale (Perrot, Noiriel), Bourdieu, anthropologie de l'alimentation, histoire de la santé |
| Hypothèse (forme) | À déterminer par la méthode | « Jusqu'en 1850, la technique précède la science plus qu'elle ne la suit » | « L'inversion mise en scène renforce l'ordre plus qu'elle ne le menace » | « Le niveau de vie ouvrier baisse de 1830 à 1850 avant de remonter » |
| Sons | Chopin (Musopen, registre existant) | Aucun, ou sons de machines reconstitués (hors charte : pas de son généré) | Chansons d'époque enregistrées librement | Chansons ouvrières, sinon aucun |
| Ce qui change | Rien | Siècle principal à choisir ; corpus en plusieurs langues (latin, anglais) : traductions libres à trouver | Corpus visuel dominant : densité de pièces plus forte admise | Chiffres : les tableaux d'époque sont des pièces, pas des figures |

Conclusion de l'épreuve : la charte tient sans règle spéciale, à deux ajustements près, inscrits
ci-dessus : le **siècle principal** d'un livre pluriséculaire est un choix de sa spec, et les
**tableaux de chiffres d'époque** comptent comme pièces (un tableau recomposé serait une figure,
exclue). Les sons sont facultatifs par nature.
