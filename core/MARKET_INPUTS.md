# Market Inputs

## Purpose

This is the cross-sport market-input workflow for Sim Savant. Its narrow responsibility is to take an attached Sim Savant projection CSV and return the same import structure with the best available market-derived fantasy projections and expected field ownership.

The user specifies the sport. This process researches the relevant betting markets, props, DFS industry information, site scoring, slate context, and ownership signals for that sport.

Sim Savant remains responsible for simulation, lineup generation, finish-rate ranking, exposure spreading, stack/correlation settings, and contest setup. Market Inputs does not build or optimize lineups.

## Trigger

**`Market Inputs — [SPORT]`**

Examples: `Market Inputs — MLB`, `Market Inputs — NFL`, `Market Inputs — NBA`, `Market Inputs — NHL`, `Market Inputs — NCAAF`, `Market Inputs — Tennis`.

When invoked with a Savant projection file:
1. Identify sport, site, slate, player pool, names and DFS IDs.
2. Research as many current reliable sportsbook/game/prop touch points as practical for that sport.
3. Convert market expectations into the correct DraftKings/FanDuel scoring system.
4. Estimate site-specific expected ownership using the ownership process below.
5. Use original Savant values only as fallback when market/industry coverage is insufficient.
6. Preserve exact Savant import structure and IDs.
7. Run mandatory import/mapping audit.
8. Return the clean CSV and stop.

## Projection principle

**Betting markets create the statistical expectation; site scoring converts that expectation into DFS points.**

Use multiple sportsbooks and both sides of priced markets when available. Do not treat a posted line without juice as the complete expectation. De-vig/consensus prices where practical. Reconcile player props with game-level markets so individual projections do not collectively imply a materially different game environment from the betting market without a documented reason.

Relevant markets depend on sport. Examples:
- MLB: K, outs, ER, hits/walks allowed, win; hitter hits/TB/HR/RBI/runs/BB/SB; game total, ML, run line, team totals.
- NFL/NCAAF: passing/rushing/receiving yards, receptions, TDs, attempts, completions, interceptions; spread, total, team totals.
- NBA: points, rebounds, assists, 3PM, steals/blocks where available, turnovers where relevant; spread, total, team totals, minutes/injury context.
- NHL: shots, goals, points, goalie saves/goals allowed/win; game total, ML, team totals, PP/line context.
- Tennis: match/set/game markets, moneyline, total games, aces/double faults/break markets where available.

Use lineup/role/minutes/workload/injury/weather/venue context to allocate market expectation appropriately. Independent DFS projections are sanity checks, not automatic overrides. Savant is the conservative fallback for sparse markets; never invent precision.

## Ownership is a field-behavior forecast

Ownership is not derived directly from Vegas. It estimates what DFS entrants will choose after seeing salary, projections, news and industry content.

### Step 1 — Numeric industry consensus
Collect as many current, legitimate, site-specific ownership projections as accessible. Savant is one source, not the authority. Prefer several independent sources. Normalize to the exact site/slate and weight fresher updates more heavily near lock. Use a median/trimmed or reliability-weighted consensus so one outlier cannot dominate.

### Step 2 — Reconstruct what the field sees
For every player, evaluate the inputs likely to drive public selection:
- site salary and salary rank
- market-derived projection and points-per-dollar/value
- position/roster-slot scarcity
- role, lineup spot, minutes/workload and confirmed news
- game/team implied scoring environment
- stacking/correlation popularity where relevant
- opportunity cost versus alternatives at the same position/salary tier
- star/name recognition and obvious slate narratives
- recent lineup/injury/value news
- industry tout frequency and consensus
- likely optimizer behavior and common construction paths

### Step 3 — Team/game/stack ownership reconciliation
Individual ownership cannot be evaluated independently. Estimate which teams, games, stacks and salary constructions the field is likely to prioritize. Player ownership should be coherent with those aggregate stories. In stack-heavy sports, account for correlated ownership rather than treating every player as an isolated selection.

### Step 4 — Model-based ownership sanity check
Treat ownership as a probability of roster selection. Compare the numeric consensus with a behavioral model based on projection/value, salary, position, role, game environment and public attention. This is a sanity check, not a license to invent numbers. Large disagreements require investigation.

### Step 5 — Contest/site calibration
Ownership is site- and slate-specific. DraftKings and FanDuel salary structures and roster rules can create very different ownership for the same player. Calibrate to slate size, roster positions, available value, number of viable alternatives and common optimizer constructions. Do not mix ownership projections from different sites or slates without adjustment.

### Step 6 — Final consensus and confidence
Assign an internal ownership confidence:
- A: multiple fresh numeric sources agree and field story supports them.
- B: multiple signals with modest disagreement.
- C: sparse numeric coverage; behavioral inference materially contributes.
- D: fallback-heavy; retain Savant/industry baseline conservatively.

If the industry consensus says a player is nearly unowned while salary/value/news/tout behavior strongly implies popularity, treat it as an audit failure until explained. Conversely, do not raise ownership merely because a player projects well if roster construction or opportunity cost makes the play difficult.

## Ownership guardrails

Ownership must remain an objective prediction of the field. Never alter ownership to create leverage, force Savant to select/fade a player, or manufacture a desired portfolio. Game theory happens after Savant builds the portfolio.

Before delivery, inspect the largest ownership changes from the source file and explain any material change through observable field drivers. Avoid false precision when data is sparse.

## Output contract

Return exactly the source Savant import structure, normally:
`Name, DFS ID, Proj, Own`

`Proj` is site-specific fantasy points. `Own` is expected site/slate field ownership percentage.

## Mandatory import audit

1. Preserve source names and DFS IDs unless a known Savant mapping exception requires omission.
2. Correct sport/site scoring.
3. No duplicate DFS IDs.
4. No duplicate exact-name mapping conflicts.
5. Remove dead duplicate identities when one live identity exists.
6. Omit a known Savant ambiguous-name row only when its projection/ownership remain unchanged, allowing Savant to retain the existing value.
7. Proj numeric and non-negative.
8. Own numeric when present and 0–100.
9. Zero projections intentional.
10. Report rows in/out, mapping conflicts, projection/ownership changes and fallback-heavy areas.

## Hard stop

Market Inputs does not build, simulate, rank, optimize, set exposures, choose stacks or allocate contests. After returning the audited CSV, stop. The user performs those tasks in Sim Savant and may send the resulting portfolio back for a separate final audit.

## Core philosophy

**Markets estimate what happens. Ownership estimates what the field believes/plays. Savant builds the lineups.**

Keep all three layers independent so projection quality, ownership forecasting and portfolio game theory can each be evaluated honestly.