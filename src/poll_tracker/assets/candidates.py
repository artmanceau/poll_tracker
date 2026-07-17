import polars as pl

candidates = {
    "abstention":{
        'name': 'Abstention',
        'color':'#F00000',
        'aliases': [
            'Abstention #',
            'Abstention, blanc ou nul',
            'Abstention'
        ]
    },
   "arthaud": {
        "name": "Nathalie Arthaud",
        "color": "#8B0000",  # Dark red
        "aliases": [
            "Arthaud",
            "Arthaud (LO)",
            "Nathalie Arthaud (LO)"
        ]
    },
    "laguiller": {
        "name": "Arlette Laguiller",
        "color": "#8B0000",  # Dark red
        "aliases": [
            "Arlette Laguiller (LO)",
            "Laguiller",
            "Laguiller (LO)",
            "Arlette Laguiller[N 1] (LO)"
        ],
    },
    "besancenot": {
        "name": "Olivier Besancenot",
        "color": "#B22222",  # Red
        "aliases": [
            "Olivier Besancenot (LCR)",
            "Besancenot",
            "Besancenot (LCR)",
            "Olivier Besancenot (NPA)"
        ],
    },
    "buffet": {
        "name": "Marie-George Buffet",
        "color": "#C00000",  # PCF red
        "aliases": [
            "Marie-George Buffet (PCF)",
            "Buffet",
            "Buffet (PCF)",
        ],
    },
    "schivardi": {
        "name": "Gérard Schivardi",
        "color": "#A52A2A",  # Brown-red
        "aliases": [
            "Gérard Schivardi (PT)",
            "Schivardi",
            "Schivardi (PT)",
        ],
    },
    "royal": {
        "name": "Ségolène Royal",
        "color": "#E91E63",  # Pink/red (PS)
        "aliases": [
            "Ségolène Royal (PS)",
            "Royal",
            "Royal (PS)",
            "Ségolène Royal[N 1] (PS)",
            "Ségolène Royal",
            "Ségolène Royal",
        ],
    },
    "bove": {
        "name": "José Bové",
        "color": "#2E8B57",  # Green-ish left
        "aliases": [
            "José Bové (DVG)",
            "Bové",
            "Bové (DVG)",
            "José Bové (SÉ)"
        ],
    },
    "voynet": {
        "name": "Dominique Voynet",
        "color": "#228B22",  # Green
        "aliases": [
            "Dominique Voynet (LV)",
            "Voynet",
            "Voynet (LV)",
            "Dominique Voynet[N 1] (EELV)",
            "Dominique Voynet (Verts)"
            "Dominique Voynet[N 1] (EELV)",
            'Dominique Voynet[N 1] (EELV)'
        ],
    },
    "bayrou": {
        "name": "François Bayrou",
        "color": "#FF8C00",  # Orange (UDF)
        "aliases": [
            "François Bayrou (UDF)",
            "Bayrou",
            "Bayrou (UDF)",
            "François Bayrou (MoDem)"
        ],
    },
    "sarkozy": {
        "name": "Nicolas Sarkozy",
        "color": "#1E3A8A",  # Blue (right)
        "aliases": [
            "Nicolas Sarkozy",
            "Sarkozy",
            "Nicolas Sarkozy (LR)"
        ],
    },
    "cope": {
        "name": "Jean-François Copé",
        "color": "#4169E1",  # UMP/LR blue
        "aliases": [
            "Jean-François Copé (UMP)",
            "Jean-Francois Cope (UMP)",
            "Jean-François Copé",
            "Copé",
        ],
    },
    "duflot": {
        "name": "Cécile Duflot",
        "color": "#228B22",  # EELV green
        "aliases": [
            "Cécile Duflot (EELV)",
            "Cecile Duflot (EELV)",
            "Cécile Duflot",
            "Duflot",
        ],
    },
    "le_maire": {
        "name": "Bruno Le Maire",
        "color": "#4169E1",
        "aliases": [
            "Bruno Le Maire (LR)",
            "Bruno Le Maire",
            "Le Maire",
        ],
    },
    "juppe": {
        "name": "Alain Juppé",
        "color": "#4169E1",
        "aliases": [
            "Alain Juppé (LR)",
            "Alain Juppe (LR)",
            "Alain Juppé",
            "Juppé",
            'Alain Juppé (UMP)'
        ],
    },
    "montebourg": {
        "name": "Arnaud Montebourg",
        "color": "#E91E63",  # PS
        "aliases": [
            "Arnaud Montebourg (PS)",
            "Arnaud Montebourg",
            "Montebourg",
            'Arnaud Montebourg (PS)'
        ],
    },
    "peillon": {
        "name": "Vincent Peillon",
        "color": "#E91E63",  # PS
        "aliases": [
            "Vincent Peillon (PS)",
            "Vincent Peillon",
            "Peillon",
        ],
    },
    "valls": {
        "name": "Manuel Valls",
        "color": "#E91E63",  # PS
        "aliases": [
            "Manuel Valls (PS)",
            "Manuel Valls",
            "Valls",
        ],
    },
    "hamon": {
        "name": "Benoît Hamon",
        "color": "#E91E63",  # PS
        "aliases": [
            "Benoît Hamon (PS)",
            "Benoit Hamon (PS)",
            "Benoît Hamon",
            "Hamon",
        ],
    },
    "de_villiers": {
        "name": "Philippe de Villiers",
        "color": "#4169E1",  # Blue
        "aliases": [
            "Philippe de Villiers (MPF)",
            "de Villiers",
            "de Villiers (MPF)",
        ],
    },
    "nihous": {
        "name": "Frédéric Nihous",
        "color": "#6B8E23",  # Olive green
        "aliases": [
            "Frédéric Nihous (CPNT)",
            "Nihous",
            "Nihous (CPNT)",
        ],
    },
    "hուլot": {
        "name": "Nicolas Hulot",
        "color": "#32CD32",  # Light green
        "aliases": [
            "Nicolas Hulot",
            "Nicolas Hulo",
            "Hulot",
        ],
    },
    "poutou": {
        "name": "Philippe Poutou",
        "color": "#C62828",  # Red
        "aliases": [
            "Poutou",
            "Poutou (NPA)",
            "Philippe Poutou (NPA)",
            "Poutou[e] (NPA-A)"
        ]
    },
    "melenchon": {
        "name": "Jean-Luc Mélenchon",
        "color": "#E53935",  # Bright left red
        "aliases": [
            "Mélenchon",
            "Mélenchon (LFI)",
            "Mélenchon (FG)",
            "Jean-Luc Mélenchon (LFI)",
            "Jean-Luc Mélenchon (FG)",
            "Mélenchon[c] (LFI)"
        ]
    },
    "chevenement": {
        "name": "Jean-Pierre Chevènement",
        "color": "#E91E63",
        "aliases": [
            "Jean-Pierre Chevènement (MRC)",
            "Jean-Pierre Chevènement (MDC)",
            "Chevènement",
        ],
    },
    "morin": {
        "name": "Hervé Morin",
        "color": "#FF8C00",
        "aliases": [
            "Hervé Morin (NC)",
            "Hervé Morin",
            "Morin",
        ],
    },
    "villepin": {
        "name": "Dominique de Villepin",
        "color": "#4169E1",
        "aliases": [
            "Dominique de Villepin (RS)",
            "Dominique de Villepin (LFH)",
            "Dominique de Villepin",
            "Villepin",
             "Villepin (LFH)"
        ],
    },
    "wauquiez": {
        "name": "Laurent Wauquiez",
        "color": "#4169E1",  # LR blue
        "aliases": [
            "Wauquiez (LR)",
            "Wauquiez[b] (LR)",
            "Wauquiez[c] (LR)",
            "Laurent Wauquiez (LR)",
        ],
    },
    "lepage": {
        "name": "Corinne Lepage",
        "color": "#2E8B57",
        "aliases": [
            "Corinne Lepage (Cap21)",
            "Corinne Lepage",
            "Lepage",
        ],
    },
    "boutin": {
        "name": "Christine Boutin",
        "color": "#4169E1",
        "aliases": [
            "Christine Boutin (PCD)",
            "Christine Boutin (FRS)",
            "Christine Boutin",
            "Boutin",
        ],
    },
    "candidat_npa": {
        "name": "Candidat NPA",
        "color": "#B22222",
        "aliases": ["Candidat NPA"],
    },
    "candidat_ps": {
        "name": "Candidat PS",
        "color": "#E91E63",
        "aliases": ["Candidat PS"],
    },
    "borloo": {
        "name": "Jean-Louis Borloo",
        "color": "#FF8C00",
        "aliases": [
            "Jean-Louis Borloo (PR)",
            "Jean-Louis Borloo",
            "Borloo",
        ],
    },
    "candidat_eelv": {
        "name": "Candidat EELV",
        "color": "#228B22",
        "aliases": ["Candidat EELV"],
    },
    "joly": {
        "name": "Eva Joly",
        "color": "#228B22",
        "aliases": [
            "Eva Joly (EELV)",
            "Eva Joly[N 1] (EELV)",
            "Eva Joly",
            "Joly",
        ],
    },
    "aubry": {
        "name": "Martine Aubry",
        "color": "#E91E63",
        "aliases": [
            "Martine Aubry[N 1] (PS)",
            "Martine Aubry (PS)",
            "Martine Aubry",
            "Aubry",
        ],
    },
    "tapie": {
        "name": "Bernard Tapie",
        "color": "#FF8C00",
        "aliases": [
            "Bernard Tapie (PRG)",
            "Bernard Tapie",
            "Tapie",
        ],
    },
    "faure": {
        "name": "Olivier Faure",
        "color": "#E91E63",  # PS
        "aliases": [
            "Faure[c] (PS)",
            "Faure[b] (PS)",
            "Faure (PS)",
            "Olivier Faure (PS)",
        ],
    },
    "tondelier": {
        "name": "Marine Tondelier",
        "color": "#228B22",  # Ecologist green
        "aliases": [
            "Tondelier[c] (LE)",
            "Tondelier[c] (LÉ)",
            "Tondelier[b] (LÉ)",
            "Tondelier (LE)",
            "Marine Tondelier (LE)",
        ],
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
            "Anne Hidalgo (PS)",
            'Hidalgo[N 5] (PS)'
        ]
    },
    "glucksmann": {
        "name": "Raphaël Glucksmann",
        "color": "#FED92D",  # Socialist pink
        "aliases": [
            'Glucksmann (PP)',
        ]
    },
    "jadot": {
        "name": "Yannick Jadot",
        "color": "#43A047",  # Green
        "aliases": [
            "Jadot",
            "Jadot (EÉLV)",
            "Jadot (EELV)",
            "Yannick Jadot (EELV)",
            'Jadot[N 5] (EELV)'

        ]
    },
    "macron": {
        "name": "Emmanuel Macron",
        "color": "#FBC02D",  # Yellow
        "aliases": [
            "Macron",
            "Macron (LREM)",
            "Macron (EM)",
            "Emmanuel Macron",
            "Emmanuel Macron (SE)",
            "Emmanuel Macron (DVG)",
            'Emmanuel Macron (EM)'
        ]
    },
    "attal": {
        "name": "Gabriel Attal",
        "color": "#FBC02D",  # Yellow
        "aliases": [
            'Attal (RE)',
        ]
    },
    "philippe": {
        "name": "Edouard Philippe",
        "color": "#1E88E5",
        "aliases": [
           'Philippe (HOR)'
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
    "retailleau": {
        "name": "Bruno Retailleau",
        "color": "#1E88E5",  # Centre-right blue
        "aliases": [
            'Retailleau (LR)'
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
            "Nicolas Dupont-Aignan (DLF)",
            "Nicolas Dupont-Aignan (DLR)"
        ]
    },
    "mamere": {
        "name": "Noël Mamère",
        "color": "#43A047",  # Green
        "aliases": [
            "Noël Mamère (LV)"
        ]
    },
    "fabius": {
        "name": "Laurent Fabius",
        "color": "#E91E63",  # PS pink/red
        "aliases": [
            "Laurent Fabius (PS)",
            "Laurent Fabius",
            "Fabius",
            "Fabius (PS)",
        ],
    },
    "lang": {
        "name": "Jack Lang",
        "color": "#E91E63",  # PS pink/red
        "aliases": [
            "Jack Lang (PS)",
            "Jack Lang",
            "Lang",
            "Lang (PS)",
        ],
    },
    "jm_le_pen": {
        "name": 'Jean-Marie Le Pen',
        "color": "#0D47A1",  # Navy blue
        "aliases": [
            "Jean-Marie Le Pen (FN)"
        ]
    },
    'bardella': {
        "name": 'Jordan Bardella',
        "color": "#0D47A1",  # Navy blue
        "aliases": [
            'Bardella (RN)'
        ]
    },
    "m_le_pen": {
        "name": "Marine Le Pen",
        "color": "#0D47A1",  # Navy blue
        "aliases": [
            "Le Pen",
            "Le Pen (RN)",
            "Le Pen (FN)",
            "Marine Le Pen (RN)",
            "Marine Le Pen (FN)",
            "Le Pen[c] (RN)"
            "Marine Le Pen",
            "Le Pen[c] (RN)",
            "Marine Le Pen"
        ]
    },
    "zemmour": {
        "name": "Éric Zemmour",
        "color": "#212121",  # Almost black
        "aliases": [
            "Zemmour",
            "Zemmour (REC)",
            "Éric Zemmour (REC)",
            "Zemmour[c] (REC)",
            'Zemmour (EXD)'
        ]
    },
    "fillon": {
        "name": "François Fillon",
        "color": "#1976D2",  # LR blue
        "aliases": [
            "Fillon",
            "Fillon (LR)",
            "François Fillon (LR)",
            "François Fillon[N 3] (LR)",
            "François Fillon (UMP)"
        ]
    },
    "hollande": {
        "name": "François Hollande",
        "color": "#EC407A",  # PS pink
        "aliases": [
            "Hollande",
            "François Hollande (PS)",
            "François Hollande"
        ]
    },
    "sarkozy": {
        "name": "Nicolas Sarkozy",
        "color": "#1565C0",  # UMP blue
        "aliases": [
            "Sarkozy",
            "Nicolas Sarkozy (UMP)",
            "Nicolas Sarkozy",
            'Nicolas Sarkozy (LR)'
        ]
    },
    "chirac": {
        "name": "Jacques Chirac",
        "color": "#0D47A1",  # Gaullist navy
        "aliases": [
            "Chirac",
            "Jacques Chirac (RPR)",
            "Jacques Chirac"
        ]
    },
    "lajoinie": {
        "name": "André Lajoinie",
        "color": "#C00000",  # PCF red
        "aliases": [
            "André Lajoinie (PCF)",
            "Lajoinie",
            "Lajoinie (PCF)",
        ],
    },
    "juquin": {
        "name": "Pierre Juquin",
        "color": "#E91E63",
        "aliases": [
            "Pierre Juquin (DVG)",
            "Pierre Juquin",
            "Juquin",
        ],
    },
    "rocard": {
        "name": "Michel Rocard",
        "color": "#E91E63",  # PS
        "aliases": [
            "Michel Rocard (PS)",
            "Michel Rocard",
            "Rocard",
        ],
    },
    "waechter": {
        "name": "Antoine Waechter",
        "color": "#228B22",  # Green
        "aliases": [
            "Antoine Waechter (LV)",
            "Antoine Waechter",
            "Waechter",
        ],
    },
    "barre": {
        "name": "Raymond Barre",
        "color": "#FF8C00",
        "aliases": [
            "Raymond Barre (UDF)",
            "Raymond Barre",
            "Barre",
        ],
    },
    "giscard_d_estaing": {
        "name": "Valéry Giscard d'Estaing",
        "color": "#FF8C00",
        "aliases": [
            "Valéry Giscard d'Estaing (UDF)",
            "Valéry Giscard d'Estaing",
            "Giscard d'Estaing",
            "Giscard",
        ],
    },
    "leotard": {
        "name": "François Léotard",
        "color": "#FF8C00",
        "aliases": [
            "François Léotard (UDF)",
            "François Léotard",
            "Léotard",
        ]
    },
    "mitterrand": {
        "name": "François Mitterrand",
        "color": "#C2185B",  # Historic PS magenta
        "aliases": [
            "Mitterrand",
            "François Mitterrand (PS)",
            "François Mitterrand"
        ]
    },
    "taubira": {
        "name": "Christiane Taubira",
        "color": "#AD1457",
        "aliases": [
            "Taubira",
            "Christiane Taubira",
            "Taubira (DVG)",
            "Christiane Taubira (PRG)"
        ],
    },
    "megret": {
        "name": "Bruno Mégret",
        "color": "#000080",  # nationalist right (navy)
        "aliases": [
            "Bruno Mégret (MNR)",
            "Bruno Mégret",
            "Megret",
            "Mégret",
        ],
    },
    "gluckstein": {
        "name": "Daniel Gluckstein",
        "color": "#B22222",  # far-left red
        "aliases": [
            "Daniel Gluckstein (POI)",
            "Daniel Gluckstein",
            "Gluckstein",
            "Gluckstein (POI)",
        ],
    },
    "pasqua": {
        "name": "Charles Pasqua",
        "color": "#4169E1",  # right/gaullist blue
        "aliases": [
            "Charles Pasqua (RPF)",
            "Charles Pasqua",
            "Pasqua",
        ],
    },
    "madelin": {
        "name": "Alain Madelin",
        "color": "#4169E1",  # liberal/center-right blue
        "aliases": [
            "Alain Madelin (DL)",
            "Alain Madelin",
            "Madelin",
            "Madelin (DL)",
        ],
    },
    "saint_josse": {
        "name": "Jean Saint-Josse",
        "color": "#6B8E23",  # CPNT olive green
        "aliases": [
            "Jean Saint-Josse (CPNT)",
            "Jean Saint-Josse",
            "Saint-Josse",
            "Saint Josse",
            "Saint-Josse (CPNT)",
        ],
    },
    "candidat_ps_pp": {
        'name': 'Candidat PS/Place Publique',
        "color":"#AD1457",
        'aliases': [
            "Candidat PS / PP"
        ]
    },
    'candidat_ens': {
        'name':"Candidat ENS",
        'color': "#FBC02D",  # Yellow
        "aliases":[
            "Candidat ENS", 
            "Candidat ENS.1",
            "Candidat EPR", 
            "Candidat EPR.1"
        ]
    },
    "montebourg": {
        "name": "Arnaud Montebourg",
        "color": "#C2185B",
        "aliases": [
            "Montebourg",
            "Arnaud Montebourg",
            "Montebourg (DVG)",
            'Arnaud Montebourg (PS)'
        ],
    },
    "asselineau": {
        "name": "François Asselineau",
        "color": "#5C6BC0",
        "aliases": [
            "Asselineau",
            "François Asselineau",
            "Asselineau (UPR)",
            "François Asselineau (UPR)"
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
            "Jacques Cheminade (S&P)",
            "Jacques Cheminade (FNS)",
            "Jacques Cheminade (SP)"
        ],
    },
     "hue": {
        "name": "Robert Hue",
        "color": "#C00000",  # PCF red
        "aliases": [
            "Robert Hue (PCF)",
            "Robert Hue",
            "Hue",
        ],
    },
    'pinel': {
        'name': 'Sylvia Pinel',
        'color':'#F00000',
        'aliases':[
            'Sylvia Pinel (PRG)'
        ]
    },
    "jospin": {
        "name": "Lionel Jospin",
        "color": "#E91E63",  # PS
        "aliases": [
            "Lionel Jospin (PS)",
            "Lionel Jospin",
            "Jospin",
        ],
    },
    "voynet": {
        "name": "Dominique Voynet",
        "color": "#228B22",  # Green
        "aliases": [
            "Dominique Voynet (Verts)",
            "Dominique Voynet (LV)",
            "Dominique Voynet",
            "Voynet",
        ],
    },
    "balladur": {
        "name": "Édouard Balladur",
        "color": "#4169E1",  # RPR/LR blue
        "aliases": [
            "Édouard Balladur (RPR)",
            "Edouard Balladur (RPR)",
            "Édouard Balladur",
            "Balladur",
        ],
    },
    "rn_candidate": {
        "name": "Candidat RN",
        "color": "#0D47A1",  # Navy blue
        "aliases": [
            "Candidat RN"
        ]
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
            'Autres candidats',
        ],
    },
    'indecis': {
        'name': 'Indécis',
        'color':'#F00000',
        'aliases':[
            'Indécis (échantillon)',
            'Indécis'
        ]
    }
}

