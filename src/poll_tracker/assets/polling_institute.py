INSTITUTES = {
    "resultats": {
        "id": 0,
        "name": "Résultats",
        "variations": [
            "Résultats",
            "Résultats officiels"
        ],
    },
    "harris_interactive": {
        "id": 1,
        "name": "Harris Interactive",
        "variations": [
            "HARRIS INTERACTIVE",
            "HARRIS",
            "Harris Interractive"
        ],
    },
    "kantar": {
        'id': 15,
        'name': 'Kantar',
        "variations": [
            'Kantar'
        ]
    },
    'politico':{
        'id': 16,
        'name': 'Politico',
        'variations': [
            'Atlas Politico'
        ]
    },
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
        "variations": [
            "CLUSTER17",
            "CLUSTER 17",
        ],
    },
    "ifop": {
        "id": 4,
        "name": "IFOP",
        "variations": [
            "IFOP",
        ],
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
}

INSTITUTE_LOOKUP = {
    variation.upper(): data["name"]
    for data in INSTITUTES.values()
    for variation in data["variations"]
}