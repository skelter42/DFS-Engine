# MLB Market Inputs Process

## Purpose

This file defines one narrow responsibility for the DFS Engine: **produce slate-ready player projections from betting-market and industry information for import into Sim Savant.**

Sim Savant remains responsible for simulation, lineup generation, 1% finish-rate ranking, exposure spreading, stack settings, and contest setup. This process does **not** build or optimize lineups.

**Projection standard (authoritative):** `core/MARKET_PROJECTIONS.md` — pure numeric conglomerate (industry scrape + Vegas scrape → composite). Goal is objective consensus, not beating the market. For these passes, `sports/mlb_market_inputs_projection_override.md` takes precedence on Proj rules. Operating addendum: `sports/mlb_market_inputs_future_iteration.md`.

### Validated defaults (do not regress)

- **2026-09-22:** Public scrape only. Do not stall for paid vendor CSVs.
- **2026-09-23:** Industry and Vegas are **joint layers on the same player**. Headline coverage is the **active pool** (SP + posted/projected 1–9), not the raw positive-Proj file. Reliever fallback is allowed; starter fallback is not.

Default joint weights when both layers exist: SP `0.40 industry / 0.40 Vegas / 0.20 Savant`. Posted hitter `0.40 industry / 0.32 Vegas-env / 0.28 Savant`. Vegas-env for hitters without props is implied team total × lineup-slot share.

## Easy trigger keywords

Use these short commands in chat:

- **`Savant Prep`** or **`Market Inputs — MLB`** = run this process on the attached Sim Savant projection CSV. **Default is projections only** (`Proj` updated, `Own` passed through). Sim Savant does not consume Engine ownership edits. Ownership research only if explicitly requested.
- **`Savant Check`** = audit a completed Sim Savant lineup/export file for final exposure, salary, correlation, Vegas-story, ownership, and game-theory issues. Do not rebuild lineups unless explicitly asked.

## Strict operating contract

### `Savant Prep` means exactly

When the user attaches a Sim Savant projection file and says **`Savant Prep`** or **`Market Inputs — MLB`**:

1. Read the attached Sim Savant projection CSV.
2. Identify the site (DraftKings or FanDuel), slate, player pool, player names, and DFS IDs.
2a. **Trust Savant zeros (mandatory).** If source `Proj` is `0` (or blank treated as 0), leave `Proj = 0`. Do not research props, industry projections, or ownership for those players. Keep the rows in the output file so import structure is preserved. Industry numeric + Vegas prop work applies only to the **positive-Proj pool**.
2b. **Build the active pool before blending.** Active pool = starting pitchers (full start or bulk-behind-opener) + confirmed/projected batting-order 1–9. This is the coverage denominator.
3. Run an **exhaustive sportsbook sweep and industry numeric-source sweep in parallel** on the active pool, then the rest of the positive-Proj pool. **Preferred method: board-level / aggregator-first.** Hit multi-player prop boards and aggregators that surface many lines at once (PropCruncher, Covers matchup prop sections, Action Network boards, PropPrizm, FanDuel Research, etc.) before falling back to player-by-player searches. Only deep-dive individual players for material gaps after the board sweep.
4. For pitchers in the positive-Proj pool, actively search every practical component market: strikeouts, outs recorded, earned runs allowed, hits allowed, walks allowed, win probability/moneyline, and any quality-start-relevant markets.
5. For hitters in the positive-Proj pool, actively search every practical component market: hits, total bases, home runs, RBI, runs, walks/HBP, stolen bases, H+R+RBI, and similar combo markets. **If those props are missing, the Vegas layer is still implied team total + lineup slot.** That is required, not optional.
6. Use the odds/juice and multiple books where available. A posted line without price context is weaker evidence than a market with both sides/juice.
7. Always pull the industry numeric layer **and** the Vegas prop/environment layer for the active pool, then build the **joint** objective consensus composite and convert into the correct site scoring system. Industry is co-primary, not a fallback. Vegas is co-primary, not a fallback.
8. Reconcile player-level projections to game totals, implied team totals, lineup slot, park/weather/roof status, matchup and expected workload/plate appearances (data only; no narrative).
9. Leave `Own` unchanged by default. Sim Savant does not consume Engine ownership edits. Research ownership only if the user explicitly requests an ownership pass.
10. Use the original Sim Savant `Proj` only as a true fallback after the market/industry sweep is exhausted for that **positive-Proj** player. Zero-Proj players stay at 0 by rule, not as researched fallback. Own-0 relievers with no save/K/outs market may stay Savant. Posted starters may not.
11. Preserve the exact Savant import structure and DFS IDs.
12. Run all import/mapping/duplicate/zero-value audit checks.
13. Run the **AI quality-grade gate** described below. Public-scrape **A-** is an allowed delivery grade when full hitter vendor grids are unavailable. Posted-starter fallback is not an allowed delivery state.
14. Return the clean CSV to the user.
15. **Stop.** Do not continue into lineup generation, lineup simulation, exposures, stacks, contest allocation, or portfolio game theory.

