# Market Inputs — Run Card

Pull industry leaders and the sportsbook board in Python. Blend them. Write the file.

1. Keep Name, DFS ID, row order, Own.
2. Savant 0 stays 0. Do not research those rows.
3. Run `python -m dfs_engine.projections --sport <sport> --pull`. Do not substitute a summarized page fetch. Write the raw rows and record the count. A full board is thousands of rows. Under 100 prop rows is a failed pull.
4. Industry median and the de-vigged book consensus are co-primary. Both present: mean of the two, in site points. One present: that one. Neither: Savant, unchanged.
5. Report both / vegas-only / industry-only / savant / zeros.
6. Stop. Do not build lineups.

Read `core/PROJECTION_MODEL.md` and `core/VEGAS_CONSENSUS.md`. The pull lives in `src/dfs_engine/projections/`.
