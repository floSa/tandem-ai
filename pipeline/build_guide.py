#!/usr/bin/env python3
"""
Régénère le Guide Markdown depuis le catalogue.

Le narratif vit dans content/ et s'écrit à la main ; les tableaux sont calculés.
Aucune valeur chiffrée n'est saisie dans ce fichier ni dans les fragments : tout
provient de catalog/, y compris les conversions en euros.
"""
from __future__ import annotations
import collections, sys
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG, CONTENT = ROOT / "catalog", ROOT / "content"
OUT = ROOT / "Guide_Complet_Solutions_Dev_IA_2026.md"

CAT = {"ide_fork": "IDE dérivés", "vscode_extension": "Extensions VS Code",
       "desktop_app": "Applications desktop", "cli_agent": "Agents CLI",
       "gateway": "Passerelles"}


def load(n):
    p = CATALOG / n
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


def frag(n):
    p = CONTENT / n
    return p.read_text(encoding="utf-8").rstrip() if p.exists() else ""


def eur(usd, fx, vat=None):
    if usd is None:
        return "—"
    v = usd * fx * (1 + vat if vat else 1)
    return f"{v:,.2f} €".replace(",", " ").replace(".", ",")


def usd(v):
    return "—" if v is None else (f"${v:g}" if v else "gratuit")


