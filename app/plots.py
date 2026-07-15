import numpy as np
import pandas as pd
import polars as pl
import streamlit as st
import plotly.graph_objects as go
from poll_tracker.assets.candidates import election_candidates
from statsmodels.nonparametric.smoothers_lowess import lowess

candidate_colors = {
    "arthaud": "#B22222",
    "poutou": "#E53935",
    "roussel": "#C00000",
    "melenchon": "#C62828",
    "hidalgo": "#E91E63",
    "jadot": "#4CAF50",
    "macron": "#F4C542",
    "pecresse": "#0055A4",
    "lassalle": "#4E342E",
    "dupont_aignan": "#1E88E5",
    "le_pen": "#0B3D91",
    "zemmour": "#5C0011",
}
CANDIDATE_COLORS = {f'C_{item}_processed': colors for item, colors in candidate_colors.items()}
BLOC_COLORS = {
    "BP_TD": "#0055A4",
    "BP_TG": "#E91E63"
}


def poll_evolution_plot(
    polls,
    official,
    year,
    mode="candidate",
):

    fig = go.Figure()

    sondeur = st.multiselect('source', polls.unique('source').get_column('source').to_list(), default=polls.unique('source').get_column('source').to_list())
    min_echantillon, max_echantillon = st.slider("Taille de l'échantillon",  polls.get_column('sample_size').min(), polls.get_column('sample_size').max(), (polls.get_column('sample_size').min(), polls.get_column('sample_size').max()))
    min_date, max_date = st.slider("Date du sondage",  polls.get_column('end_date').min(), polls.get_column('end_date').max(), (polls.get_column('end_date').min(), polls.get_column('end_date').max()))

   

    if mode == "candidate":
        items = [f'C_{candidate}_processed' for candidate in election_candidates[str(year)]]
        colors = CANDIDATE_COLORS

    else:
        items = ['BP_TD', 'BP_TG']
        colors = BLOC_COLORS

    for item in items:
        
        true_score = (
            official
            .select(item)
            .item()
        )

        fig.add_hline(
            y=true_score,
            line_width=2,
            line_dash='longdash',
            line_color=colors[item],
            annotation_text=f"{true_score:.1f}%",
            annotation_position="bottom right"
        )

        if sondeur:
            polls = polls.filter(pl.col('source').is_in(sondeur))

        polls = polls.filter(pl.col('sample_size')<=max_echantillon).filter(pl.col('sample_size')>=min_echantillon).filter(pl.col('end_date')>=min_date).filter(pl.col('end_date')<=max_date)

        pdf = (
            polls
            .select(
                [
                    "end_date",
                    "sample_size",
                    "source",
                    item
                ]
            )
            .drop_nulls()
            .to_pandas()
            .sort_values("end_date")
        )


        if pdf.empty:
            continue


        pdf["date_num"] = (
            pd.to_datetime(
                pdf["end_date"]
            )
            .map(
                lambda x:
                x.timestamp()
            )
        )

        smooth = lowess(
            endog=pdf[item],
            exog=pdf["date_num"],
            frac=0.25,
        )

        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(
                    smooth[:,0],
                    unit="s",
                ),
                y=smooth[:,1],
                mode="lines",
                name=item,
                line=dict(
                    color=colors[item],
                    width=3,
                ),
                hoverinfo="skip",
            )
        )


        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(
                    pdf["end_date"]
                ),
                y=pdf[item],
                mode="markers",
                name=item,
                marker=dict(
                    color=colors[item],
                    size=(
                        pdf["sample_size"]
                        /
                        350
                    )
                    .clip(
                        lower=5,
                        upper=20,
                    ),
                ),
                customdata=np.stack(
                    [
                        pdf["source"],
                        pdf["sample_size"],
                    ],
                    axis=1,
                ),
                hovertemplate=(
                    "%{x|%d %b %Y}<br>"
                    "source: %{customdata[0]}"
                    "<br>"
                    "sample_size: %{customdata[1]}"
                    "<extra></extra>"
                ),
            )
        )


    fig.update_layout(
        height=900,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=-0.2,
        ),
        yaxis_title="Intentions de vote (%)",
        xaxis_title="Date",
    )


    return fig