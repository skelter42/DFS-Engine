# MLB DFS Operating System v2

This file converts the MLB strategy brain into a repeatable slate operating process. `sports/mlb.md` remains the strategic doctrine. `config/mlb.json` is the machine-readable operating configuration. `schemas/mlb_slate_state.json` is the required state/output contract.

## Operating Principle

A slate is not a one-shot optimizer run. It is a state machine:

`INTAKE -> INDUSTRY_RESEARCH -> PRELOCK -> FINAL -> POSTSLATE`

The DFS Engine is AI-led. Math, projections, simulations, betting markets, and deterministic code provide evidence and guardrails; they do not mechanically choose the portfolio. AI agents reconcile disagreement, form slate theses, define game scripts, construct the portfolio, and make the final strategic decisions. Code is used for parsing, arithmetic, legality checks, exposure calculation, validation, storage, and reproducibility.

Each state has required inputs, transformations, gates, and outputs. No state may silently skip its gates.

## Sharp-Field Game Theory Assumption

Assume the tournament field is sharp unless evidence suggests otherwise. Opponents generally have access to strong projections, ownership, optimizers, markets, and common DFS strategy. The Engine must therefore seek edge in conditional leverage, correlated construction, ownership interaction, duplication avoidance, first-place path selection, and portfolio allocation rather than assuming the field simply misses obvious high-projection plays.

Chalk is not bad because it is popular. A fade or underweight must have a specific game-theory thesis. Every major contrarian decision should identify what the field believes, why that belief is reasonable, what evidence supports disagreement, and which portion of the field fails if the Engine is right.

Player-level ownership is only one layer. The Engine must also analyze likely ownership at the combination level: pitcher pairs, primary stacks, secondary stacks, value clusters, salary constructions, and repeated game environments.

## Primary Tournament Objective: Bink Coverage

The Engine's tournament objective is not to maximize the median score of the portfolio. It is to maximize the number and quality of distinct first-place paths the portfolio meaningfully owns while avoiding wasteful duplication of the same underlying bet.

A **first-place path** is a coherent combination of conditions that could plausibly produce a tournament-winning lineup. Each path should identify:

- primary offense/stack condition
- secondary offense or one-off condition
- SP1/SP2 condition
- chalk success/failure dependency
- leverage event or field mistake
- salary/roster construction implications
- likely ownership/duplication profile

Examples:

- chalk ace succeeds + chalk offense succeeds + low-owned secondary stack separates
- chalk ace succeeds + premium chalk offense fails + mid-owned stack wins
- popular pitcher fails + opposing 5-man stack breaks slate + alternative SP2 succeeds
- cheap pitcher succeeds + expensive low-owned offense becomes optimal
- two popular high-total games disappoint + overlooked mid-total offense erupts
- same popular primary stack succeeds, but wraparound/secondary-stack branch wins instead of common 1-5 construction

### Meaningful Coverage vs Cosmetic Diversity

Two lineups are not meaningfully different merely because one or two players change. If they depend on the same pitcher pair, same primary stack, same chalk conditions, and same salary structure, they are substantially the same first-place path.

The AI Portfolio Builder must identify **dead overlap**: lineups that appear unique by player count but are highly correlated in what must happen for them to win.

Portfolio diversity should therefore be evaluated at two levels:

1. **Within-path variation** — multiple credible lineup branches that capitalize on one thesis if it hits.
2. **Across-path coverage** — exposure to materially different slate outcomes that do not all fail together.

The Engine should concentrate enough lineups inside strong paths to benefit when a thesis is correct, but not spend most of the portfolio repeatedly purchasing the same outcome unless evidence strongly justifies that concentration.

### Bink Coverage Audit

Before PRELOCK and FINAL portfolio approval, the AI must answer:

- What are the strongest first-place paths on this slate?
- Which paths have zero exposure?
- Which paths are overrepresented relative to evidence and payoff?
- How many lineups are genuinely independent bets versus cosmetic variants?
- Which lineups die together if one pitcher, stack, or game environment fails?
- Does every lineup have a clear reason it improves first-place coverage?
- Are we spreading too thin across weak scenarios, or concentrating too heavily on one fragile assumption?

There is no fixed rule that more paths are always better. Bink Coverage is probability-weighted and payoff-aware. A weak path should not receive a lineup merely to increase a path count. A strong asymmetric path may deserve several coordinated bullets.

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
- broader industry hitter/pitcher projections from multiple independent sources when possible
- broader industry projected ownership from multiple independent sources when possible
- simulation/win-rate/ceiling information where available

Sim Savant must not be treated as the sole projection or ownership truth. Its view can be narrow, stale, model-specific, or materially different from the broader industry. That disagreement can be useful, but only if identified and interpreted.

