# Asset for scraping

links = {
    "2027": "https://fr.wikipedia.org/wiki/Liste_de_sondages_sur_l%27%C3%A9lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_2027",
    "2022": "https://fr.wikipedia.org/wiki/Liste_de_sondages_sur_l%27%C3%A9lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_2022",
    "2017": "https://fr.wikipedia.org/wiki/Liste_de_sondages_sur_l%27%C3%A9lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_2017",
    "2012": "https://fr.wikipedia.org/wiki/Liste_de_sondages_sur_l%27%C3%A9lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_2012",
    "2007": "https://fr.wikipedia.org/wiki/Liste_de_sondages_sur_l%27%C3%A9lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_2007",
    "2002": "https://fr.wikipedia.org/wiki/Liste_de_sondages_sur_l%27%C3%A9lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_2002",
    "1995": "https://fr.wikipedia.org/wiki/%C3%89lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_1995",
    "1988": "https://fr.wikipedia.org/wiki/%C3%89lection_pr%C3%A9sidentielle_fran%C3%A7aise_de_1988",
}

table_selector = {
    "2027": {
        "tour 1": {
            "start": "Année 2025",
            "end": "Année 2023",
        },
        "tour 2": {
            "start": "Hypothèse Attal – Bardella",
            "end": None,
        },
    },
    "2022": {
        "tour 1": {
            "start": "Sondages réalisés après la publication de la liste officielle des candidats",
            "end": "Années 2017-2020",
        },
        "tour 2": {
            "start": "Sondages effectués après le premier tour",
            "end": "Sondages effectués avant le premier tour",
        },
    },
    "2017": {
        "tour 1": {
            "start": "Sondages réalisés après la publication de la liste officielle des candidats",
            "end": "Sondages de 2013",
        },
        "tour 2": {
            "start": "Intentions de vote",
            "end": "Sondages entre Emmanuel Macron et Marine Le Pen",
        },
    },
    "2012": {
        "tour 1": {"start": "Avril 2012", "end": "Années 2007-2009"},
        "tour 2": {"start": "2012", "end": "2011"},
    },
    "2007": {
        "tour 1": {"start": "Avril", "end": "2005"},
        "tour 2": {"start": "2007", "end": "2006 (2)"},
    },
    "2002": {
        "tour 1": {"start": "Avril", "end": "1999"},
        "tour 2": {"start": "Chirac - Le Pen", "end": "Chirac - Le Pen"},
    },
    "1995": {
        "tour 1": {"start": 'Élection présidentielle française de 1995 (2)', "end": 'Élection présidentielle française de 1995 (2)'},
        "tour 2": {"start": 'Balladur - Jospin', "end": 'Balladur - Jospin'},
    },
    "1988": {
        "tour 1": {
            "start": "Élection présidentielle française de 1988 (2)",
            "end": "Élection présidentielle française de 1988 (2)",
        },
        "tour 2": {"start": 'Sondages concernant le premier tour', "end": 'Sondages concernant le premier tour'},
    },
}
