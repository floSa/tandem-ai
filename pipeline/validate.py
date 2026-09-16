#!/usr/bin/env python3
"""
Contrôle qualité du catalogue. C'est ce script qui fait la différence entre
« un document à jour » et « un document défendable ».

Sort en code 1 si une ERREUR est détectée : utilisable tel quel en CI pour
bloquer une publication qui ne respecte pas la discipline de sourçage.

Familles de contrôles :
  RÉFÉRENTIEL   intégrité des références croisées entre fichiers
  PROVENANCE    tout chiffre publié porte une source et une date de vérification
  FRAÎCHEUR     aucune donnée ne dépasse silencieusement sa date de péremption
  COHÉRENCE     contrôles arithmétiques sur les tarifs
  COMPARABILITÉ détection des scores non comparables entre eux
  COUVERTURE    trous de mesure et benchmarks à faible pouvoir discriminant
"""
from __future__ import annotations
import collections, math, sys
from datetime import date, datetime
from pathlib import Path
import yaml

import scope

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

ERR, WARN, INFO = "ERREUR", "ALERTE", "INFO"
findings: list[tuple[str, str, str]] = []


def add(level: str, family: str, msg: str) -> None:
    findings.append((level, family, msg))


def load(name: str) -> dict:
    p = CATALOG / name
    if not p.exists():
        add(ERR, "RÉFÉRENTIEL", f"fichier de catalogue manquant : catalog/{name}")
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def days_since(d: str | None) -> int | None:
    if not d:
        return None
    try:
        return (date.today() - datetime.fromisoformat(str(d)[:10]).date()).days
    except ValueError:
        return None


