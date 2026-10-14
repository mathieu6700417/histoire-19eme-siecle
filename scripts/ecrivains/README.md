# Scripts de la section « Le siècle raconté par ses écrivains »

Outils pour extraire les textes depuis Wikisource, assembler le MDX d'un chapitre et
vérifier les extraits publiés. Les règles éditoriales sont dans
`docs/specs/00-charte-chapitres-ecrivains.md` ; ce fichier ne décrit que les outils.

## Dépendances

Python 3.10 ou plus récent, **bibliothèque standard seulement** (aucun `pip install`).
Un accès réseau à `fr.wikisource.org` est nécessaire. Les commandes se lancent depuis la
racine du projet.

**Siècle (spec 18).** Spécifications et chapitres sont rangés par siècle :
`scripts/ecrivains/chapitres/<siecle>/` et `src/content/ecrivains/<siecle>/`. Chaque script
accepte `--siecle <id>` (défaut `xixe`, lu par `scripts/diaporamas/commun.py`) ; les chemins sont
calculés dans `wikisource.py` (`CHAPITRES`, `MDX`). Le chapitre paraît à `/<siecle>/ecrivains/<slug>/`.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `wikisource.py` | Bibliothèque commune : chemins du siècle, API `parse` de Wikisource, mise en texte, cache, URL publiques. |
| `chercher.py` | Recherche plein texte sur Wikisource, ou liste des sous-pages d'une œuvre. |
| `voir.py` | Affiche les paragraphes numérotés d'une page (pour choisir un extrait et ses marqueurs). |
| `extraits.py` | Extrait le texte de chaque extrait d'après la spécification JSON ; affiche les nombres de mots. |
| `generer.py` | Assemble le MDX du chapitre : gabarit + textes exacts + passage clé + appels de note + liens. |
| `gabarit.py` | Recrée le gabarit à partir du MDX publié (après des retouches faites directement dans le MDX). |
| `verifier.py` | Vérifie les MDX publiés contre les pages Wikisource (sans cache). |
| `chapitres/<siecle>/<slug>.json` | Spécification des extraits d'un chapitre (pages, segments, passage clé, ancres). |
| `chapitres/<siecle>/<slug>.gabarit.mdx` | Le chapitre rédigé, avec `@@T:id@@` (texte) et `@@L:id@@` (lien) à la place des textes. |

## Commandes

```sh
# Chercher une source
python3 scripts/ecrivains/chercher.py "Austerlitz soleil" 10
python3 scripts/ecrivains/chercher.py --sous-pages "Mémoires_d’outre-tombe"

# Lire une page en paragraphes numérotés (--vers : une ligne par vers)
python3 scripts/ecrivains/voir.py "Mémoires_d’outre-tombe/Première_partie/Livre_V"
python3 scripts/ecrivains/voir.py "Les_Châtiments/À_l’obéissance_passive" 0 80 --vers

# Contrôler les extraits d'un chapitre (mots du texte et du passage clé), ou en lire un
python3 scripts/ecrivains/extraits.py 01-revolution
python3 scripts/ecrivains/extraits.py 01-revolution bastille

# Générer le MDX (par défaut vers src/content/ecrivains/<siecle>/<slug>.mdx)
python3 scripts/ecrivains/generer.py 01-revolution
python3 scripts/ecrivains/generer.py 01-revolution --sortie /tmp/essai.mdx

# Resynchroniser le gabarit après une retouche faite dans le MDX
python3 scripts/ecrivains/gabarit.py 01-revolution

# Vérifier un chapitre, ou tous (code de sortie 1 en cas d'échec)
python3 scripts/ecrivains/verifier.py 01-revolution
npm run verifier:ecrivains
```

## Spécification JSON d'un chapitre

