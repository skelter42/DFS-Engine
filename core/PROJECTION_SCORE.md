# Projection Score

The production estimator is model v2 in `core/PROJECTION_MODEL.md`: 0.50 × DFS-site median + 0.50 × Vegas prop. This file says what "best" means and what every run must log.

## The score

Primary score: absolute error against actual site points, by position, on the positive-Proj pool.

`AbsError = |Proj - Actual|`

Do not score a slate by lineup finish.

## Required log

Every researched player is one row in `history/YYYY-MM-DD-<SLATE>-projection-log.md`. Zeros are not rows.

| Name | DFS ID | Pos | RoleConfirmed | SiteMedian | VegasNumber | Proj | Actual | AbsError |
|---|---|---|---|---:|---:|---:|---:|---:|

- `RoleConfirmed` is yes/no at the blend. No means the page was older than the official inactive or posted order.
- No prop: `VegasNumber` is blank and Proj is the site median, labeled INDUSTRY_ONLY.
- No sites: Proj is the Vegas number, labeled VEGAS_ONLY.
- `Actual` and `AbsError` are filled after the slate. Do not backfill them into `Proj`.

## What a run must reject

- A source older than the official inactive or posted-order timestamp does not vote.
- A page still allocating to a confirmed inactive does not vote.
- A no-prop player does not get a manufactured Vegas half. Team total is a slate check, not site points.

## What the log may change

Not before three slates. Not off one game. A change is allowed only if it beats both the site median alone and the Vegas number alone on absolute error.

Allowed:
- The 0.50 / 0.50 split.
- A Tier A source that loses to the site median drops to Tier B.

Not allowed:
- A Savant weight.
- A narrative bump.
- A refit off one slate.
