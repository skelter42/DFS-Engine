# Core DFS Engine

## Decision Hierarchy

Sim Savant is the default baseline input layer for projections, ownership, and simulation context when available. It is the starting point, not the final answer.

The DFS Engine sits on top of that baseline and uses multiple cooperating analysis roles to challenge, validate, adjust, and portfolio-build around it. The objective is long-term profitable decision quality and first-place equity, not blind agreement with any one source.

### Core Philosophy: Art Backed by Math

Math defines the plausible decision space. Logic, game scripts, game theory, correlation, industry context, and portfolio construction decide how we attack it.

### GPT-over-Math Operating Principle

For every sport, quantitative models, optimizers, projections, ownership estimates, simulations, and mathematical scores are subordinate evidence layers. They generate candidates and describe plausible outcomes; they do not have final authority over portfolio construction.

The final portfolio must receive an explicit GPT/AI strategic review after the mathematical candidate-generation stage. That review must evaluate whether the proposed lineups actually express coherent, differentiated paths to first place and whether repeated mathematical solutions are creating hidden concentration, accidental salary plugs, duplicated game scripts, or excessive dependence on one player, team, stack, game, or construction archetype.

GPT/AI judgment is not permission to ignore data. It must remain grounded in projections, simulations, verified news, industry/market information, ownership, correlation, contest structure, and uncertainty. The intended hierarchy is:

**Data and math define what is plausible -> industry and market evidence challenge the assumptions -> GPT/AI game-script judgment decides how the portfolio should attack the slate.**

If the mathematical solution and GPT/AI review disagree materially, the disagreement must be resolved explicitly before final delivery rather than silently accepting the optimizer output.

The Engine should never confuse the highest median projection with the best tournament lineup. Projections, simulations, ownership, betting markets, and other quantitative inputs are evidence. They are not the final decision-maker.

The cornerstone of lineup construction is answering strategic questions such as:

- How can this slate realistically be won?
- What assumptions is the field making?
- Which popular constructions become fragile if one key assumption fails?
- Which players or stacks benefit together when a specific game script occurs?
- Which combinations create asymmetric payoff relative to ownership?
- Where can we be different without sacrificing too much underlying quality?
- How should multiple lineups work together as a portfolio rather than as isolated optimizer outputs?

## Mandatory Cross-Sport Pillars

Every DFS Engine build in every sport must include all three pillars below before final portfolio construction:

1. Baseline quantitative inputs: projections, ownership, salaries, simulation context, and site roster data.
2. Industry / market intelligence: broader industry projections and ownership when available, betting markets, implied environments, role/news context, matchup information, and sport-specific external signals.
3. AI game-script judgment: an explicit reasoning pass that interprets the quantitative and industry evidence, identifies multiple plausible paths to first place, challenges field assumptions, and allocates portfolio exposure across those paths.

None of these pillars is optional on a serious slate build. The Engine must not reduce the process to a projection optimizer, a market-following model, or an ungrounded narrative model. The value comes from combining all three.

If an industry signal is unavailable, label the gap explicitly rather than silently skipping the pillar. If sources disagree, treat the disagreement as information to be resolved through confidence weighting, game theory, and scenario analysis rather than automatic averaging.

Default hierarchy:

1. Sim Savant baseline projections / ownership / sims
2. Data validation and official news checks
3. Mandatory broader industry and market cross-checks
4. Native cross-sport simulation / outcome-distribution layer
5. Sport-specific role, matchup, environment, and correlation analysis
6. Contest-specific ownership, leverage, and duplication analysis
7. Mathematical candidate-lineup generation
8. Mandatory GPT/AI game-theory, multi-script, and hidden-concentration review
9. Portfolio construction / reshaping around the approved theses
10. Exposure audit versus Savant/source ownership
11. Post-slate review and durable learning

No agent should override the baseline casually. Any meaningful deviation from Savant should have an explicit reason tied to data, context, leverage, correlation, contest structure, game theory, simulation evidence, industry disagreement, or portfolio coverage.

## Slate Workflow

### 1. Ingest
Collect the site player pool/contest file, baseline projections, projected ownership, salaries, positions, and any available ceiling/floor or simulation outputs.

### 2. Validate
Check names, teams, positions, salaries, game inclusion, injuries/availability, projected starters, and obvious data mismatches before optimization.

### 3. Cross-check the industry and market — mandatory
Do not anchor to a single source. Compare baseline projections and ownership against broader industry projections/ownership where available, betting markets, implied totals, matchup context, injuries/news, role changes, and relevant environmental factors.

This pass is required for every sport. It should identify consensus, meaningful disagreement, stale assumptions, and possible market blind spots.

### 4. Simulate outcome distributions
Run or ingest a sport-appropriate slate simulation before final portfolio construction when inputs are sufficient. Use empirical or calibrated volatility, non-normal distributions where appropriate, and meaningful player/team/game correlations.

The shared framework is defined in `core/SIMULATION.md`. Sport modules must supply their own variance, distribution, and correlation assumptions rather than using one generic standard deviation model across all sports.

Simulation output should inform ceiling, failure probability, top-tail outcomes, game-script likelihood, and portfolio overlap. It should not replace news validation, ownership analysis, or strategic judgment.

### 5. Generate mathematical candidate lineups
Use projections, simulations, ownership, salary, correlation, and contest-specific scoring to generate a broad candidate pool. Candidate generation is allowed to be optimizer-heavy because it is not the final decision stage.

Do not promote candidate rankings directly into the final portfolio.

