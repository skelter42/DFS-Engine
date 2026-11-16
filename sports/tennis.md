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

### Opponent Exclusion and Contest-Format Scope

For the six-player salary-cap slate format, the Engine's preferred construction is to avoid rostering both players from the same match and to represent six distinct match-winner paths. This is an Engine portfolio preference, not a DraftKings lineup-legality rule.

Do not apply the six-winner requirement universally across tennis formats. DraftKings also publishes:
- Short Slate contests with 3 roster spots (Captain, Assistant Captain, Player) and 1.5x / 1.25x captain multipliers.
- Snake contests with 5 roster spots (4 starting players plus 1 bench player).

Before construction, confirm the actual contest format and use its roster requirements. Tennis scoring is also format-dependent: the official rules distinguish best-of-3 from best-of-5 scoring, with different game/set/ace/break values and bonuses. Do not reuse one scoring conversion across both formats without checking the current contest rules.

Official DraftKings references (reviewed 2026-11-16):
- Single Match: https://lp.draftkings.com/help/rules/tennis/single-match
- Short Slate: https://lp.draftkings.com/help/rules/tennis/short-slate
- Snake: https://lp.draftkings.com/help/rules/tennis/snake

## Exposure Audit
Every delivered lineup set must include source projected ownership vs DFS Engine final exposure with percentage-point difference and explanations for the largest deviations.
