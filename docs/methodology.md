# Research Methodology

## Purpose

This document describes the methodological principles used in my independent systematic trading research.

The objective of the research is not to optimize historical performance or produce impressive backtest statistics. The objective is to determine whether a trading hypothesis remains credible when tested under realistic information constraints.

The central question is:

> **Would this information actually have been available when the trading decision was made?**

This principle influences data preparation, feature construction, signal generation, validation and interpretation of results.

---

## 1. Causal Research

The research follows a causal, time-aware approach.

At every historical decision point, a model should only have access to information that was known at that moment.

This means avoiding the accidental use of:

- Future prices
- Future-confirmed market structure
- Indicators calculated using unavailable future information
- Revised states that would not yet have existed
- Labels derived from subsequent market behaviour
- Retrospective classifications presented as real-time signals

A historically accurate calculation is not necessarily a historically available calculation.

That distinction is fundamental.

---

## 2. Closed-Bar Principle

Most strategy research is based on **closed bars**.

A signal associated with a historical bar is evaluated using information confirmed by the relevant decision point rather than information that developed later.

This helps create a clear separation between:

```text
Information available now
        ↓
Decision
        ↓
Future market behaviour
        ↓
Outcome
```

The outcome may be used to evaluate the decision.

It must not be allowed to influence the decision itself.

---

## 3. SHIFT1 and Temporal Alignment

Some indicators or market-state variables require explicit temporal shifting before they can safely be used by a strategy.

In these cases I use a principle I refer to internally as **SHIFT1**.

Conceptually:

```text
State calculated from completed information
                ↓
Shift forward one decision step
                ↓
State becomes available to the strategy
```

This prevents a model from using information from a bar before that information would actually have been confirmed.

The exact implementation depends on the feature and timeframe.

The broader principle is always the same:

> **Availability time matters as much as calculation time.**

---

## 4. Look-Ahead Bias

One of the most important lessons from this project has been understanding how dramatically look-ahead bias can distort research.

A strategy can appear extremely successful while unknowingly using information from the future.

Removing that information can materially change:

- Win rate
- Trade selection
- Market-state classification
- Entry timing
- Drawdown
- Expected return
- Overall strategy viability

For this reason, unusually strong historical results are treated as something to investigate rather than automatically celebrate.

A strong result should survive an information-integrity audit.

---

## 5. Source-First Data Validation

Whenever possible, the research follows a **source-first** approach.

Before trusting a derived feature, I try to establish:

1. Where the original data came from
2. When that information became available
3. How the feature was calculated
4. Whether transformations introduced future information
5. Whether the same calculation can be reproduced
6. Whether missing or revised data affects the result

The intended chain is:

```text
Source Data
    ↓
Transformation
    ↓
Feature
    ↓
Trading Rule
    ↓
Signal
    ↓
Outcome
```

Each stage should be explainable.

---

## 6. Hypothesis Before Optimization

The preferred research sequence is:

```text
Observation
    ↓
Hypothesis
    ↓
Explicit Rule
    ↓
Historical Test
    ↓
Failure Analysis
    ↓
Refinement
```

Rather than repeatedly searching historical data for combinations that maximize performance, I try to begin with a market hypothesis that can be expressed as an explicit rule.

Examples of research questions include:

- Does a specific market condition improve continuation probability?
- Does a particular regime make a setup structurally weaker?
- Can exhaustion conditions identify poor entries?
- Can external information improve regime-transition detection?
- How quickly can a market-state model identify a genuine transition?

The purpose of the test is to challenge the hypothesis, not confirm it.

---

## 7. Failure Analysis

Losing trades and failed models are treated as research data.

Instead of only asking:

> Why did the winning trades work?

I also investigate:

> What systematically distinguishes failed trades from successful ones?

This can involve examining:

- Market regime
- Trend context
- Volatility
- Momentum
- Price structure
- Extension
- Exhaustion
- Liquidity behaviour
- Entry location
- Structural risk
- Market path before entry
- External market conditions

The goal is to identify repeatable distinctions without creating rules that merely explain the past.

---

