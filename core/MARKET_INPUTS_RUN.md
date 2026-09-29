# Market Inputs — Run Card

This is the executable card. The model is `core/PROJECTION_MODEL.md` v3. The operating framework is `core/VEGAS_CONSENSUS.md`. Score and log live in `core/PROJECTION_SCORE.md`. Retrieval lives in `core/VEGAS_BOARD_SWEEP.md`. Default Savant contract lives in `core/SAVANT_PREP.md`.

## Goal

Execute projection model v3. Do not redesign it on the slate.

Look across prop boards. DraftKings, FanDuel, BetMGM, and the other books that post the market. Each price is a percentage. Strip the book edge. Consensus those percentages. Convert the consensus into site points. That expected point total is what gets uploaded to Savant.

The blend is across sportsbooks. It is not a blend with a DFS site, and it is not a blend with Savant.

```
Props exist  -> Proj = multi-book de-vigged consensus, in site points
No props     -> Proj = DFS-site median
Neither      -> Proj = Savant, unchanged
Own          = unchanged
Zeros        = stay 0
```

Savant is the last priority.

## Default invocation

Attached Savant CSV + “market inputs” / “Savant prep”
→ projection-only unless the user names an ownership pass.

Do not build lineups. Do not rerun locked boards. Do not research finished games.

## Execution order (do not invert)

1. Intake the attached file once. Preserve Name, DFS ID, row order, Own columns.
2. Split the pool: positive Proj = research universe. Savant 0 stays 0.
3. Lock roles before numbers. A confirmed inactive stays 0.
4. Cache game markets once per game (spread / total / ML).
5. Hit boards, not names. DraftKings, FanDuel, BetMGM at minimum, plus any other book on the board. De-vig inside each book. Median across books. Convert once to site points. Detail: `core/VEGAS_CONSENSUS.md`.
6. Where the board has a two-sided prop, that consensus is Proj. Do not blend a DFS site on top of it.
7. Where no book priced the player, scrape DFS projection sites and take the median.
8. Where both are empty, leave Savant unchanged.
9. Write the boards file and the projection log. Return the import CSV + coverage audit. Stop.

## Grade honestly

- A+: two-sided prices from DraftKings, FanDuel, and BetMGM on the starters and the posted order, converted, not blended with a site.
- A: multi-book props on the starters. Industry only where the board skipped a name.
- B: one book, or one side, or starters with no prop.

## What this card does not do

- Does not change Own.
- Does not invent a line from a team total.
- Does not treat an article as a prop or as a DFS site.
- Does not blend Vegas with industry or with Savant.
- Does not persist the import CSV. Persist the boards and the projection log.
