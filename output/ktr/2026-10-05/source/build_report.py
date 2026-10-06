"""Build a standalone, offline KTR sample report from source and reviewed labels."""

from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import html
import json
import math
import re
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))
STANCES = ["supportive", "critical", "neutral", "mixed", "unclear"]
LABELS = {
    "supportive": "Supportive",
    "critical": "Critical",
    "neutral": "Neutral / reporting",
    "mixed": "Mixed",
    "unclear": "Unclear",
    "unrelated": "Unrelated",
}
SHORT = {
    "Election strategy": "Election strategy",
    "Governance and development": "Governance / development",
    "Assets and allegations": "Assets / allegations",
    "Party leadership": "Party leadership",
    "Rivalry and political attacks": "Political rivalry",
    "Welfare and public requests": "Welfare / requests",
    "Public events and festivals": "Events / festivals",
    "Historical recollections": "Historical recollections",
    "Personal praise and criticism": "Personal appraisal",
    "Other or unclear": "Other / unclear",
}
COLORS = {
    "supportive": "#2D8C7A",
    "critical": "#CE4B55",
    "neutral": "#657B9D",
    "mixed": "#AA7626",
    "unclear": "#8B8295",
    "unrelated": "#8B8295",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def number(value: float) -> str:
    if abs(value) >= 1000000:
        return f"{value / 1000000:.1f}m"
    if abs(value) >= 1000:
        return f"{value / 1000:.1f}k"
    return f"{value:,.0f}"


def pct(numerator: float, denominator: float) -> str:
    return f"{numerator / denominator * 100:.0f}%" if denominator else "n/a"


def quantile(values: list[float], portion: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * portion
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def svg(title: str, contents: str, *, width: int = 720, height: int = 280) -> str:
    return f'<div class="chart-frame"><svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>{contents}</svg></div>'


def text(
    x: float, y: float, value: object, *, cls: str = "", anchor: str = "start"
) -> str:
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def table(headers: list[str], rows: list[list[object]], *, caption: str) -> str:
    head = "".join(f'<th scope="col">{esc(h)}</th>' for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{esc(v)}</td>" for v in row) + "</tr>" for row in rows
    )
    return f'<details class="data-table"><summary>View chart data</summary><div class="table-scroll"><table><caption>{esc(caption)}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></details>'


def legend(keys: list[str] = STANCES) -> str:
    return (
        '<div class="legend">'
        + "".join(f'<span><i class="{key}"></i>{LABELS[key]}</span>' for key in keys)
        + "</div>"
    )


def bars(
    entries: list[tuple[str, float]],
    *,
    title: str,
    unit: str = "posts",
    color: str = "accent",
    maximum: float | None = None,
) -> str:
    maximum = maximum or max((v for _, v in entries), default=1) or 1
    contents = ""
    height = 40 + len(entries) * 36
    for i, (label, value) in enumerate(entries):
        y = 15 + i * 36
        contents += text(0, y + 17, label, cls="bar-label")
        contents += (
            f'<rect class="bar-track" x="238" y="{y}" width="385" height="22" rx="3"/>'
        )
        contents += f'<rect class="{color}" x="238" y="{y}" width="{385 * value / maximum:.2f}" height="22" rx="3"><title>{esc(label)}: {value:,.0f} {esc(unit)}</title></rect>'
        contents += text(636, y + 17, number(value), cls="value")
    return svg(title, contents, height=height) + table(
        ["Category", unit], [[k, f"{v:,.0f}"] for k, v in entries], caption=title
    )


def stacked(
    entries: list[tuple[str, dict[str, float]]], *, title: str, normalized: bool = False
) -> str:
    contents = ""
    height = 55 + len(entries) * 38
    maximum = max((sum(c.values()) for _, c in entries), default=1) or 1
    for i, (label, counts) in enumerate(entries):
        y = 15 + i * 38
        total = sum(counts.values())
        x = 220
        contents += text(0, y + 17, label, cls="bar-label")
        for key in STANCES:
            value = counts.get(key, 0)
            width = 390 * value / (total if normalized and total else maximum)
            if width:
                contents += f'<rect class="{key}" x="{x:.2f}" y="{y}" width="{width:.2f}" height="22"><title>{esc(label)} / {LABELS[key]}: {value:.1f}; {pct(value, total)} of row</title></rect>'
            x += width
        contents += text(624, y + 17, f"n={total:,.0f}", cls="value")
    contents += text(220, height - 4, "0% / 0 posts", cls="axis") + text(
        610,
        height - 4,
        "100%" if normalized else f"{maximum:,.0f} posts",
        anchor="end",
        cls="axis",
    )
    rows = [
        [
            label,
            *[f"{counts.get(key, 0):.1f}" for key in STANCES],
            f"{sum(counts.values()):.1f}",
        ]
        for label, counts in entries
    ]
    return (
        legend()
        + svg(title, contents, height=height)
        + table(
            ["Category", *[LABELS[k] for k in STANCES], "Total"], rows, caption=title
        )
    )


def daily_chart(rows: list[dict], *, share: bool = False) -> str:
    start = datetime(2026, 9, 1, tzinfo=IST)
    end = datetime(2026, 10, 5, tzinfo=IST)
    days = [
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((end - start).days + 1)
    ]
    counts = {
        day: collections.Counter(r["stance"] for r in rows if r["day"] == day)
        for day in days
    }
    maximum = max(sum(c.values()) for c in counts.values()) or 1
    out = ""
    left = 45
    plot_width = 890
    bottom = 238
    plot_height = 190
    for fraction in [0, 0.5, 1]:
        y = bottom - plot_height * fraction
        out += f'<path class="gridline" d="M45 {y}H940"/>' + text(
            36,
            y + 4,
            f"{fraction * 100:.0f}%" if share else f"{maximum * fraction:.0f}",
            anchor="end",
            cls="axis",
        )
        out += text(
            949,
            y + 4,
            f"{fraction * 100:.0f}%" if share else f"{maximum * fraction:.0f}",
            cls="axis",
        )
    for i, day in enumerate(days):
        counts_day = counts[day]
        total = sum(counts_day.values())
        x = left + i * plot_width / len(days)
        y = bottom
        if share and total < 10:
            out += f'<rect class="sparse" x="{x:.2f}" y="{bottom - 4}" width="19" height="4"><title>{day}: n={total}; share suppressed below 10</title></rect>'
        else:
            for key in STANCES:
                h = (
                    plot_height
                    * counts_day[key]
                    / (total if share and total else maximum)
                )
                y -= h
                if h:
                    out += f'<rect class="{key}" x="{x:.2f}" y="{y:.2f}" width="19" height="{h:.2f}"><title>{day}: {LABELS[key]} {counts_day[key]}, total n={total}</title></rect>'
        if i % 5 == 0 or i == len(days) - 1:
            out += text(
                x + 9,
                bottom + 23,
                datetime.fromisoformat(day).strftime("%d %b"),
                anchor="middle",
                cls="axis",
            )
    out += text(
        45,
        24,
        "Share of collected posts" if share else "Collected posts / publication day",
        cls="axis",
    )
    out += text(935, 24, "05 Oct: partial day", anchor="end", cls="axis")
    caption = (
        "Daily stance shares (only days with at least 10 posts)"
        if share
        else "Daily collected posts by KTR stance"
    )
    return (
        legend()
        + f'<div class="chart-scroll">{svg(caption, out, width=980, height=285)}</div>'
        + table(
            ["IST publication day", "Collected n", *[LABELS[k] for k in STANCES]],
            [
                [day, sum(counts[day].values()), *[counts[day][k] for k in STANCES]]
                for day in days
            ],
            caption=caption,
        )
    )


def heatmap(rows: list[dict], topics: list[str]) -> str:
    weeks = [
        "2026-08-31",
        "2026-09-07",
        "2026-09-14",
        "2026-09-21",
        "2026-09-28",
        "2026-10-05",
    ]
    out = ""
    matrix = []

    def week_of(row: dict) -> str:
        date = datetime.fromisoformat(row["day"])
        return (date - timedelta(days=date.weekday())).strftime("%Y-%m-%d")

    maximum = (
        max(
            sum(r["topic"] == topic and week_of(r) == week for r in rows)
            for topic in topics
            for week in weeks
        )
        or 1
    )
    for i, topic in enumerate(topics):
        out += text(0, 60 + i * 33, SHORT[topic], cls="bar-label")
        values = []
        for j, week in enumerate(weeks):
            value = sum(r["topic"] == topic and week_of(r) == week for r in rows)
            values.append(value)
            x = 245 + j * 70
            y = 38 + i * 33
            bucket = min(4, math.ceil(value / maximum * 4)) if value else 0
            out += f'<rect class="heat heat-{bucket}" x="{x}" y="{y}" width="62" height="27" rx="3"><title>{esc(topic)} / week {week}: {value} posts</title></rect>'
            out += text(
                x + 31,
                y + 18,
                value,
                anchor="middle",
                cls=f"heat-text heat-text-{bucket}",
            )
        matrix.append([SHORT[topic], *values])
    for j, week in enumerate(weeks):
        out += text(
            276 + j * 70,
            24,
            datetime.fromisoformat(week).strftime("%d %b"),
            anchor="middle",
            cls="axis",
        )
    return svg(
        "Primary topic counts by week start in IST", out, height=60 + len(topics) * 33
    ) + table(
        ["Main topic", *[datetime.fromisoformat(w).strftime("%d %b") for w in weeks]],
        matrix,
        caption="Topic by week; boundary weeks are partial",
    )


def scatter(rows: list[dict]) -> str:
    out = ""
    left = 70
    bottom = 300
    height = 235
    max_x = math.ceil(math.log10(max(r["views"] for r in rows) + 1))
    max_y = math.ceil(math.log10(max(r["interactions"] for r in rows) + 1))
    for i in range(max_x + 1):
        x = left + i / max_x * 580
        out += f'<path class="gridline" d="M{x} 50V{bottom}"/>' + text(
            x, bottom + 20, number(10**i - 1), anchor="middle", cls="axis"
        )
    for i in range(max_y + 1):
        y = bottom - i / max_y * height
        out += f'<path class="gridline" d="M70 {y}H650"/>' + text(
            60, y + 4, number(10**i - 1), anchor="end", cls="axis"
        )
    for r in sorted(rows, key=lambda r: r["views"]):
        x = left + math.log10(r["views"] + 1) / max_x * 580
        y = bottom - math.log10(r["interactions"] + 1) / max_y * height
        title = f"Post {r['id'] + 1}: {LABELS[r['stance']]}; {r['views']:,} views; {r['interactions']:,} interactions"
        out += f'<a href="#evidence" data-id="{r["id"]}" aria-label="{esc(title)}"><circle class="{r["stance"]} dot" cx="{x:.2f}" cy="{y:.2f}" r="4"><title>{esc(title)}</title></circle></a>'
    out += text(
        70, 25, "Interactions: likes + reposts + replies + bookmarks", cls="axis"
    ) + text(
        650, 355, "Recorded views (log scale, value + 1)", anchor="end", cls="axis"
    )
    return (
        legend()
        + svg(
            "Recorded views and interactions per recent retained post; both axes logarithmic",
            out,
            height=380,
        )
        + '<p class="small">Each point is a post. Select a point to inspect its evidence. Views and interactions are snapshot counters, not people.</p>'
    )


def distribution(rows: list[dict]) -> str:
    out = ""
    rows_table = []
    maximum = max(math.log10(r["interactions"] + 1) for r in rows) or 1
    for i, key in enumerate(STANCES):
        values = [r["interactions"] for r in rows if r["stance"] == key]
        if not values:
            continue
        median = statistics.median(values)
        q1 = quantile(values, 0.25)
        q3 = quantile(values, 0.75)
        y = 34 + i * 44
        positions = [
            230 + math.log10(v + 1) / maximum * 370
            for v in [min(values), q1, median, q3, max(values)]
        ]
        out += text(0, y + 5, LABELS[key], cls="bar-label")
        out += f'<path class="whisker" d="M{positions[0]} {y}H{positions[4]} M{positions[0]} {y - 7}V{y + 7} M{positions[4]} {y - 7}V{y + 7}"/>'
        out += f'<rect class="{key}" x="{positions[1]}" y="{y - 10}" width="{max(2, positions[3] - positions[1])}" height="20"><title>{LABELS[key]}: n={len(values)}, median {median:,.0f}, middle half {q1:,.0f} to {q3:,.0f}, min {min(values)}, max {max(values)}</title></rect>'
        out += (
            f'<path class="median-line" d="M{positions[2]} {y - 13}V{y + 13}"/>'
            + text(625, y + 5, f"{number(median)} (n={len(values)})", cls="value")
        )
        rows_table.append(
            [
                LABELS[key],
                len(values),
                min(values),
                f"{q1:.1f}",
                f"{median:.1f}",
                f"{q3:.1f}",
                max(values),
            ]
        )
    out += text(
        230,
        275,
        "Interactions per post: min, middle 50%, median, max; log scale",
        cls="axis",
    )
    return svg(
        "Interaction distribution by stance; median and quartiles, log scale",
        out,
        height=290,
    ) + table(
        ["Stance", "n", "Minimum", "Q1", "Median", "Q3", "Maximum"],
        rows_table,
        caption="Descriptive distributions, not significance tests",
    )


def concentration(rows: list[dict]) -> tuple[str, float, float]:
    authors = collections.Counter(r["handle"] for r in rows if r["handle"])
    known_count = sum(authors.values())
    counts = sorted(authors.values(), reverse=True)
    first5 = sum(counts[:5]) / known_count * 100
    out = ""
    cumulative = 0
    points = ["55,245"]
    data = []
    for i, c in enumerate(counts):
        cumulative += c
        x = 55 + (i + 1) / len(counts) * 600
        y = 245 - cumulative / known_count * 190
        points.append(f"{x:.2f},{y:.2f}")
        data.append([i + 1, c, cumulative, pct(cumulative, known_count)])
    for fraction in [0, 0.25, 0.5, 0.75, 1]:
        y = 245 - fraction * 190
        out += f'<path class="gridline" d="M55 {y}H655"/>' + text(
            45, y + 4, f"{fraction * 100:.0f}%", anchor="end", cls="axis"
        )
        out += text(
            55 + fraction * 600,
            268,
            f"{fraction * 100:.0f}%",
            anchor="middle",
            cls="axis",
        )
    out += f'<path class="diagonal" d="M55 245L655 55"/><polyline class="concentration-line" points="{" ".join(points)}"/>'
    out += text(55, 27, "Cumulative share of posts", cls="axis") + text(
        655, 297, "Authors, ranked by post count", anchor="end", cls="axis"
    )
    return (
        svg(
            "Cumulative post share by authors ranked most prolific first",
            out,
            height=315,
        )
        + table(
            ["Authors included", "Posts by next author", "Cumulative posts", "Share"],
            data,
            caption="Recent relevant author concentration",
        ),
        first5,
        len(authors),
    )


def card(title: str, subtitle: str, content: str, *, wide: bool = False) -> str:
    return f'<article class="card{" wide" if wide else ""}"><h3>{esc(title)}</h3><p class="chart-note">{esc(subtitle)}</p>{content}</article>'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("labels", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    source = json.loads(source_bytes)
    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    if len(source) != 352 or len(labels) != 352:
        raise ValueError(
            "This report requires the original 352-row snapshot and complete labels"
        )
    expected_hash = "8e74cdfac1f5c05480201ce72445b31b6527c97e56e01dc62362b8c3aafd8b8f"
    if hashlib.sha256(source_bytes).hexdigest() != expected_hash:
        raise ValueError("Source snapshot differs from the classified input")
    by_id = {r["id"]: r for r in labels}
    if set(by_id) != set(range(len(source))):
        raise ValueError("Label IDs do not match the source rows")
    rows = []
    seen = set()
    for i, raw in enumerate(source):
        if raw["link"] in seen:
            raise ValueError("Duplicate post link in supplied input")
        seen.add(raw["link"])
        if not re.fullmatch(r"https://x\.com/[^/]+/status/\d+", raw["link"]):
            raise ValueError("Invalid X source link")
        if not all(
            isinstance(raw[k], int) and raw[k] >= 0
            for k in ["views", "likes", "reposts", "replies", "bookmarks"]
        ):
            raise ValueError("Post counters must be nonnegative integers")
        date = datetime.fromisoformat(raw["date"].replace("Z", "+00:00")).astimezone(
            IST
        )
        row = {
            **by_id[i],
            **{
                k: raw[k]
                for k in [
                    "link",
                    "handle",
                    "views",
                    "likes",
                    "reposts",
                    "replies",
                    "bookmarks",
                ]
            },
            "date": date.isoformat(),
            "day": date.strftime("%Y-%m-%d"),
            "year": date.year,
            "parent": raw.get("parent_link"),
            "interactions": sum(
                raw[k] for k in ["likes", "reposts", "replies", "bookmarks"]
            ),
            "script": "Telugu + Latin"
            if re.search(r"[\u0c00-\u0c7f]", raw["message"] or "")
            and re.search("[A-Za-z]", raw["message"] or "")
            else "Telugu script"
            if re.search(r"[\u0c00-\u0c7f]", raw["message"] or "")
            else "Latin / other",
            "official": (raw["handle"] or "").lower() == "ktrbrs",
        }
        rows.append(row)
    recent_all = [r for r in rows if r["day"] >= "2026-09-01"]
    recent = [r for r in recent_all if r["stance"] != "unrelated"]
    historical = [r for r in rows if r["day"] < "2026-09-01"]
    unrelated = [r for r in rows if r["stance"] == "unrelated"]
    counts = collections.Counter(r["stance"] for r in recent)
    topic_counts = collections.Counter(r["topic"] for r in recent)
    topics = [t for t, _ in topic_counts.most_common()]
    totals = {
        k: sum(r[k] for r in recent)
        for k in ["views", "likes", "reposts", "replies", "bookmarks", "interactions"]
    }
    recent_external = [r for r in recent if not r["official"]]
    external_counts = collections.Counter(r["stance"] for r in recent_external)
    capture = datetime.fromisoformat(
        source[0]["date"].replace("Z", "+00:00")
    ) + timedelta(hours=source[0]["age_hours"])
    capture_ist = capture.astimezone(IST)
    root_map = {r["link"]: r for r in source}
    earlier = sum(
        r.get("parent_link") in root_map
        and r["date"] < root_map[r["parent_link"]]["date"]
        for r in source
    )
    concentration_chart, top5_share, authors = concentration(recent)
    top_views = sorted(recent, key=lambda r: r["views"], reverse=True)[:8]
    peak_day, peak_n = collections.Counter(r["day"] for r in recent).most_common(1)[0]
    # Weighted shares are descriptive sensitivity checks; they are not opinion estimates.
    weighted = {
        key: sum(r["views"] for r in recent if r["stance"] == key) for key in STANCES
    }
    authored = collections.defaultdict(list)
    for r in recent:
        if r["handle"]:
            authored[r["handle"]].append(r)
    author_weights = collections.Counter()
    for posts in authored.values():
        for r in posts:
            author_weights[r["stance"]] += 1 / len(posts)
    weight_entries = [
        ("Each post: equal weight", dict(counts)),
        ("Views: share of counters", weighted),
        ("Each author: equal weight", dict(author_weights)),
    ]
    # Use separate rows scaled to 100%; actual denominators displayed by stacked().
    weight_chart = stacked(
        weight_entries,
        title="Sensitivity of stance composition to weighting",
        normalized=True,
    ).replace("n=", "total=")
    official_entries = [
        ("All retained posts", dict(counts)),
        ("Excluding KTRBRS", dict(external_counts)),
    ]
    topic_entries = [
        (
            SHORT[t],
            dict(collections.Counter(r["stance"] for r in recent if r["topic"] == t)),
        )
        for t in topics
    ]
    weekly = []
    for start in [
        "2026-08-31",
        "2026-09-07",
        "2026-09-14",
        "2026-09-21",
        "2026-09-28",
        "2026-10-05",
    ]:
        date = datetime.fromisoformat(start)
        end = (date + timedelta(days=7)).strftime("%Y-%m-%d")
        weekly.append(
            (
                date.strftime("%d %b") + " week",
                dict(
                    collections.Counter(
                        r["stance"] for r in recent if start <= r["day"] < end
                    )
                ),
            )
        )
    tone_counts = collections.Counter(r["tone"] for r in recent)
    tone_entries = [
        (
            "General emotional tone",
            {
                key: tone_counts.get(
                    {
                        "supportive": "positive",
                        "critical": "negative",
                        "neutral": "neutral",
                        "mixed": "mixed",
                        "unclear": "unclear",
                    }[key],
                    0,
                )
                for key in STANCES
            },
        ),
        ("Stance toward KTR", dict(counts)),
    ]
    tone_chart = (
        stacked(
            tone_entries,
            title="Emotional tone compared with target-specific stance",
            normalized=True,
        )
        .replace("Supportive</span>", "Positive tone / supportive stance</span>")
        .replace("Critical</span>", "Negative tone / critical stance</span>")
        .replace(
            '<th scope="col">Supportive</th>',
            '<th scope="col">Positive / supportive</th>',
        )
        .replace(
            '<th scope="col">Critical</th>', '<th scope="col">Negative / critical</th>'
        )
    )
    hashtags = collections.Counter()
    for r in recent:
        hashtags.update(
            set(
                tag.lower()
                for tag in re.findall(
                    r"(?<!\w)#([A-Za-z][A-Za-z0-9_]*)", source[r["id"]]["message"] or ""
                )
                if tag.lower() not in {"ktr", "ktrbrs", "brs", "kcr", "telangana"}
            )
        )
    # Per-post set prevents repeated hashtags inside one post inflating prevalence.
    metrics = [
        ("Likes", totals["likes"]),
        ("Reposts", totals["reposts"]),
        ("Replies", totals["replies"]),
        ("Bookmarks", totals["bookmarks"]),
    ]
    quality_entries = [
        ("Input rows / unique posts", len(rows)),
        ("Recent: Sep 1 - Oct 5", len(recent_all)),
        ("Recent: retained for KTR analysis", len(recent)),
        ("Older context", len(historical)),
        ("Unrelated: all years", len(unrelated)),
        (
            "Context needed: recent",
            sum(r["clarity"] == "context_needed" for r in recent),
        ),
        ("Missing post text", sum(not r.get("message") for r in source)),
    ]
    overview = f"""<section id="overview"><div class="section-heading"><p class="eyebrow">01 / Executive readout</p><h2>A selected conversation, seen from several angles.</h2></div><div class="takeaways"><article><span class="index">01</span><h3>{pct(counts["neutral"], len(recent))} neutral or reporting</h3><p>Author stance is distinct from the tone of an accusation or political attack. Supportive: {counts["supportive"]}; critical: {counts["critical"]}; mixed: {counts["mixed"]}; unclear: {counts["unclear"]}.</p></article><article><span class="index">02</span><h3>{esc(SHORT[topics[0]])} leads by post count</h3><p>{topic_counts[topics[0]]} of {len(recent)} recent retained posts have this primary subject. Topic labels describe the collected texts, including quoted claims.</p></article><article><span class="index">03</span><h3>{datetime.fromisoformat(peak_day).strftime("%d %b")} has the densest collection</h3><p>{peak_n} retained posts carry this publication date. This is sample density, not a measured platform-wide attention peak.</p></article></div></section>"""
    timeline = (
        '<section id="timeline"><div class="section-heading"><p class="eyebrow">02 / Publication timeline</p><h2>When posts appeared, and how their stance varied.</h2><p>September 1 - October 5, 2026, IST. Every recent chart uses the same '
        + str(len(recent))
        + ' retained posts. Gaps mean no post in this collection; October 5 is partial.</p></div><div class="grid">'
    )
    timeline += card(
        "Daily conversation volume",
        "Stacked counts preserve the daily denominator.",
        daily_chart(recent),
        wide=True,
    )
    timeline += card(
        "Daily stance composition",
        "Days with fewer than 10 posts are marked at the baseline and their shares are suppressed.",
        daily_chart(recent, share=True),
        wide=True,
    )
    timeline += card(
        "Weekly view",
        "Publication weeks start Monday. First and last weeks have only partial window coverage.",
        stacked(weekly, title="Weekly collected stance counts"),
    )
    timeline += card(
        "Sentiment in the older context",
        "Retained posts before September 2026 by publication year. Sparse, uneven selection cannot establish a long-term trend.",
        stacked(
            [
                (
                    str(year),
                    dict(
                        collections.Counter(
                            r["stance"]
                            for r in historical
                            if r["year"] == year and r["stance"] != "unrelated"
                        )
                    ),
                )
                for year in sorted({r["year"] for r in historical})
            ],
            title="Stance counts in older retained posts by publication year",
        ),
    )
    timeline += "</div></section>"
    stance = '<section id="stance"><div class="section-heading"><p class="eyebrow">03 / Sentiment, with a target</p><h2>Emotion and support are different signals.</h2><p>Neutral includes reports and statements without an expressed author judgment of KTR. Unclear preserves posts that depend on absent media, sarcasm, or context.</p></div><div class="grid">'
    stance += card(
        "Stance toward KTR",
        "Counts and rounded percentages describe the selected sample only; rounded percentages may not sum to 100%.",
        stacked(
            [("Recent retained sample", dict(counts))],
            title="Recent relevant KTR stance composition",
            normalized=True,
        )
        + "".join(
            f'<p class="countline"><span>{LABELS[k]}</span><strong>{counts[k]} / {pct(counts[k], len(recent))}</strong></p>'
            for k in STANCES
        ),
    )
    stance += card(
        "Tone versus stance",
        "A negatively worded attack on a rival can still favor KTR; quoted allegations need attribution.",
        tone_chart,
    )
    stance += card(
        "Remove the subject account",
        "KTRBRS-authored posts are separated by exact handle. Other accounts remain in the sample without inferred affiliation.",
        stacked(
            official_entries,
            title="Stance mix with and without KTRBRS posts",
            normalized=True,
        ),
    )
    stance += card(
        "Change the denominator",
        "Equal-author weighting averages known authors' post labels; missing handles are excluded. Views weight counters, not endorsement.",
        weight_chart,
    )
    stance += "</div></section>"
    themes = '<section id="themes"><div class="section-heading"><p class="eyebrow">04 / Discussion subjects</p><h2>The stories inside the sentiment.</h2><p>One primary topic per post prevents double counting. Broad subjects can contain support, criticism, neutral reporting and uncertain references.</p></div><div class="grid">'
    themes += card(
        "Topic and stance",
        "Topics ranked by collected post count. Each colored segment is an author stance label.",
        stacked(topic_entries, title="Main topic counts and stance breakdown"),
        wide=True,
    )
    themes += card(
        "Topic calendar",
        "Weekly counts; cells retain their exact values. Darker cells contain more posts.",
        heatmap(recent, topics),
        wide=True,
    )
    themes += card(
        "Recurring hashtags",
        "Number of posts containing a Latin-script tag, counted once per post. Generic KTR/BRS/KCR/Telangana tags excluded.",
        bars(
            [("#" + k, v) for k, v in hashtags.most_common(10)],
            title="Recurring non-generic Latin-script hashtags",
        ),
    )
    themes += card(
        "Text script coverage",
        "Script detection is a reproducible character check, not language identification. Transliteration remains in Latin / other.",
        bars(
            collections.Counter(r["script"] for r in recent).most_common(),
            title="Recent relevant text script composition",
        ),
    )
    themes += '</div><div class="topic-briefs">'
    for topic in topics[:3]:
        subset = [r for r in recent if r["topic"] == topic]
        topic_stances = collections.Counter(r["stance"] for r in subset)
        examples = []
        for stance_key in ["neutral", "critical", "supportive", "unclear"]:
            candidates = [
                r
                for r in subset
                if r["stance"] == stance_key and r["clarity"] == "clear"
            ]
            if candidates:
                examples.append(max(candidates, key=lambda r: r["views"]))
            if len(examples) == 2:
                break
        themes += f'<article class="topic-brief"><h3>{esc(SHORT[topic])}</h3><p class="small">{len(subset)} posts: {topic_stances["neutral"]} neutral, {topic_stances["critical"]} critical, {topic_stances["supportive"]} supportive, {topic_stances["mixed"]} mixed, {topic_stances["unclear"]} unclear.</p>'
        for example in examples:
            themes += f'<p>{esc(example["summary"])} <a href="#evidence" data-id="{example["id"]}">Post {example["id"] + 1}: {LABELS[example["stance"]]}</a></p>'
        themes += "</article>"
    themes += '</div><p class="small">Examples above are selected for visibility and contrasting stances, not randomly sampled or independently verified claims.</p></section>'

    attention = '<section id="attention"><div class="section-heading"><p class="eyebrow">05 / Recorded attention</p><h2>Visibility is uneven. Counters do not express agreement.</h2><p>Interactions = likes + reposts + replies + bookmarks. Each counter is a snapshot and may overlap in users. Older posts have had longer to accumulate activity.</p></div><div class="grid">'
    attention += card(
        "Visibility and response",
        "Logarithmic axes keep small and large posts visible. Select a point for its source and label rationale.",
        scatter(recent),
        wide=True,
    )
    attention += card(
        "Typical response by stance",
        "The middle 50% and median show skew more clearly than an average. Whiskers span the observed minimum and maximum.",
        distribution(recent),
    )
    attention += card(
        "Recorded interaction mix",
        "Four activity types, summed across the recent retained sample. No unique-user or reach estimate.",
        bars(
            metrics, title="Recorded interaction counters by type", unit="interactions"
        ),
    )
    attention += card(
        "Post concentration by author",
        f"The five most prolific handles account for {top5_share:.0f}% of posts with known authors. Missing handles are excluded from author-based views. The dashed diagonal is equal contribution.",
        concentration_chart,
    )
    top_chart = ""
    max_view = top_views[0]["views"]
    for rank, r in enumerate(top_views):
        y = rank * 45 + 12
        top_chart += text(0, y + 17, f"{rank + 1:02d}  @{r['handle']}", cls="bar-label")
        top_chart += (
            f'<a href="#evidence" data-id="{r["id"]}" aria-label="Inspect post {r["id"] + 1}"><rect class="{r["stance"]}" x="235" y="{y}" width="{370 * r["views"] / max_view:.1f}" height="22"><title>{esc(r["summary"])} / {r["views"]:,} recorded views</title></rect></a>'
            + text(620, y + 17, number(r["views"]), cls="value")
        )
    attention += card(
        "Highest-view recent posts",
        "Ranked by recorded views, with stance color. Select a bar to read the paraphrase and open the original post.",
        legend()
        + svg(
            "Eight recent retained posts with highest recorded views",
            top_chart,
            height=len(top_views) * 45 + 30,
        ),
        wide=True,
    )
    attention += "</div></section>"
    evidence = (
        """<section id="evidence"><div class="section-heading"><p class="eyebrow">06 / Evidence explorer</p><h2>Inspect the posts behind the charts.</h2><p>All 352 records are available as ASCII English paraphrases, with original links. Filters affect this explorer only; the analytical charts retain the fixed recent scope.</p></div><div class="filters"><label>Time scope<select id="scope" aria-label="Time scope"><option value="recent">Recent relevant</option><option value="all">All supplied posts</option><option value="historical">Older context</option><option value="excluded">Unrelated exclusions</option></select></label><label>Stance<select id="stance-filter" aria-label="Stance"><option value="all">All stances</option>"""
        + "".join(
            f'<option value="{k}">{LABELS[k]}</option>' for k in [*STANCES, "unrelated"]
        )
        + """</select></label><label>Main topic<select id="topic-filter" aria-label="Main topic"><option value="all">All topics</option>"""
        + "".join(f'<option value="{esc(t)}">{esc(SHORT[t])}</option>' for t in SHORT)
        + """</select></label><label>Search paraphrases<input type="search" id="search" aria-label="Search paraphrases" placeholder="e.g. assets, padayatra"></label><label>Order<select id="order" aria-label="Order"><option value="date">Newest first</option><option value="views">Most views</option><option value="interactions">Most interactions</option></select></label><button id="reset" type="button">Reset filters</button></div><p id="results" role="status" class="small"></p><div id="evidence-list">"""
    )
    for r in sorted(rows, key=lambda r: r["date"], reverse=True):
        evidence += f'''<article class="evidence-row" id="post-{r["id"]}" data-row="{r["id"]}"><div class="post-meta"><span class="pill {r["stance"]}-text">{LABELS[r["stance"]]}</span><span>{r["day"]}</span><span>{esc(SHORT[r["topic"]])}</span></div><h3>{esc(r["summary"])}</h3><p class="small">Post {r["id"] + 1} | @{esc(r["handle"] or "[missing]")} | {r["views"]:,} views | {r["interactions"]:,} interactions</p><details><summary>Label rationale and source</summary><p>{esc(r["reason"])}</p><p class="small">Tone: {r["tone"]}. Context: {r["clarity"].replace("_", " ")}. Format: {r["format"].replace("_", " ")}. These are AI-assisted interpretations.</p><p><a href="{esc(r["link"])}" target="_blank" rel="noopener noreferrer">Open original post on X</a></p></details></article>'''
    evidence += '</div><div class="pagination" id="pagination" hidden><button id="previous-page" type="button">Previous posts</button><span id="page-status"></span><button id="next-page" type="button">Next posts</button></div><p id="empty" hidden>No posts match these filters. Reset filters to restore the recent sample.</p></section>'
    methods = """<section id="method"><div class="section-heading"><p class="eyebrow">07 / Coverage and method</p><h2>What this file supports.</h2></div><div class="grid">"""
    methods += card(
        "Collection audit",
        "Inputs and classification coverage, with the full file kept separate from the analytical recent sample.",
        bars(quality_entries, title="Collection and classification audit"),
    )
    methods += f"""<article class="card"><h3>Read this as a sample report</h3><ul><li>The supplied file was described as X's top category. Its exact search query, collection protocol and completeness were not supplied. Selection favors what was collected, not a random population sample.</li><li>Publication dates span August 29, 2017 to October 5, 2026. The analytical window is September 1 - October 5, 2026 IST, including all {len(recent_all)} recent records before relevance filtering. The retained sample includes unclear records rather than forcing their exclusion.</li><li>{len(unrelated)} unrelated records are excluded from target sentiment. Historical records remain in the explorer and coverage chart.</li><li>{earlier} records predate their linked parent. Parent links are treated as collection associations, never confirmed reply relationships.</li><li>All rows imply a common age-based reference time of {capture_ist.strftime("%d %b %Y, %H:%M:%S")} IST. This is inferred from date + age_hours, not independently verified as counter capture time.</li><li>Views are summed counters, not unique reach. The unknown collection scores buzz and keep are excluded.</li></ul></article>"""
    methods += f"""<article class="card wide"><h3>Classification protocol and review status</h3><p>GPT-4.1 processed each full text in bounded batches using a fixed target-specific rubric. It returned stance, emotional tone, one topic, post format, context status, an English paraphrase and a rationale. No unseen video or image was interpreted. Reported allegations remain attributed claims. KTRBRS is a handle-based grouping, without a live identity check.</p><p>{esc(json.loads((args.labels.parent / "review-summary.json").read_text(encoding="utf-8"))["description"]) if (args.labels.parent / "review-summary.json").exists() else "Draft labels have not yet received a separate audit."}</p><p>Labels are AI-assisted judgments, not independently validated ground truth. No classifier accuracy, confidence interval, trend significance or electorate approval rate is claimed. Publication-ready sentiment totals require the official team's review, especially Telugu nuance, sarcasm and media-dependent posts. Filter to unclear posts to inspect unresolved examples.</p><details><summary>Rubric: six stance categories</summary><dl><dt>Supportive</dt><dd>Explicit favorable author judgment of KTR or his record.</dd><dt>Critical</dt><dd>Explicit unfavorable author judgment, blame or ridicule toward KTR.</dd><dt>Neutral / reporting</dt><dd>Reporting, quotations, self-announcements or requests without a clear author judgment of KTR.</dd><dt>Mixed</dt><dd>Both favorable and unfavorable judgment toward KTR in the same post.</dd><dt>Unclear</dt><dd>KTR-relevant but stance depends on absent media, context or ambiguous wording.</dd><dt>Unrelated</dt><dd>Text does not meaningfully concern the Telangana politician.</dd></dl></details><details><summary>Reproducibility and design sources</summary><p>Source: user-supplied ktr.json, {len(rows)} unique links. SHA-256: <code class="hash">{hashlib.sha256(source_bytes).hexdigest()}</code>. Every chart is built from the supplied fields and the included label ledger. Quantiles use linear interpolation; equal-author weighting gives each handle total weight one and distributes it across that author's posts.</p><p>The editorial structure follows the local political-sentiment pipeline and the evidence-focused Spirit report in <a href="https://github.com/prudhvi1709/movie-analysis" target="_blank" rel="noopener noreferrer">your movie-analysis repository</a>. The pink accent #E6007E is observed in the prior KTR configuration; it is a proposed report accent, not a verified official brand standard. No official logo was supplied. Native SVG keeps the report offline and removes CDN dependencies.</p></details></article></div></section>"""
    style = (Path(__file__).parent / "report.css").read_text(encoding="utf-8")
    script = (Path(__file__).parent / "report.js").read_text(encoding="utf-8")
    payload = json.dumps(rows, ensure_ascii=True, separators=(",", ":")).replace(
        "<", "\\u003c"
    )
    script = script.replace(
        "'use strict';", "'use strict';\n  const reportRows = " + payload + ";", 1
    )
    import base64

    css_hash = base64.b64encode(hashlib.sha256(style.encode()).digest()).decode()
    js_hash = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-{js_hash}'; style-src 'sha256-{css_hash}'; img-src data:; base-uri 'none'; object-src 'none'; form-action 'none'"><title>KTR | X Conversation Report | October 5, 2026</title><link rel="icon" href="data:,"><style>{style}</style></head><body><a class="skip" href="#overview">Skip to report</a><div class="wrap"><header><div class="top"><a class="wordmark" href="#overview">KTR<span> / X CONVERSATION REPORT</span></a><div class="tools"><button id="print" type="button">Print report</button><button id="theme" type="button" aria-pressed="false">Dark theme</button></div></div><div class="hero"><p class="eyebrow">Prepared for the KTR official team / Review draft</p><h1>The KTR conversation.<br>Across time, topic<br>and attention.</h1><p class="deck">A descriptive reading of the supplied X collection, with target-specific sentiment and traceable evidence.</p><p class="scope-note">Recent analysis: 01 Sep - 05 Oct 2026 | All dates IST<br>Historical context: 2017 - 2026 | Built 05 Oct 2026</p><a class="primary-link" href="#timeline">Explore the timeline</a><a class="secondary-link" href="#evidence">Inspect the evidence</a></div><div class="stats"><article><strong>{len(rows)}</strong><span>Unique supplied posts</span></article><article><strong>{len(recent)}</strong><span>Recent retained posts</span></article><article><strong>{int(authors)}</strong><span>Recent known handles</span></article><article><strong>{number(totals["views"])}</strong><span>Summed recent view counters</span></article></div><p class="scope-warning">Selected top-category sample. Sentiment shares describe these posts; recorded views are not unique reach or agreement.</p><nav aria-label="Report sections"><a href="#overview">Readout</a><a href="#timeline">Timeline</a><a href="#stance">Sentiment</a><a href="#themes">Topics</a><a href="#attention">Attention</a><a href="#evidence">Evidence</a><a href="#method">Method</a></nav></header><main>{overview}{timeline}{stance}{themes}{attention}{evidence}{methods}</main><footer><p>KTR / X conversation report. Descriptive analysis for internal review, October 5, 2026.</p><p>No policy recommendation, voter targeting, population approval estimate or allegation verification is inferred.</p></footer></div><dialog id="post-dialog"><div class="dialog-top"><h2>Post evidence</h2><button id="close-dialog" type="button">Close</button></div><div id="dialog-content"></div></dialog><script>{script}</script></body></html>"""
    if not document.isascii():
        raise ValueError("HTML output must use ASCII typography")
    args.destination.mkdir(parents=True, exist_ok=True)
    (args.destination / "ktr-report.html").write_text(document, encoding="utf-8")
    (args.destination / "ktr-report-data.json").write_text(
        json.dumps(
            {
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "recent_window": ["2026-09-01", "2026-10-05"],
                "metrics": {
                    "supplied_posts": len(rows),
                    "recent_before_exclusions": len(recent_all),
                    "recent_relevant": len(recent),
                    "historical": len(historical),
                    "unrelated_all_years": len(unrelated),
                    "stance_counts": dict(counts),
                    "views": totals["views"],
                    "recent_handles": authors,
                },
                "rows": rows,
            },
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )
    with (args.destination / "ktr-label-ledger.csv").open(
        "w", encoding="utf-8", newline=""
    ) as file:
        keys = [
            "id",
            "day",
            "handle",
            "stance",
            "tone",
            "topic",
            "format",
            "clarity",
            "summary",
            "reason",
            "views",
            "likes",
            "reposts",
            "replies",
            "bookmarks",
            "interactions",
            "link",
        ]
        writer = csv.DictWriter(file, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            {
                "recent": len(recent),
                "counts": dict(counts),
                "topics": dict(topic_counts),
                "unrelated": len(unrelated),
                "historical": len(historical),
                "views": totals["views"],
                "svg_count": document.count("<svg"),
            }
        )
    )


if __name__ == "__main__":
    main()
