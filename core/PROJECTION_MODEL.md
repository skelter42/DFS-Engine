# Projection Model v1

Status: production. Closed 2026-09-29.

This is the finished Market Inputs model. A run executes it. A run does not redesign it.

Constants below are declared, not fitted. Changing one is a version bump in this file after the score in `core/PROJECTION_SCORE.md` says the change beats both layers alone. One slate cannot bump the version.

## Output

One site-scoring number per positive-Savant-Proj player.

```
Proj = consensus, pulled to the Vegas band if it sits outside
```

Own is unchanged. Savant 0 stays 0. Showdown CPT = 1.5 × the frozen FLEX number.

## Inputs

1. Other DFS projection sites. Numeric projections only. Not articles, rankings, podcasts, or betting write-ups.
2. Vegas player props. Where the sportsbook has the player. De-vigged, one number per player, not one number per book.
3. Role facts. Official inactive, posted order, starter versus bulk. Locked before the number.

Savant is the import file. It is not an input vote.

## Formula

1. Drop a site page that still allocates to a confirmed inactive, the wrong slate, the wrong site scoring with no conversion, or a timestamp older than the official role news.
2. Convert every remaining number to the target site scoring.
3. Collapse a site and a page copying it to one vote.
4. Tier A votes if three or more exist. Tier B does not vote in that case. Tier A is THE BAT / BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros consensus, NumberFire, Stokastic / Awesemo, Sabersim, FantasyLabs, RotoWire, and LineStar, when they publish a number. Tier B is any other DFS site page.
5. Consensus = median of the votes that remain. Odd count: central vote. Even count: mean of the two central votes. One vote: that vote. None: Savant fallback, labeled.
6. Vegas number = de-vigged multi-book prop, converted once. Band = that number ± max(1.5 site points, 12% of the Vegas number).
7. If consensus is inside the band, Proj = consensus. If outside, Proj = nearest edge. No converted prop: Proj = consensus, labeled INDUSTRY_ONLY. Do not invent a band.
8. If player totals break the posted game total, drop the stale vote and recompute. Do not reweight.
9. Round to 2 decimals.

## What v1 does not do

- No Savant weight.
- No peer vote for Vegas.
- No narrative adjustment.
- No position-specific band. Width is the declared constant above.
- No trimmed mean. The candidate is the median until a version bump.

## Log

Every researched player is a row in `history/YYYY-MM-DD-<SLATE>-projection-log.md` with the columns in `core/PROJECTION_SCORE.md`. Actuals are filled after the slate. They do not rewrite that slate's Proj.

## Version bump

Only after three logged slates, and only if the new rule beats both the consensus alone and the Vegas number alone on absolute error. Allowed bumps: band width by position, median to a 60% trimmed mean, a Tier A source moving to Tier B. Write the before/after error next to the bump.
