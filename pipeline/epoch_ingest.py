#!/usr/bin/env python3
"""
Ingestion des données de benchmark Epoch AI vers le catalogue.

Epoch AI publie sous licence CC-BY un export complet de ~80 benchmarks, mêlant
des exécutions qu'ils ont menées eux-mêmes et des résultats collectés ailleurs.
La convention de nommage encode la provenance : un fichier suffixé `_external`
provient d'une source tierce, sans suffixe il s'agit d'un run interne Epoch.

Deux modes :
  --registry   (re)génère catalog/benchmarks.yaml depuis benchmark_metadata.csv
  --scores     génère catalog/scores.yaml pour les benchmarks marqués track: true

Terminal-Bench 4.0 n'est pas relayé par Epoch : il est lu sur tbench.ai par
`tbench_ingest.py` et fusionné ici, avec la même structure de ligne.

Source   : https://epoch.ai/benchmarks/use-this-data
Licence  : CC-BY 4.0 — l'attribution est obligatoire (voir ATTRIBUTION.md)
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from datetime import date, datetime
from pathlib import Path

import yaml

import scope
import tbench_ingest

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
RAW = ROOT / "sources" / "raw"
EPOCH_URL = "https://epoch.ai/data/benchmark_data.zip"
EPOCH_ZIP = RAW / "epoch_benchmark_data.zip"

# Curation éditoriale : ce que le référentiel décide de suivre, et pourquoi.
# Epoch catalogue ~80 benchmarks ; tous n'ont pas d'intérêt pour un audit
# d'outils de développement. `track: true` = ingéré dans scores.yaml.
CURATION = {
    "CursorBench": dict(
        track=True, domain="software_engineering", tier="reference",
        measures="Tâches de développement réelles tirées de l'usage de Cursor, exécutées dans son agent.",
        caveat="Publié par Cursor et mesuré dans son propre harnais : le couple (modèle, Cursor) "
               "est mesuré, pas le modèle seul."),
    "FrontierSWE": dict(
        track=True, domain="software_engineering", tier="secondary",
        measures="Projets d'ingénierie de plusieurs heures (implémentation, performance, recherche).",
        caveat="Peu de tâches (34) et un harnais unique (proximus) : moyenne sur 5 essais."),
    "SciCode": dict(
        track=True, domain="scientific_code", tier="secondary",
        measures="Implémentation de code scientifique à partir d'énoncés de recherche.", caveat=""),
    "FrontierCode": dict(
        track=True, domain="code_generation", tier="secondary",
        measures="Génération de code sur problèmes récents, conçu contre la contamination.", caveat=""),
    "DeepSWE": dict(
        track=True, domain="software_engineering", tier="secondary",
        measures="Ingénierie logicielle sur tâches longues.", caveat=""),
    "GSO-Bench": dict(
        track=True, domain="software_engineering", tier="secondary",
        measures="Optimisation de code sous contrainte de performance mesurée.", caveat=""),
    "MirrorCode": dict(
        track=True, domain="code_generation", tier="secondary",
        measures="Benchmark de code récent, résistant à la contamination.", caveat=""),
    "APEX-Agents": dict(
        track=True, domain="agentic_work", tier="secondary",
        measures="Capacités agentiques sur tâches expertes.", caveat=""),
    "PostTrainBench": dict(
        track=True, domain="agentic_work", tier="secondary",
        measures="Un agent post-entraîne lui-même un modèle ouvert sous contrainte de calcul.",
        caveat="Le harnais varie selon le modèle (Claude Code, Codex CLI, Cursor CLI) : "
               "lire le couple (modèle, harnais)."),
    "OSWorld 2.0": dict(
        track=True, domain="computer_use", tier="secondary",
        measures="Pilotage d'un vrai bureau graphique (fenêtres, applications).", caveat=""),
    "GPQA diamond": dict(
        track=True, domain="reasoning", tier="reference",
        measures="Questions scientifiques de niveau doctorat, hors de portée d'une recherche web.",
        caveat="Proche de la saturation chez les modèles de pointe : pouvoir discriminant en baisse."),
    "HLE": dict(
        track=True, domain="reasoning", tier="reference",
        measures="Humanity's Last Exam : questions expertes volontairement très difficiles.", caveat=""),
    "ARC-AGI-2": dict(
        track=True, domain="reasoning", tier="secondary",
        measures="Raisonnement abstrait sur grilles, résistant à la mémorisation.", caveat=""),
    "GDP.pdf": dict(
        track=True, domain="economic_value", tier="secondary",
        measures="Production de livrables professionnels (documents, analyses) jugés par des experts.",
        caveat="Évaluation par juges humains, protocole Surge AI."),
    "Remote Labor Index": dict(
        track=True, domain="economic_value", tier="secondary",
        measures="Capacité à accomplir des missions freelance réellement rémunérées.", caveat=""),
}

# Benchmarks explicitement écartés, avec la raison. Documenter un rejet vaut
# autant que documenter une sélection : cela évite de reposer la question.
REJECTED = {
    "MMLU": "Saturé (>90% pour tout modèle de pointe) — pouvoir discriminant nul.",
    "GSM8K": "Saturé et massivement contaminé.",
    "HellaSwag": "Obsolète, saturé depuis 2023.",
    "PIQA": "Obsolète, saturé.",
    "Winogrande": "Obsolète, saturé.",
    "TriviaQA": "Mesure la mémorisation, sans rapport avec le développement.",
    "SuperGLUE": "Obsolète (ère pré-LLM).",
    "ARC AI2": "Obsolète, saturé.",
    "OpenBookQA": "Obsolète, saturé.",
    "LAMBADA": "Obsolète (modélisation du langage brute).",
    "ANLI": "Obsolète.",
    "BBH": "Largement saturé.",
    "ScienceQA": "Obsolète, saturé.",
    "OSWorld": "Remplacé par OSWorld 2.0.",
    # Retirés en septembre 2026 : benchmarks figés à la source, qui ne mesurent plus
    # aucun modèle de l'offre actuelle. Les garder donnait une photo de 2025 présentée
    # comme actuelle.
    "Terminal Bench": "Terminal-Bench 2.0 : plus aucune soumission depuis mai 2026 (dernier modèle "
                      "GPT-5.5). Remplacé par Terminal-Bench 4.0, relevé sur tbench.ai.",
    "SWE-Bench verified": "Leaderboard officiel figé depuis février 2026, relais Epoch arrêté en "
                          "juin 2026 ; contamination avérée. Remplacé par CursorBench, FrontierSWE "
                          "et DeepSWE.",
    "METR Time Horizons": "Suite v1.1 saturée (horizon > 16 h, IC jusqu'à 55 h) et aucune mesure "
                          "depuis avril 2026.",
    "Aider polyglot": "Leaderboard abandonné : dernière soumission en octobre 2025.",
    "Cybench": "Aucune mesure depuis février 2026 ; son successeur ExploitBench est lui aussi "
               "figé (avril 2026).",
    "GDPval": "Aucune mesure depuis décembre 2025. Remplacé par GDP.pdf.",
    "The Agent Company": "Aucune mesure depuis septembre 2025.",
}


# Chaque benchmark nomme sa colonne de score différemment, et plusieurs exposent
# les paramètres du protocole de mesure (harnais, effort de raisonnement, budget
# d'étapes). Ces paramètres ne sont PAS du bruit : deux scores obtenus sous des
# protocoles différents ne sont pas comparables. On les conserve intégralement.
COLUMN_MAP = {
    "CursorBench":         dict(score="Score", cost="Cost per task", effort="Reasoning level",
                                harness_fixed="Cursor",
                                protocol=["Tokens per task", "Steps per task"]),
    "FrontierSWE":         dict(score="Score", harness="Harness", cost="Average cost (USD)",
                                protocol=["Aggregation", "Best@5", "Worst@5",
                                          "Average duration (hours)"]),
    "PostTrainBench":      dict(score="Average (%)", harness="Scaffold",
                                protocol=["Average SD (%)"]),
    "GDP.pdf":             dict(score="GDP.pdf score"),
    "SciCode":             dict(score="Score"),
    "FrontierCode":        dict(score="Main score", harness="Harness", protocol=["Reasoning effort"]),
    "DeepSWE":             dict(score="Pass@1", harness="Harness", cost="Mean cost (USD)",
                                effort="Reasoning effort", se="95% CI half-width", se_is_ci=True,
                                protocol=["Pass@4", "Mean output tokens", "Mean agent steps", "Runs"]),
    "GSO-Bench":           dict(score="Score OPT@1", harness="Scaffold"),
    "MirrorCode":          dict(score="Best score (across scorers)", se="stderr"),
    "APEX-Agents":         dict(score="Pass@1 score"),
    "OSWorld 2.0":         dict(score="Binary accuracy", cost="Estimated cost (USD)",
                                protocol=["Reasoning", "Tool setting", "Step budget", "Partial score"]),
    "GPQA diamond":        dict(score="Best score (across scorers)", se="stderr"),
    "HLE":                 dict(score="Accuracy"),
    "ARC-AGI-2":           dict(score="Score", cost="Cost per task"),
    "Remote Labor Index":  dict(score="Score"),
}


# Métadonnées amont incomplètes : source_file vide pour certains benchmarks.
FALLBACK_FILE = {"SciCode": "scicode_external.csv",
                 "CursorBench": "cursorbench_external.csv",
                 "FrontierSWE": "frontierswe_external.csv",
                 "GDP.pdf": "gdp_pdf_external.csv"}

# Vocabulaire d'effort : chaque source a le sien (`Extra High`, `xhigh`…).
EFFORT_ALIASES = {"extra high": "xhigh", "extra-high": "xhigh", "x-high": "xhigh"}
EFFORTS = {"minimal", "low", "medium", "high", "xhigh", "max"}

def fetch(force: bool = False) -> Path:
    """Télécharge l'export Epoch si absent ou si --force."""
    RAW.mkdir(parents=True, exist_ok=True)
    if EPOCH_ZIP.exists() and not force:
        print(f"  cache      {EPOCH_ZIP.relative_to(ROOT)} ({EPOCH_ZIP.stat().st_size:,} o)")
        return EPOCH_ZIP
    print(f"  téléchargement {EPOCH_URL}")
    urllib.request.urlretrieve(EPOCH_URL, EPOCH_ZIP)
    print(f"  écrit      {EPOCH_ZIP.relative_to(ROOT)} ({EPOCH_ZIP.stat().st_size:,} o)")
    return EPOCH_ZIP


