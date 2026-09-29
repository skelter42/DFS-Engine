# MLB Market Inputs — Future Iteration Fixes

Estimator is model v2 in `core/PROJECTION_MODEL.md`. This file does not set a different blend.

- 2026-09-22: public scrape only. Do not stall for paid CSVs.
- 2026-09-23: both layers on the same player. Grade starting pitchers plus posted 1–9.
- 2026-09-29: Proj = 0.50 × DFS-site median + 0.50 × Vegas prop. Fixed 0.40 weights and the Vegas band are retired.

Savant does not vote. No prop: site median. No sites: prop. Neither: Savant fallback, allowed for Own-0 relievers, not for posted starters.

Do not treat a team total as a hitter projection. Do not mix Main-slate pages onto a Turbo file.
