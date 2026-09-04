# MLB Market Inputs Process

## Purpose

This file defines one narrow responsibility for the DFS Engine: **produce slate-ready player projections and ownership estimates from betting-market and industry information for import into Sim Savant.**

Sim Savant remains responsible for simulation, lineup generation, 1% finish-rate ranking, exposure spreading, stack settings, and contest setup. This process does **not** build or optimize lineups.

## Easy trigger keywords

Use these short commands in chat:

- **`Savant Prep`** = run this market-input process only on the attached Sim Savant projection CSV.
- **`Savant Check`** = audit a completed Sim Savant lineup/export file for final exposure, salary, correlation, Vegas-story, ownership, and game-theory issues. Do not rebuild lineups unless explicitly asked.

## Strict operating contract

### `Savant Prep` means exactly

When the user attaches a Sim Savant projection file and says **`Savant Prep`**:

1. Read the attached Sim Savant projection CSV.
2. Identify the site (DraftKings or FanDuel), slate, player pool, player names, and DFS IDs.
3. Run an **exhaustive sportsbook sweep before accepting fallback**. Search across as many current books/aggregators as legitimately accessible, including direct sportsbook pages and reputable multi-book prop aggregators.
4. For pitchers, actively search every practical component market: strikeouts, outs recorded, earned runs allowed, hits allowed, walks allowed, win probability/moneyline, and any quality-start-relevant markets.
5. For hitters, actively search every practical component market: hits, total bases, home runs, RBI, runs, walks/HBP, stolen bases, H+R+RBI, and similar combo markets.
6. Use the odds/juice and multiple books where available. A posted line without price context is weaker evidence than a market with both sides/juice.
7. Build the most objective market-derived fantasy projection possible for each player and convert it into the correct site scoring system.
8. Reconcile player-level projections to game totals, implied team totals, lineup slot, park/weather/roof status, matchup and expected workload/plate appearances.
9. Build the best current site-specific ownership estimate from multiple reputable DFS-industry ownership sources/signals.
10. Use the original Sim Savant `Proj` and/or `Own` only as a true fallback after the market/industry sweep is exhausted for that player.
11. Preserve the exact Savant import structure and DFS IDs.
12. Run all import/mapping/duplicate/zero-value audit checks.
13. Return the clean CSV to the user.
14. **Stop.** Do not continue into lineup generation, lineup simulation, exposures, stacks, contest allocation, or portfolio game theory.

### Non-negotiable market-coverage rule

Do **not** stop after finding a small convenient subset of props. The fact that direct props were found for a few pitchers or star hitters is not evidence that the rest of the slate is market-thin.

Before labeling a player as fallback, the process must make a real effort to exhaust the available market surface:

- direct sportsbooks
- multi-book prop aggregators
- pitcher component markets
- hitter component markets
- combo markets
- game-level markets
- independent DFS projections as secondary support

If the slate has broad public prop coverage, the final output should reflect broad market-supported projection coverage. A result where only a handful of players are called Vegas-derived on a normal full MLB slate is an **audit warning**, not an acceptable stopping point.

### Projection provenance requirement

Track an internal source/provenance label for every player projection, even though the final Savant import remains only `Name, DFS ID, Proj, Own`.

Use these labels:

- **VEGAS_DIRECT** — projection materially built from one or more direct player props with pricing/juice.
- **VEGAS_SUPPORTED** — limited direct props plus game/team market and contextual allocation.
- **INDUSTRY_BLEND** — insufficient direct market data; multiple independent DFS projection systems materially drive the estimate.
- **SAVANT_FALLBACK** — insufficient market and independent industry coverage; original Savant projection retained conservatively.

A projection must not be described as Vegas-derived unless its provenance supports that claim.

### Mandatory coverage summary before delivery

Every Savant Prep run must report the projection-source counts for the active positive-projection player pool:

- number and percentage `VEGAS_DIRECT`
- number and percentage `VEGAS_SUPPORTED`
- number and percentage `INDUSTRY_BLEND`
- number and percentage `SAVANT_FALLBACK`

Also report ownership-source coverage where practical: industry consensus vs Savant fallback.

If direct/market-supported coverage is unexpectedly low relative to the available prop market, continue researching rather than merely stating that coverage is below goal.

### `Savant Prep` explicitly does NOT

- build lineups
- optimize lineups
- simulate lineups
- rank lineups by 1% finish rate
- set or recommend exposures
- choose stacks
- allocate contests
- alter projections to manufacture leverage
- apply portfolio game theory
- duplicate any task Sim Savant already handles in its interface

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

- `Proj` = site-specific fantasy points (DraftKings or FanDuel)
- `Own` = expected field ownership percentage for that site/slate
- Preserve the source Sim Savant player names and DFS IDs so imports map cleanly.

## Source hierarchy

### Projection inputs

Use as many current touch points as are legitimately available, with this priority:

1. **Sportsbook player props and prices**
   - Pitchers: strikeouts, outs recorded, earned runs allowed, hits allowed, walks allowed, win probability, and any quality-start-relevant markets.
   - Hitters: hits, total bases, home runs, RBI, runs, walks/HBP where available, stolen bases, and H+R+RBI / similar combo markets.
   - Use the odds/juice on both sides when available, not only the posted line.
   - Prefer consensus across multiple books rather than one sportsbook.

2. **Game-level Vegas markets**
   - Moneyline
   - Run line
   - Game total
   - Derived implied team totals
   - These act as reconciliation constraints for player-level expectations.

