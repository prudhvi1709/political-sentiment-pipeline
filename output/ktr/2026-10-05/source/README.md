# KTR X conversation report

Prepared October 5, 2026 for review by the KTR official team.

Open `ktr-report.html` in a browser. It is a standalone offline file with 18 native SVG visualizations, light/dark themes, chart data tables, source-linked post details and a searchable evidence explorer. Share the HTML alone to share the report. Original X links require internet access.

## Scope and findings

The supplied ktr.json contains 352 unique posts spanning August 29, 2017 to October 5, 2026. Dates are displayed in Asia/Kolkata (IST).

- 320 posts fall in September 1 - October 5, 2026.
- 287 recent posts are retained for analysis, including unresolved context cases.
- 34 unrelated records are excluded across the full file, including 33 in the recent window and one historical kei-truck post.
- 32 posts predate September 2026; 31 are retained as older context.
- Recent stance labels: 128 neutral, 78 critical, 42 supportive, 39 unclear, 0 mixed.
- Assets and allegations are the largest primary topic: 93 recent posts. Political rivalry has 47. Other/unclear has 40.
- October 2 has the largest collected recent count: 78 retained posts. This is collection density, not platform-wide activity.
- The recent sample has 155 known handles and one missing handle. Missing handles are excluded from author-based weighting and concentration views.
- Summed recent recorded views: 10,857,601. These counters overlap in people and do not measure unique reach, endorsement or launch-day performance.

## Sentiment method

The target is KTR. General emotional tone is tagged separately. A post attacking Revanth can support KTR; a journalist quoting an accusation can remain neutral in author stance. Quotes are attributed, allegations are not independently verified, and missing media is not interpreted.

GPT-4.1 classified all 352 decoded multilingual texts using a fixed rubric. The agent reviewed all final paraphrases and rationales and checked 134 selected original texts, including high-attention posts, attribution cases and Telugu sarcasm. There were 42 source-checked label revisions. The resulting labels remain AI-assisted interpretations. No independent ground-truth validation, classifier accuracy, confidence interval, electorate approval estimate or human signoff is claimed.

Neutral includes reports, subject-account activity and requests without a clear author judgment. Unclear preserves ambiguous targets, missing content, sarcasm and media dependence. KTRBRS is grouped by exact handle; identity was not checked live. KTR_News and other accounts are not assumed official or assigned political affiliations.

Each post has one primary topic. Interaction totals sum likes, reposts, replies and bookmarks. Quantiles use linear interpolation. Equal-author weighting gives each known handle total weight one, distributed across its post labels. Views-weighted composition is a sensitivity view, not an opinion estimate. Whole-number percentages can total above or below 100% after rounding.

## Collection limitations

The user described this as X's top category. Search query, ranking algorithm, collection protocol and completeness were not supplied. This is a selected sample, not a census or representative survey.

The parent_link field is treated as a collection association: 165 posts predate their linked parent. It cannot establish actual reply relationships. Every recorded date plus age_hours implies October 5, 2026 at 17:05:46 IST, but that is not independent verification of counter capture time. Undocumented buzz and keep scores are unused.

Historical observations are sparse and selected. Publication dates determine chart bins; cumulative snapshot engagement cannot establish when attention happened or whether sentiment changed in the wider public.

Source SHA-256: `8e74cdfac1f5c05480201ce72445b31b6527c97e56e01dc62362b8c3aafd8b8f`.

## Files and reproduction

- ktr-report.html: standalone report, no external scripts/fonts/CDNs.
- ktr-label-ledger.csv: all 352 labels, paraphrases, rationale, counters and original links. `id` is a zero-based source row index; displayed post numbers are `id + 1`.
- ktr-report-data.json: derived row metadata and report totals. It excludes original post text and names.
- ktr-report-source.zip: generator, CSS/JavaScript templates, final labels, classification manifest/rubric, revision ledger and verification evidence. Raw ktr.json is not bundled.

To rebuild, unzip the source bundle and run:

```sh
uv run build_report.py /path/to/ktr.json final-labels.json /path/to/output
```

The builder uses the Python standard library and requires the exact classified snapshot. Rebuilding from supplied labels makes no model calls. Editing the reviewed labels requires renewing semantic review and browser checks; no validated sentiment accuracy is implied by reproduction.

Design follows the local political-sentiment pipeline and the source-led Spirit report in [movie-analysis](https://github.com/prudhvi1709/movie-analysis). The pink accent #E6007E comes from the previous KTR pipeline configuration and is not a verified official brand standard. No official logo was supplied.

## Verification

The report's load-bearing counts and sums were recomputed independently using a different date-conversion path. Browser checks cover 1440, 768 and 375 pixel widths; light/dark themes; filter/search/reset/sort; pagination; bookmarked state and section restoration; invalid URL fallback; mouse/keyboard post inspection; Escape; reduced motion; and no-JavaScript access. There were no reported browser errors or page overflow. Text and chart color pairings passed the skill's contrast checks. These checks are not a full WCAG audit or a validation of political sentiment labels.

Evidence filters affect only the explorer. Charts retain the fixed recent scope; the older-context stance chart covers the retained historical records. The print action prints the displayed report and current evidence page. Without JavaScript, the charts, tables and complete evidence ledger remain available.

Mobile review: checked at 320, 375, 390 and 430 pixels with no reported page overflow. Timeline charts open on the latest dates on small screens, with a repeated right-side scale and a scroll hint. Filters, pagination and the post dialog were exercised with touch emulation.
