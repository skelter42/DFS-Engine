# Tennis DFS Engine

## Core Philosophy
Tennis projection inputs follow the cross-sport v6 contract in `CURRENT.md`: posted sportsbook scoring markets drive `Proj` only when the required scoring-market bundle is available; otherwise preserve the original Savant projection unchanged. Industry projections are reasonableness checks, not fills or co-primary votes. A moneyline is useful match context but is not, by itself, a complete fantasy-scoring projection. Keep ownership separate from the projection.

## Required Cross-Checks
- moneyline / implied win probability
- broader industry projections where available (reasonableness checks only; do not blend them into missing sportsbook scoring components)
- surface and tournament context
- opponent matchup
- expected match length and scoring upside
- retirement/injury news
- projected ownership

## Portfolio Construction
Favor players whose win probability and fantasy scoring ceiling are under-owned relative to the field. Avoid overconcentrating only on the largest favorites if that creates fragile duplicated builds.

Across a portfolio, include plausible upset paths where the leverage is justified rather than forcing contrarian plays for their own sake.

### Opponent Exclusion
- Do not roster both players from the same match in a final tournament lineup.
- Every final lineup must represent six separate winner paths.
- Treat this as a hard tennis construction and final-QA rule, not an ownership or leverage preference.

## Exposure Audit
Every delivered lineup set must include source projected ownership vs DFS Engine final exposure with percentage-point difference and explanations for the largest deviations.
