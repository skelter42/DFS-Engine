# DFS Engine Agent Architecture

The DFS Engine is a coordinated decision system. Agents are mandatory reasoning responsibilities, not necessarily separate autonomous processes. GitHub stores the durable brain; chat executes the workflow.

## Design Rule

`core/ENGINE.md` is the canonical operating sequence. `core/AGENTS.md` defines ownership of each stage. `core/SIMULATION.md` is the single authoritative simulation specification. Sport files define only sport-specific implementation details. Agents and sport files must not restate global policy already defined in core files.

The Engine should use the fewest agents needed to create clear ownership and traceable handoffs. Avoid multiple agents solving the same problem under different names.

## Canonical Agent Team

### 1. Slate Intake & Validation Agent
Owns raw slate integrity and pre-generation eligibility.

Responsibilities:
- identify sport, site, slate, contest, entry count, lock state, and contest type
- ingest player pool, salaries, positions, source projections, ownership, and simulations when supplied
- validate IDs, names, teams, positions, roster eligibility, game inclusion, and malformed files
- preserve source columns unchanged
- identify missing inputs before downstream modeling
- apply a hard eligibility gate before any projection, simulation, or candidate-generation stage

Hard eligibility gate:
- exclude any player with a source projection of exactly 0 unless there is verified current evidence that the zero is stale and the player has an active role that warrants a rebuilt Engine projection
- exclude any player with a blank/missing source projection when there is no verified current active role or defensible market-derived projection
- exclude confirmed inactive/out/scratched players
- for sports with confirmed starters/lineups, require current role validation near lock before treating a player as lineup-eligible
- if a zero or missing source projection conflicts with verified active status, stop and resolve the conflict explicitly; do not silently pass the player through optimization
- eligibility is a hard structural gate, not an exposure preference or game-theory decision

Output:
- validated slate dataset
- explicit eligible-player universe
- excluded-player list with reason
- source inventory
- unresolved data gaps

### 2. Market Projection Agent
Owns the DFS Engine player projection.

Responsibilities:
- build market-derived fantasy projections whenever sufficient player props exist
- use multi-book markets, de-vigging, robust consensus, alternate lines/ladders, and sport-specific prop-to-fantasy conversion
- use Action Network as a preferred aggregator when accessible, while allowing other reliable market sources
- incorporate game-level markets, official role/news, environment, and industry projections as validation or fallback inputs
- assign projection confidence based on market coverage and data quality
- shrink sparse-market estimates toward a prior instead of inventing precision
- preserve source/vendor projections separately for comparison and sensitivity analysis
- never override the eligibility gate merely because a market line exists without confirming the player is active for the slate

Canonical implementation lives in `core/MARKET_PROJECTIONS.md`; sport-specific conversion rules live in `sports/<sport>.md`.

Output per player:
- source projection(s)
- market-derived fantasy projection when available
- DFS Engine projection
- projection difference vs source
- market coverage/confidence
- major evidence and unresolved uncertainty

### 3. Ownership & Field Agent
Owns DFS Engine expected ownership and likely sharp-field behavior.

The field model must represent how strong tournament players and optimizer-driven entrants are likely to construct lineups, not merely reproduce a player-ownership column.

Responsibilities:
- triangulate source ownership, broader industry ownership, salary/value, roster construction, contest type, slate context, and likely late-news behavior
- estimate DFS Engine expected ownership independently of final exposure
- model projection-source convergence: players who rate well across multiple common projection systems should receive more field pressure than a single-source estimate may imply
- model optimizer sensitivity to salary-adjusted projection/value, positional scarcity, cheap starters/value pieces, and obvious spend-up combinations
- identify likely chalk combinations rather than treating player ownership as independent; estimate common pitcher/QB pairings, stack pairings, secondary-stack pairings, bring-backs, and value cores as sport-appropriate
- estimate construction-level popularity including salary utilization, roster archetype, stack structure, positional combinations, and common lineup paths
- distinguish total-field ownership from sharp-field behavior when contest size/type suggests the entrant pool is materially sharper or more optimizer-driven
- account for late news/lineup movement and how fast sharp fields are likely to react
- identify duplication pressure and fragile field assumptions
- never treat projected ownership as a reason to fade or play someone mechanically

Field-model principle:

**Expected field behavior = player ownership + conditional ownership + construction popularity.**

A lineup made of individually reasonable ownership plays may still be extremely duplicated if the combination is the obvious optimizer path. Conversely, a lineup does not become unique merely because one player is low owned if the rest of the construction is highly conventional.

