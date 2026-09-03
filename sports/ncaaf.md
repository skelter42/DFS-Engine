# NCAAF DFS Engine

## Core Philosophy
College football DFS is driven by role, play volume, scoring environment, ceiling, ownership, and correlation. Median projection is only the baseline. The Engine must explicitly model multiple game scripts because depth-chart uncertainty, quarterback rushing, concentrated usage, blowout risk, and pace can change fantasy outcomes dramatically.

The objective is not to reproduce Sim Savant. Savant is the starting projection/ownership source. The Engine challenges it with current market data, independent industry projections/analysis, depth charts, injuries, role information, and game-theory context.

## Required Inputs
For every slate, ingest when available:
- DraftKings entry/template CSV
- Sim Savant projections and projected ownership
- current spreads, totals, and implied team totals
- depth charts and starter designations
- injuries, suspensions, availability news, and beat-reporter updates
- independent industry projections / DFS analysis from multiple credible sources
- pace / plays per game / offensive style
- target share and route participation
- rushing share and designed QB rushing
- red-zone and goal-line role
- salary and positional eligibility
- contest type and number of entries

No single projection source is authoritative.

## NCAAF Specialized Agent Team
These passes are mandatory in addition to the DFS Engine core agents.

### 1. Depth Chart & Role Certainty Agent
Verifies starting QB, RB rotation, WR/TE starters, slot roles, injuries, transfers, suspensions, and freshman/backup uncertainty. It assigns role confidence and penalizes projections based on unclear or fragile roles.

### 2. QB Archetype Agent
Classifies QBs by fantasy path:
- dual-threat / rushing-floor QB
- pocket passer / volume QB
- efficient favorite QB
- trailing-volume underdog QB
- fragile low-volume favorite QB

It evaluates designed rushes, scramble upside, red-zone rushing, pass rate, expected game script, and stacking partners. QB rushing ceiling can justify large projection deviations.

### 3. Usage Concentration Agent
Measures how concentrated each offense is around its RBs and pass catchers. Prioritize players with durable routes, targets, carries, goal-line work, and explosive-play roles. Penalize ambiguous committees unless salary/ownership creates asymmetric upside.

### 4. Blowout & Rotation Agent
Explicitly models large-spread games. For heavy favorites, create separate branches for:
- first-half passing eruption
- starting RB controls scoring
- starters hit ceiling before rotation
- backups absorb second-half volume
- favorite disappoints relative to implied total

Do not treat blowout risk as a generic downgrade; connect it to how scoring is likely to be distributed.

### 5. Game Environment & Pace Agent
Ranks games by four-quarter fantasy potential using total, spread, pace, offensive efficiency, explosive-play ability, pass rate, and underdog competitiveness. Competitive games deserve extra stack consideration because both offenses can retain aggression for four quarters.

### 6. CFB Correlation Agent
Builds coherent combinations such as:
- QB + one pass catcher
- QB + two pass catchers when volume supports it
- QB + opponent bring-back in competitive games
- rushing-heavy favorite without forcing its QB
- opposing QB/WR stack against a favorite expected to keep scoring
- RB + team defense only when the slate/site includes defense and script supports it

Never force correlation that conflicts with the actual offensive role structure.

### 7. Script Portfolio Agent
Allocates the lineup set across explicit slate narratives rather than merely applying player exposure caps. Each lineup must belong to a plausible script family.

### 8. Duplication & Construction Agent
Evaluates likely field combinations, salary usage, common double-QB structures, chalk pairings, popular value plays, and repeated eight-player cores. It seeks tournament uniqueness without sacrificing coherent ceiling.

### 9. CFB Portfolio Risk Agent
Audits hidden concentration by:
- player
- team
- game
- QB pairing
- script family
- favorite/underdog archetype
- chalk combination
- salary construction

The portfolio should be concentrated where the Engine has an edge but diversified across ways that edge can be realized.

