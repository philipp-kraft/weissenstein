#!/usr/bin/env python3
from pathlib import Path

from dash import Dash, dash_table, dcc, html, callback, Output, Input
import plotly.express as px
import pandas as pd

RESULTS_DIR = Path(__file__).parent / "results"
BASE_COLUMNS = ["name", "score", "score_mhz", "timestamp"]


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


sources = sources_by_mtime()

app = Dash()

app.layout = [
    html.H1(children="Cheshire Sweep Results", style={"textAlign": "center"}),
    dcc.Dropdown(sources, sources[0], id="source-dropdown"),
    html.Div(
        id="skipped-note",
        style={"color": "crimson", "textAlign": "center", "margin": "12px 0"},
    ),
    dcc.Interval(id="refresh", interval=3000),
    dcc.Graph(id="graph-content"),
    dash_table.DataTable(
        id="results-table",
        page_size=10,
        sort_action="native",
        style_cell={"textAlign": "left"},
    ),
]


@callback(
    Output("source-dropdown", "options"),
    Output("source-dropdown", "value"),
    Input("refresh", "n_intervals"),
)
def refresh_sources(_n):
    found = sources_by_mtime()
    value = found[0] if found else None
    return found, value


@callback(
    Output("graph-content", "figure"),
    Output("results-table", "columns"),
    Output("results-table", "data"),
    Output("skipped-note", "children"),
    Input("source-dropdown", "value"),
    Input("refresh", "n_intervals"),
)
def update_graph(source, _n):
    if source is None:
        return px.bar(), [], [], ""
    df = load(RESULTS_DIR / source)
    plotted = df[~df["error"]].assign(is_baseline=lambda d: d["name"] == "baseline")
    skipped = df[df["error"]]["name"].tolist()
    note = f"Skipped {len(skipped)} point(s) with error: {', '.join(skipped)}" if skipped else ""
    fig = px.bar(
        plotted,
        x="name",
        y="score_mhz",
        color="is_baseline",
        color_discrete_map={True: "darkorange", False: "steelblue"},
        hover_data={"score": True, "timestamp": True, "is_baseline": False},
        labels={"name": "Sweep point", "score_mhz": "CoreMark/MHz"},
        title=f"CoreMark/MHz Results",
    )
    fig.update_layout(showlegend=False)
    fig.update_layout(xaxis_tickangle=-45)
    columns = [{"name": c, "id": c} for c in BASE_COLUMNS]
    return fig, columns, df.to_dict("records"), note


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
