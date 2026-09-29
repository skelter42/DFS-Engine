# Projection Model v3

Status: production. A run executes this. A run does not redesign it.

The projection is Vegas-driven. Industry is the fill. Savant is the last resort, unchanged.

## Output

```
Props exist     -> Proj = those prices, converted to site points
No props        -> Proj = DFS-site median
Neither         -> Proj = Savant, unchanged
```

Own is unchanged. Savant 0 stays 0. Showdown CPT = 1.5 × the frozen FLEX number.

## Odds

Plus price: `100 / (odds + 100)`. +200 is 33%. +155 is 39%. +105 is 49%.

Minus price: `odds / (odds + 100)`. −150 is 60%.

Never use `odds / (odds + 100)` on a plus price. That flips it. +155 is not 61%.

Both sides: divide each implied probability by the sum of the two. That removes the vig.

One side: still convert. Haircut about 4.5% for the missing vig. A one-sided anytime goal is the goal piece. It is not thrown out.

## Points

A 0.5 price is the chance the event happens. Expected count is `-ln(1 - p)`.

A counting line moves by the over probability. Expected value is the line plus the de-vigged over probability minus 0.5.

Add the pieces that were priced. Do not average a DFS site into a priced piece. Do not invent a piece from a team total.

A goal price alone is the goal piece, not the whole player. Add the shot line, or the outs line, before that name is finished.

DraftKings, when posted. Goal 8.5, assist 5, shot 1.6, block 1.3. Save 0.7, goal against −3.5, win 6. Baseball inning 2.25, strikeout 2, win 4, earned run −2, hit allowed −0.6, walk allowed −0.6. Single 3, double 5, triple 8, home run 10, RBI 2, run 2, walk 2, stolen base 5. Football passing yard 0.04, passing touchdown 4, interception −1, rush or receiving yard 0.1, touchdown 6, reception 1.

## Order

1. Savant 0 stays 0.
2. Hit the prop board, not the name. DraftKings, FanDuel, BetMGM, and the other books.
3. Convert every posted price. Median the books. That is Proj.
4. No price: DFS-site median.
5. No site number: Savant, unchanged.

Try the whole positive file. The floor is the group the books price: baseball lineup and pitcher, football skill players and defense, hockey top lines, goalies, and priced defensemen.

## What v3 does not do

- No 50/50 blend.
- No Savant weight inside a Vegas or industry number.
- No band.
- No flipped plus-money formula.

## Log

Every output reports the mix on the relevant group first, then the rest of the positive file: n Vegas, n industry, n Savant, as counts and percentages. Zeros are separate and not in the percentage.
