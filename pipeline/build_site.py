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
    price = {}
    for m in models:
        p = m.get("pricing") or {}
        if p.get("input_per_1m") is not None:
            price[m["id"]] = {"in": p["input_per_1m"], "out": p.get("output_per_1m"),
                              "cached": p.get("input_cached_per_1m")}

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
        "counts": {"labs": len(labs), "models": len(models),
                   "benchmarks": len(benches), "scores": len(rows),
                   "priced": len(price)},
    }


HTML = r"""<title>Observatoire Dev IA</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  color-scheme:light;
  --bg:#fbfcfd; --panel:#ffffff; --line:#e2e6ec; --line-strong:#c8cfd9;
  --ink:#0a0d12; --ink-2:#4c535e; --ink-3:#7d858f;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4;
  --s6:#008300; --s7:#4a3aa7; --s8:#e34948;
  --grid:#edf0f4; --warn:#eda100; --bad:#e34948; --good:#1baf7a;
  --seq1:#cde2fb;--seq2:#9ec5f4;--seq3:#6da7ec;--seq4:#3987e5;--seq5:#256abf;--seq6:#184f95;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --bg:#101317; --panel:#171b21; --line:#2b323b; --line-strong:#3e4753;
  --ink:#ffffff; --ink-2:#bcc3cd; --ink-3:#88909b;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
  --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --grid:#232931; --warn:#c98500; --bad:#e66767; --good:#199e70;
  --seq1:#104281;--seq2:#184f95;--seq3:#256abf;--seq4:#2a78d6;--seq5:#5598e7;--seq6:#9ec5f4;
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#101317; --panel:#171b21; --line:#2b323b; --line-strong:#3e4753;
  --ink:#ffffff; --ink-2:#bcc3cd; --ink-3:#88909b;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
  --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --grid:#232931; --warn:#c98500; --bad:#e66767; --good:#199e70;
  --seq1:#104281;--seq2:#184f95;--seq3:#256abf;--seq4:#2a78d6;--seq5:#5598e7;--seq6:#9ec5f4;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);
 font:14px/1.55 "IBM Plex Sans",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 margin:0;padding:0 20px 72px;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto}
header{padding:38px 0 20px;border-bottom:1px solid var(--line)}
h1{font-family:"IBM Plex Serif",Georgia,serif;font-size:27px;margin:0 0 7px;
 letter-spacing:-.015em;font-weight:600;text-wrap:balance}
.sub{color:var(--ink-2);font-size:14px;margin:0;max-width:74ch}
.meta{color:var(--ink-3);font-size:12px;margin-top:12px;font-variant-numeric:tabular-nums}
h2{font-family:"IBM Plex Serif",Georgia,serif;font-size:19px;margin:36px 0 4px;
 letter-spacing:-.01em;font-weight:600;text-wrap:balance}
h2 .n{color:var(--ink-3);font-weight:400;font-size:13px;margin-left:8px}
.lede{color:var(--ink-2);margin:0 0 16px;max-width:78ch;font-size:13.5px}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:1px;
 background:var(--line);border:1px solid var(--line);border-radius:9px;overflow:hidden;margin:22px 0 4px}
.cell{background:var(--panel);padding:13px 15px}
.cell b{display:block;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:22px;
 font-weight:500;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.cell span{color:var(--ink-3);font-size:10.5px;text-transform:uppercase;letter-spacing:.075em;
 margin-top:2px;display:block}
.note{border-left:3px solid var(--warn);background:var(--panel);padding:12px 15px;
 border-radius:0 8px 8px 0;margin:18px 0;font-size:13px;color:var(--ink-2)}
.note b{color:var(--ink)}
.note.bad{border-left-color:var(--bad)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:18px;margin:14px 0}
.ctrl{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin-bottom:16px}
label.f{display:flex;flex-direction:column;gap:4px;font-size:11px;color:var(--ink-3);
 text-transform:uppercase;letter-spacing:.05em}
select{background:var(--bg);color:var(--ink);border:1px solid var(--line-strong);
 border-radius:7px;padding:6px 9px;font:inherit;font-size:13px;min-width:150px;cursor:pointer}
select:focus-visible{outline:2px solid var(--s1);outline-offset:1px}
.seg{display:flex;gap:2px;background:var(--bg);border:1px solid var(--line-strong);
 border-radius:7px;padding:2px}
.seg button{background:none;border:0;color:var(--ink-2);padding:5px 11px;border-radius:5px;
 font:inherit;font-size:12.5px;cursor:pointer;white-space:nowrap}
.seg button[aria-pressed="true"]{background:var(--s1);color:#fff}
.seg button:focus-visible{outline:2px solid var(--s1);outline-offset:1px}
.chart{width:100%;overflow-x:auto}
svg{display:block;max-width:100%;height:auto;font:inherit}
.gl{stroke:var(--grid);stroke-width:1}
.ax{fill:var(--ink-3);font-size:10.5px;font-family:"IBM Plex Mono",ui-monospace,monospace}
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
td.n{text-align:right;font-family:"IBM Plex Mono",ui-monospace,monospace;
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
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media(max-width:640px){.ctrl{flex-direction:column;align-items:stretch}select{width:100%}}
</style>

<div class="wrap">
<header>
  <h1>Référentiel des solutions de développement par IA</h1>
  <p class="sub">Modèles, harnais et benchmarks — mesurés, sourcés et datés.
     Chaque score porte sa provenance, son protocole et son incertitude.</p>
  <p class="meta" id="meta"></p>
</header>

<div class="strip" id="strip"></div>
<div id="alerts"></div>

<h2>Comparer les modèles</h2>
<p class="lede">Un score n'est jamais l'attribut d'un modèle seul : il dépend du harnais qui l'exécute
et du protocole de mesure. Les barres d'erreur affichent l'intervalle de confiance à 95 % —
quand deux barres se chevauchent, l'écart n'est pas significatif.</p>

<div class="panel">
  <div class="ctrl">
    <div class="seg" id="kind" role="group" aria-label="Type de graphique">
      <button data-k="rank" aria-pressed="true">Classement</button>
      <button data-k="harness" aria-pressed="false">Effet du harnais</button>
      <button data-k="time" aria-pressed="false">Progression</button>
      <button data-k="cover" aria-pressed="false">Couverture</button>
      <button data-k="price" aria-pressed="false">Prix × performance</button>
    </div>
    <label class="f">Benchmark<select id="bench"></select></label>
    <label class="f">Fournisseur<select id="lab"><option value="">Tous</option></select></label>
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

<h2>Benchmarks suivis<span class="n" id="bn"></span></h2>
<p class="lede">Sélection raisonnée. Un benchmark saturé ou remplacé est écarté explicitement :
documenter un rejet évite d'avoir à reposer la question à chaque édition.</p>
<div class="bl" id="blist"></div>
<details><summary id="rj">Benchmarks écartés</summary><div class="bl" id="rlist"></div></details>

<footer id="foot"></footer>
</div>
<div class="tip" id="tip" role="status"></div>

<script id="payload" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('payload').textContent);
const $=s=>document.querySelector(s), tip=$('#tip');
const LABC={anthropic:'--s2',openai:'--s3',google:'--s1',deepseek:'--s7',alibaba:'--s4',
 mistral:'--s5',moonshot:'--s8',zhipu:'--s6',xai:'--ink-2',meta:'--s1',minimax:'--s3',autre:'--ink-3'};
const cv=v=>getComputedStyle(document.documentElement).getPropertyValue(v)||'#888';
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pct=(v,u)=>u==='minutes'?v.toFixed(2):(v*100).toFixed(1)+'%';
let K='rank';

// ── bandeau ────────────────────────────────────────────────────────────────
$('#meta').textContent=`${D.edition} · généré le ${D.generated} · `+
  `${D.counts.scores.toLocaleString('fr-FR')} mesures`;
const C=D.counts;
$('#strip').innerHTML=[['Fournisseurs',C.labs],['Modèles',C.models],
 ['Benchmarks',C.benchmarks],['Mesures',C.scores.toLocaleString('fr-FR')],
 ['Tarifs vérifiés',C.priced+' / '+C.models]]
 .map(([k,v])=>`<div class="cell"><b>${v}</b><span>${k}</span></div>`).join('');

const al=[];
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

// ── utilitaires ────────────────────────────────────────────────────────────
const cur=()=>D.benchmarks.find(b=>b.name===bsel.value)||{};
function rows(){
  let r=D.scores.filter(s=>s.b===bsel.value);
  if(lsel.value)r=r.filter(s=>s.o===lsel.value);
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
    lb.textContent=(s.d||s.m).slice(0,42);g.append(lb);
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
  if(!r.length)return empty('Ce benchmark ne publie pas le harnais utilisé. '+
    'Terminal Bench est le plus riche sur cet axe.');
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
  const CW=40,L=290,T=118,RH=23,W=L+bs.length*CW+24,H=T+ms.length*RH+18;
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Couverture des benchmarks par modèle'});
  bs.forEach((b,j)=>{const t=mk('text',{x:L+j*CW+CW/2,y:T-9,class:'ax',
    transform:`rotate(-52 ${L+j*CW+CW/2} ${T-9})`,'text-anchor':'start'});
    t.textContent=b.length>17?b.slice(0,16)+'…':b;sv.append(t);});
  const mp=new Map();
  D.scores.forEach(s=>{const k=s.m+'|'+s.b;const p=mp.get(k);
    if(!p||s.s>p.s)mp.set(k,s);});
  ms.forEach((m,i)=>{const y=T+i*RH,row=D.scores.find(s=>s.m===m);
    const lb=mk('text',{x:L-9,y:y+15,'text-anchor':'end',class:'lbl'});
    lb.textContent=(row?.d||m).slice(0,42);sv.append(lb);
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
  const r=best(rows()).filter(s=>D.prices[s.m]);
  if(!r.length)return empty('Aucun modèle tarifé pour ce benchmark.');
  const W=940,H=440,L=58,B=46,T=26,R=22;
  const mxp=Math.max(...r.map(s=>D.prices[s.m].in))*1.1,my=Math.max(...r.map(s=>s.s))*1.06;
  const x=v=>L+v/mxp*(W-L-R),y=v=>H-B-v/my*(H-B-T);
  const sv=mk('svg',{viewBox:`0 0 ${W} ${H}`,width:W,role:'group',
    'aria-label':'Prix contre performance'});
  for(let i=0;i<=4;i++){const v=my*i/4;
    sv.append(mk('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),class:'gl'}));
    const t=mk('text',{x:L-8,y:y(v)+4,'text-anchor':'end',class:'ax'});
    t.textContent=(v*100).toFixed(0)+'%';sv.append(t);}
  r.forEach(s=>{const c=cv(LABC[s.l]||'--ink-3'),g=mk('g');
    g.append(mk('circle',{cx:x(D.prices[s.m].in),cy:y(s.s),r:5.5,fill:c,
      stroke:cv('--panel'),'stroke-width':2}));
    wire(g,`<b>${esc(s.d||s.m)}</b>${pct(s.s)} — $${D.prices[s.m].in}/1M entrée`);
    sv.append(g);});
  const xt=mk('text',{x:(L+W)/2,y:H-8,'text-anchor':'middle',class:'ax'});
  xt.textContent='Coût d\'entrée ($ / 1M tokens)';sv.append(xt);
  legend(sv,r,W);render(sv,r,'fraction');
}

function legend(sv,r,W){
  const ls=[...new Set(r.map(s=>s.o))].slice(0,8);
  ls.forEach((o,i)=>{const s=r.find(z=>z.o===o),X=58+i*112;
    sv.append(mk('circle',{cx:X,cy:12,r:4,fill:cv(LABC[s.l]||'--ink-3')}));
    const t=mk('text',{x:X+8,y:16,class:'ax'});t.textContent=o.slice(0,14);sv.append(t);});
}
function empty(msg){$('#chart').innerHTML=`<div class="empty">${esc(msg)}</div>`;
  $('#tbl').innerHTML='';$('#caveat').innerHTML='';}
function render(sv,r,unit){
  $('#chart').innerHTML='';$('#chart').append(sv);
  const b=cur();
  $('#caveat').innerHTML=b.caveat?
    `<div class="note"><b>Réserve de lecture.</b> ${esc(b.caveat)}</div>`:'';
  $('#tbl').innerHTML=r.length?
    '<thead><tr><th>Modèle</th><th>Fournisseur</th><th>Harnais</th>'+
    '<th class="n">Score</th><th class="n">IC95</th><th>Provenance</th><th>Source</th></tr></thead>'+
    '<tbody>'+r.map(s=>`<tr><td>${esc(s.d||s.m)}</td><td>${esc(s.o)}</td>`+
      `<td>${esc(s.h||'—')}</td><td class="n">${pct(s.s,unit)}</td>`+
      `<td class="n">${s.e?'±'+(1.96*s.e*100).toFixed(1):'—'}</td>`+
      `<td>${esc(s.p)}</td><td>${s.u?`<a href="${esc(s.u)}" rel="noopener">lien</a>`:'—'}</td></tr>`
    ).join('')+'</tbody>':'';
}
const DRAW={rank,harness,time,cover,price};
function draw(){DRAW[K]();}
$('#kind').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  K=b.dataset.k;[...$('#kind').children].forEach(x=>
    x.setAttribute('aria-pressed',String(x===b)));draw();});
[bsel,lsel,$('#top')].forEach(el=>el.addEventListener('change',draw));

// ── fiches benchmarks ──────────────────────────────────────────────────────
$('#bn').textContent=D.benchmarks.length+' retenus, '+D.rejected.length+' écartés';
$('#blist').innerHTML=D.benchmarks.map(b=>
 `<div class="bc"><h3>${esc(b.name)} ${b.tier==='reference'?
   '<span class="tag ref">référence</span>':'<span class="tag">secondaire</span>'}</h3>
  <p>${esc(b.measures)}</p>${b.caveat?`<span class="cv">⚠ ${esc(b.caveat)}</span>`:''}
  <p style="color:var(--ink-3);font-size:11.5px;margin-top:8px">
  provenance : ${esc(b.provenance)}${b.released?' · publié en '+esc(b.released.slice(0,4)):''}</p></div>`).join('');
$('#rj').textContent=`Benchmarks écartés (${D.rejected.length}) — et pourquoi`;
$('#rlist').innerHTML=D.rejected.map(b=>
 `<div class="bc"><h3>${esc(b.benchmark)}</h3><p>${esc(b.reason)}</p></div>`).join('');

$('#foot').innerHTML=`Données de benchmark : <a href="https://epoch.ai/benchmarks" rel="noopener">`+
 `Epoch AI — Capabilities &amp; Benchmarking</a>, sous licence `+
 `<a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC-BY 4.0</a>. `+
 `Page générée par <code>pipeline/build_site.py</code> le ${D.generated} — ne pas éditer à la main.`;

draw();
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
