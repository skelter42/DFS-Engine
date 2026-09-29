# MLB Market Inputs Process

Status: superseded for the estimator. Do not use the 0.40 / 0.40 / 0.20 weights or any Savant prior in this file's older revisions.

Read these instead, in order:

1. `core/MARKET_INPUTS_RUN.md`
2. `core/VEGAS_CONSENSUS.md`
3. `core/PROJECTION_MODEL.md` v3
4. `sports/mlb_market_inputs_projection_override.md`

## What to do

Attached Savant CSV + market inputs / Savant prep:

- Hit prop boards across DraftKings, FanDuel, BetMGM, and the other books.
- Convert odds to probabilities. Strip the vig. Median the books. Convert that consensus into DraftKings or FanDuel points. That is Proj.
- No two-sided prop: DFS-site median.
- No site number either: leave Savant unchanged.
- Savant 0 stays 0.
- Own stays unchanged.
- Stop. Do not build lineups.

DraftKings scoring, when the component is posted: pitcher innings 2.25, strikeout 2, win 4, earned run −2, hit −0.6, walk −0.6. Hitter single 3, double 5, triple 8, home run 10, RBI 2, run 2, walk 2, stolen base 5.
