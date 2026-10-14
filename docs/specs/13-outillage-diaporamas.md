# Spec 13 — Outillage des diaporamas avant la période 03

Rédigée le 2026-10-10, à partir du bilan de la période 02
(`docs/journal/xixe/diaporama-02-consulat-empire-bilan.md`, « Pistes » 4 et 6, et l'idée « YuNet » du
journal `outillage-python.jsonl`). Trois outils à construire **avant** de produire la Restauration.
Ils servent la chaîne de la spec 12 (`scripts/diaporamas/`) ; aucune page du site ne change.

## But

Produire la période 03 plus vite et pour moins cher :

1. ne plus refaire la recherche musicale de zéro à chaque période (≈ 35 min et ~25 appels
   perdus pour la période 02) ;
2. donner à chaque agent (A, B, C) une vérification courte, limitée à son étape, et ne plus
   tomber en panne de crédits Gemini au milieu d'une étape (deux fois en deux jours) ;
3. cadrer les visages des portraits du registre sans Gemini (gratuit, local, reproductible).

## Règles communes

- Python 3 de la machine, bibliothèque standard ; OpenCV seulement par le venv existant
  `.cache/venv-visages` (comme `visages_local.py`). Pas de nouvelle dépendance npm.
- Style des scripts existants : en-tête en docstring française (usage, format, décisions), sorties
  en français, courtes. Écritures de JSON par `commun.ecrire` (fusion sous verrou) ou, pour les
  nouveaux fichiers, écriture atomique de même style.
- Aucun appel Gemini payant pour construire et tester ces outils, sauf la sonde de l'outil 2
  (quelques jetons) ; `--budget 0.05` pour tout essai qui en ferait.
- Journal obligatoire : `python3 scripts/journal/noter.py outillage-03 debut|fin|probleme|idee
  <etape> "<texte>"`, commande seule (pas groupée avec la commande de travail).
- Rien ne doit changer dans les JSON des périodes 01 et 02 (contrôle : `git diff --stat
  src/data/` vide à la fin, hors registre nouveau) ; `python3 scripts/diaporamas/verifier.py
  --tous` donne les mêmes erreurs et avertissements qu'avant, et `npm run build` passe.
- Documenter chaque outil dans `scripts/diaporamas/README.md` (section propre, courte) et ajouter
  une ligne à la spec 12, « Produire une période : leçons de Consulat et Empire ».
- Ne pas committer : l'utilisateur relit d'abord.

## Outil 1 — Registre des enregistrements libres (`registre-musique.json`)

### Données

