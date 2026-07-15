import streamlit as st
import polars as pl
from data import (
    load_poll_data,
)
from plots import (
    poll_evolution_plot,
)


st.set_page_config(
    page_title="Explorateur du sondage LLM",
    layout="wide",
)

st.header(
    "Evolution des sondages"
)

mode = st.selectbox('Mode', options=['Candidats', 'Blocs politiques'])

year = st.selectbox('Année', options=[2022])

tour = st.selectbox('Tour', options=['Premier tour', 'Second tour'])

official, polls = load_poll_data(year)

if mode == "Candidats":

    fig = poll_evolution_plot(
        polls,
        official,
        year,
        mode="candidate",
    )

else:

    fig = poll_evolution_plot(
        polls,
        official,
        year,
        mode="bloc",
    )


st.plotly_chart(
    fig,
    width="stretch",
)