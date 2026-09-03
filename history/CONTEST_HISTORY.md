# DFS Engine Contest History

## Purpose
Maintain a durable, privacy-safe index of contest-level results used by the DFS Engine learning loop.

Raw DraftKings standings exports and account-history files should **not** be committed to this public repository. They may contain usernames, entry IDs, financial/account information, or full-field data that does not belong in the public engine brain.

Store only sanitized contest metadata, derived metrics, and durable findings here.

## Ingestion Rules

For each standings export:

1. Deduplicate by DraftKings Contest ID.
2. Identify the user's entries in the field without persisting entry IDs or unnecessary account identifiers.
3. Record sport, contest ID, contest type, field size, best finish, best percentile, and useful aggregate portfolio metrics.
4. Extract field-level evidence such as winning score, ownership, duplication, stack/lineup structure, and top-percentile construction when available.
5. Run the Tiered Construction Analysis defined below for winner, top 1%, top 10%, top 20%, and full field.
6. Feed reusable findings into `core/LEARNING.md` and `learning/REGISTRY.md` only when they satisfy the promotion standard.
7. Do not promote one-off winning-player takes or hindsight-only conclusions.

## Tiered Construction Analysis — Mandatory

Every full standings ingest should compare lineup construction across these cohorts:

- Winner / 1st-place lineup
- Top 1%
- Top 10%
- Top 20%
- Full field baseline

The purpose is to identify what construction traits become more common as lineups move toward the top of tournaments, rather than merely copying one winning lineup.

### Track for every cohort

- sample size
- average and median fantasy score
- average aggregate ownership when available
- lineup duplication rate / average duplicate count
- salary used and salary left
- number of unique players relative to other lineups when measurable
- chalk concentration and low-owned-player count
- primary correlation / stack structure
- secondary correlation / mini-stack structure
- game-environment concentration
- position-specific construction relevant to the sport
- exposure to the highest-owned players and teams
- leverage combinations and common ownership ranges

### MLB

Track distributions for:

- 5-3, 5-2-1, 5-1-1-1, 4-4, 4-3-1, 4-2-2, and other stack shapes
- primary stack team frequency
- secondary stack team frequency
- same-game hitter concentration
- pitcher pairings
- pitcher vs opposing-stack leverage when present
- stack ownership / aggregate lineup ownership
- one-off ownership and correlation quality
- salary left on table

### NFL / CFB

Track distributions for:

- QB double stack, single stack, naked QB
- bring-back count
- secondary game stacks
- RB + DST correlation
- team/game concentration
- salary left and aggregate ownership

### NBA

Track distributions for:

- same-game player counts
- mini-correlations / opponent bring-backs
- stars-and-scrubs vs balanced salary construction
- positional salary allocation
- aggregate ownership and number of sub-10% players

### NHL

Track distributions for:

- full-line stacks
- 2-man line stacks
- power-play correlation
- defenseman correlation
- goalie + skater relationships
- team concentration and aggregate ownership

### Tennis

Track distributions for:

- favorite/underdog mix
- salary allocation
- aggregate ownership
- number of lower-owned players
- match/game-environment concentration where relevant

### Interpretation rule

Do not conclude that a construction is optimal merely because the winner used it. Prefer patterns that show a clear lift from full field -> top 20% -> top 10% -> top 1%, especially when repeated across multiple contests/slates.

For each meaningful construction feature, estimate a tier lift when possible:

`Tier Lift = Feature Rate in Target Cohort - Feature Rate in Full Field`

Also track whether the feature is monotonic across performance tiers. A construction that rises consistently from the field through top 20%, top 10%, and top 1% is stronger evidence than an isolated winner result.

## Initial Ingest — 2026-09-03

First batch received from recent DraftKings full-contest standings exports.

- 9 unique contests ingested after deduplication.
- Duplicate export detected for Contest ID `194736777`; count once.
- User entries were successfully identifiable in the standings files.
- Example best-finish observations from the batch:
  - Contest `194812059`: best finish 13th of 2,378 (~top 0.5%).
  - Contest `194736777`: best finish 62nd of 5,945 (~top 1.0%).
  - Contest `194878465`: best finish 73rd of 5,945 (~top 1.2%).
  - Contest `194731101`: best finish 83rd of 5,548 (~top 1.5%).

