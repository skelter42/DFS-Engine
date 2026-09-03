# MLB DFS Operating System v2

This file converts the MLB strategy brain into a repeatable slate operating process. `sports/mlb.md` remains the strategic doctrine. `config/mlb.json` is the machine-readable operating configuration. `schemas/mlb_slate_state.json` is the required state/output contract.

## Operating Principle

A slate is not a one-shot optimizer run. It is a state machine:

`INTAKE -> PRELOCK -> FINAL -> POSTSLATE`

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

## 2. PRELOCK

### 2.1 Projection Audit

Cross-check the baseline source against current context:

- implied team totals / run environment
- opponent quality and handedness
- park
- material weather
- expected or confirmed batting order
- injury/rest/scratch news
- broader industry projection/ownership information when available

Do not replace the source projection merely because another source disagrees. Record the disagreement and use it as an uncertainty/adjustment signal.

### 2.2 Team/Stack Scoring

Score every viable primary stack using `config/mlb.json` stack weights. Each factor is normalized to a common 0-100 scale before weighting.

Required stack factors:

- implied runs
- ceiling
- salary efficiency
- lineup connectivity
- platoon matchup
- park/weather
- bullpen path
- ownership leverage

The score ranks opportunities; it does not mechanically dictate exposure.

### 2.3 Pitcher Scoring

Score every viable pitcher using the configured pitcher weights:

- median projection
- ceiling
- strikeout environment
- run prevention
- salary efficiency
- ownership leverage
- role security

Popular pitcher failure paths must be paired with opposing-stack analysis.

### 2.4 Scenario Board

Create 2-8 scenarios depending on contest preset. Every scenario must state:

- trigger
- beneficiaries
- field assumption that fails or holds
- confidence
- recommended portfolio allocation
- stack/pitcher implications
- duplication/ownership implications

Scenario allocations across a contest group must sum to 1.00.

### 2.5 Candidate Lineup Generation

Generate candidates from scenario constraints rather than from projection alone. Default DK tournament construction strongly prefers a 5-man primary stack.

Candidates are scored on:

- projection
- ceiling
- correlation
- leverage
- scenario fit
- uniqueness

A material projection sacrifice is allowed only when it buys a named strategic edge.

### 2.6 Contest-Aware Portfolio Selection

Build each contest group separately using its MLB preset. Do not clone the same lineup portfolio across SE, 5-max, 20-max, and 150-max.

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

### 2.7 PRELOCK Output

A PRELOCK slate package contains:

- scenario board with allocations
- stack rankings
- pitcher rankings
- candidate/final prelock portfolio by contest group
- projected ownership vs source prebuild exposure vs DFS Engine exposure
- material exposure differences with reasons
- unresolved news/lineup/weather gates

PRELOCK is never labeled FINAL.

## 3. FINAL

Run after official lineup/news checks are sufficiently complete.

Mandatory reruns when material changes occur:

1. News & Role
2. Projection Audit
3. Stack Architecture
4. Scenario Board confidence/allocation
5. Portfolio construction for affected contest groups
6. Portfolio Risk Audit
7. Exposure Audit

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

## 4. POSTSLATE

### 4.1 Results Ingestion

Join contest results to the saved FINAL slate state. Validate contest field size before calculating top-1%, top-10%, or top-20% tiers.

### 4.2 Error Attribution

Classify portfolio misses using one or more categories:

- primary_stack
- secondary_stack
- pitcher_sp1
- pitcher_sp2
- pitcher_pairing
- lineup_order_news
- market_environment
- ownership_leverage
- duplication_uniqueness
- scenario_allocation
- portfolio_concentration
- projection_error
- variance_no_process_error

Do not assign a structural lesson solely from the winning lineup.

### 4.3 Counterfactual Review

For the highest-value missed lineups, alter one decision at a time and measure whether the result materially changes. Separate a correct thesis with poor implementation from a bad thesis.

### 4.4 Learning Promotion

New findings begin as slate notes/hypotheses. Promote to `learning/REGISTRY.md` only when they satisfy the durable-learning standard in `core/LEARNING.md`.

## Required Exposure Contract

Every delivered MLB portfolio includes a side-by-side table:

| Player | Source Own% | Source Prebuild% | DFS Engine% | vs Own pp | vs Prebuild pp | Reason |
|---|---:|---:|---:|---:|---:|---|

Source prebuild exposure may be null if unavailable, but source ownership and DFS Engine exposure are required.

## Repeatability Rule

The same normalized inputs + same configuration + same explicit scenario allocations should produce materially the same portfolio logic. Human/LLM judgment is allowed in scenario definitions and context adjustments, but every discretionary change must be recorded as a named reason rather than hidden inside the optimizer.

## Calibration Rule

All current weights and caps are starting priors, not permanent truths. They must be calibrated using accumulated post-slate data by contest type. Changes to weights/caps require either repeated evidence, clear causal evidence, or an explicit experimental flag.