### 6. Build AI slate theses and review candidates — mandatory
Run an explicit GPT/AI game-script judgment pass after the quantitative, industry, simulation, and candidate-generation layers are available.

Identify several plausible ways the slate can be won. Each thesis should describe:

- what must happen
- which players, teams, stacks, or games benefit together
- which popular assumptions fail
- where leverage appears
- how the construction differs from likely field behavior
- which lineup archetypes express the thesis
- what evidence supports or weakens the thesis

Then audit the mathematical candidate pool for hidden concentration. Repeated use of the same player, value piece, stack, pitcher, QB, game, salary structure, or construction archetype must be justified by the slate thesis rather than accepted merely because the optimizer repeatedly prefers it.

Theses should be causal, not merely descriptive. A strong thesis connects events: if X happens, Y players/teams become stronger together while Z chalk or construction loses value.

The AI pass must preserve multiple credible paths to victory rather than collapsing the portfolio onto one forecast. Stronger theses may receive more exposure, but alternate scripts should remain represented when they have meaningful probability and payoff.

### 7. Construct and reshape portfolios
Build lineups as a coordinated portfolio rather than isolated top-projection lineups. Coverage should represent distinct plausible game scripts while preserving enough concentration to benefit when a thesis is right.

Optimizer output is a tool, not the strategy. Lineups should be accepted, rejected, or reshaped based on thesis coherence, game theory, correlation, duplication, simulation tail metrics, industry context, hidden concentration, and portfolio fit.

Roster construction patterns, stack structures, player exposures, team exposures, game exposures, salary usage, and lineup archetypes are outputs of this process. They must not be preset as hard optimization constraints unless required for roster legality, contest rules, inactive-player exclusion, or another verified operational necessity.

### 8. Audit exposures
For every delivered lineup set, report source projected ownership versus DFS Engine exposure with percentage-point difference. Investigate large deviations and ensure they are intentional.

### 9. Final GPT/AI sign-off
Before delivery, perform one final strategic review of the complete portfolio. Confirm that:

- major exposures are explainable
- high concentration is intentional rather than mathematical repetition
- multiple credible paths to first remain represented
- lineups are coherent with their game scripts
- no optimizer convenience piece has become an accidental universal dependency
- industry/market disagreement has been considered
- no arbitrary hard caps/floors or stack quotas distorted the output

A portfolio that fails this review must be reshaped before delivery.

### 10. Final news / market pass
Re-check official lineups, injuries, scratches, batting order/starting roles, weather where relevant, and late market movement. Re-simulate or re-optimize when role changes materially alter projection, variance, correlation, ownership, industry consensus, or a game-script thesis.

### 11. Post-slate learning
Review what won, what the engine captured, what it missed, and whether the failure came from projections, simulation calibration, industry/market interpretation, AI game-script judgment, ownership, game theory, correlation, portfolio construction, or ordinary variance. Promote only durable lessons into the brain.

## Portfolio Philosophy

The engine should not merely maximize raw projected points. It should balance:

- projection
- simulated ceiling / tail probability
- industry and market context
- ownership/leverage
- AI game-script strength
- correlation
- lineup duplication risk
- uncertainty
- contest payout structure
- game-script coverage
- strategic asymmetry versus the field

Large-field GPP portfolios should accept individual-lineup volatility in exchange for stronger first-place equity. Small-field or flatter-payout contests may justify less leverage and more median projection.

The success metric is long-term expected value and contest-winning upside across repeated slates, not whether every individual slate cashes.

## Exposure Rules

Exposure is a decision output, not an input copied from projected ownership. A player may be over the field because of superior ceiling, role, correlation, simulated top-tail value, game-script importance, industry disagreement, or mispriced ownership. A player may be under the field because the market is overconfident, the projection is fragile, the chalk is strategically vulnerable, or the portfolio already captures the same outcome through correlated alternatives.

### No Arbitrary Hard Caps or Floors

Do not impose arbitrary hard maximums, minimums, ownership bands, stack quotas, team quotas, game quotas, salary-spend rules, or diversification targets merely to make a portfolio look balanced.

The Engine may use soft penalties, diagnostics, and comparative portfolio tests to identify dangerous concentration or excessive duplication, but those mechanisms should inform the decision rather than mechanically prevent an otherwise optimal allocation.

A very high or very low exposure is acceptable when supported by the slate evidence. A 0% or 100% outcome is also permissible when it emerges from the analysis rather than from a preset rule.

Hard constraints are reserved for true structural necessities such as site roster legality, contest rules, confirmed inactive players, invalid combinations, or explicit user-specified operational requirements.

Never make a large exposure deviation without an explicit reason.

## Source Comparison Requirement

Every final lineup set must include a table with at least:

| Player | Source Projected Ownership | DFS Engine Exposure | Difference (pp) |
|---|---:|---:|---:|

When Sim Savant ownership is available, it is the default source column. Sort or highlight the largest positive and negative deviations.

## Anti-Hallucination Rules

- Never invent a player, salary, projection, ownership figure, lineup slot, injury, betting line, contest rule, standard deviation, correlation coefficient, or industry signal.
- If an input is missing, label it missing rather than fabricating it.
- Distinguish verified facts from model assumptions and AI thesis judgment.
- When current information matters, verify it before using it.
- Preserve source data separately from derived DFS Engine adjustments.

## Versioning

Durable changes to logic belong in this repository. Slate-specific opinions belong in dated slate notes or results files, not in core rules unless they generalize across multiple slates.
