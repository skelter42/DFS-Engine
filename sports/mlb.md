# MLB DFS Engine

## Core Construction Philosophy

MLB is a high-variance, correlation-heavy sport. The engine should prioritize coherent team-stack outcomes over isolated median projections.

### MLB Strategic Doctrine: Art Backed by Math

For MLB tournaments, math is the foundation but not the final answer. Sim Savant projections, ownership, simulations, betting markets, park/weather data, matchup metrics, and broader industry information define what is plausible. The DFS Engine uses AI reasoning, game scripts, game theory, stack interaction, and portfolio construction to decide how to exploit that information.

The goal is not to build the lineup that looks best in a spreadsheet. The goal is to build lineups that are strategically positioned to win when specific slate stories occur.

Every serious MLB build should ask:

- What are the 5-10 most important ways this slate can break?
- Which chalk stacks or pitchers are dependent on fragile assumptions?
- If a popular pitcher fails, which opposing stack benefits and how much leverage is created?
- If a chalk offense succeeds, what secondary stack or pitcher pairing can still make the lineup unique?
- Which team can outscore its ownership because the field is underestimating a matchup, bullpen path, lineup structure, market move, or power ceiling?
- Which cheap bats are not just values, but connective pieces that make an entire game-script lineup work?
- Which lineups are telling the same underlying story even if the players differ?

### Sharp-Field Game Theory Doctrine

Assume the field is sharp by default. Large-field tournament opponents generally have access to strong projections, ownership tools, optimizer outputs, betting markets, and common DFS strategy. Therefore the Engine should not expect to win simply by identifying the highest-projected plays.

Chalk is usually chalk for a reason. Do not fade strong plays merely to be different. Instead, search for where the field may be efficient at the player level but fragile at the lineup or portfolio level.

The Engine should look for exploitable field behavior such as:

- over-concentrated pitcher pairings
- highly duplicated primary-stack combinations
- obvious value bats appearing together too frequently
- common salary constructions
- popular game environments that create correlated field failure
- ownership that is reasonable in isolation but inefficient when several popular pieces are combined
- opposing-stack leverage against a popular pitcher with a credible failure path
- secondary-stack or one-off combinations the field underuses despite strong conditional upside

Contrarianism is not an edge by itself. Every major underweight, fade, or low-owned overweight must answer:

1. What does the field believe?
2. Why is that belief reasonable?
3. What evidence gives the Engine permission to disagree?
4. What happens to our first-place probability if our view is correct?
5. Which portion of the field fails at the same time?

Use conditional leverage rather than raw low ownership. A 25%-owned player can be excellent leverage in the right construction, while a 3%-owned player can still be a poor tournament play.

Working mental model:

- Projection estimates what is likely.
- Ownership estimates what the field believes.
- Game theory identifies where probability and payoff may be mispriced.
- Bink Coverage determines whether the portfolio owns enough distinct first-place paths.

### Multi-Source Projection and Ownership Doctrine

No single projection or ownership source is allowed to define the slate. Sim Savant is a valuable baseline and simulation source, but its projections and ownership can be narrow, stale, model-specific, or wrong in ways that become dangerous when copied directly into portfolio exposure.

The Industry Research Agent must actively seek additional projection and projected-ownership sources whenever materially accessible. The goal is not to blindly average them. The goal is to understand the distribution of industry opinion and identify where Sim Savant is consensus, where it is an outlier, and why.

For projections, capture when possible:

- Sim Savant player projection and ceiling/simulation context
- at least one additional independent industry projection source
- additional sources when accessible
- range, median/consensus, and material outliers
- timestamps or freshness when relevant

For ownership, capture when possible:

- Sim Savant projected ownership
- at least one additional independent industry ownership projection
- additional sources when accessible
- range, median/consensus, and material outliers
- likely reasons for disagreement, such as lineup news, pricing, contest assumptions, source update time, or model methodology

A source disagreement should be treated as information. Do not automatically average it away. AI should determine whether the difference represents stale data, uncertainty, a true modeling disagreement, or a possible game-theory opportunity.

