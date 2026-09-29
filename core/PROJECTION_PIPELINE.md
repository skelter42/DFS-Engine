# Market Inputs Projection Pipeline (executable preview)

`core/MARKET_PROJECTIONS.md` remains the projection policy. This document describes the executable NFL/MLB/NHL prototype under `src/dfs_engine/`. It is a **mean DraftKings-point** converter, because a betting line is a threshold and the median of component lines is not the median of a player's fantasy score. A true fantasy-score median requires a calibrated joint outcome distribution; keep it separate from the `Proj` used by an optimizer.

## Slate cycle

1. Freeze the precise DFS contest slate: site, games and lock time, original Savant CSV, player IDs, positions, source projections and ownership. Keep every zero row unchanged unless an active-role conflict is explicitly resolved. Preserve the original CSV separately.
2. Before odds ingestion, populate a slate template with independent numeric **component** priors and role status. MLB requires confirmed/projected batting order or starter/bulk workload; NHL requires line role and confirmed starting goalie. Unverified active roles preserve their original projection with a warning in the audit. A verified inactive is zeroed.
3. Pull complete event odds boards and alternate thresholds across books. The event ID and provider player name must map explicitly to one slate game and one DFS ID. Pair over/under or yes/no at the **same book and strike**. Save book and timestamp. The import rejects stale quotes over two hours old, one-sided markets, unmapped names and off-slate games.
4. Convert priced thresholds to expected *stat components*, not directly to fantasy points. For NHL/MLB count props, the prototype fits a Poisson mean and records the fit method. This is a **provisional distribution assumption**, especially for total bases, saves, shots and workload. A count ladder that disagrees by over 10 probability points is rejected. For NFL yards, alternate lines fit spread; one line requires externally calibrated spread. No numeric source is allowed to silently create a missing component.
5. Blend market and industry at the **component** level where both are credible. Today the prototype uses a market estimate for a supported component and an explicit independent component prior for missing ones. Fixed MLB fantasy-point weights and the general 10-source grade are **not validated error weights**. Do not claim a better full-slate composite merely because more pages were read.
6. Apply DK scoring and explicit milestone/event probabilities once. Check identities such as MLB hits/total bases/HR, NHL goals+assists/points, game and team environments, and hitter/pitcher/goalie role. MLB team totals inform run environment and PA allocation; a team total multiplied by batting slot is **not** itself a hitter fantasy-point projection.
7. Export the exact Savant import schema with unchanged `Own`. Keep uncovered positive rows at their source projection and list reasons in the audit. Report coverage for the *active slate pool* and the full positive-source pool separately; a fallback is not Vegas-backed merely because a team market exists.
8. Freeze the pre-lock audit and current quote snapshot. After games finish, grade only players with paired pre-lock Engine and source projections. Track MAE, RMSE and signed bias by sport, position/role, source coverage, and time to lock. Use a meaningful sequence of slates to tune dispersion, source weights and component choices; never fit and evaluate on the same slate. Evaluate bonus probability calibration separately with Brier scores when event outcomes are available.

## Run surfaces

- `python -m dfs_engine.odds_ingest --template template.json --events event-odds.json --event-map event-map.json --player-map player-map.json --output inputs.json --audit odds-audit.json`
- `python -m dfs_engine.cli --source savant.csv --inputs inputs.json --output preview.csv --audit prelock-audit.json`
- `python -m dfs_engine.evaluate --audit prelock-audit.json --actuals actuals.csv --report scorecard.json` after completion. Results require `DFS ID,DK Points` and must use the same base player scoring (not a CPT-multiplied number).

The odds ingester accepts event response JSON in The Odds API's `oddsFormat=american` shape. Player map keys are `eventId|provider player name`; values are exact Savant `DFS ID`s. Event map keys are provider event IDs; values are exact game IDs from the slate template. It normalizes available supported player markets only. The template supplies component and bonus priors; the ingester does not manufacture them. No API key is stored in the repo.

## MLB template contract

`sport: "MLB"`, `site: "DraftKings"`, `slate`, `as_of_utc`, `lock_utc`, `games: [game_id...]`, `players: {DFS_ID: ...}`. Every player entry needs `game`, `kind` (`hitter` or `pitcher`), `active_role: true`, and numeric priors for missing market components. `inactive: true` zeroes a confirmed inactive. Preserve and check team, opponent, batting slot, expected PA/outs, park and lineups in the raw research audit; they inform priors but do not automatically create fake fantasy points.

- Hitter component fields: `hits`, `total_bases`, `triples`, `home_runs`, `rbi`, `runs`, `walks`, `hbp`, `stolen_bases`. `hits + 2*total_bases + triples + home_runs` scores the four hit types exactly, then runs, RBI, walks/HBP and steals are added. This identity avoids scoring a home run again on top of its total bases. Cross-market inconsistencies fail closed.
- Pitcher component fields: `outs`, `strikeouts`, `earned_runs`, `hits_allowed`, `walks_allowed`, `hbp_allowed`. `event_priors` or paired `event_markets` supply `win`, `complete_game`, `complete_game_shutout`, `no_hitter`. Outs are worth 0.75 DK each. Confirm full starter vs opener/bulk and postseason pitch limits before using a workload prior.

## NHL template contract

Same slate fields with `sport: "NHL"`. Every player has `game`, `kind` (`skater` or `goalie`), `active_role: true` and numeric missing-component priors. Confirm lines/power-play usage and starting goalie near lock.

- Skater components: `goals`, `assists`, `shots`, `blocks`, `shorthanded_points`, `shootout_goals`. For missing priced count distributions, `bonus_priors` supplies `hat_trick`, `five_shots`, `three_blocks`, `three_points`. A priced `points` ladder may determine 3+ points probability; do not add its mean on top of goals and assists.
- Goalie components: `saves`, `goals_against`, `goalie_goals`, `goalie_assists`. `event_priors` supplies `win`, `shutout`, `ot_loss` unless correctly paired individual-goalie markets are available; a team's moneyline is not automatically a goalie's win probability. `bonus_priors` supplies `saves35` when saves distribution is not market-fitted. A shootout loss can coexist with a zero-goals-allowed shutout.

## Delivery standard

This prototype is **not** a final A-grade projection engine. It lacks automatic independent component priors, historically learned count distributions, source weighting, game-total reconciliation and demonstrated out-of-sample accuracy. A preview can be generated only after a real slate template and current quotes exist. If these inputs are thin, return the audited source rather than assigning a false precision or high grade.
