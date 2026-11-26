"""ESIP dashboard. Run from the project root:  python dashboard/app.py  then open http://127.0.0.1:8050"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dash  # noqa: E402
import dash_bootstrap_components as dbc  # noqa: E402
from dash import dcc, html  # noqa: E402

if not (HERE.parent / "data" / "panel.csv").exists():
    sys.exit("No data yet. Run the notebooks first, starting with 01 Data.ipynb")

app = dash.Dash(__name__, use_pages=True, pages_folder=str(HERE / "pages"), assets_folder=str(HERE / "assets"),
                external_stylesheets=[dbc.themes.BOOTSTRAP], title="Africa Environmental Sustainability", suppress_callback_exceptions=True)

sidebar = html.Div([
    html.Div("ESIP", className="brand"),
    html.Div("Africa Environmental Sustainability Intelligence", className="brand-sub"),
    dbc.Nav([dbc.NavLink(p["name"], href=p["relative_path"], active="exact") for p in sorted(dash.page_registry.values(), key=lambda p: p["order"])],
            vertical=True, pills=True),
    html.Div(["Sources: World Bank, Our World in Data, ND-GAIN, UN SDG, FAOSTAT. See each chart's notes.", html.Br(), "Martin B. Mwaala"],
             className="sidebar-foot"),
], className="sidebar")

app.layout = html.Div([dcc.Location(id="url"), sidebar, html.Div(dash.page_container, className="content")])

if __name__ == "__main__":
    app.run(debug=False, port=8050)
