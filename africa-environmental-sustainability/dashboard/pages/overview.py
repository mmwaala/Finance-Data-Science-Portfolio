"""Page 1: Environmental sustainability overview."""
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
import dash_bootstrap_components as dbc

import data
from components import TEMPLATE, fmt, kpi

dash.register_page(__name__, path="/", name="Overview", order=1)

HEADLINES = [("A01", "CO2 per capita"), ("B10E", "Renewable share of electricity"), ("B06", "Access to electricity"),
             ("C01", "Forest area share of land"), ("D05", "Water stress"), ("E08", "Red List Index"),
             ("F02", "ND-GAIN vulnerability"), ("F03", "ND-GAIN readiness")]


def _headline(iid, label):
    s = data.series(iid)
    s = s[s["iso3"].isin(data.africa())]
    if s.empty:
        return dbc.Col(kpi(label, "n/a", "not loaded"), md=3)
    last = s.sort_values("year").groupby("iso3").tail(1)
    last = last[last["year"] >= last["year"].max() - 5]
    unit = data.indicators().at[iid, "unit"] if iid in data.indicators().index else ""
    return dbc.Col(kpi(label, fmt(last["value"].median()), f"Africa median, {unit}; {last['iso3'].nunique()} countries, latest {int(last['year'].max())}"), md=3)


def layout():
    o = data.obs()
    o = o[o["iso3"].isin(data.africa()) & o["year"].between(2000, 2024)]
    cov = (o.groupby(["indicator_id", "iso3"])["year"].nunique() / 25 * 100).unstack().reindex(columns=data.africa()).fillna(0)
    heat = px.imshow(cov, aspect="auto", color_continuous_scale="Greys", labels={"color": "% years"},
                     title="Data coverage 2000 to 2024 by indicator and country (% of years observed)")
    heat.update_layout(template=TEMPLATE, height=900, margin={"t": 50})
    children = [html.H3("Environmental Sustainability Overview: Africa", className="page-title"),
                html.P("Headline figures are medians across African countries using each country's latest observed value (within 5 years of the newest). "
                       "No composite index is shown: each dimension is reported on its own measures.", className="text-muted"),
                dbc.Row([_headline(i, l) for i, l in HEADLINES], className="g-2 my-2")]
    cl = data.clusters()
    if len(cl):
        m = px.choropleth(cl.assign(cluster=cl["cluster"].astype(str), country=cl["iso3"].map(data.name)), locations="iso3",
                          color="cluster", scope="africa", hover_name="country", title="Country clusters (k-means on environmental profile, see Comparisons)")
        m.update_layout(template=TEMPLATE, margin={"t": 50, "l": 0, "r": 0, "b": 0})
        children.append(dcc.Graph(figure=m))
    children.append(dcc.Graph(figure=heat))
    return html.Div(children)
