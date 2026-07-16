import numpy as np
import polars as pl
import plotly.graph_objects as go
from poll_tracker.assets.candidates import candidates
from poll_tracker.assets.bloc_mapping import BLOC_COLORS
from statsmodels.nonparametric.smoothers_lowess import lowess

CANDIDATE_COLORS = {f'C_{item}_processed': df['color'] for item, df in candidates.items()}
CANDIDATE_NAMES = {f'C_{item}_processed': df['name'] for item, df in candidates.items()}
BLOC_COLORS = {f'BP_{item}': color for item, color in BLOC_COLORS.items()}

def poll_evolution_plot(
    polls,
    official,
    items,
    mode
):
    fig = go.Figure()
    colors = CANDIDATE_COLORS if mode == 'Candidats' else BLOC_COLORS
    names = CANDIDATE_NAMES if mode == 'Candidats' else {}

    # Full x-span for the official-result reference lines. Kept as real traces
    # (not add_hline shapes) so they share each candidate's legendgroup and
    # therefore hide/show together when a candidate is toggled or isolated.
    date_min = polls.get_column("end_date").min() if polls.height else None
    date_max = polls.get_column("end_date").max() if polls.height else None

    for item in items:

        display_name = names.get(item, item.removeprefix('BP_'))

        true_score = (
            official
            .select(item)
            .item()
        )
        if true_score is not None and date_min is not None:
            fig.add_trace(
                go.Scatter(
                    x=[date_min, date_max],
                    y=[true_score, true_score],
                    mode="lines",
                    name=display_name,
                    legendgroup=item,
                    line=dict(
                        color=colors[item],
                        width=1,
                        dash="longdash",
                    ),
                    hovertemplate=(
                        f"<b>{display_name}</b><br>"
                        f"Résultat officiel : {true_score:.1f}%"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                )
            )

        sdf = (
            polls
            .select(
                [
                    "end_date",
                    "sample_size",
                    "source",
                    "source_link",
                    item,
                ]
            )
            .drop_nulls()
            .sort("end_date")
        )

        if sdf.height == 0:
            continue

        end_date = sdf.get_column("end_date").to_numpy()
        values = sdf.get_column(item).to_numpy()
        sample_size = sdf.get_column("sample_size").to_numpy()
        source = sdf.get_column("source").to_list()
        source_link = sdf.get_column("source_link").to_list()

        # statsmodels' lowess is a C extension that SEGFAULTS on degenerate input:
        # too few points, or tied x-values (very common here — several polls end the
        # same day). Collapse same-day polls to one point and only smooth when there
        # are enough distinct dates.
        agg = (
            sdf
            .select(
                pl.col("end_date").dt.epoch("s").alias("date_num"),
                pl.col(item).alias("val"),
            )
            .group_by("date_num")
            .agg(pl.col("val").mean())
            .sort("date_num")
        )

        line_drawn = False
        if agg.height >= 4:
            smooth = lowess(
                endog=agg.get_column("val").to_numpy(),
                exog=agg.get_column("date_num").to_numpy().astype("float64"),
                frac=0.25,
                it=0,
                missing="raise",
            )
            fig.add_trace(
                go.Scatter(
                    x=smooth[:, 0].astype("int64").astype("datetime64[s]"),
                    y=smooth[:, 1],
                    mode="lines",
                    name=display_name,
                    legendgroup=item,
                    line=dict(
                        color=colors[item],
                        width=3,
                    ),
                    hoverinfo="skip",
                    showlegend=True,
                )
            )
            line_drawn = True

        fig.add_trace(
            go.Scatter(
                x=end_date,
                y=values,
                mode="markers",
                name=display_name,
                legendgroup=item,
                marker=dict(
                    color=colors[item],
                    size=np.clip(sample_size / 350, 5, 20),
                ),
                customdata=np.array(
                    list(zip(source, sample_size.tolist(), source_link)),
                    dtype=object,
                ),
                hovertemplate=(
                    f"<b>{display_name}</b><br>"
                    "%{x|%d %b %Y}<br>"
                    "Intentions : %{y:.1f}%<br>"
                    "Source : %{customdata[0]}<br>"
                    "Échantillon : %{customdata[1]}<br>"
                    "<i>Cliquer pour ouvrir la source</i>"
                    "<extra></extra>"
                ),
                showlegend=not line_drawn,
            )
        )

    fig.update_layout(
        height=900,
        hovermode="closest",
        legend=dict(
            orientation="h",
            y=-0.2,
            groupclick="togglegroup",
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            title_text="Clic : masquer · Double-clic : isoler un candidat",
        ),
        yaxis_title="Intentions de vote (%)",
        xaxis_title="Date",
    )

    return fig
