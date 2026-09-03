# Core DFS Engine

## Slate Workflow

### 1. Ingest
Collect the site player pool/contest file, baseline projections, projected ownership, salaries, positions, and any available ceiling/floor or simulation outputs.

### 2. Validate
Check names, teams, positions, salaries, game inclusion, injuries/availability, projected starters, and obvious data mismatches before optimization.

### 3. Cross-check the market
Do not anchor to a single source. Compare baseline projections and ownership against broader industry information, betting markets, team totals, matchup context, injuries/news, role changes, and relevant environmental factors.

### 4. Build slate theses
Identify the most plausible ways the slate can be won. Each thesis should describe what must happen, which players/teams benefit, which popular constructions fail, and where leverage appears.

### 5. Construct portfolios
Build lineups as a coordinated portfolio rather than isolated top-projection lineups. Coverage should represent distinct plausible game scripts while preserving enough concentration to benefit when a thesis is right.

### 6. Audit exposures
For every delivered lineup set, report source projected ownership versus DFS Engine exposure with percentage-point difference. Investigate large deviations and ensure they are intentional.

### 7. Final news pass
Re-check official lineups, injuries, scratches, batting order/starting roles, weather where relevant, and late market movement. Re-optimize when role changes materially alter projection, correlation, or ownership.

### 8. Post-slate learning
Review what won, what the engine captured, what it missed, and whether the failure came from projections, ownership, correlation, portfolio construction, or variance. Promote only durable lessons into the brain.

## Portfolio Philosophy

The engine should not merely maximize raw projected points. It should balance:

- projection
- ceiling
- ownership/leverage
- correlation
- lineup duplication risk
- uncertainty
- contest payout structure
- game-script coverage

Large-field GPP portfolios should accept individual-lineup volatility in exchange for stronger first-place equity. Small-field or flatter-payout contests may justify less leverage and more median projection.

## Exposure Rules

Exposure is a decision output, not an input copied from projected ownership. A player may be over the field because of superior ceiling, role, correlation, or mispriced ownership. A player may be under the field because the market is overconfident, the projection is fragile, or the portfolio already captures the same outcome through correlated alternatives.

Never make a large exposure deviation without an explicit reason.

## Source Comparison Requirement

Every final lineup set must include a table with at least:

| Player | Source Projected Ownership | DFS Engine Exposure | Difference (pp) |
|---|---:|---:|---:|

Sort or highlight the largest positive and negative deviations.

## Anti-Hallucination Rules

- Never invent a player, salary, projection, ownership figure, lineup slot, injury, betting line, or contest rule.
- If an input is missing, label it missing rather than fabricating it.
- Distinguish verified facts from model assumptions.
- When current information matters, verify it before using it.
- Preserve source data separately from derived DFS Engine adjustments.

## Versioning

Durable changes to logic belong in this repository. Slate-specific opinions belong in dated slate notes or results files, not in core rules unless they generalize across multiple slates.