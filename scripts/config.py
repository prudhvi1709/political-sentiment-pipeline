"""
Per-person configuration for the political sentiment weekly pipeline.

Each entry defines the subject (name, X handle, party, role), the search
name-variants the browser agent should use for X collection, and party-based
branding (accent colours) so every deck/dashboard is on-brand.

This mirrors the KTR pilot recipe and parameterises it so the exact same
pipeline runs for any politician.
"""

PEOPLE = {
    "ktr": {
        "name": "K. T. Rama Rao",
        "short": "KTR",
        "handle": "@KTRBRS",
        "party": "BRS",
        "role": "BRS Working President | MLA, Sircilla",
        "name_variants": ["@KTRBRS", "KTR", "Rama Rao", "కేటీఆర్"],
        "branding": {
            "accent": "#E6007E",   # BRS pink
            "accent2": "#F5A623",
            "dark": "#14111C",
            "ink": "#1A1A1A",
        },
    },
    "bandi-sanjay": {
        "name": "Bandi Sanjay Kumar",
        "short": "Bandi Sanjay",
        "handle": "@bandisanjay_bjp",
        "party": "BJP",
        "role": "Union Minister of State | BJP, Karimnagar MP",
        "name_variants": [
            "@bandisanjay_bjp", "Bandi Sanjay", "Sanjay Kumar BJP",
            "బండి సంజయ్",
        ],
        "branding": {
            "accent": "#F47216",   # BJP saffron
            "accent2": "#138808",  # green
            "dark": "#1A1206",
            "ink": "#1A1A1A",
        },
    },
    "revanth-reddy": {
        "name": "A. Revanth Reddy",
        "short": "Revanth Reddy",
        "handle": "@revanth_anumula",
        "party": "INC",
        "role": "Chief Minister of Telangana | TPCC, Congress",
        "name_variants": [
            "@revanth_anumula", "Revanth Reddy", "CM Revanth", "రేవంత్ రెడ్డి",
        ],
        "branding": {
            "accent": "#1F6FB2",   # Congress blue
            "accent2": "#19AAA1",
            "dark": "#0B1622",
            "ink": "#1A1A1A",
        },
    },
}


def get(slug):
    if slug not in PEOPLE:
        raise KeyError(f"Unknown person slug: {slug}. Known: {list(PEOPLE)}")
    return PEOPLE[slug]
