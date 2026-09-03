# Market-Derived DFS Projections

## Purpose

The DFS Engine is a Vegas-first projection system whenever sufficiently liquid player props and game markets exist.

Market-derived projections are the primary estimate of expected fantasy scoring. Vendor projections such as Sim Savant are fallback priors used only when market coverage is weak, incomplete, stale, internally inconsistent, or unavailable. Industry projections are primarily sanity checks and secondary fallback evidence rather than equal-weight ingredients.

The market-derived projection layer converts sportsbook probabilities into expected fantasy scoring components, then into site-specific fantasy points. It is not a direct copy of one sportsbook line and it is not a replacement for role/news validation.

## Canonical Projection Hierarchy

1. Vegas / multi-book player props and game markets — primary projection evidence.
2. Sim Savant / trusted vendor projection — fallback prior when Vegas signals are weak.
3. Broader industry projections — sanity check, outlier detection, and secondary fallback evidence.
4. Verified role/news/context — required validity layer that can override stale market assumptions when a player's role changes materially.

The Engine should not begin from Savant and then add a Vegas adjustment when sufficient player-level markets exist. It should begin from the market-derived fantasy projection and add prior weight only to the extent justified by weak market coverage.

## Cross-Sport Flow

1. Collect available player props, alternate/ladder props, team/game totals, moneylines, and related markets from preferred aggregators and books.
2. Remove vig from paired/two-sided markets when possible.
3. Aggregate across books using robust consensus statistics rather than a single book.
4. Infer expected player stat components and, when data supports it, component distributions.
5. Convert expected stat components into the target site's fantasy scoring.
6. Assign a market-coverage/confidence grade for each player.
7. Set the DFS Engine projection primarily from the market-derived projection.
8. Increase fallback-prior weight only as market coverage/confidence deteriorates.
9. Preserve raw Savant/vendor projections separately for comparison and post-slate calibration.
10. Use the resulting DFS Engine projection for simulation, leverage, candidate generation, and portfolio construction.
11. Apply ownership modeling, GPT/AI game theory, correlation, duplication, and portfolio judgment on top of the projection layer.

## Coverage-Weighted Fallback Principle

Do not use rigid universal blend percentages. Weighting must respond to the quality of the available market evidence.

Conceptual defaults:

- High market confidence: Vegas dominates; Savant/vendor prior receives little or no weight unless it catches a verified market/data anomaly.
- Medium market confidence: Vegas remains primary, with meaningful shrinkage toward the fallback prior.
- Low market confidence: Savant/vendor prior may dominate because the market signal is too sparse to support a standalone projection.
- No usable market: use the fallback prior and label the projection as fallback-driven.

Confidence should consider at minimum:

- number of distinct relevant prop markets
- number of books
- presence of alternate/ladder markets
- market freshness
- liquidity when inferable
- agreement/disagreement across books
- whether overlapping markets reconcile coherently
- confirmed player role / starting status

## Preferred Sources

Action Network is a preferred market aggregator because it centralizes multi-book odds, props, consensus pricing, and market movement. It is not authoritative. Direct sportsbook lines and alternate sources may be used for triangulation or gap filling.

## Market Processing Rules

- Do not add overlapping prop expectations together without reconciliation.
- De-vig paired markets before converting odds to event probabilities when feasible.
- Prefer median/robust consensus across books to an outlier book.
- Use alternate/ladder markets to estimate tail probabilities and expected counts when helpful.
- Preserve timestamps and note stale/missing markets when material.
- Market coverage should be classified at minimum as High, Medium, Low, or None.
- High coverage should normally make the market projection dominant.
- Low/None coverage should shrink materially toward the fallback prior.
- Do not fabricate a prop or market line to complete a projection.

## Separation of Projection, Ownership, and Exposure

These are distinct outputs:

- DFS Engine Projection = our best estimate of expected fantasy scoring, Vegas-first when market coverage supports it.
- DFS Engine Expected Ownership = our best estimate of field roster rate.
- DFS Engine Exposure = how much the portfolio should roster the player after game theory, correlation, duplication, uncertainty, and script analysis.

Projection quality does not determine exposure by itself. A strong market projection can still deserve an underweight position when expected ownership or duplication is even more aggressive.

## Post-Slate Calibration

For each player, preserve and later compare:

- Savant/vendor fallback projection
- market-derived projection
- market coverage/confidence
- final DFS Engine projection
- source/vendor ownership
- DFS Engine expected ownership
- actual field ownership when available
- actual fantasy score
- DFS Engine exposure

Track whether market-confidence tiers actually predict projection reliability. If high-confidence Vegas projections do not outperform fallback priors over a meaningful sample, recalibrate the hierarchy rather than protecting the assumption.

## Sport Modules

Each `sports/<sport>.md` file should define the specific prop markets, stat inference logic, scoring conversion, and fallback implementation for that sport. Cross-sport hierarchy belongs here; sport-specific formulas should not be duplicated into core files.