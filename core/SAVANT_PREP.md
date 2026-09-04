# Savant Prep

## Trigger

When the user says **"Savant prep"**, run this workflow only. Do not build lineups, optimize portfolios, run full DFS Engine construction, or add extra slate strategy unless explicitly asked.

## Purpose

Take the user's Sim/Savant projection CSV and return the same import-ready file structure with two fields recalibrated:

1. **Projection** — make player fantasy-point projections as market-derived as possible from current Vegas / sportsbook information.
2. **Ownership** — replace or recalibrate Savant ownership toward the best estimate of actual field ownership using current industry consensus and slate context.

The user will then run the file through Savant's interface themselves.

## Projection Workflow

### Market first

For every player where usable current market data exists, derive the fantasy projection from sportsbook expectations rather than simply retaining Savant.

For MLB DraftKings:

- Pitchers: prioritize strikeout props, outs recorded / innings expectations, earned-runs or runs-allowed props where available, win probability / moneyline, opponent implied runs, and related pitcher markets. Convert the market expectation into DraftKings scoring expectations.
- Hitters: prioritize total bases, hits, home run, RBI, runs, stolen-base and other usable batter props, plus team implied run total and game environment. Convert those expectations into DraftKings scoring.
- Use multiple books / consensus prices when available; avoid anchoring to one outlier book.
- Remove vig / interpret probabilities and line prices where materially useful rather than treating posted odds as raw probabilities.
- Cross-check player props against team totals, game totals, moneylines, park/weather and lineup context so individual projections remain coherent with the game market.

### Fallback hierarchy

If a player lacks sufficient usable market data:

1. partial Vegas adjustment using team/game environment and available correlated markets;
2. broader reliable industry projection consensus when available;
3. original Savant projection as the final fallback.

Never force a fake Vegas projection when the market does not contain enough information.

## Ownership Workflow

Ownership is **not** derived from Vegas alone. Estimate expected field ownership using as many current touch points as practical, including:

- available industry ownership projections / consensus;
- Savant ownership as one input, not the authority;
- salary and positional opportunity cost;
- player projection / value and market strength;
- batting order or pitcher role;
- team implied run totals and obvious stack popularity;
- slate size and scarcity;
- likely chalk concentration and known DFS field behavior;
- late news / lineup changes where relevant.

The goal is the best estimate of **actual contest ownership**, not an optimizer target exposure and not a leverage recommendation.

## Output Contract

Return a Savant-importable CSV preserving the user's original player identifiers and required structure. At minimum keep the same identifying columns and replace the projection and ownership values in their expected fields.

Do not:

- build lineups;
- change salaries or player IDs;
- create Engine exposures;
- intentionally make ownership contrarian;
- modify projections just to create leverage;
- add unsupported players;
- remove viable players unless the source format / confirmed status explicitly requires it.

## Quality Control

Before returning the file:

- confirm the row count / player IDs still match the input;
- confirm projection and ownership columns are numeric and importable;
- sanity-check pitcher and hitter ranges against DraftKings scoring;
- check that ownership totals / distribution look plausible for the slate rather than mechanically copying Savant;
- identify major market-vs-Savant changes internally and verify they are supported by actual evidence;
- preserve Savant values when evidence is insufficient rather than inventing precision.

## Required Behavior

**"Savant prep" means exactly this process and nothing more unless the user explicitly expands the request.**
