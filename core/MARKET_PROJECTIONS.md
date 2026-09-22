# Market-Derived DFS Projections

## Purpose

The DFS Engine produces a **composite projection** as the single source of truth for expected fantasy scoring.

A composite projection is a **pure numeric conglomerate**. It is built only from:

1. **Industry layer** — scraped/pulled independent **numeric** projection sources (target: **10+** when publicly available for the sport/slate).
2. **Vegas layer** — scraped/pulled multi-book player props and game markets (de-vigged when possible), used as statistical expectation and as a reconciliation constraint on the industry blend.

**No narrative enters the number.** No "I like this matchup," no "he's due," no leverage manufacturing, no story-driven adjustment. Only numbers that were scraped or pulled, converted to the target site's scoring, and blended.

Sim Savant / any single vendor is **not** the source of truth. It is the final fallback only when both the industry blend and Vegas coverage are genuinely thin.

The final `Proj` returned to Sim Savant is always the composite number.

## Quality bar — A+ required

Every projection-only (or full Market Inputs) pass must aim for an **A or A+** on the composite.

An A+ pass means:
- Industry: as many independent **numeric** projection sources as are realistically accessible for that sport/slate were pulled and blended (explicit target **10+** when the public ecosystem supports it; never stop at 1–2 sources).
- Vegas: multi-book props and game markets were swept; juice/de-vig used where available; player-level expectations reconciled to team/game totals.
- The two layers were cross-checked numerically; material disagreements were investigated with more sources or fresher lines, not with narrative.
- Coverage and provenance are reported honestly (Vegas-rich / Vegas-supported / Industry-blend / Fallback-heavy).
- No single source was treated as authoritative.
- **No narrative, opinion, or qualitative judgment altered any projection value.**

Anything below A requires more research (more numeric sources / more prop lines) or an explicit user acceptance of the lower grade.

## Canonical hierarchy (mandatory)

1. **Industry multi-source numeric blend** (target 10+) + **Vegas multi-book layer** — co-primary evidence. Build both; form the composite from them.
2. **Role / lineup / news / availability facts** — validity layer only (who is in / out / starting). These can zero or reallocate a player; they do not invent fantasy points from a story.
3. **Sim Savant (or other single vendor)** — final fallback only when both industry breadth and Vegas coverage fail.

**Order of work, not order of weight:**
- Always research industry breadth and Vegas in parallel (or staged for efficiency).
- Weight the final composite by **evidence quality and coverage**, not by opinion:
  - Strong multi-book props → Vegas carries more weight; industry is cross-check and gap-fill.
  - Sparse props but deep industry (many independent numeric sources agreeing) → industry blend carries more weight; Vegas game totals still constrain the environment.
  - Thin on both → Savant fallback, labeled as such.

Never begin from Savant and lightly adjust. Begin from the external composite.

## Industry layer — breadth target

**Goal: A+ numeric read on what the industry is projecting.**

- Target **at least 10 independent numeric projection sources** when the sport/slate publicly supports it.
- Minimum acceptable for a non-fallback player on a mature slate: several independent numeric systems (do not stop after one or two).
- **Only numeric projections count.** Rankings, articles, podcasts, and qualitative write-ups do not enter the blend unless they publish actual projected points or component stats.
- Blend method: median, trimmed mean, or reliability-weighted consensus. Do not cherry-pick the highest or lowest.
- Convert component stats to the target site scoring when needed instead of blindly averaging fantasy-point outputs from different scoring systems.

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

**Primary use**
- Multi-book player props (with juice / both sides when available)
- Alternate / ladder markets when useful for expectation and distribution
- Game totals, spreads/moneylines, implied team totals

**Sanity-check / reconciliation use**
- Industry blend must not collectively imply a game environment that materially contradicts the betting market without a documented **data** reason (e.g. role change, confirmed lineup, stale line).
- Player component totals are checked against team implied totals and game totals.
- Large industry-vs-Vegas disagreements trigger more source pulls or fresher line checks — not narrative interpretation.

### Preferred Vegas sources
- Action Network (multi-book aggregator)
- PropCruncher or comparable multi-book prop tools
- Direct DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Hard Rock, Circa, theScore and other books when publicly accessible
- Additional reputable odds/prop aggregators

De-vig paired markets. Prefer robust multi-book consensus over any single book. Never invent a line.

## What the composite number is

For each player:

1. Build **industry consensus** from as many independent **numeric** sources as obtained (target 10+).
2. Build **Vegas-derived expectation** from available props + game context (de-vigged, multi-book).
3. Form the **composite**:
   - High Vegas confidence → Vegas-led, industry used for outlier detection and missing components.
   - Medium Vegas → blend; industry fills gaps; game markets still constrain.
   - Low/no Vegas → industry blend leads; still reconcile to game totals if they exist.
   - Thin industry + thin Vegas → Savant fallback only, labeled Fallback-heavy.
4. Apply site scoring once.
5. Record provenance: Vegas-rich / Vegas-supported / Industry-blend / Savant-fallback (and how many industry sources fed the blend).

**Nothing in steps 1–5 is narrative.** If a number cannot be traced to a scraped industry projection or a scraped sportsbook market (or a documented conversion of those), it does not belong in `Proj`.

## Cross-sport flow (efficient)

1. Intake the attached file once (names, DFS IDs, source Proj, Own, slate context).
2. Validate active universe (starters / likely roles / out players) with facts only.
3. Cache game-level Vegas markets for every game.
4. Broad prop sweep across aggregators/books.
5. Parallel (or staged) pull of industry projection sources — keep going until the breadth target is met or sources are exhausted.
6. Normalize names; reject stale/wrong-game lines.
7. Convert and form per-player composite (numeric blend only).
8. Reconcile player totals to team/game markets; investigate material breaks with more data.
9. Audit: coverage counts, largest source-to-composite moves, low-breadth players, zeros.
10. Return file (Proj updated only, unless ownership pass requested) + grade + coverage summary.
11. Stop.

## Coverage-weighted weighting (no fixed % for every player)

- **High Vegas + deep industry:** Vegas primary; industry tightens and cross-checks.
- **High Vegas + thin industry:** Vegas primary; note thin industry.
- **Low Vegas + deep industry (many sources):** Industry blend primary; Vegas game totals still used as environment constraint.
- **Low on both:** Savant fallback; label clearly.

Confidence inputs: prop count, book count, alternate markets, freshness, book agreement, **number of industry sources and their agreement**, role certainty (facts), game-market reconciliation.

## Default workflow when a file is sent

1. Projection-only unless user asks for ownership.
2. Preserve Name, DFS ID, Own, row order exactly.
3. Replace only `Proj` with the composite.
4. Return updated file + audit:
   - Projection grade (target A / A+)
   - Industry source count used (and list when useful)
   - Vegas coverage summary
   - Provenance mix (Vegas-rich / Vegas-supported / Industry-blend / Fallback-heavy)
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

If A+ composites do not outperform single-source priors over a meaningful sample, recalibrate weights — do not protect the assumption.

## Sport modules

Each `sports/<sport>.md` defines prop families, scoring conversion, and sport-specific industry sources. This file owns the cross-sport composite standard, the pure numeric conglomerate rule, and the A+ / 10+ industry breadth target.
