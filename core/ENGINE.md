# Core DFS Engine

## Decision Hierarchy

The DFS Engine is Vegas-first for player performance projections whenever sufficiently liquid player props and game markets exist.

Market-derived projections are the primary performance estimate. Sim Savant and other trusted vendor projections are fallback priors used when Vegas signals are weak, incomplete, stale, internally inconsistent, or unavailable. Broader industry projections are primarily sanity checks and secondary fallback evidence.

The objective is long-term profitable decision quality and first-place equity, not blind agreement with any one source.

### Core Philosophy: Art Backed by Math

Math defines the plausible decision space. Logic, game scripts, game theory, correlation, industry context, and portfolio construction decide how we attack it.

### GPT-over-Math Operating Principle

Quantitative models, optimizers, projections, ownership estimates, simulations, and mathematical scores are subordinate evidence layers. They generate candidates and describe plausible outcomes; they do not have final authority over portfolio construction.

The final portfolio must receive an explicit GPT/AI strategic review after mathematical candidate generation. That review must evaluate whether proposed lineups express coherent, differentiated paths to first place and whether repeated mathematical solutions create hidden concentration, accidental salary plugs, duplicated scripts, or excessive dependence on one player, team, stack, game, or construction archetype.

GPT/AI judgment must remain grounded in market-derived projections, fallback priors, verified news, industry/market information, ownership, correlation, contest structure, and uncertainty.

The intended hierarchy is:

**Raw slate/site data -> Vegas/market-derived projection -> confidence-weighted fallback prior only where needed -> DFS Engine projection + expected ownership -> simulation/candidate generation -> GPT/AI game-script and portfolio judgment.**

If mathematical output and GPT/AI review disagree materially, resolve the disagreement explicitly before final delivery.

## Mandatory Vegas-First Projection Layer

The shared framework is defined in `core/MARKET_PROJECTIONS.md`.

For every sport where sufficiently liquid player props exist, derive fantasy projections from betting markets before final lineup construction. Preferred inputs include multi-book player props, alternate/ladder markets, game totals, team totals, moneylines, and relevant role/context information.

Market-derived projections should:

- remove vig where feasible
- aggregate robustly across books
- translate fair event probabilities into expected stat components
- convert expected stat components into site-specific fantasy scoring
- track market coverage/confidence
- use Savant/vendor projections only as fallback priors when market evidence is not strong enough

Action Network is a preferred market aggregator when available, but no one market source is authoritative.

Do not substitute crude team-total multipliers when richer player-prop markets exist.

## Source Projection Eligibility Gate

A player with a supplied Savant/vendor projection of exactly `0` is excluded from candidate generation for that build.

This is a hard data-quality/eligibility rule, not an exposure cap and not a requirement that official lineups already be confirmed. Pre-confirmation builds are allowed and expected.

Rules:

- If the current supplied Savant/vendor source has `Proj = 0`, exclude that player from the candidate pool.
- Do not override a current source zero merely because the DraftKings player pool still lists the player or because a market line exists.
- If a later refreshed source file gives the player a nonzero projection, the player may re-enter only after the slate is rebuilt from that refreshed source.
- Missing or unconfirmed lineups alone do not make a nonzero-projection player ineligible.
- Confirmed OUT/scratched/inactive status remains an independent exclusion when known.
- Final QA must verify that no player with a current source projection of zero appears in the delivered lineup file.

The purpose is simple: the Engine may build before official lineups confirm, but it must never roster a player whom the current supplied baseline source has explicitly zeroed out.

## Mandatory Engine-Owned Projection and Ownership Layer

For every serious slate build, the DFS Engine must create and preserve its own projection and ownership estimates before final lineup construction.

For each player preserve at minimum:

- Savant/vendor fallback projection
- market-derived fantasy projection
- market coverage/confidence
- final DFS Engine projection
- projection difference vs fallback source
- source projected ownership
- DFS Engine expected ownership
- ownership difference vs source
- major drivers of meaningful adjustments

The final Engine projection should normally equal or closely track the market-derived projection when market coverage is High. As coverage deteriorates to Medium or Low, progressively shrink toward the Savant/vendor prior. With no usable market, the fallback prior may become the Engine projection and must be labeled fallback-driven.

Do not use a fixed universal blend. Weighting depends on market coverage, freshness, liquidity, cross-book agreement, internal consistency, and role certainty.

DFS Engine expected ownership is a separate estimate informed by broader industry ownership, salary, Engine projection/value, contest type, roster construction, field tendencies, obvious chalk combinations, and late-news behavior.

