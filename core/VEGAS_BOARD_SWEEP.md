# Vegas Board Sweep — Mandatory

## Purpose

The Vegas layer of a composite projection is built from **slate-level boards**, not from a queue of one-player searches.

Player-by-player prop lookups are a **gap-fill only**. They are not the default research path. If a Market Inputs / Savant Prep pass searched names one at a time before hitting a multi-player board, the pass is incomplete even if the final numbers look reasonable.

Canonical composite standard: `core/MARKET_PROJECTIONS.md`.
This file owns the retrieval method for the Vegas layer.

## Hard rule

**Board first. Name second.**

Required order on every projection-only or full Market Inputs run:

1. Cache game markets once (spread, total, ML, implied team totals, team totals).
2. Pull the **anytime TD / first TD / 2+ TD ladder** for the whole game in one board.
3. Pull the **yards / receptions / attempts board** for the whole game in one board (pass, rush, rec).
4. Convert those tables into site scoring for the **positive-Proj pool**.
5. Deep-dive an individual player only when that player is DFS-relevant **and** a required component is still missing after the boards.

Do not start with "Jordan Love passing yards" then "Bijan rushing yards" then "Watson receiving yards". Start with the game's TD board and the game's yards board.

## What counts as a board

A valid first-pass source surfaces **many players and many markets on one page**. Examples:

- DraftKings / FanDuel / BetMGM event pages (ATTD ladder + pass/rush/rec markets on the same event)
- Covers matchup player-prop section
- Action Network matchup / prop boards
- PropCruncher, PropPrizm, OddsShopper, FanDuel Research multi-player tables
- Any aggregator that lists consensus lines across books for a full game

A page that is one player plus a write-up is **not** a board. Use it only after the board sweep.

## NFL / NCAAF board package (minimum)

For every game on the slate, capture in one pass:

**Game**
- spread, total, moneyline
- implied team totals / team totals when posted

**Touchdowns (one ladder, every listed scorer)**
- anytime TD
- first TD when posted
- 2+ TDs when posted
- DST anytime TD when posted

**Volume / yards (one table, every listed player)**
- QB: pass yds, pass TDs, INT, completions, attempts, rush yds / rush att
- RB: rush yds, rush att, receptions, rec yds, ATTD
- WR/TE: receptions, rec yds, ATTD
- K: FGs / team total context (game total is enough if no kicker props)

**Do not require every book.** Multi-book consensus on a board beats a perfect single-book scrape of one star.

## Conversion

- De-vig ATTD when both sides or a full ladder exist. If only Yes price is posted, treat it as a vigged probability and do not pretend it is the true TD rate.
- Expected TDs ≈ P(anytime) + P(2+) when the 2+ market exists; otherwise use the anytime price as a capped expectation, not 1.0× the raw implied.
- Yards/receptions: use the consensus line as the mean unless juice is badly skewed.
- Apply site scoring once after the table is complete.
- Reconcile the sum of player TD expectations and yardage to the game total. If the board implies 7 offensive TDs in a 43-point game, the conversion is wrong — fix the de-vig, do not invent a narrative.

## Gap-fill (the only time to search one player)

After the boards are in, a named search is allowed only if:

- the player has positive Savant Proj (zeros stay zero), **and**
- the player is a likely active DFS piece, **and**
- the boards are missing that player's primary component (QB with no pass-yard line, featured RB with no rush line, WR1 with no rec-yard or ATTD price)

Even then, prefer another **board** (different book/aggregator event page) over an article about that player.

## What not to do

- Do not build the Vegas layer from prop-bet articles that mention three players.
- Do not treat an SGP alt (70+ yards, 5+ catches) as the posted mean if a standard line exists.
- Do not skip the ATTD ladder because yards already exist. TDs are a separate DK component.
- Do not research Savant-zero rows just because they appear on a TD board.

## Audit requirement

Every projection pass must report:

- which boards were hit (URL / book / timestamp)
- whether the ATTD ladder was captured for the game
- whether a yards/volume table was captured for the game
- which positive-Proj players still lacked a board component after the sweep
- which named searches were used as gap-fill, and why

If the audit cannot list a TD board and a yards board, the Vegas layer is not done.

## Sport notes

- **NFL/NCAAF Showdown:** one game, so one TD board + one yards board should cover the whole positive-Proj pool.
- **NFL/NCAAF classic:** one board pair **per game**, not per player. Loop games, not names.
- **MLB:** board = pitcher prop family table + hitter prop family table per game, not 20 sequential hitter searches. Details remain in `sports/mlb.md` / Market Inputs MLB sweep rules.
- **NBA/NHL:** board = points/rebounds/assists or shots/saves tables for the game, then gap-fill.

## Relationship to other files

- `core/MARKET_PROJECTIONS.md` — what the composite number is
- `core/MARKET_INPUTS.md` — full Market Inputs workflow
- `core/SAVANT_PREP.md` — projection-only Savant import contract
- `sports/<sport>.md` — scoring conversion and sport-specific prop families
- This file — **how Vegas data is collected**