### Non-negotiable market-coverage rule

Do **not** stop after finding a small convenient subset of props. The fact that direct props were found for a few pitchers or star hitters is not evidence that the rest of the **active pool** is market-thin.

Before labeling an **active-pool** player as fallback, the process must exhaust public industry pages **and** public Vegas boards:

- multi-player prop boards and aggregators first (PropCruncher, Covers, Action Network, PropPrizm, etc.)
- direct sportsbooks
- pitcher component markets
- hitter component markets **or** team-total + slot allocation
- combo markets
- game-level markets
- independent numeric DFS projection systems (report the count that actually printed, not a hoped-for 10)

If the slate has broad public prop and industry coverage, the final output should reflect broad composite-supported projection coverage.

### Projection provenance requirement

Track an internal source/provenance label for every player projection, even though the final Savant import remains only `Name, DFS ID, Proj, Own`.

Use these labels:

- **JOINT** — industry numeric + Vegas (props and/or team-total/slot) + Savant prior all moved the number.
- **VEGAS_DIRECT** — projection materially built from one or more direct player props with pricing/juice; industry still present.
- **VEGAS_SUPPORTED** — game/team/slot environment + Savant; no public industry print for that name.
- **INDUSTRY_BLEND** — deep industry numeric consensus with thin or no direct props; game markets still used for reconciliation.
- **SAVANT_FALLBACK** — insufficient market and independent industry coverage; original Savant projection retained conservatively. Zero-Proj rows that were never researched stay `0` and are not counted in the active-pool fallback percentage. Own-0 relievers belong here. Posted starters do not.

### Mandatory coverage summary before delivery

Every Savant Prep run must report provenance **twice**:

**Active pool first (SP + posted/projected 1–9):**

- number and percentage `JOINT`
- number and percentage `VEGAS_DIRECT`
- number and percentage `VEGAS_SUPPORTED`
- number and percentage `INDUSTRY_BLEND`
- number and percentage `SAVANT_FALLBACK` — target 0%
- industry source names actually used

**Full positive-Proj pool second (honesty row only).** Do not lead with this number. An 80% fallback share driven by relievers is not a process failure and must not be reported as one.

### AI quality-grade gate — mandatory

Before any market-input CSV is called final, the AI must grade the pass on **projection quality** using current evidence.

Use letter grades: `A+`, `A`, `A-`, `B+`, `B`, `B-`, `C`, or `Incomplete`.

A public-scrape pass may deliver at **A-** when hitter vendor grids are partial. Anything that leaves posted starters on Savant is incomplete.

#### Projection grade criteria

- breadth of **numeric** industry sources actually used
- breadth and freshness of sportsbook/player-prop coverage
- use of juice and multi-book consensus where available
- pitcher/hitter component completeness **or** team-total/slot allocation when props are missing
- reconciliation to game totals and implied team totals
- correct site scoring conversion
- provenance honesty and fallback burden on the **active pool**
- **no narrative in Proj**

#### Required grade report

- `Projection grade: <grade>`
- industry source count and names
- Vegas coverage summary
- provenance mix on the active pool, then the full positive pool
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
- change `Own` unless the user explicitly requested an ownership pass

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
- `Own` = passed through from the source file by default
- Preserve the source Sim Savant player names and DFS IDs so imports map cleanly.

