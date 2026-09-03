# Market-Derived DFS Projections

## Purpose

The DFS Engine should use betting markets as a primary projection evidence layer whenever sufficiently liquid player props and game markets exist.

The market-derived projection layer converts sportsbook probabilities into expected fantasy scoring components, then into site-specific fantasy points. It is not a direct copy of one sportsbook line and it is not a replacement for role/news validation.

## Cross-Sport Flow

1. Collect available player props, alternate/ladder props, team/game totals, moneylines, and related markets from preferred aggregators and books.
2. Remove vig from paired/two-sided markets when possible.
3. Aggregate across books using robust consensus statistics rather than a single book.
4. Infer expected player stat components and, when data supports it, component distributions.
5. Convert expected stat components into the target site's fantasy scoring.
6. Assign a market-coverage/confidence grade for each player.
7. When coverage is sparse, shrink toward a prior built from vendor/industry projections, role, and context rather than inventing missing market information.
8. Preserve raw vendor projections separately for comparison and post-slate calibration.
9. Use the resulting DFS Engine projection for simulation, leverage, candidate generation, and portfolio construction.
10. Apply GPT/AI game theory, ownership, correlation, and portfolio judgment on top of the projection layer.

## Preferred Sources

Action Network is a preferred market aggregator because it centralizes multi-book odds, props, consensus pricing, and market movement. It is not authoritative. Direct sportsbook lines and alternate sources may be used for triangulation or gap filling.

## Market Processing Rules

- Do not add overlapping prop expectations together without reconciliation.
- De-vig paired markets before converting odds to event probabilities when feasible.
- Prefer median/robust consensus across books to an outlier book.
- Use alternate/ladder markets to estimate tail probabilities and expected counts when helpful.
- Preserve timestamps and note stale/missing markets when material.
- Market coverage should be classified at minimum as High, Medium, or Low.
- High coverage may receive dominant projection weight; Low coverage should shrink materially toward the prior.
- Do not fabricate a prop or market line to complete a projection.

## Separation of Projection, Ownership, and Exposure

These are distinct outputs:

- DFS Engine Projection = our best estimate of expected fantasy scoring.
- DFS Engine Expected Ownership = our best estimate of field roster rate.
- DFS Engine Exposure = how much the portfolio should roster the player after game theory, correlation, duplication, uncertainty, and script analysis.

A player can project better than the vendor baseline but still deserve underweight exposure if expected ownership rises even more.

## Post-Slate Calibration

For each player, preserve and later compare:

- source/vendor projection
- market-derived projection
- final DFS Engine projection
- source/vendor ownership
- DFS Engine expected ownership
- actual field ownership when available
- actual fantasy score
- DFS Engine exposure
- market coverage/confidence

Grade projection calibration separately from ownership calibration and portfolio decision quality.

## Sport Modules

Each `sports/<sport>.md` file should define the specific prop markets, stat inference logic, scoring conversion, and fallback hierarchy for that sport. Cross-sport rules belong here; sport-specific formulas should not be duplicated into core files.