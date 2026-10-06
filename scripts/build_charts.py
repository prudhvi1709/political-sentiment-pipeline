"""
Branded matplotlib charts for the weekly political-sentiment decks/dashboard.

All charts read from the person's dataset JSON and write PNGs into
output/<slug>/charts/. Colours come from the person's branding block so the
charts match the deck and dashboard.
"""
import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager  # noqa: F401

PLT_RC = {
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#BBBBBB",
    "axes.labelcolor": "#333333",
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "font.size": 12,
}
plt.rcParams.update(PLT_RC)

POS = "#2E9E5B"
NEG = "#D7263D"
NEU = "#9AA0A6"


def _save(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)


def sentiment_donut(sent, accent, out):
    labels = ["Positive", "Negative", "Neutral"]
    vals = [sent["positive"], sent["negative"], sent["neutral"]]
    total = sum(vals) or 1
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    wedges, _ = ax.pie(
        vals, colors=[POS, NEG, NEU], startangle=90, counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2),
    )
    ax.text(0, 0.12, str(total), ha="center", va="center",
            fontsize=30, fontweight="bold", color="#1A1A1A")
    ax.text(0, -0.22, "items", ha="center", va="center",
            fontsize=12, color="#777777")
    ax.legend(
        wedges, [f"{l}  {v}  ({v*100//total}%)" for l, v in zip(labels, vals)],
        loc="center", bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False,
        fontsize=11,
    )
    ax.set(aspect="equal")
    _save(fig, out)


def daily_trend(daily, accent, out):
    days = [d["date"] for d in daily]
    pos = [d.get("pos", 0) for d in daily]
    neg = [d.get("neg", 0) for d in daily]
    neu = [d.get("neu", 0) for d in daily]
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    ax.bar(days, pos, color=POS, label="Positive")
    ax.bar(days, neu, bottom=pos, color=NEU, label="Neutral")
    ax.bar(days, neg, bottom=[p + n for p, n in zip(pos, neu)],
           color=NEG, label="Negative")
    totals = [p + n + u for p, n, u in zip(pos, neg, neu)]
    for i, t in enumerate(totals):
        ax.text(i, t + max(totals) * 0.02, str(t), ha="center",
                fontsize=11, color="#333", fontweight="bold")
    ax.set_ylim(0, max(totals) * 1.18 if totals else 1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper right", frameon=False, ncol=3, fontsize=10)
    _save(fig, out)


def barh(items, accent, out, figsize=(7.6, 4.0), value_suffix=""):
    items = sorted(items, key=lambda x: x["count"])
    labels = [i["label"] for i in items]
    vals = [i["count"] for i in items]
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(labels, vals, color=accent)
    mx = max(vals) if vals else 1
    for b, v in zip(bars, vals):
        ax.text(b.get_width() + mx * 0.01, b.get_y() + b.get_height() / 2,
                f"{v}{value_suffix}", va="center", fontsize=11,
                color="#333", fontweight="bold")
    ax.set_xlim(0, mx * 1.14)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    _save(fig, out)


def language_split(langs, accent, accent2, out):
    labels = list(langs.keys())
    vals = list(langs.values())
    colors = [accent, accent2, "#9AA0A6", "#C7C7C7"][: len(labels)]
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    total = sum(vals) or 1
    wedges, _ = ax.pie(vals, colors=colors, startangle=90,
                       wedgeprops=dict(width=0.42, edgecolor="white",
                                       linewidth=2))
    ax.legend(wedges, [f"{l}  {v}" for l, v in zip(labels, vals)],
              loc="center", bbox_to_anchor=(0.5, -0.05), frameon=False,
              fontsize=11)
    ax.set(aspect="equal")
    _save(fig, out)


def build_all(data, charts_dir):
    b = data["branding"]
    accent, accent2 = b["accent"], b["accent2"]
    x = data["x_data"]
    n = data["news_data"]
    sentiment_donut(x["sentiment"], accent,
                    os.path.join(charts_dir, "x_sentiment.png"))
    daily_trend(x["daily"], accent,
                os.path.join(charts_dir, "x_daily.png"))
    barh(x["issues"], NEG, os.path.join(charts_dir, "x_issues.png"))
    sentiment_donut(n["sentiment"], accent,
                    os.path.join(charts_dir, "news_sentiment.png"))
    barh(n["topics"], accent, os.path.join(charts_dir, "news_topics.png"))
    barh(n["publications"], accent2,
         os.path.join(charts_dir, "news_publications.png"))
    language_split(n["languages"], accent, accent2,
                   os.path.join(charts_dir, "news_languages.png"))
    return charts_dir


if __name__ == "__main__":
    import sys
    data_path = sys.argv[1]
    with open(data_path) as f:
        data = json.load(f)
    out = os.path.join(os.path.dirname(data_path), "charts")
    build_all(data, out)
    print("charts ->", out)
