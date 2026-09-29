# Savant Prep

## Trigger

Read `core/MARKET_INPUTS_RUN.md` and `core/VEGAS_CONSENSUS.md` first. Those two files are the job. This file is the import contract.

When the user says **"Savant prep"** or **"market inputs"** and attaches a projection CSV, run that workflow only. Do not build lineups.

## Purpose

Return the same CSV with `Proj` replaced by the multi-book sportsbook consensus, converted to site points. Leave `Own` unchanged unless the user asks for an ownership pass.

## Projection order

1. Prop boards across DraftKings, FanDuel, BetMGM, and every other book that posts the market. De-vig each book. Median the books. Convert the consensus probability into site points. That is `Proj`.
2. No two-sided prop for that player: DFS-site median.
3. No site number either: leave Savant unchanged.

Do not average a DFS site into a priced player. Do not average Savant into either. Savant is the last priority.

## Trust Savant zeros

If source `Proj` is 0 or blank:

- Leave `Proj = 0`.
- Do not research that row.
- Keep the row so the import still maps.

## Output

`Name, DFS ID, Proj, Own`

Same names, same DFS IDs, same row order. Replace `Proj` only.

Do not build lineups, change salaries, invent a prop from a team total, or write a narrative into the number.

## Required behavior

Market Inputs / Savant prep means `core/VEGAS_CONSENSUS.md` and nothing else unless the user expands the request.
