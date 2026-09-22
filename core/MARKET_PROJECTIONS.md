# Market-Derived DFS Projections

## Purpose

The DFS Engine produces a **composite projection** as the source of truth for expected fantasy scoring.

A composite projection is built from:
1. **Multi-book Vegas / sportsbook player props and game markets** (primary)
2. **Multiple independent industry projection leaders** (active cross-check and gap-fill)
3. **Sim Savant / vendor projection** only as the final fallback when both market and industry coverage are genuinely insufficient

The goal is to stop trusting any single projection source. The final `Proj` value that is returned to Sim Savant is the composite number, not the original Savant number and not a single sportsbook line.

The market-derived layer converts sportsbook probabilities into expected fantasy scoring components, then into site-specific fantasy points. Industry projections are used as independent numeric evidence, not merely narrative sanity checks. Savant is retained only when external coverage is thin.

## Canonical Projection Hierarchy (mandatory)

1. **Vegas / multi-book player props and game markets** — primary projection evidence.
2. **Broader industry projections** (multiple independent leaders) — active cross-check, consensus ingredient, and gap-fill when props are sparse.
3. **Sim Savant / trusted vendor projection** — final fallback prior only when both Vegas and multi-industry coverage are weak or absent.
4. **Verified role/news/context** — required validity layer that can override stale market assumptions when a player's role changes materially.

**Order matters.** The Engine must not begin from Savant and then lightly adjust with Vegas. It begins from the best available external evidence (Vegas first, then multi-industry) and only increases Savant weight as that external evidence deteriorates.

## What "composite" means in practice

- **High Vegas coverage (multi-book props + stable game markets):** Vegas dominates. Industry numbers are used for outlier detection and minor reconciliation. Savant weight is near zero.
- **Partial Vegas coverage:** Available props still lead. Missing components are filled from multi-industry consensus (median / trimmed mean / reliability-weighted), then reconciled to game/team markets.
- **Sparse or no usable props:** Build an industry consensus from multiple independent projection systems first. Only if that consensus is also thin do we fall back to the original Savant value.
- **Never** treat a single industry source or a single sportsbook as the composite. Prefer multi-book and multi-provider agreement.

## Cross-Sport Flow

1. Collect available player props, alternate/ladder props, team/game totals, moneylines, and related markets from preferred aggregators and books.
2. Remove vig from paired/two-sided markets when possible.
3. Aggregate across books using robust consensus statistics rather than a single book.
4. Infer expected player stat components and, when data supports it, component distributions.
5. Pull multiple independent industry projection systems for the same slate/site (THE BAT / THE BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros, LineStar, Stokastic/Awesemo public content, RotoWire, and other current reputable sources).
6. Convert expected stat components into the target site's fantasy scoring.
7. Form the composite: weight by evidence quality (Vegas-rich > Vegas-supported > multi-industry consensus > single-industry > Savant fallback).
8. Assign a market-coverage/confidence grade for each player.
9. Set the DFS Engine projection to the composite value.
10. Preserve the original Savant/vendor projection separately for comparison and post-slate calibration.
11. Use the resulting DFS Engine (composite) projection for simulation, leverage, candidate generation, and portfolio construction.
12. Apply ownership modeling, game theory, correlation, duplication, and portfolio judgment on top of the projection layer (or leave ownership as pass-through when running projection-only mode).

## Coverage-Weighted Fallback Principle

Do not use rigid universal blend percentages. Weighting must respond to the quality of the available evidence.

Conceptual defaults:

- **High market confidence:** Vegas dominates; industry is cross-check only; Savant receives little or no weight unless it catches a verified market/data anomaly.
- **Medium market confidence:** Vegas remains primary; industry consensus fills gaps and provides shrinkage; Savant weight stays low.
- **Low market confidence:** Multi-industry consensus becomes the main driver; Savant is a secondary anchor.
- **No usable market + thin industry:** Use the Savant fallback and label the projection as fallback-driven.

Confidence should consider at minimum:

- number of distinct relevant prop markets
- number of books
- presence of alternate/ladder markets
- market freshness
- liquidity when inferable
- agreement/disagreement across books
- number and agreement of independent industry projection sources
- whether overlapping markets and industry numbers reconcile coherently
- confirmed player role / starting status

## Preferred Sources

**Vegas / odds aggregators**
- Action Network (preferred multi-book aggregator)
- PropCruncher or comparable multi-book prop tools
- Direct DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Hard Rock, Circa, theScore and other books when publicly accessible

**Industry projection leaders (use multiple)**
- THE BAT / THE BAT X
- RotoGrinders
- Daily Fantasy Fuel
- FantasyPros daily projections
- LineStar
- Stokastic / Awesemo public projection content
- RotoWire DFS / projection tools
- Other current, site-specific, reputable systems

Action Network is preferred for market aggregation because it centralizes multi-book odds, props, consensus pricing, and movement. It is not the sole authority. Direct sportsbook lines and alternate sources are used for triangulation.

## Market Processing Rules

- Do not add overlapping prop expectations together without reconciliation.
- De-vig paired markets before converting odds to event probabilities when feasible.
- Prefer median/robust consensus across books to an outlier book.
- Use alternate/ladder markets to estimate tail probabilities and expected counts when helpful.
- Prefer multi-industry numeric consensus over any single industry source.
- Preserve timestamps and note stale/missing markets when material.
- Market coverage should be classified at minimum as High, Medium, Low, or None (or the tier labels Vegas-rich / Vegas-supported / Industry-supported / Fallback-heavy).
- High coverage should normally make the market projection dominant.
- Low/None coverage should move weight to multi-industry consensus, then to Savant only as last resort.
- Do not fabricate a prop or market line to complete a projection.

## Separation of Projection, Ownership, and Exposure

These are distinct outputs:

- **DFS Engine Projection (composite)** = our best multi-source estimate of expected fantasy scoring.
- **DFS Engine Expected Ownership** = our best estimate of field roster rate (or pass-through when running projection-only).
- **DFS Engine Exposure** = how much the portfolio should roster the player after game theory, correlation, duplication, uncertainty, and script analysis.

Projection quality does not determine exposure by itself. A strong composite projection can still deserve an underweight position when expected ownership or duplication is even more aggressive.

## Default workflow when a file is sent

When the user attaches a Sim Savant (or similar) projection file:

1. Treat the request as **projection-only** unless the user explicitly asks for an ownership pass.
2. Preserve exact player names, DFS IDs, row order, and the `Own` column.
3. Replace only the `Proj` column with the composite projection.
4. Return the updated file plus a short coverage/audit summary (Vegas-rich / Vegas-supported / Industry-supported / Fallback-heavy counts, largest changes, remaining uncertainty).
5. Stop. Do not build lineups or change ownership unless asked.

## Post-Slate Calibration

For each player, preserve and later compare:

- original Savant/vendor projection
- market-derived component
- industry consensus component
- final composite (DFS Engine) projection
- market coverage/confidence
- source/vendor ownership
- DFS Engine expected ownership (if computed)
- actual field ownership when available
- actual fantasy score
- DFS Engine exposure

Track whether higher-confidence composite projections actually outperform single-source priors over a meaningful sample. Recalibrate the hierarchy if they do not.

## Sport Modules

Each `sports/<sport>.md` file should define the specific prop markets, stat inference logic, scoring conversion, and fallback implementation for that sport. Cross-sport hierarchy belongs here; sport-specific formulas should not be duplicated into core files.
