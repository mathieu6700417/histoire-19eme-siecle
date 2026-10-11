# Spec 15 — Annotations de visionnage (outil local)

Décidé avec l'utilisateur le 2026-10-11 (questions posées une par une). But : pendant qu'il
regarde un diaporama **en local**, l'utilisateur met en pause d'une touche, note une correction à
faire, et reprend ; Claude lit ensuite ces notes dans le dépôt, avec tout le contexte, et corrige.

## Décisions

| Sujet | Décision |
|---|---|
| Portée | **Local uniquement.** Rien de cet outil ne doit exister dans le site déployé (ni script, ni style, ni point d'écriture) : `npm run build` et `npm run deploy` produisent un site identique à aujourd'hui. |
| Stockage | **Fichier dans le dépôt**, écrit par un petit serveur local : `docs/annotations/<slug>.jsonl` (une ligne JSON par annotation), captures dans `docs/annotations/<slug>/<id>.jpg`. |
| Contexte | **Complet, avec capture d'écran** (détail plus bas). |
| Saisie | **Texte + catégorie au clavier.** |
| Raccourci | **Touche A** : pause et ouverture du panneau ; **Entrée** enregistre et **reprend la lecture** où elle était ; **Échap** annule et reprend. |
| Relecture | **Repères sur la barre de progression** et **liste (touche L)** : relire, sauter à l'instant annoté, modifier, supprimer ; les annotations marquées traitées s'affichent comme telles. |

## Lancement

`npm run annoter` : construit le site en **mode annotation** et le sert sur un port local libre
(affiché), avec le point d'écriture. Les requêtes Range des audios doivent marcher (comme
`astro preview`). Sans ce mode, le lecteur n'embarque rien de l'outil. Le serveur n'écoute que
sur `127.0.0.1` et n'écrit que sous `docs/annotations/`.

## Dans le lecteur (mode annotation seulement)

- **A** (hors champ de saisie) : pause immédiate (voix, musique, segment en cours : chant, lecture,
  épisode, galerie, générique), ouverture d'un panneau sobre, monochrome, en bas de l'image, qui ne
  masque pas le centre de l'image. Les autres raccourcis du lecteur sont suspendus tant que le
  panneau est ouvert.
- Panneau : rappel d'une ligne du contexte (« diapositive 37 · 8,4 s · plan b »), champ de texte
  (multiligne, Maj+Entrée pour un saut de ligne), catégories choisies d'une touche **avant de
  taper** ou par Tab / clic : `image`, `cadrage`, `texte`, `voix`, `musique`, `surimpression`,
  `autre` (défaut : `autre`). Proposer des touches qui ne gênent pas la saisie (par exemple
  Alt+1…7, ou chiffres tant que le champ est vide) et les afficher.
- **Entrée** : enregistre, confirmation brève (« Annotation 12 enregistrée »), reprise de la lecture
  à l'instant exact de la pause. **Échap** : annule, reprend. Un texte vide n'enregistre rien.
- Si l'écriture échoue (serveur arrêté), le texte n'est pas perdu : message clair, panneau laissé
  ouvert, copie de secours dans `localStorage`, renvoi à la prochaine tentative.
- **Repères** : un petit trait sur la barre de progression à chaque annotation (gris moyen : à
  faire ; gris clair : traitée). **L** : liste des annotations de la période (numéro, lieu, catégorie,
  début du texte, état) ; Entrée ou clic saute à l'instant annoté (en pause) ; `e` modifie le texte
  ou la catégorie ; `Suppr` supprime après confirmation ; Échap ferme. Un compteur discret
  (« 12 annotations, 3 traitées ») près des contrôles.

## Ce qu'enregistre une annotation

```json
{
  "id": "20261011-142512-037",
  "cree": "2026-10-11T14:25:12+02:00", "modifie": null,
  "slug": "restauration", "categorie": "cadrage", "texte": "la tête est coupée en haut",
  "etat": "a-faire", "traitement": null,
  "lieu": {
    "type": "diapositive | plan | chant | galerie | lecture | episode | carton | generique | recapitulatif",
    "n": 37, "acte": "ultras-au-pouvoir", "segment": null, "plan": "b", "image_galerie": null,
    "instant": 8.42, "temps_global": 912.6
  },
  "ecran": {
    "image": { "fichier": "037-b.webp", "commons": "File:…", "titre_court": "…" },
    "phrase": "phrase de la narration en cours", "sous_titre": "texte affiché",
    "surimpressions": ["lieu:la-rochelle", "portrait:villele", "chiffre:…"],
    "camera": { "etape": 2, "vue": [0.12, 0.2, 0.74, 0.61] },
    "musique": "fond-ultras-1", "fenetre": [1440, 900], "plein_ecran": false
  },
  "capture": "restauration/20261011-142512-037.jpg"
}
```

