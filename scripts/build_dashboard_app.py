"""
Multi-view dashboard app (single file): a Compare tab + a full deep-dive tab
per persona, with the press/digital-media analysis included, plus a
cross-cutting "shared narratives" matrix that scores the same event
differently per leader (persona-relative sentiment).

KTR look (pink on dark). Writes output/index.html
"""
import os
import json
from timeline_data import DAYS, TIMELINE, PITCH, SHARED_NARRATIVES
from evidence_data import EVIDENCE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ACCENT, ACCENT2, DARK = "#E6007E", "#F5A623", "#14111C"
PCOLORS = {"ktr": "#E6007E", "bandi-sanjay": "#F47216", "revanth-reddy": "#1F6FB2"}


def load(slug):
    with open(os.path.join(ROOT, "data", f"{slug}_week_data.json")) as f:
        d = json.load(f)
    tl = [{"d": DAYS[i], "pos": p, "neg": n, "neu": u}
          for i, (p, n, u) in enumerate(TIMELINE[slug])]
    nd = d["news_data"]
    return {
        "slug": slug, "name": d["person"]["name"], "party": d["person"]["party"],
        "role": d["person"]["role"], "reconstructed": d["person"].get("reconstructed", False),
        "color": PCOLORS[slug], "timeline": tl,
        "official_posts": d["x_data"].get("official_posts", 0),
        "issues": d["x_data"]["issues"],
        "issue_notes": d["x_data"].get("issue_notes", []),
        "top_posts": d["x_data"]["top_posts"],
        "stories": d["stories"], "insights": d["insights"],
        "telugu_press": d.get("telugu_press"),
        "news": {"topics": nd["topics"], "publications": nd["publications"],
                 "sentiment": nd["sentiment"], "languages": nd["languages"],
                 "article_count": nd.get("article_count", 0),
                 "topic_notes": nd.get("topic_notes", []), "notes": nd.get("notes", [])},
        "pitch": PITCH[slug],
        "evidence": EVIDENCE[slug],
    }


TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Telangana Political Sentiment - Cockpit</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{--accent:__ACCENT__;--accent2:__ACCENT2__;--dark:__DARK__;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a1a1a;background:#f4f5f7;}
  .hero{background:var(--dark);color:#fff;padding:22px 40px 0;border-bottom:6px solid var(--accent);}
  .hero .kicker{color:var(--accent);font-weight:700;letter-spacing:1px;font-size:12px;}
  .hero h1{font-size:24px;margin:6px 0 2px;}
  .hero p{color:#9aa0a6;font-size:12.5px;margin-bottom:14px;}
  .tabs{display:flex;gap:4px;}
  .tab{background:transparent;color:#cfcfcf;border:none;padding:11px 20px;font-size:14px;font-weight:600;
        cursor:pointer;border-bottom:3px solid transparent;}
  .tab:hover{color:#fff;}
  .tab.on{color:#fff;border-bottom-color:var(--accent);}
  .controls{background:#1f1a27;color:#fff;padding:13px 40px;display:flex;flex-wrap:wrap;gap:24px;align-items:flex-end;
        position:sticky;top:0;z-index:20;border-bottom:1px solid #322b3b;}
  .ctl-group{display:flex;flex-direction:column;gap:6px;}
  .ctl-group .lab{font-size:10px;letter-spacing:.5px;color:#9aa0a6;text-transform:uppercase;}
  .pills{display:flex;gap:6px;flex-wrap:wrap;align-items:center;}
  .pill{background:transparent;color:#cfcfcf;border:1px solid #463d52;padding:6px 13px;border-radius:999px;
        font-size:12.5px;font-weight:600;cursor:pointer;transition:.12s;}
  .pill:hover{border-color:var(--accent);color:#fff;} .pill.on{background:var(--accent);border-color:var(--accent);color:#fff;}
  select{background:#2a2333;color:#fff;border:1px solid #463d52;border-radius:7px;padding:6px 9px;font-size:12.5px;}
  .rangelbl{font-size:12px;color:#cfcfcf;padding:0 2px;}
  .wrap{max-width:1240px;margin:0 auto;padding:24px 24px 70px;}
  .alert{background:#fff4f6;border:1px solid #f3c9d5;border-left:5px solid var(--accent);border-radius:10px;
        padding:11px 15px;margin-bottom:16px;font-size:13px;color:#7a1338;}
  .kpis{display:grid;gap:14px;margin-bottom:20px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));}
  .kpi{background:#fff;border-radius:12px;padding:15px 17px;box-shadow:0 1px 4px rgba(0,0,0,.06);border-top:5px solid #ccc;}
  .kpi .nm{font-weight:700;font-size:13.5px;margin-bottom:6px;display:flex;align-items:center;gap:7px;}
  .kpi .dot{width:10px;height:10px;border-radius:50%;display:inline-block;}
  .kpi .score{font-size:28px;font-weight:800;line-height:1.1;}
  .kpi .row{display:flex;justify-content:space-between;font-size:12px;color:#555;margin:3px 0;}
  .kpi .row b{color:#1a1a1a;}
  .wow{font-size:11.5px;font-weight:700;} .up{color:#2E9E5B;} .down{color:#D7263D;}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
  .card{background:#fff;border-radius:12px;padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.06);margin-bottom:18px;}
  .card h3{font-size:14px;margin-bottom:12px;color:#222;border-bottom:2px solid #eee;padding-bottom:8px;
        display:flex;justify-content:space-between;align-items:baseline;gap:10px;}
  .card h3 .sub{font-weight:400;font-size:11px;color:#999;}
  .card.full{grid-column:1/-1;} canvas{max-height:300px;}
  .secthead{font-size:12px;font-weight:700;letter-spacing:.6px;color:var(--accent);text-transform:uppercase;
        margin:6px 0 12px;border-left:4px solid var(--accent);padding-left:10px;}
  table{width:100%;border-collapse:collapse;font-size:13px;} th,td{text-align:left;padding:9px 10px;border-bottom:1px solid #eee;}
  th{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:#888;}
  .pdot{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:7px;}
  .pol{font-weight:800;padding:2px 9px;border-radius:7px;font-size:12px;display:inline-block;min-width:74px;text-align:center;}
  .pol.pos{background:#e6f5ec;color:#1e7a44;} .pol.neg{background:#fdeaed;color:#c01933;}
  .pol.neu{background:#eef0f2;color:#666;} .pol.mixed{background:#fff3e0;color:#a85b00;}
  .post{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid #eee;padding:9px 0;font-size:13px;}
  .post span.v{color:var(--accent);font-weight:700;white-space:nowrap;}
  .story{border-left:4px solid var(--accent2);padding:7px 12px;margin-bottom:10px;background:#fafafa;}
  .story b{color:var(--accent);font-size:13px;} .story span{font-size:12px;color:#555;display:block;margin-top:2px;}
  ul.ins{padding-left:18px;} ul.ins li{margin-bottom:7px;color:#333;font-size:13px;}
  .blk{margin-bottom:12px;} .blk .t{font-size:10px;letter-spacing:.5px;text-transform:uppercase;font-weight:700;margin-bottom:5px;color:var(--accent);}
  .blk .risk{color:#D7263D;} .blk .win{color:#2E9E5B;} .blk p,.blk li{font-size:13px;color:#333;margin-bottom:4px;}
  .recon{font-size:9px;background:var(--accent2);color:#14111C;padding:2px 6px;border-radius:8px;font-weight:700;}
  .src{border:1px solid #eee;border-radius:8px;padding:11px;margin-top:8px;}
  .src .sh{font-size:13px;font-weight:700;display:flex;justify-content:space-between;}
  .src .sl{font-size:11px;color:#888;font-style:italic;margin:2px 0 6px;}
  .src li{font-size:12px;list-style:none;padding-left:12px;position:relative;margin-bottom:5px;}
  .src li:before{content:"-";position:absolute;left:0;color:var(--accent);}
  .note{font-size:12.5px;color:#555;background:#faf7fb;border:1px dashed #e3c6d6;border-radius:8px;padding:10px 12px;margin-top:10px;}
  .clickhint{font-size:11px;color:#b0539a;font-weight:600;}
  .clickable{cursor:pointer;}
  #scrim{position:fixed;inset:0;background:rgba(10,8,14,.45);opacity:0;pointer-events:none;transition:.2s;z-index:40;}
  #scrim.open{opacity:1;pointer-events:auto;}
  #drawer{position:fixed;top:0;right:0;height:100%;width:440px;max-width:92vw;background:#fff;z-index:50;
        transform:translateX(100%);transition:transform .22s ease;box-shadow:-8px 0 30px rgba(0,0,0,.2);display:flex;flex-direction:column;}
  #drawer.open{transform:none;}
  #drawer .dh{background:var(--dark);color:#fff;padding:18px 20px;}
  #drawer .dh .et{font-size:11px;letter-spacing:.5px;color:var(--accent);text-transform:uppercase;font-weight:700;}
  #drawer .dh h3{font-size:17px;margin:5px 0 3px;} #drawer .dh p{font-size:12px;color:#9aa0a6;}
  #drawer .dh .x{position:absolute;top:16px;right:18px;cursor:pointer;font-size:22px;color:#cfcfcf;background:none;border:none;}
  #drawer .body{padding:16px 20px;overflow-y:auto;flex:1;}
  .cite{border:1px solid #eee;border-left:4px solid #ccc;border-radius:9px;padding:12px 14px;margin-bottom:12px;}
  .cite .meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
  .cite .badge{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;padding:2px 8px;border-radius:7px;}
  .cite .badge.x{background:#e8f1fb;color:#1f6fb2;} .cite .badge.press{background:#f3eef7;color:#7a3fa0;}
  .cite .dt{font-size:11px;color:#999;}
  .cite .txt{font-size:13.5px;color:#1a1a1a;line-height:1.5;}
  .cite a{display:inline-block;margin-top:8px;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;}
  .cite a:hover{text-decoration:underline;}
  .cite .who{font-size:11.5px;color:#777;margin-top:3px;}
  @media(max-width:820px){.grid{grid-template-columns:1fr;}.controls,.hero{padding-left:20px;padding-right:20px;}}
</style></head><body>
<div class="hero">
  <div class="kicker">SOCIAL + PRESS SENTIMENT COCKPIT &nbsp;|&nbsp; TELANGANA &nbsp;|&nbsp; 16 JUN - 13 JUL 2026</div>
  <h1 id="heroTitle">Compare</h1>
  <p id="heroSub">X conversation + Eenadu / Sakshi / English press &middot; sentiment scored per persona</p>
  <div class="tabs" id="tabs"></div>
</div>
<div class="controls">
  <div class="ctl-group" id="personaCtl"><span class="lab">Compare</span><div class="pills" id="personaPills"></div></div>
  <div class="ctl-group"><span class="lab">Period</span><div class="pills" id="weekPills"></div></div>
  <div class="ctl-group"><span class="lab">Custom range</span>
    <div class="pills"><select id="fromSel"></select><span class="rangelbl">to</span><select id="toSel"></select></div></div>
</div>
<div class="wrap">
  <div id="compareView"></div>
  <div id="personaView" style="display:none"></div>
</div>
<div id="scrim" onclick="closeDrawer()"></div>
<div id="drawer">
  <div class="dh" style="position:relative"><button class="x" onclick="closeDrawer()">&times;</button>
    <div class="et" id="dEt">Evidence</div><h3 id="dTitle">-</h3><p id="dSub">-</p></div>
  <div class="body" id="dBody"></div>
</div>
<script>
const DATA=__DATA__, DAYS=__DAYS__, SHARED=__SHARED__;
const ORDER=["ktr","bandi-sanjay","revanth-reddy"];
const POS='#2E9E5B',NEG='#D7263D',NEU='#9AA0A6',AC='__ACCENT__',AC2='__ACCENT2__';
const WEEKS={"Week 1 (Jun 16-22)":[0,6],"Week 2 (Jun 23-29)":[7,13],"Week 3 (Jun 30-Jul 6)":[14,20],"Week 4 (Jul 7-13)":[21,27],"All 4 weeks":[0,27]};
const POLTXT={pos:'Positive',neg:'Negative',neu:'Neutral',mixed:'Mixed'};
let view='ktr', sel=new Set(ORDER), range=[0,27], charts={};
const POLTXT2={pos:'Positive',neg:'Negative',neu:'Neutral'};

/* ---------- CLICK-TO-CITE DRILL-DOWN ---------- */
function evColor(s){return s==='pos'?POS:s==='neg'?NEG:NEU;}
function matchEv(slug,f){
  let items=DATA[slug].evidence.slice();
  let strict=items.filter(e=>(!f.sent||e.sent===f.sent)&&(!f.kind||e.kind===f.kind)&&(!f.label||e.tag===f.label||e.src===f.label));
  if(strict.length) return strict;
  let loose=items.filter(e=>(!f.sent||e.sent===f.sent)&&(!f.kind||e.kind===f.kind));
  if(loose.length) return loose;
  return items.filter(e=>(!f.kind||e.kind===f.kind));
}
function openDrawer(slug,f,title,sub){
  const items=matchEv(slug,f);
  document.getElementById('dEt').textContent=DATA[slug].name+(DATA[slug].reconstructed?' (reconstructed)':'');
  document.getElementById('dTitle').textContent=title;
  document.getElementById('dSub').textContent=sub+' - '+items.length+' source'+(items.length===1?'':'s');
  document.getElementById('dBody').innerHTML=items.map(e=>`
    <div class="cite" style="border-left-color:${evColor(e.sent)}">
      <div class="meta"><span class="badge ${e.kind}">${e.kind==='x'?'X / social':'Press'}</span><span class="dt">${e.date}</span></div>
      <div class="txt">${e.text}</div><div class="who">${e.src} &middot; ${POLTXT2[e.sent]} for this leader</div>
      <a href="${e.url}" target="_blank" rel="noopener">View source &#8599;</a></div>`).join('')
    + `<div class="note">Press links open the original article. X items are representative captured samples (links open the source profile/search).${DATA[slug].reconstructed?' KTR data is reconstructed from the prior session.':''}</div>`;
  document.getElementById('scrim').classList.add('open');
  document.getElementById('drawer').classList.add('open');
}
function closeDrawer(){document.getElementById('scrim').classList.remove('open');document.getElementById('drawer').classList.remove('open');}
function clickHandler(slug,kind,getFilter){return (evt,els)=>{if(!els||!els.length)return;const i=els[0].index,di=els[0].datasetIndex;getFilter(slug,kind,i,di);};}

function tot(s,a,b){let p=0,n=0,u=0;for(let i=a;i<=b;i++){const t=DATA[s].timeline[i];p+=t.pos;n+=t.neg;u+=t.neu;}return{p,n,u,tot:p+n+u};}
function net(s,a,b){const x=tot(s,a,b);return x.tot?Math.round((x.p-x.n)/x.tot*100):0;}
function destroy(){Object.values(charts).forEach(c=>c&&c.destroy());charts={};}
function donut(id,labels,vals,colors,onPick){charts[id]=new Chart(document.getElementById(id),{type:'doughnut',
  data:{labels,datasets:[{data:vals,backgroundColor:colors}]},
  options:{plugins:{legend:{position:'bottom'}},onClick:(e,els)=>{if(onPick&&els.length)onPick(labels[els[0].index],els[0].index);}}});}
function hbar(id,arr,color,onPick){arr=[...arr].sort((a,b)=>a.count-b.count);const labels=arr.map(i=>i.label);
  charts[id]=new Chart(document.getElementById(id),{type:'bar',
  data:{labels,datasets:[{data:arr.map(i=>i.count),backgroundColor:color}]},
  options:{indexAxis:'y',plugins:{legend:{display:false}},onClick:(e,els)=>{if(onPick&&els.length)onPick(labels[els[0].index]);}}});}

/* ---------- COMPARE VIEW ---------- */
function compareHTML(){return `
  <div id="alerts"></div><div class="kpis" id="kpis"></div>
  <div class="grid">
    <div class="card full"><h3>Negativity trend <span class="sub">daily % of conversation negative for each leader</span></h3><canvas id="cmpNeg"></canvas></div>
    <div class="card"><h3>Conversation volume <span class="sub">daily items</span></h3><canvas id="cmpVol"></canvas></div>
    <div class="card"><h3>Net sentiment score <span class="sub">(pos-neg)/total</span></h3><canvas id="cmpNet"></canvas></div>
    <div class="card"><h3>Share of voice <span class="sub">volume in range</span></h3><canvas id="cmpSov"></canvas></div>
    <div class="card"><h3>Sentiment split <span class="sub">% pos / neg / neu</span></h3><canvas id="cmpSplit"></canvas></div>
    <div class="card full"><h3>Scorecard</h3><table id="scoreTable"></table></div>
    <div class="card full"><h3>Shared narratives <span class="sub">the same storyline, scored for each leader</span></h3>
      <table id="sharedTable"></table>
      <div class="note"><b>Why this matters:</b> sentiment is measured <i>for each persona</i>, not for the topic. A post attacking Revanth's HYDRAA-Hitler remark is <span class="pol neg">Negative</span> for Revanth but <span class="pol pos">Positive</span> for KTR, who gains from the attack.</div>
    </div>
  </div>`;}

function renderCompare(){
  const sl=ORDER.filter(s=>sel.has(s)); const [a,b]=range; const labels=DAYS.slice(a,b+1);
  let al='';sl.forEach(s=>{const tl=DATA[s].timeline;let mx=0,day='';for(let i=Math.max(a,1);i<=b;i++){
    const c=tl[i].neg/((tl[i].pos+tl[i].neg+tl[i].neu)||1),p=tl[i-1].neg/((tl[i-1].pos+tl[i-1].neg+tl[i-1].neu)||1);
    if(c-p>mx){mx=c-p;day=DAYS[i];}}if(mx>0.12)al+=`<div class="alert"><b>${DATA[s].name}:</b> negativity spiked on ${day} (+${Math.round(mx*100)} pts) - worth a rapid-response check.</div>`;});
  document.getElementById('alerts').innerHTML=al;
  document.getElementById('kpis').innerHTML=sl.map(s=>{const d=DATA[s],x=tot(s,a,b),sc=net(s,a,b);
    const dl=net(s,21,27)-net(s,14,20),np=x.tot?Math.round(x.n/x.tot*100):0;
    const ar=dl>=0?`<span class="wow up">&#9650; +${dl} WoW</span>`:`<span class="wow down">&#9660; ${dl} WoW</span>`;
    return `<div class="kpi" style="border-top-color:${d.color}"><div class="nm"><span class="dot" style="background:${d.color}"></span>${d.name}${d.reconstructed?' <span class="recon">RECON</span>':''}</div>
      <div class="score" style="color:${sc>=0?'#2E9E5B':'#D7263D'}">${sc>0?'+':''}${sc}</div>
      <div class="row"><span>Net sentiment</span>${ar}</div><div class="row"><span>Volume</span><b>${x.tot}</b></div>
      <div class="row"><span>Negative</span><b>${np}%</b></div></div>`;}).join('');
  destroy();
  charts.n=new Chart(cmpNeg,{type:'line',data:{labels,datasets:sl.map(s=>({label:DATA[s].name,borderColor:DATA[s].color,backgroundColor:DATA[s].color,tension:.3,
    data:DATA[s].timeline.slice(a,b+1).map(t=>Math.round(t.neg/((t.pos+t.neg+t.neu)||1)*100))}))},
    options:{plugins:{legend:{position:'bottom'}},scales:{y:{title:{display:true,text:'% negative'},suggestedMax:70}}}});
  charts.v=new Chart(cmpVol,{type:'line',data:{labels,datasets:sl.map(s=>({label:DATA[s].name,borderColor:DATA[s].color,backgroundColor:DATA[s].color+'33',fill:true,tension:.3,
    data:DATA[s].timeline.slice(a,b+1).map(t=>t.pos+t.neg+t.neu)}))},options:{plugins:{legend:{position:'bottom'}}}});
  charts.net=new Chart(cmpNet,{type:'bar',data:{labels:sl.map(s=>DATA[s].name),datasets:[{data:sl.map(s=>net(s,a,b)),backgroundColor:sl.map(s=>DATA[s].color)}]},options:{plugins:{legend:{display:false}}}});
  charts.sov=new Chart(cmpSov,{type:'doughnut',data:{labels:sl.map(s=>DATA[s].name),datasets:[{data:sl.map(s=>tot(s,a,b).tot),backgroundColor:sl.map(s=>DATA[s].color)}]},options:{plugins:{legend:{position:'bottom'}}}});
  charts.sp=new Chart(cmpSplit,{type:'bar',data:{labels:sl.map(s=>DATA[s].name),datasets:[
    {label:'Positive',backgroundColor:POS,data:sl.map(s=>{const x=tot(s,a,b);return x.tot?Math.round(x.p/x.tot*100):0;})},
    {label:'Neutral',backgroundColor:NEU,data:sl.map(s=>{const x=tot(s,a,b);return x.tot?Math.round(x.u/x.tot*100):0;})},
    {label:'Negative',backgroundColor:NEG,data:sl.map(s=>{const x=tot(s,a,b);return x.tot?Math.round(x.n/x.tot*100):0;})}]},
    options:{plugins:{legend:{position:'bottom'}},scales:{x:{stacked:true},y:{stacked:true,max:100}}}});
  document.getElementById('scoreTable').innerHTML=`<thead><tr><th>Persona</th><th>Volume</th><th>Pos</th><th>Neg</th><th>Neu</th><th>Net</th><th>Top risk</th></tr></thead><tbody>`+
    sl.map(s=>{const x=tot(s,a,b),sc=net(s,a,b),pp=Math.round(x.p/x.tot*100),np=Math.round(x.n/x.tot*100),up=Math.round(x.u/x.tot*100);
    return `<tr><td><span class="pdot" style="background:${DATA[s].color}"></span>${DATA[s].name}</td><td><b>${x.tot}</b></td>
      <td style="color:#2E9E5B">${pp}%</td><td style="color:#D7263D">${np}%</td><td>${up}%</td>
      <td style="font-weight:700;color:${sc>=0?'#2E9E5B':'#D7263D'}">${sc>0?'+':''}${sc}</td><td style="font-size:12px;color:#7a1338">${DATA[s].pitch.risk}</td></tr>`;}).join('')+`</tbody>`;
  // shared narratives matrix (selected personas as columns)
  let head=`<thead><tr><th>Storyline</th>`+sl.map(s=>`<th>${DATA[s].name}</th>`).join('')+`</tr></thead>`;
  let body=SHARED.map(ev=>`<tr><td><b>${ev.event}</b><br><span style="font-size:11.5px;color:#888">${ev.detail}</span></td>`+
    sl.map(s=>{const p=ev.scores[s]||'neu';return `<td><span class="pol ${p}">${POLTXT[p]}</span></td>`;}).join('')+`</tr>`).join('');
  document.getElementById('sharedTable').innerHTML=head+`<tbody>${body}</tbody>`;
}

/* ---------- PERSONA DEEP-DIVE ---------- */
function personaHTML(s){const d=DATA[s];
  return `
  <div class="kpis" id="pk"></div>
  <div class="secthead">Social (X) conversation <span class="clickhint">- click any chart bar, slice, day or post to see the source posts/articles</span></div>
  <div class="grid">
    <div class="card"><h3>Sentiment split <span class="sub">in range, for ${d.name}</span></h3><canvas id="pSent"></canvas></div>
    <div class="card"><h3>Daily volume by sentiment</h3><canvas id="pDaily"></canvas></div>
    <div class="card"><h3>Top negative issues</h3><canvas id="pIssues"></canvas></div>
    <div class="card"><h3>Highest-reach posts</h3><div id="pPosts"></div></div>
  </div>
  <div class="secthead">Digital &amp; press media</div>
  <div class="grid">
    <div class="card"><h3>Press sentiment <span class="sub">${d.news.article_count} articles</span></h3><canvas id="pNews"></canvas></div>
    <div class="card"><h3>Coverage language</h3><canvas id="pLangs"></canvas></div>
    <div class="card"><h3>News topics</h3><canvas id="pTopics"></canvas></div>
    <div class="card"><h3>Publications</h3><canvas id="pPubs"></canvas></div>
    <div class="card full"><h3>Eenadu &amp; Sakshi <span class="sub">${d.telugu_press?d.telugu_press.window:''}</span></h3><div class="grid" id="pTP"></div></div>
  </div>
  <div class="secthead">Story &amp; recommendations</div>
  <div class="grid">
    <div class="card"><h3>Defining stories</h3><div id="pStories"></div></div>
    <div class="card"><h3>Insights</h3><ul class="ins" id="pIns"></ul></div>
    <div class="card full"><h3>Strategy</h3>
      <div class="blk"><div class="t risk">Top risk</div><p>${d.pitch.risk}</p></div>
      <div class="blk"><div class="t win">Top opportunity</div><p>${d.pitch.win}</p></div>
      <div class="blk"><div class="t">Recommended actions</div><ul>${d.pitch.actions.map(x=>`<li>${x}</li>`).join('')}</ul></div>
    </div>
    <div class="card full"><h3>How shared storylines score for ${d.name}</h3><table id="pShared"></table>
      <div class="note">Sentiment is relative: these cross-cutting events are scored from ${d.name}'s standpoint, not the topic's tone.</div></div>
  </div>`;}

function renderPersona(s){const d=DATA[s];const [a,b]=range;const x=tot(s,a,b);
  document.getElementById('personaView').innerHTML=personaHTML(s);
  const sc=net(s,a,b),dl=net(s,21,27)-net(s,14,20),np=x.tot?Math.round(x.n/x.tot*100):0,pp=x.tot?Math.round(x.p/x.tot*100):0;
  const ar=dl>=0?`<span class="wow up">&#9650; +${dl} WoW</span>`:`<span class="wow down">&#9660; ${dl} WoW</span>`;
  document.getElementById('pk').innerHTML=
    `<div class="kpi" style="border-top-color:${d.color}"><div class="nm">Net sentiment</div><div class="score" style="color:${sc>=0?'#2E9E5B':'#D7263D'}">${sc>0?'+':''}${sc}</div><div class="row"><span>vs prior week</span>${ar}</div></div>`+
    `<div class="kpi"><div class="nm">X volume (range)</div><div class="score">${x.tot}</div><div class="row"><span>Official posts</span><b>${d.official_posts}</b></div></div>`+
    `<div class="kpi"><div class="nm">Positive</div><div class="score" style="color:#2E9E5B">${pp}%</div></div>`+
    `<div class="kpi"><div class="nm">Negative</div><div class="score" style="color:#D7263D">${np}%</div></div>`;
  destroy();
  const SMAP=['pos','neg','neu'];
  donut('pSent',['Positive','Negative','Neutral'],[x.p,x.n,x.u],[POS,NEG,NEU],
    (lab,i)=>openDrawer(s,{sent:SMAP[i],kind:'x'},SMAP[i]==='neg'?'Negative X conversation':lab+' X conversation','Posts scored '+POLTXT2[SMAP[i]]+' for '+d.name));
  const dlabels=DAYS.slice(a,b+1), dmap=['pos','neu','neg'];
  charts.pd=new Chart(pDaily,{type:'bar',data:{labels:dlabels,datasets:[
    {label:'Positive',backgroundColor:POS,data:d.timeline.slice(a,b+1).map(t=>t.pos)},
    {label:'Neutral',backgroundColor:NEU,data:d.timeline.slice(a,b+1).map(t=>t.neu)},
    {label:'Negative',backgroundColor:NEG,data:d.timeline.slice(a,b+1).map(t=>t.neg)}]},
    options:{plugins:{legend:{position:'bottom'}},scales:{x:{stacked:true},y:{stacked:true}},
      onClick:(e,els)=>{if(!els.length)return;const sn=dmap[els[0].datasetIndex],day=dlabels[els[0].index];
        openDrawer(s,{sent:sn,kind:'x'},POLTXT2[sn]+' conversation - '+day,'What drove '+POLTXT2[sn].toLowerCase()+' sentiment around '+day);}}});
  hbar('pIssues',d.issues,NEG,(lab)=>openDrawer(s,{label:lab,sent:'neg',kind:'x'},lab,'Negative posts on this issue'));
  donut('pNews',['Positive','Negative','Neutral'],[d.news.sentiment.positive,d.news.sentiment.negative,d.news.sentiment.neutral],[POS,NEG,NEU],
    (lab,i)=>openDrawer(s,{sent:SMAP[i],kind:'press'},lab+' press coverage','Articles scored '+POLTXT2[SMAP[i]]+' for '+d.name));
  donut('pLangs',Object.keys(d.news.languages),Object.values(d.news.languages),[d.color,AC2,NEU,'#C7C7C7']);
  hbar('pTopics',d.news.topics,d.color,(lab)=>openDrawer(s,{label:lab,kind:'press'},lab,'Press coverage on this topic'));
  hbar('pPubs',d.news.publications,AC2,(lab)=>openDrawer(s,{label:lab},lab,'Coverage from this publication'));
  document.getElementById('pPosts').innerHTML=d.top_posts.slice(0,5).map(p=>`<div class="post clickable" onclick="openDrawer('${s}',{sent:'pos',kind:'x'},'Highest-reach posts','Positive / on-message posts for ${d.name.replace(/'/g,"")}')"><span>${p.text}</span><span class="v">${(p.views||0).toLocaleString()}</span></div>`).join('');
  document.getElementById('pTP').innerHTML=d.telugu_press?['eenadu','sakshi'].map(k=>{const o=d.telugu_press[k];
    return `<div class="src"><div class="sh"><span>${k[0].toUpperCase()+k.slice(1)}</span><span>${o.count} articles</span></div><div class="sl">${o.lean}</div><ul>${o.headlines.map(h=>`<li>${h}</li>`).join('')}</ul></div>`;}).join(''):'';
  document.getElementById('pStories').innerHTML=d.stories.map(x=>`<div class="story"><b>${x.title}</b><span>${x.detail}</span></div>`).join('');
  document.getElementById('pIns').innerHTML=d.insights.map(i=>`<li>${i}</li>`).join('');
  document.getElementById('pShared').innerHTML=`<thead><tr><th>Storyline</th><th>Score for ${d.name}</th><th>Why</th></tr></thead><tbody>`+
    SHARED.filter(e=>e.scores[s]).map(e=>{const p=e.scores[s];return `<tr><td><b>${e.event}</b></td><td><span class="pol ${p}">${POLTXT[p]}</span></td><td style="font-size:12px;color:#555">${e.why}</td></tr>`;}).join('')+`</tbody>`;
}

function render(){
  const isC=view==='compare';
  document.getElementById('compareView').style.display=isC?'':'none';
  document.getElementById('personaView').style.display=isC?'none':'';
  document.getElementById('personaCtl').style.display=isC?'':'none';
  document.getElementById('heroTitle').textContent=isC?'Compare':DATA[view].name;
  document.getElementById('heroSub').textContent=isC?'X conversation + Eenadu / Sakshi / English press - sentiment scored per persona':(DATA[view].party+' - '+DATA[view].role);
  document.querySelectorAll('#tabs .tab').forEach(t=>t.classList.toggle('on',t.dataset.v===view));
  if(isC){document.getElementById('compareView').innerHTML=compareHTML();renderCompare();}
  else{renderPersona(view);}
}

/* controls */
const tabs=document.getElementById('tabs');
[...ORDER.map(s=>[s,DATA[s].name]),['compare','Compare']].forEach(([v,label])=>{const b=document.createElement('button');
  b.className='tab'+(v===view?' on':'');b.textContent=label;b.dataset.v=v;b.onclick=()=>{view=v;render();};tabs.appendChild(b);});
const pp=document.getElementById('personaPills');
ORDER.forEach(s=>{const b=document.createElement('button');b.className='pill on';b.textContent=DATA[s].name;b.style.background=DATA[s].color;b.style.borderColor=DATA[s].color;
  b.onclick=()=>{if(sel.has(s)){if(sel.size>1){sel.delete(s);b.classList.remove('on');b.style.background='';}}else{sel.add(s);b.classList.add('on');b.style.background=DATA[s].color;}render();};pp.appendChild(b);});
const wp=document.getElementById('weekPills');
Object.keys(WEEKS).forEach(k=>{const b=document.createElement('button');b.className='pill'+(k==='All 4 weeks'?' on':'');b.textContent=k;
  b.onclick=()=>{range=WEEKS[k].slice();document.querySelectorAll('#weekPills .pill').forEach(x=>x.classList.remove('on'));b.classList.add('on');syncSel();render();};wp.appendChild(b);});
const fromSel=document.getElementById('fromSel'),toSel=document.getElementById('toSel');
DAYS.forEach((d,i)=>{fromSel.add(new Option(d,i));toSel.add(new Option(d,i));});fromSel.value=0;toSel.value=27;
function syncSel(){fromSel.value=range[0];toSel.value=range[1];}
function customChange(){let a=+fromSel.value,b=+toSel.value;if(a>b){[a,b]=[b,a];}range=[a,b];document.querySelectorAll('#weekPills .pill').forEach(x=>x.classList.remove('on'));syncSel();render();}
fromSel.onchange=customChange;toSel.onchange=customChange;
render();
</script></body></html>"""


def build(out_path):
    data = {s: load(s) for s in ["ktr", "bandi-sanjay", "revanth-reddy"]}
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(data))
            .replace("__DAYS__", json.dumps(DAYS))
            .replace("__SHARED__", json.dumps(SHARED_NARRATIVES))
            .replace("__ACCENT2__", ACCENT2)
            .replace("__ACCENT__", ACCENT)
            .replace("__DARK__", DARK))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    out = build(os.path.join(ROOT, "output", "index.html"))
    print("dashboard app ->", out)
