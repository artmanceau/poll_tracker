"""Plotly figure for the poll-evolution chart.

Per candidate (or political bloc) the figure layers three marks that share a
legend group so they toggle together:

* a dashed **official-result** line spanning the x-axis (when a result exists);
* a smoothed **trend** line (lowess);
* the **individual poll points** (square markers).

Hovering uses ``x unified``: every point sharing an ``end_date`` — i.e. all the
candidates of one poll — is grouped into a single box, with a dashed vertical
spike marking the poll's date. The trend and result lines are excluded from that
box so it lists only the poll's candidate points.
"""

from typing import NamedTuple

import numpy as np
import polars as pl
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

from poll_tracker.assets.candidates import candidates
from poll_tracker.assets.bloc_mapping import BLOC_COLORS as _BLOC_COLORS

CANDIDATE_COLORS = {f"C_{cid}_processed": c["color"] for cid, c in candidates.items()}
CANDIDATE_NAMES = {f"C_{cid}_processed": c["name"] for cid, c in candidates.items()}
BLOC_COLORS = {f"BP_{bid}": color for bid, color in _BLOC_COLORS.items()}

MODE_CANDIDATES = "Candidats"

# lowess is a C extension that segfaults on degenerate input (too few points or
# tied x-values), so we collapse same-day polls and only smooth beyond this many
# distinct dates.
MIN_POINTS_FOR_TREND = 4
TREND_FRAC = 0.25

NEUTRAL = "#8a8a8a"

# Marker sizing: fixed when no sample size is known, else scaled by sample size.
DEFAULT_MARKER_SIZE = 8
MARKER_SIZE_RANGE = (5, 20)
SAMPLE_PER_PIXEL = 350

# Trend / result lines get a minimal tooltip: candidate name + the one value.
TREND_HOVERTEMPLATE = "<b>{name}</b><br>Tendance : %{{y:.1f}}%<extra></extra>"
RESULT_HOVERTEMPLATE = "<b>{name}</b><br>Résultat : %{{y:.1f}}%<extra></extra>"


class _Series(NamedTuple):
    """Arrays extracted for one item, ready to feed to plotly / lowess."""

    end_date: np.ndarray
    values: np.ndarray
    source: list
    source_link: list
    sample_size: np.ndarray | None
    label_line: list  # "<br>Précision : …" per point, or "" when the label is null
    trend_x: np.ndarray  # distinct dates as epoch seconds
    trend_y: np.ndarray  # same-day mean of `values`


def poll_evolution_plot(
    polls,
    official,
    items,
    mode,
    no_sample_size=False,
    events=None,
):
    colors = CANDIDATE_COLORS if mode == MODE_CANDIDATES else BLOC_COLORS
    names = CANDIDATE_NAMES if mode == MODE_CANDIDATES else {}
    date_span = _date_span(polls)

    fig = go.Figure()
    official_scores = []  # (score, color, name), de-overlapped into left-edge labels

    for item in items:
        color = colors[item]
        name = names.get(item, item.removeprefix("BP_"))

        score = _official_score(official, item)
        if score is not None and date_span is not None:
            fig.add_trace(_result_line(name, color, item, score, date_span))
            official_scores.append((score, color, name))

        series = _extract_series(polls, item, no_sample_size)
        if series is None:
            continue

        trend = _trend_line(name, color, item, series)
        if trend is not None:
            fig.add_trace(trend)
        fig.add_trace(
            _poll_points(name, color, item, series, no_sample_size, show_legend=trend is None)
        )

    _add_official_labels(fig, official_scores)
    _add_events(fig, events)
    _apply_layout(fig)
    return fig


# --- Data extraction ------------------------------------------------------

def _label_column(item):
    """Sibling label column for a candidate item, or None for blocs.

    Candidate scores are ``C_<id>_processed`` and carry a free-text
    ``C_<id>_label`` (blank, or a precision on the hypothesis tested). Blocs
    (``BP_*``) have none.
    """
    if item.startswith("C_") and item.endswith("_processed"):
        return item.removesuffix("_processed") + "_label"
    return None


def _date_span(polls):
    if polls.height == 0:
        return None
    dates = polls.get_column("end_date")
    return dates.min(), dates.max()


def _official_score(official, item):
    if official.height == 0:
        return None
    return official.select(item).item()


def _extract_series(polls, item, no_sample_size):
    """Pull one item's points (sorted by date) out of `polls`, or None if empty."""
    label_col = _label_column(item)
    wanted = ["end_date", "source", "source_link", item, label_col]
    if not no_sample_size:
        wanted.append("sample_size")
    # A label column only exists in candidate-mode parquets; keep what's present.
    cols = [c for c in wanted if c and c in polls.columns]

    sdf = (
        polls.select(cols)
        .drop_nulls(subset=[item, "source", "end_date"])
        .sort("end_date")
    )
    if sdf.height == 0:
        return None

    labels = (
        sdf.get_column(label_col).to_list()
        if label_col in sdf.columns
        else [None] * sdf.height
    )
    # Collapse same-day polls to one point so lowess gets strictly distinct dates.
    agg = (
        sdf.select(
            pl.col("end_date").dt.epoch("s").alias("date_num"),
            pl.col(item).alias("val"),
        )
        .group_by("date_num")
        .agg(pl.col("val").mean())
        .sort("date_num")
    )

    return _Series(
        end_date=sdf.get_column("end_date").to_numpy(),
        values=sdf.get_column(item).to_numpy(),
        source=sdf.get_column("source").to_list(),
        source_link=sdf.get_column("source_link").to_list(),
        sample_size=None if no_sample_size else sdf.get_column("sample_size").to_numpy(),
        label_line=[f"<br>Précision : {v}" if v not in (None, "") else "" for v in labels],
        trend_x=agg.get_column("date_num").to_numpy().astype("float64"),
        trend_y=agg.get_column("val").to_numpy(),
    )


