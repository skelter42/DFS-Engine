# NFL DFS Engine

## Core Philosophy
NFL DFS should combine projection quality, outcome distributions, correlation, game environment, contest structure, and portfolio diversification. Classic generally offers stronger portfolio-building opportunities than showdown because more independent game environments can be expressed.

The engine should not depend on one third-party simulator or ownership source as a black box. Separate these problems:
1. project player outcomes,
2. define the high-quality lineup candidate universe,
3. model correlation/game scripts,
4. simulate outcomes where useful,
5. select a diversified portfolio,
6. use ownership/field estimates primarily as a game-theory and duplication layer rather than as the sole driver of lineup quality.

## Required Checks
- injuries and active/inactive status
- starting roles and depth chart
- spreads, totals, and implied team totals
- target/rush share and red-zone role
- projected ownership or field estimates when available
- weather where material

## Vegas-First Market Inputs
For every NFL `market inputs` pass, projection creation is Vegas-first. Do not use an industry fantasy projection as the primary replacement when sportsbook markets are available.

Projection source priority:
1. Sportsbook/player-prop markets across as many books as practical (DraftKings, FanDuel, BetMGM, Caesars, bet365, Fanatics and other credible books/odds aggregators).
2. Convert the betting market directly into DraftKings fantasy expectation using the canonical sportsbook projection methodology. Use the fullest available prop bundle by role: passing yards/TDs/INTs and rushing for QBs; rushing attempts/yards, receptions, receiving yards and TD probability for RBs; receptions, receiving yards, rushing usage and TD probability for WR/TE; game spread/total and team scoring expectation for DST/kickers where appropriate.
3. Use vig-free probabilities and consensus/median lines when multiple books are available. Line movement is actionable information and should influence the projection rather than being ignored.
4. If a player has only partial Vegas coverage, anchor the covered components to Vegas and use industry/model information only to fill the missing components.
5. Use broader industry projections only when sportsbook coverage is genuinely insufficient.
6. Sim Savant is a fallback/benchmark, not the primary source.

Never lower reported Vegas coverage merely because a player lacks one particular prop. A player with meaningful sportsbook markets should be classified as Vegas-driven or Vegas-anchored. Do not manufacture confidence for deep backups with no meaningful market; leave them on the best fallback source and label them accordingly.

For very early builds, preserve the Vegas-first hierarchy but mark projections provisional because props, injuries, depth-chart roles, weather and lines can move materially before lock. Re-run the market-input pass closer to lock whenever practical.

## Candidate Lineup Universe
A strong default portfolio process is:

1. Enumerate all legal DraftKings lineups for the slate when computationally practical, or generate a sufficiently exhaustive legal candidate set.
2. Rank candidates by frozen DFS Engine projection.
3. Retain a high-projection subset as the candidate universe. A top-10% projection filter is a useful default hypothesis, not a permanent law.
4. Backtest alternative candidate thresholds, including top 5%, top 10%, top 20%, and projection-loss thresholds relative to the optimal lineup.
5. Never assume the percentage cutoff has the same meaning across slates; record the projection spread from the optimal lineup to the cutoff.

The point of this stage is to ensure every lineup considered for the final portfolio belongs to a strong projection neighborhood before diversification is applied.

## Portfolio Diversification
Within the high-projection candidate universe, diversify intentionally rather than randomly.

Primary objective:
- maximize the number of distinct plausible paths to a tournament-winning outcome while preserving a strong average projection.

Useful portfolio-distance metrics include:
- number of differing players between lineups,
- overlapping player count,
- overlapping game stacks,
- overlapping team concentrations,
- repeated salary constructions,
- repeated chalk combinations,
- repeated game scripts.

A baseline selection process:
1. maximize average pairwise lineup uniqueness,
2. retain at least 90% of the maximum achievable uniqueness,
3. among sufficiently diverse solutions, maximize average projected points.

This is a portfolio-construction rule, not a projection adjustment.

## Correlation and Stacking
Correlation is essential and belongs in lineup construction and simulation, not as arbitrary bonus points added to player projections.

Core NFL relationships to represent:
- QB + pass catcher positive correlation,
- QB double-stack structures where slate context supports them,
- optional bring-backs driven by game script rather than forced mechanically,
- favored RB + DST positive game-script correlation,
- opposing passing volume rising in trailing scripts,
- negative or weak combinations such as an offensive player against the opposing DST,
- touchdown competition among teammates,
- concentration of fantasy production within specific game environments.

Field lineup generation and our own candidate generation should preserve realistic stack structures rather than sampling players independently.

## Simulation Layer
Projection alone ranks median/mean expectation. Tournament-winning outcomes depend on upper-tail results and correlated game environments.

The engine should carry underlying outcome distributions into lineup evaluation when possible rather than discarding them after calculating mean DK projection.

