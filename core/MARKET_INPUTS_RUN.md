# Market Inputs — Run Card

This is the executable card. The model is `core/PROJECTION_MODEL.md` v2. Score and log live in `core/PROJECTION_SCORE.md`. Retrieval lives in `core/VEGAS_BOARD_SWEEP.md`. Default Savant contract lives in `core/SAVANT_PREP.md`.

## Goal

Execute projection model v2. Do not redesign it on the slate.

Industry means other DFS projection sites. Blend those into a median, then blend that median with the Vegas prop.

```
Proj  = 0.50 × DFS-site median + 0.50 × Vegas prop
Own   = unchanged unless the user explicitly asks for an ownership pass
CPT   = 1.5 × FLEX on Showdown (after the FLEX number is frozen)
Zeros = stay 0
```

Model: `core/PROJECTION_MODEL.md`. Savant does not enter the blend.

No narrative. Savant is the import vessel and the final fallback, not a vote.

## Default invocation

Attached Savant CSV + “market inputs” / “Savant prep” / “GitHub NFL market inputs”  
→ **projection-only** unless the user names an ownership pass.

Do not build lineups. Do not rerun locked boards. Do not research finished games.

## Execution order (do not invert)

1. Intake the attached file once. Preserve Name, DFS ID, row order, Own columns.
2. Split the pool: **positive Proj = research universe**. Savant `0` stays `0`.
3. Lock roles before numbers. A confirmed inactive stays `0`. A source older than the official inactive or posted-order timestamp does not vote.
4. Cache game markets once per game (spread / total / ML / implied team totals).
5. Hit boards, not names. Vegas is the player prop, de-vigged to one number. NFL/NCAAF detail: `core/VEGAS_BOARD_SWEEP.md`.
6. Scrape other DFS projection sites in parallel (target 10+ numeric site projections on a mature main slate). Rankings, articles, and betting write-ups do not count.
7. Reject stale site pages.
8. Convert every DFS-site number and the Vegas prop to site scoring once. Do not average FanDuel points with DraftKings points.
9. Apply `core/PROJECTION_MODEL.md`. Median of the sites, then 50/50 with the prop when both exist. No prop: site median. No sites: prop. Neither: Savant. Showdown CPT = 1.5 × the frozen FLEX number.
10. Write the boards file and the projection log. Return the import CSV + coverage audit. Stop.

## Grade honestly

- **A+**: 10+ usable DFS-site projections, at least three Tier A, and a multi-book prop on the positive-Proj starters.
- **A**: several independent DFS sites + props for the starters. Typical Showdown.
- **B or labeled fallback**: props missing, or the site pool is a handful of stale pages.

## What this card does not do

- Does not change Own.
- Does not invent a line.
- Does not treat an article as a DFS projection site.
- Does not put Savant in the 50/50.
- Does not bump the split off one slate.
- Does not persist the import CSV. Persist the boards and the projection log.
