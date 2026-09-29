# Market Inputs — Run Card

This is the executable card. The model is `core/PROJECTION_MODEL.md`. Score and log live in `core/PROJECTION_SCORE.md`. Retrieval lives in `core/VEGAS_BOARD_SWEEP.md`. Default Savant contract lives in `core/SAVANT_PREP.md`.

## Goal

Execute projection model v1. Do not redesign it on the slate.

Industry means other DFS projection sites. Scrape those numeric projections, take the consensus, then see where Vegas has the player.

```
Proj  = DFS-site consensus median, pulled to the Vegas band if it sits outside
Own   = unchanged unless the user explicitly asks for an ownership pass
CPT   = 1.5 × FLEX on Showdown (after the FLEX number is frozen)
Zeros = stay 0
```

Model: `core/PROJECTION_MODEL.md`. Score: `core/PROJECTION_SCORE.md`. Savant does not vote when any usable DFS-site vote exists.

No narrative. No leverage manufacturing. Savant is the import vessel and the final fallback, not a vote.

## Default invocation

Attached Savant CSV + “market inputs” / “Savant prep” / “GitHub NFL market inputs”  
→ **projection-only** unless the user names an ownership pass.

Do not build lineups. Do not rerun locked boards. Do not research finished games.

## Execution order (do not invert)

1. Intake the attached file once. Preserve Name, DFS ID, row order, Own columns.
2. Split the pool: **positive Proj = research universe**. Savant `0` stays `0`.
3. Lock roles before numbers. A confirmed inactive stays `0`. A source older than the official inactive or posted-order timestamp does not vote.
4. Cache game markets once per game (spread / total / ML / implied team totals).
5. Hit boards, not names. Vegas is where the sportsbook has the player, not a DFS projection site. NFL/NCAAF detail: `core/VEGAS_BOARD_SWEEP.md`.
6. Scrape other DFS projection sites in parallel (target 10+ numeric site projections on a mature main slate). Rankings, articles, and betting write-ups do not count.
7. Reject stale site pages.
8. Convert every DFS-site number and every Vegas component to site scoring once. Do not average FanDuel points with DraftKings points.
9. Apply `core/PROJECTION_MODEL.md`. Consensus median, Vegas band, no invented band. Showdown CPT = 1.5 × the frozen FLEX number.
10. Write the boards file and the projection log. Return the import CSV + coverage audit, including how many names the band moved. Stop.

## Grade honestly

- **A+**: 10+ usable DFS-site projections, at least three Tier A, and multi-book Vegas boards, reconciled.
- **A**: several independent DFS sites + complete game boards for the positive-Proj starters. Typical Showdown.
- **B or labeled fallback**: boards missing, or the consensus is a handful of stale pages.

A thin-prop slate is industry-only, not a full market read.

## What this card does not do

- Does not change Own.
- Does not invent a line.
- Does not treat an article as a DFS projection site.
- Does not give Vegas a peer vote.
- Does not bump the model version off one slate.
- Does not persist the import CSV. Persist the boards and the projection log.
