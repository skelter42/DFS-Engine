# Core DFS Engine

## Decision Hierarchy

Sim Savant and other vendor sources are baseline inputs, not the final projection authority.

The DFS Engine sits on top of raw source data and uses market-derived projections, ownership estimates, simulations, industry/market context, and GPT/AI portfolio judgment to build tournament lineups. The objective is long-term profitable decision quality and first-place equity, not blind agreement with any one source.

### Core Philosophy: Art Backed by Math

Math defines the plausible decision space. Logic, game scripts, game theory, correlation, industry context, and portfolio construction decide how we attack it.

### GPT-over-Math Operating Principle

Quantitative models, optimizers, projections, ownership estimates, simulations, and mathematical scores are subordinate evidence layers. They generate candidates and describe plausible outcomes; they do not have final authority over portfolio construction.

The final portfolio must receive an explicit GPT/AI strategic review after mathematical candidate generation. That review must evaluate whether proposed lineups express coherent, differentiated paths to first place and whether repeated mathematical solutions create hidden concentration, accidental salary plugs, duplicated scripts, or excessive dependence on one player, team, stack, game, or construction archetype.

GPT/AI judgment must remain grounded in market-derived projections, vendor/source baselines, verified news, industry/market information, ownership, correlation, contest structure, and uncertainty.

The intended hierarchy is:

**Raw source/vendor data -> market-derived DFS projection -> DFS Engine final projection and expected ownership -> simulation/candidate generation -> GPT/AI game-script and portfolio judgment.**

If the mathematical solution and GPT/AI review disagree materially, resolve the disagreement explicitly before final delivery.

## Mandatory Market-Derived Projection Layer

The shared framework is defined in `core/MARKET_PROJECTIONS.md`.

For every sport where sufficiently liquid player props exist, the Engine should derive fantasy projections from betting markets before final lineup construction. Preferred inputs include multi-book player props, alternate/ladder markets, game totals, team totals, moneylines, and relevant role/context information.

Market-derived projections should:

- remove vig where feasible
- aggregate robustly across books
- translate fair event probabilities into expected stat components
- convert expected stat components into site-specific fantasy scoring
- track market coverage/confidence
- shrink toward vendor/industry priors when prop coverage is sparse

Action Network is a preferred market aggregator when available, but no one market source is authoritative.

Do not substitute crude team-total multipliers when richer player-prop markets exist.

## Mandatory Engine-Owned Projection and Ownership Layer

For every serious slate build, the DFS Engine must create and preserve its own projection and ownership estimates before final lineup construction.

For each player preserve at minimum:

- source/vendor projection
- market-derived fantasy projection
- market coverage/confidence
- DFS Engine final projection
- projection difference vs source
- source projected ownership
- DFS Engine expected ownership
- ownership difference vs source
- major drivers of meaningful adjustments

The final Engine projection should normally anchor to the market-derived projection when market coverage is strong. When market coverage is medium or low, blend/shrink toward vendor/industry priors, role, matchup, and environment.

Do not mechanically average sources. Weighting depends on market coverage, freshness, liquidity, internal consistency, and role certainty.

DFS Engine expected ownership is a separate estimate informed by broader industry ownership, salary, Engine projection/value, contest type, roster construction, field tendencies, obvious chalk combinations, and late-news behavior.

These Engine-owned estimates are used for downstream simulation, leverage analysis, game-script construction, candidate generation, and portfolio decisions. Vendor/source values remain immutable baselines for comparison and post-slate calibration.

## Mandatory Cross-Sport Pillars

Every serious DFS Engine build must include:

1. Raw source/vendor data and site roster inputs.
2. Market-derived projection layer when usable player props exist.
3. Broader industry/market intelligence and current news/role context.
4. DFS Engine expected ownership.
5. Sport-appropriate simulation/outcome distributions.
6. GPT/AI game-script judgment and portfolio review.

If market or industry data is unavailable, label the gap explicitly rather than inventing precision.

## Canonical Slate Workflow

1. Ingest site player pool, vendor/source projections/ownership, salaries, positions, and simulation inputs.
2. Validate names, teams, roster positions, availability, and slate membership.
3. Verify current news/roles/lineups and material weather/context.
4. Collect multi-book player props and game markets; Action Network is preferred when available.
5. De-vig, aggregate, and convert markets into expected stat components and market-derived fantasy projections.
6. Grade market coverage and blend sparse players toward vendor/industry priors.
7. Create final DFS Engine projections and DFS Engine expected ownership estimates.
8. Run sport-appropriate simulation/outcome distributions using Engine estimates.
9. Generate a broad mathematical candidate-lineup pool.
10. Run mandatory GPT/AI game-theory, multi-script, and hidden-concentration review.
11. Construct/reshape the final portfolio around approved slate theses.
12. Audit source projection vs market projection vs Engine projection, source ownership vs Engine expected ownership, and Engine exposure.
13. Perform final GPT/AI sign-off plus final news/market recheck.
14. Deliver uploadable lineups and audit files.
15. Post-slate: compare projections, ownership estimates, exposures, actual ownership, and actual scores; store only durable learning.