## 2026-09-03 MLB Early Slate — Contest 194946042

- Sport: MLB Classic
- Field size: 2,378 entries
- User entries: 20
- Winning score: 114.15
- User best: 94.15, rank 118 (~top 5.0%)
- User top-10% finishes: 2 of 20
- User top-20% finishes: 4 of 20

### Pitcher construction

- Winner: Hunter Brown + Blade Tidwell.
- Top 1%: Hunter Brown appeared in 100% of lineups; Blade Tidwell 57.7%; Jose Soriano 38.5%; Tanner Bibee 3.8%.
- Full field: Hunter Brown 71.8%; Tanner Bibee 43.5%; Jose Soriano 39.4%; Luis Castillo 19.9%; Blade Tidwell 19.7%.
- User portfolio: Hunter Brown 60%; Tanner Bibee 45%; Jose Soriano 35%; Blade Tidwell 30%; Luis Castillo 25%; Wilber Dotel 5%.
- Outcome note: Hunter Brown scored 22.7 DK points and Blade Tidwell 12.45, while Soriano (2.5), Bibee (1.6), and Castillo (-2.4) failed. The portfolio was materially underweight the slate-winning Brown/Tidwell combination relative to the true top 1%.

### Stack construction

- Winner used a 5-man Toronto primary stack with one-offs from San Francisco, Houston, and Chicago White Sox: a 5-1-1-1 construction.
- Top 1% contained 5-man stacks in roughly 42% of entries, versus roughly 23% in the full field. Toronto accounted for 10 of the 11 identified top-1% five-man primary stacks.
- User portfolio used a 5-man stack in 13 of 20 lineups (65%), so the primary structural doctrine was not the core miss.
- User best lineup used a 5-man Houston stack plus Hunter Brown + Blade Tidwell and finished 118th. It had the correct pitcher pair but the wrong primary offensive eruption relative to the winning Toronto script.
- User had two Toronto five-man stacks, but neither combined the slate's best Toronto construction with the winning pitcher pair strongly enough to reach the top tier.

### Slate-level diagnosis

- This was primarily a stack-allocation / game-script coverage miss, not a failure of the full-stack doctrine.
- Houston exposure produced a near-ceiling lineup, but Toronto was the offense that most strongly populated the top 1%.
- The pitcher portfolio carried too much exposure to Bibee/Castillo relative to their realized failure and too little Brown/Tidwell relative to the top-1% construction.
- Future review should distinguish: (1) whether the engine identified the right primary stack families, (2) whether it paired those stacks with the correct pitcher path, and (3) whether enough portfolio weight was placed on the strongest combined script.

## Metrics To Track Going Forward

Per contest:
- contest ID
- date
- sport
- slate / game type
- entry fee and max-entry format when known
- field size
- number of user entries
- best rank
- best percentile
- top 0.1%, top 1%, top 10%, and top 20% hit rates
- winning score
- user best score and score gap to winner
- actual player ownership
- lineup duplication
- winner construction profile
- top 1% construction distributions
- top 10% construction distributions
- top 20% construction distributions
- full-field construction baseline
- tier lift for major construction features
- primary/secondary stack or correlation structure
- pitcher/QB/etc. pairings when sport-relevant
- ownership leverage and game-script outcomes

Across contests:
- percentile hit rates by sport
- percentile hit rates by contest type
- ROI and profit when account-history data is joined
- ownership calibration error
- projection-vs-field performance
- portfolio concentration and diversification performance
- repeatable construction patterns among top finishers
- construction feature lift by percentile tier
- monotonic construction trends from full field to top 1%

## Workflow

`DraftKings Entry History -> Contest ID index -> Full Standings Export -> Field Analysis -> Tiered Construction Analysis -> Contest History Metrics -> Post-Slate Learning -> Durable GitHub Rule Promotion`

This file is an index/contract, not a raw-data warehouse.
