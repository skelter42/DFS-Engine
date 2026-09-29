# Projection Model v2

Status: production. Closed 2026-09-29. Replaces v1.

A run executes this. A run does not redesign it.

Industry means other DFS projection sites. Vegas means the sportsbook prop for that player. The projection is a blend of those two, and only those two.

## Output

One site-scoring number per positive-Savant-Proj player.

```
Proj = 0.50 × DFS-site median + 0.50 × Vegas prop
```

Own is unchanged. Savant 0 stays 0. Showdown CPT = 1.5 × the frozen FLEX number.

## Inputs

1. Other DFS projection sites. Numeric projections only. Not articles, rankings, podcasts, or betting write-ups.
2. Vegas player props and game odds. Where the sportsbook has the player. De-vigged. One number per player, not one number per book.
3. Role facts. Official inactive, posted order, starter versus bulk. Locked before the number.

Savant is the import file. It is not in the blend.

## Formula

1. Drop a site page that still allocates to a confirmed inactive, the wrong slate, the wrong site scoring with no conversion, or a timestamp older than the official role news.
2. Convert every remaining DFS-site number and the Vegas prop to the target site scoring.
3. Collapse a site and a page copying it to one vote.
4. Tier A votes if three or more exist. Tier B does not vote in that case. Tier A is THE BAT / BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros consensus, NumberFire, Stokastic / Awesemo, Sabersim, FantasyLabs, RotoWire, and LineStar, when they publish a number.
5. DFS-site median = median of the votes that remain. Odd count: central vote. Even count: mean of the two central votes.
6. Vegas number = de-vigged multi-book prop, converted once. Ten books are one number.
7. Blend:
   - Both exist: Proj = 0.50 × DFS-site median + 0.50 × Vegas number.
   - DFS sites only: Proj = DFS-site median, labeled INDUSTRY_ONLY.
   - Vegas only: Proj = Vegas number, labeled VEGAS_ONLY.
   - Neither: Savant fallback, labeled.
8. If player totals break the posted game total, drop the stale site vote and recompute. Do not invent a third weight.
9. Round to 2 decimals.

No converted prop means no Vegas half. Do not manufacture a prop from a team total.

## What v2 does not do

- No Savant weight.
- No per-site weight inside the median.
- No narrative adjustment.
- No band. Vegas is half the blend when a prop exists, not a fence around the sites.

## Log

Every researched player is a row in `history/YYYY-MM-DD-<SLATE>-projection-log.md`: DFS-site median, Vegas number, Proj, and later the actual site points.

## Version bump

The 0.50 / 0.50 split is declared. Change it only after three logged slates, and only if a new split beats this one on absolute error against both layers alone. One slate cannot bump the version.
