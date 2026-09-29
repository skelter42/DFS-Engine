# Market-Derived DFS Projections

## Purpose

The DFS Engine produces a **composite projection** as the single source of truth for expected fantasy scoring.

A composite projection is a **pure numeric conglomerate**. It is built only from:

1. **Industry layer** — scraped/pulled independent **numeric** projection sources (target: **10+** when publicly available for the sport/slate).
2. **Vegas layer** — scraped/pulled multi-book player props and game markets (de-vigged when possible), used as one site-converted vote and as a reconciliation constraint on the median.

**No narrative enters the number.** No "I like this matchup," no "he's due," no leverage manufacturing, no story-driven adjustment. Only numbers that were scraped or pulled, converted to the target site's scoring, and blended.

Sim Savant / any single vendor is **not** the source of truth. It is the final fallback only when both the industry blend and Vegas coverage are genuinely thin.

The final `Proj` returned to Sim Savant is always the composite number.

## Trust Savant zeros — mandatory efficiency rule

If the attached Sim Savant `Proj` is `0` (or blank/missing treated as 0):

- **Leave that player at 0.**
- Do **not** research industry projections, Vegas props, or ownership for that row.
- Keep the row in the output file so import structure and DFS IDs are preserved.

Industry numeric + Vegas prop work applies only to the **positive-Proj pool**. Coverage grades, the 10+ industry target, and provenance mix are measured against that positive pool, not the raw 1,000-row file. Zero-Proj rows are not counted as `SAVANT_FALLBACK` in the active-pool grade.

This shrinks a large main-slate file down to the DFS-relevant universe without changing inactive/bench zeros.

## Quality bar — A+ required

Every projection-only (or full Market Inputs) pass must aim for an **A or A+** on the composite.

An A+ pass means:
- Industry: as many independent **numeric** projection sources as are realistically accessible for that sport/slate were pulled and blended (explicit target **10+** when the public ecosystem supports it; never stop at 1–2 sources).
- Vegas: multi-book props and game markets were swept; juice/de-vig used where available; player-level expectations reconciled to team/game totals.
- The two layers were cross-checked numerically; material disagreements were investigated with more sources or fresher lines, not with narrative.
- Coverage and provenance are reported honestly (Vegas-rich / Vegas-supported / Industry-blend / Fallback-heavy) **on the positive-Proj pool**.
- No single source was treated as authoritative.
- **No narrative, opinion, or qualitative judgment altered any projection value.**

Anything below A requires more research (more numeric sources / more prop lines) or an explicit user acceptance of the lower grade.

## Canonical hierarchy (mandatory)

1. **Industry multi-source numeric blend** (target 10+) + **Vegas multi-book layer** — co-primary evidence. Build both; form the composite from them.
2. **Role / lineup / news / availability facts** — validity layer only (who is in / out / starting). These can zero or reallocate a player; they do not invent fantasy points from a story.
3. **Sim Savant (or other single vendor)** — final fallback only when both industry breadth and Vegas coverage fail **for a positive-Proj player**. Zero-Proj rows stay 0 by rule, not after research.

**Order of work, not a weight:**
- Always research industry breadth and Vegas in parallel (or staged for efficiency) **on the positive-Proj pool only**.
- Coverage changes how many votes exist. It does not change the estimator. The median lock below is the only blend.
- Thin on both → Savant fallback, labeled as such. Savant does not vote when any usable external vote exists.

Never begin from Savant and lightly adjust. Begin from the external composite — except for Savant zeros, which stay zero.

## Industry layer — breadth target

**Goal: A+ numeric read on what the industry is projecting.**

- Target **at least 10 independent numeric projection sources** when the sport/slate publicly supports it.
- Minimum acceptable for a non-fallback player on a mature slate: several independent numeric systems (do not stop after one or two).
- **Only numeric projections count.** Rankings, articles, podcasts, and qualitative write-ups do not enter the blend unless they publish actual projected points or component stats.
- Blend method: the median lock below. Do not cherry-pick the highest or lowest, and do not substitute a trimmed mean or a fixed weight.
- Convert component stats to the target site scoring before the median. Never average raw points from different scoring systems.

### Industry sources to pursue (expand this list whenever more become available)

Core / high-priority:
- THE BAT / THE BAT X
- RotoGrinders projections
- Daily Fantasy Fuel
- FantasyPros daily / consensus projections
- LineStar
- Stokastic / Awesemo public projection content
- RotoWire DFS / projection tools
- NumberFire (when accessible)
- Sabersim or similar simulation-based public numbers (when accessible)
- FantasyLabs / other reputable optimizer-linked projections when public numbers exist

Additional / sport-specific:
- Any other current, independent, **numeric** DFS or advanced-stats projection system for that sport
- Public expert consensus boards that publish actual projected points (not just rankings)

**Rule:** If fewer than ~5–6 solid numeric sources are found on a major-sport main slate, keep searching before calling the industry layer complete. Document which sources were used and which could not be reached.

## Vegas layer — primary + sanity check

Vegas is not optional window dressing. It is a full evidence layer built from scraped odds.

**Preferred method: board-level / aggregator-first.** Hit multi-player prop boards (PropCruncher, Covers matchup prop sections, Action Network boards, PropPrizm, FanDuel Research, comparable multi-book pages) before player-by-player searches. Deep-dive only material gaps in the positive-Proj pool.

**Primary use**
- Multi-book player props (with juice / both sides when available)
- Alternate / ladder markets when useful for expectation and distribution
- Game totals, spreads/moneylines, implied team totals

