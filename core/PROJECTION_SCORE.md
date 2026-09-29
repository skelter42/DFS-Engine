# Projection Score

The production estimator is model v3 in `core/PROJECTION_MODEL.md`. Vegas consensus is the projection. Industry is the fill. Savant is the last resort.

The 0.50 / 0.50 split is retired. Do not score a slate by lineup finish.

## Required mix, every output

On the positive-Proj pool only. Zeros are not in the denominator.

- Vegas: a two-sided prop converted to site points.
- Industry: no prop after the board sweep, DFS-site median used.
- Savant: no prop and no site number, original left unchanged.

Report counts and percentages. Example: 40 Vegas (51%), 28 industry (36%), 10 Savant (13%), 223 zeros left at 0.

## Log

Every researched player is one row in `history/YYYY-MM-DD-<SLATE>-projection-log.md`.

| Name | DFS ID | Source | Books | Proj | Actual | AbsError |
|---|---|---|---|---:|---:|---:|

`Source` is VEGAS, INDUSTRY, or SAVANT. `Actual` is filled after the slate. Do not write it back into `Proj`.