3. **Context needed to allocate team expectation**
   - Confirmed batting order / starter status
   - Lineup slot
   - Handedness matchup
   - Park
   - Weather / roof status
   - Expected plate appearances / pitcher workload

4. **Independent DFS projection systems**
   - Use multiple reputable industry projection systems as sanity checks where accessible.
   - These should not automatically override the betting market, but large disagreements must be investigated.

5. **Sim Savant projection fallback**
   - Use only when public betting markets and independent projection coverage are insufficient after the exhaustive sweep.
   - Never invent precision for poorly covered players.

### Ownership inputs

Ownership should be a consensus estimate, not a single-source number.

Collect as many current site-specific ownership projections as legitimately available, including Sim Savant and other reputable DFS industry sources. Then reconcile with the factors that drive ownership:

- Salary / points per dollar
- Position scarcity
- Batting order
- Implied team total
- Stack popularity
- Pitcher opportunity cost
- Obvious value created by lineup news
- Industry tout consensus / public DFS analysis
- Recent ownership updates close to lock

If the numeric ownership consensus conflicts strongly with the public DFS story, flag it and investigate before output.

## Market-to-fantasy conversion

### DraftKings MLB scoring

#### Hitters
- Single: 3
- Double: 5
- Triple: 8
- Home run: 10
- RBI: 2
- Run: 2
- Walk/HBP: 2
- Stolen base: 5

#### Pitchers
- Inning pitched: 2.25
- Strikeout: 2
- Win: 4
- Earned run allowed: -2
- Hit allowed: -0.6
- Walk/HBP allowed: -0.6
- Complete game: 2.5
- Complete-game shutout: 2.5 additional
- No-hitter: 5

Translate expected baseball outcomes into expected DraftKings points. Rare bonuses should be probability-weighted, not assumed.

### FanDuel MLB scoring

#### Hitters
- Single: 3
- Double: 6
- Triple: 9
- Home run: 12
- RBI: 3.5
- Run: 3.2
- Walk/HBP: 3
- Stolen base: 6

#### Pitchers
- Inning pitched: 3
- Strikeout: 3
- Win: 6
- Quality start: 4
- Earned run allowed: -3

For pitchers, an outs prop is especially useful because each recorded out is worth 1 FanDuel point through innings pitched.

## Estimation rules

### Pitchers

Build the expectation from the market components rather than applying a flat percentage adjustment to Savant.

Conceptually:

- Expected innings / outs from outs market
- Expected strikeouts from strikeout market and price
- Expected ER from ER market, opponent implied total, and workload
- Win probability from moneyline adjusted for starter qualification / bullpen context
- FanDuel QS probability from workload + ER expectation + opponent context
- DK hits/walks allowed from direct props when available; otherwise conservative inferred expectation

Then apply site scoring.

### Hitters

Use market expectations for the component stats when available:

- Expected singles/doubles/triples/HR from hits, total bases, HR props and supporting rates
- Expected RBI and runs from direct props, lineup slot, implied team total, and surrounding hitters
- Expected walks/HBP from direct or supporting markets where available
- Expected SB from stolen-base markets / matchup context

Reconcile the sum of hitter expectations against the team implied run environment. Do not allow individual projections collectively to tell a materially different offensive story from the game market without a documented reason.

## Confidence tiers

Assign an internal confidence tier to every player projection.

### Tier A — Market-rich
Multiple independent prop markets across multiple books plus stable game markets.

### Tier B — Market-supported
Some direct props plus strong team/game context and independent projection support.

### Tier C — Sparse market
Limited direct props; use team market + context + projection consensus.

### Tier D — Fallback
Insufficient market coverage; use Sim Savant / projection consensus conservatively.

The final CSV does not need to include the confidence tier unless requested, but the process must use it to avoid fake precision.

## Ownership consensus rules

- Prefer current site-specific ownership sources.
- Weight fresher updates more heavily as lock approaches.
- Avoid treating one provider as authoritative.
- Use median/trimmed consensus where multiple projections exist to reduce outlier influence.
- Check ownership against salary, projection, stack popularity and industry discussion.
- If a player is universally touted but modeled as nearly unowned, treat that as an audit failure until explained.

## Import audit — mandatory before delivery

Every output file must pass all checks below:

1. Exact 4-column structure: `Name, DFS ID, Proj, Own`.
2. Correct site scoring system used.
3. No duplicate DFS IDs.
4. No duplicate exact player-name mapping conflicts.
5. Remove dead duplicate identities when one live positive-projection identity exists.
6. Known Sim Savant ambiguous-name rows that cannot import cleanly should be omitted **only when their projection/ownership are unchanged from the original Savant file**, allowing Savant to retain its existing values.
7. `Proj` must be numeric and non-negative.
8. `Own` must be numeric when present and between 0 and 100.
9. Zero-projection players must be intentional; do not accidentally import inactive/non-slate duplicates.
10. Produce a short audit summary: rows in/out, duplicate conflicts removed, number of projection changes, number of ownership changes, source/provenance counts, and any fallback-heavy players of note.
11. If market-supported coverage is implausibly low for a normal MLB slate, treat the run as incomplete and continue the market sweep before delivery.

## Core philosophy

**Vegas/props create the expectation. Industry consensus estimates what the field will do. Sim Savant builds the lineups.**

Do not optimize projections toward the lineup result we want. Do not reverse-engineer projections to create leverage. Keep the market-input layer objective and independent from lineup construction.

This separation is intentional: projection quality and ownership quality should be judged on their own, while Savant's simulation and portfolio logic are judged separately.
