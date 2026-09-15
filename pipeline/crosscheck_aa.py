#!/usr/bin/env python3
"""
Recoupement du catalogue avec Artificial Analysis.

Tout le référentiel repose sur une source unique (Epoch AI) : si elle change de
format ou s'arrête, le pipeline meurt, et surtout aucun chiffre n'est confronté à
un second relevé. Ce script apporte le contre-témoignage.

Il ne modifie RIEN. Il signale les écarts, parce qu'une contradiction entre deux
sources s'arbitre selon la hiérarchie de provenance de `catalog/_meta.yaml`, pas
automatiquement : une page /pricing officielle prime sur un agrégateur tiers.

Clé d'API : variable d'environnement AA_API_KEY, ou fichier .env non versionné.
Le palier gratuit suffit (100 requêtes / 24 h) et expose tarifs et indices.
Sans clé, le script explique comment en obtenir une et sort proprement.

    python3 pipeline/crosscheck_aa.py
    python3 pipeline/crosscheck_aa.py --tolerance 0.10
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
RAW = ROOT / "sources" / "raw"
ENDPOINT = "https://artificialanalysis.ai/api/v2/language/models/free"


def read_key() -> str | None:
    if os.environ.get("AA_API_KEY"):
        return os.environ["AA_API_KEY"].strip()
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("AA_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def fetch(key: str) -> dict:
    req = urllib.request.Request(ENDPOINT, headers={
        "x-api-key": key,
        "User-Agent": "audit-harness-referentiel/1.0 (+recoupement tarifaire)",
    })
    with urllib.request.urlopen(req, timeout=45,
                                context=ssl.create_default_context()) as r:
        return json.loads(r.read().decode("utf-8"))


def norm(s: str) -> str:
    """Rapproche des identifiants qui ne suivent pas la même convention."""
    return "".join(c for c in (s or "").lower() if c.isalnum())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tolerance", type=float, default=0.05,
                    help="écart relatif toléré sur un tarif avant signalement (défaut 5%%)")
    ap.add_argument("--save", action="store_true", help="conserve la réponse brute")
    a = ap.parse_args()

    key = read_key()
    if not key:
        print("─" * 74)
        print("  Recoupement Artificial Analysis — clé absente, rien à faire.")
        print("─" * 74)
        print("  Cette vérification est OPTIONNELLE : le pipeline fonctionne sans elle.")
        print("  Elle apporte un second relevé pour confronter les tarifs du catalogue.")
        print()
        print("  Pour l'activer :")
        print("    1. créer une clé sur https://artificialanalysis.ai/data-api")
        print("       (le palier gratuit suffit : 100 requêtes / 24 h)")
        print("    2. echo 'AA_API_KEY=votre_cle' >> .env      # .env est non versionné")
        print()
        print("  Rappel de licence : l'affichage de ces données impose une attribution")
        print("  visible à Artificial Analysis (voir ATTRIBUTION.md).")
        return 0

    try:
        payload = fetch(key)
    except urllib.error.HTTPError as e:
        code = e.code
        msg = {401: "clé invalide ou révoquée",
               403: "le palier de l'abonnement ne couvre pas cet endpoint",
               429: "quota de 100 requêtes/24 h épuisé"}.get(code, "erreur serveur")
        print(f"✗ Artificial Analysis a répondu {code} — {msg}.")
        return 1
    except Exception as e:
        print(f"✗ appel impossible : {e}")
        return 1

    if a.save:
        RAW.mkdir(parents=True, exist_ok=True)
        (RAW / f"aa_{date.today().isoformat()}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    amont = payload.get("data", [])
    models = yaml.safe_load((CATALOG / "models.yaml").read_text(encoding="utf-8"))["models"]
    idx = {}
    for m in models:
        for k in filter(None, [m.get("api_model_id"), m["id"], m.get("display_name")]):
            idx.setdefault(norm(k), m)

    ecarts, confirmes, inconnus = [], 0, []
    for row in amont:
        cle = next((norm(row.get(k)) for k in ("slug", "id", "name")
                    if row.get(k) and norm(row.get(k)) in idx), None)
        if not cle:
            inconnus.append(row.get("name") or row.get("slug"))
            continue
        m = idx[cle]
        pr = m.get("pricing") or {}
        for champ_aa, champ_cat, lbl in (
            ("price_1m_input_tokens", "input_per_1m", "entrée"),
            ("price_1m_output_tokens", "output_per_1m", "sortie"),
            ("price_1m_cache_hit_tokens", "input_cached_per_1m", "cache"),
        ):
            v_aa, v_cat = row.get(champ_aa), pr.get(champ_cat)
            if v_aa is None or v_cat is None:
                continue
            if v_cat == 0 and v_aa == 0:
                confirmes += 1
                continue
            base = max(abs(v_cat), 1e-9)
            if abs(v_aa - v_cat) / base > a.tolerance:
                ecarts.append((m["id"], lbl, v_cat, v_aa,
                               (v_aa - v_cat) / base,
                               (pr.get("source") or {}).get("status")))
            else:
                confirmes += 1

    print("═" * 74)
    print("  RECOUPEMENT — Artificial Analysis contre le catalogue")
    print("═" * 74)
    print(f"  {len(amont)} modèles en amont · {len(amont) - len(inconnus)} rapprochés · "
          f"{confirmes} valeurs confirmées · {len(ecarts)} écarts")
    if ecarts:
        print(f"\n  ▲ Écarts supérieurs à {a.tolerance:.0%}\n")
        for mid, lbl, cat, aa, rel, st in sorted(ecarts, key=lambda x: -abs(x[4])):
            print(f"      {mid:<26} {lbl:<8} catalogue ${cat:<9g} "
                  f"AA ${aa:<9g} ({rel:+.0%})")
            print(f"          provenance du catalogue : {st or 'non renseignée'}")
        print("\n  ARBITRAGE — ne rien modifier automatiquement.")
        print("  Si le catalogue porte `official_pricing_page`, il prime : Artificial")
        print("  Analysis est un agrégateur tiers, plus bas dans la hiérarchie de")
        print("  provenance. Un écart persistant signale plutôt un tarif qui a bougé")
        print("  depuis le relevé — rouvrir la page officielle et re-relever.")
    else:
        print("\n  ✓ Aucun écart au-delà de la tolérance : les deux sources concordent.")
    if inconnus:
        print(f"\n  · {len(inconnus)} modèles en amont absents du catalogue "
              f"(candidats à l'ajout) :")
        print("      " + ", ".join(str(x) for x in inconnus[:12]))
    print("\n  Source : Artificial Analysis — attribution obligatoire (ATTRIBUTION.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
