# MLB Market Inputs Process

## Purpose

This file defines one narrow responsibility for the DFS Engine: **produce slate-ready player projections and ownership estimates from betting-market and industry information for import into Sim Savant.**

Sim Savant remains responsible for simulation, lineup generation, 1% finish-rate ranking, exposure spreading, stack settings, and contest setup. This process does **not** build or optimize lineups.

**Projection standard (authoritative):** `core/MARKET_PROJECTIONS.md` — pure numeric conglomerate (industry scrape + Vegas scrape → composite). Goal is objective consensus, not beating the market. For projection-only passes, `sports/mlb_market_inputs_projection_override.md` takes precedence on Proj rules.

## Easy trigger keywords

Use these short commands in chat:

- **`Savant Prep`** = run this market-input process only on the attached Sim Savant projection CSV.
- **`Savant Check`** = audit a completed Sim Savant lineup/export file for final exposure, salary, correlation, Vegas-story, ownership, and game-theory issues. Do not rebuild lineups unless explicitly asked.

## Strict operating contract

### `Savant Prep` means exactly

When the user attaches a Sim Savant projection file and says **`Savant Prep`**:

1. Read the attached Sim Savant projection CSV.
2. Identify the site (DraftKings or FanDuel), slate, player pool, player names, and DFS IDs.
2a. **Trust Savant zeros (mandatory).** If source `Proj` is `0` (or blank treated as 0), leave `Proj = 0`. Do not research props, industry projections, or ownership for those players. Keep the rows in the output file so import structure is preserved. Industry numeric + Vegas prop work applies only to the **positive-Proj pool**. Coverage grades and the 10+ industry target are measured against that positive pool, not the raw 1,000-row file.
3. Run an **exhaustive sportsbook sweep and industry numeric-source sweep** on the positive-Proj pool before accepting fallback. **Preferred method: board-level / aggregator-first.** Hit multi-player prop boards and aggregators that surface many lines at once (PropCruncher, Covers matchup prop sections, Action Network boards, PropPrizm, FanDuel Research, etc.) before falling back to player-by-player searches. Only deep-dive individual players for material gaps after the board sweep.
4. For pitchers in the positive-Proj pool, actively search every practical component market: strikeouts, outs recorded, earned runs allowed, hits allowed, walks allowed, win probability/moneyline, and any quality-start-relevant markets.
5. For hitters in the positive-Proj pool, actively search every practical component market: hits, total bases, home runs, RBI, runs, walks/HBP, stolen bases, H+R+RBI, and similar combo markets.
6. Use the odds/juice and multiple books where available. A posted line without price context is weaker evidence than a market with both sides/juice.
7. Build the objective consensus composite projection (industry numeric + Vegas) per `core/MARKET_PROJECTIONS.md` and convert into the correct site scoring system.
8. Reconcile player-level projections to game totals, implied team totals, lineup slot, park/weather/roof status, matchup and expected workload/plate appearances (data only; no narrative).
9. Build the best current site-specific ownership estimate from multiple reputable DFS-industry ownership sources/signals (or leave Own unchanged on projection-only passes).
10. Use the original Sim Savant `Proj` and/or `Own` only as a true fallback after the market/industry sweep is exhausted for that **positive-Proj** player. Zero-Proj players stay at 0 by rule, not as researched fallback.
11. Preserve the exact Savant import structure and DFS IDs.
12. Run all import/mapping/duplicate/zero-value audit checks.
13. Run the **AI quality-grade gate** described below. A market-input pass graded below **A** is incomplete and must continue researching/refining before delivery unless the user explicitly asks to stop.
14. Return the clean CSV to the user.
15. **Stop.** Do not continue into lineup generation, lineup simulation, exposures, stacks, contest allocation, or portfolio game theory.

### Non-negotiable market-coverage rule

Do **not** stop after finding a small convenient subset of props. The fact that direct props were found for a few pitchers or star hitters is not evidence that the rest of the **positive-Proj** slate is market-thin.

