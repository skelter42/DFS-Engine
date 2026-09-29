# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

Estimator: `core/PROJECTION_MODEL.md` v6. Same rule as every other sport.

**User default (2026-09-29): books drive. Python scrape of a real sportsbook. Savant is the fallback. A missing price is not filled.**

## Standard

1. Scrape the prop board in Python. No Odds API. No page summary. Record the raw row count.
2. Scoring prices posted: Proj is the de-vigged book number, in DraftKings points.
3. Scoring prices missing: Proj is Savant, unchanged.
4. Savant 0 stays 0.

Hitters need the posted hit, total-base, run, and RBI prices that the conversion uses. Pitchers need strikeouts, outs, and earned runs. A missing one of those is not filled from a team total.

No narrative in Proj. Own unchanged unless an ownership pass is requested. Industry is a check, not a vote.

## Trust Savant zeros

Source Proj = 0 stays 0 unless the user says `unlock posted starters`.

## Required behavior

Lock roles before the number. Reject the wrong slate. Convert to site scoring. Preserve Name, DFS ID, Own, row order. Report books / savant-fallback / zeros. Stop. No lineups.
