"""Reusable layout pieces and the standard dimension page (filters, KPI cards, trend, ranking, map)."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc

import data

GREY = "#6c757d"
TEMPLATE = "plotly_white"


def kpi(title, value, sub=""):
    return dbc.Card(dbc.CardBody([html.Div(title, className="kpi-title"), html.Div(value, className="kpi-value"),
                                  html.Div(sub, className="kpi-sub")]), className="kpi-card")


def fmt(v):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "n/a"
    return f"{v:,.0f}" if abs(v) >= 1000 else f"{v:,.2f}"


def info_block(iid):
    ind = data.indicators()
    if iid not in ind.index:
        return ""
    r = ind.loc[iid]
    return html.Div([
        html.B(r["indicator_name"]), html.Span(f"  |  Unit: {r['unit']}  |  Source: {r['source']}  |  Type: {r.get('observed_or_model', '')}"),
        html.Div(f"Definition: {(r.get('definition') or '')[:600]}", className="small"),
        html.Div(f"Limitations: {r.get('key_limitations', '')}", className="small text-muted"),
        html.Div(f"Licence: {r.get('licence', '')}", className="small text-muted"),
    ], className="info-block")


def filters(prefix, dim_letter, default=None):
    opts = data.options_for(dim_letter)
    regions = sorted(r for r in data.countries()["au_region"].dropna().unique() if r)
    comps = [{"label": data.name(c), "value": c} for c in data.countries().index if c not in data.africa()]
    africa_opts = [{"label": data.name(c), "value": c} for c in sorted(data.africa(), key=data.name)]
    return dbc.Row([
        dbc.Col([html.Label("Indicator"), dcc.Dropdown(opts, default if default in [o["value"] for o in opts] else (opts[0]["value"] if opts else None), id=f"{prefix}-ind", clearable=False)], md=4),
        dbc.Col([html.Label("AU region"), dcc.Dropdown(regions, regions, id=f"{prefix}-reg", multi=True)], md=2),
        dbc.Col([html.Label("Countries (trend)"), dcc.Dropdown(africa_opts, [c for c in data.DEFAULT_COUNTRIES if c in data.africa()], id=f"{prefix}-ctry", multi=True)], md=3),
        dbc.Col([html.Label("Comparator"), dcc.Dropdown(comps, "WLD" if "WLD" in data.countries().index else None, id=f"{prefix}-cmp")], md=1),
        dbc.Col([html.Label("Years"), dcc.RangeSlider(1990, 2030, 1, value=[2000, 2030], id=f"{prefix}-yrs",
                                                      marks={y: str(y) for y in range(1990, 2031, 10)})], md=2),
    ], className="filter-bar g-2")


def dimension_page(prefix, dim_letter, title, default=None):
    layout = html.Div([
        html.H3(title, className="page-title"),
        filters(prefix, dim_letter, default),
        dbc.Row(id=f"{prefix}-kpis", className="g-2 my-2"),
        dbc.Row([dbc.Col(dcc.Graph(id=f"{prefix}-trend"), md=7), dbc.Col(dcc.Graph(id=f"{prefix}-map"), md=5)], className="g-2"),
        dbc.Row([dbc.Col(dcc.Graph(id=f"{prefix}-rank"), md=12)], className="g-2"),
        html.Div(id=f"{prefix}-cov", className="coverage-note"),
        html.Div(id=f"{prefix}-info"),
    ])

    @callback(Output(f"{prefix}-kpis", "children"), Output(f"{prefix}-trend", "figure"), Output(f"{prefix}-map", "figure"),
              Output(f"{prefix}-rank", "figure"), Output(f"{prefix}-cov", "children"), Output(f"{prefix}-info", "children"),
              Input(f"{prefix}-ind", "value"), Input(f"{prefix}-reg", "value"), Input(f"{prefix}-ctry", "value"),
              Input(f"{prefix}-cmp", "value"), Input(f"{prefix}-yrs", "value"), Input(f"{prefix}-map", "clickData"))
    def update(iid, regions, ctrys, cmp, yrs, click):
        return render(iid, regions or [], ctrys or [], cmp, yrs, click)

    return layout


def render(iid, regions, ctrys, cmp, yrs, click=None):
    empty = go.Figure(layout={"template": TEMPLATE, "annotations": [{"text": "No data for this selection", "showarrow": False}]})
    if not iid:
        return [], empty, empty, empty, "", ""
    ind = data.indicators()
    meta = ind.loc[iid] if iid in ind.index else {}
    unit, nm = meta.get("unit", ""), meta.get("indicator_name", iid)
    s = data.series(iid)
    af = data.africa()
    cdim = data.countries()
    in_reg = [c for c in af if cdim.at[c, "au_region"] in regions]
    if click and click.get("points"):                     # cross-filter: clicking the map adds the country to the trend
        c = click["points"][0].get("location")
        if c and c not in ctrys:
            ctrys = ctrys + [c]
    s_obs = s[s["year"].between(yrs[0], yrs[1])]
    s_af = s_obs[s_obs["iso3"].isin(in_reg)]
    if s_af.empty:
        return [], empty, empty, empty, "No observations for this indicator, region and period.", info_block(iid)
    last = s_af.sort_values("year").groupby("iso3").tail(1)
    last = last[last["year"] >= last["year"].max() - 5]
    base = s_af[s_af["year"].between(2000, 2002)].groupby("iso3")["value"].mean()
    chg = (last.set_index("iso3")["value"] - base).dropna()
    pol = int(meta.get("polarity", 0) or 0)

    kpis = [dbc.Col(kpi("Africa median, latest", fmt(last["value"].median()), f"{unit}"), md=3),
            dbc.Col(kpi("Countries with data", f"{last['iso3'].nunique()} of {len(in_reg)}", f"latest year {int(last['year'].max())}"), md=3),
            dbc.Col(kpi("Median change since 2000 to 2002", fmt(chg.median()) if len(chg) else "n/a", f"{len(chg)} countries with a base"), md=3)]
    if ctrys:
        c0 = ctrys[0]
        v = last.loc[last["iso3"] == c0]
        rank = last["value"].rank(ascending=(pol == -1), method="min")
        r_txt = f"rank {int(rank[v.index[0]])} of {len(last)} ({'1 = best' if pol else '1 = highest'})" if len(v) else "no recent value"
        kpis.append(dbc.Col(kpi(f"{data.name(c0)}, latest", fmt(v["value"].iloc[0]) if len(v) else "n/a", r_txt), md=3))

    trend = go.Figure()
    for c in ctrys:
        t = s_obs[s_obs["iso3"] == c].sort_values("year")
        trend.add_trace(go.Scatter(x=t["year"], y=t["value"], mode="lines+markers", name=data.name(c), connectgaps=False))
        f = data.forecasts()
        f = f[(f["iso3"] == c) & (f["indicator_id"] == iid) & f["year"].between(yrs[0], yrs[1])]
        if len(f):
            trend.add_trace(go.Scatter(x=list(f["year"]) + list(f["year"][::-1]), y=list(f["upper_80"]) + list(f["lower_80"][::-1]),
                                       fill="toself", opacity=0.15, line={"width": 0}, showlegend=False, hoverinfo="skip"))
            trend.add_trace(go.Scatter(x=f["year"], y=f["value"], mode="lines", line={"dash": "dash"}, name=f"{data.name(c)} forecast"))
    med = s_af.groupby("year")["value"].median()
    trend.add_trace(go.Scatter(x=med.index, y=med.values, name="Africa median (selected regions)", line={"color": GREY, "dash": "dot"}))
    if cmp:
        t = s_obs[s_obs["iso3"] == cmp].sort_values("year")
        if len(t):
            trend.add_trace(go.Scatter(x=t["year"], y=t["value"], name=data.name(cmp), line={"color": "black", "dash": "dot"}))
    trend.update_layout(template=TEMPLATE, title=f"{nm}: trend (gaps are missing data, dashed = forecast)", yaxis_title=unit,
                        legend={"orientation": "h", "y": -0.2}, margin={"t": 50, "l": 10, "r": 10})

    mp = px.choropleth(last, locations="iso3", color="value", scope="africa", hover_name=last["iso3"].map(data.name),
                       hover_data={"year": True, "iso3": False}, color_continuous_scale="RdYlGn" if pol == 1 else ("RdYlGn_r" if pol == -1 else "Viridis"))
    mp.update_layout(template=TEMPLATE, title="Latest value (click a country to add it to the trend)", margin={"t": 50, "l": 0, "r": 0, "b": 0},
                     coloraxis_colorbar={"title": ""})

    rk = last.assign(country=last["iso3"].map(data.name)).sort_values("value")
    bar = px.bar(rk, x="value", y="country", orientation="h", hover_data=["year"], labels={"value": unit, "country": ""})
    bar.update_layout(template=TEMPLATE, height=max(350, 18 * len(rk)), margin={"t": 50, "l": 10, "r": 10},
                      title=f"Ranking, latest available year ({'higher is better' if pol == 1 else 'higher is worse' if pol == -1 else 'neutral indicator'})")

    stale = s_af.groupby("iso3")["year"].max()
    cov = (f"Coverage: {s_af['iso3'].nunique()} of {len(in_reg)} countries have data in {yrs[0]} to {yrs[1]}; "
           f"{int((stale < stale.max() - 5).sum())} countries' latest value is more than 5 years older than the newest and are left out of the ranking and map. "
           "Missing values are shown as gaps, never as zero.")
    return kpis, trend, mp, bar, cov, info_block(iid)
