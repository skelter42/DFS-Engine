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

## Full-run requirement — mandatory

Every `Market Inputs — [SPORT]` request is a **full slate-wide research pass by default**. Do not substitute a quick targeted adjustment pass unless the user explicitly asks for one.

A valid full run must:
1. Read the entire attached Savant player pool.
2. Identify every game/event on the slate.
3. Research game-level markets for every game/event.
4. Research player-level props for as much of the slate as the public market actually offers.
5. Use multiple books/sources where practical, not one sportsbook or one DFS source.
6. Where direct Vegas/player-prop coverage is incomplete, research multiple reputable industry projection systems before falling back to Savant.
7. Convert the final statistical expectation into the correct site-specific fantasy scoring.
8. Build ownership from multiple current site/slate-specific ownership touch points plus the behavioral ownership model below.
9. Use Savant only as the final documented fallback when both market and broader industry coverage are insufficient.
10. Audit the completed file and return it.
11. Stop.

### No partial-run masquerading

Do not call a file “Market Inputs complete” if only a small subset of players were researched or adjusted.

If broad market coverage is unavailable, say so explicitly and quantify:
- how many players were Vegas-rich
- how many were Vegas-supported
- how many were industry-supported
- how many remained fallback-heavy

If the run is fallback-heavy, label it as such rather than implying a fully market-derived slate.

## Projection principle

**Vegas is the primary truth source. Broader industry projection consensus fills the gaps. Site scoring converts the final statistical expectation into DFS points.**

Use multiple sportsbooks and both sides of priced markets when available. A posted prop line without juice is not a complete expectation. De-vig and consensus prices where practical. Prefer broad market agreement to any one book.

Reconcile player props with game-level markets so individual projections do not collectively imply a materially different game environment from the betting market without a documented reason.

Relevant markets depend on sport. Examples:
- MLB: pitcher K, outs, ER, hits/walks allowed, win; hitter hits, total bases, HR, RBI, runs, walks, SB, combo props; game total, ML, run line, team totals.
- NFL/NCAAF: passing/rushing/receiving yards, receptions, TDs, attempts, completions, interceptions; spread, total, team totals.
- NBA: points, rebounds, assists, 3PM, steals/blocks where available, turnovers where relevant; spread, total, team totals, minutes/injury context.
- NHL: shots, goals, points, goalie saves/goals allowed/win; game total, ML, team totals, PP/line context.
- Tennis: match/set/game markets, moneyline, total games, aces/double faults/break markets where available.

Use lineup/role/minutes/workload/injury/weather/venue context only to allocate market expectation appropriately. Savant is the conservative final fallback; never invent precision.

## Projection source hierarchy — mandatory

Use this order for every player:

### Tier 1 — Vegas-rich
Use when multiple direct player props are available, ideally across multiple books, plus stable game/team markets.

- Direct props and prices are primary.
- Use both over and under prices when possible.
- Use multiple sportsbooks and consensus/de-vigged expectations where practical.
- Reconcile with game total, spread/moneyline, and team total.

### Tier 2 — Vegas-supported
Use when only some direct props are available.

- Start with available direct props.
- Fill missing components from game/team markets, role/workload, and independent projection systems.
- Vegas still carries the most weight.

### Tier 3 — Industry-supported
Use when direct player props are sparse or absent but broader public/industry projection coverage exists.

Research multiple reputable projection systems before retaining Savant unchanged. Depending on sport and availability, examples may include:
- THE BAT / THE BAT X
- RotoGrinders projections
- Daily Fantasy Fuel
- FantasyPros daily projections
- LineStar
- Stokastic/Awesemo public projection content when accessible
- RotoWire projection/DFS tools when accessible
- other reputable, current, site-specific projection systems

Rules:
- Prefer numeric projections over narrative analysis.
- Prefer current site/slate-specific data.
- Use multiple independent sources where possible.
- Use median, trimmed mean, or reliability-weighted consensus rather than cherry-picking the highest/lowest projection.
- Convert component-stat projections into the target site's scoring when useful instead of blindly averaging fantasy-point outputs.
- Cross-check the industry consensus against game/team Vegas markets so industry projections cannot collectively contradict the betting environment without explanation.
- Strong Vegas evidence overrides conflicting industry consensus.

### Tier 4 — Savant fallback
Use only when direct market coverage and broader industry coverage are both insufficient.

- Retain Savant conservatively.
- Do not manufacture a new number from thin evidence.
- Mark internally as fallback-heavy.

## Projection research standard

