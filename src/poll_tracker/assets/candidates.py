import polars as pl

candidates = {
    "arthaud": {
        "name": "Nathalie Arthaud",
        "aliases": [
            "Arthaud",
            "Arthaud (LO)",
            "Nathalie Arthaud (LO)"
        ]
    },
    "poutou": {
        "name": "Philippe Poutou",
        "aliases": [
            "Poutou",
            "Poutou (NPA)",
            "Philippe Poutou (NPA)"
        ]
    },
    "melenchon": {
        "name": "Jean-Luc Mélenchon",
        "aliases": [
            "Mélenchon",
            "Mélenchon (LFI)",
            "Mélenchon (FG)",
            "Jean-Luc Mélenchon (LFI)"
        ]
    },
    "roussel": {
        "name": "Fabien Roussel",
        "aliases": [
            "Roussel",
            "Roussel (PCF)",
            "Fabien Roussel (PCF)"
        ]
    },
    "hidalgo": {
        "name": "Anne Hidalgo",
        "aliases": [
            "Hidalgo",
            "Hidalgo (PS)",
            "Anne Hidalgo (PS)"
        ]
    },
    "jadot": {
        "name": "Yannick Jadot",
        "aliases": [
            "Jadot",
            "Jadot (EÉLV)",
            "Jadot (EELV)",
            "Yannick Jadot (EELV)"
        ]
    },
    "macron": {
        "name": "Emmanuel Macron",
        "aliases": [
            "Macron",
            "Macron (LREM)",
            "Macron (EM)",
            "Emmanuel Macron"
        ]
    },
    "pecresse": {
        "name": "Valérie Pécresse",
        "aliases": [
            "Pécresse",
            "Pécresse (LR)",
            "Valérie Pécresse (LR)"
        ]
    },
    "lassalle": {
        "name": "Jean Lassalle",
        "aliases": [
            "Lassalle",
            "Lassalle (RES)",
            "Jean Lassalle (RES)"
        ]
    },
    "dupont_aignan": {
        "name": "Nicolas Dupont-Aignan",
        "aliases": [
            "Dupont-Aignan",
            "Dupont-Aignan (DLF)",
            "Nicolas Dupont-Aignan (DLF)"
        ]
    },
    "le_pen": {
        "name": "Marine Le Pen",
        "aliases": [
            "Le Pen",
            "Le Pen (RN)",
            "Le Pen (FN)",
            "Marine Le Pen (RN)",
            "Marine Le Pen (FN)"
        ]
    },
    "zemmour": {
        "name": "Éric Zemmour",
        "aliases": [
            "Zemmour",
            "Zemmour (REC)",
            "Éric Zemmour (REC)"
        ]
    },
    "fillon": {
        "name": "François Fillon",
        "aliases": [
            "Fillon",
            "Fillon (LR)",
            "François Fillon (LR)"
        ]
    },
    "hollande": {
        "name": "François Hollande",
        "aliases": [
            "Hollande",
            "François Hollande (PS)"
        ]
    },
    "sarkozy": {
        "name": "Nicolas Sarkozy",
        "aliases": [
            "Sarkozy",
            "Nicolas Sarkozy (UMP)"
        ]
    },
    "chirac": {
        "name": "Jacques Chirac",
        "aliases": [
            "Chirac",
            "Jacques Chirac (RPR)"
        ]
    },
    "mitterrand": {
        "name": "François Mitterrand",
        "aliases": [
            "Mitterrand",
            "François Mitterrand (PS)"
        ]
    }
}
election_candidates = {
    "2022": [
        "arthaud",
        "poutou",
        "roussel",
        "melenchon",
        "hidalgo",
        "jadot",
        "macron",
        "pecresse",
        "lassalle",
        "dupont_aignan",
        "le_pen",
        "zemmour"
    ],
    "2017": [
        "arthaud",
        "poutou",
        "melenchon",
        "macron",
        "lassalle",
        "fillon",
        "dupont_aignan",
        "le_pen"
    ],
    "2012": [
        "arthaud",
        "poutou",
        "melenchon",
        "hollande",
        "jadot",
        "sarkozy",
        "dupont_aignan",
        "le_pen"
    ]
}
second_round = {
    "2022": ["macron", "le_pen"],
    "2017": ["macron", "le_pen"],
    "2012": ["hollande", "sarkozy"],
    "2007": ["sarkozy", "royal"],
    "2002": ["chirac", "le_pen"]
}

alias_to_id = {
    alias.lower(): cid
    for cid, data in candidates.items()
    for alias in data["aliases"]
}


def resolve_candidate(value):
    return alias_to_id.get(value.lower())


candidate_map = pl.DataFrame(
    {
        "candidate_alias": list(alias_to_id.keys()),
        "candidate_id": list(alias_to_id.values())
    }
)