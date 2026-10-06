"""
Four-week daily sentiment timeline (16 June - 13 July 2026) + pitch metadata
and cross-cutting shared narratives per persona.

28 days, split into 4 weeks:
  Week 1: Jun 16-22   Week 2: Jun 23-29   Week 3: Jun 30-Jul 6   Week 4: Jul 7-13
Shapes are grounded in the live-collected events: the Kaleshwaram 'blood for
farmers' firestorm (peaks week 4), KTR's farmers-water agitation + World Bank
vindication, Bandi's birthday goodwill (Jul 11), Revanth's self-inflicted crisis.

Daily series are sampled/modelled from the collected conversation, not a census.
"""

DAYS = (["Jun " + str(d) for d in range(16, 31)] +   # Jun 16-30 (15)
        ["Jul " + str(d) for d in range(1, 14)])      # Jul 1-13 (13)  => 28

# (positive, negative, neutral) per day
TIMELINE = {
    "ktr": [
        (6,6,6),(7,6,5),(6,7,6),(7,6,6),(6,5,6),(5,5,5),(6,6,6),      # wk1
        (7,6,6),(8,6,6),(7,7,6),(8,6,7),(7,6,6),(6,5,6),(7,6,6),      # wk2
        (8,7,7),(9,7,7),(9,7,7),(10,8,7),(9,7,7),(11,8,8),(12,9,8),   # wk3
        (14,9,9),(15,10,10),(16,11,10),(14,10,9),(15,9,10),(17,11,10),(12,9,9),  # wk4
    ],
    "bandi-sanjay": [
        (2,2,2),(2,3,2),(2,2,2),(2,3,2),(2,2,2),(1,2,2),(2,2,2),      # wk1
        (2,2,2),(2,3,2),(2,2,2),(2,3,2),(2,2,2),(2,2,2),(2,2,2),      # wk2
        (2,3,2),(3,2,2),(2,3,2),(3,2,2),(2,2,2),(2,2,2),(3,2,2),      # wk3
        (3,2,2),(3,2,2),(3,2,2),(4,2,3),(8,3,4),(5,3,3),(4,2,3),      # wk4
    ],
    "revanth-reddy": [
        (3,4,3),(3,4,3),(2,4,3),(3,4,3),(2,3,3),(2,3,2),(3,4,3),      # wk1
        (3,4,3),(2,4,3),(3,5,3),(2,4,3),(2,4,3),(2,3,3),(3,4,3),      # wk2
        (3,5,3),(2,5,3),(3,5,3),(2,5,3),(3,5,3),(2,6,3),(2,6,3),      # wk3
        (3,7,3),(3,7,4),(3,10,4),(3,9,4),(3,8,4),(4,8,4),(3,7,4),     # wk4
    ],
}

WEEK_PRESETS = {
    "Week 1 (Jun 16-22)": [0, 6],
    "Week 2 (Jun 23-29)": [7, 13],
    "Week 3 (Jun 30-Jul 6)": [14, 20],
    "Week 4 (Jul 7-13)": [21, 27],
    "All 4 weeks": [0, 27],
}

PITCH = {
    "ktr": {
        "risk": "The govt's 'economic terrorist' / Rs 1.5L cr Kaleshwaram-failure charge is the main line against BRS.",
        "win": "The farmers-water agitation and the 'blood for farmers' row put KTR on the moral high ground; base fully mobilised.",
        "actions": [
            "Keep the Kannepalli / farmers-water agitation visual and local - it is his best-performing narrative.",
            "Blunt the 'economic terrorist' charge with a crisp barrages-maintenance rebuttal before it sticks."
        ]
    },
    "bandi-sanjay": {
        "risk": "Residual POCSO / 'audio leak' noise can resurface and overshadow the goodwill.",
        "win": "Birthday goodwill and the 'BRS conspiracy' defense rallied the base - a rare positive-leaning fortnight.",
        "actions": [
            "Use the goodwill window to push a concrete governance message, not just thank-yous.",
            "Get ahead of the audio-leak story with a clear factual line rather than leaving it to supporters."
        ]
    },
    "revanth-reddy": {
        "risk": "The 'blood for farmers' / 'belt treatment' remark is a self-inflicted crisis drawing apology demands from all sides.",
        "win": "The 'economic terrorist' Kaleshwaram-failure framing and the debate challenge to KCR are his strongest counter.",
        "actions": [
            "Close the 'blood remark' episode fast with a clarification - it is bleeding sentiment daily.",
            "Move Kaleshwaram from rhetoric to the NDSA/CWC restoration facts, which favour the govt."
        ]
    },
}

# Cross-cutting storylines: the SAME event scores differently per leader.
SHARED_NARRATIVES = [
    {
        "event": "Kaleshwaram 'blood for farmers' row",
        "detail": "Revanth's 'spill their blood on farms' / 'belt treatment' remark vs BRS's water agitation.",
        "scores": {"revanth-reddy": "neg", "ktr": "pos", "bandi-sanjay": "pos"},
        "why": "A self-inflicted gaffe for Revanth; a moral-high-ground rallying point for KTR and an attack line for the BJP."
    },
    {
        "event": "Kaleshwaram project failure (Rs 1.5L cr)",
        "detail": "Revanth's PPT alleges BRS built a collapsing project and paid Rs 1.02L cr to contractors.",
        "scores": {"ktr": "neg", "revanth-reddy": "pos", "bandi-sanjay": "pos"},
        "why": "Puts BRS/KCR on the defensive; a win for Revanth's narrative and useful for the BJP."
    },
    {
        "event": "World Bank validates Telangana economy",
        "detail": "KTR frames the upper-middle-income tag as vindication of KCR's vision.",
        "scores": {"ktr": "pos", "revanth-reddy": "neg", "bandi-sanjay": "neu"},
        "why": "Credit war: BRS claims KCR's legacy; awkward for the incumbent Congress."
    },
    {
        "event": "Bandi birthday + 'BRS conspiracy' audio leak",
        "detail": "Birthday goodwill for Bandi; supporters frame a viral audio leak as a BRS conspiracy.",
        "scores": {"bandi-sanjay": "pos", "ktr": "neg", "revanth-reddy": "neu"},
        "why": "Rallies the BJP base and paints BRS as conspirators."
    },
    {
        "event": "Shabad POCSO / law-and-order",
        "detail": "KTR blames the govt after a POCSO accused's bail and six deaths.",
        "scores": {"revanth-reddy": "neg", "ktr": "pos", "bandi-sanjay": "pos"},
        "why": "A law-and-order hit for the govt; an attack opportunity for the opposition."
    },
    {
        "event": "Civic grievances (power, ration, bus stands)",
        "detail": "Citizens tag the CM over ration quality, toilets, water and outages.",
        "scores": {"revanth-reddy": "neg", "ktr": "pos", "bandi-sanjay": "neu"},
        "why": "Daily friction lands on the ruling Congress."
    },
]
