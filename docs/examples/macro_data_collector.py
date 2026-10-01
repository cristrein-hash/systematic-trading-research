"""
Public Macroeconomic Data Collector
===================================

Sanitized public example derived from an internal external-factors
research pipeline.

This example demonstrates:

- ingestion of public macroeconomic time series
- deterministic data transformation
- year-over-year calculations
- explicit modelling of information availability
- structured output for downstream research

Private factor registries, production paths, proprietary feature
definitions and strategy logic have intentionally been removed.

Important:
The availability timestamp used below is an illustrative research proxy.
It is NOT equivalent to a true point-in-time economic-data vintage.
Production-grade historical research should use actual release/vintage
data when available.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

import pandas as pd
import requests


FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


@dataclass(frozen=True)
class MacroSeries:
    """Configuration for one public macroeconomic series."""

    series_id: str
    transform: str = "level"
    availability_lag_days: int = 0


def fetch_fred_series(
    series_id: str,
    start_date: str = "2019-01-01",
) -> pd.DataFrame:
    """
    Download a public FRED series through the CSV endpoint.

    No API key is required for this public endpoint.
    """

    response = requests.get(
        FRED_CSV_URL,
        params={
            "id": series_id,
            "cosd": start_date,
        },
        timeout=30,
    )

    response.raise_for_status()

    frame = pd.read_csv(
        StringIO(response.text)
    )

    frame.columns = [
        "observation_date",
        "value",
    ]

    frame["observation_date"] = pd.to_datetime(
        frame["observation_date"],
        utc=True,
    )

    frame["value"] = pd.to_numeric(
        frame["value"],
        errors="coerce",
    )

    return (
        frame
        .dropna(subset=["value"])
        .sort_values("observation_date")
        .reset_index(drop=True)
    )


def apply_transform(
    frame: pd.DataFrame,
    transform: str,
) -> pd.DataFrame:
    """
    Apply a transparent transformation to the raw series.

    Supported public-example transformations:

    level
        Keep the original value.

    yoy_pct
        Percentage change from 12 observations earlier. This example
        assumes a monthly series when yoy_pct is selected.
    """

    result = frame.copy()

    if transform == "level":
        return result

    if transform == "yoy_pct":
        result["value"] = (
            result["value"]
            .pct_change(periods=12)
            .mul(100)
        )

        return (
            result
            .dropna(subset=["value"])
            .reset_index(drop=True)
        )

    raise ValueError(
        f"Unsupported transform: {transform}"
    )


def add_information_availability(
    frame: pd.DataFrame,
    lag_days: int,
) -> pd.DataFrame:
    """
    Add an illustrative information-availability timestamp.

    The purpose is to make temporal assumptions explicit.

    WARNING:
    observation_date + fixed lag is only a proxy. It must not be
    represented as the true historical release timestamp or vintage.
    """

    result = frame.copy()

    result["available_at"] = (
        result["observation_date"]
        + pd.to_timedelta(
            lag_days,
            unit="D",
        )
    )

    return result


def build_macro_panel(
    series_config: list[MacroSeries],
    start_date: str = "2019-01-01",
) -> pd.DataFrame:
    """
    Build a normalized macroeconomic research panel.
    """

    panel: list[pd.DataFrame] = []

    for config in series_config:

        frame = fetch_fred_series(
            config.series_id,
            start_date=start_date,
        )

        frame = apply_transform(
            frame,
            config.transform,
        )

        frame = add_information_availability(
            frame,
            config.availability_lag_days,
        )

        frame["series_id"] = config.series_id

        panel.append(frame)

    if not panel:
        return pd.DataFrame()

    result = pd.concat(
        panel,
        ignore_index=True,
    )

    return result[
        [
            "series_id",
            "observation_date",
            "available_at",
            "value",
        ]
    ].sort_values(
        [
            "series_id",
            "observation_date",
        ]
    )


def main() -> None:
    """
    Demonstrate the collector with public FRED series.

    The selected series are illustrative and do not represent a
    trading model or investment recommendation.
    """

    series = [
        MacroSeries(
            series_id="CPIAUCSL",
            transform="yoy_pct",
            availability_lag_days=15,
        ),
        MacroSeries(
            series_id="UNRATE",
            transform="level",
            availability_lag_days=7,
        ),
    ]

    panel = build_macro_panel(series)

    print(panel.tail(10).to_string(index=False))


if __name__ == "__main__":
    main()
