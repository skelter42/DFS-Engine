# Market-Derived DFS Projections

Status: superseded for the estimator. The production model is `core/PROJECTION_MODEL.md` v3. The operating steps are `core/VEGAS_CONSENSUS.md`. The executable card is `core/MARKET_INPUTS_RUN.md`.

Do not use the industry-median-plus-Vegas-band lock in older revisions of this file. Do not use a 50/50 blend. Do not give Savant a weight.

## The number

```
Props exist  -> Proj = multi-book de-vigged consensus, in site points
No props     -> Proj = DFS-site median
Neither      -> Proj = Savant, unchanged
```

The blend is across sportsbooks (DraftKings, FanDuel, BetMGM, and the other books on the board). It is not a blend with a DFS site.

## Still in force

- Savant 0 stays 0. Do not research those rows.
- Own stays unchanged unless the user asks for an ownership pass.
- No narrative in Proj.
- Do not invent a player prop from a team total.
- Preserve Name, DFS ID, row order.
- Stop after the import CSV. Do not build lineups.
