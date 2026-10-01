# Research Architecture

## Overview

My systematic trading research evolved from individual strategy experiments into a broader research environment connecting market data, strategy logic, market-state analysis, external information, validation and automation.

The architecture is designed around one central requirement:

> **Every trading decision must be reproducible using only information that was available at that point in time.**

The public architecture below is intentionally simplified. It describes the research system without exposing proprietary strategy rules, production parameters, credentials or private infrastructure.

---

## High-Level Architecture

```text
                    MARKET DATA
                        │
                        ▼
              ┌───────────────────┐
              │ Data Preparation  │
              │ & Quality Control │
              └─────────┬─────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
      Strategy      Market-State   External
      Research        Engine       Factors
            │           │           │
            └───────────┼───────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Causal Validation │
              │ & Research Tests  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Risk & Trade      │
              │ Qualification     │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Research Output   │
              │ / Candidate Logic │
              └───────────────────┘
```

The components are separated so that a strategy can consume market context without requiring all research logic to exist inside a single trading script.

---

## 1. Market Data Layer

The first layer provides the historical and current market information required by the research environment.

The project has primarily focused on **XAUUSD**, while the broader research framework is designed to support additional instruments.

Typical inputs include:

- OHLC price data
- Volume where operationally available
- Volatility measures
- Momentum indicators
- Market structure
- Multi-timeframe information
- Derived features

Before a feature is used by a model, the research process considers both its calculation and its historical availability.

This distinction is essential because a technically correct historical value can still create look-ahead bias if it was not actually known at the decision time.

---

## 2. Strategy Research Layer

Trading hypotheses are developed as explicit, testable rules.

Different strategy families can investigate different types of market behaviour, such as:

- Trend continuation
- Pullbacks
- Structural breakouts
- Reversals
- Exhaustion
- Liquidity-related behaviour
- Market-state transitions

Each strategy is treated as a research hypothesis rather than as proof of a permanent market edge.

The objective is to determine:

```text
Market Condition
       +
Trading Setup
       +
Risk Definition
       ↓
Measurable Historical Behaviour
```

This makes it possible to compare ideas using consistent research principles.

---

## 3. Market Regime & Turn-State Engine

One of the larger research components is a transversal market-state layer.

Instead of asking every individual strategy to independently determine the broader market environment, the architecture explores a shared engine capable of describing the state available at each historical bar.

Conceptually, the engine can evaluate information such as:

- Broad market regime
- Potential turning state
- Counter-trend movement
- Market-state strength
- Confidence
- Time since a relevant transition
- Detection latency

Simplified:

```text
Historical Market Data
          ↓
   Causal State Engine
          ↓
┌─────────────────────────┐
│ Bull / Range / Bear     │
│ Potential Turn          │
│ Counter-Movement        │
│ Strength / Confidence   │
│ Detection Latency       │
└────────────┬────────────┘
             ↓
      Strategy Context
```

The engine is intended to provide context rather than automatically determine whether a trade should be taken.

Different strategies may respond differently to the same market state.

---

## 4. External Factors Layer

Price behaviour is not the only information investigated by the project.

A separate research layer explores whether external information can provide useful independent context.

The architecture supports research involving sources such as:

- Macroeconomic data
- Economic calendar events
- Central-bank information
- Financial news
- Gold-related information
- Structured event data

Conceptually:

```text
External Sources
      ↓
Data Collection
      ↓
Normalization
      ↓
Timestamp Alignment
      ↓
Structured Event Store
      ↓
Research Features
```

Timestamp alignment is especially important.

An external event should only influence a historical model after the information would realistically have become available.

The purpose of this layer is not to explain every market movement with news.

It is to test whether external information provides evidence that is sufficiently independent and useful to improve market-state or strategy research.

---

## 5. Causal Validation Layer

All major research components eventually pass through causal validation.

This layer asks whether a result survives when future information is removed.

Typical checks include:

- Closed-bar enforcement
- Temporal shifting where required
- Timestamp consistency
- Look-ahead detection
- Feature availability
- Historical reproducibility
- Candidate population verification

The basic principle is:

```text
Feature
   ↓
Was it available at decision time?
   │
   ├── NO ──→ Reject / Correct
   │
   └── YES
        ↓
   Historical Test
        ↓
   Research Evidence
```

