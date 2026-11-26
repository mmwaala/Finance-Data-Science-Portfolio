"""Page 8: African country comparisons: country profile, relationship explorer and clusters."""
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dash_table, dcc, html
import dash_bootstrap_components as dbc

import data
from components import TEMPLATE

dash.register_page(__name__, path="/comparisons", name="African Country Comparisons", order=8)

PROFILE = ["A01", "X01", "B10E", "B06", "B08", "C01", "X02", "D05", "D11", "E08", "F01", "F02", "F03", "G02", "G07"]


def _opts():
    ind = data.indicators()
    cols = [c for c in data.panel().columns if c in ind.index]
    return [{"label": f"{c}  {ind.at[c, 'indicator_name']}", "value": c} for c in cols]


def layout():
    af = sorted(data.africa(), key=data.name)
    opts = _opts()
    vals = [o["value"] for o in opts]
    return html.Div([
        html.H3("African Country Comparisons", className="page-title"),
        dbc.Row([dbc.Col([html.Label("Country profile"), dcc.Dropdown([{"label": data.name(c), "value": c} for c in af], "ZMB" if "ZMB" in af else af[0], id="cmp-country")], md=4)]),
        html.Div(id="cmp-profile", className="my-2"),
        html.H5("Relationship explorer (country averages over the window; association only)"),
        dbc.Row([dbc.Col(dcc.Dropdown(opts, "G02" if "G02" in vals else vals[0], id="cmp-x"), md=4),
                 dbc.Col(dcc.Dropdown(opts, "A01" if "A01" in vals else vals[-1], id="cmp-y"), md=4),
                 dbc.Col(dcc.RangeSlider(2000, 2024, 1, value=[2015, 2022], id="cmp-win", marks={y: str(y) for y in range(2000, 2025, 4)}), md=4)]),
        dbc.Row([dbc.Col(dcc.Checklist([{"label": " log x", "value": "lx"}, {"label": " log y", "value": "ly"}], [], id="cmp-log", inline=True), md=4)]),
        dcc.Graph(id="cmp-scatter"),
        html.Div(id="cmp-clusters"),
    ])


@callback(Output("cmp-profile", "children"), Input("cmp-country", "value"))
def profile(iso):
    ind = data.indicators()
    rows = []
    for i in PROFILE:
        s = data.series(i)
        s = s[s["iso3"].isin(data.africa())]
        if s.empty:
            continue
        last = s.sort_values("year").groupby("iso3").tail(1)
        last = last[last["year"] >= last["year"].max() - 5]
        pol = int(ind.at[i, "polarity"]) if i in ind.index else 0
        me = last[last["iso3"] == iso]
        rank = last["value"].rank(ascending=(pol == -1), method="min")
        rows.append({"Indicator": f"{i} {ind.at[i, 'indicator_name'] if i in ind.index else i}", "Unit": ind.at[i, "unit"] if i in ind.index else "",
                     "Value": round(float(me["value"].iloc[0]), 2) if len(me) else None, "Year": int(me["year"].iloc[0]) if len(me) else None,
                     "Africa median": round(float(last["value"].median()), 2),
                     "Rank": f"{int(rank[me.index[0]])} of {len(last)}" if len(me) else "no recent data",
                     "Rank basis": "1 = best" if pol else "1 = highest"})
    return dash_table.DataTable(rows, style_cell={"fontFamily": "inherit", "fontSize": 12, "textAlign": "left"},
                                style_header={"fontWeight": "bold"}, style_as_list_view=True)


@callback(Output("cmp-scatter", "figure"), Output("cmp-clusters", "children"),
          Input("cmp-x", "value"), Input("cmp-y", "value"), Input("cmp-win", "value"), Input("cmp-log", "value"))
def scatter(x, y, win, logs):
    p = data.panel()
    p = p[(p["in_africa_scope"] == True) & p["year"].between(*win)]
    if x not in p or y not in p:
        return px.scatter(title="Select indicators"), ""
    avg = p.groupby(["iso3", "au_region"])[[x, y]].mean().dropna().reset_index()
    cl = data.clusters()
    if len(cl):
        avg = avg.merge(cl[["iso3", "cluster"]], on="iso3", how="left")
        avg["cluster"] = avg["cluster"].astype("Int64").astype(str)
    color = "cluster" if "cluster" in avg else "au_region"
    ind = data.indicators()
    fig = px.scatter(avg, x=x, y=y, color=color, hover_name=avg["iso3"].map(data.name), text="iso3",
                     log_x="lx" in (logs or []), log_y="ly" in (logs or []),
                     labels={x: ind.at[x, "indicator_name"] if x in ind.index else x, y: ind.at[y, "indicator_name"] if y in ind.index else y})
    rho = avg[[x, y]].corr(method="spearman").iloc[0, 1] if len(avg) > 3 else np.nan
    fig.update_traces(textposition="top center", marker={"size": 10})
    fig.update_layout(template=TEMPLATE, height=600, title=f"{len(avg)} countries; Spearman rho = {rho:.2f} (association, not causation)")
    note = ""
    if len(cl):
        d = cl.assign(country=cl["iso3"].map(data.name)).groupby("cluster")["country"].agg(lambda s: ", ".join(sorted(s))).reset_index()
        d.columns = ["Cluster", "Members"]
        note = html.Div([html.H5("Clusters (k-means on PCA of standardised country averages; see notebook 09)"),
                         dash_table.DataTable(d.to_dict("records"), style_cell={"fontSize": 12, "textAlign": "left", "whiteSpace": "normal"},
                                              style_header={"fontWeight": "bold"})])
    return fig, note
