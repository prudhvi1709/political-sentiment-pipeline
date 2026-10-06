"""
Single-file interactive dashboard (index.html) for a person's weekly dataset.

Same data as the two decks; Chart.js loaded from CDN (works in a real browser,
renders empty inside sandboxed in-app previews, which is expected). Branding is
driven by the person's accent colours.
"""
import os
import json


def build(data, out_path):
    b = data["branding"]
    p = data["person"]
    x = data["x_data"]
    n = data["news_data"]
    xt = sum(x["sentiment"].values()) or 1
    nt = sum(n["sentiment"].values()) or 1

    payload = json.dumps({
        "x_sent": x["sentiment"],
        "x_daily": x["daily"],
        "x_issues": x["issues"],
        "n_sent": n["sentiment"],
        "n_topics": n["topics"],
        "n_pubs": n["publications"],
        "n_langs": n["languages"],
    })

    stories = "".join(
        f'<div class="story"><h4>{s["title"]}</h4><p>{s["detail"]}</p></div>'
        for s in data.get("stories", [])
    )
    insights = "".join(f"<li>{i}</li>" for i in data.get("insights", []))
    posts = "".join(
        f'<div class="post"><p>{po["text"]}</p>'
        f'<span>{po.get("views", 0):,} views</span></div>'
        for po in x.get("top_posts", [])[:5]
    )

    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{p['name']} — Weekly Sentiment</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{ --accent:{b['accent']}; --accent2:{b['accent2']}; --dark:{b['dark']}; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         color:#1a1a1a; background:#f4f5f7; }}
  .hero {{ background:var(--dark); color:#fff; padding:42px 48px;
          border-bottom:6px solid var(--accent); }}
  .hero .kicker {{ color:var(--accent); font-weight:700; letter-spacing:1px;
          font-size:13px; }}
  .hero h1 {{ font-size:40px; margin:6px 0; }}
  .hero .role {{ color:#cfcfcf; font-size:16px; }}
  .hero .week {{ color:#9aa0a6; margin-top:10px; font-size:14px; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:28px 24px 60px; }}
  .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px;
          margin-bottom:26px; }}
  .stat {{ background:#fff; border-radius:12px; padding:20px;
          border-left:6px solid var(--accent); box-shadow:0 1px 4px rgba(0,0,0,.06); }}
  .stat .v {{ font-size:32px; font-weight:800; color:var(--accent); }}
  .stat .l {{ color:#555; font-size:13px; margin-top:4px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  .card {{ background:#fff; border-radius:12px; padding:20px;
          box-shadow:0 1px 4px rgba(0,0,0,.06); margin-bottom:18px; }}
  .card h3 {{ font-size:15px; margin-bottom:14px; color:#222;
          border-bottom:2px solid #eee; padding-bottom:8px; }}
  .card.full {{ grid-column:1/-1; }}
  canvas {{ max-height:300px; }}
  .story {{ border-left:4px solid var(--accent2); padding:8px 14px;
          margin-bottom:12px; background:#fafafa; }}
  .story h4 {{ color:var(--accent); font-size:14px; }}
  .story p {{ color:#444; font-size:13px; margin-top:3px; }}
  ul.ins {{ padding-left:20px; }} ul.ins li {{ margin-bottom:8px; color:#333; }}
  .post {{ display:flex; justify-content:space-between; gap:12px;
          border-bottom:1px solid #eee; padding:10px 0; }}
  .post span {{ color:var(--accent); font-weight:700; white-space:nowrap; }}
</style></head><body>
<div class="hero">
  <div class="kicker">{p['party']} &nbsp;|&nbsp; WEEKLY MEDIA & SOCIAL SENTIMENT</div>
  <h1>{p['name']}</h1>
  <div class="role">{p['role']}</div>
  <div class="week">Week of {data['week']['label']}</div>
</div>
<div class="wrap">
  <div class="stats">
    <div class="stat"><div class="v">{x.get('sample_size', xt)}</div><div class="l">X items sampled</div></div>
    <div class="stat"><div class="v">{x['sentiment']['negative']*100//xt}%</div><div class="l">Negative on X</div></div>
    <div class="stat"><div class="v">{n.get('article_count', nt)}</div><div class="l">News articles</div></div>
    <div class="stat"><div class="v">{n['sentiment']['positive']*100//nt}%</div><div class="l">Positive in press</div></div>
  </div>
  <div class="grid">
    <div class="card"><h3>X sentiment</h3><canvas id="xSent"></canvas></div>
    <div class="card"><h3>News sentiment</h3><canvas id="nSent"></canvas></div>
    <div class="card full"><h3>Daily X volume by sentiment</h3><canvas id="xDaily"></canvas></div>
    <div class="card"><h3>Top negative issues (X)</h3><canvas id="xIssues"></canvas></div>
    <div class="card"><h3>News topics</h3><canvas id="nTopics"></canvas></div>
    <div class="card"><h3>Publications</h3><canvas id="nPubs"></canvas></div>
    <div class="card"><h3>Coverage language</h3><canvas id="nLangs"></canvas></div>
    <div class="card full"><h3>Top posts this week</h3>{posts}</div>
    <div class="card"><h3>Defining stories</h3>{stories}</div>
    <div class="card"><h3>Key insights</h3><ul class="ins">{insights}</ul></div>
  </div>
</div>
<script>
const D = {payload};
const POS='#2E9E5B', NEG='#D7263D', NEU='#9AA0A6', AC='{b['accent']}', AC2='{b['accent2']}';
const donut=(id,s)=>new Chart(document.getElementById(id),{{type:'doughnut',
  data:{{labels:['Positive','Negative','Neutral'],datasets:[{{data:[s.positive,s.negative,s.neutral],backgroundColor:[POS,NEG,NEU]}}]}},
  options:{{plugins:{{legend:{{position:'bottom'}}}}}}}});
donut('xSent',D.x_sent); donut('nSent',D.n_sent);
new Chart(document.getElementById('xDaily'),{{type:'bar',
  data:{{labels:D.x_daily.map(d=>d.date),datasets:[
    {{label:'Positive',data:D.x_daily.map(d=>d.pos||0),backgroundColor:POS}},
    {{label:'Neutral',data:D.x_daily.map(d=>d.neu||0),backgroundColor:NEU}},
    {{label:'Negative',data:D.x_daily.map(d=>d.neg||0),backgroundColor:NEG}}]}},
  options:{{responsive:true,scales:{{x:{{stacked:true}},y:{{stacked:true}}}}}}}});
const hbar=(id,arr,color)=>{{arr=[...arr].sort((a,b)=>a.count-b.count);
  new Chart(document.getElementById(id),{{type:'bar',
  data:{{labels:arr.map(i=>i.label),datasets:[{{data:arr.map(i=>i.count),backgroundColor:color}}]}},
  options:{{indexAxis:'y',plugins:{{legend:{{display:false}}}}}}}});}};
hbar('xIssues',D.x_issues,NEG); hbar('nTopics',D.n_topics,AC); hbar('nPubs',D.n_pubs,AC2);
new Chart(document.getElementById('nLangs'),{{type:'doughnut',
  data:{{labels:Object.keys(D.n_langs),datasets:[{{data:Object.values(D.n_langs),backgroundColor:[AC,AC2,NEU,'#C7C7C7']}}]}},
  options:{{plugins:{{legend:{{position:'bottom'}}}}}}}});
</script></body></html>"""

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    import sys
    data_path, out_path = sys.argv[1], sys.argv[2]
    with open(data_path) as f:
        data = json.load(f)
    build(data, out_path)
    print("dashboard ->", out_path)
