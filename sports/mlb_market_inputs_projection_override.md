# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

Iteration addendum (now default): `sports/mlb_market_inputs_future_iteration.md`.

**User default (2026-09-22): no paid vendor file drops. Scrape public industry + public Vegas. Deliver the best available composite.**

**User default (2026-09-23): industry and Vegas work together on the same player. Grade coverage on starting pitchers + posted 1–9, not the raw positive-Proj file.**

## Standard

The output `Proj` is a **pure numeric composite**:

1. **Public industry layer** — scrape every reachable numeric projection/component page for this exact slate.
2. **Public Vegas layer** — board-first multi-book props + game markets; when hitter props are missing, implied team total + lineup slot is the Vegas layer. De-vig when possible.
3. **Joint blend** — both layers plus Savant prior on the same name. Default when both exist: SP `0.40 / 0.40 / 0.20`, posted hitter `0.40 / 0.32 / 0.28`.
4. **Sim Savant** — fallback only when both public layers are thin for a positive-Proj player, or for Own-0 relievers with no save/K/outs market.

No narrative in Proj. Own unchanged unless an ownership pass is requested.

Paid vendor CSVs are optional if the user later attaches them. They are not required to start or finish a pass.

## Trust Savant zeros — mandatory

If source `Proj` is `0`, leave `Proj = 0` unless the user says `unlock posted starters`.

## Coverage denominator — mandatory

Headline provenance is the **active pool**: starting pitchers (full or bulk) + confirmed/projected 1–9.

Target on that pool: joint or Vegas-supported, **0% Savant fallback**.

The full positive-Proj pool may still show a large fallback share because of relievers. Report it second. Never lead with it.

## Required behavior

1. Split zeros vs positive-Proj pool.
2. Identify the exact slate window. Reject wrong-slate public tables.
3. Lock posted 1–9 and starter/bulk/opener roles before blending.
4. Sweep public industry pages and public Vegas boards in parallel. Do not wait for file uploads. Do not run one layer and skip the other.
5. Convert components with site scoring. Never mix Yahoo/FD/DK raw points.
6. Role facts only: posted order, opener/bulk/full start, PH/bench.
7. Preserve Name, DFS ID, Own, row order. Replace only researched `Proj`.
8. Report actual public source count, not a fictional 10.
9. Grade honestly. Public-scrape A- is an acceptable delivery grade when hitter vendor grids are unavailable.
10. Stop. No lineups.

## Grade gate

- Target remains A / A+ when public coverage supports it.
- Missing paywalled CSVs is **not** a delivery blocker.
- Report `Projection grade` and the public sources used.
- Fail the process if posted starters were left on Savant after the sweep.

## Core philosophy

**Scrape public industry projections + scrape sportsbook odds → blend both into one composite.**
Industry is talent. Vegas is environment. Savant is the prior.
Trust Savant zeros. Do not stall for files the user will not attach.
