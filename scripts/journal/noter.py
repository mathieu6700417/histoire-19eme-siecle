#!/usr/bin/env python3
"""Journal de production : ajoute une ligne horodatée à docs/journal/<nom>.jsonl.

    python3 scripts/journal/noter.py <nom> debut <etape> ["détail"]
    python3 scripts/journal/noter.py <nom> fin <etape> ["bilan : chiffres, problèmes"]
    python3 scripts/journal/noter.py <nom> note <etape> "fait marquant"
    python3 scripts/journal/noter.py <nom> probleme <etape> "ce qui a coincé, temps perdu, piste"
    python3 scripts/journal/noter.py <nom> idee <etape> "comment aller plus vite la prochaine fois"

Les étapes `debut`/`fin` découpent la session en phases ; `tokens.py` s'en sert pour
attribuer les tokens consommés à chaque phase.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TYPES = {"debut", "fin", "note", "probleme", "idee"}


def main() -> None:
    if len(sys.argv) < 4 or sys.argv[2] not in TYPES:
        sys.exit(__doc__)
    nom, quoi, etape = sys.argv[1:4]
    texte = " ".join(sys.argv[4:])
    chemin = Path(__file__).resolve().parents[2] / "docs" / "journal" / f"{nom}.jsonl"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    ligne = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "quoi": quoi,
        "etape": etape,
        "texte": texte,
    }
    with chemin.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
