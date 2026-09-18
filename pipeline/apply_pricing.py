#!/usr/bin/env python3
"""
Fusionne catalog/pricing_verified.yaml (saisi à la main) dans catalog/models.yaml.

Attache à chaque tarif sa provenance complète : l'URL réellement consultée, la
date de consultation, et le niveau de provenance. Un modèle tarifé mais absent
du catalogue est ajouté (un modèle peut être commercialisé avant d'être mesuré).
"""
from __future__ import annotations
import re
import sys
from datetime import date
from pathlib import Path
import yaml

import variantes

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
    "alibaba":   ("https://www.alibabacloud.com/help/en/model-studio/model-pricing",
                  "official_pricing_page",
                  "Grille région Singapour (International). La région Chine continentale "
                  "est sensiblement moins chère — elle n'est pas relevée ici."),
    "mistral":   ("https://docs.mistral.ai/inference/pricing", "official_pricing_page",
                  "mistral.ai/pricing ne porte pas la grille par modèle ; elle vit dans la doc. "
                  "Les identifiants versionnés viennent de docs.mistral.ai/models/overview."),
    "minimax":   ("https://platform.minimax.io/docs/guides/pricing-paygo", "official_pricing_page",
                  "platform.minimax.io/docs/price est en 404 : la grille est sous /docs/guides/."),
    "xai":       ("https://docs.x.ai/docs/models", "official_pricing_page",
                  "Grille à deux paliers : au-delà de 200k tokens de contexte, le tarif double."),
}

# La règle de découpage vit dans pipeline/variantes.py : l'ingestion et la
# tarification doivent lire un identifiant de la même façon. Elles en ont
# entretenu deux versions divergentes, et un même modèle se dédoublait.
VARIANT_SUFFIX = variantes.SUFFIXE


def mark_no_public_price(models: list[dict], groups: list[dict]) -> int:
    """Classe les modèles qui n'auront jamais de tarif éditeur, avec leur raison.

    Sans cette distinction, un modèle à poids ouverts resterait indéfiniment
    « tarif à relever » — alors qu'il n'y a rien à relever.
    """
    idx = {m["id"]: m for m in models}
    n = 0
    for g in groups or []:
        reason = " ".join((g.get("reason") or "").split())
        for mid in g.get("models") or []:
            m = idx.get(mid)
            if m is None:
                print(f"  ⚠  `no_public_price` inconnu du catalogue : {mid}")
                continue
            if (m.get("pricing") or {}).get("input_per_1m") is not None:
                print(f"  ⚠  `{mid}` est classé sans tarif mais en porte un — conflit à trancher")
                continue
            m["pricing"] = {"currency": "USD", "source": {
                "url": None, "verified_on": None,
                "status": "no_public_price", "note": reason}}
            n += 1
    return n


def propagate_variants(models: list[dict]) -> int:
    """Étend le tarif d'un modèle de base à ses variantes d'effort de raisonnement."""
    idx = {m["id"]: m for m in models}
    n = 0
    for m in models:
        pr = m.get("pricing") or {}
        if pr.get("input_per_1m") is not None or pr.get("source", {}).get("status") == "no_public_price":
            continue
        mt = VARIANT_SUFFIX.match(m["id"])
        if not mt:
            continue
        base = idx.get(mt.group("base"))
        if base is None:
            continue
        # Un réglage d'exécution ne change pas le statut commercial du modèle :
        # si la base n'a pas de tarif éditeur, la variante non plus.
        if (base.get("pricing") or {}).get("source", {}).get("status") == "no_public_price":
            m["pricing"] = dict(base["pricing"])
            n += 1
            continue
        if (base.get("pricing") or {}).get("input_per_1m") is None:
            continue
        p = {k: v for k, v in base["pricing"].items() if k != "source"}
        src = dict(base["pricing"]["source"])
        src["variant_of"] = base["id"]
        src["variant_note"] = (
            f"`{mt.group('variante')}` est un réglage d'exécution du modèle "
            f"`{base['id']}`, pas une référence facturée distincte : même tarif unitaire."
        )
        p["source"] = src
        m["pricing"] = p
        for k in ("api_model_id", "context_window", "role"):
            if base.get(k) is not None and m.get(k) is None:
                m[k] = base[k]
        n += 1
    return n


def main() -> int:
    vp = yaml.safe_load((CATALOG / "pricing_verified.yaml").read_text(encoding="utf-8"))
    doc = yaml.safe_load((CATALOG / "models.yaml").read_text(encoding="utf-8"))
    models = doc.get("models", [])
    idx = {m["id"]: m for m in models}
    today = date.today().isoformat()
    # La date d'un tarif est celle où la page a été LUE, pas celle où ce script
    # tourne : sans quoi chaque relance ferait passer un vieux relevé pour frais.
    campaign_on = str((vp.get("_meta") or {}).get("verified_on") or "") or None
    if not campaign_on:
        print("  ✗ `_meta.verified_on` absent de pricing_verified.yaml : date du relevé inconnue")
        return 1
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
            "source": {"url": url, "verified_on": str(v.get("verified_on") or campaign_on),
                       "status": status,
                       **({"note": note} if note else {})},
        })
        # Variantes tarifaires : elles ne remplacent pas le tarif principal,
        # elles le qualifient.
        for k in ("offpeak", "peak_hours_utc", "promo_until", "promo_note", "tier_note"):
            if v.get(k) is not None:
                p[k] = v[k]

        # `applies_to` : identifiants du catalogue qui désignent LE MÊME modèle
        # facturé (instantané daté, alias de passerelle). Le tarif y est recopié tel
        # quel, avec la même provenance.
        for alias in v.get("applies_to") or []:
            if alias not in idx:
                print(f"  ⚠  `applies_to` inconnu du catalogue : {alias} (depuis {v['id']})")
                continue
            a = idx[alias]
            a["pricing"] = {**p, "source": {**p["source"], "priced_as": v["id"]}}
            for k in ("context_window", "role"):
                if v.get(k) is not None and a.get(k) is None:
                    a[k] = v[k]
            updated += 1

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

    excluded = mark_no_public_price(models, vp.get("no_public_price") or [])
    propagated = propagate_variants(models)

    doc["models"] = sorted(models, key=lambda m: (m["lab"], m["id"]))
    doc.setdefault("_generated", {})["pricing_applied_on"] = today
    (CATALOG / "models.yaml").write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")

    total = len(doc["models"])
    priced = sum(1 for m in doc["models"] if (m.get("pricing") or {}).get("input_per_1m") is not None)
    print(f"✓ {updated} tarifs mis à jour, {added} modèles ajoutés, {skipped} ignorés")
    print(f"  {propagated} variantes d'effort alignées sur le statut de leur modèle de base")
    print(f"  {excluded} modèles classés sans tarif éditeur (poids ouverts, retirés, alias…)")
    print(f"  catalogue : {priced}/{total} modèles tarifés")
    return 0


if __name__ == "__main__":
    sys.exit(main())
