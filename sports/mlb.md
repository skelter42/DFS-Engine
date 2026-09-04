# MLB DFS Engine

## Core Construction Philosophy

MLB is a high-variance, correlation-heavy sport. The engine should prioritize coherent team-stack outcomes over isolated median projections.

### MLB Strategic Doctrine: Art Backed by Math

For MLB tournaments, math is the foundation but not the final answer. Market-derived projections, Sim Savant/source baselines, ownership, simulations, betting markets, park/weather data, and matchup metrics define what is plausible. The DFS Engine uses logic, game scripts, game theory, stack interaction, and portfolio construction to decide how to exploit that information.

The goal is not to build the lineup that looks best in a spreadsheet. The goal is to build lineups that are strategically positioned to win when specific slate stories occur.

Every serious MLB build should ask:

- What are the 5-10 most important ways this slate can break?
- Which chalk stacks or pitchers are dependent on fragile assumptions?
- If a popular pitcher fails, which opposing stack benefits and how much leverage is created?
- If a chalk offense succeeds, what secondary stack or pitcher pairing can still make the lineup unique?
- Which team can outscore its ownership because the field is underestimating a matchup, bullpen path, lineup structure, or power ceiling?
- Which cheap bats are not just values, but connective pieces that make an entire game-script lineup work?
- Which lineups are telling the same underlying story even if the players differ?

## MLB Market-Derived Projection Layer

The cross-sport framework lives in `core/MARKET_PROJECTIONS.md`. For MLB, the preferred projection architecture is:

**multi-book player props + game markets -> de-vigged fair probabilities -> expected MLB stat components -> DraftKings fantasy points -> confidence-weighted DFS Engine projection -> ownership/game theory/correlation -> GPT portfolio construction.**

Action Network is the preferred market aggregator when available because it centralizes multi-book player props, alternate markets, odds movement, game totals, and moneylines. It is a preferred source, not an authoritative source.

### Hitter Prop Families

Collect as many of these as are available:

- hits
- alternate hits
- total bases
- alternate total bases
- home runs
- runs scored
- RBI
- runs + RBI when useful for cross-checking
- walks
- HBP if directly available
- stolen bases
- alternate/ladders for relevant counting stats
- team total and game total
- moneyline / implied team scoring environment

Do not double-count overlapping markets. Hits, total bases, home runs, and alternate ladders should be reconciled into a coherent hit-type distribution rather than added independently.

Infer expected singles, doubles, triples, home runs, runs, RBI, BB+HBP, and stolen bases when the market supports those estimates.

For DraftKings classic MLB hitters, market-derived expected fantasy points should use the applicable DK scoring rules from the current slate/site rules. The standard structure is:

`DK hitter points = 3*E(1B) + 5*E(2B) + 8*E(3B) + 10*E(HR) + 2*E(RBI) + 2*E(R) + 2*E(BB+HBP) + 5*E(SB)`

Always verify scoring if DraftKings changes its rules or the contest uses a different format.

### Pitcher Prop Families

Collect as many of these as are available:

- strikeouts
- alternate strikeouts
- outs recorded
- innings pitched where outs are unavailable
- hits allowed
- walks allowed
- earned runs / runs allowed
- WHIP-related markets when useful as a fallback
- moneyline / team win probability
- opponent implied runs
- pitcher-specific win-related context when available

Infer expected strikeouts, outs, hits allowed, walks/HBP allowed, earned runs, and pitcher win probability when evidence supports it.

For DraftKings classic MLB pitchers, use the current DK scoring rules. The base event structure is:

`DK pitcher points = 0.75*E(outs) + 2*E(K) - 0.6*E(H allowed + BB/HBP allowed) - 2*E(ER) + 4*P(win) + expected bonus contribution`

Complete-game, complete-game shutout, and no-hitter bonuses should be included only when modeled with defensible probabilities. Do not manufacture bonus probability just to complete the formula.

### De-vigging and Multi-Book Consensus

- Remove vig from paired/two-sided markets when feasible before converting odds to probabilities.
- Prefer robust multi-book consensus, typically median or trimmed consensus, over one sportsbook.
- Use alternate/ladder markets to estimate tail probabilities and expected counts when coverage is sufficient.
- Flag stale or isolated lines rather than letting them dominate the projection.
- Record market observation count and coverage quality where possible.

### Coverage and Prior Blending

Each player receives a market-coverage grade:

- High: several independent books and multiple relevant prop families; market projection may dominate the final Engine projection.
- Medium: useful prop coverage but meaningful missing components; blend market projection with the prior.
- Low: sparse/noisy props; shrink heavily toward the prior and use the market mainly for environment/context.

The prior may use Sim Savant, broader industry projection consensus, confirmed batting order/role, matchup, park, and weather.

Do not mechanically average market and vendor projections. Weighting should depend on market coverage, liquidity, internal consistency, freshness, and role certainty.

### Team/Game Markets

Game totals, team totals, and moneylines are essential context even when player props are available. Use them to:

- cross-check whether the sum of player expectations is coherent with the team environment
- inform runs/RBI opportunities
- inform pitcher win and run-prevention expectations
- detect stale or inconsistent individual props

