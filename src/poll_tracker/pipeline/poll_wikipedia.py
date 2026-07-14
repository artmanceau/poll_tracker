import os
import re
from datetime import date
from io import StringIO

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

from poll_tracker.utils.data_loader import DataLoader, DataUtils

from poll_tracker.assets.bloc_mapping import * 
from poll_tracker.assets.candidates import *
from poll_tracker.assets.date_utils import FRENCH_MONTHS
from poll_tracker.assets.scrapping_asset import *
from poll_tracker.core.poll_fetcher import PollFetcher

# Method: scrapping wikiepdia which contains table with polling data
# Added value: consistent database (errors checking) + political trends
# Challenges: different formatting of the page

# Nice to have : source des sondages

YEARS = ["2022", "2007", "2012", "2017", "2022", "2027"]  # , "1988"]  Bug with 1988

data_path = "s3://arthurmanceau/election_modeling_uhcp/data/polls/"
# data_path = "data/polls/"

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
            "element1": "Hypothèse Attal – Bardella",
            "element2": None,
        },
    },
    "2022": {
        "tour 1": {
            "start": "Sondages réalisés après la publication de la liste officielle des candidats",
            "end": "Années 2017-2020",
        },
        "tour 2": {
            "element1": "Sondages effectués après le premier tour",
            "element2": "Sondages effectués avant le premier tour",
        },
    },
    "2017": {
        "tour 1": {
            "start": "Sondages réalisés après la publication de la liste officielle des candidats",
            "end": "Sondages de 2013",
        },
        "tour 2": {
            "element1": "Intentions de vote",
            "element2": "Sondages entre Emmanuel Macron et Marine Le Pen",
        },
    },
    "2012": {
        "tour 1": {"start": "Avril 2012", "end": "Années 2007-2009"},
        "tour 2": {"element1": "2012", "element2": "2011"},
    },
    "2007": {
        "tour 1": {"start": "Avril", "end": "2005"},
        "tour 2": {"element1": "2007", "element2": "2006 (2)"},
    },
    "2002": {
        "tour 1": {"start": "Avril", "end": "1999"},
        "tour 2": {"element1": "Chirac - Le Pen", "element2": None},
    },
    "1995": {
        "tour 1": {"start": "En 1995", "end": "En 1995"},
        "tour 2": {"element1": "Balladur - Chirac", "element2": None},
    },
    "1988": {
        "tour 1": {
            "start": "Sondages concernant le premier tour (2)",
            "end": "Sondages concernant le premier tour (2)",
        },
        "tour 2": {"element1": "Mitterrand - Chirac", "element2": None},
    },
}

# Implement through real CLI
if __name__ == "__main__":

    # Load class
    fetcher = PollFetcher()

    # Load config

    for year in YEARS:
        datasets = fetcher.fetch_polls(year)

        fetcher.save_s3(datasets, year)
