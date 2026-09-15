#!/usr/bin/env python3
"""
Compare le catalogue courant au dernier instantané publié et produit le
changelog de l'édition.

C'est ce qui transforme un document daté en observatoire : « qu'est-ce qui a
changé depuis la dernière fois ? » doit avoir une réponse sans relire le Guide.

  python3 pipeline/changelog.py            # diff contre le dernier instantané
  python3 pipeline/changelog.py --snapshot # fige l'état courant après publication
"""
from __future__ import annotations
import argparse, json, sys
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG, SNAP = ROOT / "catalog", ROOT / "snapshots"


def state() -> dict:
    """Réduit le catalogue aux faits dont un changement mérite d'être signalé."""
    def load(n):
        p = CATALOG / n
        return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    models, scores = load("models.yaml").get("models", []), load("scores.yaml").get("scores", [])
    tools = load("tools.yaml").get("tools", [])
    best: dict[str, dict] = {}
    for s in scores:
        if s.get("score") is None:
            continue
        k = s["benchmark"]
        if k not in best or s["score"] > best[k]["score"]:
            best[k] = {"score": s["score"], "model": s.get("model_version"),
                       "harness": s.get("harness")}
    return {
        "edition": load("_meta.yaml").get("audit", {}).get("edition"),
        "models": {m["id"]: {
            "lab": m.get("lab"), "status": m.get("status"),
            "price_in": (m.get("pricing") or {}).get("input_per_1m"),
            "price_out": (m.get("pricing") or {}).get("output_per_1m"),
        } for m in models},
        "tools": {t["id"]: {"status": t.get("status"), "name": t.get("name")} for t in tools},
        "benchmarks": best,
        "counts": {"models": len(models), "scores": len(scores), "tools": len(tools)},
    }


def latest() -> tuple[Path | None, dict]:
    snaps = sorted(SNAP.glob("*.json"))
    if not snaps:
        return None, {}
    return snaps[-1], json.loads(snaps[-1].read_text(encoding="utf-8"))


def fmt(v) -> str:
    return "—" if v is None else f"${v:g}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true", help="fige l'état courant")
    a = ap.parse_args()
    SNAP.mkdir(exist_ok=True)
    cur = state()

    if a.snapshot:
        p = SNAP / f"{date.today().isoformat()}.json"
        p.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"✓ instantané figé : {p.relative_to(ROOT)}")
        return 0

    path, prev = latest()
    if not prev:
        print("Aucun instantané de référence.\n"
              "  Figer l'état courant : python3 pipeline/changelog.py --snapshot")
        return 0

    L = [f"# Changelog — édition {cur['edition']}", "",
         f"Comparaison avec l'instantané `{path.name}`.", ""]

    # Modèles
    new = sorted(set(cur["models"]) - set(prev["models"]))
    gone = sorted(set(prev["models"]) - set(cur["models"]))
    if new:
        L += ["## Modèles entrants", ""] + [f"- `{m}` ({cur['models'][m]['lab']})" for m in new] + [""]
    if gone:
        L += ["## Modèles sortants", ""] + [f"- `{m}`" for m in gone] + [""]

    moves = []
    for m in sorted(set(cur["models"]) & set(prev["models"])):
        c, p = cur["models"][m], prev["models"][m]
        for k, lbl in (("price_in", "entrée"), ("price_out", "sortie")):
            if c[k] != p[k]:
                arrow = ("↑" if (c[k] or 0) > (p[k] or 0) else "↓") if (c[k] and p[k]) else "•"
                moves.append(f"- `{m}` {lbl} : {fmt(p[k])} → {fmt(c[k])} {arrow}")
        if c["status"] != p["status"]:
            moves.append(f"- `{m}` statut : {p['status']} → {c['status']}")
    if moves:
        L += ["## Mouvements tarifaires et de statut", ""] + moves + [""]

    # Outils
    tnew = sorted(set(cur["tools"]) - set(prev["tools"]))
    tgone = sorted(set(prev["tools"]) - set(cur["tools"]))
    tmov = [f"- `{t}` : {prev['tools'][t]['status']} → {cur['tools'][t]['status']}"
            for t in sorted(set(cur["tools"]) & set(prev["tools"]))
            if cur["tools"][t]["status"] != prev["tools"][t]["status"]]
    if tnew or tgone or tmov:
        L += ["## Harnais", ""]
        L += [f"- entrant : `{t}`" for t in tnew]
        L += [f"- sorti du catalogue : `{t}`" for t in tgone]
        L += tmov + [""]

    # Benchmarks : nouveaux états de l'art
    sota = []
    for b, c in sorted(cur["benchmarks"].items()):
        p = prev["benchmarks"].get(b)
        if not p:
            sota.append(f"- `{b}` : nouveau suivi — {c['score']:.1%} par `{c['model']}`")
        elif c["model"] != p["model"]:
            h = f" (harnais : {c['harness']})" if c.get("harness") else ""
            sota.append(f"- `{b}` : {p['score']:.1%} `{p['model']}` → "
                        f"**{c['score']:.1%}** `{c['model']}`{h}")
    if sota:
        L += ["## État de l'art par benchmark", ""] + sota + [""]

    L += ["## Volumétrie", "",
          f"| | précédent | courant |", "| :-- | --: | --: |"]
    for k, lbl in (("models", "Modèles"), ("tools", "Harnais"), ("scores", "Mesures")):
        L.append(f"| {lbl} | {prev['counts'].get(k, 0)} | {cur['counts'][k]} |")
    L += ["", "---", "",
          "Données de benchmark : Epoch AI — *Capabilities & Benchmarking* (CC-BY 4.0)."]

    out = ROOT / f"CHANGELOG-{date.today().isoformat()}.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\n✓ écrit : {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
