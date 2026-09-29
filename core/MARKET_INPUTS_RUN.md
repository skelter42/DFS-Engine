# Market Inputs — Run Card

This is the executable card. The model is `core/PROJECTION_MODEL.md` v3. Score and log live in `core/PROJECTION_SCORE.md`. Retrieval lives in `core/VEGAS_BOARD_SWEEP.md`. Default Savant contract lives in `core/SAVANT_PREP.md`.

## Goal

Execute projection model v3. Do not redesign it on the slate.

Vegas drives. A prop board is a set of odds. Convert the odds to probabilities, take the book edge out, consensus the books, and turn that probability into site points. That number is the projection.

```
Props exist  -> Proj = Vegas consensus
No props     -> Proj = DFS-site median
Neither      -> Proj = Savant, unchanged
Own          = unchanged
Zeros        = stay 0
```

No 50/50. Savant does not enter a Vegas number or an industry number.

## Default invocation

Attached Savant CSV + “market inputs” / “Savant prep”
→ projection-only unless the user names an ownership pass.

Do not build lineups. Do not rerun locked boards. Do not research finished games.

## Execution order (do not invert)

1. Intake the attached file once. Preserve Name, DFS ID, row order, Own columns.
2. Split the pool: positive Proj = research universe. Savant 0 stays 0.
3. Lock roles before numbers. A confirmed inactive stays 0.
4. Cache game markets once per game (spread / total / ML).
5. Hit boards, not names. Multi-book. De-vig every two-sided price. Median across books. Convert once to site points.
6. Where the board has a convertible prop, that consensus is Proj. Do not blend a DFS site on top of it.
7. Where the board is empty, scrape DFS projection sites and take the median.
8. Where both are empty, leave Savant unchanged.
9. Write the boards file and the projection log. Return the import CSV + coverage audit. Stop.

## Grade honestly

- A+: multi-book two-sided props on the positive-Proj starters and the posted 1–9, converted, not blended.
- A: multi-book props on the starters, industry fill only on names the board skipped.
- B: props missing on starters, or the board is one book and one side.

## What this card does not do

- Does not change Own.
- Does not invent a line from a team total.
- Does not treat an article as a prop or as a DFS site.
- Does not blend Vegas with industry or with Savant.
- Does not persist the import CSV. Persist the boards and the projection log.
