# Savant Prep

## Trigger

When the user says **"Savant prep"** (or attaches a projection CSV under Market Inputs / projections only), run this workflow only. Do not build lineups, optimize portfolios, run full DFS Engine construction, or add extra slate strategy unless explicitly asked.

## Purpose

Take the user's Sim/Savant projection CSV and return the same import-ready file structure with **`Proj` recalibrated to an objective consensus** and, when requested, **`Own` recalibrated toward actual field ownership**.

**Projection goal (mandatory):**  
Get the best available **objective consensus projection** by scraping as many independent **numeric** industry projection sources as possible and scraping multi-book sportsbook odds/props, then blending them. We are **not** trying to beat the market or invent edge. We are minimizing reliance on any single projection source (including Savant).

Authoritative projection standard: `core/MARKET_PROJECTIONS.md`.

The user runs the returned file through Savant themselves for sims and lineups.

## Projection Workflow — pure numeric conglomerate

### What goes into Proj

1. **Industry layer** — scrape/pull independent **numeric** DFS/projection systems (target **10+** when the slate supports it). Only numbers count; rankings and write-ups do not enter the blend.
2. **Vegas layer** — scrape/pull multi-book player props and game markets; de-vig when possible; use as statistical expectation and as reconciliation so the blend does not contradict the betting environment.
3. **Blend** — median / trimmed mean / coverage-weighted composite. Weight by evidence quality (how many sources, how much multi-book agreement), not by opinion.
4. **Savant** — final fallback only when both layers are genuinely thin. Label as such.

**No narrative enters Proj.** No matchup story, no "due," no leverage manufacturing.

### Fallback hierarchy

1. Full composite (deep industry + multi-book Vegas)
2. Industry-led composite with game-market reconciliation (thin props)
3. Vegas-led with industry cross-check (deep props, thin industry)
4. Original Savant only when both external layers fail

Never force a fake Vegas or industry number when the data does not exist.

### MLB DraftKings component checklist (when converting props)

- Pitchers: K props, outs/IP, ER, hits/walks allowed, win/ML context — convert to DK scoring.
- Hitters: hits, TB, HR, RBI, runs, walks, SB, combos + team implied runs — convert to DK scoring.
- Multi-book + juice when available; reconcile to game totals.

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

**Default for projection-only passes:** leave `Own` unchanged.

## Output Contract

Return a Savant-importable CSV preserving the user's original player identifiers and required structure. At minimum keep the same identifying columns and replace the projection (and ownership only if requested) values in their expected fields.

Do not:

- build lineups;
- change salaries or player IDs;
- create Engine exposures;
- intentionally make ownership contrarian;
- modify projections just to create leverage;
- add unsupported players;
- remove viable players unless the source format / confirmed status explicitly requires it;
- inject narrative into any projection number.

## Quality Control

Before returning the file:

- confirm the row count / player IDs still match the input;
- confirm projection and ownership columns are numeric and importable;
- report projection grade (target A / A+), industry source breadth, Vegas coverage, provenance mix;
- sanity-check pitcher and hitter ranges against site scoring;
- identify major composite-vs-Savant changes and verify they are supported by scraped numbers;
- preserve Savant values when evidence is insufficient rather than inventing precision.

## Required Behavior

**"Savant prep" / Market Inputs projection passes mean exactly this process and nothing more unless the user explicitly expands the request.**

Full projection standard: `core/MARKET_PROJECTIONS.md`.  
Cross-sport workflow: `core/MARKET_INPUTS.md`.  
MLB projection-only override: `sports/mlb_market_inputs_projection_override.md`.
