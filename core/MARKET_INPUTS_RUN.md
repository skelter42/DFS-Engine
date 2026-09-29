# Market Inputs — Run Card

Read this, then `core/VEGAS_CONSENSUS.md` and `core/PROJECTION_MODEL.md`. Do not read a retired card for the estimator.

## Order

1. Intake the attached file. Keep Name, DFS ID, row order, Own.
2. Savant 0 stays 0. Do not research those rows.
3. For each game, hit the prop boards. DraftKings, FanDuel, BetMGM, and the other books.
4. Convert. Plus price is `100 / (odds + 100)`. Minus price is `odds / (odds + 100)`. De-vig both sides. A one-sided price still converts, with a small vig haircut.
5. A 0.5 price becomes `-ln(1 - p)`. A counting line becomes the line plus the over probability minus 0.5. Multiply by site points and add the priced pieces. That is Proj.
6. No price after the sweep: DFS-site median.
7. No site number either: leave Savant unchanged.
8. Write the file. Stop. Do not build lineups.

A goal price alone is the goal piece. Add the shot line before that name is finished. Do not write a goal-only number over the whole player.

## Required mix

Every output, relevant group first, then the rest of the positive file:

- n Vegas (x%)
- n industry, no prop (x%)
- n Savant fallback (x%)
- n zeros left at 0, not in the percentage

## Grade

- A+: DraftKings, FanDuel, and BetMGM prices on the relevant group, converted, not blended.
- A: multi-book props on that group. Industry only where every book skipped a name.
- B: the relevant group is still mostly industry.
