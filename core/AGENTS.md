# DFS Engine Agent Team

The DFS Engine should behave like a coordinated research and portfolio team. Agents may be implemented as separate processes later; for now these roles are mandatory reasoning passes.

## 1. Slate Intake Agent
Validates contest, site, slate, player pool, salaries, positions, projection columns, ownership columns, and missing data. Rejects malformed inputs before optimization.

## 2. Projection Audit Agent
Compares baseline projections with alternate industry signals and identifies meaningful disagreements. It does not automatically replace the baseline; it produces a confidence adjustment and a list of fragile projections.

## 3. News & Role Agent
Verifies current starting status, injuries, scratches, batting order or lineup position, expected minutes/usage, depth-chart changes, and other role information. It flags changes that materially affect DFS value.

## 4. Market Environment Agent
Uses betting markets and relevant contextual data to identify high-upside environments, overrated environments, and possible market movement. Examples include implied team totals, totals/spreads, park/weather, pace, and matchup quality as sport-appropriate.

## 5. Ownership & Leverage Agent
Evaluates projected ownership, likely field constructions, chalk fragility, leverage pivots, and duplication risk. It distinguishes good chalk from bad chalk rather than fading popularity mechanically.

## 6. Correlation / Game Script Agent
Builds coherent slate narratives and identifies lineups that benefit together. It creates multiple plausible game scripts rather than one deterministic prediction.

## 7. Portfolio Builder Agent
Combines projection, ceiling, ownership, leverage, correlation, and contest structure to construct the actual lineup set. It manages exposures across the portfolio, not lineup by lineup in isolation.

## 8. Exposure Auditor Agent
Produces the required side-by-side source projected ownership vs DFS Engine exposure list with percentage-point difference. It challenges the largest deviations and catches accidental concentration.

## 9. Post-Slate Learning Agent
Compares results with pre-slate theses. It categorizes misses into projection error, ownership error, role/news error, correlation error, portfolio/exposure error, or ordinary variance. Only repeated or clearly structural findings become durable engine rules.

## Handoff Protocol

Each pass should preserve:

- facts and source data
- assumptions
- derived adjustments
- confidence level
- unresolved uncertainty

Later agents should not silently overwrite earlier facts. Any change must be traceable to new evidence or an explicit model decision.