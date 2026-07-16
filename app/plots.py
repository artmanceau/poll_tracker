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
    mode,
    no_sample_size=False
):
    fig = go.Figure()
    colors = CANDIDATE_COLORS if mode == 'Candidats' else BLOC_COLORS
    names = CANDIDATE_NAMES if mode == 'Candidats' else {}

    # Full x-span for the official-result reference lines. Kept as real traces
    # (not add_hline shapes) so they share each candidate's legendgroup and
    # therefore hide/show together when a candidate is toggled or isolated.
    date_min = polls.get_column("end_date").min() if polls.height else None
    date_max = polls.get_column("end_date").max() if polls.height else None

    # Official-score labels are collected here and de-overlapped after the loop,
    # then pinned to the right edge of the plot.
    official_labels = []

    for item in items:

        display_name = names.get(item, item.removeprefix('BP_'))

        if official.height > 0:

            true_score = (
                official
                .select(item)
                .item()
            )
        else:
            true_score = None

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
            official_labels.append((true_score, colors[item]))

        cols = ["end_date", "source", "source_link", item]
        if not no_sample_size:
            cols.append("sample_size")

        sdf = (
            polls
            .select(cols)
            .drop_nulls(subset=[item, 'source', 'end_date'])
            .sort("end_date")
        )

        if sdf.height == 0:
            continue

        end_date = sdf.get_column("end_date").to_numpy()
        values = sdf.get_column(item).to_numpy()
        source = sdf.get_column("source").to_list()
        source_link = sdf.get_column("source_link").to_list()
        sample_size = (
            None if no_sample_size
            else sdf.get_column("sample_size").to_numpy()
        )

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
                    hovertemplate=(
                        f"<b>{display_name}</b><br>"
                        "%{x|%d %b %Y}<br>"
                        "Tendance : %{y:.1f}%"
                        "<extra></extra>"
                    ),
                    showlegend=True,
                )
            )
            line_drawn = True

        if no_sample_size:
            marker_size = 8
            # No sample_size column: keep a placeholder slot so app.py's
            # customdata[1] read stays valid, and drop the "Échantillon" line.
            customdata = np.array(
                list(zip(source, [None] * len(source), source_link)),
                dtype=object,
            )
            hovertemplate = (
                f"<b>{display_name}</b><br>"
                "%{x|%d %b %Y}<br>"
                "Intentions : %{y:.1f}%<br>"
                "Source : %{customdata[0]}<br>"
                "<i>Cliquer pour ouvrir la source</i>"
                "<extra></extra>"
            )
        else:
            marker_size = np.clip(sample_size / 350, 5, 20)
            customdata = np.array(
                list(zip(source, sample_size.tolist(), source_link)),
                dtype=object,
            )
            hovertemplate = (
                f"<b>{display_name}</b><br>"
                "%{x|%d %b %Y}<br>"
                "Intentions : %{y:.1f}%<br>"
                "Source : %{customdata[0]}<br>"
                "Échantillon : %{customdata[1]}<br>"
                "<i>Cliquer pour ouvrir la source</i>"
                "<extra></extra>"
            )

        fig.add_trace(
            go.Scatter(
                x=end_date,
                y=values,
                mode="markers",
                name=display_name,
                legendgroup=item,
                marker=dict(
                    color=colors[item],
                    size=marker_size,
                ),
                customdata=customdata,
                hovertemplate=hovertemplate,
                showlegend=not line_drawn,
            )
        )

    # Place official-score labels on the right edge, nudging apart any that would
    # collide. Labels are sorted low→high and pushed up so each keeps a minimum
    # vertical gap from the previous one.
    if official_labels:
        span = max(s for s, _ in official_labels) - min(s for s, _ in official_labels)
        min_gap = max(0.9, span * 0.04)
        label_y = None
        for score, color in sorted(official_labels, key=lambda x: x[0]):
            label_y = score if label_y is None else max(score, label_y + min_gap)
            fig.add_annotation(
                xref="paper",
                x=1,
                xanchor="left",
                y=label_y,
                yanchor="middle",
                text=f"{score:.1f}%",
                showarrow=False,
                xshift=8,
                font=dict(color=color, size=12),
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
        margin=dict(r=70),
    )

    return fig