For each slate, collect as many of these as legitimately available:
- multiple sportsbook prices for the same prop
- both over and under prices when possible
- game totals, spreads/moneylines and team totals
- correlated player markets where useful
- recent line movement when material
- confirmed starting/lineup/role information
- site-specific DFS scoring rules
- multiple reputable industry projection systems for players with sparse direct prop coverage

Where many books disagree, prefer a consensus expectation rather than cherry-picking the most favorable line.

Where direct props are missing, do **not** jump directly to Savant. First build an industry consensus from available independent projections, anchored/reconciled to the game-level market. Savant is the last fallback.

## Projection confidence

Assign an internal projection confidence tier:
- **A — Vegas-rich:** multiple direct props across multiple books plus stable game/team markets.
- **B — Vegas-supported:** some direct props plus game context and independent projection support.
- **C — Industry-supported:** direct props are sparse, but multiple reputable projection systems plus game/team Vegas provide a coherent consensus.
- **D — Fallback-heavy:** insufficient market and industry coverage; retain Savant conservatively.

A player does not need many direct props to avoid Tier D if multiple credible industry systems and the game market provide strong independent support. Conversely, one industry projection alone does not create high confidence.

The final CSV does not need to include confidence tiers unless requested, but every full run must report coverage counts by these tiers or an equivalent summary.

## Ownership is a field-behavior forecast

Ownership is harder than projection because it is not simply about what will happen. It is a forecast of what DFS entrants will choose after seeing salaries, projections, news, optimizer outputs, industry content, and slate structure.

The goal is:

**`Own = best estimate of actual site/slate field roster percentage`**

It must be objective. Never change ownership to create leverage, force Savant toward a player, or manufacture a desired portfolio.

### Step 1 — Numeric ownership consensus
Collect as many current, legitimate, site-specific ownership projections as accessible.

Rules:
- Savant is one source, not the authority.
- Prefer several independent numeric sources.
- Match the exact site and slate.
- Weight fresher updates more heavily as lock approaches.
- Use a median, trimmed consensus, or reliability-weighted consensus so one outlier cannot dominate.
- Do not mix DK and FD ownership directly.
- Do not mix main-slate and short-slate ownership directly.
- Do not claim broad consensus if only one numeric source was available.

If multiple reliable sources agree closely, that consensus should carry heavy weight.

### Step 2 — Reconstruct what the field sees
For every player, estimate the information that a sharp DFS field and common optimizers are reacting to:
- site salary and salary rank
- market-derived/industry-supported fantasy projection
- points-per-dollar/value
- position or roster-slot scarcity
- role, lineup spot, minutes/workload and confirmed news
- game/team implied scoring environment
- stacking/correlation popularity where relevant
- opportunity cost versus alternatives at the same position/salary tier
- obvious salary relief/value created by news
- star/name recognition and obvious slate narratives
- industry tout frequency and consensus
- recent ownership-moving news
- likely optimizer behavior and common lineup construction paths

This layer is not used to invent ownership. It is used to determine whether the published numeric consensus is behaviorally plausible.

### Step 3 — Team/game/stack ownership reconciliation
Ownership must be coherent at the portfolio level.

Estimate which teams, games, stacks, stars, value plays, and salary constructions the field is likely to prioritize. Player-level ownership should make sense relative to those aggregate stories.

Examples:
- In MLB, if a team is projected to be the most popular stack, its core hitters should not all project as low-owned unless there is a salary/position reason.
- In NFL/NCAAF, a popular QB/WR game stack should be reflected in correlated ownership.
- In NBA, a newly opened value play can increase ownership on both that player and expensive stars that the salary relief enables.

### Step 4 — Behavioral sanity model
Treat ownership as a probability of roster selection and compare the numeric consensus with a behavioral model driven by:
- projection
- value
- salary
- role
- position
- Vegas environment
- industry attention
- roster construction
- correlation/stacking context

The behavioral model is a sanity check, not a replacement for real ownership data.

Large disagreements require investigation. If Savant says 8% but several industry sources, value metrics, and public content imply 25%+, do not ship 8% without resolving why.

### Step 5 — Site/slate calibration
Ownership is site- and slate-specific.

Calibrate for:
- DraftKings vs FanDuel salary structure
- roster rules and positional flexibility
- slate size
- number of viable alternatives
- amount of obvious value
- concentrated vs flat projection landscape
- common optimizer construction paths
- stack requirements/correlation incentives where relevant

The same player can correctly have very different ownership across DK and FD.

### Step 6 — Final ownership estimate and confidence
Produce the final `Own` using numeric consensus as the anchor, modified only when credible behavioral evidence shows the consensus is stale or inconsistent.

