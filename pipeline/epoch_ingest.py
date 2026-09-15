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

Source   : https://epoch.ai/benchmarks/use-this-data
Licence  : CC-BY 4.0 — l'attribution est obligatoire (voir ATTRIBUTION.md)
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.request
import zipfile
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
RAW = ROOT / "sources" / "raw"
EPOCH_URL = "https://epoch.ai/data/benchmark_data.zip"
EPOCH_ZIP = RAW / "epoch_benchmark_data.zip"

# Curation éditoriale : ce que le référentiel décide de suivre, et pourquoi.
# Epoch catalogue ~80 benchmarks ; tous n'ont pas d'intérêt pour un audit
# d'outils de développement. `track: true` = ingéré dans scores.yaml.
CURATION = {
    "SWE-Bench verified": dict(
        track=True, domain="software_engineering", tier="reference",
        measures="Résolution de vraies issues GitHub Python, patch validé par les tests du dépôt.",
        caveat="Benchmark de 2024, massivement présent dans les données d'entraînement. "
               "Les scores très élevés doivent être lus avec une réserve de contamination."),
    "Terminal Bench": dict(
        track=True, domain="agentic_cli", tier="reference",
        measures="Tâches multi-étapes en ligne de commande : navigation, exécution, vérification.",
        caveat="Le score dépend fortement du harnais (agent) utilisé, pas seulement du modèle. "
               "Toujours lire le couple (modèle, agent)."),
    "Aider polyglot": dict(
        track=True, domain="code_editing", tier="reference",
        measures="Édition de code existant dans plusieurs langages, au format diff.",
        caveat="Mesure l'édition, pas la conception. Publié par l'auteur d'Aider."),
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
    "The Agent Company": dict(
        track=True, domain="agentic_work", tier="secondary",
        measures="Tâches de travail réalistes en entreprise simulée (navigation, outils, collègues).", caveat=""),
    "APEX-Agents": dict(
        track=True, domain="agentic_work", tier="secondary",
        measures="Capacités agentiques sur tâches expertes.", caveat=""),
    "OSWorld 2.0": dict(
        track=True, domain="computer_use", tier="secondary",
        measures="Pilotage d'un vrai bureau graphique (fenêtres, applications).", caveat=""),
    "METR Time Horizons": dict(
        track=True, domain="autonomy", tier="reference",
        measures="Durée de tâche humaine qu'un modèle accomplit avec 50% de réussite. "
                 "Exprimé en minutes/heures, pas en pourcentage.",
        caveat="Unité différente des autres benchmarks : ne pas agréger avec des scores en %."),
    "Cybench": dict(
        track=True, domain="security", tier="secondary",
        measures="Résolution de défis de cybersécurité type CTF.", caveat=""),
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
    "GDPval": dict(
        track=True, domain="economic_value", tier="secondary",
        measures="Tâches professionnelles réelles évaluées par des experts du métier.", caveat=""),
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
    "Terminal Bench": None,  # placeholder, non utilisé — Terminal Bench est suivi
}


# Chaque benchmark nomme sa colonne de score différemment, et plusieurs exposent
# les paramètres du protocole de mesure (harnais, effort de raisonnement, budget
# d'étapes). Ces paramètres ne sont PAS du bruit : deux scores obtenus sous des
# protocoles différents ne sont pas comparables. On les conserve intégralement.
COLUMN_MAP = {
    "SWE-Bench verified":  dict(score="mean_score", se="stderr"),
    "Terminal Bench":      dict(score="Accuracy mean", se="Accuracy SE", harness="Agent"),
    "Aider polyglot":      dict(score="Percent correct"),
    "SciCode":             dict(score="Score"),
    "FrontierCode":        dict(score="Main score", harness="Harness", protocol=["Reasoning effort"]),
    "DeepSWE":             dict(score="Pass@1", harness="Harness", protocol=["Reasoning effort", "Pass@4"]),
    "GSO-Bench":           dict(score="Score OPT@1", harness="Scaffold"),
    "MirrorCode":          dict(score="Best score (across scorers)", se="stderr"),
    "The Agent Company":   dict(score="% Score"),
    "APEX-Agents":         dict(score="Pass@1 score"),
    "OSWorld 2.0":         dict(score="Binary accuracy",
                                protocol=["Reasoning", "Tool setting", "Step budget", "Partial score"]),
    "METR Time Horizons":  dict(score="average_score", unit="minutes", protocol=["Time horizon"]),
    "Cybench":             dict(score="Unguided % Solved"),
    "GPQA diamond":        dict(score="Best score (across scorers)", se="stderr"),
    "HLE":                 dict(score="Accuracy"),
    "ARC-AGI-2":           dict(score="Score"),
    "GDPval":              dict(score="Win Rate (%)", protocol=["Win + tie rate (%)"]),
    "Remote Labor Index":  dict(score="Score"),
}


# Métadonnées amont incomplètes : source_file vide pour certains benchmarks.
FALLBACK_FILE = {"SciCode": "scicode_external.csv"}

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
            "provenance": ("independent_run" if not b["source_file"].endswith("_external.csv")
                           else "independent_leaderboard"),
        })
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


def build_scores(z: zipfile.ZipFile, registry: dict, since: str) -> dict:
    """catalog/scores.yaml — un enregistrement par (modèle × benchmark × harnais × run)."""
    rows = []
    for bench in registry["tracked"]:
        if not bench["track"]:
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
            rows.append({
                "benchmark": bench["name"],
                "model_version": r.get("Model version") or r.get("Model") or None,
                "model_display": r.get("Name") or None,
                "organization": r.get("Organization") or r.get("Model Org") or None,
                "harness": (r.get(harness_col) or None) if harness_col else None,
                "harness_org": r.get("Agent Org") or None,
                "score": round(val * scale, 4),
                "unit": unit,
                "raw_score": round(val, 4) if scale != 1.0 else None,
                "stderr": round(float(r[se_col]) * scale, 4) if se_col and (r.get(se_col) or "").strip() else None,
                "protocol": protocol or None,
                "model_released_on": rel or None,
                "run_date": (r.get("Run date") or r.get("Started at") or "")[:10] or None,
                "provenance": bench["provenance"],
                "source_url": (r.get("Source") or "https://epoch.ai/benchmarks"),
                "evidence_url": r.get("Log viewer") or None,
            })
            kept += 1
        print(f"  {kept:>5} scores  {bench['name']}")
    return {
        "_generated": {
            "by": "pipeline/epoch_ingest.py --scores",
            "on": date.today().isoformat(),
            "upstream": "Epoch AI — Capabilities & Benchmarking (CC-BY 4.0)",
            "upstream_url": "https://epoch.ai/benchmarks",
            "filter": f"modèles publiés à partir du {since}",
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
    ap.add_argument("--since", default="2025-01-01", help="ne garder que les modèles publiés depuis cette date")
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
        dump(build_scores(z, reg, a.since), CATALOG / "scores.yaml")
    print("\n✓ ingestion terminée")
    return 0


if __name__ == "__main__":
    sys.exit(main())
