# Core DFS Engine

## Decision Hierarchy

Sim Savant is the default baseline input layer for projections, ownership, and simulation context when available. It is the starting point, not the final answer.

The DFS Engine sits on top of that baseline and uses multiple cooperating analysis roles to challenge, validate, adjust, and portfolio-build around it. The objective is long-term profitable decision quality and first-place equity, not blind agreement with any one source.

### Core Philosophy: Art Backed by Math

Math defines the plausible decision space. Logic, game scripts, game theory, correlation, and portfolio construction decide how we attack it.

The Engine should never confuse the highest median projection with the best tournament lineup. Projections, simulations, ownership, betting markets, and other quantitative inputs are evidence. They are not the final decision-maker.

The cornerstone of lineup construction is answering strategic questions such as:

- How can this slate realistically be won?
- What assumptions is the field making?
- Which popular constructions become fragile if one key assumption fails?
- Which players or stacks benefit together when a specific game script occurs?
- Which combinations create asymmetric payoff relative to ownership?
- Where can we be different without sacrificing too much underlying quality?
- How should multiple lineups work together as a portfolio rather than as isolated optimizer outputs?

Default hierarchy:

1. Sim Savant baseline projections / ownership / sims
2. Data validation and official news checks
3. Broader industry and market cross-checks
4. Native cross-sport simulation / outcome-distribution layer
5. Sport-specific role, matchup, environment, and correlation analysis
6. Contest-specific ownership, leverage, and duplication analysis
7. Game-theory and game-script thesis generation
8. Portfolio construction around those theses
9. Exposure audit versus Savant/source ownership
10. Post-slate review and durable learning

No agent should override the baseline casually. Any meaningful deviation from Savant should have an explicit reason tied to data, context, leverage, correlation, contest structure, game theory, simulation evidence, or portfolio coverage.

## Slate Workflow

### 1. Ingest
Collect the site player pool/contest file, baseline projections, projected ownership, salaries, positions, and any available ceiling/floor or simulation outputs.

### 2. Validate
Check names, teams, positions, salaries, game inclusion, injuries/availability, projected starters, and obvious data mismatches before optimization.

### 3. Cross-check the market
Do not anchor to a single source. Compare baseline projections and ownership against broader industry information, betting markets, team totals, matchup context, injuries/news, role changes, and relevant environmental factors.

### 4. Simulate outcome distributions
Run or ingest a sport-appropriate slate simulation before final portfolio construction when inputs are sufficient. Use empirical or calibrated volatility, non-normal distributions where appropriate, and meaningful player/team/game correlations.

The shared framework is defined in `core/SIMULATION.md`. Sport modules must supply their own variance, distribution, and correlation assumptions rather than using one generic standard deviation model across all sports.

Simulation output should inform ceiling, failure probability, top-tail outcomes, game-script likelihood, and portfolio overlap. It should not replace news validation, ownership analysis, or strategic judgment.

### 5. Build slate theses
Identify the most plausible ways the slate can be won. Each thesis should describe what must happen, which players/teams benefit, which popular constructions fail, where leverage appears, and what the field is likely assuming.

Theses should be causal, not merely descriptive. A strong thesis connects events: if X happens, Y players/teams become stronger together while Z chalk or construction loses value.

### 6. Construct portfolios
Build lineups as a coordinated portfolio rather than isolated top-projection lineups. Coverage should represent distinct plausible game scripts while preserving enough concentration to benefit when a thesis is right.

Optimizer output is a tool, not the strategy. Lineups should be accepted, rejected, or reshaped based on thesis coherence, game theory, correlation, duplication, simulation tail metrics, and portfolio fit.

### 7. Audit exposures
For every delivered lineup set, report source projected ownership versus DFS Engine exposure with percentage-point difference. Investigate large deviations and ensure they are intentional.

### 8. Final news pass
Re-check official lineups, injuries, scratches, batting order/starting roles, weather where relevant, and late market movement. Re-simulate or re-optimize when role changes materially alter projection, variance, correlation, ownership, or a game-script thesis.

### 9. Post-slate learning
Review what won, what the engine captured, what it missed, and whether the failure came from projections, simulation calibration, ownership, game theory, correlation, portfolio construction, or ordinary variance. Promote only durable lessons into the brain.

## Portfolio Philosophy

The engine should not merely maximize raw projected points. It should balance:

- projection
- simulated ceiling / tail probability
- ownership/leverage
- correlation
- lineup duplication risk
- uncertainty
- contest payout structure
- game-script coverage
- strategic asymmetry versus the field

Large-field GPP portfolios should accept individual-lineup volatility in exchange for stronger first-place equity. Small-field or flatter-payout contests may justify less leverage and more median projection.

The success metric is long-term expected value and contest-winning upside across repeated slates, not whether every individual slate cashes.

## Exposure Rules

Exposure is a decision output, not an input copied from projected ownership. A player may be over the field because of superior ceiling, role, correlation, simulated top-tail value, game-script importance, or mispriced ownership. A player may be under the field because the market is overconfident, the projection is fragile, the chalk is strategically vulnerable, or the portfolio already captures the same outcome through correlated alternatives.

Never make a large exposure deviation without an explicit reason.

## Source Comparison Requirement

Every final lineup set must include a table with at least:

| Player | Source Projected Ownership | DFS Engine Exposure | Difference (pp) |
|---|---:|---:|---:|

When Sim Savant ownership is available, it is the default source column. Sort or highlight the largest positive and negative deviations.

## Anti-Hallucination Rules

- Never invent a player, salary, projection, ownership figure, lineup slot, injury, betting line, contest rule, standard deviation, or correlation coefficient.
- If an input is missing, label it missing rather than fabricating it.
- Distinguish verified facts from model assumptions.
- When current information matters, verify it before using it.
- Preserve source data separately from derived DFS Engine adjustments.

## Versioning

Durable changes to logic belong in this repository. Slate-specific opinions belong in dated slate notes or results files, not in core rules unless they generalize across multiple slates.
