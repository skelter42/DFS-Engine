# Market Inputs

## Purpose

This is the cross-sport market-input workflow for Sim Savant. Its only job is to take an attached Sim Savant projection CSV and return the same import structure with the best available **full-slate market-derived fantasy projections** and the best available estimate of **expected field ownership**.

The user specifies the sport. This process researches the relevant betting markets, player props, game lines, site scoring, slate context, ownership signals, and broader DFS industry projection consensus for that sport.

Sim Savant remains responsible for simulation, lineup generation, finish-rate ranking, exposure spreading, stack/correlation settings, and contest setup. Market Inputs does not build or optimize lineups.

## Trigger

Use:

**`Market Inputs — [SPORT]`**

Examples:
- `Market Inputs — MLB`
- `Market Inputs — NFL`
- `Market Inputs — NBA`
- `Market Inputs — NHL`
- `Market Inputs — NCAAF`
- `Market Inputs — Tennis`

## Projection-only invocation — mandatory

Use **`Market Inputs — [SPORT] — projections only`** when the user wants the projection pull without ownership research or any downstream lineup work.

Projection-only mode must:
1. Preserve the exact source row order, player names, DFS IDs, and import columns.
2. Research and replace only the projection fields. For Showdown, set CPT projection to exactly 1.5 times FLEX projection unless the source schema requires a different representation.
3. Leave source ownership unchanged. Do not research, rebuild, normalize, or reinterpret ownership.
4. Stop after the projection CSV and projection audit are complete. Do not simulate, optimize, rank, select, or allocate lineups.
5. Use the composite hierarchy in `core/MARKET_PROJECTIONS.md` (industry numeric + Vegas scrape, no narrative), active-role validation, sportsbook sweep, scoring conversion, confidence grading, and audit rules defined below.

### Efficient projection-pull execution

Projection quality is the primary input objective. Speed and token efficiency come from staged retrieval and reuse, not from skipping validation.

Use this order:

1. **Intake once.** Parse the entire source file in one pass. Build one canonical player table containing exact identity fields, sport, site, slate, game, team, opponent, position, salary when available, source projection, and eligibility status.
2. **Validate the active universe first.** Resolve confirmed inactive/out players, starters, likely rotation roles, and source projections before prop research. Exclude confirmed inactive players and retain an explicit exclusion reason.

   **Trust Savant zeros (mandatory efficiency rule).** If the attached Sim Savant `Proj` is `0` (or blank/missing treated as 0), **leave that player at 0**. Do not research props, industry projections, or ownership for zero-Proj players. Keep the row in the output file with `Proj = 0` so import structure is preserved. Industry numeric + Vegas prop work applies only to the **positive-Proj pool**. This shrinks a large main-slate file (often 1,000+ rows) down to the DFS-relevant universe (often a few hundred) without changing inactive/bench zeros.
3. **Cache slate-level markets.** Pull each game total, spread/moneyline, and implied team total once. Reuse those values for every player in that game.
4. **Run one broad prop sweep (preferred method).** Prefer **board-level / aggregator-first** retrieval over player-by-player searches. Hit multi-player prop boards and aggregators that surface many lines at once (PropCruncher, Covers matchup prop sections, Action Network boards, PropPrizm, FanDuel Research, OddsShopper-style pages, etc.). Batch by game and prop family. Record all usable lines, both-side prices, alternate lines, book, timestamp, and source URL in a structured market board. Only after the board sweep should individual deep-dives be used for material gaps.
5. **Deep-search only material gaps.** Make a second targeted pass only for likely active DFS-relevant players lacking the role-specific minimum prop bundle or showing a material disagreement between books, game markets, role, and the source projection.
6. **Normalize before calculating.** Match external names to the canonical player table internally, deduplicate identical markets, reject stale/wrong-game/wrong-player lines, and never change the source identity text.
7. **Convert once.** De-vig paired prices where feasible, form robust multi-book component expectations, infer distributions from alternate ladders when useful, reconcile overlapping markets, then apply the target site's scoring once.
8. **Shrink by evidence quality.** Let high-confidence market estimates dominate. Increase prior weight only as prop breadth, book count, freshness, role certainty, or cross-book agreement deteriorates. Do not use a fixed blend for every player.
9. **Reconcile the slate.** Compare player component totals with game and team markets. Investigate material contradictions instead of forcing a mechanical rescale.
10. **Audit in batches.** Review zero projections, largest source-to-Engine changes, low-confidence DFS-relevant players, identity preservation, projection coverage, and scoring totals together.
11. **Reuse fresh evidence.** Within the same slate and run, do not repeat unchanged searches. Refresh only markets affected by a material line, injury, role, weather, or availability change.
12. **Stop at adequacy.** Research is adequate when every likely active DFS-relevant player has either a coherent role-specific market bundle or a clearly labeled fallback, game/team reconciliation passes, and all material outliers are resolved. More searches after this point add cost without improving the input.

### Projection-pull data contract

Maintain an internal audit record per player with:
- exact source name and DFS ID
- eligibility status and evidence
- source/vendor projection
- market-derived component expectations
- market-derived fantasy projection
- final DFS Engine projection
- source-to-Engine difference
- books and distinct prop families used
- market timestamp/freshness
- confidence tier and fallback weight
- major source URLs
- unresolved uncertainty

Report active-pool coverage separately as Vegas-rich, Vegas-supported, industry-supported, and fallback-heavy. The **active pool for coverage grading is the positive-Savant-Proj universe**. Raw-pool coverage may be included, but Savant-zero, bench, and inactive players must not distort the active-pool grade.

## Core target — mandatory

The default target for every Market Inputs run is:

**`Proj = pure numeric composite (industry scrape + Vegas scrape)`** — see `core/MARKET_PROJECTIONS.md` (authoritative).

**`Own = industry-derived first`**

Savant is not the source of truth for either column. Savant is the final fallback only when external market or industry coverage is genuinely insufficient.

The intended division of labor is:

**Industry numeric projections + sportsbook odds are scraped and blended into one composite Proj. No narrative.**

**The DFS industry (ownership sources) tells us what the field is likely to play.**

**Savant uses those inputs to build the lineups.**

## Full-run requirement — mandatory

Every `Market Inputs — [SPORT]` request is a **full slate-wide research pass by default**. Do not substitute a quick targeted adjustment pass unless the user explicitly asks for one.

A valid full run must:
1. Read the entire attached Savant player pool.
2. Identify every game/event on the slate.
3. Identify the likely active/starting/rotation player pool before measuring market coverage. **Positive Savant Proj only.** Trust Savant zeros: keep them at 0 and do not include them in the research/coverage denominator.
4. Research game-level markets for every game/event.
5. Systematically sweep sportsbook/player-prop markets for every likely active player, not only stars or obvious DFS plays.
6. Use sportsbook aggregators and direct sportsbook sources across as many books as practical, including sources that surface DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Hard Rock, Circa, theScore and other available books.
7. Where direct Vegas/player-prop coverage is incomplete, research multiple reputable industry projection systems before falling back to Savant.
8. Convert the final statistical expectation into the correct site-specific fantasy scoring.
9. Build ownership from multiple current site/slate-specific industry ownership projections plus the behavioral ownership model below.
10. Use Savant only as the final documented fallback when both market and broader industry coverage are insufficient.
11. Audit the completed file and return it.
12. Stop.
