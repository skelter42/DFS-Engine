# Projection Model v4

One number. Industry leaders and sportsbook props, pulled in Python, then blended.

```
Python pull of industry sites + book props
Both present   -> Proj = mean(industry median, de-vigged book consensus in site points)
One present    -> Proj = that one
Neither        -> Proj = Savant, unchanged
Savant 0       -> 0
```

Do not use a summarized page fetch as the board. Run `python -m dfs_engine.projections`. A full prop pull is thousands of rows. Record the count.

Industry is numeric DFS projection sites. Articles are not industry. Books are DraftKings, FanDuel, BetMGM, plus any other book the pull returns. Strip the vig inside each book. Median the books.

Own stays unchanged. Savant is the file skeleton, not a third equal vote.

Conversion math is `core/VEGAS_CONSENSUS.md`. The executable card is `core/MARKET_INPUTS_RUN.md`.
