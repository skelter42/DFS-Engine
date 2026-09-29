# Vegas Consensus — the projection

This is the operating framework for every sport. Model owner is `core/PROJECTION_MODEL.md` v3. This file is how a run builds the number that gets uploaded to Sim Savant.

Do this every time. Do not skip to a DFS site. Do not skip to Savant. The first action is the prop board.

## Thesis

Look across prop boards. DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Fanatics, and any other book that posts the market. Each price is a percentage chance. Strip the book edge. Consensus those percentages. Convert the consensus into site points. That expected point total is the projection uploaded to Savant.

The blend is across sportsbooks. It is not a blend with a DFS site, and it is not a blend with Savant.

## Priority

1. Multi-book prop consensus, converted to site points. This is the projection.
2. DFS-site median, only for a player no book has priced after the board sweep.
3. Savant, only when there is no prop and no site number. Leave it unchanged.

Savant 0 stays 0. Do not open a board for a zero row.

## Every-time board sweep

Loop games, not names. One board covers the game.

For each game:

1. Open the event page on DraftKings, FanDuel, and BetMGM. Add Caesars, BetRivers, Fanatics, and an aggregator that shows the actual prices (Covers, Action Network, OddsShopper, PropCruncher).
2. Pull the pitcher family for every priced pitcher: strikeouts, outs recorded, earned runs, hits allowed, walks, win.
3. Pull the hitter family for every priced hitter: hits, total bases, home runs, RBI, runs, walks, stolen bases, hits+runs+RBI.
4. Record both sides. A one-sided price is not a consensus.
5. De-vig inside each book. Median the books. Ten books are one number.
6. Convert that consensus into site points. That player is done. Do not average a DFS site on top.
7. A player still empty after every book on that game falls to the industry median. If that is empty too, leave Savant unchanged.

A page about one player is a gap-fill, used only after the game board is in and a positive-Proj starter or posted hitter is still missing a primary component.

## From odds to a percentage

American odds to implied probability:

- Plus price: `100 / (odds + 100)`. +150 is 40%.
- Minus price: `odds / (odds + 100)`. −150 is 60%.

Remove the edge. If the over is 40% raw and the under is 64% raw, the two sides sum to 104%. De-vigged over is `40 / 104`. Do this inside each book, then take the median de-vigged probability across books.

The line is the median line. Do not average a 7.5 with a 6.5 into a 7.0 if most books are on 7.5.

## From a percentage to points

The upload is expected site points, not the probability itself.

- A 0.5 market: de-vigged over probability times the site points that event is worth. A hit is 3 for a single. A home run is 10. An RBI is 2. A run is 2. A walk is 2. A stolen base is 5.
- A counting market (strikeouts, outs, total bases): de-vigged expectation at the consensus line, then site scoring. Outs divided by 3 is innings. An inning is 2.25. A strikeout is 2. An earned run is −2. A hit allowed is −0.6. A walk allowed is −0.6. A win is 4.
- Add the components that were on the board. Do not invent a walk, a steal, or a win that no book posted.
- A hits price alone is not a full projection. If runs, RBI, and total bases are not on the board, the player is not a Vegas projection yet. Keep sweeping books before falling to industry.
- Do not manufacture a prop from a team total.

## What gets uploaded

`Name, DFS ID, Proj, Own`

- `Proj` is the Vegas consensus in site points, else the industry median, else Savant unchanged.
- `Own` is unchanged unless the user asks for an ownership pass.
- Savant 0 stays 0.
- Row order and DFS IDs stay as in the import.

## Grade

- A+: two-sided prices from DraftKings, FanDuel, and BetMGM on the starters and the posted order, converted, not blended with a site.
- A: multi-book props on the starters and most of the posted order. Industry only where every book skipped a name.
- B: one book, or one side, or starters with no prop.
