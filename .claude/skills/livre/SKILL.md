---
name: livre
description: |
  Reprend la méthode d'un « livre » (charte docs/specs/23-charte-livres.md) à l'étape où elle en
  est : cabinet des lentilles, séminaire sur pièces, débat contradicteur, lecture du corpus,
  hypothèses et pré-enquête, plan et écriture. Utiliser avec « /livre <slug> » (ex. /livre
  sand-et-chopin), ou quand on demande « reprends le livre », « lance le cabinet des lentilles »,
  « continue le séminaire ». Option : « /livre <slug> étape N » pour forcer une étape.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Artifact
---

# /livre <slug> [étape N]

Tu reprends la méthode d'un livre du site « Histoire de France » avec l'utilisateur. Le slug est
le premier argument (par défaut, le seul livre de `docs/livres/`). Tout se passe en français.

## 1. Se mettre au courant (sans rien demander)

Lis dans cet ordre, en entier :

1. `docs/specs/23-charte-livres.md` : la charte (méthode en six étapes, format, exactitude).
2. `docs/specs/NN-livre-<slug>.md` : la spec du livre (corpus repéré, lentilles et pièces
   candidates, sons, état).
3. `docs/livres/<slug>/` : la trace de la méthode. L'étape en cours se déduit des fichiers :
   - rien → **étape 0** (cabinet des lentilles) ;
   - `lentilles.md` sans ligne « Retenues : » → étape 0 en cours ;
   - lentilles retenues, moins de 10 fichiers dans `pieces/` ou `questions.md` absent → **étape 1**
     (séminaire sur pièces) ;
   - `questions.md` avec des questions sans verdict → **étape 2** (débat contradicteur) ;
   - verdicts rendus, `lecture/` incomplet par rapport au noyau de la spec → **étape 3**
     (lecture du corpus) ;
   - `hypotheses.md` absent, ou présent sans choix de l'utilisateur, ou `pre-enquete-*.md`
     sans décision → **étape 4** ;
   - hypothèse choisie, `plan.md` absent ou chapitres non tous validés → **étape 5** ;
   - tous les chapitres validés → **étape 6**.
   Un fichier `etat.md` à la racine du dossier, s'il existe, prévaut : il dit l'étape, ce qui est
   fait, ce qui reste, et les décisions prises. Un argument « étape N » prévaut sur tout.
4. `docs/journal/livres/<slug>.jsonl` s'il existe (dernières entrées).

Dis en deux lignes où en est le livre et ce que tu vas faire, puis commence.

## 2. Mener l'étape

Règles valables à toutes les étapes :

- **Une question à la fois** (AskUserQuestion), jamais en rafale ; proposer des options, dont
  une recommandée en premier avec « (Recommended) », et accepter les réponses libres.
- **Ne jamais proposer d'angle, de thèse ni de plan** en dehors de l'étape qui le prévoit (4 et
  5). Si l'utilisateur en demande un avant, rappeler l'étape où il viendra et continuer.
- **Pièces et citations mot pour mot**, avec leur référence précise et leur URL ; rien de
  mémoire. Vérifier chaque citation à sa source avant de la présenter.
- **Consigner** chaque décision de l'utilisateur et sa raison dans le fichier de l'étape, au fil
  de la séance, pas à la fin. Mettre à jour `docs/livres/<slug>/etat.md` à chaque pas franchi.
- Noter début, fin, problèmes et idées avec
  `python3 scripts/journal/noter.py --siecle livres <slug> <debut|fin|note|probleme|idee> <etape> "…"`
  (écrit dans `docs/journal/livres/<slug>.jsonl`).
- Les sous-agents de lecture et d'écriture utilisent le modèle Opus et reçoivent la charte, la
  spec et les fichiers de l'étape. Les choix restent à l'utilisateur.
- Ne pas committer.

### Étape 0 — Cabinet des lentilles

Partir de la liste de la spec. Présenter **une lentille par question**, au gabarit de la charte
(nom et auteurs, ce qu'elle rend visible sur un exemple concret du corpus, usage classique,
risque) ; options : garder, écarter, garder en réserve. Après 8 à 10 lentilles, demander les 3 ou 4
retenues si plus de 4 ont été gardées. Écrire `lentilles.md` (toutes, retenues, raisons).

### Étape 1 — Séminaire sur pièces

Choisir les pièces dans la spec et le corpus, les **vérifier à la source** (texte recopié depuis
Wikisource, Gutenberg, Gallica ou Archive ; image depuis Commons avec sa licence). Les pièces
visuelles et sonores sont montrées dans une page privée (outil Artifact, page simple, sobre) ou
sur le site en local. Une pièce par question : la pièce (ou son lien), sa référence, ce qu'une
lentille retenue y voit en trois à six phrases, puis « Qu'est-ce qui t'intrigue ou te résiste
ici ? » (réponse libre). Reformuler la réaction en une ou plusieurs questions et les soumettre
pour accord. Fichiers : `pieces/NN-<id>.md`, `questions.md` (numéro, question, pièce, lentille,
formulation initiale, reformulation, état).

### Étape 2 — Débat contradicteur

Une question par appel : plaider **contre** (déjà tranchée ? intestable avec les sources libres ?
triviale ? mal posée ?) puis **pour**, pièces à l'appui, vérification historiographique rapide
admise ; options : garder, reformuler, fusionner, abandonner. Verdict et raison dans `questions.md`.

### Étape 3 — Lecture du corpus

Confirmer avec l'utilisateur la liste des sources du noyau et du deuxième cercle (une question).
Lancer les sous-agents Opus (une source ou un tome par agent, en parallèle, chacun écrivant son
`lecture/<source>.md` : grille des questions avec citations et références, relevé libre, pistes
de pièces). Vérifier que les citations sont recopiées, pas inventées (sondage par script ou
par relecture à la source). Bilan dans `docs/journal/livres/<slug>-lecture-bilan.md`.

### Étape 4 — Hypothèses et pré-enquête

Rédiger 6 à 8 hypothèses au gabarit de la charte dans `hypotheses.md`, à partir des dossiers de
lecture et des questions. Les présenter une par une ; l'utilisateur en retient une ou deux.
Sous-agent de pré-enquête par hypothèse → `pre-enquete-<n>.md` (pièces pour et contre, verdict
provisoire tient / vacille / réfutée). Présenter les verdicts, l'utilisateur choisit l'hypothèse
du livre ; la noter dans `etat.md` et dans la spec du livre.

### Étape 5 — Plan et écriture

Proposer le plan (`plan.md`) et le faire valider ; puis un chapitre à la fois : écriture (Opus),
vérification des faits, `scripts/livres/verifier.py` (à créer au premier chapitre si absent),
lecture contradictoire par un second agent (`contradictions/<nn>.md`), corrections, validation de
l'utilisateur. Le code du format (section « Livres », mises en page, composants, schéma) se crée
au premier chapitre, par un sous-agent Opus, selon la charte § 2 et § 5, en réutilisant
l'existant (`Oeuvre.astro`, `Chapitre.astro`, registre de musique, `adresses.ts`).

### Étape 6 — Appareil, build, compte rendu

Cahier des pièces, chronologie, bibliographie, cahier d'écoute, `npm run build`, test navigateur
(grand écran et 390 px), compte rendu dans `docs/journal/livres/<slug>-bilan.md`.

## 3. Finir une séance

À tout moment, si l'utilisateur arrête, écrire `etat.md` (étape, fait, reste, décisions), noter
la fin dans le journal, et dire en trois lignes où reprendre : « /livre <slug> ».