def read_csv(z: zipfile.ZipFile, name: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(z.read(name).decode("utf-8"))))


def build_registry(z: zipfile.ZipFile) -> dict:
    """catalog/benchmarks.yaml — le registre raisonné des benchmarks."""
    meta = read_csv(z, "benchmark_metadata.csv")
    entries, skipped = [], []
    for b in meta:
        name = b["benchmark"]
        cur = CURATION.get(name)
        if not cur:
            if name in REJECTED and REJECTED[name]:
                skipped.append({"benchmark": name, "reason": REJECTED[name]})
            continue
        entries.append({
            "id": name.lower().replace(" ", "_").replace("-", "_"),
            "name": name,
            "domain": cur["domain"],
            "tier": cur["tier"],
            "track": cur["track"],
            "measures": cur["measures"],
            "caveat": cur["caveat"] or None,
            "released_on": b["release_date"] or None,
            "scale_to_fraction": float(b["scale"]) if b["scale"] else 1.0,
            "random_baseline": float(b["random_baseline"]) if b["random_baseline"] else None,
            "score_ceiling": float(b["score_ceiling"]) if b["score_ceiling"] else None,
            "superseded_by": b["superseded_by"] or None,
            "epoch_source_file": b["source_file"] or FALLBACK_FILE.get(name, ""),
            "provenance": ("independent_run" if not (b["source_file"] or FALLBACK_FILE.get(name, ""))
                           .endswith("_external.csv") else "independent_leaderboard"),
        })
    entries.append(dict(tbench_ingest.REGISTRY))
    return {
        "_generated": {
            "by": "pipeline/epoch_ingest.py --registry",
            "on": date.today().isoformat(),
            "upstream": "Epoch AI — Capabilities & Benchmarking (CC-BY 4.0)",
            "upstream_url": "https://epoch.ai/benchmarks",
            "warning": "Fichier généré. Éditer CURATION dans pipeline/epoch_ingest.py, pas ce fichier.",
        },
        "tracked": sorted(entries, key=lambda e: (e["tier"] != "reference", e["domain"], e["name"])),
        "rejected": sorted(skipped, key=lambda e: e["benchmark"]),
    }


