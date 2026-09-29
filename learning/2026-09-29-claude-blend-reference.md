# 2026-09-29 — Claude blend reference, not a model change

- Sport: NHL worked example; MLB Sept 3 market workbook attached with it
- Status: reference only
- Evidence: Claude's pack produced an NHL upload by equal-weighting Sim Savant, Daily Fantasy Fuel, and a props-implied number, then rescaling the props number to the services' mean and standard deviation. The same drop included a Sept 3 MLB workbook that is market-only when book coverage is dense (`Market Weight = 1`).
- Durable lesson: keep the math (no-vig, Poisson 1+ conversion, DK scoring, audit columns). Do not promote the blend weights. v3 already says a two-sided prop is the projection, a DFS site is only the fallback, and Savant is last and unchanged.
- Engine impact: none on `core/PROJECTION_MODEL.md`. Files live under `reference/claude-2026-09-29/`.
- Revisit condition: only if a logged slate shows the equal-weight blend beating Vegas-alone on absolute error.
