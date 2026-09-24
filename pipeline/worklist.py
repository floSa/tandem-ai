#!/usr/bin/env python3
"""
Plan de travail de la prochaine mise à jour.

Répond à une seule question : « qu'est-ce qui est à vérifier maintenant, et dans
quel ordre ? » — en distinguant ce qui n'a jamais été vérifié de ce qui l'a été
mais a dépassé sa date de péremption.

C'est le point d'entrée de toute session de mise à jour. Il produit une liste
d'actions concrètes, chacune avec l'URL à ouvrir, triée par impact.

  python3 pipeline/worklist.py              # plan complet
  python3 pipeline/worklist.py --pricing    # uniquement les tarifs
  python3 pipeline/worklist.py --markdown   # sortie cochable
"""
from __future__ import annotations
import argparse, collections, re, sys
from datetime import date, datetime
from pathlib import Path
import yaml

import scope

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

# Pièges d'accès rencontrés lors des relevés précédents. Les consigner évite de
# les redécouvrir à chaque édition.
GOTCHAS = {
    "anthropic": "anthropic.com/pricing renvoie une 301 vers claude.com/pricing.",
    "openai": "openai.com/api/pricing renvoie 403. Utiliser developers.openai.com/api/docs/pricing.",
    "moonshot": "platform.moonshot.ai/docs/pricing redirige vers platform.kimi.ai/docs/pricing.",
    "mistral": "mistral.ai/pricing ne porte que les abonnements Vibe. La grille API par modèle "
               "vit sur docs.mistral.ai/inference/pricing, et la correspondance nom commercial → "
               "identifiant versionné sur docs.mistral.ai/models/overview.",
    "google": "Tarifs à paliers (≤200k / >200k) et promotions datées : relever les deux.",
    "deepseek": "Tarification heures pleines / heures creuses : relever les deux grilles.",
    "alibaba": "La page /models ne porte pas de tarif : la grille est sur "
               "alibabacloud.com/help/en/model-studio/model-pricing. Prix par région — "
               "le catalogue relève Singapour (International), la Chine continentale est "
               "nettement moins chère. Beaucoup de modèles sont à paliers de contexte.",
    "minimax": "platform.minimax.io/docs/price renvoie 404 : la grille est sous "
               "/docs/guides/pricing-paygo.",
    "meta": "La grille vit sur dev.meta.ai/models/muse-spark/. Les deux anciennes adresses "
            "y mènent par redirections successives : llama.developer.meta.com → "
            "ai.developer.meta.com (404), et developer.meta.com/ai/models/muse-spark → dev.meta.ai.",
    "xai": "docs.x.ai/docs/models porte la grille. x.ai/grok renvoie 403 : les paliers "
           "d'abonnement SuperGrok n'ont pas pu être relevés.",
}

# Pièges d'accès rencontrés sur les pages d'outils, pas de modèles.
GOTCHAS_OUTILS = {
    "windsurf": "windsurf.com redirige (308) vers devin.ai. devin.ai/pricing répond 429 "
                "(limitation de débit) : réessayer plus tard ou depuis app.devin.ai.",
}


def load(n: str) -> dict:
    p = CATALOG / n
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


