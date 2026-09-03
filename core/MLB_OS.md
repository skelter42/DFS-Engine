# MLB DFS Operating System v2

This file converts the MLB strategy brain into a repeatable slate operating process. `sports/mlb.md` remains the strategic doctrine. `config/mlb.json` is the machine-readable operating configuration. `schemas/mlb_slate_state.json` is the required state/output contract.

## Operating Principle

A slate is not a one-shot optimizer run. It is a state machine:

`INTAKE -> INDUSTRY_RESEARCH -> PRELOCK -> FINAL -> POSTSLATE`

The DFS Engine is AI-led. Math, projections, simulations, betting markets, and deterministic code provide evidence and guardrails; they do not mechanically choose the portfolio. AI agents reconcile disagreement, form slate theses, define game scripts, construct the portfolio, and make the final strategic decisions. Code is used for parsing, arithmetic, legality checks, exposure calculation, validation, storage, and reproducibility.

Each state has required inputs, transformations, gates, and outputs. No state may silently skip its gates.

## 1. INTAKE

Required actions:

1. Parse DraftKings entry file and separate true entries from embedded player-pool/reference rows.
2. Partition entries by contest type: single-entry, 5-max, 20-max, 150-max, other.
3. Load baseline projections, projected ownership, and source prebuild exposure separately when available.
4. Normalize player names, teams, positions, salaries, games, batting order placeholders, and pitcher/hitter roles.
5. Record all missing inputs explicitly.

Required output:

- verified entry count
- contest groups
- normalized player pool
- source audit
- initial status = `INTAKE`

Hard failure conditions:

- unknown true entry count
- missing salaries or roster eligibility
- projections cannot be joined reliably to DK player IDs/names

## 2. INDUSTRY RESEARCH

Industry research is mandatory before lineup construction. Sim Savant or any uploaded projection source is a baseline, not the answer.

### 2.1 Required Research Pass

Search the current industry and market for as many of the following as are materially available:

- sportsbook game totals
- implied team run totals
- moneylines
- opening vs current market movement
- pitcher strikeout and other relevant props
- park factors
- weather, wind, temperature, precipitation/delay risk
- confirmed starting pitchers
- confirmed or expected batting orders
- scratches, rest, injuries, pitch-count/role news
- bullpen quality, workload, and availability
- platoon and handedness matchup context
- broader industry hitter/pitcher projections
- broader industry projected ownership
- simulation/win-rate/ceiling information where available

Use multiple independent sources when practical. Do not manufacture consensus when only one source is available.

### 2.2 Industry Consensus Board

Create a structured team/game/player board before the strategic agents proceed. At minimum capture when available:

- source name and timestamp
- opening game total
- current game total
- team implied runs
- market movement
- moneyline
- pitcher K expectation/prop
- park/weather flag
- lineup status
- opposing pitcher and bullpen notes
- baseline/Savant projection
- broader projection range or consensus
- baseline/Savant ownership
- broader ownership range or consensus
- material disagreements
- AI confidence and interpretation note

Every important conclusion should distinguish observed facts from AI interpretation.

### 2.3 Disagreement Logic

The AI must explicitly investigate meaningful disagreement, for example:

- Savant is high on a team while the market is moving against it.
- Savant is low on a team while implied runs or other projections are rising.
- projected ownership is high but the payoff profile is fragile.
- a popular pitcher has strong median projection but weak market/prop/role support.
- lineup-order changes create value that older projections have not captured.

Do not average disagreements away automatically. Determine why sources differ and whether the disagreement creates uncertainty, an edge, or no actionable signal.

### 2.4 Research Completion Gate

A slate may not advance to PRELOCK until the Industry Research Agent has either:

1. completed the material market/industry checks, or
2. explicitly documented which inputs could not be obtained and how that uncertainty will affect portfolio confidence.

Required output:

- industry consensus board
- source list with freshness/timestamps where possible
- major consensus signals
- major disagreements/outliers
- unresolved research gaps
- AI slate-environment summary

## 3. PRELOCK

### 3.1 AI Projection Audit

Reconcile the baseline source against the Industry Consensus Board and current context.

Do not replace the source projection merely because another source disagrees. Record the disagreement and use AI judgment to determine whether it changes confidence, scenario probability, stack attractiveness, pitcher attractiveness, ownership leverage, or exposure.

Fixed scores may be used as summaries and diagnostics, but no composite score mechanically dictates portfolio exposure.

### 3.2 AI Pitcher Analysis

Evaluate every viable pitcher using projection distributions plus current evidence such as:

- ceiling and strikeout path
- opponent contact/K profile
- run prevention environment
- pitch count and role security
- salary
- ownership
- betting/prop support
- weather/park
- leverage created by fading or using the pitcher

Popular pitcher failure paths must be paired with opposing-stack analysis.

### 3.3 AI Stack Architecture

Evaluate viable stacks using the full information set:

- implied runs and market movement
- ceiling and power path
- batting-order connectivity
- platoon matchup
- opposing pitcher failure path
- bullpen path
- park/weather
- salary construction
- individual and full-stack ownership
- connective low-owned value
- likely field combinations and duplication

The objective is not to rank teams by one formula. The AI should identify which stacks are best for which slate stories and why.

### 3.4 Scenario Board

Create 2-8 scenarios depending on contest preset. Every scenario must state:

