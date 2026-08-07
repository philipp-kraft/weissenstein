#!/usr/bin/env python3
"""Dash web app: benchmark score for each Cheshire microarchitectural sweep point."""

import time
from pathlib import Path

from dash import Dash, dash_table, dcc, html, callback, Output, Input, State
import plotly.graph_objects as go
import pandas as pd

RESULTS_DIR = Path(__file__).parent / "results"
BASE_COLUMNS = ["name", "score", "score_mhz", "timestamp"]

INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
SURFACE = "#ffffff"
PAGE = "#f5f5f4"
GRIDLINE = "#e6e5e1"
BORDER = "#e2e1dc"
BLUE = "#2a78d6"
RED = "#d03b3b"
GREEN = "#0ca30c"
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

SOURCE_COLORS = [BLUE, "#0ca3a3", "#8b5cf6", "#eb6834", "#c026d3", "#65a30d", "#d97706", "#0891b2"]

CARD = {
    "backgroundColor": SURFACE,
    "border": f"1px solid {BORDER}",
    "borderRadius": "10px",
    "padding": "20px 24px",
}


def load(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["error"] = df["error"].astype(str).str.lower() != "false"
    if "family" not in df.columns:
        df["family"] = ""
    else:
        df["family"] = df["family"].fillna("")
    return df


def load_combined(sources: list[str]) -> pd.DataFrame:
    frames = []
    for s in sources:
        d = load(RESULTS_DIR / s)
        d["source"] = s
        frames.append(d)
    if not frames:
        return pd.DataFrame(columns=["source", "family", "error"] + BASE_COLUMNS)
    return pd.concat(frames, ignore_index=True)


def sources_by_mtime() -> list[str]:
    return [
        p.name
        for p in sorted(
            RESULTS_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True
        )
    ]


def format_ago(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    return f"{seconds // 3600}h ago"


def badge(text: str, dot: str = BLUE):
    return html.Span(
        [
            html.Span(
                style={
                    "display": "inline-block",
                    "width": "7px",
                    "height": "7px",
                    "borderRadius": "50%",
                    "backgroundColor": dot,
                    "marginRight": "6px",
                }
            ),
            text,
        ],
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "backgroundColor": PAGE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "999px",
            "padding": "4px 12px",
            "fontSize": "12px",
            "color": SECONDARY_INK,
            "marginRight": "8px",
        },
    )


def stat_tile(tile_id: str, label: str):
    return html.Div(
        style={**CARD, "flex": "1", "position": "relative", "overflow": "hidden"},
        children=[
            html.Div(
                style={
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "width": "4px",
                    "height": "100%",
                    "backgroundColor": BLUE,
                }
            ),
            html.Div(
                label,
                style={
                    "color": MUTED_INK,
                    "fontSize": "11px",
                    "fontWeight": 600,
                    "textTransform": "uppercase",
                    "letterSpacing": "0.04em",
                    "marginBottom": "6px",
                },
            ),
            html.Div(
                id=tile_id,
                style={"color": INK, "fontSize": "24px", "fontWeight": 600},
            ),
        ],
    )


sources = sources_by_mtime()

app = Dash()

app.layout = html.Div(
    style={
        "backgroundColor": PAGE,
        "minHeight": "100vh",
        "fontFamily": FONT,
        "padding": "32px 40px",
    },
    children=[
        html.Div(
            style={"maxWidth": "1200px", "margin": "0 auto"},
            children=[
                html.H1(
                    "Cheshire Sweep Results",
                    style={
                        "color": INK,
                        "fontSize": "26px",
                        "fontWeight": 700,
                        "margin": "0 0 6px",
                    },
                ),
                html.P(
                    "Benchmark score for each Cheshire microarchitectural sweep point.",
                    style={
                        "color": SECONDARY_INK,
                        "fontSize": "14px",
                        "margin": "0 0 14px",
                    },
                ),
                html.Div(id="meta-row", style={"marginBottom": "24px"}),
                dcc.Interval(id="refresh", interval=10000),
                html.Div(
                    style={**CARD, "marginBottom": "20px"},
                    children=[
                        html.Div(
                            "Options",
                            style={
                                "color": MUTED_INK,
                                "fontSize": "11px",
                                "fontWeight": 600,
                                "textTransform": "uppercase",
                                "letterSpacing": "0.04em",
                                "marginBottom": "10px",
                            },
                        ),
                        html.Div(
                            style={"display": "flex", "gap": "24px"},
                            children=[
                                html.Div(
                                    children=[
                                        html.Label(
                                            "Sources",
                                            style={
                                                "display": "block",
                                                "color": SECONDARY_INK,
                                                "fontSize": "12px",
                                                "fontWeight": 600,
                                                "marginBottom": "4px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            sources,
                                            sources[:1],
                                            id="source-dropdown",
                                            multi=True,
                                            clearable=False,
                                            style={
                                                "width": "420px",
                                                "fontFamily": FONT,
                                            },
                                        ),
                                    ],
                                ),
                                html.Div(
                                    children=[
                                        html.Label(
                                            "Sweep family",
                                            style={
                                                "display": "block",
                                                "color": SECONDARY_INK,
                                                "fontSize": "12px",
                                                "fontWeight": 600,
                                                "marginBottom": "4px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["All"],
                                            "All",
                                            id="family-dropdown",
                                            clearable=False,
                                            style={
                                                "width": "200px",
                                                "fontFamily": FONT,
                                            },
                                        ),
                                    ],
                                ),
                                html.Div(
                                    children=[
                                        html.Label(
                                            "Sort by",
                                            style={
                                                "display": "block",
                                                "color": SECONDARY_INK,
                                                "fontSize": "12px",
                                                "fontWeight": 600,
                                                "marginBottom": "4px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            [
                                                {
                                                    "label": "Default",
                                                    "value": "default",
                                                },
                                                {"label": "Name", "value": "name"},
                                                {
                                                    "label": "Score",
                                                    "value": "score_mhz",
                                                },
                                            ],
                                            "default",
                                            id="sort-dropdown",
                                            clearable=False,
                                            style={
                                                "width": "160px",
                                                "fontFamily": FONT,
                                            },
                                        ),
                                    ],
                                ),
                                html.Div(
                                    children=[
                                        html.Label(
                                            "Auto-refresh",
                                            style={
                                                "display": "block",
                                                "color": SECONDARY_INK,
                                                "fontSize": "12px",
                                                "fontWeight": 600,
                                                "marginBottom": "4px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            [
                                                {"label": "1s", "value": 1},
                                                {"label": "3s", "value": 3},
                                                {"label": "10s", "value": 10},
                                                {"label": "30s", "value": 30},
                                                {"label": "Off", "value": 0},
                                            ],
                                            10,
                                            id="refresh-interval-dropdown",
                                            clearable=False,
                                            style={
                                                "width": "160px",
                                                "fontFamily": FONT,
                                            },
                                        ),
                                    ],
                                ),
                                html.Div(
                                    children=[
                                        html.Label(
                                            "Labels",
                                            style={
                                                "display": "block",
                                                "color": SECONDARY_INK,
                                                "fontSize": "12px",
                                                "fontWeight": 600,
                                                "marginBottom": "4px",
                                            },
                                        ),
                                        dcc.Checklist(
                                            [{"label": " Show numbers", "value": "show"}],
                                            ["show"],
                                            id="show-labels-checklist",
                                            style={
                                                "color": SECONDARY_INK,
                                                "fontSize": "13px",
                                                "marginTop": "6px",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "16px",
                        "marginBottom": "20px",
                    },
                    children=[
                        stat_tile("stat-total", "Sweep points"),
                        stat_tile("stat-errored", "Errors"),
                        stat_tile("stat-best", "Best Score"),
                    ],
                ),
                html.Div(
                    style={**CARD, "marginBottom": "20px"},
                    children=[
                        html.Div(
                            "Benchmark score by configuration",
                            style={
                                "color": INK,
                                "fontSize": "15px",
                                "fontWeight": 600,
                                "marginBottom": "4px",
                            },
                        ),
                        html.Div(
                            id="skipped-note",
                            style={
                                "color": RED,
                                "fontSize": "13px",
                                "fontWeight": 600,
                                "marginBottom": "8px",
                            },
                        ),
                        dcc.Graph(
                            id="graph-content",
                            config={
                                "displaylogo": False,
                                "toImageButtonOptions": {
                                    "format": "png",
                                    "filename": "cheshire_benchmark",
                                    "scale": 10,
                                },
                            },
                        ),
                    ],
                ),
                html.Div(
                    style=CARD,
                    children=[
                        html.Div(
                            id="table-title",
                            style={
                                "color": INK,
                                "fontSize": "15px",
                                "fontWeight": 600,
                                "marginBottom": "12px",
                            },
                        ),
                        dash_table.DataTable(
                            id="results-table",
                            page_size=25,
                            sort_action="native",
                            fixed_rows={"headers": True},
                            style_table={
                                "overflowX": "auto",
                                "overflowY": "auto",
                                "maxHeight": "420px",
                            },
                            style_as_list_view=True,
                            style_cell={
                                "textAlign": "left",
                                "fontFamily": FONT,
                                "fontSize": "13px",
                                "color": INK,
                                "padding": "8px 12px",
                                "border": "none",
                                "borderBottom": f"1px solid {GRIDLINE}",
                            },
                            style_header={
                                "backgroundColor": SURFACE,
                                "color": MUTED_INK,
                                "fontWeight": 600,
                                "textTransform": "uppercase",
                                "fontSize": "11px",
                                "letterSpacing": "0.04em",
                                "borderBottom": f"1px solid {GRIDLINE}",
                            },
                            style_data={"backgroundColor": SURFACE},
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@callback(
    Output("source-dropdown", "options"),
    Output("source-dropdown", "value"),
    Input("refresh", "n_intervals"),
    State("source-dropdown", "value"),
)
def refresh_sources(_n, current):
    found = sources_by_mtime()
    current = current or []
    value = [s for s in current if s in found] or (found[:1] if found else [])
    return found, value


@callback(
    Output("family-dropdown", "options"),
    Output("family-dropdown", "value"),
    Input("source-dropdown", "value"),
    State("family-dropdown", "value"),
)
def refresh_families(sources, current):
    if not sources:
        return ["All"], "All"
    families = sorted(load_combined(sources)["family"].unique())
    options = ["All", "Baseline"] + [f for f in families if f != "baseline"]
    value = current if current in options else "All"
    return options, value


@callback(
    Output("refresh", "interval"),
    Output("refresh", "disabled"),
    Input("refresh-interval-dropdown", "value"),
)
def set_refresh_interval(seconds):
    return max(seconds, 1) * 1000, seconds == 0


@callback(
    Output("graph-content", "figure"),
    Output("results-table", "columns"),
    Output("results-table", "data"),
    Output("skipped-note", "children"),
    Output("meta-row", "children"),
    Output("stat-total", "children"),
    Output("stat-errored", "children"),
    Output("stat-best", "children"),
    Output("table-title", "children"),
    Input("source-dropdown", "value"),
    Input("family-dropdown", "value"),
    Input("sort-dropdown", "value"),
    Input("show-labels-checklist", "value"),
    Input("refresh", "n_intervals"),
)
def update_graph(sources, family, sort_by, show_labels, _n):
    show_labels = "show" in (show_labels or [])
    if not sources:
        return go.Figure(), [], [], "", [], "-", "-", "-", "Sweep results"

    df = load_combined(sources)
    if family == "Baseline":
        df = df[df["name"] == "baseline"]
    elif family and family != "All":
        df = df[(df["family"] == family) | (df["name"] == "baseline")]
    plotted = df[~df["error"]].assign(is_baseline=lambda d: d["name"] == "baseline")

    if sort_by == "name":
        name_order = sorted(plotted["name"].unique())
    elif sort_by == "score_mhz":
        name_order = (
            plotted.groupby("name")["score_mhz"]
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        )
    else:
        name_order = list(dict.fromkeys(plotted["name"]))
    if "baseline" in name_order:
        name_order.remove("baseline")
        name_order.insert(0, "baseline")

    skipped = [
        f"{row['name']} ({row['source']})" for _, row in df[df["error"]].iterrows()
    ]
    note = (
        f"Skipped {len(skipped)} point(s) with error: {', '.join(skipped)}"
        if skipped
        else ""
    )

    best_row = plotted.loc[plotted["score_mhz"].idxmax()]
    best_val = f"{best_row['score_mhz']:.3f}"

    latest_mtime = max((RESULTS_DIR / s).stat().st_mtime for s in sources)
    meta = [
        badge(f"Last updated: {format_ago(time.time() - latest_mtime)}", dot=GREEN),
    ]

    data_order = [n for n in name_order if n != "baseline"]
    if "baseline" in name_order:
        data_order.append("baseline")

    max_score = plotted["score_mhz"].max()

    bargap = 0.25
    n_sources = len(sources)
    group_width = 1 - bargap
    bar_width = group_width / n_sources

    fig = go.Figure()
    for i, src in enumerate(sources):
        d = plotted[plotted["source"] == src].set_index("name").reindex(data_order)
        color = SOURCE_COLORS[i % len(SOURCE_COLORS)]
        fig.add_bar(
            name=src,
            x=data_order,
            y=d["score_mhz"],
            width=bar_width,
            offset=-group_width / 2 + i * bar_width,
            text=[f"{v:.2f}" if pd.notna(v) and show_labels else "" for v in d["score_mhz"]],
            textposition="outside",
            textfont=dict(size=14, color=INK, family=FONT, weight="bold"),
            cliponaxis=False,
            marker=dict(
                color=color,
                line_width=0,
                pattern=dict(shape=["/" if b else "" for b in d["is_baseline"].fillna(False)]),
            ),
            customdata=d[["score", "timestamp"]],
            hovertemplate=(
                f"<b>%{{x}}</b><br>{src}"
                "<br>score_mhz: %{y:.3f}"
                "<br>score: %{customdata[0]:.3f}"
                "<br>timestamp: %{customdata[1]}<extra></extra>"
            ),
        )
    fig.update_layout(
        barmode="group",
        title=None,
        font=dict(family=FONT, color=INK, size=13),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=50, r=20, t=30, b=80),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            title="Configuration",
            tickangle=-45,
            showgrid=False,
            linecolor=GRIDLINE,
            color=INK,
            categoryorder="array",
            categoryarray=name_order,
        ),
        yaxis=dict(
            title="Score (CoreMark/MHz)",
            showgrid=True,
            gridcolor=GRIDLINE,
            gridwidth=1,
            zeroline=False,
            color=INK,
            range=[0, max_score * 1.15] if pd.notna(max_score) else None,
        ),
        bargap=bargap,
    )

    columns = [{"name": "source", "id": "source"}] + [
        {"name": c, "id": c} for c in BASE_COLUMNS
    ]
    return (
        fig,
        columns,
        df.to_dict("records"),
        note,
        meta,
        str(len(df)),
        str(len(skipped)),
        best_val,
        f"Sweep data — showing {len(df)} rows across {len(sources)} source(s)",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
