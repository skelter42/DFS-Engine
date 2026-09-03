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

**Raw source data -> DFS Engine projection and ownership estimates -> simulation and candidate generation -> industry/market challenge -> GPT/AI portfolio judgment.**

If the mathematical solution and GPT/AI review disagree materially, the disagreement must be resolved explicitly before final delivery rather than silently accepting the optimizer output.

The Engine should never confuse the highest median projection with the best tournament lineup. Projections, simulations, ownership, betting markets, and other quantitative inputs are evidence. They are not the final decision-maker.

## Mandatory Engine-Owned Projection and Ownership Layer

For every serious slate build, the DFS Engine must create and preserve its own projection and ownership estimates before final lineup construction.

Sim Savant and any other vendor source are immutable baseline inputs. They must never be relabeled as DFS Engine estimates.

For each player, preserve at minimum:

- source projection (Sim Savant when provided)
- DFS Engine projection
- projection difference (Engine minus source)
- source projected ownership
- DFS Engine expected ownership
- ownership difference (Engine minus source)
- confidence / uncertainty notes when material
- major drivers of any meaningful adjustment

DFS Engine projection adjustments should be informed by broader industry projections, betting markets, role/news, matchup, environment, sport-specific context, and simulation calibration. DFS Engine expected ownership should be informed by broader industry ownership, salary, projection/value, contest type, roster construction, recent field tendencies, obvious chalk combinations, and likely late-news behavior.

Do not mechanically average sources. The Engine should form an explicit estimate and preserve the reason for meaningful disagreement.

These Engine-owned estimates are the numbers used for downstream simulation, leverage analysis, game-script construction, candidate generation, and portfolio decisions. Savant remains the raw baseline used for comparison and post-slate calibration.

## Mandatory Cross-Sport Pillars

Every DFS Engine build in every sport must include all three pillars below before final portfolio construction:

1. Baseline quantitative inputs: projections, ownership, salaries, simulation context, and site roster data.
2. Industry / market intelligence: broader industry projections and ownership when available, betting markets, implied environments, role/news context, matchup information, and sport-specific external signals.
3. AI game-script judgment: an explicit reasoning pass that interprets the quantitative and industry evidence, identifies multiple plausible paths to first place, challenges field assumptions, and allocates portfolio exposure across those paths.

None of these pillars is optional on a serious slate build. The Engine must not reduce the process to a projection optimizer, a market-following model, or an ungrounded narrative model. The value comes from combining all three.

If an industry signal is unavailable, label the gap explicitly rather than silently skipping the pillar. If sources disagree, treat the disagreement as information to be resolved through confidence weighting, game theory, and scenario analysis rather than automatic averaging.

Default hierarchy:

1. Sim Savant/source baseline projections / ownership / sims
2. Data validation and official news checks
3. Mandatory broader industry and market cross-checks
4. Create DFS Engine projection and expected-ownership estimates
5. Native cross-sport simulation / outcome-distribution layer using Engine estimates
6. Sport-specific role, matchup, environment, and correlation analysis
7. Contest-specific ownership, leverage, and duplication analysis
8. Mathematical candidate-lineup generation
9. Mandatory GPT/AI game-theory, multi-script, and hidden-concentration review
10. Portfolio construction / reshaping around the approved theses
11. Exposure audit versus both Savant/source ownership and DFS Engine expected ownership
12. Post-slate review and durable learning

Any meaningful deviation from Savant/source data should have an explicit reason tied to data, context, leverage, correlation, contest structure, game theory, simulation evidence, industry disagreement, or portfolio coverage.

## Slate Workflow

### 1. Ingest
Collect the site player pool/contest file, baseline projections, projected ownership, salaries, positions, and any available ceiling/floor or simulation outputs. Preserve raw source columns unchanged.

### 2. Validate
Check names, teams, positions, salaries, game inclusion, injuries/availability, projected starters, and obvious data mismatches before optimization.

### 3. Cross-check the industry and market — mandatory
Do not anchor to a single source. Compare baseline projections and ownership against broader industry projections/ownership where available, betting markets, implied totals, matchup context, injuries/news, role changes, and relevant environmental factors.

This pass is required for every sport. It should identify consensus, meaningful disagreement, stale assumptions, and possible market blind spots.

### 4. Create DFS Engine projections and ownership — mandatory
Produce an Engine projection and Engine expected-ownership estimate for each relevant player. Preserve both raw source values and Engine values side by side.

Large differences must have a reason. Missing evidence should lower confidence rather than cause invented precision.

### 5. Simulate outcome distributions
Run or ingest a sport-appropriate slate simulation before final portfolio construction when inputs are sufficient. Use empirical or calibrated volatility, non-normal distributions where appropriate, and meaningful player/team/game correlations.

The shared framework is defined in `core/SIMULATION.md`. Sport modules must supply their own variance, distribution, and correlation assumptions rather than using one generic standard deviation model across all sports.

Simulation should use DFS Engine estimates when they exist while retaining source values for sensitivity checks. Simulation output should inform ceiling, failure probability, top-tail outcomes, game-script likelihood, and portfolio overlap. It should not replace news validation, ownership analysis, or strategic judgment.