def age(d) -> int | None:
    if not d:
        return None
    try:
        return (date.today() - datetime.fromisoformat(str(d)[:10]).date()).days
    except ValueError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pricing", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args()

    meta = load("_meta.yaml")
    labs = {l["id"]: l for l in load("labs.yaml").get("labs", [])}
    models = load("models.yaml").get("models", [])
    plans = load("plans.yaml").get("plans", [])
    tools = load("tools.yaml").get("tools", [])
    scores = load("scores.yaml").get("scores", [])
    bench = load("benchmarks.yaml")

    warn = meta.get("freshness", {}).get("warn_after_days", 90)
    stale = meta.get("freshness", {}).get("stale_after_days", 180)

    # Chaque tâche : (priorité, catégorie, intitulé, url, détail)
    tasks: list[tuple[int, str, str, str | None, str]] = []

    # ── 1. Tarifs API, groupés par lab ────────────────────────────────────
    per_lab = collections.defaultdict(lambda: {"never": [], "stale": [], "warn": [], "ok": 0})
    for m in models:
        pr = m.get("pricing") or {}
        src = pr.get("source") or {}
        has = pr.get("input_per_1m") is not None
        # Un modèle sans tarif éditeur (poids ouverts, génération retirée, alias
        # de passerelle) n'est pas un reste-à-faire : il n'y a rien à relever.
        if not has and src.get("status") == "no_public_price":
            continue
        lab = m.get("lab")
        weight = m.get("benchmark_records") or 0
        if not has:
            per_lab[lab]["never"].append((weight, m["id"]))
            continue
        d = age(src.get("verified_on"))
        if d is None or d > stale:
            per_lab[lab]["stale"].append((weight, m["id"], d))
        elif d > warn:
            per_lab[lab]["warn"].append((weight, m["id"], d))
        else:
            per_lab[lab]["ok"] += 1

    for lab, st in sorted(per_lab.items(),
                          key=lambda kv: -(len(kv[1]["stale"]) * 100 + len(kv[1]["never"]))):
        info = labs.get(lab, {})
        url = info.get("pricing_url")
        name = info.get("name", lab)
        g = GOTCHAS.get(lab)
        if st["stale"]:
            top = sorted(st["stale"], reverse=True)[:5]
            tasks.append((0, "TARIFS", f"{name} — {len(st['stale'])} tarifs périmés", url,
                          "à re-relever : " + ", ".join(f"`{i}`" for _, i, _ in top)
                          + (f"\n    ⓘ {g}" if g else "")))
        if st["never"]:
            top = sorted(st["never"], reverse=True)[:5]
            # Les modèles les plus mesurés d'abord : ce sont ceux qu'on cite.
            lead = ", ".join(f"`{i}`" for _, i in top if _ > 0) or "aucun modèle mesuré"
            tasks.append((1 if any(w > 0 for w, _ in st["never"]) else 3, "TARIFS",
                          f"{name} — {len(st['never'])} modèles sans tarif", url,
                          f"prioritaires (les plus mesurés) : {lead}"
                          + (f"\n    ⓘ {g}" if g else "")))
        if st["warn"]:
            tasks.append((2, "TARIFS", f"{name} — {len(st['warn'])} tarifs à rafraîchir", url,
                          f"vérifiés il y a plus de {warn} jours"))

    if a.pricing:
        emit(tasks, a.markdown)
        return 0

    # ── 2. Taux de change ─────────────────────────────────────────────────
    fx = meta.get("fx", {})
    d = age(fx.get("verified_on"))
    if fx.get("status") != "verified" or d is None or d > warn:
        tasks.append((0, "TAUX", "Taux de change USD→EUR non vérifié", fx.get("source_url"),
                      f"valeur actuelle {fx.get('usd_eur')} — toutes les conversions en euros "
                      f"en héritent. Mettre à jour `fx` dans catalog/_meta.yaml et passer "
                      f"`status: verified`."))

    # ── 3. Forfaits d'abonnement ──────────────────────────────────────────
    vendors = collections.defaultdict(list)
    for p in plans:
        d = age((p.get("source") or {}).get("verified_on"))
        if d is None or d > warn:
            vendors[p["vendor"]].append((p.get("product"), p.get("name"), d))
    for v, items in sorted(vendors.items()):
        tasks.append((1, "FORFAITS", f"{v} — {len(items)} forfaits à re-vérifier",
                      (p.get("source") or {}).get("url"),
                      ", ".join(f"{a_} {b}" for a_, b, _ in items)))
    known = {p["vendor"] for p in plans}
    for t in tools:
        # `no_subscription` : l'outil se facture à l'usage et ne vend aucun palier.
        # Vérifié, donc plus rien à relever.
        if t.get("plans") or t.get("free") or t.get("no_subscription"):
            continue
        if t.get("pricing_url") and t.get("vendor") not in known:
            tasks.append((2, "FORFAITS", f"{t['name']} — aucun forfait au catalogue",
                          t.get("pricing_url"),
                          "l'outil est payant mais ses paliers ne sont pas relevés"
                          + (f"\n    ⓘ {GOTCHAS_OUTILS[t['id']]}" if t["id"] in GOTCHAS_OUTILS else "")))

    # ── 3 bis. Couverture fournisseur ─────────────────────────────────────
    # La veille par mots-clés trouve les outils dont on parle, pas ceux qui
    # existent. Le balayage lab par lab attrape ce qu'elle manque.
    vendeurs = {(t.get("vendor") or "").lower() for t in tools}
    sans_outil = []
    for lab in labs.values():
        # Un fournisseur balayé qui ne publie aucun harnais n'est pas un trou du
        # catalogue : c'est un constat. Ce qui doit rester visible, c'est le
        # fournisseur qu'on n'a jamais cherché à balayer.
        if (lab.get("tooling") or {}).get("checked_on"):
            continue
        nom = lab["name"].split(" (")[0].split(" /")[0].lower()
        if not any(nom in v for v in vendeurs if v):
            sans_outil.append(lab)
    if sans_outil:
        tasks.append((1, "OUTILS",
                      f"{len(sans_outil)} fournisseurs sans aucun outil au catalogue", None,
                      ", ".join(l["name"] for l in sans_outil)
                      + "\n    ⓘ pour chacun : application desktop officielle ? agent CLI ? "
                        "extension IDE ? Voir protocol/04 §5."))

    # ── 4. Harnais ────────────────────────────────────────────────────────
    never, old = [], []
    for t in tools:
        v = t.get("verification") or {}
        d = age(v.get("verified_on"))
        if v.get("status") == "unverified" or d is None:
            never.append(t)
        elif d > stale:
            old.append((t, d))
    if never:
        tasks.append((1, "HARNAIS", f"{len(never)} harnais jamais re-vérifiés", None,
                      ", ".join(t["name"] for t in never[:8])
                      + ("…" if len(never) > 8 else "")
                      + "\n    ⓘ contrôler : projet actif/archivé/racheté, URL vivantes, "
                        "changement de modèle économique, date du dernier commit."))
    for t, d in old:
        g = GOTCHAS_OUTILS.get(t["id"])
        tasks.append((2, "HARNAIS", f"{t['name']} — fiche vieille de {d} j", t.get("url"),
                      f"ⓘ {g}" if g else ""))

    # ── 4 bis. Harnais mesurés mais absents du catalogue ──────────────────
    # La veille par mots-clés trouve les outils dont on parle. Les mesures, elles,
    # nomment ceux qui servent vraiment : un harnais qui apparaît dans les scores
    # existe, est utilisé, et compte — qu'on en ait entendu parler ou non. C'est
    # ce contrôle qui manquait quand mini-SWE-agent, le harnais le plus mesuré du
    # référentiel, est resté hors catalogue.
    def cle(x: str) -> str:
        return re.sub(r"[^a-z0-9]", "", (x or "").lower())

    connus = {cle(t["id"]) for t in tools} | {cle(t["name"]) for t in tools}
    ecartes = load("tools.yaml").get("ecartes") or []
    connus |= {cle(e["id"]) for e in ecartes} | {cle(e["name"]) for e in ecartes}
    vus = collections.Counter(s["harness"] for s in scores if s.get("harness"))
    inconnus = [(n, h) for h, n in vus.items()
                if not any(k and (k in cle(h) or cle(h) in k) for k in connus)]
    if inconnus:
        inconnus.sort(reverse=True)
        tasks.append((0, "HARNAIS",
                      f"{len(inconnus)} harnais mesurés absents du catalogue", None,
                      ", ".join(f"{h} ({n} scores)" for n, h in inconnus[:6])
                      + "\n    ⓘ un harnais qui apparaît dans les mesures est utilisé pour de bon. "
                        "Le cataloguer, ou consigner son rejet dans `ecartes` de tools.yaml."))

    # ── 5. Benchmarks ─────────────────────────────────────────────────────
    runs = [s.get("run_date") for s in scores if s.get("run_date")]
    if runs:
        d = age(max(runs))
        if d and d > warn:
            tasks.append((1, "BENCHMARKS", f"Dernière mesure vieille de {d} jours", None,
                          "relancer : python3 pipeline/epoch_ingest.py --force-download"))
    for b, r, lag in scope.dormant_benchmarks(scores, scope.dormant_after_days()):
        tasks.append((1, "BENCHMARKS", f"`{b}` en sommeil — dernier modèle mesuré sorti le {r}", None,
                      f"{lag} j de retard sur le modèle le plus récent du catalogue : il ne compare "
                      "plus l'offre actuelle.\n    Vérifier la source d'origine (une version plus "
                      "récente existe-t-elle ?), sinon le retirer\n    dans CURATION et consigner "
                      "le motif dans REJECTED (pipeline/epoch_ingest.py)."))
    by_b = collections.defaultdict(list)
    for s in scores:
        if s.get("score") is not None:
            by_b[s["benchmark"]].append(s["score"])
    for b in bench.get("tracked", []):
        if not b.get("track"):
            continue
        v = by_b.get(b["name"])
        if not v:
            tasks.append((2, "BENCHMARKS", f"`{b['name']}` suivi mais sans aucune mesure", None,
                          "vérifier le mapping de colonne dans pipeline/epoch_ingest.py"))
            continue
        ceil = b.get("score_ceiling") or 1.0
        if b["name"] != "METR Time Horizons" and max(v) >= 0.92 * ceil:
            tasks.append((2, "BENCHMARKS", f"`{b['name']}` saturé ({max(v):.0%})", None,
                          "pouvoir discriminant épuisé — lui chercher un remplaçant "
                          "et documenter le rejet dans REJECTED"))

    # ── 6. Veille ─────────────────────────────────────────────────────────
    if not (ROOT / ".env").exists() and not __import__("os").environ.get("AA_API_KEY"):
        tasks.append((2, "SOURCES",
                      "Source de recoupement non configurée", "https://artificialanalysis.ai/data-api",
                      "Tous les benchmarks proviennent d'Epoch AI seul : aucun chiffre n'est "
                      "confronté à un second relevé.\n    Palier gratuit suffisant (100 req/24 h), "
                      "puis : python3 pipeline/crosscheck_aa.py"))
    tasks.append((3, "VEILLE", "Rechercher les nouveaux harnais", None,
                  'requêtes : "AI code editor" 2026 · "autonomous coding agent" CLI 2026 · '
                  'site:github.com "coding agent" stars:>2000 pushed:>2026-01-01'))
    tasks.append((3, "VEILLE", "Détecter les nouveaux modèles mesurés", None,
                  "python3 pipeline/epoch_ingest.py --force-download && "
                  "python3 pipeline/seed_catalog.py"))

    emit(tasks, a.markdown)
    return 0