Before labeling a **positive-Proj** player as fallback, the process must make a real effort to exhaust the available market surface **and** independent numeric industry sources:

- multi-player prop boards and aggregators first (PropCruncher, Covers, Action Network, PropPrizm, etc.)
- direct sportsbooks
- pitcher component markets
- hitter component markets
- combo markets
- game-level markets
- independent numeric DFS projection systems (target 10+ when available)

If the slate has broad public prop and industry coverage, the final output should reflect broad composite-supported projection coverage.

### Projection provenance requirement

Track an internal source/provenance label for every player projection, even though the final Savant import remains only `Name, DFS ID, Proj, Own`.

Use these labels:

- **VEGAS_DIRECT** — projection materially built from one or more direct player props with pricing/juice.
- **VEGAS_SUPPORTED** — limited direct props plus game/team market and industry support.
- **INDUSTRY_BLEND** — deep industry numeric consensus with thin or no direct props; game markets still used for reconciliation.
- **SAVANT_FALLBACK** — insufficient market and independent industry coverage; original Savant projection retained conservatively. Zero-Proj rows that were never researched stay `0` and are not counted in the active-pool fallback percentage.

### Mandatory coverage summary before delivery

Every Savant Prep run must report the projection-source counts for the **active positive-projection player pool** (Savant `Proj` > 0):

- number and percentage `VEGAS_DIRECT`
- number and percentage `VEGAS_SUPPORTED`
- number and percentage `INDUSTRY_BLEND`
- number and percentage `SAVANT_FALLBACK`
- industry source count used (target 10+)

Also report ownership-source coverage where practical: industry consensus vs Savant fallback.

### AI quality-grade gate — mandatory

Before any market-input CSV is called final, the AI must grade the pass on **projection quality** (and ownership quality when ownership is in scope) using current evidence.

Use letter grades: `A+`, `A`, `A-`, `B+`, `B`, `B-`, `C`, or `Incomplete`.

A final pass must receive an **overall grade of A or A+**. Anything below A is a failure of the market-input process and requires another research/refinement pass before delivery unless the user explicitly instructs otherwise.

#### Projection grade criteria

- breadth of **numeric** industry sources (target 10+)
- breadth and freshness of sportsbook/player-prop coverage
- use of juice and multi-book consensus where available
- pitcher/hitter component completeness
- reconciliation to game totals and implied team totals
- correct site scoring conversion
- provenance honesty and fallback burden
- **no narrative in Proj**

#### Required grade report

- `Projection grade: <grade>`
- industry source count
- Vegas coverage summary
- provenance mix
- remaining fallback/uncertainty if any

### `Savant Prep` explicitly does NOT

- build lineups
- optimize lineups
- simulate lineups
- rank lineups by 1% finish rate
- set or recommend exposures
- choose stacks
- allocate contests
- alter projections to manufacture leverage
- inject narrative into projections
- apply portfolio game theory
- duplicate any task Sim Savant already handles in its interface
- research Savant-zero players

The user handles lineup generation, 1% finish-rate sorting, exposure spreading, stack settings, and contest setup inside Sim Savant.

### `Savant Check` means exactly

After the user builds the portfolio in Sim Savant and sends the resulting lineup/export file with **`Savant Check`**:

1. Audit the finished portfolio against Vegas expectations, player salary, expected ownership, correlation, stack construction, exposure concentration, and tournament game theory.
2. Identify only material issues, including specific exposure caps/floors when warranted.
3. Explain whether the portfolio's overall story is coherent with Vegas, salary, and field expectations.
4. Do **not** rebuild or replace the portfolio unless explicitly asked.

## Output contract

For each site/slate, output exactly:

`Name, DFS ID, Proj, Own`

- `Proj` = site-specific fantasy points (DraftKings or FanDuel) from the objective composite
- `Own` = expected field ownership percentage for that site/slate (or pass-through on projection-only)
- Preserve the source Sim Savant player names and DFS IDs so imports map cleanly.

## Source hierarchy

### Projection inputs