## Full NCAAF Handoff Chain
Slate Intake -> Projection Audit -> Depth Chart & Role Certainty -> News & Role -> Market Environment -> QB Archetype -> Usage Concentration -> Blowout & Rotation -> Game Environment & Pace -> Ownership & Leverage -> CFB Correlation -> Script Portfolio -> Portfolio Builder -> Duplication & Construction -> CFB Portfolio Risk -> Exposure Auditor -> Post-Slate Learning.

## Industry Comparison Protocol
Before final lineup construction, compare Savant against multiple independent sources whenever available.

For every meaningful player, record:
- Savant projection
- Savant projected ownership
- independent projection/analysis signals
- confirmed role
- market environment
- Engine adjustment
- confidence

Industry disagreement is useful information. Do not average sources blindly. Determine why they disagree: role, rushing upside, target concentration, blowout assumptions, matchup, or stale depth-chart information.

## Game Script Portfolio Requirements
For multi-entry builds, intentionally represent the slate's realistic paths. Common script families include:
- balanced highest-ceiling build
- favorite wins through passing
- favorite wins through rushing
- underdog keeps game competitive
- underdog trails and creates passing volume
- shootout exceeds market total
- popular high-total game disappoints
- large favorite rotates early
- low-owned starter/value role breaks the slate
- one competitive game becomes the four-quarter slate winner

The number of lineups in each family should reflect confidence and tournament leverage, not equal weighting.

## Construction Rules
- Obey all DraftKings salary, position, and eligibility rules.
- For S-FLEX slates, treat the second QB slot as a strategic decision, not an automatic rule.
- Double-QB is preferred when QB opportunity cost and ceiling justify it, but do not force it if an RB/WR creates superior tournament ceiling.
- QB stacks should be tied to real route/target roles.
- In competitive games, allow meaningful game stacks and bring-backs.
- In large-spread games, diversify passing vs rushing vs rotation outcomes.
- Avoid portfolios where most lineups share the same six- or seven-player core unless the edge is overwhelming and documented.
- Single-entry builds should favor coherent ceiling and role certainty over extreme leverage darts.

## Exposure Framework
Player exposure is an output of slate theses, not the primary objective.

Overweight when:
- role is more secure than Savant assumes
- rushing/target/red-zone ceiling is understated
- game environment supports four-quarter volume
- ownership is below realistic ceiling probability
- independent sources confirm a projection miss

Underweight when:
- projected role is fragile or backup-dependent
- blowout/rotation threatens volume
- ownership exceeds ceiling probability
- salary forces highly duplicated combinations
- projection is dependent on uncertain depth-chart assumptions

## Mandatory Exposure Audit
Every delivered lineup set must include a full side-by-side:

Player | Savant projected ownership | DFS Engine final exposure | percentage-point difference

Major deviations must include a stated reason based on role, ceiling, leverage, correlation, script coverage, or industry disagreement. This exposure card is mandatory for every NCAAF build.

## Late News Protocol
Before lock, re-check:
- QB confirmations
- surprise starters
- RB depth-chart changes
- WR/TE availability
- suspensions
- weather if material
- market movement

If late news changes a role, rebuild affected script families rather than simply swapping one player everywhere.

## Post-Slate Learning
After results are available, evaluate:
- which game scripts actually occurred
- whether the correct script families existed in the portfolio
- whether exposure was sufficient to benefit
- projection misses vs role/news misses
- ownership accuracy
- QB archetype accuracy
- blowout/rotation assumptions
- correlation quality
- lineup duplication/uniqueness
- whether a correct thesis was undermined by another roster decision

Use counterfactual review. Example questions:
- If the game-stack thesis hit, did the portfolio have the right players within it?
- If the underweight chalk failed as expected, did our alternatives actually carry enough ceiling?
- If a backup unexpectedly produced, was that foreseeable role information or ordinary variance?
- If the best QB archetype was identified, were stack partners and exposure correct?

Only repeated or clearly structural findings should become permanent rules. Do not overfit one slate.

## Default Output Package
Every completed NCAAF Engine run should produce:
1. final DraftKings upload CSV
2. human-readable lineup list
3. Savant vs DFS Engine exposure card
4. game-script family allocation
5. major industry disagreements and Engine decisions
6. key leverage/fade explanations
7. post-slate learning record when results become available
