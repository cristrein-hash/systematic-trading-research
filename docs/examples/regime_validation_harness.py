"""
Regime Validation Harness
=========================

Sanitized public version derived from an internal market-regime
validation harness used in my systematic trading research.

The purpose of this example is to demonstrate:

- causal benchmark construction
- deterministic validation
- precision / recall measurement
- detection-latency analysis
- false-positive measurement
- comparison against a deterministic null baseline
- future-data invariance testing

Private datasets, proprietary strategy parameters, internal paths and
production trading logic have intentionally been removed.

This module is a research example, not a trading strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class RegimeEvent:
    """
    Reference transition used only for evaluation.

    The reference label represents a known transition in the evaluation
    dataset. It must never be exposed to the detector as an input feature.
    """

    index: int
    direction: int  # +1 bullish transition, -1 bearish transition


@dataclass
class ValidationResult:
    """Summary metrics produced by the validation harness."""

    precision: float
    recall: float
    median_latency: float
    signals: int
    false_positives: int


# ---------------------------------------------------------------------
# BASIC INDICATORS
# ---------------------------------------------------------------------


def ema(values: pd.Series, span: int) -> pd.Series:
    """
    Exponential moving average calculated recursively from historical data.

    No future values are required for the value at time t.
    """

    return values.ewm(
        span=span,
        adjust=False,
    ).mean()


# ---------------------------------------------------------------------
# CAUSAL BASELINE DETECTORS
# ---------------------------------------------------------------------


def detect_ma_cross(
    close: pd.Series,
    fast_span: int = 10,
    slow_span: int = 30,
) -> pd.Series:
    """
    Detect moving-average crossovers.

    Returns:
        +1 when the fast EMA crosses above the slow EMA
        -1 when the fast EMA crosses below the slow EMA
         0 otherwise

    Only current and previously calculated values are used.
    """

    fast = ema(close, fast_span)
    slow = ema(close, slow_span)

    previous_difference = (fast - slow).shift(1)
    current_difference = fast - slow

    signal = pd.Series(0, index=close.index, dtype="int8")

    signal.loc[
        (previous_difference <= 0)
        & (current_difference > 0)
    ] = 1

    signal.loc[
        (previous_difference >= 0)
        & (current_difference < 0)
    ] = -1

    return signal


def detect_ema_slope(
    close: pd.Series,
    span: int = 20,
) -> pd.Series:
    """
    Detect changes in the direction of an EMA slope.

    This is a simple causal benchmark rather than a production regime model.
    """

    average = ema(close, span)
    slope = average.diff()

    previous_slope = slope.shift(1)

    signal = pd.Series(0, index=close.index, dtype="int8")

    signal.loc[
        (previous_slope <= 0)
        & (slope > 0)
    ] = 1

    signal.loc[
        (previous_slope >= 0)
        & (slope < 0)
    ] = -1

    return signal


def detect_swing_break(
    close: pd.Series,
    lookback: int = 20,
) -> pd.Series:
    """
    Detect breaks of previously completed price ranges.

    The current observation is excluded from the historical range used
    to define the previous high and low.
    """

    previous_high = (
        close.shift(1)
        .rolling(lookback)
        .max()
    )

    previous_low = (
        close.shift(1)
        .rolling(lookback)
        .min()
    )

    signal = pd.Series(0, index=close.index, dtype="int8")

    signal.loc[close > previous_high] = 1
    signal.loc[close < previous_low] = -1

    return signal


# ---------------------------------------------------------------------
# DETERMINISTIC NULL BASELINE
# ---------------------------------------------------------------------


def deterministic_null(
    length: int,
    probability: float = 0.03,
    seed: int = 17,
) -> np.ndarray:
    """
    Produce a deterministic pseudo-random baseline.

    A fixed seed makes the benchmark reproducible across validation runs.

    The output contains:
        +1 random bullish event
        -1 random bearish event
         0 no event
    """

    rng = np.random.default_rng(seed)

    fire = rng.random(length) < probability
    direction = rng.choice(
        np.array([-1, 1], dtype=np.int8),
        size=length,
    )

    return np.where(
        fire,
        direction,
        0,
    ).astype(np.int8)


# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------


def score_detector(
    signals: pd.Series | np.ndarray,
    events: list[RegimeEvent],
    matching_window: int = 10,
) -> ValidationResult:
    """
    Compare detector outputs with reference regime-transition events.

    Reference events are used strictly for evaluation and never as model
    features.

    A signal is counted as a true positive when:

    1. its direction matches the reference event, and
    2. it occurs from the reference index up to matching_window observations
       later.

    Detection latency measures how many observations elapsed between the
    reference transition and the first matching detector signal.
    """

    signal_array = np.asarray(signals, dtype=np.int8)

    true_positives = 0
    latencies: list[int] = []
    matched_signal_indices: set[int] = set()

    for event in events:
        start = event.index
        stop = min(
            len(signal_array),
            event.index + matching_window + 1,
        )

        matching_indices = [
            i
            for i in range(start, stop)
            if signal_array[i] == event.direction
        ]

        if matching_indices:
            first_match = matching_indices[0]

            true_positives += 1
            latencies.append(first_match - event.index)
            matched_signal_indices.add(first_match)

    fired_indices = np.flatnonzero(signal_array != 0)

    false_positives = sum(
        index not in matched_signal_indices
        for index in fired_indices
    )

    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0.0
    )

    recall = (
        true_positives / len(events)
        if events
        else 0.0
    )

    median_latency = (
        float(np.median(latencies))
        if latencies
        else float("nan")
    )

    return ValidationResult(
        precision=precision,
        recall=recall,
        median_latency=median_latency,
        signals=len(fired_indices),
        false_positives=false_positives,
    )


# ---------------------------------------------------------------------
# FUTURE-DATA INVARIANCE TEST
# ---------------------------------------------------------------------


def future_data_invariance_test(
    close: pd.Series,
    detector: Callable[[pd.Series], pd.Series],
) -> bool:
    """
    Test whether appending an additional future observation changes any
    detector outputs that were already calculated.

    This is intentionally described as a future-data invariance test rather
    than proof that an entire research pipeline is free from look-ahead bias.

    Passing this test demonstrates one useful temporal property:
    future observations do not rewrite the detector's historical outputs.
    """

    original = detector(close)

    future_index = close.index[-1] + pd.Timedelta(hours=4)

    synthetic_future = pd.Series(
        [float(close.iloc[-1]) * 1.50],
        index=[future_index],
    )

    extended_close = pd.concat(
        [close, synthetic_future]
    )

    recalculated = detector(extended_close).iloc[:-1]

    return np.array_equal(
        original.to_numpy(),
        recalculated.to_numpy(),
    )


# ---------------------------------------------------------------------
# EXAMPLE DATA
# ---------------------------------------------------------------------


def build_example_data(
    observations: int = 300,
    seed: int = 42,
) -> pd.Series:
    """
    Build deterministic synthetic price data.

    Synthetic data is used here because the public example is intended to
    demonstrate the validation architecture rather than publish private
    market datasets.
    """

    rng = np.random.default_rng(seed)

    returns = rng.normal(
        loc=0.0002,
        scale=0.006,
        size=observations,
    )

    prices = 2000.0 * np.exp(
        np.cumsum(returns)
    )

    index = pd.date_range(
        "2025-01-01",
        periods=observations,
        freq="4h",
        tz="UTC",
    )

    return pd.Series(
        prices,
        index=index,
        name="close",
    )


def build_example_reference_events(
    close: pd.Series,
) -> list[RegimeEvent]:
    """
    Construct a small synthetic evaluation set.

    IMPORTANT:
    These labels exist only to demonstrate the scoring harness.

    In real research, reference-event construction must be kept separate
    from detector features to prevent target leakage.
    """

    event_locations = [
        (60, 1),
        (125, -1),
        (190, 1),
        (250, -1),
    ]

    return [
        RegimeEvent(index=index, direction=direction)
        for index, direction in event_locations
        if index < len(close)
    ]


# ---------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------


def print_result(
    name: str,
    result: ValidationResult,
) -> None:
    """Print a compact validation summary."""

    print(
        f"{name:<20} "
        f"precision={result.precision:.3f} "
        f"recall={result.recall:.3f} "
        f"median_latency={result.median_latency:.1f} "
        f"signals={result.signals} "
        f"false_positives={result.false_positives}"
    )


# ---------------------------------------------------------------------
# DEMONSTRATION
# ---------------------------------------------------------------------


def main() -> None:
    """
    Run the public demonstration.

    The numbers produced by this script are illustrative and must not be
    interpreted as trading performance.
    """

    close = build_example_data()

    reference_events = build_example_reference_events(
        close
    )

    detectors: dict[
        str,
        Callable[[pd.Series], pd.Series],
    ] = {
        "MA cross": detect_ma_cross,
        "EMA slope": detect_ema_slope,
        "Swing break": detect_swing_break,
    }

    print("REGIME VALIDATION HARNESS")
    print("=" * 72)
    print()

    for name, detector in detectors.items():
        signals = detector(close)

        result = score_detector(
            signals,
            reference_events,
        )

        print_result(
            name,
            result,
        )

        invariant = future_data_invariance_test(
            close,
            detector,
        )

        print(
            f"  future-data invariance: "
            f"{'PASS' if invariant else 'FAIL'}"
        )

        print()

    null_signals = deterministic_null(
        len(close)
    )

    null_result = score_detector(
        null_signals,
        reference_events,
    )

    print_result(
        "Deterministic NULL",
        null_result,
    )


if __name__ == "__main__":
    main()
