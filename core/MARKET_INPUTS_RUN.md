# Market Inputs — Run Card

Executable NFL/MLB/NHL preview, odds normalization and paired post-slate evaluation: `core/PROJECTION_PIPELINE.md`. That prototype does not establish calibrated weights or guarantee complete coverage; report its fallback rows honestly.

This is the executable card. Methodology lives in `core/MARKET_PROJECTIONS.md`. Retrieval lives in `core/VEGAS_BOARD_SWEEP.md`. Default Savant contract lives in `core/SAVANT_PREP.md`.

## Goal

Produce **one objective composite projection** for each positive-Savant-Proj player.

```
Proj  = numeric blend(industry scrape, Vegas scrape)
Own   = unchanged unless the user explicitly asks for an ownership pass
CPT   = 1.5 × FLEX on Showdown (after the FLEX composite is frozen)
Zeros = stay 0
```

No narrative, no leverage manufacturing, no “I like this matchup.”  
Savant is the import vessel and the final fallback, not the source of truth.

## Default invocation

Attached Savant CSV + “market inputs” / “Savant prep” / “GitHub NFL market inputs”  
→ **projection-only** unless the user names an ownership pass.

Do not build lineups. Do not rerun locked boards. Do not research finished games.

## Execution order (do not invert)

1. Intake the attached file once. Preserve Name, DFS ID, row order, Own columns.
2. Split the pool: **positive Proj = research universe**. Savant `0` stays `0`.
3. Confirm actives/inactives. A confirmed inactive stays `0` even if a prop board still lists them.
4. Cache game markets once per game (spread / total / ML / implied team totals).
5. Hit boards, not names: ATTD/FTD/2+ ladder, then yards/receptions/attempts table. NFL/NCAAF detail: `core/VEGAS_BOARD_SWEEP.md`.
6. Pull independent **numeric** industry sources in parallel (target 10+ on a mature main slate). Rankings and write-ups do not count.
7. Reject stale industry pages (still allocating to a confirmed inactive, wrong slate, wrong site scoring with no conversion).
8. Convert Vegas components to site scoring once. Haircut vigged ATTD. Reconcile TD/yard sums to the game total.
9. Blend by evidence quality into **one FLEX number**. Showdown CPT = 1.5 × that number.
10. Write `history/YYYY-MM-DD-<SLATE>-vegas-boards.md`. Return the import CSV + coverage audit. Stop.

## Grade honestly

- **A+**: broad genuinely independent numeric sources, current multi-book boards, full component and role reconciliation, and an established paired scorecard for this sport/role. Ten sources alone do not prove accuracy.
- **A**: several independent numeric sources + complete game boards for the positive-Proj starters. Typical Showdown.
- **B or labeled fallback**: boards missing, or industry is a handful of stale/mixed-scoring pages. An honest lower-grade public pass may be delivered with gaps visible.

Do not count a component-only cite (pass yards only) as a full DK projection source. It still feeds the Vegas/industry layers; it does not inflate the source count toward 10+.

## Coverage (positive-Proj pool only)

Report Vegas-rich / Vegas-supported / Industry-blend / Savant-fallback.  
Zeros are not fallback.

## What this card does not do

- Does not change Own.
- Does not invent a line that was not posted.
- Does not promote one-slate scoring misses into a new blend weight.
- Does not persist the import CSV to GitHub. Persist the **boards**.
