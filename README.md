# poll_tracker
Database gathering polls for the french presidential elections, with visualizations

Method: scrapping wikiepdia which contains table with polling data
Added value: consistent database (errors checking) + political trends
Challenges: different formatting of the page


Method: partir de la commission des sondages ou les liens sont stockés selon cette logique
https://www.commission-des-sondages.fr/notices/files/notices/2026/juin/10211-pres-iv-ifop-le-figaro-25-juin.pdf
-> Creer une table sondage_metadata à partir de la (scrapper just la structure des fichiers) :
sondage_id  |  election |   nom du sondage (pas normé) (essayer d'extraires des iformations)


-> Partir de la page wikipedia et parser les résultats, en retrouvant le sondage id dans le lien
-> Sauver le titre de la table dans la table comme une colonne de métadonnées

-> Candidates id (seulement les candidats qui se présente, les autres sont agrégés dans AUTRES — pour 2027, candidats préssentis), avec matching des formes
-> Faire un séparation sur (avec les titres sur la page):
    - premier tour
        Avant la liste des candidats
        Après
    - deuxième tour
        Après le premier tour
        Hypothèse 1, 2, ...

-> Parsing des dates

-> Mapping politiques avec les blocs et les candidats id

# TODO
# Hoovering (...)
# Events (...)
# 2027 —> Keep track of indicated precision to show in the UI (multiple sondages??) (...)
# Multiple second tour hyp TODO

# Resultats 1995, 1988 (?)
# Previous election (?) 1981, 1974, 1969, 1965
