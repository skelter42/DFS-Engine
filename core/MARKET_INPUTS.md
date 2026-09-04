# Market Inputs

## Purpose

This is the cross-sport market-input workflow for Sim Savant. Its only job is to take an attached Sim Savant projection CSV and return the same import structure with the best available **full-slate market-derived fantasy projections** and the best available estimate of **expected field ownership**.

The user specifies the sport. This process researches the relevant betting markets, player props, game lines, site scoring, slate context, and ownership signals for that sport.

Sim Savant remains responsible for simulation, lineup generation, finish-rate ranking, exposure spreading, stack/correlation settings, and contest setup. Market Inputs does not build or optimize lineups.

## Trigger

Use:

**`Market Inputs — [SPORT]`**

Examples:
- `Market Inputs — MLB`
- `Market Inputs — NFL`
- `Market Inputs — NBA`
- `Market Inputs — NHL`
- `Market Inputs — NCAAF`
- `Market Inputs — Tennis`

## Full-run requirement — mandatory

Every `Market Inputs — [SPORT]` request is a **full slate-wide research pass by default**. Do not substitute a quick targeted adjustment pass unless the user explicitly asks for one.

A valid full run must:
1. Read the entire attached Savant player pool.
2. Identify every game/event on the slate.
3. Research game-level markets for every game/event.
4. Research player-level props for as much of the slate as the public market actually offers.
5. Use multiple books/sources where practical, not one sportsbook or one DFS source.
6. Convert those expectations into the correct site-specific fantasy scoring.
7. Build ownership from multiple current site/slate-specific ownership touch points plus the behavioral ownership model below.
8. Use Savant only as a documented fallback for players/markets with insufficient public coverage.
9. Audit the completed file and return it.
10. Stop.

### No partial-run masquerading

Do not call a file “Market Inputs complete” if only a small subset of players were researched or adjusted.

If broad market coverage is unavailable, say so explicitly and quantify:
- how many players were market-rich
- how many were market-supported
- how many required sparse-market inference
- how many remained fallback-heavy

If the run is fallback-heavy, label it as such rather than implying a fully market-derived slate.

## Projection principle

**Betting markets create the statistical expectation; site scoring converts that expectation into DFS points.**

Use multiple sportsbooks and both sides of priced markets when available. A posted prop line without juice is not a complete expectation. De-vig and consensus prices where practical. Prefer broad market agreement to any one book.

Reconcile player props with game-level markets so individual projections do not collectively imply a materially different game environment from the betting market without a documented reason.

Relevant markets depend on sport. Examples:
- MLB: pitcher K, outs, ER, hits/walks allowed, win; hitter hits, total bases, HR, RBI, runs, walks, SB, combo props; game total, ML, run line, team totals.
- NFL/NCAAF: passing/rushing/receiving yards, receptions, TDs, attempts, completions, interceptions; spread, total, team totals.
- NBA: points, rebounds, assists, 3PM, steals/blocks where available, turnovers where relevant; spread, total, team totals, minutes/injury context.
- NHL: shots, goals, points, goalie saves/goals allowed/win; game total, ML, team totals, PP/line context.
- Tennis: match/set/game markets, moneyline, total games, aces/double faults/break markets where available.

Use lineup/role/minutes/workload/injury/weather/venue context only to allocate market expectation appropriately. Independent DFS projections are sanity checks, not automatic overrides. Savant is the conservative fallback for sparse markets; never invent precision.

## Projection research standard

For each slate, collect as many of these as legitimately available:
- multiple sportsbook prices for the same prop
- both over and under prices when possible
- game totals, spreads/moneylines and team totals
- correlated player markets where useful
- recent line movement when material
- confirmed starting/lineup/role information
- site-specific DFS scoring rules

Where many books disagree, prefer a consensus expectation rather than cherry-picking the most favorable line.

Where direct props are missing, infer conservatively from team/game markets, role, workload and independent projections. Do not simply apply a flat multiplier to Savant and call it market-derived.

## Ownership is a field-behavior forecast

Ownership is harder than projection because it is not simply about what will happen. It is a forecast of what DFS entrants will choose after seeing salaries, projections, news, optimizer outputs, industry content, and slate structure.

The goal is:

**`Own = best estimate of actual site/slate field roster percentage`**

It must be objective. Never change ownership to create leverage, force Savant toward a player, or manufacture a desired portfolio.

### Step 1 — Numeric ownership consensus
Collect as many current, legitimate, site-specific ownership projections as accessible.

Rules:
- Savant is one source, not the authority.
- Prefer several independent numeric sources.
- Match the exact site and slate.
- Weight fresher updates more heavily as lock approaches.
- Use a median, trimmed consensus, or reliability-weighted consensus so one outlier cannot dominate.
- Do not mix DK and FD ownership directly.
- Do not mix main-slate and short-slate ownership directly.
- Do not claim broad consensus if only one numeric source was available.

If multiple reliable sources agree closely, that consensus should carry heavy weight.

