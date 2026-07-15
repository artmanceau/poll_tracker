import polars as pl

candidates = {
   "arthaud": {
        "name": "Nathalie Arthaud",
        "color": "#8B0000",  # Dark red
        "aliases": [
            "Arthaud",
            "Arthaud (LO)",
            "Nathalie Arthaud (LO)"
        ]
    },
    "poutou": {
        "name": "Philippe Poutou",
        "color": "#C62828",  # Red
        "aliases": [
            "Poutou",
            "Poutou (NPA)",
            "Philippe Poutou (NPA)"
        ]
    },
    "melenchon": {
        "name": "Jean-Luc Mélenchon",
        "color": "#E53935",  # Bright left red
        "aliases": [
            "Mélenchon",
            "Mélenchon (LFI)",
            "Mélenchon (FG)",
            "Jean-Luc Mélenchon (LFI)"
        ]
    },
    "roussel": {
        "name": "Fabien Roussel",
        "color": "#D32F2F",  # Communist red
        "aliases": [
            "Roussel",
            "Roussel (PCF)",
            "Fabien Roussel (PCF)"
        ]
    },
    "hidalgo": {
        "name": "Anne Hidalgo",
        "color": "#E91E63",  # Socialist pink
        "aliases": [
            "Hidalgo",
            "Hidalgo (PS)",
            "Anne Hidalgo (PS)"
        ]
    },
    "jadot": {
        "name": "Yannick Jadot",
        "color": "#43A047",  # Green
        "aliases": [
            "Jadot",
            "Jadot (EÉLV)",
            "Jadot (EELV)",
            "Yannick Jadot (EELV)"
        ]
    },
    "macron": {
        "name": "Emmanuel Macron",
        "color": "#FBC02D",  # Yellow
        "aliases": [
            "Macron",
            "Macron (LREM)",
            "Macron (EM)",
            "Emmanuel Macron"
        ]
    },
    "pecresse": {
        "name": "Valérie Pécresse",
        "color": "#1E88E5",  # Centre-right blue
        "aliases": [
            "Pécresse",
            "Pécresse (LR)",
            "Valérie Pécresse (LR)"
        ]
    },
    "lassalle": {
        "name": "Jean Lassalle",
        "color": "#8D6E63",  # Brown
        "aliases": [
            "Lassalle",
            "Lassalle (RES)",
            "Jean Lassalle (RES)"
        ]
    },
    "dupont_aignan": {
        "name": "Nicolas Dupont-Aignan",
        "color": "#3949AB",  # Indigo
        "aliases": [
            "Dupont-Aignan",
            "Dupont-Aignan (DLF)",
            "Nicolas Dupont-Aignan (DLF)"
        ]
    },
    "le_pen": {
        "name": "Marine Le Pen",
        "color": "#0D47A1",  # Navy blue
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
        "color": "#212121",  # Almost black
        "aliases": [
            "Zemmour",
            "Zemmour (REC)",
            "Éric Zemmour (REC)"
        ]
    },
    "fillon": {
        "name": "François Fillon",
        "color": "#1976D2",  # LR blue
        "aliases": [
            "Fillon",
            "Fillon (LR)",
            "François Fillon (LR)"
        ]
    },
    "hollande": {
        "name": "François Hollande",
        "color": "#EC407A",  # PS pink
        "aliases": [
            "Hollande",
            "François Hollande (PS)"
        ]
    },
    "sarkozy": {
        "name": "Nicolas Sarkozy",
        "color": "#1565C0",  # UMP blue
        "aliases": [
            "Sarkozy",
            "Nicolas Sarkozy (UMP)"
        ]
    },
    "chirac": {
        "name": "Jacques Chirac",
        "color": "#0D47A1",  # Gaullist navy
        "aliases": [
            "Chirac",
            "Jacques Chirac (RPR)"
        ]
    },
    "mitterrand": {
        "name": "François Mitterrand",
        "color": "#C2185B",  # Historic PS magenta
        "aliases": [
            "Mitterrand",
            "François Mitterrand (PS)"
        ]
    },
    "taubira": {
        "name": "Christiane Taubira",
        "color": "#AD1457",
        "aliases": [
            "Taubira",
            "Christiane Taubira",
            "Taubira (DVG)",
        ],
    },

    "montebourg": {
        "name": "Arnaud Montebourg",
        "color": "#C2185B",
        "aliases": [
            "Montebourg",
            "Arnaud Montebourg",
            "Montebourg (DVG)",
        ],
    },

    "asselineau": {
        "name": "François Asselineau",
        "color": "#5C6BC0",
        "aliases": [
            "Asselineau",
            "François Asselineau",
            "Asselineau (UPR)",
        ],
    },

    "philippot": {
        "name": "Florian Philippot",
        "color": "#283593",
        "aliases": [
            "Philippot",
            "Florian Philippot",
            "Philippot (LP)",
        ],
    },

    "thouy": {
        "name": "Hélène Thouy",
        "color": "#66BB6A",
        "aliases": [
            "Thouy",
            "Hélène Thouy",
            "Thouy (PA)",
        ],
    },

    "lagarde": {
        "name": "Jean-Christophe Lagarde",
        "color": "#64B5F6",
        "aliases": [
            "Lagarde",
            "Jean-Christophe Lagarde",
            "Lagarde (UDI)",
        ],
    },

    "poisson": {
        "name": "Jean-Frédéric Poisson",
        "color": "#455A64",
        "aliases": [
            "Poisson",
            "Jean-Frédéric Poisson",
            "Poisson (VIA)",
        ],
    },

    "cheminade": {
        "name": "Jacques Cheminade",
        "color": "#795548",
        "aliases": [
            "Cheminade",
            "Jacques Cheminade",
            "Cheminade (S&P)",
        ],
    },

    "lr_candidate": {
        "name": "Candidat LR",
        "color": "#1976D2",
        "aliases": [
            "Candidat LR",
            "Candidat LR/SL/DVD",
        ],
    },

    "ps_candidate": {
        "name": "Candidat PS/DVG",
        "color": "#EC407A",
        "aliases": [
            "Candidat PS/DVG",
        ],
    },
    "others": {
        "name": "Autres",
        "color": "#9E9E9E",
        "aliases": [
            "Autres",
        ],
    },
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
    alias.lower(): f'C_{cid}'
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