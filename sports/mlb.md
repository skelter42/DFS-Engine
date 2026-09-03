# MLB DFS Engine

## Core Construction Philosophy

MLB is a high-variance, correlation-heavy sport. The engine should prioritize coherent team-stack outcomes over isolated median projections.

### Default GPP Priorities

- Strong preference for full 5-man primary stacks on DraftKings when slate size supports it.
- Secondary correlation matters; do not treat the remaining hitters as random salary fillers.
- Pitcher decisions should consider strikeout ceiling, run prevention, matchup, ownership, salary, and correlation with opposing bats.
- Avoid overfitting to raw optimizer projection when a lineup sacrifices stack quality or ceiling.

## Required MLB Agent Team

Every MLB slate build uses the full core agent team plus these specialized passes:

- Simulation / Outcome Distribution Agent
- Stack Architecture Agent
- Pitcher Failure / Opposing Stack Agent
- Duplication / Lineup Uniqueness Agent
- Portfolio Risk Manager Agent

Default MLB handoff chain:

Slate Intake -> Projection Audit -> News & Role -> Market Environment -> Simulation / Outcome Distribution -> Ownership & Leverage -> Stack Architecture -> Pitcher Failure / Opposing Stack -> Correlation / Game Script -> Portfolio Builder -> Duplication / Lineup Uniqueness -> Portfolio Risk Manager -> Exposure Auditor -> Post-Slate Learning.

These passes are mandatory reasoning stages for MLB, even when implemented within one chat session rather than as autonomous background processes.

## Required Cross-Checks

Sim Savant or any baseline source must be checked against broader industry information. At minimum evaluate:

- implied team totals / run environment
- opposing pitcher quality and handedness
- park factors
- weather where material
- official starting batting orders
- projected ownership
- meaningful injury/rest/scratch news

No one projection source is authoritative.

## Simulation / Outcome Distribution

Do not evaluate MLB only from median projections. Assess ceiling and failure distributions for hitters, pitchers, stacks, and game environments. Use Sim Savant simulations when available, then adjust confidence for current lineup, market, weather, matchup, and ownership context.

The goal is not to predict one exact outcome; it is to identify which outcome families have enough probability and enough payoff to deserve portfolio exposure.

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

- implied scoring environment
- top-to-bottom lineup quality
- home-run and extra-base-hit ceiling
- matchup platoon advantages
- bullpen path
- ownership of the full stack, not only individual hitters
- availability of low-owned connective value
- wraparound connectivity and lineup-order structure
- salary efficiency of the full stack
- likelihood that the field uses the same exact combination

The goal is to identify combinations where team ceiling is under-owned relative to the field.

## Pitcher Failure Leverage

Popular pitcher exposure must be evaluated together with the opposing offense. When a chalk pitcher has a realistic failure path, the Engine should consider whether the opposing stack offers asymmetric leverage.

Pitcher fades should never be mechanical. They must be supported by matchup, contact quality, platoon, park/weather, pitch-count/role, bullpen, ownership, or other evidence.

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

Large differences should have a stated reason such as stack concentration, lineup-order value, ownership leverage, pitching ceiling, uniqueness, game-script coverage, or reduced confidence in the source projection.

## Post-Slate Learning

Review not only which stack won but also:

- whether the engine owned the winning primary stack
- whether secondary-stack choices separated winners from near-misses
- whether SP1/SP2 construction was correct
- whether ownership leverage was appropriately allocated
- whether any value hitter became essential because of lineup position or salary
- whether duplication or salary construction limited top-end payout
- whether portfolio concentration was intentional or accidental

### Counterfactual Review

Post-slate analysis must ask what would have happened if one decision changed while others stayed fixed. Examples:

- if our primary stack hit, would our pitcher construction still have failed?
- if our pitcher call was correct, was the secondary stack the real problem?
- if our leverage thesis was correct, did we simply lack enough exposure?
- if chalk failed as expected, did we choose the right alternative path?

Do not conclude that a stack rule is correct merely because one winning lineup used it. Separate process quality from ordinary baseball variance.