# Market Inputs — Run Card

Same steps every slate. The only inputs are the sport, the date, and the Savant file.

1. Keep Name, DFS ID, row order, Own.
2. Savant 0 stays 0. Do not research those rows.
3. Run `python -m dfs_engine.projections --sport <sport> --date <YYYY-MM-DD> --savant <file> --pull`. Do not substitute a summarized page fetch. Do not load a prior slate's props.
4. Write the raw rows next to the output and record the count. Reject the pull if the lines do not vary by player. That is a flattened fetch, not a board.
5. Industry median and the de-vigged book consensus are co-primary. Both present: mean of the two, in site points. One present: that one. Neither: Savant, unchanged.
6. Report both / vegas-only / industry-only / savant / zeros.
7. Stop. Do not build lineups.

Read `core/PROJECTION_MODEL.md` and `core/VEGAS_CONSENSUS.md`. The pull lives in `src/dfs_engine/projections/`. Files under `reference/` are examples. Do not run them.