```json
{
  "slug": "02-empire",
  "gabarit": "02-empire.gabarit.mdx",
  "sortie": "src/content/ecrivains/xixe/02-empire.mdx",
  "ancres": { "id-extrait": { "mot de la note": "autre ancre dans le texte" } },
  "extraits": {
    "austerlitz": {
      "page": "Titre_exact/de/la/page",
      "segments": [
        { "debut": "premiers mots exacts du passage", "fin": "derniers mots exacts du passage." },
        "CUT",
        { "debut": "…", "fin": "…" }
      ],
      "cle": [2, 4]
    },
    "un-poeme": {
      "page": "Recueil/Poème",
      "poeme": { "debut": "Premier vers exact,", "fin": "Dernier vers exact.", "strophe": 6 },
      "cle": [0, 3]
    }
  }
}
```

- **`page`** : titre Wikisource (soulignés ou espaces, apostrophes typographiques comprises),
  tel que l'affichent `chercher.py` ou l'URL. Le lien publié est construit à partir de lui.
- **`segments`** : chaque segment va du marqueur `debut` jusqu'au marqueur `fin` inclus, sur
  un ou plusieurs paragraphes consécutifs ; il peut commencer ou finir au milieu d'un
  paragraphe. Copier les marqueurs depuis la sortie de `voir.py` (une soixantaine de
  caractères suffit ; ils doivent être uniques dans la page). `"CUT"` insère une coupure `[…]`
  dans un paragraphe à part.
- **`poeme`** : vers pris ligne à ligne du premier au dernier (inclus), regroupés en strophes de
  `strophe` vers (0 : une seule strophe). Le nombre de vers doit être divisible par `strophe`.
- **`cle`** : passage clé = paragraphes (ou strophes) `i` à `j` inclus, comptés à partir de 0
  dans la liste produite (les `[…]` comptent pour un paragraphe). Pas de `[…]` dans le passage
  clé ; 150 à 350 mots, sinon `generer.py` s'arrête.
- **`ancres`** : l'appel de note n est placé juste après la première occurrence du `mot` de la
  note n (apostrophe droite changée en ’), cherchée après l'appel précédent. Si le mot de la note
  n'apparaît pas tel quel dans le texte, donner ici l'ancre à utiliser.

**Leçon à extraits (hors de la section).** Une leçon peut citer des extraits avec le même
outillage (ex. `figures-babeuf`, spec 19) : sa spécification donne en `"sortie"` le MDX de la
leçon (`src/content/lecons/<siecle>/…`) et ses propres bornes, `"texte_mots"` (texte complet)
et `"cle_mots"` (passage clé). `verifier.py --tous` (donc `npm run verifier:ecrivains`) la
vérifie avec les chapitres. Les sources citées de seconde main (un texte reproduit dans une
édition Wikisource plus récente) sont vérifiées sur la page de cette édition.

`generer.py` s'arrête avec un message clair si un marqueur, une ancre (« introuvable » ou
« hors d'ordre » : réordonner alors les notes dans le gabarit) ou le passage clé pose problème.
Il remplace aussi « 1o » en début de ligne par `1<sup>o</sup>`.

## Workflow

1. Chercher les sources (`chercher.py`), lire les pages (`voir.py`), choisir les extraits.
2. Écrire `chapitres/<siecle>/<slug>.json` et `chapitres/<siecle>/<slug>.gabarit.mdx` (modèle d'extrait dans la
   charte ; `texte` et `lien` remplacés par `@@T:id@@` et `@@L:id@@`).
3. `extraits.py <slug>` : contrôler les longueurs (texte 400 à 900 mots, passage clé 150 à 350).
4. `generer.py <slug>` puis `verifier.py <slug>` (tout doit être « ok »), puis `npm run build`.
5. Retouches de l'appareil : dans le gabarit puis `generer.py`, ou dans le MDX puis
   `gabarit.py` pour garder le gabarit à jour. Ne jamais retoucher un texte cité à la main.

## Cache

`generer.py`, `extraits.py` et `voir.py` mettent les pages en cache dans `.cache/wikisource/`
(ignoré par git ; on peut le supprimer à tout moment). `verifier.py` n'utilise pas ce cache :
il télécharge à neuf chaque page publique à l'URL du lien.