### 6. Generate mathematical candidate lineups
Use Engine projections, Engine expected ownership, simulations, salary, correlation, and contest-specific scoring to generate a broad candidate pool. Candidate generation is allowed to be optimizer-heavy because it is not the final decision stage.

Do not promote candidate rankings directly into the final portfolio.

### 7. Build AI slate theses and review candidates — mandatory
Run an explicit GPT/AI game-script judgment pass after the quantitative, industry, simulation, and candidate-generation layers are available.

Identify several plausible ways the slate can be won. Each thesis should describe what must happen, which players/teams/stacks/games benefit together, which popular assumptions fail, where leverage appears, how construction differs from likely field behavior, which lineup archetypes express the thesis, and what evidence supports or weakens it.

Then audit the mathematical candidate pool for hidden concentration. Repeated use of the same player, value piece, stack, pitcher, QB, game, salary structure, or construction archetype must be justified by the slate thesis rather than accepted merely because the optimizer repeatedly prefers it.

The AI pass must preserve multiple credible paths to victory rather than collapsing the portfolio onto one forecast. Stronger theses may receive more exposure, but alternate scripts should remain represented when they have meaningful probability and payoff.

### 8. Construct and reshape portfolios
Build lineups as a coordinated portfolio rather than isolated top-projection lineups. Coverage should represent distinct plausible game scripts while preserving enough concentration to benefit when a thesis is right.

Optimizer output is a tool, not the strategy. Lineups should be accepted, rejected, or reshaped based on thesis coherence, game theory, correlation, duplication, simulation tail metrics, industry context, hidden concentration, and portfolio fit.

Roster construction patterns, stack structures, player exposures, team exposures, game exposures, salary usage, and lineup archetypes are outputs of this process. They must not be preset as hard optimization constraints unless required for roster legality, contest rules, inactive-player exclusion, or another verified operational necessity.

### 9. Audit projections, ownership, and exposures
Every delivered lineup set should preserve these three comparisons:

| Player | Source Projection | DFS Engine Projection | Projection Diff | Source Projected Ownership | DFS Engine Expected Ownership | Ownership Diff | DFS Engine Exposure |
|---|---:|---:|---:|---:|---:|---:|---:|

Investigate the largest projection, ownership, and exposure deviations and ensure they are intentional.

### 10. Final GPT/AI sign-off
Before delivery, perform one final strategic review of the complete portfolio. Confirm that major exposures are explainable, high concentration is intentional rather than mathematical repetition, multiple credible paths to first remain represented, lineups are coherent with their game scripts, no optimizer convenience piece has become an accidental universal dependency, industry/market disagreement has been considered, and no arbitrary hard caps/floors or stack quotas distorted the output.

A portfolio that fails this review must be reshaped before delivery.

### 11. Final news / market pass
Re-check official lineups, injuries, scratches, batting order/starting roles, weather where relevant, and late market movement. Rebuild Engine projection/ownership estimates, re-simulate, or re-optimize when role changes materially alter projection, variance, correlation, ownership, industry consensus, or a game-script thesis.

### 12. Post-slate learning
Review source projection vs Engine projection vs actual outcome, source projected ownership vs Engine expected ownership vs actual field ownership, and Engine exposure vs portfolio performance.

Grade projection calibration, ownership calibration, industry/market interpretation, AI game-script judgment, simulation calibration, correlation, and portfolio construction separately. Promote only durable lessons into the brain.

## Exposure Rules

Exposure is a decision output, not an input copied from projected ownership. A player may be over the field because of superior ceiling, role, correlation, simulated top-tail value, game-script importance, industry disagreement, or mispriced ownership. A player may be under the field because the market is overconfident, the projection is fragile, the chalk is strategically vulnerable, or the portfolio already captures the same outcome through correlated alternatives.

### No Arbitrary Hard Caps or Floors

Do not impose arbitrary hard maximums, minimums, ownership bands, stack quotas, team quotas, game quotas, salary-spend rules, or diversification targets merely to make a portfolio look balanced.

The Engine may use soft penalties, diagnostics, and comparative portfolio tests to identify dangerous concentration or excessive duplication, but those mechanisms should inform the decision rather than mechanically prevent an otherwise optimal allocation.

A very high or very low exposure is acceptable when supported by the slate evidence. A 0% or 100% outcome is also permissible when it emerges from the analysis rather than from a preset rule.

Hard constraints are reserved for true structural necessities such as site roster legality, contest rules, confirmed inactive players, invalid combinations, or explicit user-specified operational requirements.

Never make a large exposure deviation without an explicit reason.

## Anti-Hallucination Rules

- Never invent a player, salary, source projection, Engine projection, source ownership, Engine ownership, lineup slot, injury, betting line, contest rule, standard deviation, correlation coefficient, or industry signal.
- If an input is missing, label it missing rather than fabricating it.
- Distinguish verified facts from model assumptions and AI thesis judgment.
- When current information matters, verify it before using it.
- Preserve source data separately from derived DFS Engine adjustments.

## Versioning

Durable changes to logic belong in this repository. Slate-specific opinions belong in dated slate notes or results files, not in core rules unless they generalize across multiple slates.