Fichier `src/data/diaporamas/xixe/commun/registre-musique.json` (commun aux 9 périodes, à côté
d'`indicatif.json`). Une entrée par **enregistrement** vérifié, qu'il ait été retenu ou non :

```json
{
  "id": "archive:x.-0699-beckmans-o-richard-o-mon-roi#X.0699 Beckmans - O Richard o mon Roi.flac",
  "source": { "type": "archive", "id": "…", "fichier": "…", "publication": "1929" },
  "oeuvre": "Ô Richard, ô mon roi (Richard Cœur de Lion)",
  "compositeur": "André Grétry", "auteur_texte": "Michel-Jean Sedaine", "date_oeuvre": "1784",
  "interprete": "José Beckmans, baryton, avec orchestre", "enregistrement": "Pathé, vers 1929",
  "genre": "chant | instrumental",
  "licence": "Domaine public en Europe (78 tours publié avant 1963)",
  "preuve_date": "date de publication de l'item IA + étiquette Pathé X.0699 (vers 1929)",
  "duree": 182.4, "filtres": "78tours",
  "structure": [[36.3, 54.8, "refrain, « Ô Richard ! ô mon roi ! »"]],
  "periodes": ["01-revolution"], "statut": "retenu | possible | ecarte",
  "motif": "si écarté : pourquoi (licence ND, son trop abîmé, identification douteuse…)",
  "verifie": "2026-10-08"
}
```

- `id` : `<type>:<identifiant>#<fichier>` (Commons : `commons:File:…`), unique.
- `structure` : passages utiles connus (secondes, libellé) ; facultative.
- `statut` : `retenu` (utilisé par une période), `possible` (vérifié, pas encore utilisé),
  `ecarte` (avec `motif` : on ne le recherche plus). Les œuvres cherchées **sans** enregistrement
  libre trouvé vont dans une liste à part, `introuvables` : `[{ "oeuvre", "compositeur",
  "cherche": "2026-10-08", "ou": "Commons, IA (requêtes…)" }]` (période 02 : Cherubini, *Les Deux
  Journées* et *Anacréon* ; Méhul, *Joseph*, ouverture ; etc. — relevé dans
  `docs/journal/xixe/diaporama-02-consulat-empire.jsonl`, entrée 35).

### Script `scripts/diaporamas/registre_musique.py`

- `--amorcer` : remplit le registre depuis le bloc `musique` (fonds et intermèdes) des JSON des
  périodes existantes (statut `retenu`, `periodes` renseigné, champs repris tels quels ; durée lue
  dans le cache `.cache/diaporamas/musique/sources/` si présent) et depuis les recherches
  infructueuses du journal 02 (`introuvables`, saisies à la main par l'agent qui construit
  l'outil, après lecture de l'entrée 35). Idempotent : relancé, il n'ajoute pas de doublon.
- `chercher <mots>` : recherche sans accents ni casse dans œuvre, compositeur, interprète ; une
  ligne par résultat (`statut`, œuvre, interprète, année, `id`), et les `introuvables` qui
  correspondent. C'est la première commande que l'agent B lance pour chaque piste proposée.
- `ajouter --depuis <slug>` : après `musique.py <slug>`, verse dans le registre les pistes de la
  période qui n'y sont pas encore (statut `retenu`) et met à jour `periodes` des autres.
- `ecarter <id> "<motif>"` et `introuvable "<œuvre>" "<compositeur>" "<où>"` : saisie rapide.
- `musique.py` n'est pas modifié dans sa logique ; il peut seulement afficher en fin de passe
  « n pistes absentes du registre : lancer registre_musique.py ajouter --depuis <slug> ».
- `verifier.py` (étape B) avertit si une piste de la période n'est pas au registre.

### Acceptation

- Après `--amorcer` : 17 + 14 entrées `retenu` au plus (moins s'il y a des réutilisations, comme
  les extraits de Georges Thill), toutes avec licence et `source` identiques aux JSON ; au moins
  6 `introuvables`.
- `registre_musique.py chercher thill` liste les enregistrements de Georges Thill avec les
  périodes qui les utilisent.
- Section README « Registre des enregistrements libres » ; la consigne de l'agent B (spec 12) dit
  de chercher dans le registre avant toute recherche Commons / Internet Archive.

## Outil 2 — `verifier.py --etape A|B|C` et solde Gemini

### Vérification par étape

`verifier.py <slug> --etape A|B|C` n'exécute et n'affiche que les contrôles de l'étape ; sans
`--etape`, comportement actuel inchangé (tout). Répartition (à ajuster si un contrôle dépend d'une
donnée produite plus tard : il passe alors à l'étape qui la produit) :

| Étape | Contrôles |
|---|---|
| **A** (texte, images, prévus) | structure (nombre de diapositives et d'actes, numérotation, actes et dates), narration (mots, phrases, parenthèses, abréviations), images (présence, licence, métadonnées, recadrage, titre court, réutilisation), dates (`controler_dates`), dosage des enrichissements **prévus**, richesse des épisodes, générique (`controler_generique`) |
| **B** (voix, zone utile, caméra, musique) | audio (présence, péremption, fidélité, horodatage, durées), `controler_ouverture`, `controler_utile`, `controler_camera`, `controler_musique`, `controler_segments`, `controler_boucles`, registre musical (outil 1) |
| **C** (surimpressions, vérification) | `controler_surimpressions`, `controler_portraits`, `controler_objets`, `controler_chiffres`, `controler_avant_apres_mosaiques`, vignettes coupées, puis **tout** (C est l'étape finale : `--etape C` = vérification complète, mais sortie résumée) |

Sortie : une ligne de bilan par famille (« images : 0 erreur, 2 avertissements »), puis les
erreurs, puis au plus 15 avertissements (`--tout` pour les voir tous). Code de retour 1 s'il y a
des erreurs de l'étape. Les contrôles hors ligne restent disponibles (`--hors-ligne`).

### Solde Gemini

L'API ne donne pas le solde des crédits prépayés : on le **tient soi-même** et on **sonde** avant
chaque étape payante.

- **Registre des dépenses** : `gemini.compter` ajoute chaque appel à
  `.cache/diaporamas/gemini-depenses.jsonl` (`ts`, script, tâche, modèle, jetons, dollars
  estimés). Écriture en ajout, sous verrou (appels parallèles).
- **Crédit déclaré** : `.cache/diaporamas/gemini-credit.json` `{ "credit": 10.0, "depuis":
  "<ts>" }`, posé par l'utilisateur quand il recharge (`gemini.py --crediter 10`). Solde estimé
  = crédit − dépenses depuis `depuis` (tarifs indicatifs : estimation, affichée comme telle).
- **`gemini.py --solde`** : affiche le solde estimé, la dépense des 7 derniers jours par script,
  et le résultat d'une **sonde** (un appel minimal au modèle flash, quelques jetons ; 402 ou
  `RESOURCE_EXHAUSTED` → « crédits épuisés », code de retour 2).
- **Avant chaque passe payante** (`voix.py`, `utile.py`, `camera.py`, `portraits.py`,
  `paroles.py`, `surimpressions.py` quand ils appellent Gemini) : sonde automatique au premier
  appel, et refus de démarrer si `--budget` dépasse le solde estimé (message : recharger, puis
  `gemini.py --crediter`). `--sans-sonde` pour les cas où l'on sait. La sonde est faite une fois
  par lancement, pas par appel.
- Un 402 en cours de route lève une erreur propre (comme `BudgetAtteint`) : le script écrit ce
  qui est fait et s'arrête, avec le même message.

### Acceptation

- `verifier.py consulat-empire --etape A` puis `B` puis `C` : la réunion de leurs erreurs et
  avertissements est égale à celle de `verifier.py consulat-empire` (test fourni sous
  forme de commande dans le README, ou petit script `scripts/diaporamas/tester_etapes.py`).
- Sortie de `--etape A` sur la période 02 : moins de 40 lignes.
- `gemini.py --solde` fonctionne sans crédit déclaré (affiche seulement dépenses et sonde).
- Un appel simulé renvoyant 402 (variable d'environnement de test, ex.
  `DIAPORAMAS_GEMINI_SIMULER=402`) fait s'arrêter proprement un script en écrivant son travail.

## Outil 3 — Cadre des visages du registre des portraits par YuNet

### Comportement

`portraits.py` calcule aujourd'hui `cadre_visage` (visage avec cheveux et menton, fractions de
l'original) par Gemini. Il passe au **détecteur local** :

- Appel de `visages_local.py` en **mode portrait** (`{"portrait": true, "chemins": [...]}`, déjà
  utilisé par `camera.py`) dans le venv `.cache/venv-visages`, par lots (un seul lancement pour
  tous les portraits à cadrer). La boîte rendue est déjà élargie « crâne-menton, oreille à
  oreille » ; ajouter la marge de cheveux attendue par `cadre_visage` si l'étalonnage montre
  qu'elle manque (comparer aux cadres Gemini existants, voir Acceptation).
- **Repli Gemini** seulement si YuNet ne trouve rien et que `--repli-gemini` est donné (avec
  `--budget`) ; sinon le portrait est signalé « visage non trouvé : cadre à poser à la main
  (`cadre_visage_manuel`) ».
- `cadre_visage_manuel: true` reste prioritaire ; le cache (`cle`) évite de recalculer.
- Le contrôle « à relire » existant (planche de vérification) est conservé : une planche des
  seuls portraits nouveaux ou douteux (score bas, boîte très petite ou très décentrée).
- Si le venv ou le modèle `yunet.onnx` manquent, message avec les deux commandes d'installation
  (celles de l'en-tête de `visages_local.py`) et arrêt.

### Acceptation

- Étalonnage sur les portraits déjà cadrés par Gemini des périodes 01 et 02 (registre
  `src/data/diaporamas/xixe/portraits.json`), **sans rien écrire** (`--essai`) : rapport du nombre de
  visages trouvés, de l'IoU médiane avec le cadre Gemini et des 10 plus gros écarts (planche).
  Objectif : visage trouvé pour ≥ 90 % des portraits, IoU médiane ≥ 0,7 ; sinon ajuster la
  marge, puis montrer la planche des écarts à l'utilisateur avant de basculer.
- Après bascule, les cadres existants ne sont pas recalculés (cache), sauf `--force`.
- 0 $ de Gemini pour une passe sans `--repli-gemini`.

## Ordre conseillé et découpage

Trois chantiers indépendants (fichiers distincts, sauf `verifier.py` touché par 1 et 2 : faire
l'outil 2 avant le contrôle « registre » de l'outil 1, ou les confier au même agent). Un agent
Opus peut tout faire à la suite (≈ 1 h) ; ou deux agents en parallèle : (2) puis la ligne
`verifier.py` de (1), et (3) + le reste de (1).

## Hors périmètre

Recherche Wikidata des lieux (`lieux.py --wikidata`), recadrage automatique des marges
d'estampes, un seul appel caméra par image : pistes du bilan, à traiter plus tard.
