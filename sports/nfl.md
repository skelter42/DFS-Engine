# NFL DFS Engine

## Core Philosophy
NFL DFS should combine projection, ceiling, ownership, correlation, game environment, and contest structure. Classic generally offers stronger portfolio-building opportunities than showdown because more independent game environments can be expressed.

## Required Checks
- injuries and active/inactive status
- starting roles and depth chart
- spreads, totals, and implied team totals
- target/rush share and red-zone role
- projected ownership
- weather where material

## Vegas-First Market Inputs
For every NFL `market inputs` pass, projection creation is Vegas-first. Do not use an industry fantasy projection as the primary replacement when sportsbook markets are available.

Projection source priority:
1. Sportsbook/player-prop markets across as many books as practical (DraftKings, FanDuel, BetMGM, Caesars, bet365, Fanatics and other credible books/odds aggregators).
2. Convert the betting market directly into DraftKings fantasy expectation using the official DK scoring rules. Use the fullest available prop bundle by role: passing yards/TDs/INTs and rushing for QBs; rushing attempts/yards, receptions, receiving yards and TD probability for RBs; receptions, receiving yards, rushing usage and TD probability for WR/TE; game spread/total and team scoring expectation for DST/kickers where appropriate.
3. Use vig-free probabilities and consensus/median lines when multiple books are available. Line movement is actionable information and should influence the projection rather than being ignored.
4. If a player has only partial Vegas coverage, anchor the covered components to Vegas and use industry/model information only to fill the missing components.
5. Use broader industry projections only when sportsbook coverage is genuinely insufficient.
6. Sim Savant is the final fallback, not the primary source.

Never lower the reported Vegas coverage merely because a player lacks one particular prop. A player with meaningful sportsbook markets should be classified as Vegas-driven or Vegas-anchored. Do not manufacture confidence for deep backups with no meaningful market; leave them on the best fallback source and label them accordingly in analysis.

For very early builds, preserve the Vegas-first hierarchy but mark projections provisional because props, injuries, depth-chart roles, weather and lines can move materially before lock. Re-run the market-input pass closer to lock whenever practical.

## Pregame Projection Process

This is the implemented NFL projection method. Cross-sport hierarchy lives in
`core/MARKET_PROJECTIONS.md`; the formulas and constants below are NFL-specific
and are **modeling decisions**, not sportsbook rules. Calibrate them against
realized outcomes before treating them as optimal.

### 1. Eligible pool

Start from the DraftKings salary file. Match to stable identities, positions,
teams, opponents and game times; for Showdown preserve separate Captain and FLEX
IDs for the same player. Remove inactives *before* allocating team production.

An absent prop is not a zero projection. An excluded player and an active player
with a small modeled role are different cases.

Showdown coverage target per team, where the roster supports it: one starting QB,
two RBs, four WRs, two TEs, the kicker and the defense.

### 2. Markets to collect

| Position | Useful inputs |
|---|---|
| QB | Passing yards, passing TDs, interceptions, rushing yards, anytime TD; attempts/completions as supporting inputs |
| RB | Rushing yards, receiving yards, receptions, anytime TD; rushing attempts as a workload check |
| WR/TE | Receiving yards, receptions, anytime TD; rushing yards where relevant |
| K | Made field goals, made extra points, distance information when available |
| DST | Sacks, turnovers, defensive TDs, opponent team total and passing volume |

Save each observation with player, game, statistic, line, over price, under
price, book/board, source URL and observation time. Pair over and under **from
the same book at the same line**; never pair the best over from one book with
the best under from another and call it a market. Bet percentages, handle,
analyst picks and other models' forecasts are not sportsbook odds. Count a book
seen through several aggregators once.

### 3. Consensus

Fit an expected value per independent book, then take the **median of those
fitted means**. Record whether a component came from a multi-book consensus, one
verified paired book, or a labeled consensus board.

### 4. Distribution choices

**Yardage — Gamma.** Coefficients of variation: passing 0.30, rushing 0.55,
receiving 0.65. For line `L` and fair over probability `p`:

```
shape = 1 / CV^2
scale = L / GammaQuantile(1 - p, shape)
expected_yards = shape * scale
```

Because the distribution is skewed, expected yards exceed a balanced-price line.
The nonnegative Gamma is an approximation for stats that can occasionally be
negative.

**Receptions, passing TDs, interceptions — Poisson.** Solve
`P(X > floor(L)) = fair_over` for the mean. Do not substitute the line or the
probability for the expected count. Integer lines can push and are rejected
rather than treated as half-integer lines.

**Anytime TD — expected count, not a probability.** For a one-sided price the
fallback is an 8% probability reduction, then a Poisson inversion:

```
p = implied_probability * 0.92
expected_TD_count = -ln(1 - p)
```

`6 x anytime_probability` would cap the player at one score. Keep passing TDs
separate from rushing/receiving TDs; a QB's anytime-TD mean belongs to the
latter. Individual return TDs are not separately projected.

### 5. Uncovered components

Fill from the role/workload model — expected opportunities, receiving
involvement, recent usage, depth-chart role, or a saved estimate. Those inputs
need their own basis; they cannot be inferred from the absence of a prop.
Preserve component-level provenance: a player with a TD prop and estimated
receiving yards is partly modeled, not fully market-derived.

Lost-fumble fallback for RB/WR/TE:
`0.0035 * (expected receptions + 0.22 * expected rushing yards)`. QB lost fumbles
use a separate estimate. Two-point conversions and individual return/recovery
TDs carry no projected contribution; do not invent one to complete the table.