**Sanity-check / reconciliation use**
- Industry blend must not collectively imply a game environment that materially contradicts the betting market without a documented **data** reason (e.g. role change, confirmed lineup, stale line).
- Player component totals are checked against team implied totals and game totals.
- Large industry-vs-Vegas disagreements trigger more source pulls or fresher line checks — not narrative interpretation.

### Preferred Vegas sources
- PropCruncher or comparable multi-book prop tools (preferred first stop for mass data)
- Action Network (multi-book aggregator)
- Covers matchup prop sections
- PropPrizm / FanDuel Research / OddsShopper-style boards
- Direct DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Hard Rock, Circa, theScore and other books when publicly accessible
- Additional reputable odds/prop aggregators

De-vig paired markets. Prefer robust multi-book consensus over any single book. Never invent a line.

## Median lock — mandatory

`Proj` is the median of independent, site-converted numeric votes. It is not a weighted mean, not a trimmed mean, and not a coverage-weighted average. Savant does not get a vote when any usable external vote exists.

For each **positive-Proj** player:

1. Convert every industry number and every Vegas component to the target site scoring first. Do not average FanDuel points with DraftKings points.
2. Collapse source families to one vote. A consensus board and a page reprinting that consensus are one family. Ten books are not ten Vegas votes.
3. Reject unusable votes: a page still allocating to a confirmed inactive, the wrong slate, or the wrong site with no conversion. Component-only cites feed the conversion. They are not a separate vote unless they convert to a full site projection.
4. Build at most one Vegas vote: the de-vigged multi-book expectation, converted once. If no player prop exists, the environment-derived expectation (team total × role share, or the posted ladder) is that single Vegas vote. Game total, spread, and team total are reconciliation constraints, not extra votes.
5. `Proj` = median of the remaining votes.
   - Odd count: the central vote.
   - Even count: the mean of the two central votes.
   - One usable external vote: that vote.
   - Zero usable external votes: Savant fallback, labeled. Savant zeros stay 0 and are not researched.
6. Reconcile to the board. If the medians in a game imply an environment the posted total rejects by a material amount, drop or haircut the offending vote and recompute the median. Do not replace the median with a fixed-weight average, and do not write a story into the number.
7. Round to 2 decimals. Showdown CPT = 1.5 × the frozen FLEX median.
8. Record provenance on the positive-Proj pool: Vegas-rich / Vegas-supported / Industry-blend / Savant-fallback, plus the usable vote count after family collapse.

**Nothing in steps 1–8 is narrative.** If a number cannot be traced to a scraped industry projection or a scraped sportsbook market (or a documented conversion of those), it does not belong in `Proj`.

Do not refit this rule because one slate beat or missed the locked median. That is calibration archive.

## Cross-sport flow (efficient)

1. Intake the attached file once (names, DFS IDs, source Proj, Own, slate context).
2. Validate active universe. **Trust Savant zeros:** leave `Proj = 0` rows at 0; do not research them. Research only the positive-Proj pool.
3. Cache game-level Vegas markets for every game.
4. Broad **board-level** prop sweep across aggregators/books for the positive-Proj pool.
5. Parallel (or staged) pull of industry projection sources for the positive-Proj pool — keep going until the breadth target is met or sources are exhausted.
6. Normalize names; reject stale/wrong-game lines.
7. Convert to site scoring, collapse source families, and set Proj to the median lock.
8. Reconcile player totals to team/game markets; investigate material breaks with more data.
9. Audit: coverage counts on the **positive-Proj pool**, largest source-to-composite moves, low-breadth players. Zeros stay zeros.
10. Return file (Proj updated only for the researched pool, unless ownership pass requested) + grade + coverage summary.
11. Stop.

## What coverage changes — and what it does not

Coverage changes the vote count and the label. It does not change the estimator.

- Deep industry + a player prop: many industry votes, one Vegas vote, median of those votes, game total as the check.
- Thin industry + a sharp prop board: the Vegas vote carries more of the median because there are fewer votes, not because a weight was assigned.
- Industry only: median of the industry votes, reconciled to the game total.
- Neither layer: Savant fallback, labeled.

Confidence inputs stay descriptive: prop count, book count, freshness, family count after collapse, role certainty, and whether reconciliation moved a vote. They are not blend weights.

## Default workflow when a file is sent

1. Projection-only unless user asks for ownership.
2. Preserve Name, DFS ID, Own, row order exactly.
3. Replace only `Proj` with the composite **for positive-Proj players**. Leave Savant zeros at 0.
4. Return updated file + audit:
   - Projection grade (target A / A+)
   - Industry source count used (and list when useful)
   - Vegas coverage summary
   - Provenance mix on the **positive-Proj pool** (Vegas-rich / Vegas-supported / Industry-blend / Fallback-heavy)
   - Largest composite vs original Savant deltas
5. Do not build lineups or change ownership unless asked.
6. Do not inject narrative into any projection.

## Separation of outputs

- **Composite Proj** = multi-source expected fantasy points (industry numeric scrape + Vegas odds scrape).
- **Own** = field ownership estimate (or pass-through in projection-only mode).
- **Exposure** = portfolio decision after game theory — not the same as Proj.

## Post-slate calibration

Preserve for learning:
- original Savant Proj
- industry consensus component
- Vegas-derived component
- final composite
- industry source count / list
- Vegas coverage tier
- actual fantasy score and actual ownership when available

If locked medians do not beat both layers alone on absolute error over a meaningful sample, revisit the estimator — do not protect the assumption, and do not refit off one slate.

## Sport modules

Each `sports/<sport>.md` defines prop families, scoring conversion, and sport-specific industry sources. This file owns the cross-sport composite standard, the pure numeric conglomerate rule, the Savant-zero efficiency rule, the A+ / 10+ industry breadth target.