When evidence permits, preserve both:
- overall expected ownership / construction behavior
- sharp-field expected ownership / construction behavior

If separate sharp-field data is unavailable, infer it cautiously from projection/value consensus, contest profile, lineup construction incentives, and known optimizer behavior; label uncertainty rather than inventing precision.

Output per player/construction:
- source ownership
- DFS Engine expected ownership
- sharp-field expected ownership when defensible
- ownership difference
- confidence
- conditional/chalk-combination notes
- likely field construction archetypes
- duplication-risk notes

### 4. Simulation & Scenario Agent
Owns all simulation execution and interpretation. GPT does not substitute for simulation.

Responsibilities:
- follow `core/SIMULATION.md` as the single authoritative simulation contract
- use DFS Engine projections as the primary simulation mean/input while retaining source projections for sensitivity checks
- generate full-slate correlated worlds when executable inputs are sufficient
- estimate ceiling, floor/failure, top-tail rates, correlated team/game outcomes, scenario frequencies, lineup finish proxies, and portfolio overlap
- use empirical/calibrated sport-specific volatility and correlation; never invent unsupported SDs or correlation coefficients
- ingest vendor/native simulation outputs when useful but do not treat them as final authority
- clearly label whether a build used: (a) native executable simulation, (b) trusted external simulation inputs, or (c) scenario-only fallback because calibrated sim inputs were unavailable
- never describe a scenario-only reasoning pass as a Monte Carlo simulation

Implementation rule:
- there should be one native executable simulation implementation shared across sports, with sport-specific distribution/correlation adapters; do not create separate overlapping simulators in sport files
- if native simulation code is unavailable for a build, preserve the gap explicitly rather than letting GPT silently mimic simulation

Output:
- simulation mode used
- player/team/game outcome distributions
- scenario probabilities
- lineup top-tail / finish proxies when field modeling is available
- portfolio overlap / hidden-world concentration
- sensitivity/uncertainty notes

### 5. Sport Strategy & Game Script Agent
Owns sport-specific correlation and the slate thesis board.

Responsibilities:
- apply the relevant `sports/<sport>.md` rules
- create multiple coherent ways the slate can be won
- identify which field assumptions succeed or fail in each world
- connect leverage decisions to the players/teams that directly benefit
- identify construction archetypes appropriate to each script
- interpret simulation output strategically without replacing it
- prevent the Engine from collapsing to one median forecast

Examples:
- MLB stacks and pitcher-failure leverage
- NFL/NCAAF QB/pass-catcher and game correlations
- NBA minutes/usage redistribution and game environments
- NHL line/power-play correlation
- tennis opponent negative correlation and match outcomes

Output:
- slate script board
- correlation map
- sport-specific construction guidance

### 6. Candidate & Portfolio Agent
Owns lineup generation and final portfolio assembly.

Responsibilities:
- generate candidates only from the eligible-player universe approved by Slate Intake & Validation
- generate a broad legal candidate pool using Engine projection, expected ownership, conditional field behavior, simulation outputs when available, salary, correlation, and contest rules
- treat optimization as candidate generation, not final authority
- compare candidate constructions against likely sharp-field constructions rather than only summing individual ownership
- select/reshape the final set around coherent scripts, leverage, duplication, top-tail simulation evidence when available, and first-place equity
- allow exposures, stack structures, salary usage, and roster archetypes to emerge naturally
- when entries span multiple contests, allocate lineups under the two-level framework in `core/ENGINE.md` so each contest is a complete mini-portfolio and the combined entries remain one coordinated bankroll portfolio
- never use arbitrary hard caps/floors/stack quotas unless required by site legality, contest rules, confirmed inactivity, or an explicit user constraint

Output:
- final portfolio
- script assignment for each lineup when practical
- contest-level allocation and quality ladder when multiple contests are entered
- key portfolio allocations

### 7. Portfolio Risk & Exposure Auditor
Owns final strategic QA and independent pre-delivery eligibility validation.