- `etat` : `a-faire` ou `traite` ; `traitement` : une phrase écrite par Claude quand il corrige
  (ce qui a été fait, ou pourquoi rien n'a été fait).
- **Capture** : l'image telle que l'utilisateur la voit au moment de la pause (image, cartouche,
  surimpressions, sous-titre), en JPEG ~1280 px. Prise **dans le navigateur de l'utilisateur** si
  c'est fiable sans dépendance lourde ; sinon produite par le serveur avec `captures.py` au même
  instant (à défaut, signaler `capture: null` plutôt que d'échouer). Le panneau d'annotation n'y
  figure pas.
- Modifier ou supprimer réécrit le fichier `.jsonl` de façon atomique ; une suppression efface
  aussi la capture.

## Côté Claude

`scripts/diaporamas/annotations.py` :

- `lister <slug> [--a-faire] [--categorie x]` : une ligne par annotation (id court, lieu,
  catégorie, texte), triées par position dans le diaporama ; `--detail <id>` : tout le contexte et
  le chemin de la capture ;
- `traiter <id> "<ce qui a été fait>"` : passe l'annotation à `traite` ;
- `bilan <slug>` : nombre par catégorie et par état.

Les annotations et leurs captures sont **versionnées** (elles documentent les retouches) ; ajouter
une ligne à `CLAUDE.md` ou au README des scripts : « avant de retoucher un diaporama, lire
`annotations.py lister <slug> --a-faire` ».

## Acceptation

- `npm run build` : le HTML et les scripts produits ne contiennent aucune trace de l'outil
  (recherche de « annot » dans `dist/` vide hors contenu éditorial) ; périodes 01 à 03 identiques
  au pixel (`captures.py --comparer` sur un échantillon).
- `npm run annoter` : A met en pause et ouvre le panneau pendant une diapositive, un plan, un
  chant, une galerie, une lecture et un épisode ; Entrée écrit la ligne et la capture, la lecture
  reprend au même instant ; Échap n'écrit rien ; repères et liste fonctionnent ; modification et
  suppression réécrivent le fichier.
- `annotations.py lister restauration` relit ce qui a été saisi ; `traiter` change l'état, visible
  dans le lecteur après rechargement.
- Téléphone : hors périmètre (outil de bureau, clavier).

## Mise en œuvre (2026-10-11) : précisions et écarts

- **Mode annotation** : variable `ANNOTATIONS=1` lue par `astro.config.mjs` (constante
  `__ANNOTATIONS__`), build dans `dist-annotations/` ; serveur `scripts/diaporamas/annoter.py`
  (Python standard). `dist/` n'est jamais touché par `npm run annoter`.
- **Catégories** : chiffres 1 à 7 tant que le champ est vide, Alt+1…7 à tout moment, Tab / Maj+Tab,
  ou clic.
- **Capture** : retenue **côté serveur** (`captures.py` au même instant, en tâche de fond, fenêtre et
  sous-titres de l'utilisateur) ; `capture` vaut `null` quelques secondes, puis le chemin. Une capture
  dans le navigateur aurait demandé une bibliothèque de rendu du DOM (lourde, infidèle aux
  transformations et aux flous) ou une autorisation de capture d'onglet à chaque page. C'est donc une
  reconstitution : le plein écran, un fondu d'entrée en cours ou l'ouverture en volets ne sont pas
  reproduits à l'identique.
- **Identifiant** : fabriqué par le navigateur (heure locale + numéro de diapositive), ce qui rend le
  renvoi d'une copie de secours sans doublon ; le serveur décale d'une seconde en cas de collision.
- **Champs nuls** : `camera` hors diapositive et plan ; `image` pendant un carton, un générique, un
  épisode ; `n` et `acte` pendant le générique et le récapitulatif. `lieu.type` vaut `chant` pour un
  intermède à paroles (même illustré) et `galerie` pour une série d'images sur un extrait instrumental.
- **Saut depuis la liste** : exact pour une diapositive, un plan, un segment ; au début pour un
  carton, le générique et le récapitulatif.
- **L** met aussi la lecture en pause ; Échap la reprend, un saut laisse en pause.