Do not simply multiply a player's vendor projection by an implied-team-total ratio when richer player props exist.

### Projection Output Contract

For every relevant MLB player preserve:

- source/vendor projection
- market-derived DK projection
- market coverage grade
- major market inputs / observation count when available
- final DFS Engine projection
- projection difference vs source
- source projected ownership
- DFS Engine expected ownership
- final DFS Engine exposure

The market-derived projection is a projection input. Ownership and final exposure remain separate decisions.

### Default GPP Priorities

- Full 5-man primary stacks should be strongly considered on DraftKings because MLB scoring is highly correlated, but they are not a forced construction rule.
- The Engine may use 5-3, 5-2-1, 4-4, 4-3-1, 4-2-2, 3-3-2, or other legal constructions when simulation, leverage, duplication, salary, or slate structure makes them superior.
- Stack structure is an optimization output, not a fixed input. No portfolio should default to 100% of one stack type unless the Engine independently concludes that is best for that slate and contest.
- Secondary correlation matters; do not treat remaining hitters as random salary fillers.
- Pitcher decisions should consider strikeout ceiling, run prevention, matchup, ownership, salary, and correlation with opposing bats.
- Avoid overfitting to raw optimizer projection when a lineup sacrifices stack quality, ceiling, leverage, uniqueness, or game-script coherence.
- Optimizer ranking is subordinate to strategic fit within the portfolio.

## No Hard Exposure Caps or Floors

The DFS Engine should not use arbitrary hard maximum or minimum exposures for players, teams, stacks, pitchers, game environments, salary usage, or lineup archetypes.

Exposure is an endogenous portfolio result based on projection, simulated tail outcomes, ownership, leverage, correlation, duplication, uncertainty, contest structure, and thesis strength.

Hard caps/floors are allowed only when required by platform legality, explicit contest rules, unavailable/inactive players, or a verified operational constraint. They should not be used merely to force diversification or match a preconceived allocation.

Soft concentration controls are permitted as diagnostics or penalties. For example, the Portfolio Risk Manager may flag excessive overlap, duplicated game scripts, or hidden concentration and ask the builder to compare alternative portfolios. These controls should not mechanically block an exposure percentage unless there is a genuine structural reason.

If the optimal portfolio naturally produces 70% of one pitcher, 0% of another, or 100% five-man stacks, that outcome is allowed—but it must be explained by the slate evidence rather than by a preset cap or force rule.

## Required MLB Agent Team

Every MLB slate build uses the full core agent team plus these specialized passes:

- Market-Derived Projection Agent
- Simulation / Outcome Distribution Agent
- Stack Architecture Agent
- Pitcher Failure / Opposing Stack Agent
- Duplication / Lineup Uniqueness Agent
- Portfolio Risk Manager Agent

Default MLB handoff chain:

Slate Intake -> Projection/Market Intake -> News & Role -> Market-Derived Projection -> Engine Ownership Estimate -> Simulation / Outcome Distribution -> Ownership & Leverage -> Stack Architecture -> Pitcher Failure / Opposing Stack -> Correlation / Game Script -> Candidate Generation -> GPT Portfolio Review -> Portfolio Builder -> Duplication / Lineup Uniqueness -> Portfolio Risk Manager -> Exposure Auditor -> Final News/Market Pass -> Post-Slate Learning.

These passes are mandatory reasoning stages for MLB, even when implemented within one chat session rather than as autonomous background processes.

## Required Cross-Checks

At minimum evaluate:

- market-derived player projections / prop coverage
- implied team totals / run environment
- opposing pitcher quality and handedness
- park factors
- weather where material
- official starting batting orders
- broader industry projections where available
- projected ownership / broader industry ownership
- meaningful injury/rest/scratch news

No one projection or market source is authoritative.

## Simulation / Outcome Distribution

Do not evaluate MLB only from median projections. Assess ceiling and failure distributions for hitters, pitchers, stacks, and game environments. Use market-derived stat distributions, alternate props, Sim Savant simulations, and other defensible distribution inputs when available.

The goal is not to predict one exact outcome; it is to identify which outcome families have enough probability and enough payoff to deserve portfolio exposure.

Simulation probabilities should inform game-script selection, not replace it. Two scenarios with similar probabilities may deserve very different exposure if one creates much stronger leverage or a less duplicated path to first place.

## Batting Order Adjustments

Re-evaluate projection and exposure when:

- an unexpected player leads off
- a cheap/value hitter moves into the top five
- a core hitter falls materially in the order
- a projected starter is scratched
- a team rests multiple regulars

A lineup-position change should influence plate-appearance expectation, stack connectivity, prop interpretation, and ownership, not just raw player projection.

## Stack Evaluation

For each team, evaluate:

- implied scoring environment
- market-derived player ceilings / distributions
- top-to-bottom lineup quality
- home-run and extra-base-hit ceiling
- matchup platoon advantages
- bullpen path
- ownership of the full stack, not only individual hitters
- availability of low-owned connective value
- wraparound connectivity and lineup-order structure
- salary efficiency of the full stack
- likelihood that the field uses the same exact combination
- how the stack fits specific pitcher and secondary-stack game scripts

