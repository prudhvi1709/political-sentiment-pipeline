"""
Unified single-file dashboard for all personas, in the KTR look
(BRS pink on dark) with a persona switcher. Same palette for everyone,
as requested. Chart.js via CDN.

Usage: python3 build_unified_dashboard.py ktr bandi-sanjay revanth-reddy
Writes output/index.html
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# KTR palette, applied to all personas by request
ACCENT = "#E6007E"
ACCENT2 = "#F5A623"
DARK = "#14111C"

TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Weekly Political Sentiment - Telangana</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root { --accent:__ACCENT__; --accent2:__ACCENT2__; --dark:__DARK__; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; color:#1a1a1a; background:#f4f5f7; }
  .hero { background:var(--dark); color:#fff; padding:34px 48px 0; border-bottom:6px solid var(--accent); }
  .hero .kicker { color:var(--accent); font-weight:700; letter-spacing:1px; font-size:13px; }
  .hero h1 { font-size:38px; margin:6px 0 2px; }
  .hero .role { color:#cfcfcf; font-size:15px; }
  .hero .week { color:#9aa0a6; margin-top:8px; font-size:13px; }
  .switch { display:flex; gap:8px; margin-top:22px; }
  .switch button { background:transparent; color:#cfcfcf; border:1px solid #3a3340;
        padding:10px 20px; border-radius:999px 999px 0 0; font-size:14px; font-weight:600;
        cursor:pointer; transition:all .15s; border-bottom:none; }
  .switch button:hover { color:#fff; border-color:var(--accent); }
  .switch button.active { background:#f4f5f7; color:var(--accent); border-color:var(--accent); }
  .recon { display:inline-block; margin-left:8px; font-size:10px; color:#14111C; background:var(--accent2);
        padding:2px 7px; border-radius:10px; font-weight:700; vertical-align:middle; }
  .wrap { max-width:1180px; margin:0 auto; padding:26px 24px 60px; }
  .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }
  .stat { background:#fff; border-radius:12px; padding:18px; border-left:6px solid var(--accent);
        box-shadow:0 1px 4px rgba(0,0,0,.06); }
  .stat .v { font-size:30px; font-weight:800; color:var(--accent); }
  .stat .l { color:#555; font-size:12.5px; margin-top:4px; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
  .card { background:#fff; border-radius:12px; padding:20px; box-shadow:0 1px 4px rgba(0,0,0,.06); margin-bottom:18px; }
  .card h3 { font-size:15px; margin-bottom:14px; color:#222; border-bottom:2px solid #eee; padding-bottom:8px; }
  .card.full { grid-column:1/-1; }
  canvas { max-height:300px; }
  .story { border-left:4px solid var(--accent2); padding:8px 14px; margin-bottom:12px; background:#fafafa; }
  .story h4 { color:var(--accent); font-size:14px; }
  .story p { color:#444; font-size:13px; margin-top:3px; }
  ul.ins { padding-left:20px; } ul.ins li { margin-bottom:8px; color:#333; font-size:14px; }
  .post { display:flex; justify-content:space-between; gap:12px; border-bottom:1px solid #eee; padding:10px 0; }
  .post span { color:var(--accent); font-weight:700; white-space:nowrap; }
  .tp { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  .tp .src { border:1px solid #eee; border-radius:10px; padding:14px; }
  .tp .src h4 { font-size:15px; color:var(--dark); display:flex; justify-content:space-between; align-items:center; }
  .tp .src .cnt { color:#fff; background:var(--accent); border-radius:8px; padding:2px 10px; font-size:13px; }
  .tp .src .lean { font-size:12px; color:#777; margin:4px 0 10px; font-style:italic; }
  .tp .src li { font-size:12.5px; color:#333; margin-bottom:7px; list-style:none; padding-left:14px; position:relative; }
  .tp .src li:before { content:"-"; position:absolute; left:0; color:var(--accent); }
  .tag { font-size:11px; font-weight:700; letter-spacing:.5px; color:var(--accent); text-transform:uppercase; }
  @media(max-width:760px){ .stats,.grid,.tp{grid-template-columns:1fr;} .hero{padding:24px 20px 0;} }
</style></head><body>
<div class="hero">
  <div class="kicker">WEEKLY MEDIA &amp; SOCIAL SENTIMENT &nbsp;|&nbsp; TELANGANA</div>
  <h1 id="pName">-</h1>
  <div class="role" id="pRole">-</div>
  <div class="week" id="pWeek">-</div>
  <div class="switch" id="switch"></div>
</div>
<div class="wrap">
  <div class="stats" id="stats"></div>
  <div class="grid">
    <div class="card"><h3>X sentiment</h3><canvas id="xSent"></canvas></div>
    <div class="card"><h3>News sentiment</h3><canvas id="nSent"></canvas></div>
    <div class="card full"><h3>Daily X volume by sentiment</h3><canvas id="xDaily"></canvas></div>
    <div class="card"><h3>Top negative issues (X)</h3><canvas id="xIssues"></canvas></div>
    <div class="card"><h3>News topics</h3><canvas id="nTopics"></canvas></div>
    <div class="card"><h3>Publications</h3><canvas id="nPubs"></canvas></div>
    <div class="card"><h3>Coverage language</h3><canvas id="nLangs"></canvas></div>
    <div class="card full">
      <h3>Eenadu &amp; Sakshi <span class="tag" id="tpWindow"></span></h3>
      <div class="tp" id="tp"></div>
    </div>
    <div class="card full"><h3>Top posts this week</h3><div id="posts"></div></div>
    <div class="card"><h3>Defining stories</h3><div id="stories"></div></div>
    <div class="card"><h3>Key insights</h3><ul class="ins" id="insights"></ul></div>
  </div>
</div>
<script>
const DATA = __DATA__;
const ORDER = __ORDER__;
const POS='#2E9E5B', NEG='#D7263D', NEU='#9AA0A6', AC='__ACCENT__', AC2='__ACCENT2__';
let charts = {};

function destroyCharts(){ Object.values(charts).forEach(c=>c&&c.destroy()); charts={}; }
function donut(id,s){ charts[id]=new Chart(document.getElementById(id),{type:'doughnut',
  data:{labels:['Positive','Negative','Neutral'],datasets:[{data:[s.positive,s.negative,s.neutral],backgroundColor:[POS,NEG,NEU]}]},
  options:{plugins:{legend:{position:'bottom'}}}}); }
function hbar(id,arr,color){ arr=[...arr].sort((a,b)=>a.count-b.count);
  charts[id]=new Chart(document.getElementById(id),{type:'bar',
  data:{labels:arr.map(i=>i.label),datasets:[{data:arr.map(i=>i.count),backgroundColor:color}]},
  options:{indexAxis:'y',plugins:{legend:{display:false}}}}); }

function render(slug){
  const d = DATA[slug];
  const x = d.x_data, n = d.news_data;
  const xt = x.sentiment.positive+x.sentiment.negative+x.sentiment.neutral || 1;
  const nt = n.sentiment.positive+n.sentiment.negative+n.sentiment.neutral || 1;
  const recon = d.person.reconstructed ? '<span class="recon">RECONSTRUCTED</span>' : '';
  document.getElementById('pName').innerHTML = d.person.name + recon;
  document.getElementById('pRole').textContent = d.person.party + '  -  ' + d.person.role;
  document.getElementById('pWeek').textContent = 'Week of ' + d.week.label;
  document.getElementById('stats').innerHTML =
    stat(x.sample_size||xt,'X items sampled') +
    stat(Math.round(x.sentiment.negative*100/xt)+'%','Negative on X') +
    stat(n.article_count||nt,'News articles') +
    stat(Math.round(n.sentiment.positive*100/nt)+'%','Positive in press');
  destroyCharts();
  donut('xSent',x.sentiment); donut('nSent',n.sentiment);
  charts.xDaily=new Chart(document.getElementById('xDaily'),{type:'bar',
    data:{labels:x.daily.map(r=>r.date),datasets:[
      {label:'Positive',data:x.daily.map(r=>r.pos||0),backgroundColor:POS},
      {label:'Neutral',data:x.daily.map(r=>r.neu||0),backgroundColor:NEU},
      {label:'Negative',data:x.daily.map(r=>r.neg||0),backgroundColor:NEG}]},
    options:{responsive:true,scales:{x:{stacked:true},y:{stacked:true}}}});
  hbar('xIssues',x.issues,NEG); hbar('nTopics',n.topics,AC); hbar('nPubs',n.publications,AC2);
  charts.nLangs=new Chart(document.getElementById('nLangs'),{type:'doughnut',
    data:{labels:Object.keys(n.languages),datasets:[{data:Object.values(n.languages),backgroundColor:[AC,AC2,NEU,'#C7C7C7']}]},
    options:{plugins:{legend:{position:'bottom'}}}});
  // telugu press
  const tp = d.telugu_press;
  document.getElementById('tpWindow').textContent = tp ? tp.window : '';
  document.getElementById('tp').innerHTML = tp ? (srcCard('Eenadu',tp.eenadu)+srcCard('Sakshi',tp.sakshi)) : '';
  document.getElementById('posts').innerHTML = (x.top_posts||[]).slice(0,5).map(p=>
    `<div class="post"><span style="color:#1a1a1a;font-weight:400">${p.text}</span><span>${(p.views||0).toLocaleString()} views</span></div>`).join('');
  document.getElementById('stories').innerHTML = (d.stories||[]).map(s=>
    `<div class="story"><h4>${s.title}</h4><p>${s.detail}</p></div>`).join('');
  document.getElementById('insights').innerHTML = (d.insights||[]).map(i=>`<li>${i}</li>`).join('');
  document.querySelectorAll('#switch button').forEach(b=>b.classList.toggle('active', b.dataset.slug===slug));
}
function stat(v,l){ return `<div class="stat"><div class="v">${v}</div><div class="l">${l}</div></div>`; }
function srcCard(name,o){ if(!o) return '';
  return `<div class="src"><h4>${name}<span class="cnt">${o.count} articles</span></h4>
    <div class="lean">${o.lean}</div><ul>${o.headlines.map(h=>`<li>${h}</li>`).join('')}</ul></div>`; }

const sw = document.getElementById('switch');
ORDER.forEach(slug=>{ const b=document.createElement('button'); b.textContent=DATA[slug].person.name;
  b.dataset.slug=slug; b.onclick=()=>render(slug); sw.appendChild(b); });
render(ORDER[0]);
</script></body></html>"""


def build(slugs, out_path):
    data = {}
    for s in slugs:
        with open(os.path.join(ROOT, "data", f"{s}_week_data.json")) as f:
            data[s] = json.load(f)
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(data))
            .replace("__ORDER__", json.dumps(slugs))
            .replace("__ACCENT2__", ACCENT2)
            .replace("__ACCENT__", ACCENT)
            .replace("__DARK__", DARK))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    slugs = sys.argv[1:] or ["ktr", "bandi-sanjay", "revanth-reddy"]
    out = build(slugs, os.path.join(ROOT, "output", "index.html"))
    print("unified dashboard ->", out)
