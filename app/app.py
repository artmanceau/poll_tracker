import streamlit as st
import s3fs
import polars as pl
from plots import (
    poll_evolution_plot,
)
from poll_tracker.assets.candidates import candidates, election_candidates, second_round
from poll_tracker.assets.bloc_mapping import blocs_level_1, blocs_level_2, blocs_level_3
import faulthandler

faulthandler.enable()

storage_options = {
    "profile": "default",
}

# TODO
# Hoovering
# Blocs colors
# 2027 —> Keep track of indicated precision to show in the UI
# Multiple second tour
# Resultats 1995, 1988
# Previous election
# + deploy

fs = s3fs.S3FileSystem(
    profile="default",
    endpoint_url="https://minio.lab.sspcloud.fr",
    client_kwargs={
        "region_name": "us-east-1",
    },
)

YEARS = ["2027", "2022", "2017","2012",  "2007",  "2002","1995", "1988"]


@st.cache_data
def load_poll_data(
    year,
    election_type,
    tour
):
    data = (
        pl.read_parquet(
            f"s3://arthurmanceau/poll_tracker/wiki/{election_type}/{year}/{tour}/polls.parquet",
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

year = st.selectbox('Année', options=YEARS)

election_type = st.selectbox('Type d\'élection', options=["Élections présidentielles"])

tour = st.selectbox('Tour', options=['Premier tour', 'Second tour'])

data = load_poll_data(year, CODE_ELECTION[election_type], CODE_TOUR[tour])
official, polls = data.filter(pl.col('source') == "Résultats"), data.filter(pl.col('source')!="Résultats")
no_sample_size = polls.filter(pl.col('sample_size').is_not_null()).height == 0

if official.height == 0:
    st.warning(f'No result for: {year}')


col1, col2 = st.columns([1, 4], gap="small")


with col1:
    sources = (
        polls["source"]
        .unique()
        .sort()
        .to_list()
    )
    sondeur = st.multiselect('source', sources, default=sources)

    # Sliders must tolerate missing/all-null columns: st.slider rejects None
    # bounds (KeyError: NoneType), and older parquet files may lack sample_size.
    if no_sample_size:
        min_echantillon = max_echantillon = None
    else:
        sample_vals = polls.get_column('sample_size').drop_nulls()
        if sample_vals.len() > 0:
            s_lo, s_hi = int(sample_vals.min()), int(sample_vals.max())
            if s_lo < s_hi:
                min_echantillon, max_echantillon = st.slider(
                    "Taille de l'échantillon", s_lo, s_hi, (s_lo, s_hi)
                )
            else:
                min_echantillon, max_echantillon = s_lo, s_hi

    min_date = max_date = None
    date_vals = polls.get_column('end_date').drop_nulls()
    if date_vals.len() > 0:
        d_lo, d_hi = date_vals.min(), date_vals.max()
        if d_lo < d_hi:
            default_lo = polls.select(
                pl.col('end_date').max().dt.offset_by("-6mo")
            ).item()
            if default_lo is None or default_lo < d_lo:
                default_lo = d_lo
            min_date, max_date = st.slider(
                "Date du sondage", d_lo, d_hi, (default_lo, d_hi)
            )
        else:
            min_date, max_date = d_lo, d_hi
    mode = st.selectbox('Mode', options=['Candidats', 'Blocs politiques'] if (tour == 'Premier tour') else ['Candidats'])
    
    if (mode == 'Candidats') and (tour == 'Premier tour'):
        if official.height > 0:
            remove_below_5 = st.checkbox('Retirer les candidats avec moins de 5%', value=True)
            remove_candidate_that_didnt_run = st.checkbox('Retirer les candidats qui ne se sont pas présenté officiellement', value=True)
            if remove_candidate_that_didnt_run:
                items = [f'C_{candidate}_processed' for candidate in election_candidates[str(year)]]
            else:
                items = list(set([f'C_{candidate}_processed' for candidate in candidates.keys()]).intersection(set(polls.columns)))

            if remove_below_5:
                cand = items
                items = official.select(cand).transpose(
                    include_header=True,
                    header_name="candidate",
                ).filter(
                    pl.col("column_0") > 5
                ).get_column("candidate")

        else:
            items = [f'C_{candidate}_processed' for candidate in election_candidates[str(year)]]

    elif (mode == 'Candidats') and (tour == 'Second tour'):
        items = [f'C_{candidate}_processed' for candidate in second_round[str(year)]]

    elif mode == 'Blocs politiques':
        blocs = st.radio('Division', options=[blocs_level_1, blocs_level_2, blocs_level_3])
        items = [f'BP_{b}' for b in blocs]

with col2:

    poll_filter = pl.col("source").is_in(sondeur)
    poll_filter &= pl.col("end_date").is_between(min_date, max_date)

    if not no_sample_size:
        poll_filter &= pl.col("sample_size").is_between(min_echantillon, max_echantillon)
    
    fig = poll_evolution_plot(
        polls.filter(poll_filter),
        official,
        items=items,
        mode=mode,
        no_sample_size=no_sample_size
    )

    event = st.plotly_chart(
        fig,
        width="stretch",
        on_select="rerun",
        selection_mode="points",
        key="poll_chart",
    )

    # A plotly hover tooltip can't be clicked (it disappears on mouse-out), so
    # instead we capture the clicked marker and render its source as a real link.
    points = event.selection["points"] if event and event.selection else []
    if points:
        customdata = points[0].get("customdata")
        if customdata:
            source, sample_size, source_link = customdata[0], customdata[1], customdata[2]
            if source_link is not None:
                st.link_button(
                    f"Ouvrir la source — {source} (n={sample_size})",
                    source_link,
                )
        else:
            st.info("Ce point n'a pas de lien source associé.")