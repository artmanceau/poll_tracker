import numpy as np
import pandas as pd
import polars as pl
import streamlit as st
import plotly.graph_objects as go
from poll_tracker.assets.candidates import candidates
from poll_tracker.assets.bloc_mapping import BLOC_COLORS
from statsmodels.nonparametric.smoothers_lowess import lowess

CANDIDATE_COLORS = {f'C_{item}_processed': df['color'] for item, df in candidates.items()}
BLOC_COLORS = {f'BP_{item}': color for item, color in BLOC_COLORS.items()}


def poll_evolution_plot(
    polls,
    official,
    items,
    mode
):
    fig = go.Figure()
    colors = CANDIDATE_COLORS if mode == 'Candidats' else BLOC_COLORS

    df = polls.sort("end_date").to_pandas()
    official_pdf = official.to_pandas()

    for item in items:

        if item in official.columns and official.height:
            true_score = official[item][0]
        else:
            true_score = None

        if true_score is not None:
            fig.add_hline(
                y=true_score,
                line_width=1,
                line_dash='longdash',
                line_color=colors[item],
                annotation_text=f"{true_score:.1f}%",
                annotation_position="bottom right"
            )

        pdf = df[
                ["end_date", "sample_size", "source", "source_link", item]
            ].dropna()

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

        if len(df) >= 3:
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
                        showlegend=False,
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
                    customdata=df[
                        ["source", "sample_size", "source_link"]
                    ].to_numpy(),
                    hovertemplate=(
                        "%{x|%d %b %Y}<br>"
                        "Element: %{name}"
                        "Value: %{y:.1f}%<br>"
                        "Source: %{customdata[0]}<br>"
                        "Sample size: %{customdata[1]}<br>"
                        "<a href='%{customdata[2]}'>Source link</a>"
                        "<extra></extra>"
                    ),
                    showlegend=True,
                )
        )


    fig.update_layout(
            height=900,
            hovermode="closest",
            legend=dict(
                orientation="h",
                y=-0.2,
            ),
            yaxis_title="Intentions de vote (%)",
            xaxis_title="Date",
    )


    return fig