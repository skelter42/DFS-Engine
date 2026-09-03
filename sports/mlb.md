# MLB DFS Engine

## Core Construction Philosophy

MLB is a high-variance, correlation-heavy sport. The engine should prioritize coherent team-stack outcomes over isolated median projections.

### Default GPP Priorities

- Strong preference for full 5-man primary stacks on DraftKings when slate size supports it.
- Secondary correlation matters; do not treat the remaining hitters as random salary fillers.
- Pitcher decisions should consider strikeout ceiling, run prevention, matchup, ownership, salary, and correlation with opposing bats.
- Avoid overfitting to raw optimizer projection when a lineup sacrifices stack quality or ceiling.

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

The goal is to identify combinations where team ceiling is under-owned relative to the field.

## Portfolio Coverage

Across multiple lineups, intentionally cover different plausible slate outcomes:

- chalk offense succeeds
- chalk offense fails
- elite pitcher dominates
- value pitcher unlocks premium bats
- lower-owned team breaks the slate
- one game becomes a shootout

Coverage must remain concentrated enough that a correct thesis can generate multiple top-end lineups.

## Exposure Audit

Every MLB lineup set must include Sim Savant/source projected ownership vs DFS Engine final exposure with percentage-point difference.

Large differences should have a stated reason such as stack concentration, lineup-order value, ownership leverage, pitching ceiling, or reduced confidence in the source projection.

## Post-Slate Learning

Review not only which stack won but also:

- whether the engine owned the winning primary stack
- whether secondary-stack choices separated winners from near-misses
- whether SP1/SP2 construction was correct
- whether ownership leverage was appropriately allocated
- whether any value hitter became essential because of lineup position or salary

Do not conclude that a stack rule is correct merely because one winning lineup used it.