When only one external projection or ownership source is obtainable, explicitly record that the consensus is thin and reduce confidence accordingly. Never label a single-source view as industry consensus.

### Default GPP Priorities

- Strong preference for full 5-man primary stacks on DraftKings when slate size supports it.
- Secondary correlation matters; do not treat the remaining hitters as random salary fillers.
- Pitcher decisions should consider strikeout ceiling, run prevention, matchup, ownership, salary, market support, and correlation with opposing bats.
- Avoid overfitting to raw optimizer projection when a lineup sacrifices stack quality, ceiling, leverage, uniqueness, or game-script coherence.
- Optimizer ranking is subordinate to strategic fit within the portfolio.
- Fixed mathematical scores are evidence summaries, not automatic exposure instructions.

## Required MLB Agent Team

Every MLB slate build uses the full core agent team plus these specialized passes:

- Industry Research / Market Consensus Agent
- Simulation / Outcome Distribution Agent
- Stack Architecture Agent
- Pitcher Failure / Opposing Stack Agent
- Duplication / Lineup Uniqueness Agent
- Portfolio Risk Manager Agent

Default MLB handoff chain:

Slate Intake -> Industry Research / Market Consensus -> Projection Audit -> News & Role -> Simulation / Outcome Distribution -> Ownership & Leverage -> Stack Architecture -> Pitcher Failure / Opposing Stack -> Correlation / Game Script -> Portfolio Builder -> Duplication / Lineup Uniqueness -> Portfolio Risk Manager -> Exposure Auditor -> Post-Slate Learning.

These passes are mandatory reasoning stages for MLB, even when implemented within one chat session rather than as autonomous background processes.

## Mandatory Industry Research / Market Consensus

Before any serious MLB portfolio is built, search the current industry and market. Sim Savant or any other uploaded source is a baseline, not the answer.

At minimum, when materially available, evaluate:

- sportsbook game totals
- implied team run totals
- moneylines
- opening vs current line movement
- relevant pitcher strikeout/outs/earned-run props
- park factors
- weather, wind, temperature, precipitation and delay risk
- confirmed starting pitchers
- official or expected batting orders
- injuries, scratches, rest and role/pitch-count news
- bullpen quality, workload and availability
- opposing pitcher quality and handedness
- platoon matchup context
- broader industry hitter/pitcher projections from multiple sources when possible
- broader industry projected ownership from multiple sources when possible
- simulation, ceiling or win-rate information when accessible

Use multiple independent sources when practical. Record source freshness/timestamps when useful. Never pretend a consensus exists when only one source is available.

### Industry Consensus Board

Every slate should create a structured consensus board before the Pitcher, Stack, Leverage, and Game Script agents make final recommendations. Capture when available:

- opening and current game totals
- implied team runs
- moneyline
- market movement
- pitcher prop expectations
- park/weather status
- lineup confirmation status
- bullpen and role notes
- Sim Savant/baseline projection
- each available independent industry projection
- industry projection range and median/consensus
- Sim Savant/baseline projected ownership
- each available independent industry projected ownership
- industry ownership range and median/consensus
- material source disagreement
- whether Sim Savant is inside consensus, high outlier, or low outlier
- AI interpretation and confidence

Observed facts must be separated from AI interpretation.

### Disagreement Is a Feature

Do not automatically average conflicting sources. Investigate why they disagree.

Examples:

- Savant likes an offense while the market total is moving down.
- Savant is lukewarm while implied runs, lineup quality, and other projections are improving.
- a high-owned pitcher has a good median projection but weak K prop, workload, or matchup support.
- a cheap hitter moves into a premium lineup slot before projections fully update.
- Savant ownership is materially higher or lower than multiple independent industry ownership projections.

A disagreement can indicate uncertainty, stale information, a genuine model edge, or no actionable signal. The AI must decide which and record the reason.

## Required Cross-Checks

Sim Savant or any baseline source must be checked against broader industry information. At minimum evaluate:

- implied team totals / run environment
- opposing pitcher quality and handedness
- park factors
- weather where material
- official starting batting orders
- multiple projected-ownership sources when accessible
- multiple projection sources when accessible
- meaningful injury/rest/scratch news