Responsibilities:
- detect hidden concentration by player, stack/team, game, pitcher/QB pairing, salary construction, chalk combination, and script family
- audit construction-shape distribution when the sport has meaningful correlation structures (for example MLB stack sizes, NFL/NCAAF game stacks, NHL line stacks); compare the final mix with sport correlation, slate size, salary/position constraints, simulation evidence when available, and likely sharp-field construction
- when a portfolio is unusually concentrated in or unusually sparse on a high-correlation construction (for example very few MLB 5-man stacks), require an explicit strategic explanation and stress-test a plausible alternative construction mix before final delivery; this is a diagnostic requirement, not a hard quota or preset stack rule
- compare the portfolio to likely sharp-field archetypes and flag accidental duplication with common optimizer constructions
- distinguish intentional concentration from repeated optimizer convenience
- verify multiple credible paths to first remain represented
- for multi-contest builds, independently verify that every contest has viable script coverage, that higher-priority quality tilts are modest and justified, and that no contest is merely receiving leftover lineups
- audit portfolio concentration across simulated winning worlds when simulation output exists
- verify all lineup rows are legal, unique as required, and upload-ready
- independently recheck every rostered player against the current eligibility universe immediately before delivery
- fail the build if any delivered lineup contains a player with a source projection of 0, missing unresolved projection/role, confirmed inactive/out/scratched status, or another unresolved eligibility conflict
- if verified current evidence proves a zero source projection is stale, require the rebuilt Engine projection and active-status evidence to be documented before allowing that player into the final file
- preserve the required projection/ownership/exposure audit

Required player audit:

| Player | Source Projection | DFS Engine Projection | Projection Diff | Source Projected Ownership | DFS Engine Expected Ownership | Ownership Diff | DFS Engine Exposure |
|---|---:|---:|---:|---:|---:|---:|---:|

When the user asks for direct file-only exposure or stack counts, calculate them from the delivered file without adding unrelated comparisons.

Output:
- upload-ready lineup file
- eligibility validation result
- exposure audit
- stack/correlation allocation audit where relevant
- simulation/portfolio-risk summary when available
- largest intentional deviations
- unresolved pre-lock risks

### 8. Post-Slate Learning Agent
Owns feedback and durable learning.

Responsibilities:
- compare source projection -> Engine projection -> actual result
- compare source ownership -> Engine expected ownership -> actual field ownership
- compare estimated sharp-field constructions -> actual top-field constructions when contest data is available
- compare Engine exposure/scripts -> portfolio performance
- separately grade projection calibration, ownership calibration, field-construction calibration, market interpretation, simulation calibration, sport/game-script judgment, correlation, duplication, eligibility failures, and portfolio construction
- run counterfactual review so one bad outcome does not produce the wrong lesson
- store single-slate observations as hypotheses unless structurally true or repeatedly supported
- promote, merge, revise, or remove durable rules under `core/PROCESS_GOVERNANCE.md`

Output:
- process diagnosis
- durable lessons or hypotheses
- GitHub updates only when warranted

## Canonical Handoff

Slate Intake & Validation
-> Market Projection
-> Ownership & Field
-> Simulation & Scenario
-> Sport Strategy & Game Script
-> Candidate & Portfolio
-> Portfolio Risk & Exposure Audit
-> Final news/market validation
-> Delivery
-> Post-Slate Learning

A late material role, weather, lineup, or market change loops back to Market Projection and all affected downstream stages. A late eligibility change immediately invalidates affected candidates and lineups and requires rebuild/revalidation before delivery.

## Handoff Contract

Every agent passes forward:
- verified facts/source values
- derived values
- assumptions
- confidence
- unresolved uncertainty
- current eligibility status

Later stages must not silently overwrite source data or earlier facts. Derived estimates may change only because of explicit new evidence or a documented model decision.

## GPT-over-Math Final Authority

Quantitative systems generate evidence and candidates. The final portfolio requires GPT/AI strategic sign-off as defined in `core/ENGINE.md`.

GPT judgment must remain grounded in market projections, ownership, simulations, current news, sport correlation, contest structure, and portfolio interaction. It is not permission for ungrounded narrative overrides, is not a replacement for Monte Carlo simulation, and cannot override an unresolved eligibility failure.

## Sport-Specific Extensions

Do not create permanent specialized agents unless they own a genuinely distinct sport-specific task that cannot be cleanly handled by the eight canonical agents. Prefer defining sport-specific responsibilities inside the Sport Strategy & Game Script Agent or Simulation & Scenario Agent.

Existing useful MLB responsibilities such as stack architecture, pitcher-failure leverage, duplication, and portfolio concentration remain mandatory concepts, but they are responsibilities inside the canonical agents rather than separate overlapping global agents.

Likewise NCAAF role certainty, QB archetypes, blowout/rotation behavior, usage concentration, pace, and correlation belong in `sports/ncaaf.md` and are executed by the canonical agents rather than requiring a growing list of independent agents.
