# Vegas Consensus — the projection

Do this every time. The price is the projection. Convert it.

## Odds to a probability

Plus price: `100 / (odds + 100)`. +200 is 33%. +155 is 39%. +105 is 49%.

Minus price: `odds / (odds + 100)`. −150 is 60%.

Never use `odds / (odds + 100)` on a plus price. That flips it. +155 is not 61%.

Both sides: divide each implied probability by the sum of the two so they add to 1. That removes the vig.

One side: still convert. Haircut about 4.5% for the missing vig. A one-sided anytime goal is the goal piece.

## Probability to points

A 0.5 price is the chance the event happens. Expected count is `-ln(1 - p)`.

A counting line moves by the over probability. Expected value is the line plus the de-vigged over probability minus 0.5.

DraftKings, add the pieces that were priced:

- Goal 8.5. Assist 5. Shot 1.6. Block 1.3.
- Save 0.7. Goal against −3.5. Win 6.
- Baseball: inning 2.25, strikeout 2, win 4, earned run −2, hit allowed −0.6, walk allowed −0.6. Single 3, double 5, triple 8, home run 10, RBI 2, run 2, walk 2, stolen base 5.
- Football: passing yard 0.04, passing touchdown 4, interception −1, rushing or receiving yard 0.1, rush or receiving touchdown 6, reception 1.

A shot is already in the shot line. A goal is extra. Add both. Do not average a DFS site into a priced piece.

A goal price alone is the goal piece, not the whole player. Add the shot line before that name is a finished projection.

## Order

1. Boards across DraftKings, FanDuel, BetMGM, and the other books. Loop games.
2. Convert every posted price. Median the books.
3. No price: industry median.
4. No site number: Savant, unchanged.
5. Savant 0 stays 0.

Try the whole positive file. The floor is the group the books price.

## Mix

Every output, counts and percentages, relevant group first:

- n Vegas
- n industry, no prop
- n Savant
- n zeros, not in the percentage
