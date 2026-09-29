# Vegas Consensus — the projection

Do this every time. The first action is the prop board.

## Order

1. Prop boards across DraftKings, FanDuel, BetMGM, and every other book that posts the market.
2. Each price is a percentage. +150 is 40%. Strip the vig inside that book so the two sides sum to 1. Median the books.
3. Convert the consensus into site points. That is the projection uploaded to Savant.
4. No prop after the sweep: industry consensus, the median of DFS-site projections.
5. No site number either: Savant, unchanged.
6. Savant 0 stays 0.

The blend is across sportsbooks. A DFS site does not get averaged into a priced player. Savant does not get a weight.

## Board

Loop games, not names. One event page covers the game. Pull every priced pitcher and every priced hitter. Both sides. A one-sided price is not a consensus. A hits price alone is not a full projection. Keep sweeping before a player falls through.

DraftKings points, when the component is posted: inning 2.25, strikeout 2, win 4, earned run −2, hit allowed −0.6, walk allowed −0.6. Single 3, double 5, triple 8, home run 10, RBI 2, run 2, walk 2, stolen base 5.

Do not invent a prop from a team total.

## Required mix

Every output, on the positive-Proj pool:

- n Vegas (x%)
- n industry, no prop (x%)
- n Savant fallback (x%)
- n zeros left at 0, not in the percentage