## 8. Market-State Research

Individual trade signals are not evaluated in isolation.

A significant part of the project investigates the **state of the market surrounding a potential trade**.

Research includes concepts such as:

- Bull regimes
- Bear regimes
- Range conditions
- Trend continuation
- Counter-trend movement
- Potential turning states
- Market-state strength
- Transition latency

The objective is to determine whether the same trading setup behaves differently under different structural environments.

---

## 9. Latency Matters

A market regime model can look excellent historically if it identifies turning points retrospectively.

That is not sufficient.

A practical system must also answer:

> **How long after the actual market transition could the model realistically identify it?**

For this reason, regime research evaluates detection latency as well as classification quality.

This creates a trade-off between:

```text
Earlier Detection
        ↕
Higher False-Positive Risk
        ↕
Later but More Confirmed Detection
```

The appropriate balance depends on how the state will be used by the trading system.

---

## 10. Risk Before Outcome

Risk should be defined before the trade outcome is known.

Research therefore attempts to separate:

- Entry logic
- Invalidation logic
- Stop placement
- Position risk
- Target logic
- Outcome measurement

This prevents successful outcomes from retrospectively justifying weak trade construction.

The project has explored structural stop placement and predefined risk/reward frameworks rather than evaluating trades solely by whether price eventually moved in the expected direction.

---

## 11. Research, Validation and Production

I try to maintain a conceptual separation between three stages:

### Research

Explore hypotheses, features and market behaviour.

### Validation

Test whether the evidence survives causal and historical scrutiny.

### Production

Only use logic that has passed the required validation process.

Conceptually:

```text
RESEARCH
   ↓
Candidate Hypothesis
   ↓
VALIDATION
   ↓
Causal Evidence
   ↓
PRODUCTION CANDIDATE
```

Not every interesting research result becomes a trading rule.

---

## 12. Out-of-Sample Thinking

Whenever practical, research should distinguish between data used to develop an idea and data used to evaluate it independently.

The general objective is to avoid repeatedly adapting rules to the same historical observations.

Possible approaches include:

- Historical holdout periods
- Forward validation
- Different market regimes
- Different instruments
- Unseen future data

Out-of-sample testing does not guarantee that a strategy will work in the future.

It provides another barrier against overfitting.

---

## 13. Reproducibility

A useful research result should be reproducible.

Where possible, the project uses:

- Explicit rules
- Structured datasets
- Automated scripts
- Version-controlled code
- Consistent historical timestamps
- Defined evaluation metrics
- Repeatable research workflows

This reduces dependence on subjective memory and makes it easier to identify when a result changes because the methodology changed.

---

## 14. AI-Assisted Research

AI tools are used extensively as development and research assistants.

They can help with:

- Code development
- Research organization
- Data-processing workflows
- Hypothesis generation
- Debugging
- Documentation
- Comparative analysis
- Automation

However, AI-generated reasoning is not treated as market evidence.

The intended relationship is:

```text
Human Research Question
        ↓
AI-Assisted Development
        ↓
Explicit Testable Rule
        ↓
Historical Data
        ↓
Validation
        ↓
Human Interpretation
```

The evidence must come from the data and methodology rather than from the confidence of an AI-generated explanation.

---

## 15. Research Integrity

The most important principle developed during this project is simple:

> **A weaker result produced by a valid methodology is more valuable than an exceptional result produced by invalid information.**

Finding that a strategy does not work is useful.

Finding that a feature contains look-ahead bias is useful.

Finding that an attractive hypothesis does not survive validation is useful.

Each of these outcomes improves the research process.

The goal is therefore not to protect a trading idea.

The goal is to discover whether the evidence supports it.

---

## Scope of This Public Repository

This repository documents selected methodology, architecture and sanitized examples from the research project.

It intentionally does **not** publish:

- Complete proprietary trading strategies
- Exact production parameters
- Private datasets
- Credentials or API keys
- Live trading infrastructure
- Private research archives

The purpose of the repository is to demonstrate the research process and technical learning behind the project while maintaining an appropriate boundary between public documentation and private research.