- trigger
- evidence supporting the scenario
- beneficiaries
- field assumption that fails or holds
- confidence
- recommended portfolio allocation
- stack/pitcher implications
- duplication/ownership implications

Scenario allocations across a contest group must sum to 1.00. Allocations are AI strategic decisions informed by evidence, not formula outputs.

### 3.5 AI Lineup Construction

Construct candidates from scenario constraints rather than from projection alone. Default DK tournament construction strongly prefers a 5-man primary stack when slate size supports it.

The AI Portfolio Builder decides how to combine:

- projection/ceiling
- correlation
- leverage
- game-script coherence
- salary structure
- uniqueness
- portfolio coverage

A material projection sacrifice is allowed only when it buys a named strategic edge.

### 3.6 Contest-Aware Portfolio Selection

Build each contest group separately. Do not clone the same lineup portfolio across SE, 5-max, 20-max, and 150-max.

Portfolio selection must audit concentration by:

- player
- primary stack
- secondary stack
- pitcher
- pitcher pair
- game environment
- scenario
- salary bucket

Different lineups that express the same scenario count as correlated portfolio risk.

### 3.7 Deterministic Validation Layer

After AI constructs the portfolio, code/deterministic checks validate rather than choose strategy:

- DraftKings salary legality
- roster/position legality
- duplicate lineups
- required uniques
- player/team exposure arithmetic
- scenario allocation arithmetic
- contest assignment
- prohibited pitcher-vs-hitter conflicts when applicable
- exposure limits or explicit exceptions

Any failed validation returns the lineup to the AI Portfolio Builder for repair without silently replacing the strategic thesis.

### 3.8 PRELOCK Output

A PRELOCK slate package contains:

- Industry Consensus Board
- major source disagreements and AI interpretations
- scenario board with allocations
- stack theses
- pitcher theses
- candidate/final prelock portfolio by contest group
- projected ownership vs source prebuild exposure vs DFS Engine exposure
- material exposure differences with reasons
- unresolved news/lineup/weather/research gates

PRELOCK is never labeled FINAL.

## 4. FINAL

Run after official lineup/news checks are sufficiently complete.

Mandatory refresh when material changes occur:

1. Industry Research / Market Environment
2. News & Role
3. AI Projection Audit
4. Stack Architecture
5. Pitcher Analysis
6. Scenario Board confidence/allocation
7. Portfolio construction for affected contest groups
8. Deterministic Validation
9. Portfolio Risk Audit
10. Exposure Audit

Finalization gates are defined in `config/mlb.json`. Every gate must be true before status may become `FINAL`.

Required FINAL output:

- upload-ready lineups
- contest assignment
- scenario assignment per lineup
- player/stack/pitcher exposure tables
- Savant/source projected ownership vs source prebuild exposure vs DFS Engine final exposure
- percentage-point differences
- reasons for every material difference
- final risk/concentration summary
- material industry/market evidence behind the final portfolio

## 5. POSTSLATE

### 5.1 Results Ingestion

Join contest results to the saved FINAL slate state. Validate contest field size before calculating top-1%, top-10%, or top-20% tiers.

### 5.2 Error Attribution

Classify portfolio misses using one or more categories:

- primary_stack
- secondary_stack
- pitcher_sp1
- pitcher_sp2
- pitcher_pairing
- lineup_order_news
- industry_research_miss
- market_environment
- ownership_leverage
- duplication_uniqueness
- scenario_allocation
- portfolio_concentration
- projection_error
- variance_no_process_error

Do not assign a structural lesson solely from the winning lineup.

### 5.3 Counterfactual Review

For the highest-value missed lineups, alter one decision at a time and measure whether the result materially changes. Separate a correct thesis with poor implementation from a bad thesis.

Also ask whether the Industry Research Agent correctly identified the material pre-slate signals and whether the AI interpreted them appropriately.

### 5.4 Learning Promotion

New findings begin as slate notes/hypotheses. Promote to `learning/REGISTRY.md` only when they satisfy the durable-learning standard in `core/LEARNING.md`.

## Required Exposure Contract

Every delivered MLB portfolio includes a side-by-side table:

| Player | Source Own% | Source Prebuild% | DFS Engine% | vs Own pp | vs Prebuild pp | Reason |
|---|---:|---:|---:|---:|---:|---|

Source prebuild exposure may be null if unavailable, but source ownership and DFS Engine exposure are required.

## AI Authority Rule

AI judgment is the final authority for MLB tournament portfolio construction. No fixed formula, optimizer rank, or composite score may automatically determine exposure. Quantitative models summarize evidence and enforce consistency; AI agents decide how that evidence changes the slate thesis and portfolio.

All material discretionary decisions must be auditable: record the evidence, interpretation, scenario, and reason for the exposure decision.

## Repeatability Rule

Repeatability means the same evidence and canonical rules should produce materially consistent reasoning, scenarios, and portfolio intent. It does not mean replacing AI judgment with deterministic optimization. Any major change in thesis or exposure should be traceable to changed evidence or an explicitly recorded strategic judgment.

## Calibration Rule

Current weights, caps, and heuristics are starting priors and guardrails, not permanent truths. They must be calibrated using accumulated post-slate data by contest type. Changes require repeated evidence, clear causal evidence, or an explicit experimental flag.