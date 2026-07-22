blocs = {
    "2027": {
        "G": ["arthaud", "poutou", "melenchon", "roussel"],
        "CG": [
            "tondelier",
            "candidat_ps_pp",
            "faure",
            "candidat_eelv",
        ],
        "C": ["candidat_ens"],
        "CD": ["lr_candidate", "wauquiez"],
        "D": ["villepin", "dupont_aignan", "rn_candidate", "zemmour", "m_le_pen"],
    },
    "2022": {
        "G": ["arthaud", "poutou", "roussel", "melenchon"],
        "CG": ["hidalgo", "jadot"],
        "C": ["macron"],
        "CD": ["pecresse"],
        "D": ["dupont_aignan", "m_le_pen", "zemmour"],
    },
    "2017": {
        "G": ["arthaud", "poutou", "melenchon"],
        "CG": ["hamon"],
        "C": ["macron"],
        "CD": ["fillon"],
        "D": ["dupont_aignan", "m_le_pen", "asselineau"],
    },
    "2012": {
        "G": ["arthaud", "poutou", "melenchon"],
        "CG": ["hollande", "joly"],
        "C": ["bayrou"],
        "CD": ["sarkozy"],
        "D": ["dupont_aignan", "m_le_pen"],
    },
    "2007": {
        "G": ["laguiller", "besancenot", "buffet", "schivardi"],
        "CG": ["royal", "bove", "voynet"],
        "C": ["bayrou"],
        "CD": ["sarkozy"],
        "D": ["de_villiers", "jm_le_pen"],
    },
    "2002": {
        "G": ["laguiller", "gluckstein", "besancenot", "hue"],
        "CG": ["jospin", "taubira", "mamere", "chevenement", "lepage"],
        "C": ["bayrou"],
        "CD": ["boutin", "chirac", "madelin"],
        "D": ["saint_josse", "jm_le_pen", "megret"],
    },
    "1995": {
        "G": ["laguiller", "hue"],
        "CG": ["jospin", "voynet"],
        "C": ["balladur"],
        "CD": ["chirac"],
        "D": ["de_villiers", "jm_le_pen"],
    },
    "1988": {
        "G": ["laguiller", "lajoinie"],
        "CG": ["juquin", "mitterrand", "rocard", "waechter"],
        "C": ["barre"],
        "CD": ["giscard_d_estaing", "leotard", "chirac"],
        "D": ["jm_le_pen"],
    },
}

BLOC_COLORS = {
    # Level 1
    "G": "#E53935",      # Red
    "CG": "#E91E63",    #  Centre-left
    "C": "#FBC02D",      # Yellow
    "CD": "#1976D2",     # Blue / Centre-right
    "D": "#0D47A1",      # Dark blue

    # Level 2
    "GCG": "#E91E63",   # Red (Left coalition)
    "C": "#FBC02D", 
    "DCD": "#1565C0",    # Medium-dark blue (Right coalition)

    # Level 3
    "TG":"#E91E63",   # Dark green (Entire left)
    "TD": "#1976D2",          # Navy (Entire right)
}


BLOC_NAME = {
    'TD': 'Toutes les forces politiques de droite',
    'TG': 'Toutes les forces politiques de gauche',
    'D' : 'Extrême droite',
    'CD': 'Droite',
    'C': 'Centre',
    'CG' : "Gauche",
    'G': 'Extrême gauche',
    'GCG' : 'Bloc de gauche',
    'DCD' : 'Bloc de droite',
    'C' : 'Bloc centriste'
}

blocs_level_1 = ["G", "CG", "CD", "C", "D"]
blocs_level_1_str = [BLOC_NAME[bloc] for bloc in blocs_level_1]
blocs_level_2 = ["GCG", "DCD", "C"]
blocs_level_2_str = [BLOC_NAME[bloc] for bloc in blocs_level_2]
blocs_level_3 = ["TG", "TD"]
blocs_level_3_str = [BLOC_NAME[bloc] for bloc in blocs_level_3]

bloc_level_mapping = {
    str(blocs_level_1_str): blocs_level_1,
    str(blocs_level_2_str): blocs_level_2,
    str(blocs_level_3_str): blocs_level_3
}