These Engine-owned estimates are used for downstream simulation, leverage analysis, game-script construction, candidate generation, and portfolio decisions. Vendor/source values remain immutable baselines for comparison and post-slate calibration.

## Mandatory Cross-Sport Pillars

Every serious DFS Engine build must include:

1. Raw slate/site data and fallback vendor inputs.
2. Vegas/market-derived projection layer when usable player props exist.
3. Current news/role validation and broader industry sanity checks.
4. DFS Engine expected ownership.
5. Sport-appropriate simulation/outcome distributions.
6. GPT/AI game-script judgment and portfolio review.

If market or industry data is unavailable, label the gap explicitly rather than inventing precision.

## Canonical Slate Workflow

1. Ingest site player pool, salaries, positions, entries, vendor/source projections/ownership, and available simulation inputs.
2. Apply the Source Projection Eligibility Gate and validate names, teams, roster positions, availability, and slate membership.
3. Verify current news/roles/lineups and material weather/context when available; official lineup confirmation is not required for a prebuild.
4. Collect multi-book player props and game markets; Action Network is preferred when available.
5. De-vig, aggregate, reconcile overlapping markets, and convert them into expected stat components and market-derived fantasy projections.
6. Grade market coverage/confidence for every relevant player.
7. Use the market projection as primary; apply Savant/vendor fallback weight only where confidence is insufficient.
8. Create final DFS Engine projections and DFS Engine expected ownership estimates.
9. Run sport-appropriate simulation/outcome distributions using Engine estimates.
10. Generate a broad mathematical candidate-lineup pool.
11. Run mandatory GPT/AI game-theory, multi-script, and hidden-concentration review.
12. Construct/reshape the final portfolio around approved slate theses.
13. Audit fallback projection vs market projection vs Engine projection, source ownership vs Engine expected ownership, and Engine exposure.
14. Perform final GPT/AI sign-off plus final news/market recheck and re-run the zero-projection audit on every delivered lineup.
15. Rebuild when material late information changes roles, markets, ownership, source projections, or scripts.
16. Deliver uploadable lineups and audit files.
17. Post-slate: compare projection methods, ownership estimates, exposures, actual ownership, and actual scores; store only durable learning.

## Simulation / Outcome Distribution

Run or ingest a sport-appropriate slate simulation when inputs are sufficient. Use calibrated volatility, non-normal distributions where appropriate, and meaningful player/team/game correlations.

Simulation should use DFS Engine estimates while retaining market and fallback values for sensitivity checks. Simulation output should inform ceiling, failure probability, top-tail outcomes, game-script likelihood, and portfolio overlap. It should not replace news validation, ownership analysis, or strategic judgment.

## Candidate Generation and GPT Review

Mathematical candidate generation may be optimizer-heavy because it is not the final decision stage.

Do not promote candidate rankings directly into the final portfolio.

GPT/AI review must identify several plausible ways the slate can be won and audit the candidate pool for hidden concentration. Repeated use of the same player, value piece, stack, pitcher, QB, game, salary structure, or construction archetype must be justified by a slate thesis rather than accepted merely because the optimizer repeatedly prefers it.

The AI pass must preserve multiple credible paths to victory. Stronger theses may receive more exposure, but alternate scripts should remain represented when they have meaningful probability and payoff.

## Portfolio Construction

Build lineups as a coordinated portfolio rather than isolated top-projection lineups.

Optimizer output is a tool, not the strategy. Lineups should be accepted, rejected, or reshaped based on projection quality, market confidence, expected ownership, thesis coherence, game theory, correlation, duplication, simulation tail metrics, industry context, hidden concentration, and portfolio fit.

Roster construction patterns, stack structures, player exposures, team exposures, game exposures, salary usage, and lineup archetypes are outputs of this process. They must not be preset as hard optimization constraints unless required for roster legality, contest rules, inactive-player exclusion, or another verified operational necessity.

### Multi-Contest Portfolio Allocation

When entries span multiple contests on the same slate, optimize at two levels simultaneously:

1. **Contest portfolio:** each contest's entries must form a complete, coherent mini-portfolio capable of taking down that contest on its own.
2. **Bankroll portfolio:** all entries together must broaden aggregate first-place equity, reduce redundant outcome exposure, and support long-term profitability.

Do not sort all lineups by median projection and place the entire highest-ranked block into the largest or highest-buy-in contest. That creates scenario gaps in the other contests and treats them as leftovers.

