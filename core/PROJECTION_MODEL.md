# Projection Model v4

One number, any slate. Industry leaders and sportsbook props, pulled in Python, then blended.

Inputs are the sport, the slate date, and the Savant file. No game list, player list, or row quota lives in the engine.

```
Python pull for that sport and date
Both present   -> Proj = mean(industry median, de-vigged book consensus in site points)
One present    -> Proj = that one
Neither        -> Proj = Savant, unchanged
Savant 0       -> 0
```

Do not use a summarized page fetch as the board. Do not reuse another slate's raw file. Run `python -m dfs_engine.projections --sport <sport> --date <YYYY-MM-DD> --savant <file> --pull`.

Industry is numeric DFS projection sites. Articles are not industry. Books are DraftKings, FanDuel, BetMGM, plus any other book the pull returns. Strip the vig inside each book. Median the books.

Own stays unchanged. Savant is the file skeleton, not a third equal vote.

A worked example from one date is reference only. It is not the next slate.

Conversion math is `core/VEGAS_CONSENSUS.md`. The executable card is `core/MARKET_INPUTS_RUN.md`.