LABELS = {0: "BLOQUANT", 1: "IMPORTANT", 2: "À FAIRE", 3: "VEILLE"}


def emit(tasks, markdown: bool) -> None:
    tasks.sort(key=lambda t: (t[0], t[1]))
    if markdown:
        print(f"# Plan de mise à jour — {date.today().isoformat()}\n")
        cur = None
        for pr, cat, title, url, detail in tasks:
            if pr != cur:
                print(f"\n## {LABELS[pr]}\n")
                cur = pr
            line = f"- [ ] **[{cat}]** {title}"
            if url:
                line += f" — <{url}>"
            print(line)
            if detail:
                for l in detail.split("\n"):
                    print(f"      {l.strip()}")
        return

    print("═" * 78)
    print(f"  PLAN DE MISE À JOUR — {date.today().isoformat()}")
    print("═" * 78)
    if not tasks:
        print("  ✓ Rien à faire : tout est vérifié et dans les délais.")
        return
    cur = None
    for pr, cat, title, url, detail in tasks:
        if pr != cur:
            mark = {0: "✗", 1: "▲", 2: "·", 3: "○"}[pr]
            print(f"\n  {mark} {LABELS[pr]}")
            cur = pr
        print(f"      [{cat}] {title}")
        if url:
            print(f"          → {url}")
        if detail:
            for l in detail.split("\n"):
                print(f"          {l.strip()}")
    n = collections.Counter(t[0] for t in tasks)
    print("\n" + "─" * 78)
    print(f"  {n[0]} bloquant · {n[1]} important · {n[2]} à faire · {n[3]} veille")
    print("  Une fois les relevés faits : saisir dans catalog/pricing_verified.yaml,")
    print("  puis apply_pricing.py → validate.py → build_site.py")


if __name__ == "__main__":
    sys.exit(main())
