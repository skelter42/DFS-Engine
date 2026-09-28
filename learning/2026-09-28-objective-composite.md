# 2026-09-28 — One composite projection; Own is opt-in

- Sport: all Market Inputs / Savant Prep, enforced on NFL Showdown after ATL-GB and LAR-DEN
- Status: validated (user-stated goal + repeated process correction)
- Evidence: User restated the objective: read Vegas odds and industry numeric projections and return **one composite Proj**. LAR-DEN (2026-09-27) and ATL-GB (2026-09-24) already ran that way. Two recurring failure modes showed up in execution, not in philosophy: (1) `MARKET_INPUTS.md` still said `Own = industry-derived first` while `SAVANT_PREP.md` and the user’s standing instruction say Own is pass-through unless requested; (2) industry pages can stay stale after inactives post (FanDuel Research still listed Puka Nacua as a top Rams projection after he was official inactive). Process governance also still said “Vegas-first / market-first” in one place while the canonical composite is **industry + Vegas co-primary**.
- Durable lesson:
  - There is a single projection object: the composite.
  - Own is a separate object and defaults to unchanged.
  - Industry numbers that still allocate to a confirmed inactive, the wrong slate, or an unconverted scoring system are rejected or down-weighted, not averaged in.
  - A+ requires 10+ *usable* numeric sources. Component-only cites (pass yards, rec yards) feed conversion; they do not pad the source count.
  - One-slate actuals (LAR-DEN finished 30-26, Stafford 390 pass, Mumpfield/Higbee/Adkins outproduced thin crumbs) are calibration archive, not a reason to change blend weights.
- Engine impact: Add `core/MARKET_INPUTS_RUN.md` as the executable card. Align Own default, stale-source rejection, and co-primary wording across core files. NFL board-to-DK conversion recipe lives in `sports/nfl.md`.
- Slate artifacts: `history/2026-09-27-LAR-DEN-vegas-boards.md`, `history/2026-09-24-ATL-GB-vegas-boards.md`.
- Files updated: `core/MARKET_INPUTS_RUN.md`, `core/MARKET_PROJECTIONS.md`, `core/PROCESS_GOVERNANCE.md`, `core/SAVANT_PREP.md`, `sports/nfl.md`, `README.md`, `learning/REGISTRY.md`, this file.
- Revisit condition: after a sample of locked composites vs actual DK points, recalibrate blend weights only if the composite is systematically worse than both layers alone.
