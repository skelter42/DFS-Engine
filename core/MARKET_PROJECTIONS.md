# Market-Derived DFS Projections

## Purpose

The DFS Engine produces a **composite projection** as the single source of truth for expected fantasy scoring.

A composite projection is a **pure numeric conglomerate**. It is built only from:

1. **Industry layer** — scraped/pulled independent **numeric** projection sources (target: **10+** when publicly available for the sport/slate). The industry median is the candidate.
2. **Vegas layer** — scraped/pulled multi-book player props and game markets (de-vigged when possible), used as a band around that median, not as a peer vote.

**No narrative enters the number.** No "I like this matchup," no "he's due," no leverage manufacturing, no story-driven adjustment. Only numbers that were scraped or pulled, converted to the target site's scoring, and passed through the lock below.

Sim Savant / any single vendor is **not** the source of truth. It is the final fallback only when the industry layer is genuinely thin.

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
- Industry: as many independent **numeric** projection sources as are realistically accessible for that sport/slate were pulled (explicit target **10+** when the public ecosystem supports it; never stop at 1–2 sources). At least three Tier A votes on a mature main slate.
- Vegas: multi-book props and game markets were swept; juice/de-vig used where available; player-level expectations reconciled to team/game totals.
- The industry median was checked against the Vegas band; names pulled to the edge are counted, not narrated.
- Coverage and provenance are reported honestly (Vegas-rich / Vegas-supported / Industry-blend / Fallback-heavy) **on the positive-Proj pool**.
- No single source was treated as authoritative.
- **No narrative, opinion, or qualitative judgment altered any projection value.**

Anything below A requires more research (more numeric sources / more prop lines) or an explicit user acceptance of the lower grade.

## Canonical hierarchy (mandatory)

1. **Industry multi-source numeric median** (target 10+, Tier A if three or more exist) — the candidate.
2. **Vegas multi-book band** — pulls the candidate to the nearest edge when it sits outside. Not a peer vote.
3. **Role / lineup / news / availability facts** — validity layer only, locked before the number. These can zero or reallocate a player; they do not invent fantasy points from a story.
4. **Sim Savant (or other single vendor)** — final fallback only when no usable industry vote exists for a positive-Proj player. Zero-Proj rows stay 0 by rule, not after research.

**Order of work, not a weight:**
- Lock role first. Then research industry breadth and Vegas in parallel on the positive-Proj pool only.
- Coverage changes how many industry votes exist and whether a band exists. It does not change the estimator.
- No usable industry vote → Savant fallback, labeled. Savant does not vote when any usable industry vote exists.

Never begin from Savant and lightly adjust. Begin from the external composite — except for Savant zeros, which stay zero.

## Industry layer — breadth target

**Goal: A+ numeric read on what the industry is projecting.**

- Target **at least 10 independent numeric projection sources** when the sport/slate publicly supports it.
- Minimum acceptable for a non-fallback player on a mature slate: several independent numeric systems (do not stop after one or two).
- **Only numeric projections count.** Rankings, articles, podcasts, and qualitative write-ups do not enter the blend unless they publish actual projected points or component stats.
- Blend method: the industry-median + Vegas-band lock below. Do not cherry-pick the highest or lowest, and do not substitute a trimmed mean or a fixed weight.
- Convert component stats to the target site scoring before the median. Never average raw points from different scoring systems.

### Tiers — pre-declared, not a mid-run judgment

**Tier A** — a model or a real consensus that publishes components or site points:
- THE BAT / THE BAT X (separate families if both publish independent numbers)
- RotoGrinders projections
- Daily Fantasy Fuel
- FantasyPros consensus (the consensus, not each expert)
- NumberFire
- Stokastic / Awesemo public projections
- Sabersim
- FantasyLabs
- RotoWire, when it publishes components or site points
- LineStar, when it publishes site points

**Tier B** — any other single public numeric page.

If three or more Tier A votes exist, Tier B does not vote. Tier B fills a gap only when Tier A is thinner than three.

### Industry sources to pursue (expand this list whenever more become available)

Core / high-priority: the Tier A list above.

Additional / sport-specific:
- Any other current, independent, **numeric** DFS or advanced-stats projection system for that sport
- Public expert consensus boards that publish actual projected points (not just rankings)

**Rule:** If fewer than ~5–6 solid numeric sources are found on a major-sport main slate, keep searching before calling the industry layer complete. Document which sources were used and which could not be reached.

## Vegas layer — band, not a peer vote

Vegas is not optional window dressing. It is the band around the industry median, built from scraped odds.

**Preferred method: board-level / aggregator-first.** Hit multi-player prop boards (PropCruncher, Covers matchup prop sections, Action Network boards, PropPrizm, FanDuel Research, comparable multi-book pages) before player-by-player searches. Deep-dive only material gaps in the positive-Proj pool.

**Primary use**
- Multi-book player props (with juice / both sides when available), de-vigged and converted once
- Alternate / ladder markets when useful for the converted expectation
- Game totals, spreads/moneylines, implied team totals as the slate check

**Sanity-check / reconciliation use**
- Player medians must not collectively imply a game environment that materially contradicts the betting market without a documented **data** reason (role change, confirmed lineup, stale line).
- A break drops the stale vote and recomputes. It does not reweight.

### Preferred Vegas sources
- PropCruncher or comparable multi-book prop tools (preferred first stop for mass data)
- Action Network (multi-book aggregator)
- Covers matchup prop sections
- PropPrizm / FanDuel Research / OddsShopper-style boards
- Direct DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Hard Rock, Circa, theScore and other books when publicly accessible
- Additional reputable odds/prop aggregators

