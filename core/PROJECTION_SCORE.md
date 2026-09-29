# Projection Score

This file is how a Market Inputs number becomes the best projection. The estimator stays the industry median + Vegas band in `core/MARKET_PROJECTIONS.md`. This file says what "best" means, what every run must log, and the only changes the log is allowed to make.

## The score

Primary score: absolute error against actual site points, by position, on the positive-Proj pool.

`AbsError = |Proj - Actual|`

Secondary score, lump-scoring positions only (QB, TD-dependent skill players, HR-dependent hitters, pitcher wins): signed error `Proj - Actual`. A negative average means the median is light relative to the mean Savant will simulate.

Do not score a slate by lineup finish. A good roster can come from a bad projection.

## Required log

Every researched player is one row in `history/YYYY-MM-DD-<SLATE>-projection-log.md`. Zeros are not rows.

| Name | DFS ID | Pos | RoleConfirmed | IndustryMedian | VegasNumber | BandLo | BandHi | BandMoved | TierACount | Proj | Actual | AbsError |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|

- `RoleConfirmed` is yes/no at the time of the blend. No means the page was older than the official inactive or posted order, or the role was still unconfirmed.
- `BandMoved` is yes/no. No-prop players are `INDUSTRY_ONLY` in `VegasNumber` and blank band edges.
- `Actual` and `AbsError` are filled after the slate. Do not backfill them into `Proj`.

Also log the game total used for the slate check. A thin-prop slate is labeled industry-only. It is not reported as a full market read.

## What a run must reject

- A source older than the official inactive or posted-order timestamp does not vote.
- A page still allocating to a confirmed inactive does not vote.
- A no-prop player does not get a manufactured band. Team total is logged. It is not site points.

## What the log may change

Not before three slates. Not off one game. A change is allowed only if it beats both the industry median alone and the Vegas number alone on absolute error.

Allowed:
- Band width by position. The published width is 1.5 site points or 12%, whichever is larger. That is a starting constant.
- Candidate switch from median to a 60% trimmed mean, only if signed error shows the median is systematically light on lump scoring.
- Tier move. A Tier A source that loses to the median on absolute error drops to Tier B. A Tier B source that beats the median can rise. Not before the sample.

Not allowed:
- A Savant weight.
- A narrative bump.
- A peer vote for Vegas.
- A refit off one slate.

## Sample size

Three to five slates can show a bias. They cannot crown a winner. Promote a change in this file and in `core/MARKET_PROJECTIONS.md` only after that sample, and write the before/after absolute error next to the change.
