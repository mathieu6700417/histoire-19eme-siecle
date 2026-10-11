# Annotations de visionnage (spec 15)

Corrections notées par l'utilisateur pendant le visionnage d'un diaporama en local
(`npm run annoter`, touche A). Un fichier `<slug>.jsonl` par période (une annotation par ligne),
captures d'écran dans `<slug>/<id>.jpg`. Fichiers écrits par `scripts/diaporamas/annoter.py` ;
ne pas les modifier à la main.

Avant de retoucher un diaporama :

    python3 scripts/diaporamas/annotations.py lister <slug> --a-faire
    python3 scripts/diaporamas/annotations.py lister <slug> --detail <id>
    python3 scripts/diaporamas/annotations.py traiter <id> "ce qui a été fait"

Format et raccourcis : `docs/specs/15-annotations-de-visionnage.md` et
`scripts/diaporamas/README.md`, « Annotations de visionnage (spec 15) ».