De-vig paired markets. Prefer robust multi-book consensus over any single book. Never invent a line. Ten books are one Vegas number.

## Industry median + Vegas band — mandatory

`Proj` is the industry median, pulled to the Vegas band if it sits outside. It is not a weighted mean. It is not an equal-vote median of industry and Vegas. Savant does not get a vote when any usable industry vote exists.

For each **positive-Proj** player:

1. Lock role first. Confirmed inactive stays 0. Do not blend a name until starter / bulk / order / inactive status is set.
2. Convert every industry number and every Vegas component to the target site scoring first. Do not average FanDuel points with DraftKings points.
3. Collapse source families to one vote. A consensus board and a page reprinting that consensus are one family.
4. Reject unusable votes: a page still allocating to a confirmed inactive, the wrong slate, or the wrong site with no conversion. Component-only cites feed the conversion. They are not a separate vote unless they convert to a full site projection.
5. Industry candidate:
   - Three or more Tier A votes: median of Tier A. Tier B does not vote.
   - Fewer than three Tier A: median of every usable vote.
   - One usable vote: that vote.
   - None: Savant fallback, labeled. Savant zeros stay 0 and are not researched.
   - Odd count: the central vote. Even count: the mean of the two central votes.
6. Build one Vegas number: the de-vigged multi-book prop expectation, converted once. No converted player prop: there is no band. The industry median stands. Game total remains a slate check. Do not manufacture a player band from an unwritten slot share. A sport file may publish a pre-declared share and a site conversion; until it does, environment-only is not a band.
7. Band = Vegas number ± the larger of 1.5 site points or 12% of the Vegas number. Width is fixed. Inside the band, keep the industry median. Outside, pull to the nearest edge.
8. Reconcile the game. If the resulting numbers imply a total the board rejects, drop the stale vote and recompute. Do not replace the lock with a fixed-weight average, and do not write a story into the number.
9. Round to 2 decimals. Showdown CPT = 1.5 × the frozen FLEX number.
10. Record provenance on the positive-Proj pool, the usable Tier A / Tier B counts, and how many names the band moved.

**Nothing in steps 1–10 is narrative.** If a number cannot be traced to a scraped industry projection or a scraped sportsbook market (or a documented conversion of those), it does not belong in `Proj`.

Do not refit the band width because one slate beat or missed the locked number. That is calibration archive.

## Cross-sport flow (efficient)

1. Intake the attached file once (names, DFS IDs, source Proj, Own, slate context).
2. Validate active universe. **Trust Savant zeros:** leave `Proj = 0` rows at 0; do not research them. Research only the positive-Proj pool.
3. Lock roles before numbers.
4. Cache game-level Vegas markets for every game.
5. Broad **board-level** prop sweep across aggregators/books for the positive-Proj pool.
6. Parallel (or staged) pull of industry projection sources for the positive-Proj pool — keep going until the breadth target is met or sources are exhausted.
7. Normalize names; reject stale/wrong-game lines. Convert to site scoring. Collapse families. Set Proj with the industry-median + Vegas-band lock.
8. Reconcile player totals to team/game markets; a break drops a stale vote and recomputes.
9. Audit: coverage counts on the **positive-Proj pool**, names the band moved, largest source-to-composite moves, low-breadth players. Zeros stay zeros.
10. Return file (Proj updated only for the researched pool, unless ownership pass requested) + grade + coverage summary.
11. Stop.

## What coverage changes — and what it does not

Coverage changes the industry vote count and whether a band exists. It does not change the estimator.

- Three or more Tier A votes + a converted prop: median of Tier A, pulled to the band edge only if it sits outside.
- Thin Tier A + a converted prop: median of the usable votes, same band.
- Industry only: the industry median. No manufactured band.
- No industry vote: Savant fallback, labeled.

Confidence inputs stay descriptive: prop count, book count, freshness, Tier A count after collapse, role certainty, and whether the band moved the number. They are not blend weights.

## Default workflow when a file is sent

1. Projection-only unless user asks for ownership.
2. Preserve Name, DFS ID, Own, row order exactly.
3. Replace only `Proj` with the composite **for positive-Proj players**. Leave Savant zeros at 0.
4. Return updated file + audit:
   - Projection grade (target A / A+)
   - Tier A / Tier B counts used
   - Vegas coverage summary
   - Count of names the band moved
   - Provenance mix on the **positive-Proj pool**
   - Largest composite vs original Savant deltas
5. Do not build lineups or change ownership unless asked.
6. Do not inject narrative into any projection.

## Separation of outputs

- **Composite Proj** = industry median, pulled to the Vegas band when it sits outside.
- **Own** = field ownership estimate (or pass-through in projection-only mode).
- **Exposure** = portfolio decision after game theory — not the same as Proj.

## Post-slate calibration

Preserve for learning, per researched player:
- original Savant Proj
- industry median
- Vegas number and band edges
- final Proj
- Tier A count
- whether the band moved the number
- actual fantasy score when available

If the band-pulled median does not beat both layers alone on absolute error over a meaningful sample, revisit the estimator — do not protect the assumption, and do not refit off one slate.

## Sport modules

Each `sports/<sport>.md` defines prop families, scoring conversion, and sport-specific industry sources. This file owns the cross-sport composite standard, the industry-median + Vegas-band lock, the Savant-zero efficiency rule, and the A+ / 10+ industry breadth target.
