# DFS Engine Agent Team

The DFS Engine should behave like a coordinated research and portfolio team. Agents may be implemented as separate processes later; for now these roles are mandatory reasoning passes.

## Core Agents

### 1. Slate Intake Agent
Validates contest, site, slate, player pool, salaries, positions, projection columns, ownership columns, and missing data. Rejects malformed inputs before optimization.

### 2. Projection Audit Agent
Compares baseline projections with alternate industry signals and identifies meaningful disagreements. It does not automatically replace the baseline; it produces a confidence adjustment and a list of fragile projections.

### 3. News & Role Agent
Verifies current starting status, injuries, scratches, batting order or lineup position, expected minutes/usage, depth-chart changes, and other role information. It flags changes that materially affect DFS value.

### 4. Market Environment Agent
Uses betting markets and relevant contextual data to identify high-upside environments, overrated environments, and possible market movement. Examples include implied team totals, totals/spreads, park/weather, pace, and matchup quality as sport-appropriate.

### 5. Ownership & Leverage Agent
Evaluates projected ownership, likely field constructions, chalk fragility, leverage pivots, and duplication risk. It distinguishes good chalk from bad chalk rather than fading popularity mechanically.

### 6. Correlation / Game Script Agent
Builds coherent slate narratives and identifies lineups that benefit together. It creates multiple plausible game scripts rather than one deterministic prediction.

### 7. Portfolio Builder Agent
Combines projection, ceiling, ownership, leverage, correlation, and contest structure to construct the actual lineup set. It manages exposures across the portfolio, not lineup by lineup in isolation.

### 8. Exposure Auditor Agent
Produces the required side-by-side source projected ownership vs DFS Engine exposure list with percentage-point difference. It challenges the largest deviations and catches accidental concentration.

### 9. Post-Slate Learning Agent
Compares results with pre-slate theses. It categorizes misses into projection error, ownership error, role/news error, correlation error, portfolio/exposure error, or ordinary variance. Only repeated or clearly structural findings become durable engine rules.

## MLB Specialized Agents

These are mandatory for MLB slate builds in addition to the core agents.

### 10. Simulation / Outcome Distribution Agent
Moves beyond median projections to evaluate ceiling paths, volatility, boom rates, team scoring distributions, pitcher upside/failure distributions, and how often different slate scripts can plausibly produce first-place lineups. It should use Sim Savant simulation outputs when available, then challenge them with current context rather than treating them as final truth.

### 11. Stack Architecture Agent
Evaluates full-stack construction quality rather than only individual hitter quality. It scores primary 5-man stacks, secondary correlations, wraparound combinations, lineup-order connectivity, salary efficiency, platoon fit, and full-stack ownership. It should identify stacks that are individually popular but collectively over-owned, as well as under-owned combinations with coherent ceiling.

### 12. Pitcher Failure / Opposing Stack Agent
Explicitly models where popular pitchers can fail and connects those failure paths to opposing bats and stacks. It compares pitcher ownership, strikeout ceiling, contact quality allowed, platoon splits, park, weather, bullpen context, and opposing stack leverage. Pitcher fades should be tied to coherent offensive leverage rather than random avoidance.

### 13. Duplication / Lineup Uniqueness Agent
Estimates lineup duplication risk using salary usage, common pitcher pairings, chalk stack combinations, popular value bats, roster construction, and likely field behavior. It seeks enough uniqueness for contest-winning equity without sacrificing excessive projection or correlation.

### 14. Portfolio Risk Manager Agent
Audits the entire lineup set for hidden concentration. It measures exposure not only by player, but also by primary stack, secondary stack, pitcher pairing, game environment, salary construction, and game script. Its job is to prevent the portfolio from making the same underlying bet repeatedly while still preserving concentration when the Engine has a strong edge.

## MLB Default Handoff Chain

Slate Intake -> Projection Audit -> News & Role -> Market Environment -> Simulation / Outcome Distribution -> Ownership & Leverage -> Stack Architecture -> Pitcher Failure / Opposing Stack -> Correlation / Game Script -> Portfolio Builder -> Duplication / Lineup Uniqueness -> Portfolio Risk Manager -> Exposure Auditor -> Post-Slate Learning.

## Post-Slate Counterfactual Review

For MLB, the Post-Slate Learning Agent must include a counterfactual pass. It should ask what would have happened if one major decision had been correct while another was held constant, including:

- if the primary stack hit, did pitcher construction still sink the lineup?
- if the pitcher call was right, did the secondary stack or one-off construction fail?
- if the leverage thesis was correct, was exposure too low to benefit?
- if the field chalk failed as expected, did the Engine choose the right alternatives?
- was the miss caused by process or ordinary baseball variance?

The purpose is to avoid learning the wrong lesson from final standings alone.

## Handoff Protocol

Each pass should preserve:

- facts and source data
- assumptions
- derived adjustments
- confidence level
- unresolved uncertainty

Later agents should not silently overwrite earlier facts. Any change must be traceable to new evidence or an explicit model decision.