## Source hierarchy

### Projection inputs

Build a pure numeric composite per `core/MARKET_PROJECTIONS.md`. Industry numeric sources and sportsbook props are **co-primary**. Always collect both for every active-pool player. Industry is **not** a fallback used only when Vegas is missing. Vegas is **not** a fallback used only when industry is missing.

Always collect, then blend:

1. **Independent numeric DFS projection systems** (Industry layer)
   - THE BAT / THE BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros, FantasyTeamAdvisors, LineStar, Stokastic/Awesemo, RotoWire, NumberFire, Sabersim, and others with actual projected points or component stats.
   - Rankings and narrative write-ups do not count.
   - Pull this layer for every active-pool player, not only when props are thin.

2. **Sportsbook player props and prices** (Vegas layer) — **prefer board-level / aggregator-first**
   - Hit multi-player boards (PropCruncher, Covers, Action Network, PropPrizm, etc.) for mass data before player-by-player lookups.
   - Pitchers: strikeouts, outs recorded, earned runs allowed, hits allowed, walks allowed, win probability, and any quality-start-relevant markets.
   - Hitters: hits, total bases, home runs, RBI, runs, walks/HBP where available, stolen bases, and H+R+RBI / similar combo markets.
   - Missing hitter props → implied team total + lineup slot is still the Vegas layer.
   - Use the odds/juice on both sides when available, not only the posted line.
   - Prefer consensus across multiple books rather than one sportsbook.

3. **Game-level Vegas markets**
   - Moneyline, run line, game total, implied team totals — reconciliation constraints on both layers.

4. **Context needed to allocate team expectation** (facts only)
   - Confirmed batting order / starter status, lineup slot, handedness, park, weather/roof, expected PA / workload.
   - Opener vs bulk vs full start.

5. **Sim Savant projection fallback**
   - Use only when public betting markets **and** independent numeric projection coverage are both insufficient after the exhaustive sweep.
   - Allowed for Own-0 relievers with no market.
   - Not allowed as the default for posted 1–9 or announced starters.
   - Never invent precision for poorly covered players.
   - Savant zeros stay zero without research.

Form `Proj` from industry consensus + Vegas expectation + Savant prior. Weight by coverage quality. Do not skip the industry pull because props were found, and do not skip the Vegas pull because industry numbers were found.

### Ownership inputs

Ownership is off by default and passed through unchanged. If the user explicitly requests an ownership pass, ownership should be a consensus estimate, not a single-source number.

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

- **Tier A — Joint / Vegas-rich:** multiple props or a full industry print + game environment
- **Tier B — Vegas-supported or strong industry blend:** slot/total environment or deep industry with game reconciliation
- **Tier C — Thin external:** limited sources; higher prior weight
- **Tier D — Fallback:** Savant retained conservatively (relievers / uncovered only)

## Import audit — mandatory before delivery

1. Exact 4-column structure: `Name, DFS ID, Proj, Own`.
2. Correct site scoring system used.
3. No duplicate DFS IDs.
4. `Proj` numeric and non-negative; `Own` numeric 0–100 when present.
5. Coverage / provenance / industry source count reported for the **active pool** first.
6. Grade gate: A / A+ when coverage supports it; public-scrape A- allowed; posted-starter fallback is not.
7. No narrative adjustments in Proj.
8. `Own` unchanged unless an ownership pass was requested.

## Core philosophy

**Industry numeric projections + sportsbook odds are scraped and blended into one objective consensus `Proj`. Sim Savant builds the lineups and handles ownership internally.**

Industry is talent. Vegas is environment. They work on the same name.

We are not trying to beat the market. We are minimizing single-source risk and delivering the best available consensus projection. No narrative enters `Proj`.

Do not optimize projections toward the lineup result we want. Do not reverse-engineer projections to create leverage. Keep the market-input layer objective and independent from lineup construction.

Authoritative projection rules: `core/MARKET_PROJECTIONS.md`.
Override: `sports/mlb_market_inputs_projection_override.md`.
Addendum: `sports/mlb_market_inputs_future_iteration.md`.
