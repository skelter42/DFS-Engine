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
7. Always research multiple independent numeric industry projection systems for the positive-Proj pool (target 10+). Industry is co-primary with Vegas, not a fallback. Blend industry numeric consensus with the Vegas layer. Use Savant only when both layers are thin.
8. Convert the final statistical expectation into the correct site-specific fantasy scoring.
9. Build ownership from multiple current site/slate-specific industry ownership projections plus the behavioral ownership model below.
10. Use Savant only as the final documented fallback when both market and broader industry coverage are insufficient.
11. Audit the completed file and return it.
12. Stop.

### No low-Vegas-coverage pass accepted without escalation

A Market Inputs run should not quietly finish with a low percentage of Vegas-supported projections for likely starters when public sportsbook markets are known to be broadly available.

Industry projections are collected for every positive-Proj player regardless of Vegas depth. Before assigning a likely active player to Savant fallback (thin industry AND thin Vegas), the process must escalate Vegas research through:
1. direct sportsbook pages when accessible
2. sportsbook comparison/aggregation pages
3. alternate prop categories for the same player
4. game/team markets
5. additional reputable sportsbook/odds aggregators

For MLB specifically, if a confirmed starting hitter or starting pitcher is still not Vegas-rich or Vegas-supported after the first pass, perform a second sportsbook sweep before accepting that classification.

Do not treat inability to extract one sportsbook page as evidence that Vegas coverage does not exist.

### Coverage target

For mature major-sport slates, the expected steady-state outcome is:
- **every positive-Proj player should receive both an industry numeric blend (target 10+ sources) and a Vegas prop/game-market layer, then a composite of the two**
- **most confirmed starters/rotation players should be Vegas-rich or Vegas-supported on the Vegas side of that composite**
- **most DFS-relevant players should have at least one external industry ownership source**
- Savant fallback should be concentrated mainly among bench, inactive, deep-fringe, or genuinely uncovered players after both layers were attempted

This is a process target, not a reason to invent data. If the target is not met, explicitly state why and identify which source categories failed before delivery.

### No partial-run masquerading

Do not call a file “Market Inputs complete” if only a small subset of players were researched or adjusted.

If broad market coverage is unavailable, say so explicitly and quantify coverage against the **likely active/starting pool**, not merely the full raw Savant pool:
- how many players were Vegas-rich
- how many were Vegas-supported
- how many were industry-supported
- how many remained fallback-heavy

Also report raw-pool counts separately if useful, but do not let bench/inactive/deep-fringe players make usable sportsbook coverage look artificially poor.

If the active-player run is fallback-heavy, label it as such rather than implying a fully market-derived slate.

## Projection principle

**Proj is a pure numeric conglomerate: scrape independent industry projections + scrape multi-book sportsbook odds, then blend. No narrative enters the number.** Full standard lives in `core/MARKET_PROJECTIONS.md` (target 10+ industry sources + Vegas layer → A+).

Use multiple sportsbooks and both sides of priced markets when available. A posted prop line without juice is not a complete expectation. De-vig and consensus prices where practical. Prefer broad market agreement to any one book.

Reconcile player props with game-level markets so individual projections do not collectively imply a materially different game environment from the betting market without a documented **data** reason.

Relevant markets depend on sport. Examples:
- MLB: pitcher K, outs, ER, hits/walks allowed, win; hitter hits, singles, total bases, HR, RBI, runs, walks, H+R+RBI, SB; game total, ML, run line, team totals.
- NFL/NCAAF: passing/rushing/receiving yards, receptions, TDs, attempts, completions, interceptions; spread, total, team totals.
- NBA: points, rebounds, assists, 3PM, steals/blocks where available, turnovers where relevant; spread, total, team totals, minutes/injury context.
- NHL: shots, goals, points, goalie saves/goals allowed/win; game total, ML, team totals, PP/line context.
- Tennis: match/set/game markets, moneyline, total games, aces/double faults/break markets where available.

