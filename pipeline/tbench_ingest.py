#!/usr/bin/env python3
"""
Terminal-Bench 4.0, relevé sur le leaderboard officiel tbench.ai.

Epoch AI ne relaie que Terminal-Bench 2.0, dont la dernière soumission date de mai
2026. La version courante n'existe que sur tbench.ai : ce module la lit à la source,
et `epoch_ingest.py` l'intègre au registre et aux scores comme n'importe quel autre
benchmark.

La page n'expose pas d'API : les lignes du classement sont embarquées dans le flux
de données Next.js (`self.__next_f.push`). Si la structure change, le parseur
échoue bruyamment plutôt que de produire un classement partiel.

Aucun identifiant n'est inventé : un libellé de modèle est rattaché à l'identifiant
Epoch dont le nom affiché correspond. Un libellé sans correspondance est écarté et
signalé — il faut alors compléter ALIASES à la main.
"""
from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "sources" / "raw"
URL = "https://www.tbench.ai/leaderboard/terminal-bench/4.0"
CACHE = RAW / "tbench_4.0.html"
NAME = "Terminal-Bench 4.0"

REGISTRY = {
    "id": "terminal_bench_4_0",
    "name": NAME,
    "domain": "agentic_cli",
    "tier": "reference",
    "track": True,
    "measures": "Tâches multi-étapes en ligne de commande : navigation, exécution, vérification.",
    "caveat": "Le score dépend fortement du harnais (agent) utilisé, pas seulement du modèle. "
              "Toujours lire le couple (modèle, agent).",
    "released_on": None,
    "scale_to_fraction": 0.01,
    "random_baseline": 0.0,
    "score_ceiling": 1.0,
    "superseded_by": None,
    "epoch_source_file": None,
    "source_url": URL,
    "provenance": "independent_leaderboard",
}

# Libellé tbench.ai → identifiant de base Epoch, quand les noms affichés divergent
# au-delà de ce que la normalisation absorbe.
ALIASES: dict[str, str] = {}

EFFORTS = {"low", "medium", "high", "xhigh", "max", "minimal"}


def fetch(force: bool = False) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    if CACHE.exists() and not force:
        return CACHE
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (tandem-ai)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        CACHE.write_bytes(r.read())
    return CACHE


def parse_rows(html: str) -> list[dict]:
    """Extrait les lignes brutes du classement depuis le flux Next.js."""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    flight = "".join(json.loads(f'"{c}"') for c in chunks)
    if f'"title":"{NAME}"' not in flight:
        raise ValueError(f"la page ne porte plus le classement « {NAME} » — structure changée ?")
    i = flight.find('"rows":[')
    if i < 0:
        raise ValueError("lignes du classement introuvables dans le flux Next.js")
    rows, _ = json.JSONDecoder().raw_decode(flight[i + len('"rows":'):])
    if not rows or "metrics" not in rows[0]:
        raise ValueError("classement vide ou format de ligne inattendu")
    return rows


def _norm(s: str) -> str:
    s = re.sub(r"\(.*?\)", "", s.lower())
    s = re.sub(r"^claude\s+", "", s.strip())
    return re.sub(r"[\s\-_]+", " ", s).strip()


def epoch_index(z: zipfile.ZipFile) -> dict[str, dict]:
    """Nom affiché normalisé → {base, organization} depuis model_metadata.csv."""
    idx: dict[str, dict] = {}
    meta = csv.DictReader(io.StringIO(z.read("model_metadata.csv").decode("utf-8")))
    for r in meta:
        # Suffixe de réglage (`_max`, `_24K`) retiré : on rattache au modèle de base.
        base = re.sub(r"_[A-Za-z0-9]+$", "", r["model_version"])
        idx.setdefault(_norm(r["display_name"] or ""), {
            "base": base, "organization": r["organization"] or None})
    return idx


def build_scores(z: zipfile.ZipFile, since: str, force: bool = False) -> list[dict]:
    rows = parse_rows(fetch(force).read_text(encoding="utf-8"))
    idx = epoch_index(z)
    out, unmatched = [], []
    for r in rows:
        md, mt = r["metadata"], r["metrics"]
        label = md["model_display"]["label"]
        hit = ({"base": ALIASES[label], "organization": md["model_org"]["label"]}
               if label in ALIASES else idx.get(_norm(label)))
        if not hit:
            unmatched.append(label)
            continue
        rel = md.get("date")
        if rel and rel < since:
            continue
        effort = (md.get("reasoning_effort") or "").lower()
        effort = effort if effort in EFFORTS else None
        n = mt.get("n_trials") or r.get("n_trials")
        cost = mt.get("total_cost_usd")
        ci = mt.get("accuracy_ci95_half_width")
        out.append({
            "benchmark": NAME,
            "model_version": f"{hit['base']}_{effort or 'unknown'}",
            "model_base": hit["base"],
            "effort": effort,
            # Coût total du run rapporté à un essai : même grandeur que le coût
            # par tâche des autres benchmarks.
            "cost_usd": round(cost / n, 4) if cost and n else None,
            "model_display": label,
            "organization": hit["organization"],
            "harness": md["agent_display"]["label"],
            "harness_org": md["agent_org"]["label"],
            "score": round(mt["accuracy"] * REGISTRY["scale_to_fraction"], 4),
            "unit": "fraction",
            "raw_score": mt["accuracy"],
            # Demi-largeur d'IC95 en points de pourcentage → erreur-type en fraction.
            "stderr": round(ci * REGISTRY["scale_to_fraction"] / 1.96, 4) if ci else None,
            "protocol": {"Trials": str(n), "Pass@5": str(mt.get("pass_at_5"))}
                        if mt.get("pass_at_5") is not None else {"Trials": str(n)},
            "model_released_on": rel,
            "run_date": (r.get("created_at") or "")[:10] or None,
            "provenance": REGISTRY["provenance"],
            "source_url": URL,
            "evidence_url": None,
        })
    for label in unmatched:
        print(f"  ⚠  {NAME} : « {label} » sans identifiant Epoch — compléter ALIASES "
              f"dans pipeline/tbench_ingest.py")
    print(f"  {len(out):>5} scores  {NAME} (tbench.ai)")
    return out
