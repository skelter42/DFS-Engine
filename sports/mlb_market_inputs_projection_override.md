# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

Iteration addendum (now default): `sports/mlb_market_inputs_future_iteration.md`.

**User default (2026-09-22): no paid vendor file drops. Scrape public industry + public Vegas. Deliver the best available composite.**

**User default (2026-09-23): industry and Vegas work together on the same player. Grade coverage on starting pitchers + posted 1–9, not the raw positive-Proj file.**

**User default (2026-09-29): Proj is the industry median, pulled to the Vegas band if it sits outside. Canonical rule: `core/MARKET_PROJECTIONS.md`.**

## Standard

The output `Proj` is a **pure numeric composite**:

1. **Public industry layer** — scrape every reachable numeric projection/component page for this exact slate. Tier A votes if three or more exist.
2. **Public Vegas layer** — board-first multi-book props + game markets. De-vig and convert once. That number is the band, not a peer vote.
3. **Industry median + Vegas band** — keep the industry median inside the band; pull to the nearest edge if it sits outside. Band = Vegas number ± the larger of 1.5 site points or 12% of it. No converted prop: the industry median stands.
4. **Sim Savant** — does not vote when any usable industry vote exists. Fallback only when the public industry layer is thin for a positive-Proj player, or for Own-0 relievers with no save/K/outs market.

No narrative in Proj. Own unchanged unless an ownership pass is requested.

Paid vendor CSVs are optional if the user later attaches them. They are not required to start or finish a pass.

## No-prop hitters

A missing hitter prop does not create a player band. Implied team total × lineup slot is an environment check only, using this pre-declared share of team runs:

| Slot | Share |
|---|---|
| 1 | 0.13 |
| 2 | 0.12 |
| 3 | 0.12 |
| 4 | 0.11 |
| 5 | 0.11 |
| 6 | 0.11 |
| 7 | 0.10 |
| 8 | 0.10 |
| 9 | 0.10 |

Do not treat that product as site points. It flags a game-total break. It does not replace the industry median.

## Trust Savant zeros — mandatory

If source `Proj` is `0`, leave `Proj = 0` unless the user says `unlock posted starters`.

## Coverage denominator — mandatory

Headline provenance is the **active pool**: starting pitchers (full or bulk) + confirmed/projected 1–9.

Target on that pool: industry median or band-pulled, **0% Savant fallback**.

The full positive-Proj pool may still show a large fallback share because of relievers. Report it second. Never lead with it.

## Required behavior

1. Split zeros vs positive-Proj pool.
2. Identify the exact slate window. Reject wrong-slate public tables.
3. Lock posted 1–9 and starter/bulk/opener roles before blending.
4. Sweep public industry pages and public Vegas boards in parallel. Do not wait for file uploads. Do not run one layer and skip the other.
5. Convert components with site scoring. Never mix Yahoo/FD/DK raw points.
6. Role facts only: posted order, opener/bulk/full start, PH/bench.
7. Preserve Name, DFS ID, Own, row order. Replace only researched `Proj`.
8. Report actual public source count, not a fictional 10. Report how many names the band moved.
9. Grade honestly. Public-scrape A- is an acceptable delivery grade when hitter vendor grids are unavailable.
10. Stop. No lineups.

## Grade gate

- Target remains A / A+ when public coverage supports it.
- Missing paywalled CSVs is **not** a delivery blocker.
- Report `Projection grade` and the public sources used.
- Fail the process if posted starters were left on Savant after the sweep.

## Core philosophy

**Scrape public industry projections + scrape sportsbook odds → industry median, pulled to the Vegas band if it sits outside.**
Industry is the candidate. Vegas is the band. Savant is the fallback, not a vote.
Trust Savant zeros. Do not stall for files the user will not attach.
