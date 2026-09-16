#!/usr/bin/env python3
"""
Génère site/index.html : la vue interactive du référentiel.

Page autonome (aucune dépendance externe, données embarquées) — donc publiable
telle quelle sur GitHub Pages ou en artifact.
"""
from __future__ import annotations
import collections, json, sys
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG, SITE = ROOT / "catalog", ROOT / "site"


def load(n):
    return yaml.safe_load((CATALOG / n).read_text(encoding="utf-8")) or {}


def build_payload() -> dict:
    meta, bench = load("_meta.yaml"), load("benchmarks.yaml")
    labs = {l["id"]: l for l in load("labs.yaml").get("labs", [])}
    models = load("models.yaml").get("models", [])
    scores = load("scores.yaml").get("scores", [])

    org2lab = {"Anthropic": "anthropic", "OpenAI": "openai", "Google DeepMind": "google",
               "DeepSeek": "deepseek", "Alibaba": "alibaba", "Mistral AI": "mistral",
               "Moonshot": "moonshot", "Z.ai (Zhipu AI)": "zhipu", "xAI": "xai",
               "Meta AI": "meta", "MiniMax": "minimax"}
    # Les scores sont indexés par version Epoch, les tarifs par identifiant de
    # modèle : on projette les tarifs sur toutes les versions connues du modèle
    # pour que le croisement prix × performance puisse se faire.
    price, priced_models = {}, []
    for m in models:
        p = m.get("pricing") or {}
        if p.get("input_per_1m") is None:
            continue
        rec = {"in": p["input_per_1m"], "out": p.get("output_per_1m"),
               "cached": p.get("input_cached_per_1m"),
               "src": (p.get("source") or {}).get("url"),
               "on": (p.get("source") or {}).get("verified_on")}
        price[m["id"]] = rec
        for v in m.get("epoch_model_versions", []):
            price[v] = rec
        # Un tarif dérivé — variante d'effort, ou instantané daté rattaché par
        # `applies_to` — désigne la même référence facturée que sa base. Le
        # reprendre ici produit deux lignes au tarif identique.
        src = p.get("source") or {}
        if src.get("variant_of") or src.get("priced_as"):
            continue
        priced_models.append({
            "id": m["id"], "name": m.get("display_name") or m["id"],
            "lab": m.get("lab"), "role": m.get("role"),
            "ctx": m.get("context_window"),
            "api_id": m.get("api_model_id"),
            **rec,
            "offpeak": p.get("offpeak"), "promo": p.get("promo_note"),
            "tier": p.get("tier_note"),
        })
    priced_models.sort(key=lambda x: x["in"])

    rows = []
    for s in scores:
        if s.get("score") is None or not s.get("model_version"):
            continue
        rows.append({
            "b": s["benchmark"],
            "m": s["model_version"],
            "d": s.get("model_display") or s["model_version"],
            "o": s.get("organization") or "—",
            "l": org2lab.get(s.get("organization") or "", "autre"),
            "h": s.get("harness"),
            "mb": s.get("model_base"),
            "ef": s.get("effort"),
            "c": s.get("cost_usd"),
            "s": s["score"],
            "e": s.get("stderr"),
            "r": s.get("model_released_on"),
            "p": s.get("provenance"),
            "u": s.get("source_url"),
            "v": s.get("evidence_url"),
        })

    benches = [{"name": b["name"], "domain": b["domain"], "tier": b["tier"],
                "measures": b["measures"], "caveat": b.get("caveat"),
                "ceiling": b.get("score_ceiling"), "provenance": b["provenance"],
                "released": b.get("released_on")}
               for b in bench.get("tracked", []) if b.get("track")]

    plans = load("plans.yaml").get("plans", [])
    tools = load("tools.yaml").get("tools", [])
    fx = (meta.get("fx") or {}).get("usd_eur", 0.92)
    vat = (meta.get("vat") or {}).get("rate", 0.20)
    for pl in plans:
        u = pl.get("price_usd_month")
        if u is not None:
            pl["eur_ht"] = round(u * fx, 2)          # pro, autoliquidation
            pl["eur_ttc"] = round(u * fx * (1 + vat), 2)  # particulier, TVA FR

    return {
        "edition": meta.get("audit", {}).get("label", ""),
        "generated": date.today().isoformat(),
        "fx": meta.get("fx", {}),
        "benchmarks": benches,
        "rejected": bench.get("rejected", []),
        "labs": [{"id": v["id"], "name": v["name"], "country": v["country"],
                  "pricing_url": v["pricing_url"]} for v in labs.values()],
        "scores": rows,
        "prices": price,
        "priced_models": priced_models,
        "plans": plans,
        # Les blocs `verification` et les notes de conformité documentent le
        # travail d'audit, pas le sujet : ils restent dans le catalogue mais ne
        # sont pas embarqués dans la page.
        "tools": [{k: v for k, v in t.items() if k not in ("verification",)}
                  | ({"compliance": {k2: v2 for k2, v2 in (t.get("compliance") or {}).items()
                                     if k2 not in ("note", "status", "verified_on")}}
                     if t.get("compliance") else {})
                  for t in tools],
        "labs_full": [{"id": v["id"], "name": v["name"], "country": v["country"],
                       "pricing_url": v["pricing_url"], "docs": v.get("api_docs_url")}
                      for v in labs.values()],
        "vat": vat,
        "counts": {"labs": len(labs), "models": len(models),
                   "benchmarks": len(benches), "scores": len(rows),
                   "priced": len(priced_models), "plans": len(plans),
                   "tools": len(tools),
                   "tools_verified": sum(1 for t in tools
                       if (t.get("verification") or {}).get("status") != "unverified")},
    }