Use lineup/role/minutes/workload/injury/weather/venue context only to allocate market expectation appropriately. Savant is the conservative final fallback; never invent precision.

## Projection source hierarchy — mandatory

Industry numeric projections and Vegas props are **co-primary**. Always collect both for every positive-Proj player. Do **not** treat industry as a fallback that is only used when Vegas is missing.

For every positive-Proj player:

1. **Industry layer (always).** Pull independent numeric projection sources. Target **10+** on a mature main slate. Blend with median / trimmed mean / reliability-weighted consensus. Convert component stats to the target site's scoring. Rankings and write-ups do not count.
2. **Vegas layer (always).** Board-level / aggregator-first sweep of player props + game/team markets. De-vig and multi-book consensus where available.
3. **Composite.** Blend the two layers by evidence quality:
   - Strong multi-book props → Vegas carries more weight; industry cross-checks and fills missing components.
   - Sparse props + deep industry → industry blend carries more weight; Vegas game totals still constrain the environment.
   - Both strong → blend; investigate material disagreements with more data, not narrative.
4. **Savant fallback only** when both industry breadth and Vegas coverage are genuinely thin after the sweeps.

Industry sources to pursue (expand whenever more become available):
- THE BAT / THE BAT X
- RotoGrinders projections
- Daily Fantasy Fuel
- FantasyPros daily projections
- LineStar
- Stokastic/Awesemo public projection content when accessible
- RotoWire projection/DFS tools when accessible
- NumberFire
- Sabersim or similar simulation-based public numbers
- other reputable, current, site-specific numeric projection systems

Rules:
- Prefer numeric projections over narrative analysis.
- Prefer current site/slate-specific data.
- Use multiple independent sources on every positive-Proj player, not only when props are sparse.
- Use median, trimmed mean, or reliability-weighted consensus rather than cherry-picking the highest/lowest projection.
- Convert component-stat projections into the target site's scoring when useful instead of blindly averaging fantasy-point outputs.
- Cross-check the industry consensus against game/team Vegas markets so industry projections cannot collectively contradict the betting environment without a data reason.
- Strong Vegas evidence can outweigh a conflicting industry number on the components the market is pricing; it does not mean skip the industry layer.

Provenance labels (evidence mix, not a research-order):
- **VEGAS_DIRECT / Vegas-rich** — composite built with multiple direct player props + industry support.
- **VEGAS_SUPPORTED** — some direct props + industry + game/team markets.
- **INDUSTRY_BLEND** — deep industry numeric consensus with thin direct props; game markets still used for reconciliation.
- **SAVANT_FALLBACK** — both layers thin; original Savant retained. Zero-Proj rows stay 0 and are not counted here.

## Sportsbook sweep standard — mandatory

**Preferred method: board-level / aggregator-first.** Do not default to player-by-player prop searches. First hit multi-player prop boards and aggregators that surface many lines at once (PropCruncher, Covers matchup prop sections, Action Network boards, PropPrizm, FanDuel Research, comparable multi-book pages). Extract mass data, then deep-dive only material gaps. This is the default efficiency path and must be used on every full run unless a board is inaccessible.

Do not assume missing sportsbook data after checking only one source or one prop category.

For each likely active player, systematically search the available sportsbook/aggregator ecosystem as the Vegas layer of the composite (industry is collected in parallel, not after Vegas fails). Relevant sources may include:
- PropCruncher or comparable multi-book prop aggregators (preferred first stop for mass data)
- Action Network player/game prop pages and boards
- Covers matchup prop sections
- PropPrizm and similar slate boards
- RotoWire betting/player-prop comparison tools
- direct DraftKings Sportsbook markets when publicly accessible
- direct FanDuel Sportsbook markets when publicly accessible
- BetMGM, Caesars, BetRivers, Hard Rock, Circa, theScore and other books surfaced through reputable comparison tools
- additional reputable odds/prop aggregators when useful

Do not require every book to be directly accessible. Aggregators that expose current lines and prices across multiple books are valid market touch points.

### MLB-specific sportsbook sweep