Assign an internal ownership confidence tier:
- **A — High confidence:** multiple fresh numeric sources agree and the field story supports them.
- **B — Good confidence:** several signals with modest disagreement.
- **C — Sparse:** limited numeric coverage; behavioral inference contributes materially.
- **D — Fallback-heavy:** retain Savant/industry baseline conservatively.

When confidence is low, avoid false precision and make smaller changes from Savant.

### Ownership audit failures
Treat the following as failures that must be investigated before delivery:
- a universally touted obvious value modeled as nearly unowned
- a highly popular projected stack whose core players are all modeled low-owned
- a player with extreme ownership that has no plausible salary/value/role/field explanation
- using stale ownership after material injury/lineup news
- mixing ownership from the wrong site or slate
- large ownership changes with no observable field-behavior explanation
- calling ownership “industry consensus” when only one source was checked

## Player identity preservation — absolute rule

The attached Savant CSV is the canonical identity source.

For every returned row:
- `Name` must be copied **exactly character-for-character** from the source Savant file.
- `DFS ID` must be copied **exactly character-for-character** from the source Savant file.
- Do not normalize accents, punctuation, suffixes, apostrophes, hyphens, spaces, capitalization, abbreviations, or name order in the output.
- Do not replace a Savant name with a sportsbook, DFS-site, or industry spelling.
- Do not generate names from an external player database.
- External-source names may be normalized internally for research matching only; after matching, write results back to the exact original Savant row.
- Never modify `Name` or `DFS ID` as part of deduplication.

Before delivery, compare every output `Name` and `DFS ID` against the source file. Any text mismatch is an audit failure.

### Savant ambiguous-name handling

Some names can still trigger Savant mapping prompts even when the text is unchanged because Savant may have multiple internal identities with the same display name.

For a known ambiguous row:
1. First preserve the exact original `Name` and `DFS ID`.
2. If Savant still cannot import it automatically and the row's `Proj`/`Own` were not changed, omit that row from the import so Savant retains its native values.
3. If the row's `Proj` or `Own` would be changed, do **not** silently rename it. Either keep the exact source identity and flag that manual mapping may be required, or conservatively revert that player's values to the source and omit the row if an import-clean file is required.
4. Record the omitted/flagged identity in the audit summary.

The priority is a clean, repeatable Savant import without corrupting player identity.

## Output contract

Return exactly the source Savant import structure, normally:

`Name, DFS ID, Proj, Own`

- `Name` = exact source Savant text, unchanged.
- `DFS ID` = exact source Savant text, unchanged.
- `Proj` = site-specific fantasy points.
- `Own` = expected site/slate field ownership percentage.
- Only `Proj` and `Own` are intended to change during Market Inputs.

## Mandatory import audit

Every returned file must pass:
1. Exact source column structure preserved.
2. `Name` values are character-for-character identical to their source Savant rows.
3. `DFS ID` values are character-for-character identical to their source Savant rows.
4. Correct sport/site scoring system used.
5. No duplicate DFS IDs created by the process.
6. No duplicate exact-name rows created by the process.
7. Never deduplicate by editing a player's name or ID.
8. Remove dead duplicate source identities only when one live identity clearly exists and document the removal.
9. Apply the Savant ambiguous-name handling rules above.
10. `Proj` numeric and non-negative.
11. `Own` numeric when present and between 0 and 100.
12. Zero projections intentional.
13. Largest projection and ownership changes reviewed for plausibility.
14. Compare output identity columns directly against the source before saving.
15. Return a short audit summary: rows in/out, mapping conflicts, identity exceptions, projection changes, ownership changes, and fallback-heavy areas.
16. Return projection coverage counts as Vegas-rich / Vegas-supported / industry-supported / fallback-heavy (or equivalent).

## Hard stop

Market Inputs does **not**:
- build lineups
- simulate lineups
- rank lineups
- optimize lineups
- set exposures
- choose stacks
- allocate contests
- alter projections to manufacture leverage
- alter ownership to manufacture leverage

After returning the audited CSV, stop. The user performs lineup generation and exposure spreading inside Sim Savant and may send the resulting portfolio back for a separate final game-theory/exposure audit.

## Core philosophy

**Vegas estimates what happens first. Industry consensus fills missing market coverage. Ownership estimates what the field will play. Savant builds the lineups.**

Every Market Inputs invocation is a full slate-wide research pass unless the user explicitly requests a quicker targeted adjustment.

**Only Proj and Own should change. Savant player identity text is immutable.**

Keep projection quality, ownership forecasting, player identity, and portfolio game theory separate so each layer can be evaluated honestly.