Use multiple independent sources when practical. Do not manufacture consensus when only one source is available.

### 2.2 Industry Projection and Ownership Consensus

For projections, capture when available:

- Sim Savant projection
- each independent industry projection source
- industry low/high range
- industry median/consensus estimate
- whether Savant sits inside consensus, above it, or below it
- source freshness/timestamp

For ownership, capture when available:

- Sim Savant projected ownership
- each independent industry ownership projection
- industry low/high range
- industry median/consensus estimate
- whether Savant sits inside consensus, above it, or below it
- source freshness/timestamp

Do not blindly average sources. The purpose is to understand the shape of industry opinion, model disagreement, and uncertainty.

If only one external source is available, label the consensus as thin and lower confidence. Never call a one-source comparison an industry consensus.

### 2.3 Industry Consensus Board

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
- individual industry projection values
- broader projection range and median/consensus
- baseline/Savant ownership
- individual industry ownership values
- broader ownership range and median/consensus
- Savant consensus classification: inside / high outlier / low outlier / insufficient data
- material disagreements
- AI confidence and interpretation note

Every important conclusion should distinguish observed facts from AI interpretation.

### 2.4 Disagreement Logic

The AI must explicitly investigate meaningful disagreement, for example:

- Savant is high on a team while the market is moving against it.
- Savant is low on a team while implied runs or other projections are rising.
- Savant ownership differs materially from multiple independent ownership models.
- projected ownership is high but the payoff profile is fragile.
- a popular pitcher has strong median projection but weak market/prop/role support.
- lineup-order changes create value that older projections have not captured.

Do not average disagreements away automatically. Determine why sources differ and whether the disagreement creates uncertainty, an edge, or no actionable signal.

### 2.5 Research Completion Gate

A slate may not advance to PRELOCK until the Industry Research Agent has either:

1. completed the material market/industry checks, including attempts to obtain independent projection and ownership sources, or
2. explicitly documented which inputs could not be obtained and how that uncertainty will affect portfolio confidence.

Required output:

- industry consensus board
- projection source list and freshness
- ownership source list and freshness
- Savant-vs-industry projection comparison
- Savant-vs-industry ownership comparison
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

### 3.4 Scenario and First-Place Path Board

Create 2-8 major scenario families depending on contest preset, then branch each meaningful scenario into distinct first-place paths when different pitcher, secondary-stack, salary, leverage, or duplication conditions materially change how the lineup wins.

Every scenario/path must state:

- trigger
- evidence supporting the scenario
- primary win condition
- secondary win condition
- pitcher condition
- chalk dependency
- leverage event
- beneficiaries
- field assumption that fails or holds
- confidence
- recommended portfolio allocation/bullet count
- stack/pitcher implications
- duplication/ownership implications
- failure linkage to other paths

Scenario allocations across a contest group should reflect AI judgment and can be converted into target lineup counts. Allocations are evidence-informed strategic decisions, not formula outputs.

### 3.5 AI Lineup Construction

Construct candidates from first-place path constraints rather than from projection alone. Default DK tournament construction strongly prefers a 5-man primary stack when slate size supports it.

The AI Portfolio Builder decides how to combine:

- projection/ceiling
- correlation
- leverage
- game-script coherence
- salary structure
- uniqueness
- first-place path fit
- bink coverage contribution

Every lineup must be able to answer: **what has to happen for this lineup to win, and what first-place path does it own that justifies its portfolio slot?**

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
- first-place path
- chalk dependency
- leverage event
- salary bucket

Different lineups that express the same first-place path count as correlated portfolio risk even if several players differ.

The AI should remove or replace redundant lineups when another candidate adds materially more first-place coverage without sacrificing too much quality.

### 3.7 Deterministic Validation Layer

After AI constructs the portfolio, code/deterministic checks validate rather than choose strategy:

- DraftKings salary legality
- roster/position legality
- duplicate lineups
- required uniques
- player/team exposure arithmetic
- scenario/path allocation arithmetic
- contest assignment
- prohibited pitcher-vs-hitter conflicts when applicable
- exposure limits or explicit exceptions

Any failed validation returns the lineup to the AI Portfolio Builder for repair without silently replacing the strategic thesis.

### 3.8 Bink Coverage Review

Before PRELOCK approval, produce a Bink Coverage table containing at minimum:

| Path | Core Win Condition | Pitcher Condition | Chalk Dependency | Leverage Event | Lineups | Portfolio % | Failure Linkage | AI Rationale |
|---|---|---|---|---|---:|---:|---|---|

Also summarize:

- number of meaningful first-place paths owned
- paths intentionally faded and why
- largest dead-overlap cluster
- most fragile shared dependency
- strongest asymmetric leverage path
- whether portfolio concentration is intentional

The point of this audit is not to maximize the raw number of paths. It is to ensure every portfolio slot purchases a credible chance at first place instead of accidentally duplicating an existing thesis.

### 3.9 PRELOCK Output

A PRELOCK slate package contains:

- Industry Consensus Board
- Savant-vs-industry projection comparison
- Savant-vs-industry ownership comparison
- major source disagreements and AI interpretations
- scenario/first-place path board with allocations
- Bink Coverage audit
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
2. Projection and Ownership Consensus
3. News & Role
4. AI Projection Audit
5. Stack Architecture
6. Pitcher Analysis
7. Scenario/First-Place Path Board confidence/allocation
8. Portfolio construction for affected contest groups
9. Deterministic Validation
10. Bink Coverage Audit
11. Portfolio Risk Audit
12. Exposure Audit

Finalization gates are defined in `config/mlb.json`. Every gate must be true before status may become `FINAL`.

Required FINAL output:

- upload-ready lineups
- contest assignment
- scenario and first-place path assignment per lineup
- Bink Coverage table
- player/stack/pitcher exposure tables
- Sim Savant projected ownership
- industry projected-ownership range/consensus when available
- source prebuild exposure
- DFS Engine final exposure
- percentage-point differences and reasons for material differences
- final risk/concentration summary
- material industry/market evidence behind the final portfolio

## 5. POSTSLATE

### 5.1 Results Ingestion

Join contest results to the saved FINAL slate state. Validate contest field size before calculating top-1%, top-10%, or top-20% tiers.

### 5.2 First-Place Path Review

Identify the actual winning/top-1% outcome family and compare it with the pre-slate path board:

- Was the winning path modeled?
- Did we own it?
- If yes, did we allocate enough bullets?
- Did our lineup branches correctly express the path?
- If the path was modeled but our lineups failed, which secondary/pitcher/player choice prevented the bink?
- If the path was not modeled, was the omission a research/interpretation error or ordinary variance?
- Did dead overlap waste portfolio slots that could have covered the winning path?

### 5.3 Error Attribution

Classify portfolio misses using one or more categories:

- primary_stack
- secondary_stack
- pitcher_sp1
- pitcher_sp2
- pitcher_pairing
- lineup_order_news
- industry_research_miss
- projection_consensus_miss
- ownership_consensus_miss
- market_environment
- ownership_leverage
- duplication_uniqueness
- missing_first_place_path
- underallocated_first_place_path
- dead_overlap
- scenario_allocation
- portfolio_concentration
- projection_error
- variance_no_process_error

Do not assign a structural lesson solely from the winning lineup.

### 5.4 Counterfactual Review

For the highest-value missed lineups, alter one decision at a time and measure whether the result materially changes. Separate a correct thesis with poor implementation from a bad thesis.

Also ask whether the Industry Research Agent correctly identified the material pre-slate signals, whether Sim Savant was materially outside industry consensus, and whether the AI interpreted those differences appropriately.

### 5.5 Learning Promotion

New findings begin as slate notes/hypotheses. Promote to `learning/REGISTRY.md` only when they satisfy the durable-learning standard in `core/LEARNING.md`.

## Required Exposure Contract

Every delivered MLB portfolio includes a side-by-side table:

| Player | Savant Own% | Industry Own Range/Consensus | Savant Prebuild% | DFS Engine% | vs Savant pp | vs Industry | Reason |
|---|---:|---:|---:|---:|---:|---|---|

Industry ownership may be null when no independent source is accessible, but the Engine must document the research attempt and confidence limitation. Savant prebuild exposure remains separate from projected ownership.

## AI Authority Rule

AI judgment is the final authority for MLB tournament portfolio construction. No fixed formula, optimizer rank, or composite score may automatically determine exposure. Quantitative models summarize evidence and enforce consistency; AI agents decide how that evidence changes the slate thesis and portfolio.

All material discretionary decisions must be auditable: record the evidence, interpretation, scenario/path, and reason for the exposure decision.

## Repeatability Rule

Repeatability means the same evidence and canonical rules should produce materially consistent reasoning, scenarios, first-place paths, and portfolio intent. It does not mean replacing AI judgment with deterministic optimization. Any major change in thesis or exposure should be traceable to changed evidence or an explicitly recorded strategic judgment.

## Calibration Rule

Current weights, caps, and heuristics are starting priors and guardrails, not permanent truths. They must be calibrated using accumulated post-slate data by contest type. Changes require repeated evidence, clear causal evidence, or an explicit experimental flag.
