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

MLB projection inputs follow the cross-sport process in `CURRENT.md`. There is no separate MLB Market Inputs override. For a Market Inputs run, read `CURRENT.md` first and then only the three operational files it names.

Books drive the projection when the required scoring-market prices for that player are posted and can be converted into DraftKings site points. If the required scoring markets are incomplete or unavailable, preserve the original Savant projection unchanged. Do not fill missing components with industry projections, rates, season averages, team totals, or narrative. Industry information is a reasonableness check only. Preserve source zeros and leave `Own` unchanged during the projection-only pass.

The prop families below are a research inventory, not permission to combine overlapping markets, manufacture a missing side, or partially blend a player projection.

### Hitter Prop Families

Collect relevant posted markets when available:

- hits and alternate hits
- total bases and alternate total bases
- home runs
- runs scored
- RBI
- walks
- HBP if directly available
- stolen bases
- team total and game total as context

Do not double-count overlapping markets. Hits, total bases, home runs, and alternate ladders must be reconciled into a coherent event distribution rather than added independently.

For DraftKings Classic hitters, use the current official scoring rules for the contest format. The standard base scoring structure is:

`DK hitter points = 3*E(1B) + 5*E(2B) + 8*E(3B) + 10*E(HR) + 2*E(RBI) + 2*E(R) + 2*E(BB+HBP) + 5*E(SB)`

Verify the current site rules before changing this conversion or applying it to another format.

### Pitcher Prop Families

Collect relevant posted markets when available:

- strikeouts and alternate strikeouts
- outs recorded
- hits allowed
- walks allowed
- earned runs / runs allowed
- moneyline / team win probability
- opponent implied runs as context

For DraftKings Classic pitchers, use the current official scoring rules. The standard base event structure is:

`DK pitcher points = 0.75*E(outs) + 2*E(K) - 0.6*E(H allowed + BB/HBP allowed) - 2*E(ER) + 4*P(win) + expected bonus contribution`

Complete-game, complete-game shutout, and no-hitter bonuses should be included only when modeled with defensible probabilities. Do not manufacture bonus probability.

### De-vigging and Multi-Book Consensus

- Convert only prices actually posted by the sportsbook.
- Remove vig from paired sides when both are posted; follow `core/VEGAS_CONSENSUS.md` for one-sided and push-capable lines.
- Aggregate comparable same-market prices across books using the canonical conversion process.
- Do not treat alternate lines or overlapping prop families as independent scoring components.
- Record source, line, side, odds, timestamp, and URL for each price used.

### Coverage and Fallback

A complete qualifying scoring-market bundle can produce the book-derived site-point projection. If a required scoring market is missing, preserve the original Savant projection unchanged for that player. Do not blend priced components with Savant or fill missing components from an industry projection, season rate, or team total.

Team totals, game totals, and moneylines are useful for checking the game environment and the plausibility of player markets. They are not substitutes for missing player scoring markets.

### Projection Output Contract

For Market Inputs, the import and reconciliation requirements are owned by `core/MARKET_INPUTS_RUN.md`. Preserve the original CSV columns, player identity, row order, and ownership; change only `Proj` where the book projection qualifies. Record the exact posted prices used and whether each row remained on Savant or stayed zero.

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