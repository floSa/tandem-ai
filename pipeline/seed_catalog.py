#!/usr/bin/env python3
"""
Amorce catalog/labs.yaml et catalog/models.yaml à partir des identités de modèles
réellement observées dans les données de benchmark.

Principe : on n'invente aucun modèle. Un modèle n'entre au catalogue que s'il
apparaît dans au moins une source de benchmark vérifiable. Les champs tarifaires
sont délibérément laissés vides et marqués `unverified` — ils ne peuvent être
remplis que depuis la page /pricing officielle du fournisseur.

Un modèle publié avant la fenêtre glissante (`scope.model_window_months`) est
obsolète et n'entre pas. `labs.yaml` n'est pas écrasé : les champs relevés à la main
(source vérifiée, balayage outillage) sont conservés, seul le décompte est mis à jour.
"""
from __future__ import annotations
import collections, csv, io, re, sys, zipfile
from datetime import date
from pathlib import Path
import yaml

import scope

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
EPOCH_ZIP = ROOT / "sources" / "raw" / "epoch_benchmark_data.zip"

# Labs suivis par le référentiel, avec leurs points d'entrée officiels.
# Les URL sont le point de départ obligatoire de toute vérification tarifaire.
LABS = {
    "Anthropic":        dict(id="anthropic", country="US",
                             pricing_url="https://www.anthropic.com/pricing",
                             api_docs="https://docs.claude.com/en/docs/about-claude/models",
                             console="https://console.anthropic.com"),
    "OpenAI":           dict(id="openai", country="US",
                             pricing_url="https://openai.com/api/pricing/",
                             api_docs="https://platform.openai.com/docs/models",
                             console="https://platform.openai.com"),
    "Google DeepMind":  dict(id="google", country="US",
                             pricing_url="https://ai.google.dev/gemini-api/docs/pricing",
                             api_docs="https://ai.google.dev/gemini-api/docs/models",
                             console="https://aistudio.google.com"),
    "DeepSeek":         dict(id="deepseek", country="CN",
                             pricing_url="https://api-docs.deepseek.com/quick_start/pricing",
                             api_docs="https://api-docs.deepseek.com",
                             console="https://platform.deepseek.com"),
    "Alibaba":          dict(id="alibaba", country="CN",
                             pricing_url="https://www.alibabacloud.com/help/en/model-studio/models",
                             api_docs="https://www.alibabacloud.com/help/en/model-studio",
                             console="https://modelstudio.console.alibabacloud.com"),
    "Mistral AI":       dict(id="mistral", country="FR",
                             pricing_url="https://mistral.ai/pricing",
                             api_docs="https://docs.mistral.ai/getting-started/models/models_overview/",
                             console="https://console.mistral.ai"),
    "Moonshot":         dict(id="moonshot", country="CN",
                             pricing_url="https://platform.moonshot.ai/docs/pricing",
                             api_docs="https://platform.moonshot.ai/docs",
                             console="https://platform.moonshot.ai"),
    "Z.ai (Zhipu AI)":  dict(id="zhipu", country="CN",
                             pricing_url="https://docs.z.ai/guides/overview/pricing",
                             api_docs="https://docs.z.ai",
                             console="https://z.ai"),
    "xAI":              dict(id="xai", country="US",
                             pricing_url="https://docs.x.ai/docs/models",
                             api_docs="https://docs.x.ai",
                             console="https://console.x.ai"),
    "Meta AI":          dict(id="meta", country="US",
                             pricing_url="https://llama.developer.meta.com/docs/pricing",
                             api_docs="https://llama.developer.meta.com/docs",
                             console="https://llama.developer.meta.com"),
    "MiniMax":          dict(id="minimax", country="CN",
                             pricing_url="https://platform.minimax.io/docs/price",
                             api_docs="https://platform.minimax.io/docs",
                             console="https://platform.minimax.io"),
}

UNVERIFIED = dict(url=None, verified_on=None, status="unverified",
                  note="À renseigner depuis la page /pricing officielle du lab.")


