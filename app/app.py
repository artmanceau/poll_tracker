"""Streamlit app: browse the evolution of French presidential-election polls.

Layout: a top row of dataset selectors (year / election / round), then two
columns — filters on the left, the plotly chart on the right.
"""
import polars as pl
import streamlit as st
from plots import poll_evolution_plot
from poll_tracker.assets.candidates import (
    candidates,
    election_candidates,
    second_round,
)
from poll_tracker.assets.bloc_mapping import (
    blocs_level_1_str,
    blocs_level_2_str,
    blocs_level_3_str,
    bloc_level_mapping
)


# --- Configuration --------------------------------------------------------

POLL_URI = "s3://arthurmanceau/poll_tracker/wiki/{election}/{year}/{tour}/polls.parquet"
STORAGE_OPTIONS = {
    "aws_skip_signature": "true",
    "aws_region": "us-east-1",
    "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
}
EVENTS_URI = "s3://arthurmanceau/poll_tracker/wiki/{election}/{year}/events.parquet"

RESULT_SOURCE = "Résultats"  # the source value marking the official result row

YEARS = ["2027", "2022", "2017", "2012", "2007", "2002", "1995", "1988"]
ELECTIONS = {"Élections présidentielles": "presidentiel"}
TOURS = {"Premier tour": "t1", "Second tour": "t2"}

MODE_CANDIDATES = "Candidats"
MODE_BLOCS = "Blocs politiques"
MIN_SCORE_PCT = 5  # threshold for the "remove candidates below 5%" filter

# TODO
# Multiple second tour hyp
# Resultats 1995, 1988
# Previous election
# + deploy


# --- Data loading ---------------------------------------------------------

@st.cache_data
def load_poll_data(year, election, tour):
    uri = POLL_URI.format(election=election, year=year, tour=tour)
    return pl.read_parquet(
        uri, storage_options=STORAGE_OPTIONS
    )


@st.cache_data
def load_events(election: str, year: int, date_range) -> pl.DataFrame:
    """Events for an election/year as a Polars DataFrame[event_name, event_date]."""

    start_date, end_date = date_range

    empty = pl.DataFrame(
        schema={
            "event_name": pl.String,
            "event_date": pl.Date,
        }
    )

    df = pl.read_parquet(
            EVENTS_URI.format(election=election, year=year),
            storage_options=STORAGE_OPTIONS
    )

    if df.height == 0:
        return empty

    return (
        df.with_columns(
            pl.col("event_date").str.to_date()
        ).filter(
            (pl.col('event_date') > start_date) & (pl.col('event_date')<end_date)
        )
        .select("event_name", "event_date")
    )


def split_results(data):
    """Split a poll table into (official_result_row, polls)."""
    is_result = pl.col("source") == RESULT_SOURCE
    return data.filter(is_result), data.filter(~is_result)


def has_sample_size(polls):
    return (
        "sample_size" in polls.columns
        and polls.get_column("sample_size").drop_nulls().len() > 0
    )


# --- Controls (rendered inside the left column) ---------------------------

def select_dataset():
    """Top-row selectors. Returns (year, election_label, tour_label)."""
    year = st.selectbox("Année", options=YEARS)
    election = st.selectbox("Type d'élection", options=list(ELECTIONS))
    tour = st.selectbox("Tour", options=list(TOURS))
    return year, election, tour


def select_sources(polls):
    sources = polls["source"].unique().sort().to_list()
    return st.multiselect("source", sources, default=sources)


def select_sample_range(polls, no_sample_size):
    """(min, max) sample-size bounds, or None when unavailable.

    st.slider rejects None bounds and a zero-width range, so we only render it
    when there are at least two distinct sample sizes.
    """
    if no_sample_size:
        return None
    values = polls.get_column("sample_size").drop_nulls()
    lo, hi = int(values.min()), int(values.max())
    if lo >= hi:
        return lo, hi
    return st.slider("Taille de l'échantillon", lo, hi, (lo, hi))


def select_date_range(polls):
    """(min, max) date bounds; defaults to the last 6 months of polling."""
    values = polls.get_column("end_date").drop_nulls()
    if values.len() == 0:
        return None, None
    lo, hi = values.min(), values.max()
    if lo >= hi:
        return lo, hi
    default_lo = polls.select(pl.col("end_date").max().dt.offset_by("-6mo")).item()
    if default_lo is None or default_lo < lo:
        default_lo = lo
    return st.slider("Date du sondage", lo, hi, (default_lo, hi))


def select_mode(tour):
    options = [MODE_CANDIDATES]
    if tour == "Premier tour":
        options.append(MODE_BLOCS)
    return st.selectbox("Mode", options=options)


def select_items(mode, tour, year, polls, official):
    """The candidate/bloc columns to plot, per the chosen mode and round."""
    if mode == MODE_BLOCS:
        blocs = st.radio("Division", options=[blocs_level_1_str, blocs_level_2_str, blocs_level_3_str])
        return [f"BP_{b}" for b in bloc_level_mapping[str(blocs)]]
    if tour == "Second tour":
        return _candidate_columns(_known_candidates(second_round, year))
    if official.height == 0:
        return _candidate_columns(_known_candidates(election_candidates, year))
    return _first_round_candidates(year, polls, official)


def _known_candidates(mapping, year):
    """Candidate ids configured for `year`, warning (not crashing) if none."""
    ids = mapping.get(str(year))
    if not ids:
        st.info(f"Aucun candidat défini pour cette sélection ({year}).")
        return []
    return ids


def _candidate_columns(ids):
    return [f"C_{cid}_processed" for cid in ids]


def _first_round_candidates(year, polls, official):
    remove_below_5 = st.checkbox("Retirer les candidats avec moins de 5%", value=True)
    only_declared = st.checkbox(
        "Retirer les candidats qui ne se sont pas présenté officiellement",
        value=True,
    )

    if only_declared:
        items = _candidate_columns(election_candidates[str(year)])
    else:
        available = set(_candidate_columns(candidates.keys()))
        items = sorted(available.intersection(polls.columns))

    if remove_below_5:
        items = _above_threshold(official, items, MIN_SCORE_PCT)
    return items


def _above_threshold(official, items, threshold):
    """Keep only items whose official score exceeds `threshold`."""
    return (
        official.select(items)
        .transpose(include_header=True, header_name="candidate")
        .filter(pl.col("column_0") > threshold)
        .get_column("candidate")
        .to_list()
    )


def build_poll_filter(sources, date_range, sample_range):
    expr = pl.col("source").is_in(sources)
    expr &= pl.col("end_date").is_between(*date_range)
    if sample_range is not None:
        expr &= pl.col("sample_size").is_between(*sample_range)
    return expr


# --- Rendering ------------------------------------------------------------

def render_source_link(event):
    """A plotly tooltip can't be clicked, so turn a clicked marker into a link."""
    points = event.selection["points"] if event and event.selection else []
    if not points:
        return
    customdata = points[0].get("customdata")
    if not customdata:
        st.info("Ce point n'a pas de lien source associé.")
        return
    source, sample_size, source_link, *_ = customdata
    if source_link is not None:
        st.link_button(f"Ouvrir la source — {source} (n={sample_size})", source_link)


def main():
    st.set_page_config(page_title="Sondages", layout="wide")
    st.header("Evolution des sondages")

    year, election, tour = select_dataset()
    data = load_poll_data(year, ELECTIONS[election], TOURS[tour])
    official, polls = split_results(data)
    if official.height == 0:
        st.warning(f"No result for: {year}")

    no_sample_size = not has_sample_size(polls)
    controls, chart = st.columns([1, 4], gap="small")

    with controls:
        sources = select_sources(polls)
        sample_range = select_sample_range(polls, no_sample_size)
        date_range = select_date_range(polls)
        mode = select_mode(tour)
        items = select_items(mode, tour, year, polls, official)

    with chart:
        poll_filter = build_poll_filter(sources, date_range, sample_range)
        fig = poll_evolution_plot(
            polls.filter(poll_filter),
            official,
            items=items,
            mode=mode,
            no_sample_size=no_sample_size,
            events=load_events(ELECTIONS[election], year, date_range),
        )
        event = st.plotly_chart(
            fig,
            width="stretch",
            on_select="rerun",
            selection_mode="points",
            key="poll_chart",
        )
        render_source_link(event)


if __name__ == "__main__":
    main()
