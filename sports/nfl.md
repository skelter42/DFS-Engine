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

## Vegas-First Market Inputs
For every NFL `market inputs` pass, projection creation is Vegas-first. Do not use an industry fantasy projection as the primary replacement when sportsbook markets are available.

Projection source priority:
1. Sportsbook/player-prop markets across as many books as practical (DraftKings, FanDuel, BetMGM, Caesars, bet365, Fanatics and other credible books/odds aggregators).
2. Convert the betting market directly into DraftKings fantasy expectation using the official DK scoring rules. Use the fullest available prop bundle by role: passing yards/TDs/INTs and rushing for QBs; rushing attempts/yards, receptions, receiving yards and TD probability for RBs; receptions, receiving yards, rushing usage and TD probability for WR/TE; game spread/total and team scoring expectation for DST/kickers where appropriate.
3. Use vig-free probabilities and consensus/median lines when multiple books are available. Line movement is actionable information and should influence the projection rather than being ignored.
4. If a player has only partial Vegas coverage, anchor the covered components to Vegas and use industry/model information only to fill the missing components.
5. Use broader industry projections only when sportsbook coverage is genuinely insufficient.
6. Sim Savant is the final fallback, not the primary source.

Never lower the reported Vegas coverage merely because a player lacks one particular prop. A player with meaningful sportsbook markets should be classified as Vegas-driven or Vegas-anchored. Do not manufacture confidence for deep backups with no meaningful market; leave them on the best fallback source and label them accordingly in analysis.

For very early builds, preserve the Vegas-first hierarchy but mark projections provisional because props, injuries, depth-chart roles, weather and lines can move materially before lock. Re-run the market-input pass closer to lock whenever practical.

## Correlation
Use QB-pass catcher stacks as a foundational correlation tool. Bring-backs should be driven by game script and ownership rather than forced mechanically. Running backs can correlate strongly with favored game scripts; opposing passing volume can rise in those same scripts.

## Showdown
Treat showdown as a distinct, duplication-sensitive format. Use uniqueness and game-script coherence aggressively. When testing showdown rules, explicitly track whether constraints such as at least one QB in flex improve results before promoting them to core logic.

## Exposure Audit
Every delivered lineup set must include source projected ownership vs DFS Engine exposure with percentage-point difference and explanations for meaningful deviations.