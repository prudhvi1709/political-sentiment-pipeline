"""
Comparison dashboard: 2-week timeline (2-15 June 2026), week + custom filters,
multi-persona comparison (1-3), negativity trend line, and client-pitch panels.

KTR look (pink on dark). Persona series get distinct colours for legibility.
Writes output/index.html
"""
import os
import sys
import json
from timeline_data import DAYS, TIMELINE, PITCH

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ACCENT, ACCENT2, DARK = "#E6007E", "#F5A623", "#14111C"
# distinct colour per persona for comparison lines/bars
PCOLORS = {"ktr": "#E6007E", "bandi-sanjay": "#F47216", "revanth-reddy": "#1F6FB2"}


def load(slug):
    with open(os.path.join(ROOT, "data", f"{slug}_week_data.json")) as f:
        d = json.load(f)
    tl = [{"d": DAYS[i], "pos": p, "neg": n, "neu": u}
          for i, (p, n, u) in enumerate(TIMELINE[slug])]
    return {
        "slug": slug,
        "name": d["person"]["name"],
        "party": d["person"]["party"],
        "role": d["person"]["role"],
        "reconstructed": d["person"].get("reconstructed", False),
        "color": PCOLORS[slug],
        "timeline": tl,
        "issues": d["x_data"]["issues"],
        "top_posts": d["x_data"]["top_posts"],
        "stories": d["stories"],
        "insights": d["insights"],
        "telugu_press": d.get("telugu_press"),
        "news": {
            "topics": d["news_data"]["topics"],
            "publications": d["news_data"]["publications"],
            "sentiment": d["news_data"]["sentiment"],
            "languages": d["news_data"]["languages"],
        },
        "pitch": PITCH[slug],
    }


TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Telangana Political Sentiment - Comparison Cockpit</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{--accent:__ACCENT__;--accent2:__ACCENT2__;--dark:__DARK__;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a1a1a;background:#f4f5f7;}
  .hero{background:var(--dark);color:#fff;padding:26px 40px 22px;border-bottom:6px solid var(--accent);}
  .hero .kicker{color:var(--accent);font-weight:700;letter-spacing:1px;font-size:12px;}
  .hero h1{font-size:28px;margin:6px 0 2px;}
  .hero p{color:#9aa0a6;font-size:13px;}
  .controls{background:#1f1a27;color:#fff;padding:16px 40px;display:flex;flex-wrap:wrap;gap:26px;align-items:center;
        position:sticky;top:0;z-index:20;border-bottom:1px solid #322b3b;}
  .ctl-group{display:flex;flex-direction:column;gap:6px;}
  .ctl-group .lab{font-size:10px;letter-spacing:.5px;color:#9aa0a6;text-transform:uppercase;}
  .pills{display:flex;gap:6px;flex-wrap:wrap;}
  .pill{background:transparent;color:#cfcfcf;border:1px solid #463d52;padding:7px 14px;border-radius:999px;
        font-size:13px;font-weight:600;cursor:pointer;transition:.12s;}
  .pill:hover{border-color:var(--accent);color:#fff;}
  .pill.on{background:var(--accent);border-color:var(--accent);color:#fff;}
  .ppill.on{color:#fff;}
  select{background:#2a2333;color:#fff;border:1px solid #463d52;border-radius:7px;padding:7px 9px;font-size:13px;}
  .rangelbl{font-size:12px;color:#cfcfcf;align-self:flex-end;padding-bottom:7px;}
  .wrap{max-width:1240px;margin:0 auto;padding:24px 24px 70px;}
  .alert{background:#fff4f6;border:1px solid #f3c9d5;border-left:5px solid var(--accent);border-radius:10px;
        padding:12px 16px;margin-bottom:18px;font-size:13.5px;color:#7a1338;}
  .kpis{display:grid;gap:14px;margin-bottom:20px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));}
  .kpi{background:#fff;border-radius:12px;padding:16px 18px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-top:5px solid #ccc;}
  .kpi .nm{font-weight:700;font-size:14px;margin-bottom:8px;display:flex;align-items:center;gap:8px;}
  .kpi .dot{width:10px;height:10px;border-radius:50%;display:inline-block;}
  .kpi .row{display:flex;justify-content:space-between;font-size:12.5px;color:#555;margin:3px 0;}
  .kpi .row b{color:#1a1a1a;font-size:13.5px;}
  .kpi .score{font-size:30px;font-weight:800;line-height:1;}
  .kpi .wow{font-size:12px;font-weight:700;}
  .up{color:#2E9E5B;} .down{color:#D7263D;}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
  .card{background:#fff;border-radius:12px;padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.06);margin-bottom:18px;}
  .card h3{font-size:14px;margin-bottom:12px;color:#222;border-bottom:2px solid #eee;padding-bottom:8px;
        display:flex;justify-content:space-between;align-items:center;}
  .card h3 .sub{font-weight:400;font-size:11px;color:#999;}
  .card.full{grid-column:1/-1;}
  canvas{max-height:300px;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th,td{text-align:left;padding:9px 10px;border-bottom:1px solid #eee;}
  th{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:#888;}
  td .pdot{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:7px;}
  .detail{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px;}
  .pcard{background:#fff;border-radius:12px;padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-top:5px solid #ccc;}
  .pcard h4{font-size:15px;margin-bottom:4px;}
  .pcard .meta{font-size:11px;color:#999;margin-bottom:12px;}
  .blk{margin-bottom:12px;} .blk .t{font-size:10px;letter-spacing:.5px;color:var(--accent);text-transform:uppercase;font-weight:700;margin-bottom:5px;}
  .blk .risk{color:#D7263D;} .blk .win{color:#2E9E5B;}
  .blk p,.blk li{font-size:12.5px;color:#333;margin-bottom:4px;}
  .blk ul{padding-left:16px;}
  .story{border-left:3px solid var(--accent2);padding:5px 10px;margin-bottom:8px;background:#fafafa;}
  .story b{color:var(--accent);font-size:12.5px;} .story span{font-size:11.5px;color:#555;display:block;}
  .recon{font-size:9px;background:var(--accent2);color:#14111C;padding:2px 6px;border-radius:8px;font-weight:700;}
  .src{border:1px solid #eee;border-radius:8px;padding:10px;margin-top:8px;}
  .src .sh{font-size:13px;font-weight:700;display:flex;justify-content:space-between;}
  .src .sl{font-size:11px;color:#888;font-style:italic;margin:2px 0 6px;}
  .src li{font-size:11.5px;list-style:none;padding-left:12px;position:relative;}
  .src li:before{content:"-";position:absolute;left:0;color:var(--accent);}
  @media(max-width:820px){.grid{grid-template-columns:1fr;}.controls{padding:14px 20px;gap:16px;}.hero{padding:20px;}}
</style></head><body>
<div class="hero">
  <div class="kicker">SOCIAL + PRESS SENTIMENT COCKPIT &nbsp;|&nbsp; TELANGANA</div>
  <h1>Two-Week Comparison: KTR &middot; Bandi Sanjay &middot; Revanth Reddy</h1>
  <p>2-15 June 2026 &middot; X conversation + Eenadu/Sakshi/English press &middot; sampled &amp; modelled</p>
</div>
<div class="controls">
  <div class="ctl-group"><span class="lab">Compare</span><div class="pills" id="personaPills"></div></div>
  <div class="ctl-group"><span class="lab">Period</span><div class="pills" id="weekPills"></div></div>
  <div class="ctl-group"><span class="lab">Custom range</span>
    <div class="pills"><select id="fromSel"></select><span class="rangelbl">to</span><select id="toSel"></select></div>
  </div>
</div>
<div class="wrap">
  <div id="alerts"></div>
  <div class="kpis" id="kpis"></div>
  <div class="grid">
    <div class="card full"><h3>Negativity trend <span class="sub">daily % of conversation that is negative</span></h3><canvas id="negTrend"></canvas></div>
    <div class="card"><h3>Conversation volume <span class="sub">daily items</span></h3><canvas id="volTrend"></canvas></div>
    <div class="card"><h3>Net sentiment score <span class="sub">(positive - negative) / total</span></h3><canvas id="netBar"></canvas></div>
    <div class="card"><h3>Share of voice <span class="sub">volume in range</span></h3><canvas id="sov"></canvas></div>
    <div class="card"><h3>Sentiment split <span class="sub">% pos / neg / neu</span></h3><canvas id="split"></canvas></div>
    <div class="card full"><h3>Scorecard</h3><table id="scoreTable"></table></div>
    <div class="card full"><h3>Persona detail <span class="sub">stories, risks, recommended actions, Telugu press</span></h3><div class="detail" id="detail"></div></div>
  </div>
</div>
<script>
const DATA = __DATA__;
const DAYS = __DAYS__;
const ORDER = ["ktr","bandi-sanjay","revanth-reddy"];
const POS='#2E9E5B',NEG='#D7263D',NEU='#9AA0A6';
const WEEKS={ "Week 1 (Jun 2-8)":[0,6], "Week 2 (Jun 9-15)":[7,13], "Both weeks":[0,13] };
let sel = new Set(ORDER);
let range=[0,13];
let charts={};

function totals(slug,a,b){let p=0,n=0,u=0;for(let i=a;i<=b;i++){const t=DATA[slug].timeline[i];p+=t.pos;n+=t.neg;u+=t.neu;}return{p,n,u,tot:p+n+u};}
function net(slug,a,b){const x=totals(slug,a,b);return x.tot?Math.round((x.p-x.n)/x.tot*100):0;}
function destroy(){Object.values(charts).forEach(c=>c&&c.destroy());charts={};}

function render(){
  const sl=ORDER.filter(s=>sel.has(s));
  const [a,b]=range;
  const labels=DAYS.slice(a,b+1);
  // alerts: biggest single-day negativity jump in range among selected
  let alertHtml='';
  sl.forEach(s=>{const tl=DATA[s].timeline;let mx=0,day='';for(let i=Math.max(a,1);i<=b;i++){
    const cur=tl[i].neg/((tl[i].pos+tl[i].neg+tl[i].neu)||1), prev=tl[i-1].neg/((tl[i-1].pos+tl[i-1].neg+tl[i-1].neu)||1);
    if(cur-prev>mx){mx=cur-prev;day=DAYS[i];}}
    if(mx>0.12)alertHtml+=`<div class="alert"><b>${DATA[s].name}:</b> negativity spiked on ${day} (+${Math.round(mx*100)} pts of share) - worth a rapid-response check.</div>`;});
  document.getElementById('alerts').innerHTML=alertHtml;
  // KPIs
  document.getElementById('kpis').innerHTML = sl.map(s=>{
    const d=DATA[s], x=totals(s,a,b), score=net(s,a,b);
    const w1=net(s,0,6), w2=net(s,7,13), delta=w2-w1;
    const negp=x.tot?Math.round(x.n/x.tot*100):0;
    const arrow=delta>=0?`<span class="wow up">&#9650; +${delta} WoW</span>`:`<span class="wow down">&#9660; ${delta} WoW</span>`;
    return `<div class="kpi" style="border-top-color:${d.color}">
      <div class="nm"><span class="dot" style="background:${d.color}"></span>${d.name}${d.reconstructed?' <span class="recon">RECON</span>':''}</div>
      <div class="score" style="color:${score>=0?'#2E9E5B':'#D7263D'}">${score>0?'+':''}${score}</div>
      <div class="row"><span>Net sentiment</span> ${arrow}</div>
      <div class="row"><span>Volume</span><b>${x.tot}</b></div>
      <div class="row"><span>Negative</span><b>${negp}%</b></div></div>`;}).join('');
  destroy();
  // negativity trend
  charts.neg=new Chart(negTrend,{type:'line',data:{labels,datasets:sl.map(s=>{
    const tl=DATA[s].timeline.slice(a,b+1);
    return{label:DATA[s].name,borderColor:DATA[s].color,backgroundColor:DATA[s].color,tension:.3,
      data:tl.map(t=>Math.round(t.neg/((t.pos+t.neg+t.neu)||1)*100))};})},
    options:{plugins:{legend:{position:'bottom'}},scales:{y:{title:{display:true,text:'% negative'},suggestedMax:70}}}});
  // volume trend
  charts.vol=new Chart(volTrend,{type:'line',data:{labels,datasets:sl.map(s=>{
    const tl=DATA[s].timeline.slice(a,b+1);
    return{label:DATA[s].name,borderColor:DATA[s].color,backgroundColor:DATA[s].color+'33',fill:true,tension:.3,
      data:tl.map(t=>t.pos+t.neg+t.neu)};})},options:{plugins:{legend:{position:'bottom'}}}});
  // net sentiment bar
  charts.netb=new Chart(netBar,{type:'bar',data:{labels:sl.map(s=>DATA[s].name),
    datasets:[{data:sl.map(s=>net(s,a,b)),backgroundColor:sl.map(s=>DATA[s].color)}]},
    options:{plugins:{legend:{display:false}},scales:{y:{title:{display:true,text:'net score'}}}}});
  // share of voice
  charts.sov=new Chart(sov,{type:'doughnut',data:{labels:sl.map(s=>DATA[s].name),
    datasets:[{data:sl.map(s=>totals(s,a,b).tot),backgroundColor:sl.map(s=>DATA[s].color)}]},
    options:{plugins:{legend:{position:'bottom'}}}});
  // sentiment split grouped (% pos/neg/neu)
  charts.split=new Chart(split,{type:'bar',data:{labels:sl.map(s=>DATA[s].name),datasets:[
    {label:'Positive',backgroundColor:POS,data:sl.map(s=>{const x=totals(s,a,b);return x.tot?Math.round(x.p/x.tot*100):0;})},
    {label:'Neutral',backgroundColor:NEU,data:sl.map(s=>{const x=totals(s,a,b);return x.tot?Math.round(x.u/x.tot*100):0;})},
    {label:'Negative',backgroundColor:NEG,data:sl.map(s=>{const x=totals(s,a,b);return x.tot?Math.round(x.n/x.tot*100):0;})}]},
    options:{plugins:{legend:{position:'bottom'}},scales:{x:{stacked:true},y:{stacked:true,max:100}}}});
  // scorecard table
  let rows=sl.map(s=>{const x=totals(s,a,b),sc=net(s,a,b);
    const pp=x.tot?Math.round(x.p/x.tot*100):0,np=x.tot?Math.round(x.n/x.tot*100):0,up=x.tot?Math.round(x.u/x.tot*100):0;
    return `<tr><td><span class="pdot" style="background:${DATA[s].color}"></span>${DATA[s].name}</td>
      <td><b>${x.tot}</b></td><td style="color:#2E9E5B">${pp}%</td><td style="color:#D7263D">${np}%</td>
      <td>${up}%</td><td style="font-weight:700;color:${sc>=0?'#2E9E5B':'#D7263D'}">${sc>0?'+':''}${sc}</td>
      <td style="font-size:12px;color:#7a1338">${DATA[s].pitch.risk}</td></tr>`;}).join('');
  document.getElementById('scoreTable').innerHTML=`<thead><tr><th>Persona</th><th>Volume</th><th>Pos</th><th>Neg</th><th>Neu</th><th>Net</th><th>Top risk</th></tr></thead><tbody>${rows}</tbody>`;
  // detail
  document.getElementById('detail').innerHTML = sl.map(s=>{const d=DATA[s];
    return `<div class="pcard" style="border-top-color:${d.color}">
      <h4>${d.name}${d.reconstructed?' <span class="recon">RECON</span>':''}</h4>
      <div class="meta">${d.party} &middot; ${d.role}</div>
      <div class="blk"><div class="t risk">Top risk</div><p>${d.pitch.risk}</p></div>
      <div class="blk"><div class="t win">Top opportunity</div><p>${d.pitch.win}</p></div>
      <div class="blk"><div class="t">Recommended actions</div><ul>${d.pitch.actions.map(x=>`<li>${x}</li>`).join('')}</ul></div>
      <div class="blk"><div class="t">Defining stories</div>${d.stories.slice(0,3).map(x=>`<div class="story"><b>${x.title}</b><span>${x.detail}</span></div>`).join('')}</div>
      ${d.telugu_press?`<div class="blk"><div class="t">Eenadu &amp; Sakshi - ${d.telugu_press.window}</div>
        <div class="src"><div class="sh"><span>Eenadu</span><span>${d.telugu_press.eenadu.count} articles</span></div><div class="sl">${d.telugu_press.eenadu.lean}</div><ul>${d.telugu_press.eenadu.headlines.slice(0,3).map(h=>`<li>${h}</li>`).join('')}</ul></div>
        <div class="src"><div class="sh"><span>Sakshi</span><span>${d.telugu_press.sakshi.count} articles</span></div><div class="sl">${d.telugu_press.sakshi.lean}</div><ul>${d.telugu_press.sakshi.headlines.slice(0,3).map(h=>`<li>${h}</li>`).join('')}</ul></div></div>`:''}
    </div>`;}).join('');
}

// build controls
const pp=document.getElementById('personaPills');
ORDER.forEach(s=>{const b=document.createElement('button');b.className='pill ppill on';
  b.style.borderColor=DATA[s].color;b.textContent=DATA[s].name;b.dataset.s=s;
  b.onclick=()=>{if(sel.has(s)){if(sel.size>1){sel.delete(s);b.classList.remove('on');b.style.background='';}}
    else{sel.add(s);b.classList.add('on');b.style.background=DATA[s].color;}render();};
  b.style.background=DATA[s].color;pp.appendChild(b);});
const wp=document.getElementById('weekPills');
Object.keys(WEEKS).forEach((k,i)=>{const b=document.createElement('button');b.className='pill'+(k==='Both weeks'?' on':'');
  b.textContent=k;b.onclick=()=>{range=WEEKS[k].slice();document.querySelectorAll('#weekPills .pill').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');syncSel();render();};wp.appendChild(b);});
const fromSel=document.getElementById('fromSel'),toSel=document.getElementById('toSel');
DAYS.forEach((d,i)=>{fromSel.add(new Option(d,i));toSel.add(new Option(d,i));});
fromSel.value=0;toSel.value=13;
function syncSel(){fromSel.value=range[0];toSel.value=range[1];}
function customChange(){let a=+fromSel.value,b=+toSel.value;if(a>b){[a,b]=[b,a];}range=[a,b];
  document.querySelectorAll('#weekPills .pill').forEach(x=>x.classList.remove('on'));syncSel();render();}
fromSel.onchange=customChange;toSel.onchange=customChange;
render();
</script></body></html>"""


def build(out_path):
    data = {s: load(s) for s in ["ktr", "bandi-sanjay", "revanth-reddy"]}
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(data))
            .replace("__DAYS__", json.dumps(DAYS))
            .replace("__ACCENT2__", ACCENT2)
            .replace("__ACCENT__", ACCENT)
            .replace("__DARK__", DARK))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    out = build(os.path.join(ROOT, "output", "index.html"))
    print("comparison dashboard ->", out)