def build_fiches(labs, models, plans, tools, scores, fx, vat) -> int:
    """Régénère data/ : une fiche par catégorie de harnais, plus une par lab.

    Ces fiches dupliquaient le catalogue et constituaient une seconde source de
    vérité. Générées, elles n'en sont plus une.
    """
    import collections
    DATA = ROOT / "data"
    DATA.mkdir(exist_ok=True)
    for old in DATA.glob("*.md"):
        old.unlink()
    hdr = ("<!-- FICHIER GÉNÉRÉ par pipeline/build_guide.py — ne pas éditer.\n"
           "     Corriger dans catalog/, puis régénérer. -->\n\n")
    written = 0

    by_cat = collections.defaultdict(list)
    for t in tools:
        by_cat[t.get("category", "autre")].append(t)
    for i, (cat, label) in enumerate(CAT.items(), start=1):
        items = sorted(by_cat.get(cat, []), key=lambda x: x["name"])
        if not items:
            continue
        L = [hdr.rstrip(), "", f"# {label}", "",
             f"{len(items)} outils au catalogue. "
             f"Généré le {date.today().isoformat()} depuis `catalog/tools.yaml`.", ""]
        for t in items:
            L.append(f"## {t['name']}")
            L.append("")
            L.append(f"- **Éditeur :** {t.get('vendor', '—')}")
            if t.get("url"):
                L.append(f"- **Site :** [{t['url']}]({t['url']})")
            for k, lbl in (("docs_url", "Documentation"), ("repo_url", "Dépôt"),
                           ("pricing_url", "Tarifs")):
                if t.get(k):
                    L.append(f"- **{lbl} :** [{t[k]}]({t[k]})")
            L.append(f"- **Statut :** {t.get('status', 'inconnu')}")
            caps = ", ".join(filter(None, [
                "BYOK" if t.get("byok") else None,
                "modèles locaux" if t.get("local_models") else None,
                "MCP" if t.get("mcp") else None,
                "gratuit" if t.get("free") else None])) or "—"
            L.append(f"- **Capacités :** {caps}")
            if t.get("serves_openai_api"):
                L.append(f"- **Endpoint local :** `{t['serves_openai_api']}`")
            for pid in t.get("plans") or []:
                pl = next((x for x in plans if x["id"] == pid), None)
                if pl:
                    u = pl.get("price_usd_month")
                    L.append(f"- **Forfait {pl['name']} :** {usd(u)}"
                             f"{'/u' if pl.get('per_seat') else ''} — "
                             f"{eur(u, fx)} HT · {eur(u, fx, vat)} TTC")
            v = t.get("verification") or {}
            if v.get("status") == "unverified":
                L.append("- **Vérification :** fiche non re-contrôlée à cette édition")
            else:
                L.append(f"- **Vérification :** {v.get('verified_on')} "
                         f"({v.get('status')})")
                if v.get("finding"):
                    L.append(f"- **Constat :** {v['finding']}")
            if t.get("note"):
                L += ["", t["note"]]
            L.append("")
        (DATA / f"{i:02d}_{cat}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        written += 1

    # Une fiche par fournisseur de modèles.
    best = collections.defaultdict(dict)
    for s_ in scores:
        if s_.get("score") is None:
            continue
        k = s_.get("model_base") or s_.get("model_version")
        b = s_["benchmark"]
        if b not in best[k] or s_["score"] > best[k][b]["score"]:
            best[k][b] = s_
    L = [hdr.rstrip(), "", "# Fournisseurs de modèles", "",
         f"{len(labs)} laboratoires suivis. "
         f"Généré le {date.today().isoformat()} depuis `catalog/`.", ""]
    for lab in labs.values():
        ms = [m for m in models if m["lab"] == lab["id"]]
        pr = [m for m in ms if (m.get("pricing") or {}).get("input_per_1m") is not None]
        L += [f"## {lab['name']}", "",
              f"- **Pays :** {lab.get('country', '—')}",
              f"- **Tarifs :** [{lab['pricing_url']}]({lab['pricing_url']})",
              f"- **Documentation :** [{lab['api_docs_url']}]({lab['api_docs_url']})",
              f"- **Modèles au catalogue :** {len(ms)} · **tarifés :** {len(pr)}", ""]
        if pr:
            L += ["| Modèle | Entrée $ | Cache $ | Sortie $ | Contexte | Relevé le |",
                  "| :-- | --: | --: | --: | --: | :-- |"]
            for m in sorted(pr, key=lambda x: x["pricing"]["input_per_1m"]):
                q = m["pricing"]
                ctx = f"{m['context_window'] // 1000}k" if m.get("context_window") else "—"
                L.append(f"| {m.get('display_name', m['id'])} | {usd(q['input_per_1m'])} | "
                         f"{usd(q.get('input_cached_per_1m'))} | {usd(q.get('output_per_1m'))} | "
                         f"{ctx} | {(q.get('source') or {}).get('verified_on', '—')} |")
            L.append("")
        mesures = [(m, best.get(m["id"], {})) for m in ms]
        mesures = [(m, b) for m, b in mesures if b]
        if mesures:
            L += ["**Meilleurs scores mesurés**", ""]
            for m, b in sorted(mesures, key=lambda kv: -len(kv[1]))[:6]:
                top = sorted(b.values(), key=lambda x: -x["score"])[:3]
                frag_ = " · ".join(f"{x['benchmark']} {x['score']:.1%}" for x in top)
                L.append(f"- `{m['id']}` — {frag_}")
            L.append("")
    (DATA / "06_fournisseurs_modeles.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return written + 1


def main() -> int:
    meta = load("_meta.yaml")
    labs = {l["id"]: l for l in load("labs.yaml").get("labs", [])}
    models = load("models.yaml").get("models", [])
    plans = load("plans.yaml").get("plans", [])
    tools = load("tools.yaml").get("tools", [])
    scores = load("scores.yaml").get("scores", [])
    bench = load("benchmarks.yaml")

    fx = meta["fx"]["usd_eur"]
    vat = meta["vat"]["rate"]
    fx_ok = meta["fx"].get("status") == "verified"
    ed = meta["audit"]

    L: list[str] = []
    A = L.append

    # ── En-tête ───────────────────────────────────────────────────────────
    A("# Tandem — guide de référence")
    A("")
    A(f"**{ed['label']}** · document généré le {date.today().isoformat()} "
      f"depuis `catalog/` · prochaine révision prévue le {ed['next_review_due']}")
    A("")
    A("> [!NOTE]")
    A("> Ce document est **généré**. Toute correction se fait dans `catalog/`, "
      "puis `python3 pipeline/build_guide.py`.")
    A("> Une modification faite ici sera écrasée à la prochaine génération.")
    A("")

    priced = [m for m in models if (m.get("pricing") or {}).get("input_per_1m") is not None]
    tools_ok = [t for t in tools if (t.get("verification") or {}).get("status") != "unverified"]
    A("## État de vérification")
    A("")
    A("| Couche | Couverture |")
    A("| :-- | :-- |")
    A(f"| Mesures de benchmark | {len(scores):,} sur {len({s['benchmark'] for s in scores})} "
      f"benchmarks |".replace(",", " "))
    A(f"| Modèles au catalogue | {len(models)} |")
    A(f"| Tarifs API relevés sur page officielle | {len(priced)} / {len(models)} |")
    A(f"| Forfaits d'abonnement relevés | {len(plans)} |")
    A(f"| Harnais re-vérifiés | {len(tools_ok)} / {len(tools)} |")
    A(f"| Taux de change USD→EUR | {fx} — "
      f"{'vérifié' if fx_ok else '**non vérifié**'} |")
    A("")
    if not fx_ok:
        A("> [!WARNING]")
        A("> Le taux de change n'est pas vérifié : **toutes les valeurs en euros de ce "
          "document en héritent**. Les montants en dollars, eux, sont relevés sur les "
          "pages officielles.")
        A("")
    A("---")
    A("")

    A(frag("01_taxonomie.md")); A(""); A("---"); A("")
    A(frag("02_facturation_france.md")); A(""); A("---"); A("")

    # ── Harnais ───────────────────────────────────────────────────────────
    A("## 3. Panorama des harnais")
    A("")
    A("La colonne *vérifié* indique si la fiche a été re-contrôlée à cette édition. "
      "Une fiche non re-contrôlée est signalée comme telle plutôt que présentée "
      "comme à jour.")
    A("")
    by_cat = collections.defaultdict(list)
    for t in tools:
        by_cat[t.get("category", "autre")].append(t)
    for cat, items in sorted(by_cat.items(), key=lambda kv: list(CAT).index(kv[0])
                             if kv[0] in CAT else 99):
        A(f"### 3.{list(CAT).index(cat) + 1 if cat in CAT else 9} {CAT.get(cat, cat)}")
        A("")
        A("| Outil | Éditeur | Capacités | Forfaits | Vérifié |")
        A("| :-- | :-- | :-- | :-- | :-- |")
        for t in sorted(items, key=lambda x: x["name"]):
            caps = ", ".join(filter(None, [
                "BYOK" if t.get("byok") else None,
                "modèles locaux" if t.get("local_models") else None,
                "MCP" if t.get("mcp") else None,
                "gratuit" if t.get("free") else None])) or "—"
            pl = ", ".join(next((p["name"] for p in plans if p["id"] == pid), pid)
                           for pid in (t.get("plans") or [])) or "—"
            v = t.get("verification") or {}
            vs = v.get("verified_on") if v.get("status") != "unverified" else "non"
            name = f"[{t['name']}]({t['url']})" if t.get("url") else t["name"]
            st = "" if t.get("status") in ("active", "unknown") else f" *({t['status']})*"
            A(f"| {name}{st} | {t.get('vendor', '—')} | {caps} | {pl} | {vs or 'non'} |")
        A("")
        for t in items:
            f_ = (t.get("verification") or {}).get("finding")
            if f_:
                A(f"> **{t['name']} —** {f_}")
                A("")
    A("---"); A("")

    # ── Forfaits ──────────────────────────────────────────────────────────
    A("## 4. Forfaits d'abonnement")
    A("")
    A(f"Montants calculés au taux de {fx} $/€ et à une TVA de {vat:.0%}. "
      "La colonne **€ HT** est ce que débite un professionnel en autoliquidation ; "
      "la colonne **€ TTC** ce que débite un particulier.")
    A("")
    A("| Éditeur | Produit | Forfait | Affiché | € HT (pro) | € TTC | Inclus | Source |")
    A("| :-- | :-- | :-- | --: | --: | --: | :-- | :-- |")
    for p in sorted(plans, key=lambda x: (x["vendor"], x.get("price_usd_month") or 0)):
        u = p.get("price_usd_month")
        seat = "/u" if p.get("per_seat") else ""
        src = (p.get("source") or {}).get("url", "")
        A(f"| {p['vendor']} | {p.get('product', '—')} | **{p['name']}** | "
          f"{usd(u)}{seat} | {eur(u, fx)} | {eur(u, fx, vat)} | "
          f"{p.get('includes', '—')} | [page]({src}) |")
    A("")
    A("---"); A("")

    # ── Tarifs API ────────────────────────────────────────────────────────
    A("## 5. Tarifs API au million de tokens")
    A("")
    A("Une ligne par modèle, triée par coût d'entrée croissant. Seuls figurent les "
      "modèles dont le tarif a été relevé sur la page officielle du fournisseur : "
      "un modèle absent de ce tableau n'est pas un modèle sans tarif, c'est un "
      "tarif non encore vérifié.")
    A("")
    A("| Fournisseur | Modèle | Rôle | Contexte | Entrée $ | Cache $ | Sortie $ | "
      "Entrée € HT | Sortie € HT | Relevé le |")
    A("| :-- | :-- | :-- | --: | --: | --: | --: | --: | --: | :-- |")
    for m in sorted(priced, key=lambda x: x["pricing"]["input_per_1m"]):
        pr = m["pricing"]
        lab = labs.get(m["lab"], {}).get("name", m["lab"])
        ctx = f"{m['context_window'] // 1000}k" if m.get("context_window") else "—"
        A(f"| {lab} | **{m.get('display_name', m['id'])}** | {m.get('role') or '—'} | {ctx} | "
          f"{usd(pr['input_per_1m'])} | {usd(pr.get('input_cached_per_1m'))} | "
          f"{usd(pr.get('output_per_1m'))} | {eur(pr['input_per_1m'], fx)} | "
          f"{eur(pr.get('output_per_1m'), fx)} | {(pr.get('source') or {}).get('verified_on', '—')} |")
    A("")
    notes = [(m.get("display_name", m["id"]), m["pricing"]) for m in priced
             if any(m["pricing"].get(k) for k in ("offpeak", "promo_note", "tier_note"))]
    if notes:
        A("**Particularités tarifaires**")
        A("")
        for n, pr in notes:
            if pr.get("offpeak"):
                o = pr["offpeak"]
                A(f"- **{n}** — heures creuses : {usd(o['input_per_1m'])} en entrée, "
                  f"{usd(o['output_per_1m'])} en sortie ({pr.get('peak_hours_utc', '')}).")
            if pr.get("promo_note"):
                A(f"- **{n}** — {pr['promo_note']} (jusqu'au {pr.get('promo_until', '?')}).")
            if pr.get("tier_note"):
                A(f"- **{n}** — {pr['tier_note']}")
        A("")
    A("---"); A("")

    # ── Benchmarks ────────────────────────────────────────────────────────
    A("## 6. Performance mesurée")
    A("")
    tracked = [b for b in bench.get("tracked", []) if b.get("track")]
    A(f"{len(tracked)} benchmarks suivis, {len(bench.get('rejected', []))} écartés "
      "(saturés, obsolètes ou mesurant de la mémorisation). Chaque rejet est "
      "documenté avec son motif dans `catalog/benchmarks.yaml`.")
    A("")

    by_b = collections.defaultdict(list)
    for s in scores:
        if s.get("score") is not None:
            by_b[s["benchmark"]].append(s)

    A("### 6.1 État de l'art par benchmark")
    A("")
    A("| Benchmark | Ce qu'il mesure | Meilleur score | Modèle | Harnais |")
    A("| :-- | :-- | --: | :-- | :-- |")
    for b in sorted(tracked, key=lambda x: (x["tier"] != "reference", x["name"])):
        rows = by_b.get(b["name"])
        if not rows:
            continue
        top = max(rows, key=lambda r: r["score"])
        unit = "min" if b["name"] == "METR Time Horizons" else ""
        val = f"{top['score']:.2f} {unit}" if unit else f"{top['score']:.1%}"
        A(f"| **{b['name']}** | {b['measures'][:74]} | {val} | "
          f"`{top.get('model_version', '—')}` | {top.get('harness') or '—'} |")
    A("")

    # Égalités statistiques : ce que le document n'a pas le droit d'affirmer.
    import math
    ties = []
    for b, rows in by_b.items():
        r = sorted([x for x in rows if x.get("stderr")], key=lambda x: -x["score"])
        if len(r) >= 2:
            gap = r[0]["score"] - r[1]["score"]
            comb = math.sqrt(r[0]["stderr"] ** 2 + r[1]["stderr"] ** 2)
            if gap < 1.96 * comb:
                ties.append((b, r[0], r[1], gap, 1.96 * comb))
    if ties:
        A("> [!IMPORTANT]")
        A("> **Égalités statistiques.** Sur les benchmarks suivants, les deux premiers "
          "ne sont pas séparés au seuil de 95 % : les classer l'un devant l'autre est "
          "une erreur de lecture.")
        A(">")
        for b, a_, b_, gap, ci in ties:
            A(f"> - **{b}** — `{a_['model_version']}` et `{b_['model_version']}` "
              f"(écart {gap:.3f}, intervalle {ci:.3f})")
        A("")

    # Coût mesuré
    cost_rows = [s for s in scores if s.get("cost_usd") and s.get("effort")]
    if cost_rows:
        A("### 6.2 Coût mesuré et effort de raisonnement")
        A("")
        A("Les suffixes `low` à `max` ne désignent pas des modèles différents mais le "
          "**budget de raisonnement** accordé au même modèle. Son effet dépasse souvent "
          "l'écart entre deux modèles concurrents, et il se paie. Le coût ci-dessous est "
          "celui **réellement mesuré pendant le run**, pas un prix au token.")
        A("")
        fam = collections.defaultdict(list)
        for s in cost_rows:
            fam[(s["benchmark"], s["model_base"])].append(s)
        order = ["minimal", "low", "medium", "high", "xhigh", "max"]
        multi = {k: v for k, v in fam.items() if len({x["effort"] for x in v}) > 1}
        # Préférer un benchmark dont le harnais est connu ET unique : c'est la
        # seule configuration où l'écart mesuré s'impute au modèle et à l'effort.
        def controle(b):
            h = {x.get("harness") for x in by_b.get(b, [])}
            return len(h - {None}) == 1 and None not in h
        cands = collections.Counter(k[0] for k in multi)
        best_b = next((b for b, _ in cands.most_common() if controle(b)),
                      cands.most_common(1)[0][0])
        if controle(best_b):
            h = next(iter({x["harness"] for x in by_b[best_b]}))
            A(f"Benchmark de référence sur cet axe : **{best_b}**, mesuré sous un "
              f"harnais unique (`{h}`) — l'écart observé s'impute donc au modèle et "
              f"à son effort, pas au harnais.")
        else:
            A(f"Benchmark de référence sur cet axe : **{best_b}**. "
              f"Le harnais n'est pas publié pour ce benchmark : les écarts ci-dessous "
              f"mêlent l'effet du modèle et celui de son environnement d'exécution.")
        A("")
        A("| Modèle | Effort le plus bas | Effort le plus haut | Gain | Surcoût |")
        A("| :-- | :-- | :-- | --: | --: |")
        for (b, m), v in sorted(multi.items(),
                                key=lambda kv: -max(x["score"] for x in kv[1])):
            if b != best_b:
                continue
            v = sorted(v, key=lambda x: order.index(x["effort"])
                       if x["effort"] in order else len(order))
            lo, hi = v[0], v[-1]
            gain = (hi["score"] - lo["score"]) * 100
            ratio = hi["cost_usd"] / lo["cost_usd"] if lo["cost_usd"] else 0
            A(f"| `{m}` | {lo['effort']} — {lo['score']:.1%} à ${lo['cost_usd']:.2f} | "
              f"{hi['effort']} — {hi['score']:.1%} à ${hi['cost_usd']:.2f} | "
              f"{gain:+.1f} pts | ×{ratio:.1f} |")
        A("")
        A("Un gain faible pour un surcoût élevé signale que l'effort supplémentaire "
          "ne s'achète plus. Certains modèles **régressent** au palier maximal.")
        A("")
    A("---"); A("")

    A(frag("03_avertissement_lecture.md"))
    A("")
    A("---")
    A("")
    A("## Sources et licences")
    A("")
    A("Données de benchmark : [Epoch AI — *Capabilities & Benchmarking*]"
      "(https://epoch.ai/benchmarks), sous licence "
      "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). "
      "Tarifs relevés sur les pages officielles des fournisseurs, dont l'URL et la "
      "date de consultation figurent dans `catalog/`. "
      "Attributions complètes : [`ATTRIBUTION.md`](./ATTRIBUTION.md).")
    A("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    nf = build_fiches(labs, models, plans, tools, scores, fx, vat)
    print(f"✓ {OUT.name} — {len(L)} lignes, {OUT.stat().st_size / 1024:.0f} Ko")
    print(f"✓ data/ — {nf} fiches régénérées")
    print(f"  {len(priced)} tarifs · {len(plans)} forfaits · {len(tools)} harnais · "
          f"{len(tracked)} benchmarks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
