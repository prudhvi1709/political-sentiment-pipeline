"""
Orchestrator: dataset JSON -> charts -> 2 decks -> dashboard.

Usage:
    python3 run.py <slug>
Expects data/<slug>_week_data.json to exist (built from collected data).
Writes everything to output/<slug>/.
"""
import os
import sys
import json
import build_charts
import build_decks
import build_dashboard

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def run(slug):
    data_path = os.path.join(ROOT, "data", f"{slug}_week_data.json")
    with open(data_path) as f:
        data = json.load(f)
    out_dir = os.path.join(ROOT, "output", slug)
    charts_dir = os.path.join(out_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    build_charts.build_all(data, charts_dir)
    build_decks.build_x_deck(data, charts_dir,
                             os.path.join(out_dir, f"{slug}_x_report.pptx"))
    build_decks.build_news_deck(data, charts_dir,
                                os.path.join(out_dir, f"{slug}_news_report.pptx"))
    build_dashboard.build(data, os.path.join(out_dir, "index.html"))
    print(f"[done] {slug} -> {out_dir}")
    for fn in sorted(os.listdir(out_dir)):
        print("   ", fn)


if __name__ == "__main__":
    run(sys.argv[1])
