"""
Causal Alignment Example
========================

Simplified public example from my systematic trading research methodology.

Purpose:
Demonstrate the difference between a feature's calculation timestamp and
the moment when that feature can safely become available to a historical
decision process.

This is an educational example only. It does not contain proprietary
strategy logic, production parameters or trading signals.
"""

from __future__ import annotations

import pandas as pd


def calculate_market_state(data: pd.DataFrame) -> pd.Series:
    """
    Create a deliberately simple market-state feature.

    This is NOT a trading strategy. The feature exists only to demonstrate
    temporal alignment.

    A state of:
        +1 = positive short-term momentum
        -1 = negative short-term momentum
         0 = insufficient information
    """

    momentum = data["close"].pct_change(3)

    state = pd.Series(0, index=data.index, dtype="int8")
    state.loc[momentum > 0] = 1
    state.loc[momentum < 0] = -1

    return state


def apply_causal_alignment(state: pd.Series) -> pd.Series:
    """
    Shift a close-confirmed state before exposing it to the decision layer.

    If state[t] is only known after bar t has closed, a strategy making its
    next decision should not behave as though that state had been available
    earlier.

    The one-bar shift used here illustrates that principle.
    """

    return state.shift(1)


def build_research_frame(data: pd.DataFrame) -> pd.DataFrame:
    """
    Build a small audit-friendly research table containing both the raw
    calculated state and the causally aligned state.
    """

    frame = data.copy()

    frame["state_calculated"] = calculate_market_state(frame)

    frame["state_available_to_model"] = apply_causal_alignment(
        frame["state_calculated"]
    )

    return frame


def validate_alignment(frame: pd.DataFrame) -> None:
    """
    Verify that the state exposed to the model is exactly the previous
    completed state.

    In a larger research system, temporal-integrity checks can be automated
    so that invalid feature alignment fails validation rather than silently
    entering a backtest.
    """

    expected = frame["state_calculated"].shift(1)

    pd.testing.assert_series_equal(
        frame["state_available_to_model"],
        expected,
        check_names=False,
    )


if __name__ == "__main__":
    example_data = pd.DataFrame(
        {
            "close": [
                2000.0,
                2004.0,
                2002.0,
                2010.0,
                2016.0,
                2012.0,
                2021.0,
                2025.0,
            ]
        },
        index=pd.date_range(
            "2026-01-01",
            periods=8,
            freq="4h",
            tz="UTC",
        ),
    )

    research_frame = build_research_frame(example_data)

    validate_alignment(research_frame)

    print(research_frame)
