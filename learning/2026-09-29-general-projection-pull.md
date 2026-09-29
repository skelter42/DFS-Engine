# 2026-09-29 — Projection pull is general

- Sport: all Market Inputs / Savant Prep
- Status: validated (user correction the same day)
- Evidence: The Claude pack and the Sept 3 workbook are one NHL slate and one MLB slate. Baking their games, name fixes, or row count into the engine would make the next slate wrong.
- Durable lesson: The engine takes a sport, a date, and a Savant file. It pulls that date's industry sites and book board in Python and blends them. A prior slate's raw file is not an input.
- Engine impact: `core/MARKET_INPUTS_RUN.md`, `src/dfs_engine/projections/`. `reference/` is an example and is not run.
- Revisit condition: none, unless the inputs stop being sport, date, and the Savant file.