election_candidates = {
    "2027": [
        "candidat_ps_pp",
        'poutou',
        "melenchon",
        "tondelier",
        "faure",
        "candidat_ens",
        "lr_candidate",
        "dupont_aignan",
        "rn_candidate",
        "zemmour",
        "villepin",
        "wauquiez",
        "arthaud",
        "others"
    ],
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
        "m_le_pen",
        "zemmour"
    ],
    "2017": [
        "arthaud",
        "poutou",
        "melenchon",
        "macron",
        "hamon",
        "cheminade",
        "lassalle",
        "fillon",
        "dupont_aignan",
        "m_le_pen"
    ],
    "2012": [
        "arthaud",
        "poutou",
        "melenchon",
        "hollande",
        "joly",
        "sarkozy",
        "dupont_aignan",
        "m_le_pen"
    ],
    "2007": [
          "laguiller",
          "besancenot",
          "buffet",
          "schivardi",
          "royal",
          "bove",
          "voynet",
          "bayrou",
          "nihous",
          "sarkozy",
          "de_villiers",
          "jm_le_pen"
    ],
    "2002": [
          "laguiller",
          "besancenot",
          "gluckstein",
          "hue",
          "jospin",
          "mamere",
          "taubira",
          "chevenement",
          "bayrou",
          "chirac",
          "madelin",
          "boutin",
          "saint_josse",
          "lepage",
          "megret",
          "jm_le_pen"
    ],
    "1995": [
          "laguiller",
          "hue",
          "jospin",
          "voynet",
          "chirac",
          "balladur",
          "de_villiers",
          "jm_le_pen",
          "cheminade"
      ],
      "1988": [
          "laguiller",
          "juquin",
          "lajoinie",
          "mitterrand",
          "waechter",
          "barre",
          "chirac",
          "jm_le_pen"
      ],
      "1981": [
          "bouchardeau",
          "laguiller",
          "marchais",
          "mitterrand",
          "crepeau",
          "lalonde",
          "giscard_destaing",
          "chirac",
          "debre",
          "garaud"
      ],
      "1974": [
          "krivine",
          "laguiller",
          "dumont",
          "mitterrand",
          "muller",
          "giscard_destaing",
          "chaban_delmas",
          "royer",
          "jm_le_pen",
          "renouvin",
          "sebag",
          "heraud"
      ],
      "1969": [
          "krivine",
          "duclos",
          "defferre",
          "rocard",
          "poher",
          "pompidou",
          "ducatel"
      ],
      "1965": [
          "barbu",
          "mitterrand",
          "marcilhacy",
          "de_gaulle",
          "lecanuet",
          "tixier_vignancour"
      ]
}

second_round = {
    "2027": ["attal", "bardella"],
    "2022": ["macron", "m_le_pen"],
    "2017": ["macron", "m_le_pen"],
    "2012": ["hollande", "sarkozy"],
    "2007": ["sarkozy", "royal"],
    "2002": ["chirac", "jm_le_pen"],
    "1995": ["chirac", "jospin"],
    "1988": ["mitterrand", "chirac"],
    "1981": ["mitterrand", "giscard_destaing"],
    "1974": ["giscard_destaing", "mitterrand"],
    "1969": ["pompidou", "poher"],
    "1965": ["de_gaulle", "mitterrand"]
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