Before allocation, label each lineup by its meaningful slate script, correlation structure, anchor combination, risk tier, ownership/duplication profile, and other sport-specific outcome drivers. Allocate the lineup set across contests with a scenario-stratified quality ladder:

- distribute the strongest risk-adjusted lineup to the highest-priority contest, the next comparable lineup to the next contest, and continue through the contest set before restarting the rotation;
- perform that ladder within or across the material script families so every contest retains credible favorite/chalk, balanced, and leverage/upset paths as appropriate to the sport;
- allow the higher-priority or higher-buy-in contest to be modestly stronger on average, but never let it monopolize the strongest scripts or leave another contest without a viable path to first;
- treat contest size, payout concentration, field strength, duplication, buy-in, and the user's risk objective as the real priority inputs; use entry fee only as a weak proxy when richer contest metadata is unavailable;
- let slate uncertainty control the degree of coverage and quality tilt: uncertain slates require broader script protection inside each contest, while more deterministic slates may concentrate more heavily on the strongest thesis;
- permit repeating a lineup across different contests only when the repeated lineup has intentional positive expected value and the added contest coverage is worth the increased outcome correlation; do not require either global uniqueness or cross-contest duplication mechanically.

Allocation is a portfolio decision, not administrative row ordering. Lower-buy-in contests must not become dumping grounds for lower-quality candidates. Every allocated lineup must remain strategically coherent and every contest must pass an independent take-down-path audit.

For every multi-contest build, report by contest at minimum:

- lineup count and uniqueness
- average projection plus ceiling/top-tail evidence when available
- average ownership/leverage or duplication proxy
- allocation across material script, anchor, correlation, and risk families
- key player/team/game exposure where relevant
- the reason for any contest-specific tilt

Reject and reallocate a portfolio when one contest monopolizes the best risk-adjusted candidates, another contest lacks a material script family without a documented reason, or the contest blocks do not collectively improve bankroll-level first-place equity.

## Exposure Rules

Exposure is a decision output, not an input copied from projected ownership.

### No Arbitrary Hard Caps or Floors

Do not impose arbitrary hard maximums, minimums, ownership bands, stack quotas, team quotas, game quotas, salary-spend rules, or diversification targets merely to make a portfolio look balanced.

Soft penalties, diagnostics, and comparative portfolio tests may identify dangerous concentration or excessive duplication, but they should inform rather than mechanically prevent an otherwise superior allocation.

A 0% or 100% exposure is permissible when it emerges from the evidence rather than a preset rule.

Hard constraints are reserved for true structural necessities such as site roster legality, contest rules, confirmed inactive players, invalid combinations, the Source Projection Eligibility Gate, or explicit user-specified operational requirements.

## Required Audit Output

Every delivered lineup set should preserve:

| Player | Savant/Vendor Fallback | Market-Derived Projection | Market Coverage | DFS Engine Projection | Source Ownership | DFS Engine Expected Ownership | DFS Engine Exposure |
|---|---:|---:|---|---:|---:|---:|---:|

Investigate the largest projection, ownership, and exposure deviations and ensure they are intentional.

## Final GPT/AI Sign-Off

Before delivery confirm that:

- no current source-zero player appears in the lineup file
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

- Savant/vendor fallback projection vs market-derived projection vs Engine projection vs actual fantasy score
- source ownership vs Engine expected ownership vs actual field ownership
- Engine exposure vs portfolio performance
- whether market-confidence tiers predicted projection reliability
- simulation calibration
- game-script judgment
- correlation and portfolio construction

The Vegas-first hierarchy is itself testable. If high-confidence market projections fail to outperform fallback priors over a meaningful sample, recalibrate confidence rules rather than protecting the assumption.

Grade projection calibration, ownership calibration, and portfolio decision quality separately. Promote only durable lessons into the brain.

## Anti-Hallucination Rules

- Never invent a player, salary, source projection, market-derived projection, Engine projection, source ownership, Engine ownership, prop line, betting line, lineup slot, injury, contest rule, standard deviation, correlation coefficient, or industry signal.
- If an input is missing, label it missing rather than fabricating it.
- Distinguish verified facts from model assumptions and GPT/AI thesis judgment.
- Preserve raw source data separately from derived Engine values.

## Versioning

Durable cross-sport logic belongs in `core/`. Sport-specific prop conversions and correlation logic belong in `sports/`. Slate-specific opinions belong in dated slate notes/results, not core rules unless they generalize across repeated evidence.