No one projection source is authoritative.

## Simulation / Outcome Distribution

Do not evaluate MLB only from median projections. Assess ceiling and failure distributions for hitters, pitchers, stacks, and game environments. Use Sim Savant simulations when available, then adjust confidence for current lineup, market, weather, matchup, industry disagreement, and ownership context.

The goal is not to predict one exact outcome; it is to identify which outcome families have enough probability and enough payoff to deserve portfolio exposure.

Simulation probabilities should inform game-script selection, not replace it. Two scenarios with similar probabilities may deserve very different exposure if one creates much stronger leverage or a less duplicated path to first place.

## Batting Order Adjustments

Re-evaluate projection and exposure when:

- an unexpected player leads off
- a cheap/value hitter moves into the top five
- a core hitter falls materially in the order
- a projected starter is scratched
- a team rests multiple regulars

A lineup-position change should influence plate-appearance expectation, stack connectivity, and ownership, not just raw player projection.

## Stack Evaluation

For each team, evaluate:

- implied scoring environment and market movement
- top-to-bottom lineup quality
- home-run and extra-base-hit ceiling
- matchup platoon advantages
- opposing pitcher failure path
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

Pitcher fades should never be mechanical. They must be supported by matchup, contact quality, platoon, park/weather, pitch-count/role, market/prop evidence, bullpen, ownership, or other evidence.

The strongest leverage spots often come from linked decisions: underweighting a fragile chalk pitcher while overweighting the offense that directly benefits if the pitcher fails.

## Game-Script Construction

Before final portfolio construction, create a slate-script board. Each major script should include:

- trigger condition
- evidence supporting the script
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

## AI Portfolio Authority

The AI Portfolio Builder is the final strategic authority for tournament lineup construction. Projections, optimizer outputs, composite scores, betting markets, and simulations are inputs. They do not automatically determine exposures.

Deterministic code should be used for tasks such as parsing, salary/position legality, duplicate checks, exposure arithmetic, contest assignment, and storage. If validation fails, return the lineup to the AI for repair without silently changing the slate thesis.

Material exposure decisions should be explainable through evidence + interpretation + game script.

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

A portfolio containing many different lineups can still represent the same underlying bet. The risk audit must identify that explicitly.

## Exposure Audit

Every MLB lineup set must include Sim Savant/source projected ownership vs DFS Engine final exposure with percentage-point difference.

When available, also include Savant/source prebuild portfolio exposure as a separate quantity and industry ownership consensus/range as a separate reference point.

Large differences should have a stated reason such as stack concentration, lineup-order value, ownership leverage, pitching ceiling, market/industry disagreement, uniqueness, game-script coverage, or reduced confidence in the source projection.

## Post-Slate Learning

Review not only which stack won but also:

- whether the engine owned the winning primary stack
- whether secondary-stack choices separated winners from near-misses
- whether SP1/SP2 construction was correct
- whether ownership leverage was appropriately allocated
- whether any value hitter became essential because of lineup position or salary
- whether duplication or salary construction limited top-end payout
- whether portfolio concentration was intentional or accidental
- whether our slate scripts were logically sound even if they did not occur
- whether the Industry Research Agent identified the important pre-slate signals
- whether the AI interpreted market/industry disagreement correctly
- whether Sim Savant was materially outside industry projection or ownership consensus and whether the Engine handled that appropriately
- whether the winning construction revealed a new strategic interaction or merely variance

### Counterfactual Review

Post-slate analysis must ask what would have happened if one decision changed while others stayed fixed. Examples:

- if our primary stack hit, would our pitcher construction still have failed?
- if our pitcher call was correct, was the secondary stack the real problem?
- if our leverage thesis was correct, did we simply lack enough exposure?
- if chalk failed as expected, did we choose the right alternative path?
- if a market or projection disagreement mattered, did we identify the right side before lock?

Do not conclude that a stack rule is correct merely because one winning lineup used it. Separate process quality from ordinary baseball variance.