# Vegas Consensus — the projection

This is the operating framework for every sport. Model owner is `core/PROJECTION_MODEL.md` v3. This file is how a run builds the number that gets uploaded to Sim Savant.

## Thesis

Look across prop boards. DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Fanatics, and any other book that posts the market. Each price is a percentage chance. Strip the book edge. Consensus those percentages. Convert the consensus into site points. That expected point total is the projection uploaded to Savant.

The blend is across sportsbooks. It is not a blend with a DFS site, and it is not a blend with Savant.

## Priority

1. Multi-book prop consensus, converted to site points. This is the projection.
2. DFS-site median, only for a player no book has priced.
3. Savant, only when there is no prop and no site number. Leave it unchanged.

Savant is the last priority. A positive Savant number does not vote if either layer above exists.

## Books

Hit boards, not names. A board lists many players and many markets on one page.

Required book set when posted: DraftKings, FanDuel, BetMGM. Add Caesars, BetRivers, Fanatics, and the consensus page of an aggregator (Action Network, Covers, PropCruncher, OddsShopper) when it shows the actual prices.

One book is not a consensus. A one-sided price is not a consensus. An article that mentions a line is not a board.

## From odds to a percentage

American odds to implied probability:

- Plus price: `100 / (odds + 100)`. +150 is 40%.
- Minus price: `odds / (odds + 100)`. −150 is 60%.

Remove the edge. If the over is 40% raw and the under is 64% raw, the two sides sum to 104%. De-vigged over is `40 / 104`. Do this inside each book, then take the median de-vigged probability across books. Ten books are one number.

The line is the median line. Do not average a 7.5 with a 6.5 into a 7.0 if most books are on 7.5. Note the outlier book and keep the median.

## From a percentage to points

The upload is expected site points, not the probability itself.

- A 0.5 market (hits, home runs, RBI, to-score): de-vigged over probability times the site points that event is worth.
- A counting market (strikeouts, outs, total bases, yards): de-vigged expectation at the consensus line, then site scoring.
- Add only components that were on the board. Do not invent a walk, a steal, or a win that no book posted.
- Do not manufacture a prop from a team total. Team total is a check, not a player projection.

DraftKings MLB, when the component is posted: pitcher strikeouts, outs, earned runs, hits allowed, walks, win. Hitter hits, home runs, total bases, RBI, runs, walks, stolen bases.

## What gets uploaded

`Name, DFS ID, Proj, Own`

- `Proj` is the Vegas consensus in site points, else the industry median, else Savant unchanged.
- `Own` is unchanged unless the user asks for an ownership pass.
- Savant 0 stays 0.
- Row order and DFS IDs stay as in the import.

## Grade

- A+: two-sided prices from DraftKings, FanDuel, and BetMGM on the starters and the posted order, converted, not blended with a site.
- A: multi-book props on the starters. Industry only where the board skipped a name.
- B: one book, or one side, or starters with no prop.
