# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

## Standard

The output `Proj` is a **pure numeric composite** that must meet the A+ bar defined in `core/MARKET_PROJECTIONS.md`:

1. **Industry layer** — scrape/pull as many independent **numeric** projection sources as are realistically available (target **10+** on a normal MLB main slate). Rankings and write-ups do not count.
2. **Vegas layer** — scrape/pull multi-book player props + game markets via **board-level / aggregator-first** sweeps; de-vig when possible; use as statistical expectation and as reconciliation against the industry blend.
3. **Sim Savant** — final fallback only when both layers are thin **for a positive-Proj player**.

**No narrative enters Proj.** No matchup story, no "due" adjustment, no leverage manufacturing. Only scraped industry numbers + scraped sportsbook odds, converted and blended.

Ownership (`Own`) is left unchanged unless the user explicitly requests an ownership pass.

## Trust Savant zeros — mandatory

If source `Proj` is `0` (or blank treated as 0), leave `Proj = 0`. Do not research industry projections or Vegas props for that row. Keep the row in the file. Industry + Vegas work, the 10+ source target, coverage grades, and provenance mix apply only to the **positive-Proj pool**.

## Required behavior

1. Split the file: zeros stay zeros; research only the positive-Proj pool.
2. Exhaust industry sources and sportsbook markets for `Proj` on that pool before delivery (keep going until A+ or sources are exhausted).
3. Industry: pursue THE BAT / THE BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros, LineStar, Stokastic/Awesemo, RotoWire, NumberFire, Sabersim, and any other current **numeric** MLB DFS projection systems. Do not stop at one or two sources.
4. Vegas: **board-level first** — PropCruncher, Covers, Action Network, PropPrizm, FanDuel Research, then deep-dive gaps. Multi-book props (K, outs, ER, hits/walks, win for pitchers; hits, TB, HR, RBI, runs, walks, H+R+RBI, SB for hitters) + game totals / ML / team totals. De-vig and consensus across books.
5. Form the composite from both layers numerically; reconcile player totals to the game environment with data only.
6. Preserve Name, DFS ID, Own, and row order. Replace only `Proj` on researched (positive-Proj) rows.
7. Track provenance: `VEGAS_DIRECT`, `VEGAS_SUPPORTED`, `INDUSTRY_BLEND`, `SAVANT_FALLBACK`, plus industry source count. Zero-Proj rows are not counted in the active-pool fallback percentage.
8. Report grade, industry source count, Vegas coverage, and largest composite vs original Savant deltas **for the positive-Proj pool**.

## Grade gate

- `Projection grade: <grade>`
- `Overall projection-input grade: <grade>`
- Target: **A or A+**
- Below A → more industry and/or Vegas research required unless user accepts lower grade.

## Core philosophy

**Scrape industry projections + scrape sportsbook odds → blend into one composite. That is the entire projection process.**

Trust Savant zeros so the research list stays small. Sim Savant receives the composite and handles ownership separately unless asked otherwise. Never alter projections to manufacture leverage. Keep the composite objective and independent from lineup construction.
