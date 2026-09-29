# Projection Model v3

Status: production. Closed 2026-09-29. Replaces v2.

A run executes this. A run does not redesign it.

v2 blended a DFS-site median 50/50 with a prop. That commit is retired. The user corrected it the same day: the projection is Vegas-driven. Industry is the fill. Savant is the last resort, unchanged.

## Output

One site-scoring number per positive-Savant-Proj player.

```
Props exist     -> Proj = Vegas consensus, converted to site points
No props        -> Proj = DFS-site median
Neither         -> Proj = Savant, unchanged
```

Own is unchanged. Savant 0 stays 0. Showdown CPT = 1.5 × the frozen FLEX number.

## Order

1. Lock the role. Confirmed inactive stays 0. Opener versus bulk versus full start is locked before the number.
2. Hit the prop board, not the name. Multi-book. Every book that posts the market.
3. If a convertible prop exists, that consensus is the projection. Do not average it with a DFS site.
4. If the board has nothing on that player, use the DFS-site median.
5. If there is no site number either, leave Savant as it came in.

## Vegas consensus

One number per player, not one number per book.

1. American odds to implied probability. +150 is 40%. −150 is 60%.
2. Remove the book edge. De-vig the two sides so they sum to 1. A one-sided price is not a consensus.
3. Consensus is the median de-vigged probability across books, at the median line. Ten books are one number.
4. Points come from that probability. A 0.5 over is the de-vigged chance the event happens, times the site points that event is worth. A counting line (strikeouts, outs, total bases) uses the de-vigged expectation, then the same site scoring.
5. Add the components. Do not add a component that was not on the board.

DraftKings MLB components, when posted: pitcher strikeouts, outs, earned runs, hits allowed, walks, win. Hitter hits, home runs, total bases, RBI, runs, walks, stolen bases.

No prop means no Vegas number. Do not manufacture one from a team total.

## Industry fill

Only when the board has no convertible prop for that player.

Numeric DFS projection sites only. Not articles, rankings, or betting write-ups. Collapse a site and a page copying it to one vote. Median of the votes. Tier A is THE BAT / BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros consensus, NumberFire, Stokastic / Awesemo, Sabersim, FantasyLabs, RotoWire, and LineStar, when they publish a number.

## What v3 does not do

- No 50/50 blend. Vegas is the projection when a prop exists, not half of it.
- No Savant weight inside a Vegas or industry number.
- No narrative adjustment.
- No band.

## Log

Every researched player is a row in `history/YYYY-MM-DD-<SLATE>-projection-log.md`: books used, de-vigged consensus, site points, and the label VEGAS, INDUSTRY, or SAVANT.

## Version bump

v2 was retired by explicit user correction on 2026-09-29, not by the three-slate error test. Change v3 only the same way, or after three logged slates if a different estimator beats Vegas-alone on absolute error.