def clean_version(v: str) -> str:
    """`claude-opus-4-7_max` → (`claude-opus-4-7`, `max`) : suffixe = effort de raisonnement."""
    m = re.match(r"^(.*?)_(max|high|medium|low|xhigh|minimal|unknown)$", v)
    return (m.group(1), m.group(2)) if m else (v, None)


def main() -> int:
    if not EPOCH_ZIP.exists():
        print("✗ données Epoch absentes — lancer d'abord : python3 pipeline/epoch_ingest.py")
        return 1
    z = zipfile.ZipFile(EPOCH_ZIP)
    meta = list(csv.DictReader(io.StringIO(z.read("model_metadata.csv").decode())))
    scores = yaml.safe_load((CATALOG / "scores.yaml").read_text(encoding="utf-8"))["scores"]

    # Un modèle n'est retenu que s'il est à la fois documenté ET mesuré.
    measured = collections.Counter()
    for s in scores:
        if s["model_version"]:
            measured[clean_version(s["model_version"])[0]] += 1

    since = scope.cutoff()
    by_lab: dict[str, dict] = collections.defaultdict(dict)
    for r in meta:
        org, ver = r["organization"], r["model_version"]
        if org not in LABS or not ver or not r["date"]:
            continue
        base, _ = clean_version(ver)
        if base not in measured or r["date"] < since:
            continue
        e = by_lab[org].setdefault(base, {
            "id": base, "lab": LABS[org]["id"],
            "display_name": r["display_name"] or base,
            "released_on": r["date"],
            "accessibility": r["accessibility"] or None,
            "benchmark_records": measured[base],
            "epoch_model_versions": set(),
            "status": "active",
            "api_model_id": None,
            "context_window": None,
            "role": None,
            "pricing": {"currency": "USD", "input_per_1m": None,
                        "input_cached_per_1m": None, "output_per_1m": None,
                        "source": dict(UNVERIFIED)},
        })
        e["epoch_model_versions"].add(ver)

    labs_path = CATALOG / "labs.yaml"
    existing = {l["id"]: l for l in
                (yaml.safe_load(labs_path.read_text(encoding="utf-8")) or {}).get("labs", [])} \
        if labs_path.exists() else {}
    labs_out, models_out = [], []
    for org, cfg in LABS.items():
        if org not in by_lab and cfg["id"] not in existing:
            continue
        lab = existing.get(cfg["id"]) or {
            "id": cfg["id"], "name": org, "country": cfg["country"],
            "pricing_url": cfg["pricing_url"], "api_docs_url": cfg["api_docs"],
            "console_url": cfg["console"],
            "model_count_tracked": 0,
            "source": dict(UNVERIFIED),
        }
        lab["model_count_tracked"] = len(by_lab.get(org, {}))
        labs_out.append(lab)
        if org not in by_lab:
            continue
        for m in sorted(by_lab[org].values(), key=lambda x: (x["released_on"], x["id"]), reverse=True):
            m["epoch_model_versions"] = sorted(m["epoch_model_versions"])
            models_out.append(m)

    hdr = {
        "_generated": {
            "by": "pipeline/seed_catalog.py", "on": date.today().isoformat(),
            "basis": "Identités de modèles observées dans les données de benchmark Epoch AI (CC-BY).",
            "warning": "AMORCE. Les champs tarifaires sont vides et marqués `unverified` : "
                       "ils doivent être renseignés depuis la page /pricing officielle de chaque lab. "
                       "Voir protocol/04_collecte_donnees.md.",
        }}
    labs_path.write_text(
        yaml.safe_dump({**hdr, "labs": labs_out}, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    (CATALOG / "models.yaml").write_text(
        yaml.safe_dump({**hdr, "models": models_out}, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"✓ {len(labs_out)} labs, {len(models_out)} modèles amorcés (tarifs à vérifier)")
    for l in labs_out:
        print(f"    {l['name']:<20} {l['model_count_tracked']:>3} modèles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