### 6. Team reconciliation

Apply availability changes and raw market updates first, then reconcile the
active receiving pool **once**:

```
yard_factor = QB expected passing yards / sum(raw receiving yards)
TD_factor   = QB expected passing TDs   / sum(raw receiving TDs)
```

Split each player's raw rushing/receiving TD mean into a receiving component and
a remainder. Fallback receiving shares: 1.00 for WR/TE, 0.12 for RB — assumptions,
replaceable with player-specific shares. Only the receiving component is
rescaled. QB rushing scores are separate, and receptions are not rescaled by the
yardage factor.

Always compute factors from **raw** values so reruns cannot compound the scaling.
A zero denominator means missing inputs and must be resolved. This step can move
a projection away from its direct prop-derived value; it is a team-consistency
adjustment, not a change to the observed quote. Preserve both raw and adjusted
fields.

### 7. DK scoring and bonuses

```
DK = 0.04*pass_yards + 4*pass_TD - 1*INT
   + 0.10*(rush_yards + rec_yards) + 1*receptions
   + 6*(rush+rec TDs) - 1*lost_fumbles + 2*two_point
   + expected yardage bonuses
```

Bonuses are **probabilities**, not all-or-nothing awards on the projected mean:

```
bonus = 3*P(pass_yards >= 300) + 3*P(rush_yards >= 100) + 3*P(rec_yards >= 100)
```

Compute each tail from the Gamma model using the **final adjusted** means
(`shape = 1/CV^2`, `scale = mean*CV^2`). Do not add a rush+rec combined prop on
top of its components. When reusing a model built for another platform, reuse its
expected statistics and apply DK scoring from scratch — a half-PPR total is not a
full-PPR DK projection.

### 8. Kickers and defenses

Use direct props where they exist. Otherwise, with game total `T` and expected
home margin `M`, implied points are `(T ± M) / 2`.

Kicker — a residual-scoring model. Sum the team's expected rushing/receiving TDs
including QB rushing scores; do not also add passing TDs, which would double
count receiving scores.

```
expected_XP_made = 0.96 * team_offensive_TD_mean
residual         = team_implied_points - 6*team_offensive_TD_mean - expected_XP_made
expected_FG_made = max(0, residual / 3)
DK_per_FG        = 0.55*3 + 0.30*4 + 0.15*5 = 3.60
kicker_DK        = expected_XP_made + 3.60 * expected_FG_made
```

The distance mix is 55% under 40 yards, 30% at 40-49, 15% at 50+. A negative
residual is flagged even though the FG mean is floored at zero.

Defense — with `advantage = own_implied - opponent_implied`:

```
opponent_dropbacks = opponent_pass_attempts / 0.93
sacks              = dropbacks * 0.07 * max(0.75, 1 + 0.04*advantage)
interceptions      = opponent QB expected INTs   (fallback 0.023 * attempts)
fumble recoveries 0.40, safeties 0.035, blocked kicks 0.035
defensive/ST TDs   = 0.12 + 0.005*max(advantage, 0)
```

Points allowed uses a Normal centered on the opponent implied total with SD 10,
weighting each DK band by its probability (0 → 10; 1-6 → 7; 7-13 → 4; 14-20 → 1;
21-27 → 0; 28-34 → -1; 35+ → -4). Half-point boundaries on a continuous
distribution approximate the discrete scoring.

```
DST_DK = sacks + 2*(INT + fumble recoveries + safeties + blocked kicks)
       + 6*defensive/ST TDs + expected points-allowed score
```

### 9. Freeze and validate

Retain identity, team/opponent, eligibility, salary/slot IDs, all raw means,
final means, source references, model assumptions, projected DK points, and a
projection version/time. Before freezing, confirm:

- every market belongs to the correct player, game, statistic and pregame period, with duplicate book observations removed;
- recovered probabilities lie in (0, 1) and fitted distributions reproduce their source threshold probabilities;
- every active eligible player has an explicit projection basis, and inactives cannot reach the lineup builder;
- reconciled team receiving yards equal projected QB passing yards, and allocated receiving TDs equal QB passing TDs;
- bonuses use final means, and catches, lost fumbles and TD categories carry the correct weights;
- passing TDs and receiver TDs are credited to their own players without double counting in the team model;
- a manual scoring example agrees with the code, and large raw-to-adjusted changes are inspectable.

For Showdown, Captain points are 1.5x the FLEX projection, applied once.

### Portfolio flow

One documented flow consumes these frozen projections without modifying them:
enumerate legal lineups under the slate's settings, retain the configured
high-projection pool (often the top 10%), maximize average pairwise uniqueness,
retain at least 90% of that maximum, then maximize average projected points.
Correlation requirements shape lineup construction; they never add points to
player means.

## Correlation
Use QB-pass catcher stacks as a foundational correlation tool. Bring-backs should be driven by game script and ownership rather than forced mechanically. Running backs can correlate strongly with favored game scripts; opposing passing volume can rise in those same scripts.

## Showdown
Treat showdown as a distinct, duplication-sensitive format. Use uniqueness and game-script coherence aggressively. When testing showdown rules, explicitly track whether constraints such as at least one QB in flex improve results before promoting them to core logic.

## Exposure Audit
Every delivered lineup set must include source projected ownership vs DFS Engine exposure with percentage-point difference and explanations for meaningful deviations.