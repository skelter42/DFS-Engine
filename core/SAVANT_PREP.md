# Savant Prep

## Trigger

Read `core/MARKET_INPUTS_RUN.md` and `core/PROJECTION_MODEL.md` first. This file is the import contract.

When the user says **Savant prep** or **market inputs** and attaches a projection CSV, run that workflow only. Do not build lineups.

## Purpose

Return the same CSV with `Proj` replaced by the Python blend of industry leaders and the sportsbook board. Leave `Own` unchanged unless the user asks for an ownership pass.

## Projection order

1. Python pull of numeric DFS sites and of DraftKings, FanDuel, BetMGM, and every other book on the board.
2. Both present: mean of the industry median and the de-vigged book consensus, in site points.
3. One present: that one.
4. Neither: leave Savant unchanged.

Savant is not a third equal vote. A summarized page fetch is not a pull.

## Trust Savant zeros

If source `Proj` is 0 or blank:

- Leave `Proj = 0`.
- Do not research that row.
- Keep the row so the import still maps.

## Output

`Name, DFS ID, Proj, Own`

Same names, same DFS IDs, same row order. Replace `Proj` only.

Do not build lineups, change salaries, invent a prop from a team total, or write a narrative into the number.