# --- Traces ---------------------------------------------------------------

def _result_line(name, color, group, score, date_span):
    """Dashed horizontal line at the official result, spanning the x-axis."""
    date_min, date_max = date_span
    return go.Scatter(
        x=[date_min, date_max],
        y=[score, score],
        mode="lines",
        name=name,
        legendgroup=group,
        line=dict(color=color, width=1, dash="longdash"),
        hovertemplate=RESULT_HOVERTEMPLATE.format(name=name),
        showlegend=False,
    )


def _trend_line(name, color, group, series):
    """Smoothed lowess trend, or None when there are too few distinct dates."""
    if len(series.trend_x) < MIN_POINTS_FOR_TREND:
        return None
    smooth = lowess(
        endog=series.trend_y,
        exog=series.trend_x,
        frac=TREND_FRAC,
        it=0,
        missing="raise",
    )
    return go.Scatter(
        x=smooth[:, 0].astype("int64").astype("datetime64[s]"),
        y=smooth[:, 1],
        mode="lines",
        name=name,
        legendgroup=group,
        line=dict(color=color, width=3),
        hovertemplate=TREND_HOVERTEMPLATE.format(name=name),
        showlegend=True,
    )


def _poll_points(name, color, group, series, no_sample_size, show_legend):
    """Square markers for individual polls.

    customdata keeps source/sample/link at indices 0..2 (app.py reads those for
    the click-to-open link) and the pre-formatted label suffix at index 3.
    """
    if no_sample_size:
        marker_size = DEFAULT_MARKER_SIZE
        sample_col = [None] * len(series.source)
    else:
        marker_size = np.clip(series.sample_size / SAMPLE_PER_PIXEL, *MARKER_SIZE_RANGE)
        sample_col = series.sample_size.tolist()

    customdata = np.array(
        list(zip(series.source, sample_col, series.source_link, series.label_line)),
        dtype=object,
    )
    return go.Scatter(
        x=series.end_date,
        y=series.values,
        mode="markers",
        name=name,
        legendgroup=group,
        marker=dict(color=color, size=marker_size, symbol="square"),
        customdata=customdata,
        hovertemplate=_point_hovertemplate(name, no_sample_size),
        showlegend=show_legend,
    )


def _point_hovertemplate(name, no_sample_size):
    """Detailed per-point tooltip: date, institute, sample, name, score, label."""
    lines = [
        f"<b>{name}</b>",
        "%{x|%d %b %Y}",
        "Institut : %{customdata[0]}",
    ]
    if not no_sample_size:
        lines.append("Échantillon : %{customdata[1]}")
    lines.append("Intentions : %{y:.1f}%")
    # customdata[3] adds a "<br>Précision : …" line only when the label is non-null.
    return "<br>".join(lines) + "%{customdata[3]}<extra></extra>"


# --- Annotations & layout -------------------------------------------------

def _add_official_labels(fig, official_scores):
    """Direct-label each result line at the right edge: candidate name + score.

    Labels are sorted low→high and nudged up so each keeps a minimum vertical
    gap from the previous one.
    """
    if not official_scores:
        return
    scores = [s for s, _, _ in official_scores]
    min_gap = max(0.9, (max(scores) - min(scores)) * 0.04)

    label_y = None
    for score, color, name in sorted(official_scores, key=lambda sc: sc[0]):
        label_y = score if label_y is None else max(score, label_y + min_gap)
        fig.add_annotation(
            xref="paper",
            x=1,
            xanchor="left",
            y=label_y,
            yanchor="middle",
            text=f"<b>{name}</b> {score:.1f}%",
            showarrow=False,
            xshift=8,
            font=dict(color=color, size=12),
        )


def _add_events(fig, events):
    """Draw a vertical dashed line + top label for each event.

    `events` is any frame exposing rows with `event_name` and `event_date`
    (pandas or polars). None or empty is a no-op.
    """
    for name, date in _event_rows(events):
        if date is None:
            continue
        x = str(getattr(date, "isoformat", lambda: date)())
        fig.add_vline(x=x, line=dict(color=NEUTRAL, width=1, dash="dot"))
        fig.add_annotation(
            x=x,
            xref="x",
            y=1,
            yref="paper",
            yanchor="bottom",
            text=name,
            showarrow=False,
            textangle=-90,
            font=dict(size=10, color="#6a6a6a"),
            xshift=-6,
        )


def _event_rows(events):
    """Normalize an events frame (pandas/polars/None) to (name, date) pairs."""
    if events is None:
        return []
    if isinstance(events, pl.DataFrame):
        if events.height == 0:
            return []
        return events.select("event_name", "event_date").iter_rows()
    if getattr(events, "empty", True):  # pandas DataFrame
        return []
    return zip(events["event_name"], events["event_date"])


def _apply_layout(fig):
    fig.update_layout(
        height=900,
        # "closest" gives each mark its own tooltip (point / trend / result).
        hovermode="closest",
        # The dashed spike snaps to the hovered point's date and spans the plot,
        # marking that poll's whole column — every same-poll point and the trend
        # line sit on it — without showing any of their tooltips.
        xaxis=dict(
            title="Date",
            showspikes=True,
            spikemode="across",
            spikedash="dash",
            spikecolor=NEUTRAL,
            spikethickness=1,
            spikesnap="data",
        ),
        yaxis_title="Intentions de vote (%)",
        legend=dict(
            orientation="h",
            y=-0.2,
            groupclick="togglegroup",
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            title_text="Clic : masquer · Double-clic : isoler un candidat",
        ),
        # Wide right margin: labels now read "Candidate name XX.X%", not a bare %.
        margin=dict(r=180),
    )