The goal is to identify combinations where team ceiling is under-owned relative to the field and where the full lineup tells a coherent tournament-winning story.

## Pitcher Failure Leverage

Popular pitcher exposure must be evaluated together with the opposing offense. When a chalk pitcher has a realistic failure path, the Engine should consider whether the opposing stack offers asymmetric leverage.

Pitcher fades should never be mechanical. They must be supported by prop-derived failure risk, matchup, contact quality, platoon, park/weather, pitch-count/role, bullpen, ownership, or other evidence.

The strongest leverage spots often come from linked decisions: underweighting a fragile chalk pitcher while overweighting the offense that directly benefits if the pitcher fails.

## Game-Script Construction

Before final portfolio construction, create a slate-script board. Each major script should include:

- trigger condition
- teams/players that benefit
- chalk or field assumptions that fail
- likely stack/pitcher construction
- ownership/leverage consequence
- expected duplication profile
- confidence tier

Examples:

- elite chalk pitcher dominates and chalk offense also succeeds
- elite chalk pitcher dominates but chalk offense fails
- popular pitcher fails and opposing stack breaks the slate
- two high-total games disappoint while a mid-owned offense erupts
- value pitcher succeeds and unlocks expensive low-owned stack
- low-owned wraparound stack outscores the obvious 1-5 combination

Portfolio exposure should be intentionally allocated across these scripts rather than allowing an optimizer to determine the story accidentally.

## Portfolio Coverage

Across multiple lineups, intentionally cover different plausible slate outcomes:

- chalk offense succeeds
- chalk offense fails
- elite pitcher dominates
- popular pitcher fails and opposing stack wins
- value pitcher unlocks premium bats
- lower-owned team breaks the slate
- one game becomes a shootout

Coverage must remain concentrated enough that a correct thesis can generate multiple top-end lineups.

## Duplication and Uniqueness

The Engine should estimate likely duplication using salary usage, pitcher pairings, stack popularity, value bats, and common field constructions. Seek meaningful uniqueness without forcing low-quality plays solely to be different.

Uniqueness should preferably come from intelligent game theory: a different stack combination, pitcher pairing, lineup-order structure, or correlated leverage path, not from randomly sacrificing projection.

## Portfolio Risk Audit

Before finalizing, audit hidden concentration by:

- player exposure
- primary stack exposure
- secondary stack exposure
- pitcher pairing
- game environment
- salary construction
- game-script dependency

A portfolio containing many different lineups can still represent the same underlying bet. The risk audit must identify that explicitly. The audit should diagnose concentration rather than enforce arbitrary hard limits.

### Short-Slate Portfolio Concentration Audit

On short slates with few viable pitchers and offenses, an optimizer can turn modest median-projection preferences into one hidden portfolio-wide bet. If one pitcher, pitcher pair, primary-stack family, team core, or combined pitcher-plus-stack script appears in all or nearly all multi-entry lineups, the Portfolio Risk Manager must run an explicit counterfactual stress test before final delivery.

The audit must:

- distinguish simulation-supported concentration from repeated optimizer convenience
- test credible alternate-pitcher success, chalk-pitcher failure, and competing team-eruption scenarios
- measure the stack and hitter-ceiling paths unlocked by alternate pitcher salaries
- detect when superficially different lineups still depend on the same pitcher pair and four- or five-player team core
- compare the concentrated portfolio with at least one plausible alternate candidate portfolio
- verify that each contest mini-portfolio still contains distinct paths to first place
- document why the concentration remains superior if it is retained

This is a diagnostic and evidence requirement, not a hard pitcher exposure cap, floor, or mechanical diversification quota.

## Exposure Audit

Every MLB lineup set must include source projected ownership, DFS Engine expected ownership, and DFS Engine final exposure with percentage-point differences.

Large differences should have a stated reason such as market-derived projection edge, stack concentration, lineup-order value, ownership leverage, pitching ceiling, uniqueness, game-script coverage, or reduced confidence in the source projection.

## Post-Slate Learning

Review not only which stack won but also:

- market-derived projection vs vendor projection vs actual DK score
- Engine expected ownership vs actual field ownership
- whether market coverage/confidence predicted projection reliability
- whether the engine owned the winning primary stack
- whether secondary-stack choices separated winners from near-misses
- whether SP1/SP2 construction was correct
- whether ownership leverage was appropriately allocated
- whether any value hitter became essential because of lineup position or salary
- whether duplication or salary construction limited top-end payout
- whether portfolio concentration was intentional or accidental
- whether our slate scripts were logically sound even if they did not occur
- whether the winning construction revealed a new strategic interaction or merely variance

### Counterfactual Review

Post-slate analysis must ask what would have happened if one decision changed while others stayed fixed. Examples:

- if the primary stack hit, would our pitcher construction still have failed?
- if the pitcher call was correct, was the secondary stack the real problem?
- if the leverage thesis was correct, did we simply lack enough exposure?
- if chalk failed as expected, did we choose the right alternative path?

Do not conclude that a stack rule is correct merely because one winning lineup used it. Separate process quality from ordinary baseball variance.