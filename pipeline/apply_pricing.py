#!/usr/bin/env python3
"""
Fusionne catalog/pricing_verified.yaml (saisi à la main) dans catalog/models.yaml.

Attache à chaque tarif sa provenance complète : l'URL réellement consultée, la
date de consultation, et le niveau de provenance. Un modèle tarifé mais absent
du catalogue est ajouté (un modèle peut être commercialisé avant d'être mesuré).
"""
from __future__ import annotations
import sys
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

# URL RÉELLEMENT consultées lors du relevé — pas les URL théoriques de labs.yaml.
# Une redirection change la source : on consigne la destination.
SOURCES = {
    "anthropic": ("https://claude.com/pricing", "official_pricing_page",
                  "anthropic.com/pricing redirige (301) vers claude.com/pricing."),
    "openai":    ("https://developers.openai.com/api/docs/pricing", "official_pricing_page",
                  "platform.openai.com/docs/pricing redirige vers developers.openai.com."),
    "google":    ("https://ai.google.dev/gemini-api/docs/pricing", "official_pricing_page",
                  "Plusieurs modèles en tarif promotionnel jusqu'au 31/12/2026."),
    "deepseek":  ("https://api-docs.deepseek.com/quick_start/pricing", "official_pricing_page",
                  "Tarification dynamique : heures creuses à 50%. Montants = tarif de pointe."),
    "moonshot":  ("https://platform.kimi.ai/docs/pricing", "official_pricing_page",
                  "platform.moonshot.ai redirige vers platform.kimi.ai."),
    "zhipu":     ("https://docs.z.ai/guides/overview/pricing", "official_pricing_page", None),
}


def main() -> int:
    vp = yaml.safe_load((CATALOG / "pricing_verified.yaml").read_text(encoding="utf-8"))
    doc = yaml.safe_load((CATALOG / "models.yaml").read_text(encoding="utf-8"))
    models = doc.get("models", [])
    idx = {m["id"]: m for m in models}
    today = date.today().isoformat()
    updated = added = skipped = 0

    for v in vp.get("models", []):
        lab = v["lab"]
        if lab not in SOURCES:
            print(f"  ⚠  pas de source déclarée pour le lab `{lab}` — {v['id']} ignoré")
            skipped += 1
            continue
        url, status, note = SOURCES[lab]
        p = dict(v["pricing"])
        p.update({
            "currency": "USD",
            "source": {"url": url, "verified_on": today, "status": status,
                       **({"note": note} if note else {})},
        })
        # Variantes tarifaires : elles ne remplacent pas le tarif principal,
        # elles le qualifient.
        for k in ("offpeak", "peak_hours_utc", "promo_until", "promo_note", "tier_note"):
            if v.get(k) is not None:
                p[k] = v[k]

        if v["id"] in idx:
            m = idx[v["id"]]
            m["pricing"] = p
            for k in ("api_model_id", "context_window", "role", "display_name"):
                if v.get(k) is not None:
                    m[k] = v[k]
            updated += 1
        else:
            models.append({
                "id": v["id"], "lab": lab,
                "display_name": v.get("display_name", v["id"]),
                "released_on": None, "accessibility": None,
                "benchmark_records": 0, "epoch_model_versions": [],
                "status": "active",
                "api_model_id": v.get("api_model_id"),
                "context_window": v.get("context_window"),
                "role": v.get("role"),
                "pricing": p,
            })
            added += 1

    doc["models"] = sorted(models, key=lambda m: (m["lab"], m["id"]))
    doc.setdefault("_generated", {})["pricing_applied_on"] = today
    (CATALOG / "models.yaml").write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")

    total = len(doc["models"])
    priced = sum(1 for m in doc["models"] if (m.get("pricing") or {}).get("input_per_1m") is not None)
    print(f"✓ {updated} tarifs mis à jour, {added} modèles ajoutés, {skipped} ignorés")
    print(f"  catalogue : {priced}/{total} modèles tarifés")
    return 0


if __name__ == "__main__":
    sys.exit(main())
