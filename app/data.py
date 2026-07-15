import polars as pl
import s3fs
import streamlit as st
from poll_tracker.assets.candidates import election_candidates

storage_options = {
    "profile": "default",
}


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
):
    polls = (
        pl.read_parquet(
            f"s3://arthurmanceau/poll_tracker/data/polls/presidentiel/{year}/t1/polls.parquet",
            storage_options=storage_options,
        )
    )

    official = (
        polls
        .filter(
            pl.col("source")
            ==
            "Résultats"
        )
    )

    polls = (
        polls
        .filter(
            pl.col("source")
            !=
            "Résultats"
        )
    )

    return official, polls