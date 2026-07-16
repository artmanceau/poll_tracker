import streamlit as st
import s3fs
import polars as pl
from plots import (
    poll_evolution_plot,
)
from poll_tracker.assets.candidates import candidates, election_candidates, second_round
from poll_tracker.assets.bloc_mapping import blocs_level_1, blocs_level_2, blocs_level_3
import polars
import pyarrow
import pandas
import numpy
import statsmodels
import streamlit

print(polars.__version__)
print(pyarrow.__version__)
print(pandas.__version__)
print(numpy.__version__)
print(statsmodels.__version__)
print(streamlit.__version__)

storage_options = {
    "profile": "default",
}

# TODO
# Segmentation faukt
# Clickable link
# Colors fix
# {name}

fs = s3fs.S3FileSystem(
    profile="default",
    endpoint_url="https://minio.lab.sspcloud.fr",
    client_kwargs={
        "region_name": "us-east-1",
    },
)


@st.cache_data
def load_poll_data(
    year,
    election_type,
    tour
):
    data = (
        pl.read_parquet(
            f"s3://arthurmanceau/poll_tracker/data/polls/{election_type}/{year}/{tour}/polls.parquet",
            storage_options=storage_options,
        )
    )
    return data

st.set_page_config(
    page_title="Sondages",
    layout="wide",
)

st.header(
    "Evolution des sondages"
)

CODE_TOUR = {'Premier tour': 't1', 'Second tour': 't2'}
CODE_ELECTION = {"Élections présidentielles": 'presidentiel'}

year = st.selectbox('Année', options=[2022])

election_type = st.selectbox('Type d\'élection', options=["Élections présidentielles"])

tour = st.selectbox('Tour', options=['Premier tour', 'Second tour'])

data = load_poll_data(year, CODE_ELECTION[election_type], CODE_TOUR[tour])
official, polls = data.filter(pl.col('source') == "Résultats"), polldatas.filter(pl.col('source')!="Résultats")

col1, col2 = st.columns([1, 4], gap="small")

with col1:
    sources = (
        polls["source"]
        .unique()
        .sort()
        .to_list()
    )
    sondeur = st.multiselect('source', sources, default=sources)
    min_echantillon, max_echantillon = st.slider("Taille de l'échantillon", polls.get_column('sample_size').min(), polls.get_column('sample_size').max(), (polls.get_column('sample_size').min(), polls.get_column('sample_size').max()))
    min_date, max_date = st.slider("Date du sondage",  polls.get_column('end_date').min(), polls.get_column('end_date').max(), (polls.select(pl.col('end_date').max().dt.offset_by("-6mo")).get_column('end_date')[0], polls.get_column('end_date').max()))
    mode = st.selectbox('Mode', options=['Candidats', 'Blocs politiques'])
    if (mode == 'Candidats') and (tour ==  'Premier tour'):
        remove_below_5 = st.checkbox('Retirer les candidats avec moins de 5%', value=True)
        remove_candidate_that_didnt_run = st.checkbox('Retirer les candidats qui ne se sont pas présenté officiellement', value=True)
        if remove_candidate_that_didnt_run:
            items = [f'C_{candidate}_processed' for candidate in election_candidates[str(year)]]
        else:
            items = list(set([f'C_{candidate}_processed' for candidate in candidates.keys()]).intersection(set(polls.columns)))
    else:
        items = [f'C_{candidate}_processed' for candidate in second_round[str(year)]]

        if remove_below_5:
            cand = items
            items = official.select(cand).transpose(
                include_header=True,
                header_name="candidate",
            ).filter(
                pl.col("column_0") > 5
            ).get_column("candidate")
    
    if mode == 'Blocs politiques':
        blocs = st.radio('Division', options=[blocs_level_1, blocs_level_2, blocs_level_3])
        items = [f'BP_{b}' for b in blocs]

with col2:
    
    fig = poll_evolution_plot(
        polls.filter(
            pl.col("source").is_in(sondeur)
            & pl.col("sample_size").is_between(min_echantillon, max_echantillon)
            & pl.col("end_date").is_between(min_date, max_date)
        ),
        official,
        items=items,
        mode=mode
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )