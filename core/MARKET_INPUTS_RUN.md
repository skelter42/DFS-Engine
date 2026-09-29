# Market Inputs — Run Card

This is the executable card. Methodology lives in `core/MARKET_PROJECTIONS.md`. Score and log live in `core/PROJECTION_SCORE.md`. Retrieval lives in `core/VEGAS_BOARD_SWEEP.md`. Default Savant contract lives in `core/SAVANT_PREP.md`.

## Goal

Produce **one objective composite projection** for each positive-Savant-Proj player, and log the pieces so the number can be scored.

```
Proj  = industry median, pulled to the Vegas band if it sits outside
Own   = unchanged unless the user explicitly asks for an ownership pass
CPT   = 1.5 × FLEX on Showdown (after the FLEX number is frozen)
Zeros = stay 0
```

Estimator lock: `core/MARKET_PROJECTIONS.md`. Score: `core/PROJECTION_SCORE.md`. Not a weighted mean. Not an equal-vote median. Savant does not vote when any usable industry vote exists.

No narrative, no leverage manufacturing, no “I like this matchup.”  
Savant is the import vessel and the final fallback, not the source of truth.

## Default invocation

Attached Savant CSV + “market inputs” / “Savant prep” / “GitHub NFL market inputs”  
→ **projection-only** unless the user names an ownership pass.

Do not build lineups. Do not rerun locked boards. Do not research finished games.

## Execution order (do not invert)

1. Intake the attached file once. Preserve Name, DFS ID, row order, Own columns.
2. Split the pool: **positive Proj = research universe**. Savant `0` stays `0`.
3. Lock roles before numbers. A confirmed inactive stays `0` even if a prop board still lists them. A source older than the official inactive or posted-order timestamp does not vote. Do not blend a name until that status is set.
4. Cache game markets once per game (spread / total / ML / implied team totals).
5. Hit boards, not names: ATTD/FTD/2+ ladder, then yards/receptions/attempts table. NFL/NCAAF detail: `core/VEGAS_BOARD_SWEEP.md`.
6. Pull independent **numeric** industry sources in parallel (target 10+ on a mature main slate). Rankings and write-ups do not count.
7. Reject stale industry pages (still allocating to a confirmed inactive, wrong slate, wrong site scoring with no conversion, or older than the role news).
8. Convert every industry number and every Vegas component to site scoring once. Haircut vigged ATTD. Do not average FanDuel points with DraftKings points.
9. Collapse source families to one vote. If three or more Tier A votes exist, Tier B does not vote. Industry candidate = median of the votes that remain. Build one Vegas number from the de-vigged board. Band = that number ± the larger of 1.5 site points or 12% of it. Keep the industry median inside the band; pull to the nearest edge if it sits outside. No converted prop: the industry median stands, labeled `INDUSTRY_ONLY`. Showdown CPT = 1.5 × that frozen FLEX number.
10. If the slate totals still break the board, drop the stale vote and recompute. Do not reweight. Write `history/YYYY-MM-DD-<SLATE>-vegas-boards.md` and `history/YYYY-MM-DD-<SLATE>-projection-log.md` with the columns in `core/PROJECTION_SCORE.md`. Return the import CSV + coverage audit, including how many names the band moved. Stop.

## Grade honestly

- **A+**: 10+ usable numeric industry sources, at least three Tier A, and multi-book Vegas boards, reconciled.
- **A**: several independent numeric sources + complete game boards for the positive-Proj starters. Typical Showdown.
- **B or labeled fallback**: boards missing, or industry is a handful of stale/mixed-scoring pages.

Do not count a component-only cite as a full site projection source. A thin-prop slate is industry-only, not a full market read.

## Coverage (positive-Proj pool only)

Report Vegas-rich / Vegas-supported / Industry-only / Savant-fallback, plus the count of names the band moved.  
Zeros are not fallback.

## What this card does not do

- Does not change Own.
- Does not invent a line that was not posted.
- Does not give Vegas a peer vote against the industry median.
- Does not manufacture a band for a no-prop player.
- Does not change band width or Tier A off one slate.
- Does not persist the import CSV to GitHub. Persist the **boards** and the **projection log**.
