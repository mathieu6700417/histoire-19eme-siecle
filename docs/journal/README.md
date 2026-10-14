# Journaux de production

Un journal par production longue (ex. un diaporama), pour voir après coup où passent le temps
et les tokens, et ce qu'on peut améliorer.

Journaux rangés par siècle (spec 18) : `docs/journal/<siecle>/` (`noter.py --siecle <id>`, défaut `xixe`).

- `<nom>.jsonl` : lignes horodatées écrites au fil de l'eau par `scripts/journal/noter.py`
  (`debut` / `fin` d'étape, `note`, `probleme`, `idee`).
- `<nom>-bilan.md` : bilan de fin, avec la sortie de `scripts/journal/tokens.py <session-id>
  --journal docs/journal/<siecle>/<nom>.jsonl` (tokens réels par fil, par phase, par outil, et les
  résultats d'outil les plus lourds à « traîner » dans le contexte), puis les pistes retenues.

Les transcriptions lues par `tokens.py` sont celles de Claude Code
(`~/.claude/projects/<projet>/<session>.jsonl` et `<session>/subagents/`).