## Simulation / Outcome Distribution

Run or ingest a sport-appropriate slate simulation when inputs are sufficient. Use calibrated volatility, non-normal distributions where appropriate, and meaningful player/team/game correlations.

Simulation should use DFS Engine estimates while retaining source/vendor values for sensitivity checks. Simulation output should inform ceiling, failure probability, top-tail outcomes, game-script likelihood, and portfolio overlap. It should not replace news validation, ownership analysis, or strategic judgment.

## Candidate Generation and GPT Review

Mathematical candidate generation may be optimizer-heavy because it is not the final decision stage.

Do not promote candidate rankings directly into the final portfolio.

GPT/AI review must identify several plausible ways the slate can be won and audit the candidate pool for hidden concentration. Repeated use of the same player, value piece, stack, pitcher, QB, game, salary structure, or construction archetype must be justified by a slate thesis rather than accepted merely because the optimizer repeatedly prefers it.

The AI pass must preserve multiple credible paths to victory. Stronger theses may receive more exposure, but alternate scripts should remain represented when they have meaningful probability and payoff.

## Portfolio Construction

Build lineups as a coordinated portfolio rather than isolated top-projection lineups.

Optimizer output is a tool, not the strategy. Lineups should be accepted, rejected, or reshaped based on projection quality, market confidence, expected ownership, thesis coherence, game theory, correlation, duplication, simulation tail metrics, industry context, hidden concentration, and portfolio fit.

Roster construction patterns, stack structures, player exposures, team exposures, game exposures, salary usage, and lineup archetypes are outputs of this process. They must not be preset as hard optimization constraints unless required for roster legality, contest rules, inactive-player exclusion, or another verified operational necessity.

## Exposure Rules

Exposure is a decision output, not an input copied from projected ownership.

### No Arbitrary Hard Caps or Floors

Do not impose arbitrary hard maximums, minimums, ownership bands, stack quotas, team quotas, game quotas, salary-spend rules, or diversification targets merely to make a portfolio look balanced.

Soft penalties, diagnostics, and comparative portfolio tests may identify dangerous concentration or excessive duplication, but they should inform rather than mechanically prevent an otherwise superior allocation.

A 0% or 100% exposure is permissible when it emerges from the evidence rather than a preset rule.

Hard constraints are reserved for true structural necessities such as site roster legality, contest rules, confirmed inactive players, invalid combinations, or explicit user-specified operational requirements.

## Required Audit Output

Every delivered lineup set should preserve:

| Player | Source Projection | Market-Derived Projection | Market Coverage | DFS Engine Projection | Source Ownership | DFS Engine Expected Ownership | DFS Engine Exposure |
|---|---:|---:|---|---:|---:|---:|---:|

Investigate the largest projection, ownership, and exposure deviations and ensure they are intentional.

## Final GPT/AI Sign-Off

Before delivery confirm that:

- major exposures are explainable
- high concentration is intentional rather than mathematical repetition
- multiple credible paths to first remain represented
- lineups are coherent with their game scripts
- no optimizer convenience piece has become an accidental universal dependency
- market/industry disagreement has been considered
- no arbitrary hard caps/floors or stack quotas distorted output

A portfolio that fails this review must be reshaped before delivery.

## Post-Slate Learning

Review:

- source/vendor projection vs market-derived projection vs Engine projection vs actual fantasy score
- source ownership vs Engine expected ownership vs actual field ownership
- Engine exposure vs portfolio performance
- whether market coverage/confidence predicted projection reliability
- simulation calibration
- game-script judgment
- correlation and portfolio construction

Grade projection calibration, ownership calibration, and portfolio decision quality separately. Promote only durable lessons into the brain.

## Anti-Hallucination Rules

- Never invent a player, salary, source projection, market-derived projection, Engine projection, source ownership, Engine ownership, prop line, betting line, lineup slot, injury, contest rule, standard deviation, correlation coefficient, or industry signal.
- If an input is missing, label it missing rather than fabricating it.
- Distinguish verified facts from model assumptions and GPT/AI thesis judgment.
- Preserve raw source data separately from derived Engine values.

## Versioning

Durable cross-sport logic belongs in `core/`. Sport-specific prop conversions and correlation logic belong in `sports/`. Slate-specific opinions belong in dated slate notes/results, not core rules unless they generalize across repeated evidence.