#!/usr/bin/env python3
"""Bilan des tokens d'une session Claude Code (et de ses sous-agents), par phase et par outil.

    python3 scripts/journal/tokens.py <session-id> [--journal docs/journal/<nom>.jsonl] [--top 25]

Lit ~/.claude/projects/<projet>/<session>.jsonl et <session>/subagents/*.jsonl.
- Tokens réels (champ usage de chaque requête, dédoublonné par requestId) : entrée,
  écriture et lecture du cache, sortie.
- Par phase : si un journal (scripts/journal/noter.py) est donné, chaque requête est rangée
  dans la dernière phase ouverte (`debut`) avant son horodatage.
- Par outil et par commande Bash (nom du script lancé).
- « Poids traîné » d'un résultat d'outil : sa taille estimée (caractères / 3,5) multipliée par
  le nombre de requêtes qui suivent dans le même fil, puisqu'il est relu (en cache) à chaque
  tour. Les plus gros sont les meilleurs candidats à réduire (sorties verbeuses, fichiers lus
  en entier, relectures).
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PROJET = Path.home() / ".claude" / "projects" / "-Users-mathieu-ai-projects-19eme-siecle"


def lire(chemin):
    lignes = []
    for l in chemin.open(encoding="utf-8"):
        try:
            lignes.append(json.loads(l))
        except json.JSONDecodeError:
            pass
    return lignes


def categorie_bash(cmd):
    cmd = re.sub(r"^\s*(cd\s+\S+\s*(&&|;)\s*)+", "", cmd)
    cmd = re.sub(r"^\s*(\w+=\S+\s*;?\s*)+", "", cmd)
    m = re.search(r"(scripts/[\w/]+\.py|npm run [\w:]+|npx [\w-]+|git \w+)", cmd)
    if m:
        return "Bash " + m.group(1).split("/")[-1]
    premier = cmd.strip().split()[0] if cmd.strip() else "?"
    return "Bash " + premier.split("/")[-1]


def taille(contenu):
    if isinstance(contenu, str):
        return len(contenu)
    if isinstance(contenu, list):
        return sum(len(b.get("text", "")) if isinstance(b, dict) else 0 for b in contenu)
    return 0


def analyser_fil(lignes, fil, phases):
    requetes = {}  # requestId -> (ts, usage)
    appels = {}  # tool_use_id -> (nom, résumé, index requête)
    ordre = []
    resultats = []  # (taille, index requête, tool_use_id)
    for d in lignes:
        if d.get("type") == "assistant":
            msg = d["message"]
            rid = d.get("requestId") or msg.get("id")
            # une requête est écrite en plusieurs lignes (un bloc par ligne) : on garde
            # l'usage le plus complet (la sortie n'est totale que sur la dernière)
            u = msg.get("usage") or {}
            if rid not in requetes:
                requetes[rid] = (d.get("timestamp", ""), u)
                ordre.append(rid)
            elif u.get("output_tokens", 0) >= requetes[rid][1].get("output_tokens", 0):
                requetes[rid] = (requetes[rid][0], u)
            for b in msg.get("content", []):
                if b.get("type") == "tool_use":
                    nom = b["name"]
                    entree = b.get("input", {})
                    if nom == "Bash":
                        nom = categorie_bash(entree.get("command", ""))
                        resume = entree.get("command", "")[:90]
                    else:
                        resume = str(entree.get("file_path") or entree.get("description") or "")[:90]
                    appels[b["id"]] = (nom, resume, len(ordre) - 1)
        elif d.get("type") == "user" and isinstance(d["message"].get("content"), list):
            for b in d["message"]["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    resultats.append((taille(b.get("content")), len(ordre) - 1, b["tool_use_id"]))
    n = len(ordre)
    par_outil = defaultdict(lambda: Counter())
    traines = []
    for car, idx, tid in resultats:
        nom, resume, _ = appels.get(tid, ("?", "", idx))
        tok = car / 3.5
        relu = tok * max(n - 1 - idx, 0)
        par_outil[nom]["appels"] += 1
        par_outil[nom]["tokens_resultat"] += tok
        par_outil[nom]["poids_traine"] += relu
        traines.append((relu, tok, fil, nom, resume))
    par_phase = defaultdict(Counter)
    total = Counter()
    for rid in ordre:
        ts, u = requetes[rid]
        phase = "(hors phase)"
        for debut, etape in phases:
            if debut <= ts:
                phase = etape
        c = Counter(
            entree=u.get("input_tokens", 0),
            cache_ecrit=u.get("cache_creation_input_tokens", 0),
            cache_lu=u.get("cache_read_input_tokens", 0),
            sortie=u.get("output_tokens", 0),
            requetes=1,
        )
        par_phase[phase] += c
        total += c
    return total, par_phase, par_outil, traines


def main():
    p = argparse.ArgumentParser()
    p.add_argument("session")
    p.add_argument("--journal")
    p.add_argument("--top", type=int, default=25)
    a = p.parse_args()
    phases = []
    if a.journal:
        for d in lire(Path(a.journal)):
            if d["quoi"] == "debut":
                phases.append((d["ts"].replace("+00:00", "Z"), d["etape"]))
        phases.sort()
    fils = [(PROJET / f"{a.session}.jsonl", "principal")]
    sous = PROJET / a.session / "subagents"
    if sous.is_dir():
        for f in sorted(sous.glob("*.jsonl")):
            meta = f.with_suffix(".meta.json")
            nom = json.loads(meta.read_text()).get("description", f.stem) if meta.exists() else f.stem
            fils.append((f, nom))
    grand_total = Counter()
    toutes_phases = defaultdict(Counter)
    tous_outils = defaultdict(Counter)
    tous_traines = []
    print("## Par fil (session principale et sous-agents)\n")
    print("| Fil | Requêtes | Entrée | Cache écrit | Cache lu | Sortie |\n|---|---|---|---|---|---|")
    for chemin, fil in fils:
        if not chemin.exists():
            continue
        total, pp, po, tr = analyser_fil(lire(chemin), fil, phases)
        print(f"| {fil} | {total['requetes']} | {total['entree']:,} | {total['cache_ecrit']:,} | {total['cache_lu']:,} | {total['sortie']:,} |")
        grand_total += total
        for k, v in pp.items():
            toutes_phases[k] += v
        for k, v in po.items():
            tous_outils[k] += v
        tous_traines += tr
    g = grand_total
    print(f"| **Total** | {g['requetes']} | {g['entree']:,} | {g['cache_ecrit']:,} | {g['cache_lu']:,} | {g['sortie']:,} |\n")
    if phases:
        print("## Par phase du journal\n")
        print("| Phase | Requêtes | Cache écrit | Cache lu | Sortie |\n|---|---|---|---|---|")
        for k, v in sorted(toutes_phases.items(), key=lambda kv: -kv[1]["cache_lu"]):
            print(f"| {k} | {v['requetes']} | {v['cache_ecrit']:,} | {v['cache_lu']:,} | {v['sortie']:,} |")
        print()
    print("## Par outil (résultats renvoyés au modèle)\n")
    print("| Outil | Appels | Tokens des résultats (est.) | Poids traîné (est.) |\n|---|---|---|---|")
    for k, v in sorted(tous_outils.items(), key=lambda kv: -kv[1]["poids_traine"])[: a.top]:
        print(f"| {k} | {v['appels']} | {int(v['tokens_resultat']):,} | {int(v['poids_traine']):,} |")
    print(f"\n## Les {a.top} résultats d'outil les plus lourds à traîner\n")
    print("| Poids traîné | Tokens | Fil | Outil | Appel |\n|---|---|---|---|---|")
    for relu, tok, fil, nom, resume in sorted(tous_traines, reverse=True)[: a.top]:
        resume = resume.replace("|", "\\|").replace("\n", " ")
        print(f"| {int(relu):,} | {int(tok):,} | {fil} | {nom} | `{resume}` |")


if __name__ == "__main__":
    main()
