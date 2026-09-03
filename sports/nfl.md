# NFL DFS Engine

## Core Philosophy
NFL DFS should combine projection, ceiling, ownership, correlation, game environment, and contest structure. Classic generally offers stronger portfolio-building opportunities than showdown because more independent game environments can be expressed.

## Required Checks
- injuries and active/inactive status
- starting roles and depth chart
- spreads, totals, and implied team totals
- target/rush share and red-zone role
- projected ownership
- weather where material

## Correlation
Use QB-pass catcher stacks as a foundational correlation tool. Bring-backs should be driven by game script and ownership rather than forced mechanically. Running backs can correlate strongly with favored game scripts; opposing passing volume can rise in those same scripts.

## Showdown
Treat showdown as a distinct, duplication-sensitive format. Use uniqueness and game-script coherence aggressively. When testing showdown rules, explicitly track whether constraints such as at least one QB in flex improve results before promoting them to core logic.

## Exposure Audit
Every delivered lineup set must include source projected ownership vs DFS Engine exposure with percentage-point difference and explanations for meaningful deviations.