### Step 2 — Reconstruct what the field sees
For every player, estimate the information that a sharp DFS field and common optimizers are reacting to:
- site salary and salary rank
- market-derived fantasy projection
- points-per-dollar/value
- position or roster-slot scarcity
- role, lineup spot, minutes/workload and confirmed news
- game/team implied scoring environment
- stacking/correlation popularity where relevant
- opportunity cost versus alternatives at the same position/salary tier
- obvious salary relief/value created by news
- star/name recognition and obvious slate narratives
- industry tout frequency and consensus
- recent ownership-moving news
- likely optimizer behavior and common lineup construction paths

This layer is not used to invent ownership. It is used to determine whether the published numeric consensus is behaviorally plausible.

### Step 3 — Team/game/stack ownership reconciliation
Ownership must be coherent at the portfolio level.

Estimate which teams, games, stacks, stars, value plays, and salary constructions the field is likely to prioritize. Player-level ownership should make sense relative to those aggregate stories.

Examples:
- In MLB, if a team is projected to be the most popular stack, its core hitters should not all project as low-owned unless there is a salary/position reason.
- In NFL/NCAAF, a popular QB/WR game stack should be reflected in correlated ownership.
- In NBA, a newly opened value play can increase ownership on both that player and expensive stars that the salary relief enables.

### Step 4 — Behavioral sanity model
Treat ownership as a probability of roster selection and compare the numeric consensus with a behavioral model driven by:
- projection
- value
- salary
- role
- position
- Vegas environment
- industry attention
- roster construction
- correlation/stacking context

The behavioral model is a sanity check, not a replacement for real ownership data.

Large disagreements require investigation. If Savant says 8% but several industry sources, value metrics, and public content imply 25%+, do not ship 8% without resolving why.

### Step 5 — Site/slate calibration
Ownership is site- and slate-specific.

Calibrate for:
- DraftKings vs FanDuel salary structure
- roster rules and positional flexibility
- slate size
- number of viable alternatives
- amount of obvious value
- concentrated vs flat projection landscape
- common optimizer construction paths
- stack requirements/correlation incentives where relevant

The same player can correctly have very different ownership across DK and FD.

### Step 6 — Final ownership estimate and confidence
Produce the final `Own` using numeric consensus as the anchor, modified only when credible behavioral evidence shows the consensus is stale or inconsistent.

Assign an internal ownership confidence tier:
- **A — High confidence:** multiple fresh numeric sources agree and the field story supports them.
- **B — Good confidence:** several signals with modest disagreement.
- **C — Sparse:** limited numeric coverage; behavioral inference contributes materially.
- **D — Fallback-heavy:** retain Savant/industry baseline conservatively.

When confidence is low, avoid false precision and make smaller changes from Savant.

### Ownership audit failures
Treat the following as failures that must be investigated before delivery:
- a universally touted obvious value modeled as nearly unowned
- a highly popular projected stack whose core players are all modeled low-owned
- a player with extreme ownership that has no plausible salary/value/role/field explanation
- using stale ownership after material injury/lineup news
- mixing ownership from the wrong site or slate
- large ownership changes with no observable field-behavior explanation
- calling ownership “industry consensus” when only one source was checked

## Projection confidence

Assign an internal projection confidence tier:
- **A — Market-rich:** multiple direct props across multiple books plus stable game markets.
- **B — Market-supported:** some direct props plus strong game context and independent projection support.
- **C — Sparse market:** limited direct props; use game/team market plus context and projection consensus.
- **D — Fallback:** insufficient market coverage; use Savant/projection consensus conservatively.

The final CSV does not need to include confidence tiers unless requested.

## Output contract

Return exactly the source Savant import structure, normally:

`Name, DFS ID, Proj, Own`

- `Proj` = site-specific fantasy points.
- `Own` = expected site/slate field ownership percentage.
- Preserve source names and DFS IDs whenever possible.

## Mandatory import audit

Every returned file must pass:
1. Exact source column structure preserved.
2. Correct sport/site scoring system used.
3. No duplicate DFS IDs.
4. No duplicate exact-name mapping conflicts.
5. Remove dead duplicate identities when one live identity exists.
6. Omit a known Savant ambiguous-name row only when its projection/ownership remain unchanged, allowing Savant to retain its existing value.
7. `Proj` numeric and non-negative.
8. `Own` numeric when present and between 0 and 100.
9. Zero projections intentional.
10. Largest projection and ownership changes reviewed for plausibility.
11. Return a short audit summary: rows in/out, mapping conflicts, projection changes, ownership changes, and fallback-heavy areas.
12. Return coverage counts by confidence tier or equivalent market-coverage summary.

## Hard stop

Market Inputs does **not**:
- build lineups
- simulate lineups
- rank lineups
- optimize lineups
- set exposures
- choose stacks
- allocate contests
- alter projections to manufacture leverage
- alter ownership to manufacture leverage

After returning the audited CSV, stop. The user performs lineup generation and exposure spreading inside Sim Savant and may send the resulting portfolio back for a separate final game-theory/exposure audit.

## Core philosophy

**Markets estimate what happens. Ownership estimates what the field will play. Savant builds the lineups.**

Every Market Inputs invocation is a full slate-wide research pass unless the user explicitly requests a quicker targeted adjustment.

Keep projection quality, ownership forecasting, and portfolio game theory separate so each layer can be evaluated honestly.