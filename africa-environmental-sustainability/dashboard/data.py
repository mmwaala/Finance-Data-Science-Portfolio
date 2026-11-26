"""Data access for the dashboard. Reads the CSVs that the notebooks write to data/."""
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

DEFAULT_COUNTRIES = ["ZMB", "ZAF", "NGA", "KEN", "EGY"]


@lru_cache
def obs() -> pd.DataFrame:
    return pd.read_csv(DATA / "observations.csv")


@lru_cache
def indicators() -> pd.DataFrame:
    d = pd.read_csv(DATA / "indicators.csv").set_index("indicator_id")
    d["polarity"] = pd.to_numeric(d["polarity"], errors="coerce").fillna(0).astype(int)
    for c in ("definition", "key_limitations", "licence", "source", "unit", "role"):
        d[c] = d[c].fillna("") if c in d else ""
    d["observed_or_model"] = d["source"].map(lambda s: "composite index" if "ND-GAIN" in s else "derived" if s.startswith("Derived") else "published estimate")
    return d


@lru_cache
def countries() -> pd.DataFrame:
    c = pd.read_csv(DATA / "countries.csv").set_index("iso3")
    c["in_africa_scope"] = c["group"] == "Africa"
    c["au_region"] = c["au_region"].fillna("")
    return c


@lru_cache
def panel() -> pd.DataFrame:
    p = pd.read_csv(DATA / "panel.csv")
    c = pd.read_csv(DATA / "countries.csv")
    p["in_africa_scope"] = p["iso3"].isin(c.loc[c["group"] == "Africa", "iso3"])
    return p


@lru_cache
def forecasts() -> pd.DataFrame:
    p = DATA / "forecasts.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame(columns=["iso3", "indicator_id", "year", "value", "lower_80", "upper_80"])


@lru_cache
def clusters() -> pd.DataFrame:
    p = DATA / "clusters.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame(columns=["iso3", "cluster"])


def series(indicator_id: str) -> pd.DataFrame:
    """Observed values for one indicator, including derived X series from the panel."""
    o = obs()
    s = o[o["indicator_id"] == indicator_id][["iso3", "year", "value"]]
    if s.empty and indicator_id in panel():
        s = panel()[["iso3", "year", indicator_id]].dropna().rename(columns={indicator_id: "value"})
    return s


def africa() -> list[str]:
    c = countries()
    return c.index[c["in_africa_scope"]].tolist()


def name(iso3: str) -> str:
    c = countries()
    return c.at[iso3, "country_name"] if iso3 in c.index and isinstance(c.at[iso3, "country_name"], str) else iso3


def options_for(dim_letter: str) -> list[dict]:
    ind = indicators()
    have = set(obs()["indicator_id"]) | {c for c in panel().columns if c.startswith("X")}
    sel = ind[ind.index.str.startswith(dim_letter) | ((ind["role"] == "Derived") & ind["dimension"].astype(str).str.startswith(dim_letter))]
    return [{"label": f"{i}  {r['indicator_name']}", "value": i} for i, r in sel.iterrows() if i in have]
