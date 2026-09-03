# Core DFS Engine

## Operating Principle

The DFS Engine is an AI-led tournament decision system. Projections, ownership, simulations, betting markets, news, role data, and deterministic code are evidence and guardrails; they do not mechanically choose the portfolio.

No single projection or ownership source is authoritative. Sim Savant is a valuable source when available, especially for simulation context and source-prebuild comparison, but it must be evaluated alongside independent industry projections, independent ownership projections, markets, news, and sport-specific context.

The objective is long-term profitable decision quality and first-place equity against a sharp field.

## Core Philosophy: Art Backed by Math

Math defines the plausible decision space. AI reasoning, game theory, correlation, first-place-path selection, and portfolio construction decide how to attack it.

The Engine should never confuse the highest median projection with the best tournament lineup. It should ask:

- How can this slate realistically be won?
- What is the sharp field likely to build?
- Which field constructions are strong and should be accepted?
- Which popular constructions are fragile if one key assumption fails?
- Which combinations create asymmetric payoff relative to ownership?
- Which first-place paths are worth owning, and with how many bullets?
- Which lineups look different but actually die together?

Chalk is not bad because it is popular. Contrarianism is not an edge by itself. A meaningful fade or overweight must have a causal, game-theory reason.

## Canonical Decision Flow

1. Slate intake and data validation
2. Industry research, projections, ownership, markets, news, and role audit
3. Sharp-field construction and game-theory analysis
4. Sport-specific architecture analysis
5. Scenario and first-place-path generation
6. Contest-specific AI portfolio construction and risk management
7. Exposure and deterministic final validation
8. Post-slate learning and calibration

The detailed responsibility boundaries live in `core/AGENTS.md`. Sport-specific logic lives in `sports/`.

## Slate Workflow

### 1. Ingest and Validate
Collect the site player pool/contest file, salaries, positions, IDs, available projections, projected ownership, ceilings/floors/sim outputs, and contest attributes. Determine the true number of entries and flag missing or malformed inputs.

### 2. Build the Evidence Layer
Search current independent industry projections and ownership when accessible. Add betting markets, implied totals, relevant props, weather/park, official news, starting roles, injuries/scratches, and sport-specific context.

Record source freshness and independence when practical. If industry consensus is thin, label it thin rather than manufacturing certainty.

### 3. Model the Sharp Field
Estimate what the field is likely to build at the lineup level, not only who it will roster. Consider common combinations, correlations, value clusters, salary structures, duplication pressure, and constructions that fail together.

### 4. Build First-Place Paths
Create causal slate theses describing what must happen for a lineup to win, which players/teams benefit together, which field assumptions succeed or fail, and where conditional leverage appears.

Do not maximize raw path count. Favor probability-weighted, payoff-aware Bink Coverage.

### 5. Construct the Portfolio
The AI Portfolio Builder creates contest-specific lineups around first-place paths. It decides the appropriate balance between concentration and coverage based on actual contest structure.

Optimizer output or composite scoring may support the process but never determines exposure automatically.

### 6. Audit and Validate
Audit player, team, stack, pitcher/QB, game, salary, and path concentration. Detect dead overlap. Run deterministic checks for legality, salary, positions, IDs, duplicates, uniques, contest assignment, and exposure arithmetic.

If validation fails, repair the lineup without silently replacing its strategic thesis.

### 7. Final Refresh
Re-check material late news, lineups/roles, weather, markets, and source changes. Revisit only the affected evidence, first-place paths, and portfolio decisions rather than rebuilding blindly.

### 8. Post-Slate Learning
Compare the saved pre-slate evidence and theses against actual ownership, winning/top-tier construction when valid, and Engine results. Separate source errors, field-model errors, strategic errors, implementation errors, and ordinary variance.

Promote only durable lessons into the canonical brain.

## Portfolio Philosophy

The Engine balances:

- projection and ceiling
- ownership and conditional leverage
- correlation
- field construction and duplication risk
- uncertainty
- contest structure and payout shape
- first-place-path coverage
- strategic asymmetry
- shared failure / dead overlap

The goal is not maximum diversification. The goal is to own enough distinct high-quality winning paths while concentrating enough bullets inside the best paths to benefit when the thesis is correct.

## Exposure Contract

Every delivered lineup set must include, when available:

| Player | Savant/Source Own% | Industry Own Range/Consensus | Source Prebuild% | DFS Engine% | vs Source pp | vs Industry pp | Reason |
|---|---:|---:|---:|---:|---:|---:|---|

Source prebuild exposure is not projected ownership and must remain a separate signal.

Material exposure deviations require a stated strategic reason.

## Anti-Hallucination Rules

- Never invent a player, salary, projection, ownership figure, lineup slot, injury, betting line, contest rule, or source value.
- If an input is missing, label it missing.
- Distinguish verified facts from AI interpretation.
- Verify current information before using it when freshness matters.
- Preserve source data separately from Engine-derived conclusions.
- Do not call one external source an industry consensus.

## Code Boundary

AI is the portfolio manager. Deterministic code handles repetitive, auditable work such as parsing, joins, legality, IDs, salary, duplicates, uniques, exposure arithmetic, result joins, storage, and upload-ready CSV creation.

Code must not silently replace AI game-theory decisions.

## Versioning and Streamlining

GitHub stores canonical rules, sport brains, schemas, validated learnings, and execution helpers. It should not become a dump of slate-specific thoughts.

Do not add a rule, agent, metric, or threshold merely because it sounds sophisticated. It must improve a decision, prevent a recurring error, enforce a required output, or support durable learning. Remove or merge logic that becomes redundant, unused, or unsupported by evidence.