Build a pure numeric composite per `core/MARKET_PROJECTIONS.md`. Industry numeric sources and sportsbook props are **co-primary**; neither is ignored when available. Practical order of collection:

1. **Sportsbook player props and prices** (Vegas layer) — **prefer board-level / aggregator-first**
   - Hit multi-player boards (PropCruncher, Covers, Action Network, PropPrizm, etc.) for mass data before player-by-player lookups.
   - Pitchers: strikeouts, outs recorded, earned runs allowed, hits allowed, walks allowed, win probability, and any quality-start-relevant markets.
   - Hitters: hits, total bases, home runs, RBI, runs, walks/HBP where available, stolen bases, and H+R+RBI / similar combo markets.
   - Use the odds/juice on both sides when available, not only the posted line.
   - Prefer consensus across multiple books rather than one sportsbook.

2. **Game-level Vegas markets**
   - Moneyline, run line, game total, implied team totals — reconciliation constraints.

3. **Independent numeric DFS projection systems** (Industry layer — target 10+)
   - THE BAT / THE BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros, LineStar, Stokastic/Awesemo, RotoWire, NumberFire, Sabersim, and others with actual projected points or component stats.
   - Rankings and narrative write-ups do not count.

4. **Context needed to allocate team expectation** (facts only)
   - Confirmed batting order / starter status, lineup slot, handedness, park, weather/roof, expected PA / workload.

5. **Sim Savant projection fallback**
   - Use only when public betting markets and independent numeric projection coverage are both insufficient after the exhaustive sweep **of the positive-Proj pool**.
   - Never invent precision for poorly covered players.
   - Savant zeros stay zero without research.

### Ownership inputs

Ownership should be a consensus estimate, not a single-source number. (Projection-only passes leave Own unchanged.)

## Market-to-fantasy conversion

### DraftKings MLB scoring

#### Hitters
- Single: 3 | Double: 5 | Triple: 8 | Home run: 10 | RBI: 2 | Run: 2 | Walk/HBP: 2 | Stolen base: 5

#### Pitchers
- Inning pitched: 2.25 | Strikeout: 2 | Win: 4 | Earned run allowed: -2 | Hit allowed: -0.6 | Walk/HBP allowed: -0.6 | Complete game: 2.5 | CG shutout: +2.5 | No-hitter: 5

### FanDuel MLB scoring

#### Hitters
- Single: 3 | Double: 6 | Triple: 9 | Home run: 12 | RBI: 3.5 | Run: 3.2 | Walk/HBP: 3 | Stolen base: 6

#### Pitchers
- Inning pitched: 3 | Strikeout: 3 | Win: 6 | Quality start: 4 | Earned run allowed: -3

## Confidence tiers

- **Tier A — Vegas-rich / deep composite:** multiple props across books + strong industry support
- **Tier B — Vegas-supported or strong industry blend:** partial props or deep industry with game reconciliation
- **Tier C — Thin external:** limited sources; higher prior weight
- **Tier D — Fallback:** Savant retained conservatively

## Import audit — mandatory before delivery

1. Exact 4-column structure: `Name, DFS ID, Proj, Own`.
2. Correct site scoring system used.
3. No duplicate DFS IDs.
4. `Proj` numeric and non-negative; `Own` numeric 0–100 when present.
5. Coverage / provenance / industry source count reported for the **positive-Proj pool**.
6. Grade gate: overall A or A+ unless user accepts lower.
7. No narrative adjustments in Proj.

## Core philosophy

**Industry numeric projections + sportsbook odds are scraped and blended into one objective consensus `Proj`. Ownership estimates what the field will play. Sim Savant builds the lineups.**

We are not trying to beat the market. We are minimizing single-source risk and delivering the best available consensus projection. No narrative enters `Proj`.

Do not optimize projections toward the lineup result we want. Do not reverse-engineer projections to create leverage. Keep the market-input layer objective and independent from lineup construction.

Authoritative projection rules: `core/MARKET_PROJECTIONS.md`.
