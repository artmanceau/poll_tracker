INSTITUTES = {
    "resultats": {
        "id": 0,
        "name": "Résultats",
        "variations": ["Résultats", "Résultats officiels"],
    },
    "harris_interactive": {
        "id": 1,
        "name": "Harris Interactive",
        "variations": [
            "HARRIS INTERACTIVE",
            "HARRIS",
            "Harris Interractive",
            "Louis Harris",
            "Harris-Interactive",
            "Harris[g]",
        ],
    },
    "kantar": {
        "id": 15,
        "name": "Kantar",
        "variations": [
            "Kantar",
            "Sofres",
            "TNS Sofres",
            "Kantar Sofres - OnePoint",
            "Kantar Sofres-OnePointKantar\xa0Sofres - OnePoint",
            "Kantar Sofres-OnePoint",
            "Kantar Sofres",
        ],
    },
    "politico": {"id": 16, "name": "Politico", "variations": ["Atlas Politico"]},
    "opinionway": {
        "id": 2,
        "name": "OpinionWay",
        "variations": [
            "OPINIONWAY",
            "OPINION WAY",
        ],
    },
    "cluster17": {
        "id": 3,
        "name": "Cluster 17",
        "variations": ["CLUSTER17", "CLUSTER 17", "Cluster17[m]"],
    },
    "ifop": {
        "id": 4,
        "name": "IFOP",
        "variations": ["IFOP", "Ifop[2]", "Ifop[3]", "Ifop-Fiducial", "Ifop[f]"],
    },
    "elabe": {
        "id": 5,
        "name": "ELABE",
        "variations": [
            "ELABE",
        ],
    },
    "ipsos": {
        "id": 6,
        "name": "IPSOS",
        "variations": [
            "IPSOS",
            "Ipsos[1]",
            "Ispos",
            "Cevipof Ipsos Sopra Steria",
            "Cevipof Ipsos Sopra Steria",
            "Ipsos Sopra Steria",
            "«\xa0Ipsos\xa0»(Archive.org • Wikiwix • Google • Que faire\xa0?)",
            "Ipsos\xa0Sopra\xa0Steria",
            "Cevipof Ipsos-Sopra Steria",
        ],
    },
    "bva": {
        "id": 7,
        "name": "BVA",
        "variations": [
            "BVA",
        ],
    },
    "csa": {
        "id": 8,
        "name": "CSA",
        "variations": [
            "CSA",
        ],
    },
    "odoxa": {
        "id": 9,
        "name": "Odoxa",
        "variations": [
            "ODOXA",
        ],
    },
    "verian": {
        "id": 10,
        "name": "Verian",
        "variations": [
            "VERIAN",
        ],
    },
    "toluna": {
        "id": 11,
        "name": "Toluna",
        "variations": [
            "TOLUNA",
        ],
    },
    "yougov": {
        "id": 12,
        "name": "YouGov",
        "variations": [
            "YOUGOV",
        ],
    },
    "sagis": {
        "id": 13,
        "name": "Sagis",
        "variations": [
            "SAGIS",
        ],
    },
    "pige": {
        "id": 14,
        "name": "Pige",
        "variations": [
            "PIGE",
            "PIGÉ",
        ],
    },
    "lh2": {
        "id": 18,
        "name": "LH2",
        "variations": [
            "LH2",
        ],
    },
    "scan_research": {
        "id": 19,
        "name": "Scan Research",
        "variations": [
            "Scan Research - Le Terrain",
        ],
    },
    "dedicated_research": {
        "id": 19,
        "name": "Dedicated Research",
        "variations": [
            "Dedicated Research",
        ],
    },
    "future_thinking": {
        "id": 20,
        "name": "Future Thinking",
        "variations": [
            "Future Thinking - SSI",
        ],
    },
}

INSTITUTE_LOOKUP = {
    variation.upper(): data["name"]
    for data in INSTITUTES.values()
    for variation in data["variations"]
}