def main() -> int:
    meta = load("_meta.yaml")
    labs = load("labs.yaml").get("labs", [])
    models = load("models.yaml").get("models", [])
    bench = load("benchmarks.yaml")
    scores_doc = load("scores.yaml")
    scores = scores_doc.get("scores", [])
    tracked = bench.get("tracked", [])

    allowed_prov = set(meta.get("provenance_ranking", []))
    warn_days = meta.get("freshness", {}).get("warn_after_days", 90)
    stale_days = meta.get("freshness", {}).get("stale_after_days", 180)

    # ── RÉFÉRENTIEL ────────────────────────────────────────────────────────
    lab_ids = {l["id"] for l in labs}
    for m in models:
        if m.get("lab") not in lab_ids:
            add(ERR, "RÉFÉRENTIEL", f"modèle `{m['id']}` référence un lab inconnu : {m.get('lab')}")
    bench_names = {b["name"] for b in tracked}
    for b in {s["benchmark"] for s in scores}:
        if b not in bench_names:
            add(ERR, "RÉFÉRENTIEL", f"scores présents pour un benchmark hors registre : {b}")
    for b in tracked:
        if b.get("superseded_by") and b.get("track"):
            add(WARN, "RÉFÉRENTIEL",
                f"benchmark `{b['name']}` est marqué remplacé par `{b['superseded_by']}` "
                f"mais reste suivi")

    # ── PROVENANCE ─────────────────────────────────────────────────────────
    fx = meta.get("fx", {})
    if fx.get("status") != "verified" or not fx.get("verified_on"):
        add(WARN, "PROVENANCE",
            "le taux de change USD→EUR n'est pas vérifié — toutes les valeurs en euros "
            "du document en héritent")
    priced = unverified_price = no_price = 0
    for m in models:
        pr = m.get("pricing") or {}
        has_price = any(pr.get(k) is not None for k in
                        ("input_per_1m", "input_cached_per_1m", "output_per_1m"))
        src = pr.get("source") or {}
        if has_price:
            priced += 1
            if not src.get("url") or not src.get("verified_on"):
                add(ERR, "PROVENANCE",
                    f"modèle `{m['id']}` porte un tarif sans source vérifiable "
                    f"(url + verified_on obligatoires)")
            if src.get("status") not in allowed_prov and src.get("status") != "verified":
                add(ERR, "PROVENANCE",
                    f"modèle `{m['id']}` : statut de source invalide `{src.get('status')}`")
        elif src.get("status") == "no_public_price":
            # Pas de tarif éditeur par construction (poids ouverts, génération
            # retirée, alias de passerelle). La raison est obligatoire : sans
            # elle, l'exclusion serait une commodité plutôt qu'un constat.
            no_price += 1
            if not src.get("note"):
                add(ERR, "PROVENANCE",
                    f"modèle `{m['id']}` est classé sans tarif éditeur sans motif — "
                    f"renseigner `reason` dans no_public_price")
        else:
            unverified_price += 1
        if pr.get("currency") and pr["currency"] != "USD":
            add(ERR, "COHÉRENCE",
                f"modèle `{m['id']}` : les tarifs se saisissent en USD uniquement "
                f"(la conversion € est calculée au build)")
    for s in scores:
        if not s.get("source_url"):
            add(ERR, "PROVENANCE", f"score sans source : {s.get('model_version')} / {s.get('benchmark')}")
        if s.get("provenance") not in allowed_prov:
            add(ERR, "PROVENANCE",
                f"provenance invalide `{s.get('provenance')}` sur {s.get('model_version')}")
    self_rep = sum(1 for s in scores if s.get("provenance") == "self_reported")
    if self_rep:
        add(INFO, "PROVENANCE",
            f"{self_rep} scores sont auto-déclarés par le lab producteur du modèle — "
            f"à signaler explicitement dans toute publication")

    # ── FRAÎCHEUR ──────────────────────────────────────────────────────────
    for m in models:
        src = (m.get("pricing") or {}).get("source") or {}
        d = days_since(src.get("verified_on"))
        if d is None:
            continue
        if d > stale_days:
            add(ERR, "FRAÎCHEUR", f"tarif de `{m['id']}` vérifié il y a {d} j (> {stale_days} j) : périmé")
        elif d > warn_days:
            add(WARN, "FRAÎCHEUR", f"tarif de `{m['id']}` vérifié il y a {d} j : à re-vérifier")
    # Par benchmark : un benchmark qui reçoit des mesures chaque semaine ne doit pas
    # masquer un benchmark figé depuis des mois. C'est ce qui a laissé Terminal-Bench
    # 2.0, METR et SWE-bench Verified présentés comme actuels jusqu'en septembre 2026.
    for b, r, lag in scope.dormant_benchmarks(scores, scope.dormant_after_days()):
        add(WARN, "FRAÎCHEUR",
            f"`{b}` est en sommeil : son modèle mesuré le plus récent est sorti le {r}, "
            f"{lag} j avant le plus récent du catalogue — il ne compare plus l'offre actuelle, "
            f"lui chercher un remplaçant")
    since = (scores_doc.get("_generated") or {}).get("since")
    if since:
        vieux = sorted({s["model_version"] for s in scores
                        if s.get("model_released_on") and s["model_released_on"] < since})
        if vieux:
            add(ERR, "FRAÎCHEUR",
                f"{len(vieux)} scores portent sur des modèles antérieurs à la fenêtre "
                f"({since}) : " + ", ".join(f"`{v}`" for v in vieux[:5]))
    run_dates = [s["run_date"] for s in scores if s.get("run_date")]
    if run_dates:
        d = days_since(max(run_dates))
        if d and d > warn_days:
            add(WARN, "FRAÎCHEUR",
                f"le score le plus récent du catalogue date d'il y a {d} j — "
                f"relancer pipeline/epoch_ingest.py")

    # ── COHÉRENCE ──────────────────────────────────────────────────────────
    for m in models:
        pr = m.get("pricing") or {}
        i, c, o = pr.get("input_per_1m"), pr.get("input_cached_per_1m"), pr.get("output_per_1m")
        if i is not None and o is not None and o < i:
            add(WARN, "COHÉRENCE", f"`{m['id']}` : sortie ({o}) moins chère que l'entrée ({i}) — inhabituel")
        if i is not None and c is not None and c > i:
            add(ERR, "COHÉRENCE", f"`{m['id']}` : entrée en cache ({c}) plus chère qu'en cache miss ({i})")
        for k in ("input_per_1m", "input_cached_per_1m", "output_per_1m"):
            if pr.get(k) is not None and pr[k] < 0:
                add(ERR, "COHÉRENCE", f"`{m['id']}` : tarif négatif sur {k}")

    # ── COMPARABILITÉ ──────────────────────────────────────────────────────
    # Un score n'a de sens qu'avec son protocole. Si un même benchmark a été
    # passé sous plusieurs harnais, un classement brut est trompeur.
    by_bench = collections.defaultdict(list)
    for s in scores:
        by_bench[s["benchmark"]].append(s)
    for b, rows in sorted(by_bench.items()):
        harnesses = {r["harness"] for r in rows if r.get("harness")}
        if len(harnesses) > 1:
            add(INFO, "COMPARABILITÉ",
                f"`{b}` : {len(harnesses)} harnais différents mesurés — "
                f"un classement modèle-contre-modèle y est trompeur, comparer à harnais égal")
        protos = {tuple(sorted((r.get("protocol") or {}).items())) for r in rows if r.get("protocol")}
        if len(protos) > 1:
            add(INFO, "COMPARABILITÉ",
                f"`{b}` : {len(protos)} configurations de protocole distinctes "
                f"(effort de raisonnement, budget d'étapes…)")
        # Écart au sommet vs incertitude : deux modèles peuvent être à égalité statistique.
        ranked = sorted([r for r in rows if r.get("score") is not None],
                        key=lambda r: -r["score"])
        if len(ranked) >= 2 and ranked[0].get("stderr") and ranked[1].get("stderr"):
            gap = ranked[0]["score"] - ranked[1]["score"]
            comb = math.sqrt(ranked[0]["stderr"] ** 2 + ranked[1]["stderr"] ** 2)
            if gap < 1.96 * comb:
                add(INFO, "COMPARABILITÉ",
                    f"`{b}` : les deux premiers ({ranked[0]['model_version']} et "
                    f"{ranked[1]['model_version']}) ne sont PAS séparés statistiquement "
                    f"(écart {gap:.3f} < IC95 {1.96 * comb:.3f}) — ne pas titrer sur un vainqueur")

    # ── COUVERTURE ─────────────────────────────────────────────────────────
    for b in tracked:
        if not b.get("track"):
            continue
        rows = by_bench.get(b["name"], [])
        if not rows:
            add(WARN, "COUVERTURE", f"benchmark suivi `{b['name']}` sans aucun score ingéré")
            continue
        ceil = b.get("score_ceiling") or 1.0
        top = max(r["score"] for r in rows)
        if b["name"] != "METR Time Horizons" and ceil and top >= 0.92 * ceil:
            add(WARN, "COUVERTURE",
                f"`{b['name']}` est proche de la saturation (meilleur score {top:.2f} / plafond {ceil}) — "
                f"pouvoir discriminant en baisse, prévoir un remplaçant")
    # Décalage entre le marché et la mesure : un modèle peut être commercialisé
    # bien avant d'être mesuré par un tiers indépendant. Ce décalage doit être
    # affiché, pas subi — sinon le catalogue paraît incomplet alors qu'il est
    # simplement en avance sur les jeux de benchmark.
    vendus_non_mesures = [m for m in models
                          if (m.get("pricing") or {}).get("input_per_1m") is not None
                          and not m.get("epoch_model_versions")]
    if vendus_non_mesures:
        add(INFO, "COUVERTURE",
            f"{len(vendus_non_mesures)} modèles sont commercialisés (tarif relevé) mais "
            f"pas encore mesurés par une source indépendante : "
            + ", ".join(f"`{m['id']}`" for m in vendus_non_mesures[:6])
            + " — décalage normal entre annonce commerciale et mesure tierce, "
              "à signaler plutôt qu'à combler")
    mesures_sans_tarif = [m for m in models
                          if (m.get("benchmark_records") or 0) >= 20
                          and (m.get("pricing") or {}).get("input_per_1m") is None
                          and (m.get("pricing") or {}).get("source", {}).get("status")
                          != "no_public_price"]
    if mesures_sans_tarif:
        add(WARN, "COUVERTURE",
            f"{len(mesures_sans_tarif)} modèles largement mesurés n'ont aucun tarif — "
            f"ce sont ceux qu'on cite le plus : "
            + ", ".join(f"`{m['id']}`" for m in
                        sorted(mesures_sans_tarif,
                               key=lambda x: -(x.get("benchmark_records") or 0))[:5]))
    # Conformité
    sans_conf = [t for t in load("tools.yaml").get("tools", [])
                 if (t.get("compliance") or {}).get("status") in (None, "unverified")]
    if sans_conf:
        add(INFO, "COUVERTURE",
            f"{len(sans_conf)}/{len(load('tools.yaml').get('tools', []))} harnais sans "
            f"données de conformité relevées (rétention, résidence, SSO, audit)")

    measured = {s["model_version"] for s in scores}
    nomeasure = [m for m in models
                 if not set(m.get("epoch_model_versions", [])) & measured]
    if nomeasure:
        add(INFO, "COUVERTURE", f"{len(nomeasure)} modèles du catalogue sans score rattaché")

    # ── RAPPORT ────────────────────────────────────────────────────────────
    counts = collections.Counter(f[0] for f in findings)
    print("═" * 78)
    print("  CONTRÔLE QUALITÉ DU RÉFÉRENTIEL")
    print("═" * 78)
    print(f"  catalogue : {len(labs)} labs · {len(models)} modèles · "
          f"{len(tracked)} benchmarks · {len(scores)} scores")
    print(f"  tarifs    : {priced} relevés · {unverified_price} à relever · "
          f"{no_price} sans tarif éditeur")
    print("─" * 78)
    for lvl in (ERR, WARN, INFO):
        rows = [f for f in findings if f[0] == lvl]
        if not rows:
            continue
        mark = {ERR: "✗", WARN: "▲", INFO: "·"}[lvl]
        print(f"\n  {mark} {lvl} ({len(rows)})")
        for _, fam, msg in sorted(rows, key=lambda r: r[1]):
            print(f"      [{fam}] {msg}")
    print("\n" + "─" * 78)
    if counts[ERR]:
        print(f"  ✗ ÉCHEC — {counts[ERR]} erreur(s) bloquante(s). Publication déconseillée.")
        return 1
    print(f"  ✓ VALIDÉ — {counts[WARN]} alerte(s), {counts[INFO]} remarque(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