For every projected/confirmed starting pitcher, search for as many of the following as available:
- strikeouts
- outs recorded
- earned runs allowed
- hits allowed
- walks allowed
- pitcher win
- any other workload/run-prevention markets useful for DK/FD scoring

For every confirmed/likely starting hitter, search for as many of the following as available:
- hits
- singles
- total bases
- home runs
- RBI
- runs
- H+R+RBI or similar combo markets
- walks
- stolen bases

A hitter with several of these markets should normally be Vegas-rich or Vegas-supported, not industry-only. A starting pitcher with multiple K/outs/ER/hits/walks markets should normally be Vegas-rich.

Use the available prices on both sides and consensus across books where practical. Do not reduce a market to the posted line alone when juice materially changes the expectation.

### MLB second-pass rule

Before any confirmed starting pitcher is classified Industry-supported or fallback-heavy, verify at least:
- one strikeout source
- one workload source such as outs recorded
- one run-prevention/baserunner source such as ER, hits allowed, or walks allowed
- game moneyline and total/team-total context

Before any confirmed starting hitter is classified Industry-supported or fallback-heavy, verify that multiple hitter prop families were checked across aggregators/books, including at minimum:
- hits or total bases
- HR
- RBI or runs
- at least one additional category such as walks, H+R+RBI, singles, or SB

If those categories are broadly posted for the slate, failure to find one source does not justify fallback. Search alternate books/aggregators.

## Projection research standard

For each slate, collect as many of these as legitimately available:
- multiple sportsbook prices for the same prop
- both over and under prices when possible
- game totals, spreads/moneylines and team totals
- correlated player markets where useful
- recent line movement when material
- confirmed starting/lineup/role information
- site-specific DFS scoring rules
- multiple independent numeric industry projection systems for every positive-Proj player (target 10+; industry is co-primary, not sparse-prop fallback)

Where many books disagree, prefer a consensus expectation rather than cherry-picking the most favorable line.

Always build the industry consensus (target 10+) **and** the Vegas layer, then blend. If direct props are missing, the industry blend still leads and is reconciled to game-level markets. Do **not** jump to Savant while either layer still has unused sources. Savant is the last fallback only when both layers are thin.

## Projection confidence

Assign an internal projection confidence tier:
- **A — Vegas-rich composite:** multiple direct props across multiple books + industry numeric blend + stable game/team markets.
- **B — Vegas-supported composite:** some direct props + industry numeric blend + game context.
- **C — Industry-led composite:** direct props are sparse, but multiple reputable numeric projection systems (aim 10+) plus game/team Vegas provide a coherent consensus.
- **D — Fallback-heavy:** insufficient market **and** industry coverage after both sweeps; retain Savant conservatively.

A player does not need many direct props to avoid Tier D if multiple credible industry systems and the game market provide strong independent support. Conversely, one industry projection alone does not create high confidence.

Every full run must report confidence-tier coverage for the likely active/starting pool and may additionally report the full raw-pool counts.

## Ownership principle — industry first

Ownership should be **industry-derived first**, not Savant-derived first.

For DFS-relevant players, the process should actively search for multiple site/slate-specific ownership projections before retaining Savant ownership unchanged. Savant is one ownership source, not the baseline authority.

The preferred hierarchy is:
1. multiple current numeric industry ownership projections for the exact site/slate
2. one current numeric ownership source plus corroborating salary/value/optimizer/stack behavior
3. behavioral field model plus Savant as a conservative anchor
4. Savant-only fallback when no credible external ownership signal exists

For mature main slates, a low percentage of external ownership coverage should trigger an additional industry-search pass before delivery.

## Ownership is a field-behavior forecast

Ownership is harder than projection because it is not simply about what will happen. It is a forecast of what DFS entrants will choose after seeing salaries, projections, news, optimizer outputs, industry content, and slate structure.

The goal is:

**`Own = best estimate of actual site/slate field roster percentage`**

It must be objective. Never change ownership to create leverage, force Savant toward a player, or manufacture a desired portfolio.