def build_scores(z: zipfile.ZipFile, registry: dict, since: str, force: bool = False) -> dict:
    """catalog/scores.yaml — un enregistrement par (modèle × benchmark × harnais × run)."""
    rows = []
    for bench in registry["tracked"]:
        if not bench["track"] or not bench.get("epoch_source_file"):
            continue
        fname = bench["epoch_source_file"]
        try:
            data = read_csv(z, fname)
        except KeyError:
            print(f"  ⚠  fichier absent de l'export : {fname}")
            continue
        cm = COLUMN_MAP.get(bench["name"], {})
        cols = list(data[0].keys()) if data else []
        score_col = cm.get("score")
        if score_col not in cols:
            score_col = next((c for c in ("mean_score", "Accuracy mean",
                                          "Best score (across scorers)", "score") if c in cols), None)
        if not score_col:
            print(f"  ⚠  colonne de score introuvable dans {fname} (colonnes: {cols[:7]})")
            continue
        se_col = cm.get("se") if cm.get("se") in cols else None
        harness_col = cm.get("harness") if cm.get("harness") in cols else (
            "Agent" if "Agent" in cols else None)
        protocol_cols = [c for c in cm.get("protocol", []) if c in cols]
        cost_col = cm.get("cost") if cm.get("cost") in cols else None
        effort_col = cm.get("effort") if cm.get("effort") in cols else None
        # Certains benchmarks publient une demi-largeur d'IC95 plutôt qu'une
        # erreur-type : on ramène à l'erreur-type pour rester homogène.
        se_div = 1.96 if cm.get("se_is_ci") else 1.0
        unit = cm.get("unit", "fraction")
        # Certains benchmarks publient en % (0-100), d'autres en fraction (0-1).
        # `scale` ramène tout à une fraction comparable.
        scale = bench.get("scale_to_fraction") or 1.0
        kept = 0
        for r in data:
            raw = (r.get(score_col) or "").strip()
            if not raw:
                continue
            rel = (r.get("Release date") or "").strip()
            if rel and rel < since:
                continue
            try:
                val = float(raw)
            except ValueError:
                continue
            # Le protocole exact sous lequel le score a été obtenu.
            protocol = {c: r[c] for c in protocol_cols if (r.get(c) or "").strip()}
            mv = r.get("Model version") or r.get("Model") or None
            effort = (r.get(effort_col) or "").strip().lower() if effort_col else ""
            effort = EFFORT_ALIASES.get(effort, effort)
            effort = effort if effort in EFFORTS else ""
            if not effort and mv:
                m_ = re.search(r"_(max|xhigh|high|medium|low|minimal)$", mv)
                effort = m_.group(1) if m_ else ""
            cost = None
            if cost_col and (r.get(cost_col) or "").strip():
                try:
                    v_ = round(float(str(r[cost_col]).replace("$", "").replace(",", "")), 4)
                    # Un coût de 0 est une valeur manquante encodée en zéro, jamais
                    # une mesure : la garder fausserait le front de Pareto.
                    cost = v_ if v_ > 0 else None
                except ValueError:
                    cost = None
            rows.append({
                "benchmark": bench["name"],
                "model_version": mv,
                "model_base": re.sub(r"_(max|xhigh|high|medium|low|minimal|none|unknown)$", "", mv)
                               if mv else None,
                "effort": effort or None,
                "cost_usd": cost,
                "model_display": r.get("Name") or None,
                "organization": r.get("Organization") or r.get("Model Org") or None,
                "harness": ((r.get(harness_col) or None) if harness_col
                            else cm.get("harness_fixed")),
                "harness_org": r.get("Agent Org") or None,
                "score": round(val * scale, 4),
                "unit": unit,
                "raw_score": round(val, 4) if scale != 1.0 else None,
                "stderr": round(float(r[se_col]) * scale / se_div, 4)
                          if se_col and (r.get(se_col) or "").strip() else None,
                "protocol": protocol or None,
                "model_released_on": rel or None,
                "run_date": (r.get("Run date") or r.get("Started at") or "")[:10] or None,
                "provenance": bench["provenance"],
                "source_url": (r.get("Source") or "https://epoch.ai/benchmarks"),
                "evidence_url": r.get("Log viewer") or None,
            })
            kept += 1
        print(f"  {kept:>5} scores  {bench['name']}")
    rows += tbench_ingest.build_scores(z, since, force)
    return {
        "_generated": {
            "by": "pipeline/epoch_ingest.py --scores",
            "on": date.today().isoformat(),
            "upstream": "Epoch AI — Capabilities & Benchmarking (CC-BY 4.0)",
            "upstream_url": "https://epoch.ai/benchmarks",
            "filter": f"modèles publiés à partir du {since}",
            "since": since,
            "warning": "Fichier généré. Ne pas éditer à la main.",
        },
        "scores": rows,
    }