Preferred sequence:
1. freeze player expected-stat distributions,
2. simulate correlated game outcomes,
3. score every player under DraftKings rules,
4. score candidate lineups,
5. estimate lineup rates such as first-place proxy, top 0.1%, top 1%, top 10%, and cash where appropriate,
6. combine simulation evidence with projection quality and portfolio diversification.

Simulation should be an evidence layer, not an automatic override. Very small simulation counts can intentionally preserve noise, but larger simulation counts are needed for stable probability estimates. Store the simulation count and seed/configuration used.

## Ownership and Field Modeling
Ownership should not be treated as perfectly known. It is a noisy estimate of field behavior.

Short-term approach:
- use credible industry ownership consensus when obtainable,
- compare multiple sources rather than trusting a single source,
- retain our own ownership estimate separately,
- compare both to actual DraftKings ownership after lock.

Long-term engine goal:
- learn expected ownership from salary, projection, salary-adjusted projection, positional scarcity, optimal rate, role, injury news, team/game totals, and slate context,
- calibrate against actual DraftKings ownership from completed contests.

Ownership is most useful for:
- duplication risk,
- identifying overly common lineup combinations,
- leverage analysis,
- realistic field generation,
- contest-specific game theory.

Do not let uncertain ownership estimates automatically eliminate high-projection lineups.

## Expected Field Generation
A realistic field model must reproduce lineup behavior, not just individual player ownership percentages.

Model at two levels:

### Marginal ownership
Estimate each player's overall ownership.

### Conditional ownership / lineup structure
Represent how player selection changes after another player is already selected. Examples:
- P(WR1 | QB) differs from unconditional WR1 ownership,
- QB double-stack frequency,
- bring-back frequency,
- RB + DST frequency,
- salary-left distributions,
- number of players from the same game,
- cumulative lineup ownership,
- cheap-value + spend-up combinations,
- chalk-on-chalk construction frequency.

Generate thousands of plausible field lineups whose aggregate player ownership and lineup structures converge toward these targets.

## Optimal Rate
Keep optimal rate separate from projected ownership.

Optimal rate = percentage of simulated outcome worlds in which a player appears in the highest-scoring or otherwise optimal DraftKings lineup.

This is useful because:
- projection + salary alone does not capture all slate-relative lineup demand,
- optimal rate helps identify players who frequently belong in tournament-winning constructions,
- actual field ownership can be compared against optimal rate to identify over- or under-owned areas.

Optimal rate is a model output, not a substitute for actual ownership.

## Contest-Specific Learning
The engine should learn from the contests we actually play.

After each slate, save:
- actual player ownership,
- actual top-lineup constructions,
- QB stack frequencies,
- double-stack frequencies,
- bring-back frequencies,
- salary used/left,
- cumulative ownership,
- team/game concentration,
- duplicated lineup structures where observable,
- winning/top-0.1%/top-1%/top-10% lineup characteristics,
- our lineup outcomes.

Use completed DraftKings standings as the primary calibration label for field behavior.

Do not promote a new rule from one slate. Track persistent error before changing durable logic.

## Showdown
Treat Showdown as a distinct, duplication-sensitive format.

Requirements:
- Captain projection = 1.5x FLEX projection, applied once,
- model Captain ownership separately from FLEX ownership where data exist,
- emphasize game-script coherence,
- measure duplication risk aggressively,
- test rules such as at least one QB in FLEX before promoting them to core logic,
- preserve multiple plausible scripts instead of forcing one median build.

## Savant Role
Sim Savant can be used as:
- a benchmark projection source,
- a candidate-lineup generator,
- a comparison simulator,
- a diagnostic for disagreement.

It should not be treated as authoritative when its player projections or simulated field appear inconsistent with market data or actual contest behavior.

The long-term objective is a self-contained DFS Engine capable of:
Vegas projections -> outcome distributions -> candidate lineup universe -> correlated simulations -> field model -> contest simulation -> diversified 20-lineup portfolio.

## Exposure Audit
Every delivered lineup set should include:
- source/consensus projected ownership when available,
- DFS Engine final exposure,
- percentage-point difference,
- explanations for meaningful deviations,
- projection percentile or distance from optimal,
- stack/correlation summary,
- relevant simulation rates,
- duplication/field-risk flags when available.

## Research / Validation Questions
These remain hypotheses until backtested:
- Is top 10% by projection the best candidate cutoff?
- Is a fixed percentile or points-from-optimal threshold more stable across slates?
- How much simulated top-1% rate should influence portfolio selection relative to projection?
- Which lineup-distance metric best improves 20-max portfolio performance?
- How much does ownership add after high-projection filtering, correlation, and diversification?
- Which field-construction statistics most improve duplication estimates?
