#!/usr/bin/env python3
import time
from pathlib import Path

from dash import Dash, dash_table, dcc, html, callback, Output, Input, State
import plotly.express as px
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
ORANGE = "#eb6834"
RED = "#d03b3b"
GREEN = "#0ca30c"
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

CARD = {
    "backgroundColor": SURFACE,
    "border": f"1px solid {BORDER}",
    "borderRadius": "10px",
    "padding": "20px 24px",
}


def load(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["error"] = df["error"].astype(str).str.lower() == "true"
    return df


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
                    "Benchmark score for each CVA6 microarchitectural sweep point, "
                    "measured on the Genesys2 FPGA.",
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
                                            "Source",
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
                                            sources[0],
                                            id="source-dropdown",
                                            clearable=False,
                                            style={
                                                "width": "320px",
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
                        stat_tile("stat-baseline", "Baseline Score"),
                    ],
                ),
                html.Div(
                    style={**CARD, "marginBottom": "20px"},
                    children=[
                        html.Div(
                            "Benchmark score by sweep point",
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
                            id="graph-content", config={"displaylogo": False}
                        ),
                        html.P(
                            "Baseline highlighted in orange; points that errored "
                            "during the run are excluded from the chart.",
                            style={
                                "color": MUTED_INK,
                                "fontSize": "12px",
                                "fontStyle": "italic",
                                "margin": "12px 0 0",
                                "borderTop": f"1px solid {GRIDLINE}",
                                "paddingTop": "10px",
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
    value = current if current in found else (found[0] if found else None)
    return found, value


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
    Output("stat-baseline", "children"),
    Output("table-title", "children"),
    Input("source-dropdown", "value"),
    Input("refresh", "n_intervals"),
)
def update_graph(source, _n):
    if source is None:
        return px.bar(), [], [], "", [], "-", "-", "-", "-", "Sweep results"

    df = load(RESULTS_DIR / source)
    plotted = df[~df["error"]].assign(is_baseline=lambda d: d["name"] == "baseline")
    skipped = df[df["error"]]["name"].tolist()
    note = (
        f"Skipped {len(skipped)} point(s) with error: {', '.join(skipped)}"
        if skipped
        else ""
    )

    best_row = plotted.loc[plotted["score_mhz"].idxmax()]
    baseline_rows = plotted[plotted["name"] == "baseline"]
    baseline_val = (
        f"{baseline_rows['score_mhz'].iloc[0]:.3f}" if not baseline_rows.empty else "-"
    )

    mtime = (RESULTS_DIR / source).stat().st_mtime
    meta = [
        badge(f"Last updated: {format_ago(time.time() - mtime)}", dot=GREEN),
    ]

    fig = px.bar(
        plotted,
        x="name",
        y="score_mhz",
        color="is_baseline",
        color_discrete_map={True: ORANGE, False: BLUE},
        hover_data={"score": ":.3f", "timestamp": True, "is_baseline": False},
        labels={"name": "Sweep point", "score_mhz": "Benchmark score"},
    )
    fig.for_each_trace(
        lambda t: t.update(name="Baseline" if t.name == "True" else "Sweep point")
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
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
            tickangle=-45,
            showgrid=False,
            linecolor=GRIDLINE,
            color=INK,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRIDLINE,
            gridwidth=1,
            zeroline=False,
            color=INK,
        ),
        bargap=0.25,
    )

    columns = [{"name": c, "id": c} for c in BASE_COLUMNS]
    return (
        fig,
        columns,
        df.to_dict("records"),
        note,
        meta,
        str(len(df)),
        str(len(skipped)),
        f"{best_row['score_mhz']:.3f}",
        baseline_val,
        f"Sweep data — showing {len(df)} rows",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