HTML = r"""<title>Tandem</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  color-scheme:light;
  --bg:#fbfcfd; --panel:#ffffff; --line:#e2e6ec; --line-strong:#c8cfd9;
  --ink:#0a0d12; --ink-2:#4c535e; --ink-3:#676e79;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4;
  --s6:#008300; --s7:#4a3aa7; --s8:#e34948;
  --grid:#edf0f4; --warn:#eda100; --bad:#e34948; --good:#1baf7a;
  --seq1:#cde2fb;--seq2:#9ec5f4;--seq3:#6da7ec;--seq4:#3987e5;--seq5:#256abf;--seq6:#184f95;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --bg:#101317; --panel:#171b21; --line:#2b323b; --line-strong:#3e4753;
  --ink:#ffffff; --ink-2:#bcc3cd; --ink-3:#a7aeb9;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
  --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --grid:#232931; --warn:#c98500; --bad:#e66767; --good:#199e70;
  --seq1:#104281;--seq2:#184f95;--seq3:#256abf;--seq4:#2a78d6;--seq5:#5598e7;--seq6:#9ec5f4;
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#101317; --panel:#171b21; --line:#2b323b; --line-strong:#3e4753;
  --ink:#ffffff; --ink-2:#bcc3cd; --ink-3:#a7aeb9;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
  --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --grid:#232931; --warn:#c98500; --bad:#e66767; --good:#199e70;
  --seq1:#104281;--seq2:#184f95;--seq3:#256abf;--seq4:#2a78d6;--seq5:#5598e7;--seq6:#9ec5f4;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
body{background:var(--bg);color:var(--ink);
 font:14px/1.55 "IBM Plex Sans",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 margin:0;padding:0 20px 72px;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto}
header{padding:38px 0 20px;border-bottom:1px solid var(--line)}
h1{font-family:"IBM Plex Serif",Georgia,serif;font-size:27px;margin:0 0 7px;
 letter-spacing:-.015em;font-weight:600;text-wrap:balance}
.sub{color:var(--ink);font-size:15px;margin:18px 0 0;line-height:1.5}
.meta{color:var(--ink-3);font-size:12.5px;margin:8px 0 0;font-variant-numeric:tabular-nums}
h2{font-family:"IBM Plex Serif",Georgia,serif;font-size:19px;margin:22px 0 4px;
 letter-spacing:-.01em;font-weight:600;text-wrap:balance}
h2 .n{color:var(--ink-3);font-weight:400;font-size:13px;margin-left:8px}
h2 .en-h{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink-3);
 text-transform:uppercase;letter-spacing:.1em;font-weight:400;margin-left:9px;
 vertical-align:middle}
.lede{color:var(--ink-2);margin:0 0 14px;font-size:13.5px}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:1px;
 background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;
 margin:26px 0 0}
.cell{background:var(--panel);padding:14px 16px}
.cell b{display:block;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:22px;
 font-weight:500;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.cell span{color:var(--ink-3);font-size:10.5px;text-transform:uppercase;letter-spacing:.075em;
 margin-top:2px;display:block}
.note{border-left:3px solid var(--warn);background:var(--panel);padding:12px 15px;
 border-radius:0 8px 8px 0;margin:18px 0;font-size:13px;color:var(--ink-2)}
.note b{color:var(--ink)}
.note.bad{border-left-color:var(--bad)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:18px;margin:14px 0}
nav.tabs{display:flex;width:100%;margin:22px 0 4px;border-bottom:1px solid var(--line)}
nav.tabs button{flex:1 1 0;background:none;border:0;border-bottom:2px solid transparent;
 color:var(--ink-3);padding:9px 6px 8px;font:inherit;cursor:pointer;text-align:center;
 display:flex;flex-direction:column;gap:1px;align-items:center;margin-bottom:-1px}
nav.tabs button .fr{font-size:14px;font-weight:500;letter-spacing:-.01em}
nav.tabs button .en{font-size:10px;text-transform:uppercase;letter-spacing:.1em;
 color:var(--ink-3);font-weight:400}
nav.tabs button:hover{color:var(--ink-2)}
nav.tabs button[aria-selected="true"]{color:var(--ink);border-bottom-color:var(--s1)}
nav.tabs button[aria-selected="true"] .fr{font-weight:600}
nav.tabs button[aria-selected="true"] .en{color:var(--s1)}
nav.tabs button:focus-visible{outline:2px solid var(--s1);outline-offset:-2px;border-radius:4px}
@media(max-width:700px){nav.tabs{flex-wrap:wrap}nav.tabs button{flex:1 1 33%}}
h3.grp{font-family:"IBM Plex Serif",Georgia,serif;font-size:15.5px;font-weight:600;
 margin:26px 0 3px;letter-spacing:-.01em}
h3.grp .c{color:var(--ink-3);font-weight:400;font-size:12px;font-family:"IBM Plex Sans",sans-serif;
 margin-left:7px}
.layer{border-left:3px solid var(--s1);padding:3px 0 3px 15px;margin:6px 0 4px;
 color:var(--ink-2);font-size:13.5px;line-height:1.5}
.ctrl{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin-bottom:16px}
/* Rangée des vues : collée à la rangée des filtres qu'elle commande. */
.ctrl:has(>.seg){margin-bottom:13px}
label.f{display:flex;flex-direction:column;gap:4px;font-size:11px;color:var(--ink-3);
 text-transform:uppercase;letter-spacing:.05em}
select{background:var(--bg);color:var(--ink);border:1px solid var(--line-strong);
 border-radius:7px;padding:6px 9px;font:inherit;font-size:13px;min-width:150px;cursor:pointer}
select:focus-visible{outline:2px solid var(--s1);outline-offset:1px}
/* Liste déroulante maison : le menu natif s'ouvre où le navigateur décide,
   sans hauteur maximale et parfois vers le haut. Ici il s'ouvre toujours vers
   le bas et défile au-delà de six options. */
.cb{position:relative}
.cb>select{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.cb-b{display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;
 background:var(--bg);color:var(--ink);border:1px solid var(--line-strong);border-radius:7px;
 padding:6px 9px;font:inherit;font-size:13px;min-width:150px;cursor:pointer;
 text-align:left;white-space:nowrap}
.cb-b::after{content:"";flex:none;width:0;height:0;margin-top:2px;
 border:4px solid transparent;border-top-color:var(--ink-3)}
.cb-b:hover{border-color:var(--s1)}
.cb-b:focus-visible{outline:2px solid var(--s1);outline-offset:1px}
.cb[data-open] .cb-b{border-color:var(--s1)}
.cb[data-open] .cb-b::after{transform:rotate(180deg);margin-top:-2px}
.cb-l{position:absolute;top:calc(100% + 4px);left:0;min-width:100%;z-index:40;
 background:var(--panel);border:1px solid var(--line-strong);border-radius:8px;padding:4px;
 box-shadow:0 12px 28px rgba(0,0,0,.22);
 max-height:186px;overflow-y:auto;overscroll-behavior:contain}
.cb-o{display:block;width:100%;background:none;border:0;border-radius:5px;
 padding:6px 9px;font:inherit;font-size:13px;color:var(--ink-2);
 cursor:pointer;text-align:left;white-space:nowrap}
.cb-o:hover,.cb-o[data-act]{background:var(--grid);color:var(--ink)}
.cb-o[aria-selected="true"]{color:var(--ink);font-weight:600}
.seg{display:flex;gap:7px;flex-wrap:wrap;background:none;border:0;padding:0}
#har-cat,#pas-cat,#met-cat{margin:18px 0 10px}
.seg button{background:var(--panel);border:1px solid var(--line-strong);border-radius:999px;
 color:var(--ink-2);padding:7px 15px;font:inherit;font-size:13px;cursor:pointer;
 white-space:nowrap;transition:border-color .12s,color .12s}
.seg button:hover{border-color:var(--s1);color:var(--ink)}
.seg button[aria-pressed="true"]{background:var(--s1);border-color:var(--s1);color:#fff}
.seg button:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.seg button:disabled{opacity:.4;cursor:not-allowed;border-style:dashed}
.seg button:disabled:hover{border-color:var(--line-strong);color:var(--ink-2)}
.chart{width:100%;overflow-x:auto}
svg{display:block;max-width:100%;height:auto;font:inherit}
.gl{stroke:var(--grid);stroke-width:1}
.ax{fill:var(--ink-3);font-size:11px;font-family:"IBM Plex Mono",ui-monospace,monospace}
.lbl{fill:var(--ink);font-size:11.5px}
.val{fill:var(--ink-2);font-size:11px;font-family:"IBM Plex Mono",ui-monospace,monospace;
 font-variant-numeric:tabular-nums}
.bar{rx:4}
.tip{position:fixed;pointer-events:none;z-index:60;background:var(--panel);
 border:1px solid var(--line-strong);border-radius:8px;padding:9px 11px;font-size:12px;
 box-shadow:0 8px 26px rgba(0,0,0,.17);max-width:310px;opacity:0;transition:opacity .1s}
.tip b{display:block;margin-bottom:3px}
.tip i{color:var(--ink-3);font-style:normal;display:block;margin-top:4px;font-size:11px}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin-top:6px}
th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line)}
th{color:var(--ink-3);font-weight:500;font-size:11px;text-transform:uppercase;letter-spacing:.05em;
 position:sticky;top:0;background:var(--panel)}
/* En-tête et valeur d'une colonne chiffrée partagent le même axe : centrés
   tous les deux, le titre tombe au-dessus de ses chiffres. */
th.n,td.n{text-align:center}
td.n{font-family:"IBM Plex Mono",ui-monospace,monospace;
 font-variant-numeric:tabular-nums}
.tw{max-height:420px;overflow:auto;border:1px solid var(--line);border-radius:9px}
details{margin-top:12px}
summary{cursor:pointer;color:var(--ink-2);font-size:13px;padding:5px 0}
summary:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.tag{display:inline-block;padding:1px 7px;border-radius:99px;font-size:10.5px;
 border:1px solid var(--line-strong);color:var(--ink-2);white-space:nowrap}
.tag.ref{border-color:var(--s1);color:var(--s1)}
.bl{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));gap:11px;margin-top:12px}
.bc{border:1px solid var(--line);border-radius:9px;padding:13px 15px;background:var(--panel)}
.bc h3{margin:0 0 3px;font-size:13.5px;font-weight:600}
.bc p{margin:5px 0 0;font-size:12.5px;color:var(--ink-2)}
.bc .cv{color:var(--warn);font-size:12px;margin-top:7px;display:block}
footer{margin-top:52px;padding-top:18px;border-top:1px solid var(--line);
 color:var(--ink-3);font-size:12px}
a{color:var(--s1)}
.empty{padding:40px 20px;text-align:center;color:var(--ink-3);font-size:13px;
 border:1px dashed var(--line-strong);border-radius:9px}
.empty p{max-width:62ch;margin:0 auto;line-height:1.6}
.empty p+p{margin-top:10px;color:var(--ink-2)}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media(max-width:640px){.ctrl{flex-direction:column;align-items:stretch}
 select,.cb,.cb-b{width:100%}}
</style>

<div class="wrap">
<header>
  <h1>Modèles et harnais de développement IA</h1>
  <p class="meta" id="meta"></p>
</header>

<div class="strip" id="strip"></div>

<p class="sub"><b>Comparer la performance, le coût réel et les tarifs des modèles de
   fondation et des outils qui les exécutent</b> — sur des mesures sourcées, datées
   et reproductibles.</p>

<nav class="tabs" id="nav" role="tablist" aria-label="Sections">
  <button data-s="mesures" role="tab" aria-selected="true">
    <span class="fr">Benchmarks</span><span class="en">performance</span></button>
  <button data-s="modeles" role="tab" aria-selected="false">
    <span class="fr">Tarifs</span><span class="en">pricing</span></button>
  <button data-s="harnais" role="tab" aria-selected="false">
    <span class="fr">Harnais</span><span class="en">harness</span></button>
  <button data-s="passerelles" role="tab" aria-selected="false">
    <span class="fr">Passerelles</span><span class="en">gateways</span></button>
  <button data-s="methode" role="tab" aria-selected="false">
    <span class="fr">Méthode</span><span class="en">methodology</span></button>
</nav>

<div id="alerts"></div>

<section id="s-mesures" role="tabpanel">
  <h2>Performance mesurée</h2>
  <p class="lede">Les barres d'erreur affichent l'intervalle de confiance à 95 % : quand deux
  barres se chevauchent, l'écart n'est <b>pas</b> significatif et les deux modèles sont à
  égalité. Chaque point renvoie à sa source et à la date de sa mesure.</p>

  <div class="panel">
    <div class="ctrl">
      <div class="seg" id="kind" role="group" aria-label="Type de graphique">
        <button data-k="rank" aria-pressed="true">Classement</button>
        <button data-k="frontier" aria-pressed="false">Coût × performance</button>
        <button data-k="budget" aria-pressed="false">Sous contrainte de budget</button>
        <button data-k="harness" aria-pressed="false">Effet du harnais</button>
        <button data-k="time" aria-pressed="false">Progression</button>
        <button data-k="cover" aria-pressed="false">Couverture</button>
        <button data-k="api" aria-pressed="false">Tarifs API</button>
        <button data-k="plans" aria-pressed="false">Forfaits</button>
      </div>
    </div>
    <div class="ctrl">
      <label class="f">Benchmark<select id="bench"></select></label>
      <label class="f">Fournisseur / provider<select id="lab"><option value="">Tous</option></select></label>
      <label class="f">Effort / reasoning<select id="eff">
        <option value="">Tous</option><option value="low">low</option>
        <option value="medium">medium</option><option value="high">high</option>
        <option value="xhigh">xhigh</option><option value="max">max</option></select></label>
      <label class="f" id="budwrap" hidden>Budget max / tâche<select id="bud">
        <option value="0.25">0,25 $</option><option value="0.5">0,50 $</option>
        <option value="1">1 $</option><option value="2" selected>2 $</option>
        <option value="5">5 $</option><option value="10">10 $</option>
        <option value="25">25 $</option></select></label>
      <label class="f">Affichage<select id="top">
        <option value="15">15 premiers</option><option value="25">25 premiers</option>
        <option value="0">Tout</option></select></label>
    </div>
    <div class="chart" id="chart"></div>
    <div id="caveat"></div>
    <details><summary>Voir les données sous forme de tableau</summary>
      <div class="tw"><table id="tbl"></table></div>
    </details>
  </div>
</section>

<section id="s-modeles" role="tabpanel" hidden>
  <h2>Tarifs des modèles <span class="en-h">pricing</span></h2>
  <p class="layer"><b>Couche 3 — les modèles de fondation</b> <i>(models)</i> et leur coût
  d'accès à l'API, au million de tokens. Seuls figurent les tarifs relevés sur la page
  officielle du fournisseur <i>(provider)</i>. Un modèle absent de cette page n'est pas
  gratuit : son tarif n'a simplement pas encore été vérifié.</p>
  <div id="mod"></div>
</section>

<section id="s-harnais" role="tabpanel" hidden>
  <h2>Harnais <span class="en-h">harness</span></h2>
  <p class="layer"><b>Couche 1 — l'interface développeur.</b> Le <b>harnais</b> est le logiciel
  avec lequel on code et qui pilote le modèle : il lit le dépôt, construit le contexte, décide
  quels outils appeler et enchaîne les étapes. Deux harnais donnant le même modèle n'obtiennent
  pas le même résultat — sur Terminal-Bench, l'écart entre harnais dépasse souvent l'écart entre
  deux modèles concurrents.</p>
  <div class="seg" id="har-cat" role="group" aria-label="Catégories de harnais"></div>
  <div id="har"></div>
</section>

<section id="s-passerelles" role="tabpanel" hidden>
  <h2>Passerelles <span class="en-h">gateways</span></h2>
  <p class="layer"><b>Couche 2 — le routage et le service.</b> Une <b>passerelle</b> n'écrit
  jamais de code : c'est le tuyau entre le harnais et le modèle. Elle prend la requête du
  harnais et la route, soit vers plusieurs laboratoires derrière une clé d'API unique
  <i>(agrégateur)</i>, soit vers un modèle tournant sur votre propre machine
  <i>(serveur local)</i>. Changer de passerelle ne change pas la qualité du code produit :
  cela change le prix, la latence et qui voit vos données.</p>
  <div class="seg" id="pas-cat" role="group" aria-label="Catégories de passerelles"></div>
  <div id="pas"></div>
</section>

<section id="s-methode" role="tabpanel" hidden>
  <div class="seg" id="met-cat" role="group" aria-label="Sous-sections">
    <button data-m="regles" aria-pressed="true">Les six règles</button>
    <button data-m="bench" aria-pressed="false">Benchmarks retenus</button>
    <button data-m="etat" aria-pressed="false">État du référentiel</button>
  </div>

  <div id="m-regles">
    <p class="layer">Ce que ce référentiel s'autorise à affirmer, et ce qu'il refuse.</p>
    <div class="bl" id="meth"></div>
  </div>

  <div id="m-bench" hidden>
    <p class="layer">Sélection raisonnée<span id="bn"></span>. Un benchmark saturé ou remplacé
    est écarté explicitement : documenter un rejet évite d'avoir à reposer la question à chaque
    édition.</p>
    <div class="bl" id="blist"></div>
    <details><summary id="rj">Benchmarks écartés</summary><div class="bl" id="rlist"></div></details>
  </div>

  <div id="m-etat" hidden>
    <p class="layer">Ce que la vérification couvre à ce jour, et ce qu'elle ne couvre pas encore.</p>
    <div id="alerts"></div>
  </div>
</section>

<footer id="foot"></footer>
</div>
<div class="tip" id="tip" role="status"></div>

<script id="payload" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('payload').textContent);
const $=s=>document.querySelector(s), tip=$('#tip');
// ── listes déroulantes ─────────────────────────────────────────────────────
// Le menu d'un <select> natif est dessiné par le navigateur : ni sa hauteur ni
// son sens d'ouverture ne sont adressables. Sur une page où certains menus
// comptent vingt entrées, il s'ouvrait vers le haut ou vers le bas selon la
// place, sans jamais défiler. On l'habille donc d'un combobox — le <select>
// reste dans le document et garde la valeur : tout le reste du code continue
// de le lire et d'écouter son événement `change`.
const jauge=document.createElement('canvas').getContext('2d');
function habiller(sel){
  if(!sel||sel.dataset.cb)return;
  sel.dataset.cb='1';
  const cb=document.createElement('div');cb.className='cb';
  sel.parentElement.insertBefore(cb,sel);cb.append(sel);
  const btn=document.createElement('button');
  btn.type='button';btn.className='cb-b';
  btn.setAttribute('role','combobox');
  btn.setAttribute('aria-haspopup','listbox');
  btn.setAttribute('aria-expanded','false');
  const nom=document.createElement('span');btn.append(nom);
  const list=document.createElement('div');
  list.className='cb-l';list.setAttribute('role','listbox');list.hidden=true;
  list.id='cbl-'+sel.id;btn.setAttribute('aria-controls',list.id);
  cb.append(btn,list);
  let actif=-1;

  const libelle=()=>{nom.textContent=sel.options[sel.selectedIndex]?.textContent||'';};
  // Largeur calée sur l'option la plus longue : sans cela le bouton change de
  // taille à chaque sélection et fait sauter toute la rangée.
  const caler=()=>{
    jauge.font=getComputedStyle(btn).font||'13px sans-serif';
    const w=Math.max(0,...[...sel.options].map(o=>jauge.measureText(o.textContent).width));
    btn.style.minWidth=Math.min(320,Math.ceil(w)+48)+'px';
  };
  const peupler=()=>{
    list.textContent='';
    [...sel.options].forEach((o,i)=>{
      const b=document.createElement('button');
      b.type='button';b.className='cb-o';b.textContent=o.textContent;
      b.setAttribute('role','option');
      b.setAttribute('aria-selected',String(i===sel.selectedIndex));
      b.addEventListener('click',()=>choisir(i));
      list.append(b);});
    libelle();caler();
  };
  const marquer=()=>[...list.children].forEach((c,i)=>{
    if(i===actif){c.setAttribute('data-act','');c.scrollIntoView({block:'nearest'});}
    else c.removeAttribute('data-act');});
  const ouvrir=()=>{
    peupler();list.hidden=false;cb.setAttribute('data-open','');
    btn.setAttribute('aria-expanded','true');
    actif=sel.selectedIndex;marquer();};
  const fermer=()=>{
    list.hidden=true;cb.removeAttribute('data-open');
    btn.setAttribute('aria-expanded','false');actif=-1;};
  const choisir=i=>{
    if(sel.selectedIndex!==i){
      sel.selectedIndex=i;
      sel.dispatchEvent(new Event('change',{bubbles:true}));}
    peupler();fermer();btn.focus();};
  const bouger=d=>{
    if(list.hidden){ouvrir();return;}
    actif=Math.max(0,Math.min(list.children.length-1,actif+d));marquer();};

  btn.addEventListener('click',()=>list.hidden?ouvrir():fermer());
  btn.addEventListener('keydown',e=>{
    const k=e.key;
    if(k==='ArrowDown'){e.preventDefault();bouger(1);}
    else if(k==='ArrowUp'){e.preventDefault();bouger(-1);}
    else if(k==='Home'&&!list.hidden){e.preventDefault();actif=0;marquer();}
    else if(k==='End'&&!list.hidden){e.preventDefault();actif=list.children.length-1;marquer();}
    else if(k==='Enter'||k===' '){
      e.preventDefault();
      if(list.hidden)ouvrir();else if(actif>=0)choisir(actif);}
    else if(k==='Escape'&&!list.hidden){e.preventDefault();fermer();}
    else if(k==='Tab')fermer();});
  document.addEventListener('click',e=>{if(!cb.contains(e.target))fermer();});
  // Une valeur posée par le code doit se voir sur le bouton.
  sel.addEventListener('change',libelle);
  peupler();
}

const LABC={anthropic:'--s2',openai:'--s3',google:'--s1',deepseek:'--s7',alibaba:'--s4',
 mistral:'--s5',moonshot:'--s8',zhipu:'--s6',xai:'--ink-2',meta:'--s1',minimax:'--s3',autre:'--ink-3'};
const cv=v=>getComputedStyle(document.documentElement).getPropertyValue(v)||'#888';
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pct=(v,u)=>u==='minutes'?v.toFixed(2):(v*100).toFixed(1)+'%';
let K='rank';

// ── bandeau ────────────────────────────────────────────────────────────────
$('#meta').textContent=`${D.edition} · données arrêtées au ${D.generated}`;
const C=D.counts;
$('#strip').innerHTML=[
 [C.scores.toLocaleString('fr-FR'),'mesures sourcées'],
 [C.models,'modèles'],
 [C.labs,'fournisseurs'],
 [D.tools.filter(t=>t.layer===1).length,'harnais'],
 [D.tools.filter(t=>t.layer===2).length,'passerelles'],
 [C.benchmarks,'benchmarks'],
 [C.priced,'tarifs vérifiés'],
 [C.plans,'forfaits'],
].map(([v,k])=>`<div class="cell"><b>${v}</b><span>${k}</span></div>`).join('');

const al=[];
// N'alerter que sur ce qui rend un chiffre INEXPLOITABLE. L'état d'avancement
// du relevé regarde celui qui tient le catalogue, pas celui qui le lit.
if(C.priced===0)al.push(['bad','Aucun tarif vérifié.',
 'Les tarifs du catalogue sont vides et marqués <code>unverified</code> : ils doivent être relevés sur la page /pricing officielle de chaque fournisseur avant toute publication chiffrée. Le graphique « Prix × performance » reste vide jusque-là.']);
if(D.fx&&D.fx.status!=='verified')al.push(['','Taux de change non vérifié.',
 'Toute conversion en euros hérite de cette incertitude.']);
$('#alerts').innerHTML=al.map(([c,t,b])=>
 `<div class="note ${c}"><b>${t}</b> ${b}</div>`).join('');

// ── sélecteurs ─────────────────────────────────────────────────────────────
const bsel=$('#bench');
D.benchmarks.forEach(b=>bsel.add(new Option(b.name,b.name)));
bsel.value=D.benchmarks.find(b=>b.name==='SWE-Bench verified')?'SWE-Bench verified':D.benchmarks[0]?.name;
const lsel=$('#lab');
[...new Set(D.scores.map(s=>s.o))].sort().forEach(o=>lsel.add(new Option(o,o)));
['#bench','#lab','#eff','#bud','#top'].forEach(q=>habiller($(q)));

// ── utilitaires ────────────────────────────────────────────────────────────
const cur=()=>D.benchmarks.find(b=>b.name===bsel.value)||{};
function rows(){
  let r=D.scores.filter(s=>s.b===bsel.value);
  if(lsel.value)r=r.filter(s=>s.o===lsel.value);
  const e=$('#eff').value;
  if(e)r=r.filter(s=>s.ef===e);
  return r;
}
// Un modèle peut avoir plusieurs runs : on garde le meilleur, en mémorisant combien.
function best(r){
  const m=new Map();
  r.forEach(s=>{const k=s.m+'|'+(s.h||'');const p=m.get(k);
    if(!p||s.s>p.s)m.set(k,{...s,runs:(p?.runs||0)+1});else p.runs++;});
  return [...m.values()].sort((a,b)=>b.s-a.s);
}
function show(e,html){tip.innerHTML=html;tip.style.opacity='1';
  const r=tip.getBoundingClientRect();
  tip.style.left=Math.min(e.clientX+14,innerWidth-r.width-10)+'px';
  tip.style.top=Math.max(8,e.clientY-r.height-12)+'px';}
const hide=()=>tip.style.opacity='0';
function wire(el,html){el.style.cursor='pointer';
  el.addEventListener('mousemove',e=>show(e,html));el.addEventListener('mouseleave',hide);
  el.setAttribute('tabindex','0');el.setAttribute('role','img');
  el.addEventListener('focus',e=>show({clientX:el.getBoundingClientRect().left+40,
    clientY:el.getBoundingClientRect().top+40},html));el.addEventListener('blur',hide);}
// ── échelle logarithmique ──────────────────────────────────────────────────
// Un prix ne se lit pas sur une échelle linéaire : entre 0,03 $ et 30 $ il y a
// trois décades, et tout le bas de gamme se retrouve collé à l'axe.
function decades(lo,hi){
  const out=[];
  for(let e=Math.floor(lo);e<=Math.ceil(hi);e++)
    for(const m of [1,2,5]){const v=m*Math.pow(10,e);
      if(Math.log10(v)>=lo&&Math.log10(v)<=hi)out.push(v);}
  return out;
}
const money=v=>'$'+(v<1?v.toFixed(2):v.toFixed(0));
const NS='http://www.w3.org/2000/svg';
const mk=(t,a={})=>{const e=document.createElementNS(NS,t);
  for(const k in a)e.setAttribute(k,a[k]);return e;};

// ── graphiques ─────────────────────────────────────────────────────────────
function rank(){
  const b=cur(),unit=b.name==='METR Time Horizons'?'minutes':'fraction';
  let r=best(rows()); const n=+$('#top').value; if(n)r=r.slice(0,n);
  if(!r.length)return empty('Aucune mesure pour ce filtre.');
  const W=940,L=290,R=78,BH=25,H=r.length*BH+52,max=Math.max(...r.map(x=>x.s+(x.e||0)))*1.06;
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':`Classement sur ${b.name}`});
  const x=v=>L+v/max*(W-L-R);
  for(let i=0;i<=4;i++){const v=max*i/4;
    sv.append(mk('line',{x1:x(v),x2:x(v),y1:30,y2:H-20,class:'gl'}));
    const t=mk('text',{x:x(v),y:22,'text-anchor':'middle',class:'ax'});
    t.textContent=unit==='minutes'?v.toFixed(1):(v*100).toFixed(0)+'%';sv.append(t);}
  // Le meilleur score et son IC95 : tout ce qui chevauche n'est pas séparable.
  const t0=r[0], band=t0.e?t0.s-1.96*t0.e:null;
  if(band!==null){sv.append(mk('rect',{x:x(band),y:30,width:x(t0.s)-x(band),height:H-50,
    fill:cv('--s1'),opacity:.07}));
   const tt=mk('text',{x:x(band)+3,y:H-6,class:'ax'});
   tt.textContent='◂ égalité statistique avec le 1ᵉʳ';sv.append(tt);}
  r.forEach((s,i)=>{const y=34+i*BH,c=cv(LABC[s.l]||'--ink-3');
    const g=mk('g');
    const lb=mk('text',{x:L-9,y:y+13,'text-anchor':'end',class:'lbl'});
    lb.textContent=(s.d||s.m).slice(0,36);g.append(lb);
    if(s.ef){  // l'effort est une variable de décision, pas un détail de nommage
      const eb=mk('text',{x:L+4,y:y+14,class:'ax','font-size':'9.5'});
      eb.textContent=s.ef;eb.setAttribute('fill',cv('--panel'));
      const bw=s.ef.length*6+8;
      g.append(mk('rect',{x:L+2,y:y+4,width:bw,height:13,rx:3,
        fill:cv('--ink-2'),opacity:.9}));
      eb.setAttribute('x',L+6);g.append(eb);}
    g.append(mk('rect',{x:L,y:y+3,width:Math.max(2,x(s.s)-L),height:15,class:'bar',fill:c}));
    if(s.e){const a=x(s.s-1.96*s.e),z=x(s.s+1.96*s.e);
      g.append(mk('line',{x1:a,x2:z,y1:y+10.5,y2:y+10.5,stroke:cv('--ink-2'),'stroke-width':1.5}));
      [a,z].forEach(p=>g.append(mk('line',{x1:p,x2:p,y1:y+6,y2:y+15,
        stroke:cv('--ink-2'),'stroke-width':1.5})));}
    const vt=mk('text',{x:W-R+7,y:y+14,class:'val'});vt.textContent=pct(s.s,unit);g.append(vt);
    wire(g,`<b>${esc(s.d||s.m)}</b>${esc(s.o)}<br>${pct(s.s,unit)}`+
      (s.e?` ± ${(1.96*s.e*100).toFixed(1)} pts (IC95)`:'')+
      (s.h?`<br>harnais : <b>${esc(s.h)}</b>`:'')+
      `<i>provenance : ${esc(s.p)}${s.r?' · modèle publié le '+esc(s.r):''}`+
      `${s.v?' · logs disponibles':''}</i>`);
    sv.append(g);});
  render(sv,r,unit);
}

function harness(){
  // Même modèle, harnais différents : l'écart mesure l'effet du harnais.
  const r=rows().filter(s=>s.h);
  if(!r.length){
    // Dire lesquels le publient vaut mieux que de laisser un cadre vide.
    const ok=[...new Set(D.scores.filter(s=>s.h).map(s=>s.b))].sort();
    return empty('Ce benchmark ne nomme pas l\'outil utilisé pour lancer les modèles : '+
      'l\'écart entre outils n\'y est donc pas mesurable.'+
      (ok.length?'\n\nCeux qui le publient : '+ok.join(', ')+'.':''));}
  const by=new Map();
  r.forEach(s=>{if(!by.has(s.m))by.set(s.m,[]);by.get(s.m).push(s);});
  let g=[...by.entries()].filter(([,v])=>v.length>1)
    .map(([m,v])=>({m,d:v[0].d,o:v[0].o,l:v[0].l,v:v.sort((a,b)=>b.s-a.s)}))
    .sort((a,b)=>(b.v[0].s-b.v.at(-1).s)-(a.v[0].s-a.v.at(-1).s));
  const n=+$('#top').value; if(n)g=g.slice(0,n);
  if(!g.length)return empty('Aucun modèle mesuré sous plusieurs harnais ici.');
  const W=940,L=290,R=78,RH=27,H=g.length*RH+52;
  const max=Math.max(...r.map(s=>s.s))*1.06;
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Écart de score selon le harnais'});
  const x=v=>L+v/max*(W-L-R);
  for(let i=0;i<=4;i++){const v=max*i/4;
    sv.append(mk('line',{x1:x(v),x2:x(v),y1:30,y2:H-20,class:'gl'}));
    const t=mk('text',{x:x(v),y:22,'text-anchor':'middle',class:'ax'});
    t.textContent=(v*100).toFixed(0)+'%';sv.append(t);}
  g.forEach((row,i)=>{const y=34+i*RH,c=cv(LABC[row.l]||'--ink-3'),
    hi=row.v[0],lo=row.v.at(-1),gap=hi.s-lo.s;
    const gr=mk('g');
    const lb=mk('text',{x:L-9,y:y+14,'text-anchor':'end',class:'lbl'});
    lb.textContent=(row.d||row.m).slice(0,42);gr.append(lb);
    gr.append(mk('line',{x1:x(lo.s),x2:x(hi.s),y1:y+11,y2:y+11,
      stroke:c,'stroke-width':2,opacity:.45}));
    row.v.forEach(s=>gr.append(mk('circle',{cx:x(s.s),cy:y+11,r:4.5,fill:c,
      stroke:cv('--panel'),'stroke-width':2})));
    const vt=mk('text',{x:W-R+7,y:y+15,class:'val'});
    vt.textContent='+'+(gap*100).toFixed(1)+' pts';gr.append(vt);
    wire(gr,`<b>${esc(row.d||row.m)}</b>${row.v.length} harnais mesurés<br>`+
      `meilleur : <b>${esc(hi.h)}</b> ${pct(hi.s)}<br>`+
      `moins bon : <b>${esc(lo.h)}</b> ${pct(lo.s)}`+
      `<i>Le choix du harnais vaut ${(gap*100).toFixed(1)} points sur ce modèle.</i>`);
    sv.append(gr);});
  render(sv,r,'fraction');
}

function time(){
  const r=best(rows()).filter(s=>s.r);
  if(r.length<2)return empty('Pas assez de dates de publication.');
  const W=940,H=430,L=58,B=46,T=26,R=22;
  const ds=r.map(s=>+new Date(s.r)),mn=Math.min(...ds),mx=Math.max(...ds);
  const my=Math.max(...r.map(s=>s.s))*1.06;
  const x=d=>L+(+new Date(d)-mn)/((mx-mn)||1)*(W-L-R);
  const y=v=>H-B-v/my*(H-B-T);
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Progression des scores dans le temps'});
  for(let i=0;i<=4;i++){const v=my*i/4;
    sv.append(mk('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),class:'gl'}));
    const t=mk('text',{x:L-8,y:y(v)+4,'text-anchor':'end',class:'ax'});
    t.textContent=(v*100).toFixed(0)+'%';sv.append(t);}
  const yr=new Set();
  r.forEach(s=>{const d=new Date(s.r),k=d.getFullYear()+'-'+(d.getMonth()<6?'S1':'S2');
    if(yr.has(k))return;yr.add(k);
    const t=mk('text',{x:x(s.r),y:H-B+17,'text-anchor':'middle',class:'ax'});
    t.textContent=k;sv.append(t);});
  // Front de progression : meilleur score atteint à chaque date.
  let bs=0;const front=[...r].sort((a,b)=>+new Date(a.r)-+new Date(b.r))
    .filter(s=>{if(s.s>bs){bs=s.s;return true;}return false;});
  if(front.length>1){const d=front.map(s=>`${x(s.r)},${y(s.s)}`).join(' L');
    sv.append(mk('path',{d:'M'+d,fill:'none',stroke:cv('--ink-3'),
      'stroke-width':1.5,'stroke-dasharray':'4 3',opacity:.6}));}
  r.forEach(s=>{const c=cv(LABC[s.l]||'--ink-3');
    const g=mk('g');
    g.append(mk('circle',{cx:x(s.r),cy:y(s.s),r:5,fill:c,
      stroke:cv('--panel'),'stroke-width':2}));
    wire(g,`<b>${esc(s.d||s.m)}</b>${esc(s.o)}<br>${pct(s.s)} — publié le ${esc(s.r)}`);
    sv.append(g);});
  legend(sv,r,W);
  render(sv,r,'fraction');
}

function cover(){
  // La matrice des trous : ce qui n'a PAS été mesuré compte autant.
  let ms=[...new Set(D.scores.map(s=>s.m))];
  if(lsel.value)ms=ms.filter(m=>D.scores.some(s=>s.m===m&&s.o===lsel.value));
  const cnt=new Map();
  D.scores.forEach(s=>cnt.set(s.m,(cnt.get(s.m)||0)+1));
  ms.sort((a,b)=>cnt.get(b)-cnt.get(a));
  const n=+$('#top').value; if(n)ms=ms.slice(0,n);
  const bs=D.benchmarks.map(b=>b.name);
  if(!ms.length)return empty('Aucun modèle pour ce filtre.');

  // Regroupement par fournisseur : comparer deux générations d'un même
  // laboratoire n'a de sens que si elles se suivent à l'écran.
  const info=new Map();
  D.scores.forEach(s=>{if(!info.has(s.m))info.set(s.m,s);});
  const parO=new Map();
  ms.forEach(m=>{const o=info.get(m)?.o||'—';
    if(!parO.has(o))parO.set(o,[]);parO.get(o).push(m);});
  const grp=[...parO.entries()]
    .map(([o,v])=>({o,v,tot:v.reduce((a,m)=>a+cnt.get(m),0)}))
    .sort((a,b)=>b.tot-a.tot);
  const ordre=grp.flatMap(g=>g.v);

  const GUT=118,CW=40,L=GUT+212,T=118,RH=23,GAP=9,
        W=L+bs.length*CW+24,
        H=T+ordre.length*RH+grp.length*GAP+18;
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Couverture des benchmarks par modèle, groupée par fournisseur'});
  // Même encre que les noms de lignes : pivoté et petit, ce texte a besoin du
  // contraste maximal pour rester lisible.
  bs.forEach((b,j)=>{const t=mk('text',{x:L+j*CW+CW/2,y:T-9,class:'lbl','font-size':'11',
    transform:`rotate(-52 ${L+j*CW+CW/2} ${T-9})`,'text-anchor':'start'});
    t.textContent=b.length>17?b.slice(0,16)+'…':b;sv.append(t);});
  const mp=new Map();
  D.scores.forEach(s=>{const k=s.m+'|'+s.b;const p=mp.get(k);
    if(!p||s.s>p.s)mp.set(k,s);});

  // Position verticale de chaque modèle, décalée d'un cran par groupe.
  const posY=new Map();
  let k=0;
  grp.forEach((g,gi)=>{
    const y0=T+k*RH+gi*GAP;
    g.v.forEach((m,j)=>posY.set(m,y0+j*RH));
    k+=g.v.length;
    const y1=y0+g.v.length*RH-4,xb=GUT-10;
    // Crochet : il tient ensemble les modèles d'un même laboratoire. Neutre —
    // la couleur est déjà prise par l'intensité des cases.
    sv.append(mk('path',{d:`M${xb+6},${y0+2} H${xb} V${y1} H${xb+6}`,
      fill:'none',stroke:cv('--line-strong'),'stroke-width':1.5}));
    const t=mk('text',{x:8,y:(y0+y1)/2+4,class:'lbl','font-size':'11','font-weight':'600'});
    t.textContent=g.o.length>15?g.o.slice(0,14)+'…':g.o;sv.append(t);});

  ordre.forEach(m=>{const y=posY.get(m),row=info.get(m);
    const lb=mk('text',{x:L-9,y:y+15,'text-anchor':'end',class:'lbl'});
    lb.textContent=(row?.d||m).slice(0,32);sv.append(lb);
    bs.forEach((b,j)=>{const s=mp.get(m+'|'+b),X=L+j*CW;
      const g=mk('g');
      if(!s){g.append(mk('rect',{x:X+2,y:y+2,width:CW-4,height:RH-4,rx:4,
        fill:'none',stroke:cv('--line'),'stroke-width':1,'stroke-dasharray':'2 2'}));
        wire(g,`<b>${esc(row?.d||m)}</b>${esc(b)}<i>Non mesuré — aucune donnée publiée.</i>`);}
      else{const st=Math.min(5,Math.max(0,Math.floor(s.s*6)));
        g.append(mk('rect',{x:X+2,y:y+2,width:CW-4,height:RH-4,rx:4,
          fill:cv('--seq'+(st+1))}));
        const t=mk('text',{x:X+CW/2,y:y+16,'text-anchor':'middle',
          fill:st>=3?'#fff':cv('--ink'),'font-size':'10',
          style:'font-variant-numeric:tabular-nums'});
        t.textContent=(s.s*100).toFixed(0);g.append(t);
        wire(g,`<b>${esc(row?.d||m)}</b>${esc(b)} — ${pct(s.s)}`+
          (s.h?`<br>harnais : ${esc(s.h)}`:'')+`<i>provenance : ${esc(s.p)}</i>`);}
      sv.append(g);});});
  render(sv,[],'fraction');
}

function price(){
  if(!Object.keys(D.prices).length)
    return empty('Aucun tarif vérifié dans le catalogue. '+
     'Ce graphique croise le coût au million de tokens avec la performance — '+
     'il s\'activera dès que les tarifs auront été relevés sur les pages officielles '+
     'et validés par pipeline/validate.py.');
  // Les tarifs s'étalent sur trois décades — de 0,03 $ à 30 $ le million. Une
  // échelle linéaire écrase tout le bas de gamme contre l'axe : elle est log.
  let all=best(rows()).filter(s=>D.prices[s.m]);
  const n=+$('#top').value; if(n)all=all.slice(0,n);   // le sélecteur d'affichage vaut ici aussi
  const r=all.filter(s=>D.prices[s.m].in>0);
  const gratuits=all.length-r.length;
  if(!r.length)return empty('Aucun modèle tarifé pour ce benchmark.');
  const W=940,H=470,L=58,B=52,T=34,R=178;
  const ps=r.map(s=>D.prices[s.m].in);
  const lo=Math.log10(Math.min(...ps)*0.7),hi=Math.log10(Math.max(...ps)*1.4);
  // Cadrage sur la plage réellement occupée : partir de zéro laissait la moitié
  // du graphique vide et écrasait les écarts entre modèles.
  const smax=Math.max(...r.map(s=>s.s))*1.04,
        smin=Math.max(0,Math.min(...r.map(s=>s.s))-0.05);
  // Même convention que le coût mesuré : moins cher vers la droite.
  const x=v=>W-R-(Math.log10(v)-lo)/(hi-lo)*(W-L-R),
        y=v=>H-B-(v-smin)/(smax-smin)*(H-B-T);
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Prix catalogue contre performance, échelle logarithmique'});
  for(let i=0;i<=4;i++){const v=smin+(smax-smin)*i/4;
    sv.append(mk('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),class:'gl'}));
    const t=mk('text',{x:L-8,y:y(v)+4,'text-anchor':'end',class:'ax'});
    t.textContent=(v*100).toFixed(0)+'%';sv.append(t);}
  decades(lo,hi).forEach(v=>{
    sv.append(mk('line',{x1:x(v),x2:x(v),y1:T,y2:H-B,class:'gl'}));
    const t=mk('text',{x:x(v),y:H-B+16,'text-anchor':'middle',class:'ax'});
    t.textContent=money(v);sv.append(t);});
  r.forEach(s=>{const c=cv(LABC[s.l]||'--ink-3'),g=mk('g');
    g.append(mk('circle',{cx:x(D.prices[s.m].in),cy:y(s.s),r:5.5,fill:c,
      stroke:cv('--panel'),'stroke-width':2}));
    wire(g,`<b>${esc(s.d||s.m)}</b>${esc(s.o)}<br>${pct(s.s)} pour `+
      `<b>$${D.prices[s.m].in}</b> le million de tokens d'entrée`+
      `<i>prix affiché au catalogue, pas un coût de tâche mesuré</i>`);
    sv.append(g);});
  const xt=mk('text',{x:(L+W-R)/2,y:H-8,'text-anchor':'middle',class:'ax'});
  xt.textContent='◀ plus cher      prix d\'entrée par million de tokens (échelle log)      moins cher ▶';
  sv.append(xt);
  if(gratuits){const t=mk('text',{x:W-8,y:H-8,'text-anchor':'end',class:'ax'});
    t.textContent=gratuits+' modèle'+(gratuits>1?'s':'')+' gratuit'+(gratuits>1?'s':'')+
      ' — hors échelle';sv.append(t);}
  // L'identité ne doit pas reposer sur la seule couleur : chaque point est nommé.
  gouttiere(sv,r.map(s=>({nom:s.d||s.m,c:cv(LABC[s.l]||'--ink-3'),
    cx:x(D.prices[s.m].in),cy:y(s.s)})),W,R,T,B,H);
  render(sv,r,'fraction');
}

function legend(sv,r,W){
  // Espacement calculé sur la longueur réelle : à pas fixe, les noms longs
  // débordaient sur le suivant.
  let X=58;
  [...new Set(r.map(s=>s.o))].slice(0,8).forEach(o=>{
    const z=r.find(v=>v.o===o),lb=o.length>20?o.slice(0,19)+'…':o;
    if(X+lb.length*6.3+30>W)return;
    sv.append(mk('circle',{cx:X,cy:12,r:4,fill:cv(LABC[z.l]||'--ink-3')}));
    const t=mk('text',{x:X+8,y:16,class:'ax'});t.textContent=lb;sv.append(t);
    X+=lb.length*6.3+30;});
}

// Étiquettes directes posées dans la gouttière de droite. Au point, elles se
// recouvrent dès que le nuage est dense ; ici elles sont décollées d'un pas
// minimum et reliées à leur marque par un filet.
function gouttiere(sv,items,W,R,T,B,H){
  const PAS=13,lab=items.slice().sort((a,b)=>a.cy-b.cy);
  let prev=T-PAS;
  lab.forEach(z=>{z.ly=Math.max(z.cy,prev+PAS);prev=z.ly;});
  const debord=lab.length?lab.at(-1).ly-(H-B):0;
  if(debord>0){prev=H-B+PAS;
    for(let i=lab.length-1;i>=0;i--){lab[i].ly=Math.min(lab[i].ly,prev-PAS);prev=lab[i].ly;}}
  lab.forEach(z=>{const lx=W-R+12;
    sv.append(mk('path',{d:`M${z.cx+7},${z.cy} L${lx-8},${z.ly-4} L${lx-3},${z.ly-4}`,
      fill:'none',stroke:z.c,'stroke-width':1,opacity:.4}));
    const t=mk('text',{x:lx,y:z.ly,class:'lbl','font-size':'11'});
    t.textContent=z.nom.slice(0,26);sv.append(t);});
}
// Ce que montre chaque vue, en une phrase. Sans elle, un graphique juste reste
// un graphique qu'on ne sait pas lire.
const HOWTO={
 rank:"Une barre par modèle : la longueur est son score sur le benchmark choisi. Le trait "+
   "fin qui la traverse est sa marge d'erreur — deux modèles dont les traits se chevauchent "+
   "ne sont pas départageables, même si le classement les sépare.",
 harness:"Un même modèle, relancé sous plusieurs outils différents. Chaque point est un "+
   "outil, la ligne relie le pire au meilleur : sa longueur, c'est ce que le choix de "+
   "l'outil vous fait gagner ou perdre, à modèle identique.",
 time:"Chaque point est un modèle, placé à sa date de publication et à la hauteur de son "+
   "score. La ligne pointillée suit le record du moment : elle montre à quelle vitesse ce "+
   "benchmark se fait battre, et quand il commence à saturer.",
 cover:"Une ligne par modèle, une colonne par benchmark, regroupées par fournisseur. Plus "+
   "la case est foncée, meilleur est le score ; une case en pointillés veut dire que "+
   "personne n'a publié la mesure — le trou compte autant que le chiffre.",
 // Cette note sert au repli « prix catalogue » de la vue coût × performance :
 // quand le benchmark publie un coût mesuré, frontier() écrit la sienne.
 frontier:"Chaque point est un modèle : son <b>prix affiché au catalogue</b> par million de "+
   "tokens d'entrée en abscisse, son score en ordonnée. <b>L'axe des prix est logarithmique "+
   "et inversé</b> — chaque graduation vaut dix fois la précédente, et <b>le meilleur rapport "+
   "se lit en haut à droite</b>. Ce benchmark ne publiant pas le coût réel des runs, c'est le "+
   "tarif au token qui sert d'approximation : il ne dit rien du nombre de tokens qu'une tâche "+
   "consomme réellement.",
};
function empty(msg){
  $('#chart').innerHTML='<div class="empty">'+
    msg.split('\n\n').map(x=>`<p>${esc(x)}</p>`).join('')+'</div>';
  $('#tbl').innerHTML='';$('#caveat').innerHTML='';}
function render(sv,r,unit){
  $('#chart').innerHTML='';$('#chart').append(sv);
  const b=cur();
  // Deux notes distinctes : comment lire le dessin, puis ce que le benchmark
  // lui-même ne garantit pas. Les confondre rendait les deux illisibles.
  $('#caveat').innerHTML=
    (HOWTO[K]?`<div class="note"><b>Comment lire.</b> ${HOWTO[K]}</div>`:'')+
    // La couverture ne dépend pas du benchmark sélectionné : lui accoler la
    // réserve de SWE-Bench laisserait croire qu'elle porte sur toute la matrice.
    (b.caveat&&K!=='cover'?
      `<div class="note"><b>Réserve sur ce benchmark.</b> ${esc(b.caveat)}</div>`:'');
  $('#tbl').innerHTML=r.length?
    '<thead><tr><th>Modèle</th><th>Fournisseur</th><th>Harnais</th>'+
    '<th class="n">Score</th><th class="n">IC95</th><th>Provenance</th><th>Source</th></tr></thead>'+
    '<tbody>'+r.map(s=>`<tr><td>${esc(s.d||s.m)}</td><td>${esc(s.o)}</td>`+
      `<td>${esc(s.h||'—')}</td><td class="n">${pct(s.s,unit)}</td>`+
      `<td class="n">${s.e?'±'+(1.96*s.e*100).toFixed(1):'—'}</td>`+
      `<td>${esc(s.p)}</td><td>${s.u?`<a href="${esc(s.u)}" rel="noopener">lien</a>`:'—'}</td></tr>`
    ).join('')+'</tbody>':'';
}

const EFF=['low','medium','high','xhigh','max'];
function frontier(){
  // Coût RÉELLEMENT MESURÉ (pas le prix catalogue) contre score, avec les
  // points d'un même modèle reliés par son échelle d'effort de raisonnement.
  // Axe des coûts inversé : moins cher vers la droite, donc « mieux » = haut-droite.
  let r=rows().filter(s=>s.c!=null&&s.c>0);
  if(!r.length)return empty(
    "Ce benchmark ne publie pas de coût mesuré. Les benchmarks qui le font : "+
    "DeepSWE (le plus complet — 5 niveaux d'effort par modèle, harnais unique), "+
    "Aider polyglot, ARC-AGI-2, OSWorld 2.0, The Agent Company.");
  const by=new Map();
  r.forEach(s=>{const k=s.mb||s.m;if(!by.has(k))by.set(k,[]);by.get(k).push(s);});
  let g=[...by.entries()].map(([k,v])=>({k,d:v[0].d,o:v[0].o,l:v[0].l,
    v:v.sort((a,b)=>(EFF.indexOf(a.ef)-EFF.indexOf(b.ef))||a.c-b.c)}));
  g.sort((a,b)=>Math.max(...b.v.map(x=>x.s))-Math.max(...a.v.map(x=>x.s)));
  const n=+$('#top').value; if(n)g=g.slice(0,n);
  const pts=g.flatMap(x=>x.v);
  if(!pts.length)return empty('Aucun point exploitable.');

  const W=940,H=560,L=62,R=188,T=34,B=54;
  const cmin=Math.min(...pts.map(p=>p.c)),cmax=Math.max(...pts.map(p=>p.c));
  const smax=Math.max(...pts.map(p=>p.s))*1.08,smin=Math.max(0,Math.min(...pts.map(p=>p.s))-0.05);
  const lo=Math.log10(cmin*0.8),hi=Math.log10(cmax*1.25);
  // Inversion : le coût le plus BAS est à droite.
  const x=c=>W-R-(Math.log10(c)-lo)/(hi-lo)*(W-L-R);
  const y=v=>H-B-(v-smin)/(smax-smin)*(H-B-T);
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Coût mesuré contre performance, par niveau d\'effort'});

  // grille + graduations de coût (décades)
  for(let i=0;i<=4;i++){const v=smin+(smax-smin)*i/4;
    sv.append(mk('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),class:'gl'}));
    const t=mk('text',{x:L-8,y:y(v)+4,'text-anchor':'end',class:'ax'});
    t.textContent=(v*100).toFixed(0)+'%';sv.append(t);}
  decades(lo,hi).forEach(v=>{
    sv.append(mk('line',{x1:x(v),x2:x(v),y1:T,y2:H-B,class:'gl'}));
    const t=mk('text',{x:x(v),y:H-B+16,'text-anchor':'middle',class:'ax'});
    t.textContent=money(v);sv.append(t);});

  // Front de Pareto : rien n'est à la fois moins cher ET meilleur.
  const par=pts.filter(p=>!pts.some(q=>q!==p&&q.c<=p.c&&q.s>=p.s&&(q.c<p.c||q.s>p.s)))
               .sort((a,b)=>a.c-b.c);
  if(par.length>1){
    let d=`M${x(par[0].c)},${y(par[0].s)}`;
    for(let i=1;i<par.length;i++)d+=` L${x(par[i].c)},${y(par[i-1].s)} L${x(par[i].c)},${y(par[i].s)}`;
    sv.append(mk('path',{d,fill:'none',stroke:cv('--ink-3'),'stroke-width':1.5,
      'stroke-dasharray':'5 4',opacity:.55}));
    const t=mk('text',{x:x(par.at(-1).c)+6,y:y(par.at(-1).s)-8,class:'ax'});
    t.textContent='front de Pareto';sv.append(t);}

  // Une polyligne par modèle : son échelle d'effort.
  g.forEach(row=>{const c=cv(LABC[row.l]||'--ink-3');
    if(row.v.length>1){
      const d='M'+row.v.map(p=>`${x(p.c)},${y(p.s)}`).join(' L');
      sv.append(mk('path',{d,fill:'none',stroke:c,'stroke-width':2,opacity:.55,
        'stroke-linejoin':'round'}));}
    row.v.forEach((p,i)=>{const gg=mk('g');
      // Taille croissante avec l'effort : la position dans l'échelle se lit sans légende.
      const rad=row.v.length>1?3+2.4*i/Math.max(1,row.v.length-1):4.6;
      gg.append(mk('circle',{cx:x(p.c),cy:y(p.s),r:rad,fill:c,
        stroke:cv('--panel'),'stroke-width':1.8}));
      wire(gg,`<b>${esc(p.d||p.m)}</b>${esc(p.o)}`+
        (p.ef?`<br>effort : <b>${esc(p.ef)}</b>`:'')+
        `<br>score <b>${(p.s*100).toFixed(1)}%</b> pour <b>$${p.c.toFixed(2)}</b> par tâche`+
        (p.h?`<br>harnais : ${esc(p.h)}`:'')+
        `<i>coût mesuré lors du run, pas un prix catalogue</i>`);
      sv.append(gg);});
    });

  // Étiquettes directes — l'identité ne doit pas reposer sur la seule couleur.
  // Posées au point, elles se recouvraient toutes au centre du nuage : elles
  // vivent donc dans la gouttière de droite, décollées verticalement, chacune
  // reliée à son modèle par un filet.
  gouttiere(sv,g.map(row=>{const b=row.v.reduce((a,c)=>c.s>a.s?c:a);
    return {nom:row.d||row.k,c:cv(LABC[row.l]||'--ink-3'),cx:x(b.c),cy:y(b.s)};}),
    W,R,T,B,H);

  const xt=mk('text',{x:(L+W-R)/2,y:H-8,'text-anchor':'middle',class:'ax'});
  xt.textContent='◀ plus cher      coût mesuré par tâche (échelle log)      moins cher ▶';
  sv.append(xt);
  const yt=mk('text',{x:14,y:H/2,'text-anchor':'middle',class:'ax',
    transform:`rotate(-90 14 ${H/2})`});
  yt.textContent='score';sv.append(yt);

  $('#chart').innerHTML='';$('#chart').append(sv);
  $('#caveat').innerHTML='<div class="note"><b>Comment lire.</b> Chaque polyligne est '+
    "un modèle, chaque point un niveau d'effort de raisonnement (du plus petit cercle, "+
    "<code>low</code>, au plus grand, <code>max</code>). L'axe des coûts est inversé : "+
    "<b>en haut à droite = meilleur et moins cher</b>. Le coût affiché est celui "+
    "<b>réellement mesuré pendant le run</b>, pas un prix au token — c'est ce qui rend "+
    "les niveaux d'effort comparables. Une courbe qui s'aplatit signale que l'effort "+
    "supplémentaire ne s'achète plus : le point <code>max</code> coûte souvent le double "+
    "du <code>xhigh</code> pour un gain nul, voire négatif.</div>";
  $('#tbl').innerHTML='<thead><tr><th>Modèle</th><th>Effort</th><th class="n">Score</th>'+
    '<th class="n">Coût/tâche</th><th class="n">$ par point</th><th>Harnais</th></tr></thead><tbody>'+
    pts.sort((a,b)=>b.s-a.s).map(p=>`<tr><td>${esc(p.d||p.m)}</td><td>${esc(p.ef||'—')}</td>`+
      `<td class="n">${(p.s*100).toFixed(1)}%</td><td class="n">$${p.c.toFixed(2)}</td>`+
      `<td class="n">$${(p.c/(p.s*100)).toFixed(3)}</td><td>${esc(p.h||'—')}</td></tr>`
    ).join('')+'</tbody>';
}


function budget(){
  // Question inverse : sous plafond de coût, que peut-on espérer de mieux ?
  const cap=parseFloat($('#bud').value);
  let r=rows().filter(s=>s.c!=null&&s.c>0);
  if(!r.length)return empty(
    "Cette vue a besoin d'un coût mesuré. Benchmarks concernés : DeepSWE, "+
    "Aider polyglot, ARC-AGI-2, OSWorld 2.0, The Agent Company.");
  const within=r.filter(s=>s.c<=cap);
  // Meilleure configuration atteignable par modèle sous le plafond.
  const by=new Map();
  within.forEach(s=>{const k=s.mb||s.m;const p=by.get(k);
    if(!p||s.s>p.s)by.set(k,s);});
  let g=[...by.values()].sort((a,b)=>b.s-a.s);
  const n=+$('#top').value; if(n)g=g.slice(0,n);
  const exclus=new Set(r.map(s=>s.mb||s.m)).size-by.size;
  if(!g.length)return empty(
    `Aucun modèle n'atteint ce benchmark pour ${cap} $ ou moins par tâche. `+
    `Le moins cher mesuré coûte ${Math.min(...r.map(s=>s.c)).toFixed(2)} $.`);
  const W=940,L=290,R=150,BH=26,H=g.length*BH+52;
  const max=Math.max(...g.map(x=>x.s))*1.06;
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':`Meilleur score atteignable sous ${cap} dollars par tâche`});
  const x=v=>L+v/max*(W-L-R);
  for(let i=0;i<=4;i++){const v=max*i/4;
    sv.append(mk('line',{x1:x(v),x2:x(v),y1:30,y2:H-20,class:'gl'}));
    const t=mk('text',{x:x(v),y:22,'text-anchor':'middle',class:'ax'});
    t.textContent=(v*100).toFixed(0)+'%';sv.append(t);}
  g.forEach((s,i)=>{const y=34+i*BH,c=cv(LABC[s.l]||'--ink-3'),gg=mk('g');
    const lb=mk('text',{x:L-9,y:y+14,'text-anchor':'end',class:'lbl'});
    lb.textContent=(s.d||s.m).slice(0,40);gg.append(lb);
    gg.append(mk('rect',{x:L,y:y+3,width:Math.max(2,x(s.s)-L),height:15,rx:4,fill:c}));
    const vt=mk('text',{x:W-R+7,y:y+15,class:'val'});
    vt.textContent=`${(s.s*100).toFixed(1)}% · $${s.c.toFixed(2)}`;gg.append(vt);
    wire(gg,`<b>${esc(s.d||s.m)}</b>${esc(s.o)}<br>`+
      `meilleur résultat sous ${cap} $ : <b>${(s.s*100).toFixed(1)}%</b> pour `+
      `<b>$${s.c.toFixed(2)}</b>`+(s.ef?`<br>à l'effort <b>${esc(s.ef)}</b>`:'')+
      `<i>marge restante : $${(cap-s.c).toFixed(2)} par tâche</i>`);
    sv.append(gg);});
  $('#chart').innerHTML='';$('#chart').append(sv);
  const meilleur=g[0];
  $('#caveat').innerHTML=`<div class="note"><b>Sous ${cap} $ par tâche.</b> `+
    `Le meilleur résultat atteignable est <b>${esc(meilleur.d||meilleur.m)}</b> `+
    `à <b>${(meilleur.s*100).toFixed(1)}%</b>`+
    (meilleur.ef?` avec un effort <code>${esc(meilleur.ef)}</code>`:'')+
    `, pour ${meilleur.c.toFixed(2)} $. `+
    (exclus>0?`${exclus} modèle${exclus>1?'s sont exclus':' est exclu'} du plafond. `:'')+
    `Chaque barre montre la <b>meilleure configuration accessible</b> du modèle, `+
    `pas sa performance maximale : un modèle plus puissant mais hors budget `+
    `n'apparaît qu'à un palier d'effort qu'il peut se payer ici.</div>`;
  $('#tbl').innerHTML='<thead><tr><th>Modèle</th><th>Effort accessible</th>'+
    '<th class="n">Score</th><th class="n">Coût</th><th class="n">Marge</th></tr></thead><tbody>'+
    g.map(s=>`<tr><td>${esc(s.d||s.m)}</td><td>${esc(s.ef||'—')}</td>`+
      `<td class="n">${(s.s*100).toFixed(1)}%</td><td class="n">$${s.c.toFixed(2)}</td>`+
      `<td class="n">$${(cap-s.c).toFixed(2)}</td></tr>`).join('')+'</tbody>';
}

function api(){
  // Barres du coût d'entrée, avec le coût de sortie en repère secondaire.
  let r=D.priced_models.slice();
  if(lsel.value){const m={'Anthropic':'anthropic','OpenAI':'openai','Google DeepMind':'google',
   'DeepSeek':'deepseek','Alibaba':'alibaba','Mistral AI':'mistral','Moonshot':'moonshot',
   'Z.ai (Zhipu AI)':'zhipu','xAI':'xai','Meta AI':'meta','MiniMax':'minimax'}[lsel.value];
   if(m)r=r.filter(x=>x.lab===m);}
  const n=+$('#top').value; if(n)r=r.slice(0,n);
  if(!r.length)return empty('Aucun modèle tarifé pour ce filtre.');
  // Les tarifs couvrent trois décades : en linéaire, tout ce qui est sous 1 $
  // se colle à l'axe et devient illisible. L'échelle est donc logarithmique —
  // ce qui interdit la barre, qui a besoin d'un zéro. Chaque modèle est une
  // haltère : un point pour l'entrée, un pour la sortie, reliés par leur écart.
  const W=940,L=250,R=132,BH=25,TOP=46,H=r.length*BH+TOP+22;
  const vals=r.flatMap(m=>[m.in,m.out]).filter(v=>v!=null&&v>0);
  const gratuits=r.filter(m=>!m.in);
  const lo=Math.log10(Math.min(...vals)*0.7),hi=Math.log10(Math.max(...vals)*1.4);
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Tarifs API par million de tokens, échelle logarithmique'});
  const x=v=>L+(Math.log10(v)-lo)/(hi-lo)*(W-L-R);
  decades(lo,hi).forEach(v=>{
    sv.append(mk('line',{x1:x(v),x2:x(v),y1:TOP-10,y2:H-20,class:'gl'}));
    const t=mk('text',{x:x(v),y:TOP-16,'text-anchor':'middle',class:'ax'});
    t.textContent=money(v);sv.append(t);});
  [['entrée','--s1',0],['sortie','--s2',108]].forEach(([lb,c,off])=>{
    sv.append(mk('circle',{cx:L+off,cy:11,r:4.5,fill:cv(c)}));
    const t=mk('text',{x:L+off+9,y:15,class:'ax'});t.textContent=lb;sv.append(t);});
  const eh=mk('text',{x:W-8,y:15,'text-anchor':'end',class:'ax'});
  eh.textContent='échelle logarithmique';sv.append(eh);
  r.forEach((m,i)=>{const y=TOP+i*BH,g=mk('g'),cy=y+11;
    const lb=mk('text',{x:L-9,y:y+15,'text-anchor':'end',class:'lbl'});
    lb.textContent=(m.name||m.id).slice(0,34);g.append(lb);
    if(m.in){
      if(m.out)g.append(mk('line',{x1:x(m.in),x2:x(m.out),y1:cy,y2:cy,
        stroke:cv('--ink-3'),'stroke-width':2,opacity:.35}));
      g.append(mk('circle',{cx:x(m.in),cy,r:4.5,fill:cv('--s1'),
        stroke:cv('--panel'),'stroke-width':1.8}));
      if(m.out)g.append(mk('circle',{cx:x(m.out),cy,r:4.5,fill:cv('--s2'),
        stroke:cv('--panel'),'stroke-width':1.8}));}
    const vt=mk('text',{x:W-R+7,y:y+15,class:'val'});
    vt.textContent=m.in?`$${m.in} / $${m.out??'—'}`:'gratuit';g.append(vt);
    wire(g,`<b>${esc(m.name)}</b>${esc(m.api_id||m.id)}<br>`+
      `entrée <b>$${m.in}</b> · cache $${m.cached??'—'} · sortie <b>$${m.out??'—'}</b> /1M`+
      (m.ctx?`<br>contexte : ${(m.ctx/1000).toFixed(0)}k`:'')+
      (m.offpeak?`<br>heures creuses : $${m.offpeak.input_per_1m} / $${m.offpeak.output_per_1m}`:'')+
      (m.promo?`<br>${esc(m.promo)}`:'')+(m.tier?`<br>${esc(m.tier)}`:'')+
      ``);
    sv.append(g);});
  $('#chart').innerHTML='';$('#chart').append(sv);
  $('#caveat').innerHTML='<div class="note"><b>Comment lire.</b> Chaque ligne est un modèle. '+
    'Le point bleu est le prix d\'un million de tokens envoyés, le point orange celui d\'un '+
    'million de tokens produits ; l\'écart entre les deux est le facteur de sortie. '+
    '<b>L\'axe est logarithmique</b> : chaque graduation vaut dix fois la précédente, sans quoi '+
    'les modèles à quelques centimes seraient tous écrasés contre le bord gauche.</div>'+
    '<div class="note"><b>Réserve de lecture.</b> Le coût réel d\'une tâche dépend du ratio '+
    'entrée/sortie et du taux de cache. Un modèle cher au token peut revenir moins cher '+
    's\'il réussit du premier coup.</div>';
  $('#tbl').innerHTML='<thead><tr><th>Modèle</th><th>Identifiant API</th>'+
    '<th class="n">Entrée</th><th class="n">Cache</th><th class="n">Sortie</th>'+
    '<th class="n">Contexte</th></tr></thead><tbody>'+
    r.map(m=>`<tr><td>${esc(m.name)}</td><td>${esc(m.api_id||'—')}</td>`+
      `<td class="n">$${m.in}</td><td class="n">${m.cached!=null?'$'+m.cached:'—'}</td>`+
      `<td class="n">${m.out!=null?'$'+m.out:'—'}</td>`+
      `<td class="n">${m.ctx?(m.ctx/1000).toFixed(0)+'k':'—'}</td></tr>`).join('')+'</tbody>';
}

function plans(){
  const r=D.plans.filter(p=>p.price_usd_month!=null)
                 .sort((a,b)=>a.price_usd_month-b.price_usd_month);
  if(!r.length)return empty('Aucun forfait au catalogue.');
  const W=940,L=250,R=176,BH=27,H=r.length*BH+56;
  const max=Math.max(...r.map(p=>p.eur_ttc||0))*1.08||1;
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Forfaits mensuels, montants débités en France'});
  const x=v=>L+v/max*(W-L-R);
  for(let i=0;i<=4;i++){const v=max*i/4;
    sv.append(mk('line',{x1:x(v),x2:x(v),y1:30,y2:H-20,class:'gl'}));
    const t=mk('text',{x:x(v),y:22,'text-anchor':'middle',class:'ax'});
    t.textContent=v.toFixed(0)+' €';sv.append(t);}
  [['HT (pro, autoliquidation)','--s3',0],['TTC (particulier)','--s1',196]]
    .forEach(([lb,c,off])=>{
    sv.append(mk('circle',{cx:L+off,cy:12,r:4,fill:cv(c)}));
    const t=mk('text',{x:L+off+8,y:16,class:'ax'});t.textContent=lb;sv.append(t);});
  r.forEach((p,i)=>{const y=34+i*BH,g=mk('g');
    const lb=mk('text',{x:L-9,y:y+15,'text-anchor':'end',class:'lbl'});
    lb.textContent=`${p.product} · ${p.name}`.slice(0,36);g.append(lb);
    if(p.eur_ttc)g.append(mk('rect',{x:L,y:y+3,width:Math.max(2,x(p.eur_ttc)-L),height:16,
      rx:4,fill:cv('--s1'),opacity:.28}));
    if(p.eur_ht)g.append(mk('rect',{x:L,y:y+3,width:Math.max(2,x(p.eur_ht)-L),height:16,
      rx:4,fill:cv('--s3')}));
    const vt=mk('text',{x:W-R+7,y:y+15,class:'val'});
    vt.textContent=p.price_usd_month===0?'gratuit':
      `${p.eur_ht} € HT · ${p.eur_ttc} € TTC`;g.append(vt);
    wire(g,`<b>${esc(p.vendor)} — ${esc(p.product)} ${esc(p.name)}</b>`+
      `affiché ${p.price_usd_month} $/mois${p.per_seat?' par siège':''}<br>`+
      `pro (autoliquidation) : <b>${p.eur_ht} € HT</b><br>`+
      `particulier (TVA 20 %) : <b>${p.eur_ttc} € TTC</b>`+
      (p.credits_usd_month?`<br>crédits inclus : ${p.credits_usd_month} $/mois`:'')+
      (p.price_usd_month_annual?`<br>engagement annuel : ${p.price_usd_month_annual} $/mois`:'')+
      `<br>${esc(p.includes||'')}`);
    sv.append(g);});
  $('#chart').innerHTML='';$('#chart').append(sv);
  $('#caveat').innerHTML='<div class="note"><b>Deux régimes de facturation.</b> '+
    'Un professionnel qui renseigne son numéro de TVA intracommunautaire est facturé '+
    'en autoliquidation (0 % débité) : il paie le montant HT. Un particulier paie la '+
    'TVA française de 20 %. Les euros sont calculés au taux de '+
    `${D.fx.usd_eur} $/€, lui-même ${D.fx.status==='verified'?'vérifié':'NON vérifié'}.</div>`;
  $('#tbl').innerHTML='<thead><tr><th>Éditeur</th><th>Forfait</th><th class="n">Affiché</th>'+
    '<th class="n">€ HT (pro)</th><th class="n">€ TTC</th><th>Inclus</th></tr></thead><tbody>'+
    r.map(p=>`<tr><td>${esc(p.vendor)}</td><td>${esc(p.product)} ${esc(p.name)}</td>`+
      `<td class="n">$${p.price_usd_month}${p.per_seat?'/u':''}</td>`+
      `<td class="n">${p.eur_ht} €</td><td class="n">${p.eur_ttc} €</td>`+
      `<td>${esc(p.includes||'—')}</td></tr>`).join('')+'</tbody>';
}

// Deux façons de croiser coût et performance, sous un même bouton : le coût
// réellement mesuré quand le benchmark le publie, le prix catalogue sinon. Les
// deux ne se valent pas — chaque vue le dit dans sa note de lecture.
const coutPerf=()=>mesure(bsel.value)?frontier():price();
const DRAW={rank,frontier:coutPerf,budget,harness,time,cover,api,plans};

// Toutes les vues ne s'appliquent pas à tous les benchmarks : le coût mesuré et
// le nom du harnais ne sont publiés que par une minorité d'entre eux. Proposer
// un bouton qui ne peut rien afficher se lit comme une panne — on le désactive
// et on dit où la vue existe.
const EXIGE={budget:'le coût mesuré de chaque run',
             harness:"le nom du harnais utilisé"};
const mesure=b=>D.scores.some(s=>s.b===b&&s.c!=null&&s.c>0);
function dispo(k,b){
  b=b||bsel.value;
  // Le coût mesuré n'existe que sur quelques benchmarks, mais le prix catalogue
  // existe pour tout modèle tarifé : la vue reste donc ouverte, et dit lequel
  // des deux elle montre.
  if(k==='frontier')
    return mesure(b)||D.scores.some(s=>s.b===b&&D.prices[s.m]);
  if(k==='budget')return mesure(b);
  if(k==='harness'){
    const vus=new Map();
    for(const s of D.scores){
      if(s.b!==b||!s.h)continue;
      if(!vus.has(s.m))vus.set(s.m,new Set());
      vus.get(s.m).add(s.h);
      if(vus.get(s.m).size>1)return true;   // il faut deux harnais pour comparer
    }
    return false;
  }
  return true;
}
// Un filtre qui n'agit sur rien ne doit pas être affiché : la matrice de
// couverture montre TOUS les benchmarks, les vues tarifaires n'en dépendent
// d'aucun. Laisser le sélecteur visible laissait croire qu'il agissait.
const CTRL={rank:'blet',frontier:'blet',budget:'blet',harness:'blet',time:'blet',
            cover:'lt',api:'lt',plans:''};
function majControles(){
  const c=CTRL[K]??'blet';
  bsel.closest('label').hidden=!c.includes('b');
  lsel.closest('label').hidden=!c.includes('l');
  $('#eff').closest('label').hidden=!c.includes('e');
  $('#top').closest('label').hidden=!c.includes('t');
  $('#budwrap').hidden=(K!=='budget');
}
function majBoutons(){
  [...$('#kind').children].forEach(btn=>{
    const k=btn.dataset.k,ok=dispo(k);
    btn.disabled=!ok;
    if(ok){btn.removeAttribute('title');btn.removeAttribute('aria-disabled');return;}
    btn.setAttribute('aria-disabled','true');
    const ailleurs=D.benchmarks.map(x=>x.name).filter(n=>dispo(k,n));
    btn.title=`${bsel.value} ne publie pas ${EXIGE[k]}.`+
      (ailleurs.length?` Vue disponible sur : ${ailleurs.join(', ')}.`:'');
  });
  if(!dispo(K)){
    K='rank';
    [...$('#kind').children].forEach(x=>
      x.setAttribute('aria-pressed',String(x.dataset.k==='rank')));
    $('#budwrap').hidden=true;
  }
}
function draw(){majBoutons();majControles();DRAW[K]();}
$('#kind').addEventListener('click',e=>{const b=e.target.closest('button');
  if(!b||b.disabled)return;
  K=b.dataset.k;[...$('#kind').children].forEach(x=>
    x.setAttribute('aria-pressed',String(x===b)));
  draw();});
[bsel,lsel,$('#top'),$('#eff'),$('#bud')].forEach(el=>el.addEventListener('change',draw));

// ── navigation par onglets ────────────────────────────────────────────────
const SEC=['mesures','modeles','harnais','passerelles','methode'];
function showSection(name,remonter){
  SEC.forEach(x=>{const el=$('#s-'+x);if(el)el.hidden=(x!==name);});
  [...$('#nav').children].forEach(b=>
    b.setAttribute('aria-selected',String(b.dataset.s===name)));
  if(name==='mesures')draw();
  if(remonter){
    const doux=!matchMedia('(prefers-reduced-motion: reduce)').matches;
    $('#nav').scrollIntoView({block:'start',behavior:doux?'smooth':'auto'});
  }
  try{localStorage.setItem('tandem.section',name);}catch(e){}
}
$('#nav').addEventListener('click',e=>{const b=e.target.closest('button');
  if(b)showSection(b.dataset.s,true);});

$('#met-cat').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  [...$('#met-cat').children].forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  ['regles','bench','etat'].forEach(k=>{$('#m-'+k).hidden=(k!==b.dataset.m);});});

// ── fiches outils, groupées par catégorie ─────────────────────────────────
const CATL={ide_fork:'IDE dérivés',vscode_extension:'Extensions VS Code',
 desktop_app:'Applications desktop',cli_agent:'Agents CLI',
 gateway:'Agrégateurs cloud',local_server:'Serveurs locaux'};
const CATD={
 ide_fork:"Éditeurs complets, généralement dérivés de VS Code, où l'IA est intégrée au cœur de l'outil.",
 vscode_extension:"Greffons installés dans un VS Code ou un JetBrains standard : on garde son éditeur.",
 desktop_app:"Applications autonomes, hors éditeur de code, disposant d'un accès aux fichiers locaux.",
 cli_agent:"Agents pilotés depuis le terminal, au plus près du dépôt Git.",
 gateway:"Un point d'accès unique à plusieurs laboratoires, avec une seule clé d'API.",
 local_server:"Exécution des modèles sur la machine de l'utilisateur, exposée en API compatible OpenAI."};

function carteOutil(t){
  const mort=t.status==='retired';
  const caps=[t.byok&&'BYOK',t.local_models&&'modèles locaux',t.mcp&&'MCP',t.free&&'gratuit']
    .filter(Boolean);
  const pl=(t.plans||[]).map(id=>D.plans.find(p=>p.id===id)).filter(Boolean);
  const c=t.compliance||{};
  const cf=[c.zero_data_retention&&'rétention zéro',c.self_hosted&&'auto-hébergeable',
    c.sso&&'SSO',c.audit_logs&&"journaux d'audit",
    c.data_residency==='local'&&'données locales'].filter(Boolean);
  return `<div class="bc" ${mort?'style="opacity:.7"':''}>
   <h3>${esc(t.name)} ${mort?'<span class="tag" style="border-color:var(--bad);color:var(--bad)">retiré</span>':''}</h3>
   <p style="color:var(--ink-3);font-size:11.5px;margin:2px 0 7px">${esc(t.vendor||'—')}</p>
   <p>${esc(t.note||'')}</p>
   ${caps.length?`<p style="margin-top:8px">${caps.map(x=>`<span class="tag">${x}</span>`).join(' ')}</p>`:''}
   ${t.serves_openai_api?`<p style="margin-top:7px;font-size:12px;color:var(--ink-2)">
     Endpoint : <code>${esc(t.serves_openai_api)}</code></p>`:''}
   ${pl.length?`<p style="margin-top:8px;font-size:12px;color:var(--ink-2)">
     ${pl.map(x=>`${esc(x.name)} — ${x.price_usd_month===0?'gratuit':
       x.eur_ht+' € HT'+(x.per_seat?'/siège':'')}`).join(' · ')}</p>`:''}
   ${cf.length?`<p style="margin-top:9px;padding-top:9px;border-top:1px solid var(--line)">
     <span style="color:var(--ink-3);font-size:10.5px;text-transform:uppercase;
     letter-spacing:.06em">Conformité</span><br>
     ${cf.map(x=>`<span class="tag">${x}</span>`).join(' ')}</p>`:''}
   ${(t.url||t.repo_url)?`<p style="margin-top:10px;font-size:12px">
     ${t.url?`<a href="${esc(t.url)}" rel="noopener">site officiel</a>`:''}
     ${t.url&&t.repo_url?' · ':''}
     ${t.repo_url?`<a href="${esc(t.repo_url)}" rel="noopener">dépôt</a>`:''}</p>`:''}
  </div>`;
}

function rendreCouche(cible,couche,ordre,filtre){
  const el=$(cible);let html='';
  ordre.filter(c=>!filtre||c===filtre).forEach(cat=>{
    const items=D.tools.filter(t=>t.layer===couche&&t.category===cat);
    if(!items.length)return;
    html+=`<h3 class="grp">${CATL[cat]}<span class="c">${items.length} outil${
      items.length>1?'s':''}</span></h3>
      <p class="lede" style="font-size:13px">${CATD[cat]}</p>
      <div class="bl">${items.map(carteOutil).join('')}</div>`;
  });
  el.innerHTML=html;
}

// Sélecteur de catégorie : évite de faire défiler toute la couche pour
// atteindre une famille d'outils.
function brancherCategories(idBoutons,cible,couche,ordre){
  const bar=$(idBoutons);
  const dispo=ordre.filter(c=>D.tools.some(t=>t.layer===couche&&t.category===c));
  bar.innerHTML=`<button data-c="" aria-pressed="true">Toutes</button>`+
    dispo.map(c=>`<button data-c="${c}" aria-pressed="false">${CATL[c]}</button>`).join('');
  bar.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
    [...bar.children].forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
    rendreCouche(cible,couche,ordre,b.dataset.c||null);});
}
const ORD_H=['ide_fork','vscode_extension','cli_agent','desktop_app'];
const ORD_P=['gateway','local_server'];
rendreCouche('#har',1,ORD_H,null);
rendreCouche('#pas',2,ORD_P,null);
brancherCategories('#har-cat','#har',1,ORD_H);
brancherCategories('#pas-cat','#pas',2,ORD_P);

// ── modèles & tarifs ──────────────────────────────────────────────────────
(function(){
  const parLab=new Map();
  D.priced_models.forEach(m=>{if(!parLab.has(m.lab))parLab.set(m.lab,[]);
    parLab.get(m.lab).push(m);});
  const nomLab=id=>(D.labs_full.find(l=>l.id===id)||{}).name||id;
  let html='';
  [...parLab.entries()].sort((a,b)=>nomLab(a[0]).localeCompare(nomLab(b[0]))).forEach(([lab,ms])=>{
    const L=D.labs_full.find(l=>l.id===lab)||{};
    html+=`<h3 class="grp">${esc(nomLab(lab))}<span class="c">${ms.length} tarif${
      ms.length>1?'s':''} relevé${ms.length>1?'s':''}${L.country?' · '+esc(L.country):''}</span></h3>
     <div class="tw" style="max-height:none"><table>
     <thead><tr><th>Modèle</th><th>Identifiant API</th><th>Rôle</th>
     <th class="n">Entrée</th><th class="n">Cache</th><th class="n">Sortie</th>
     <th class="n">Entrée € HT</th><th class="n">Contexte</th></tr></thead><tbody>`;
    ms.sort((a,b)=>a.in-b.in).forEach(m=>{
      html+=`<tr><td><b>${esc(m.name)}</b></td><td><code style="font-size:11px">${
        esc(m.api_id||'—')}</code></td><td>${esc(m.role||'—')}</td>
        <td class="n">$${m.in}</td><td class="n">${m.cached!=null?'$'+m.cached:'—'}</td>
        <td class="n">$${m.out!=null?m.out:'—'}</td>
        <td class="n">${(m.in*D.fx.usd_eur).toFixed(3).replace('.',',')} €</td>
        <td class="n">${m.ctx?(m.ctx/1000).toFixed(0)+'k':'—'}</td></tr>`;
      const notes=[m.offpeak&&`heures creuses : $${m.offpeak.input_per_1m} / $${m.offpeak.output_per_1m}`,
        m.promo,m.tier].filter(Boolean);
      if(notes.length)html+=`<tr><td colspan="8" style="color:var(--ink-3);font-size:11.5px;
        padding-top:0;border-bottom:1px solid var(--line)">↳ ${esc(notes.join(' · '))}</td></tr>`;
    });
    html+=`</tbody></table></div>
     ${L.pricing_url?`<p style="font-size:12px;margin-top:6px"><a href="${esc(L.pricing_url)}"
       rel="noopener">page tarifaire officielle</a></p>`:''}`;
  });
  $('#mod').innerHTML=html;
})();

// ── méthode ───────────────────────────────────────────────────────────────
$('#meth').innerHTML=[
 ['Un score appartient à un triplet',
  "Modèle, harnais et effort de raisonnement. Le catalogue recense 52 harnais distincts sur "+
  "le seul Terminal-Bench, et l'écart qu'ils produisent dépasse souvent l'écart entre deux "+
  "modèles concurrents. Aucun classement n'est publié sans son harnais."],
 ['Aucun chiffre sans source',
  "Chaque tarif porte l'URL réellement consultée, la date du relevé et un niveau de "+
  "provenance. En cas de doute, le champ reste vide plutôt que rempli d'une valeur plausible."],
 ["L'incertitude fait partie de la donnée",
  "Deux modèles dont les intervalles de confiance à 95 % se chevauchent sont à égalité. "+
  "Le validateur refuse les classements qui l'ignorent."],
 ['Le coût se mesure, il ne se déduit pas',
  "Le prix au token ne permet pas de comparer deux niveaux d'effort : le tarif est identique, "+
  "seule la consommation change. Les vues de coût n'utilisent que des dépenses réellement "+
  "mesurées pendant les runs."],
 ['Les trous sont affichés, jamais comblés',
  "Un modèle non mesuré sur un benchmark reste vide. La vue Couverture montre les absences "+
  "en pointillés plutôt que de les interpoler."],
 ['Une disparition est une information',
  "Un outil archivé passe en statut retiré, avec sa date. Il n'est pas supprimé du catalogue."],
].map(([t,d])=>`<div class="bc"><h3>${esc(t)}</h3><p>${d}</p></div>`).join('');

// ── fiches benchmarks ─────────────────────────────────────────────────────
$('#bn').textContent=` — ${D.benchmarks.length} retenus, ${D.rejected.length} écartés`;
$('#blist').innerHTML=D.benchmarks.map(b=>
 `<div class="bc"><h3>${esc(b.name)} ${b.tier==='reference'?
   '<span class="tag ref">référence</span>':'<span class="tag">secondaire</span>'}</h3>
  <p>${esc(b.measures)}</p>${b.caveat?`<span class="cv">▲ ${esc(b.caveat)}</span>`:''}
  <p style="color:var(--ink-3);font-size:11.5px;margin-top:8px">
  provenance : ${esc(b.provenance)}${b.released?' · publié en '+esc(b.released.slice(0,4)):''}</p></div>`).join('');
$('#rj').textContent=`Benchmarks écartés (${D.rejected.length}) — et pourquoi`;
$('#rlist').innerHTML=D.rejected.map(b=>
 `<div class="bc"><h3>${esc(b.benchmark)}</h3><p>${esc(b.reason)}</p></div>`).join('');

$('#foot').innerHTML=`Données de benchmark : <a href="https://epoch.ai/benchmarks" rel="noopener">`+
 `Epoch AI — Capabilities &amp; Benchmarking</a>, sous licence `+
 `<a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC-BY 4.0</a>. `+
 `Page générée par <code>pipeline/build_site.py</code> le ${D.generated} — ne pas éditer à la main.`;

try{const m=localStorage.getItem('tandem.section');
  showSection(SEC.includes(m)?m:'mesures',false);}catch(e){showSection('mesures',false);}
</script>
"""


def main() -> int:
    SITE.mkdir(exist_ok=True)
    p = build_payload()
    out = HTML.replace("__DATA__", json.dumps(p, ensure_ascii=False, separators=(",", ":")))
    (SITE / "index.html").write_text(out, encoding="utf-8")
    kb = (SITE / "index.html").stat().st_size / 1024
    print(f"✓ site/index.html — {kb:.0f} Ko · {p['counts']['scores']} mesures · "
          f"{p['counts']['benchmarks']} benchmarks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
