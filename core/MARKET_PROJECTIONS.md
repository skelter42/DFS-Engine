# Market-Derived DFS Projections

Status: v4. Industry leaders and the book board are co-primary. The pull is Python.

```
Both present   -> Proj = mean(industry median, de-vigged book consensus in site points)
One present    -> Proj = that one
Neither        -> Proj = Savant, unchanged
Savant 0       -> 0
```

Do not use the Vegas-only card from earlier on 2026-09-29. Do not equal-weight Savant into a priced player. Do not rescale the book number onto the industry mean and spread.

## Still in force

- Pull with `python -m dfs_engine.projections`. Record the raw row count.
- Savant 0 stays 0. Do not research those rows.
- Own stays unchanged unless the user asks for an ownership pass.
- No narrative in Proj.
- Do not invent a player prop from a team total.
- Preserve Name, DFS ID, row order.
- Stop after the import CSV. Do not build lineups.
