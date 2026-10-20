# Political Sentiment Weekly Pipeline

Automated weekly media and social-sentiment report, rebuilt from the KTR pilot
and parameterised so the same pipeline runs for any politician.

## Flow

1. Collect (per week, per person)
   - X / social: Brave browser agent. Day-sliced handle search + name-variant
     searches (English + Telugu) + reply-thread crawls on the top 5 posts.
   - News: WebSearch + web fetch across English and Telugu outlets.
2. Enrich: sentiment, topic and issue tagging plus insight bullets (LLM).
3. Build: matplotlib charts -> python-pptx decks (X deck + news deck) -> index.html.

## Layout

- `scripts/config.py` - per-person config (handle, party, name variants, branding)
- `scripts/build_charts.py` - branded matplotlib charts
- `scripts/build_decks.py` - python-pptx X deck + news deck
- `scripts/build_dashboard.py` - single-file Chart.js dashboard (CDN)
- `scripts/run.py` - orchestrator: `python3 run.py <slug>`
- `data/<slug>_week_data.json` - the dataset that drives all outputs
- `output/<slug>/` - charts, two .pptx decks, index.html

## Reports

- [Political stories dashboard](https://prudhvi1709.github.io/political-sentiment-pipeline/output/)
- [Anurag Thakur: X and Reddit](https://prudhvi1709.github.io/political-sentiment-pipeline/output/anurag-thakur/2026-10-20/the-verdict.html)
- [K. T. Rama Rao](https://prudhvi1709.github.io/political-sentiment-pipeline/output/ktr/2026-10-05/ktr-report.html)
- [Bandi Sanjay](https://prudhvi1709.github.io/political-sentiment-pipeline/output/bandi-sanjay/)
- [Revanth Reddy](https://prudhvi1709.github.io/political-sentiment-pipeline/output/revanth-reddy/)

## Dataset schema (`data/<slug>_week_data.json`)

```
person:    name, handle, party, role
week:      start, end, label
branding:  accent, accent2, dark, ink   (party colours)
x_data:    official_posts, sample_size,
           sentiment{positive,negative,neutral},
           daily[{date,pos,neg,neu}],
           issues[{label,count}], issue_notes[],
           top_posts[{text,views}]
news_data: article_count, sentiment{...},
           topics[{label,count}], topic_notes[],
           publications[{label,count}], languages{lang:count}, notes[]
stories:   [{title,detail}]   (5 defining stories)
insights:  [str]
```

## Notes / caveats

- X figures are a sample, not a census (X caps search depth for browser agents).
- Telugu print is typically under-sampled vs the original manual reports.
- Dashboard charts load Chart.js from CDN: they render in a real browser
  (Chrome/Brave) but show empty inside sandboxed in-app previews.