def dump(obj, path: Path) -> None:
    path.write_text(
        yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=100, default_flow_style=False),
        encoding="utf-8")
    print(f"  écrit      {path.relative_to(ROOT)} ({path.stat().st_size:,} o)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", action="store_true", help="régénère catalog/benchmarks.yaml")
    ap.add_argument("--scores", action="store_true", help="régénère catalog/scores.yaml")
    ap.add_argument("--force-download", action="store_true", help="ignore le cache local")
    ap.add_argument("--since", default=scope.cutoff(),
                    help="ne garder que les modèles publiés depuis cette date "
                         "(défaut : fenêtre glissante scope.model_window_months de _meta.yaml)")
    a = ap.parse_args()
    if not (a.registry or a.scores):
        a.registry = a.scores = True

    CATALOG.mkdir(exist_ok=True)
    z = zipfile.ZipFile(fetch(a.force_download))

    if a.registry:
        print("\n▸ Registre des benchmarks")
        dump(build_registry(z), CATALOG / "benchmarks.yaml")
    if a.scores:
        print("\n▸ Scores")
        reg = yaml.safe_load((CATALOG / "benchmarks.yaml").read_text(encoding="utf-8"))
        dump(build_scores(z, reg, a.since, a.force_download), CATALOG / "scores.yaml")
    print("\n✓ ingestion terminée")
    return 0


if __name__ == "__main__":
    sys.exit(main())