This layer is intentionally skeptical.

A strong backtest is not considered sufficient evidence if the information path cannot be explained.

---

## 6. Risk & Trade Qualification

Signal generation and risk construction are treated as related but distinct problems.

Research can therefore evaluate:

- Entry qualification
- Structural invalidation
- Stop placement
- Risk/reward definition
- Market extension
- Exhaustion
- Market-state context
- Trade outcome

This helps distinguish between:

```text
Good Market Idea
        │
        ├── Poor Entry
        ├── Poor Risk Construction
        ├── Wrong Market State
        └── Valid Trade Construction
```

The distinction is useful because a failed trade does not necessarily imply that every component of the underlying hypothesis was wrong.

---

## 7. Research and Production Separation

Experimental research should not automatically become production logic.

The architecture therefore distinguishes between:

```text
EXPERIMENT
    ↓
RESEARCH RESULT
    ↓
CAUSAL VALIDATION
    ↓
ROBUSTNESS REVIEW
    ↓
PRODUCTION CANDIDATE
```

This creates a deliberate barrier between discovering an interesting pattern and trusting it in a live decision-making process.

A research result may remain experimental indefinitely if the evidence is insufficient.

---

## 8. AI and MCP-Assisted Workflow

AI tools are used as part of the development environment rather than as autonomous sources of trading truth.

The project has explored workflows in which AI can interact with structured research tools and market-analysis environments through **Model Context Protocol (MCP)**.

Conceptually:

```text
Researcher
    │
    ▼
AI Assistant
    │
    ▼
MCP / Research Tools
    │
    ├── Market Data
    ├── Research Scripts
    ├── TradingView Workflows
    ├── Validation Tools
    └── Structured Results
    │
    ▼
Human Review + Empirical Validation
```

This architecture can reduce manual research work while preserving an important boundary:

> **AI can assist the research process. It does not replace empirical validation.**

---

## 9. Research Technology

The project currently involves practical work across several technologies and research tools.

### Python

Used for data processing, research scripts, validation, analysis and automation.

### TradingView

Used for market visualization, strategy research and interaction with historical market data.

### Pine Script

Used for indicator and strategy logic inside TradingView.

### Git / GitHub

Used for version control, research organization and documentation.

### APIs and Structured Data

Used for collecting and organizing external market and macroeconomic information.

### MCP

Used experimentally to connect AI-assisted workflows with research tools and structured environments.

---

## 10. Simplified End-to-End Flow

The overall research environment can be summarized as:

                  ┌───────────────┐
                  │  Market Data  │
                  └───────┬───────┘
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
     Strategy Research         Market-State Engine
             │                         │
             └────────────┬────────────┘
                          │
                          │
 External Data ──→ External Factors
                          │
                          ▼
                  Causal Validation
                          │
                          ▼
                 Risk Qualification
                          │
                          ▼
                   Historical Test
                          │
                          ▼
                   Failure Analysis
                          │
                          ▼
                  Robustness Review
                          │
                          ▼
                 Production Candidate
```

This structure continues to evolve as new hypotheses are tested and components are validated.

---

## Design Principles

The architecture is guided by a small set of principles:

1. **Causality before performance**
2. **Source data before derived interpretation**
3. **Explicit rules before retrospective explanations**
4. **Risk defined before outcome**
5. **Failed hypotheses are valid research results**
6. **Research and production should remain separated**
7. **Automation should improve consistency, not hide methodology**
8. **AI assistance should remain subordinate to empirical evidence**

---

## Public vs. Private Research

This public repository documents the architecture and methodology of the project.

The private research environment contains additional implementation details that are intentionally excluded, including:

- Proprietary strategy parameters
- Complete entry and exit logic
- Private research datasets
- API credentials
- Production configuration
- Live execution infrastructure
- Internal strategy evaluation material

This separation allows the portfolio to demonstrate technical and methodological work without publishing sensitive research logic.

---

## Project Direction

The longer-term objective is to develop a modular research environment where multiple strategy families can be evaluated under a common framework for:

- Data integrity
- Market-state context
- Risk
- Causal validation
- External information
- Historical testing
- Automation

Rather than relying on a single strategy or market hypothesis, the architecture is designed to support continued experimentation while maintaining consistent research standards.
