# DFS Engine Agent Architecture

The DFS Engine is a coordinated decision system. Agents are mandatory reasoning responsibilities, not necessarily separate autonomous processes. GitHub stores the durable brain; chat executes the workflow.

## Design Rule

`core/ENGINE.md` is the canonical operating sequence. `core/AGENTS.md` defines ownership of each stage. Sport files define only sport-specific implementation details. Agents must not restate global policy already defined in `core/ENGINE.md`.

The Engine should use the fewest agents needed to create clear ownership and traceable handoffs. Avoid multiple agents solving the same problem under different names.

## Canonical Agent Team

### 1. Slate Intake & Validation Agent
Owns raw slate integrity.

Responsibilities:
- identify sport, site, slate, contest, entry count, lock state, and contest type
- ingest player pool, salaries, positions, source projections, ownership, and simulations when supplied
- validate IDs, names, teams, positions, roster eligibility, game inclusion, and malformed files
- preserve source columns unchanged
- identify missing inputs before downstream modeling

Output:
- validated slate dataset
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

Canonical implementation lives in `core/MARKET_PROJECTIONS.md`; sport-specific conversion rules live in `sports/<sport>.md`.

Output per player:
- source projection(s)
- market-derived fantasy projection when available
- DFS Engine projection
- projection difference vs source
- market coverage/confidence
- major evidence and unresolved uncertainty

### 3. Ownership & Field Agent
Owns DFS Engine expected ownership and likely field behavior.

Responsibilities:
- triangulate source ownership, broader industry ownership, salary/value, roster construction, contest type, slate context, and likely late-news behavior
- estimate DFS Engine expected ownership independently of final exposure
- identify chalk combinations, likely stack/game concentrations, pitcher/QB pairings, duplication pressure, and fragile field assumptions
- never treat projected ownership as a reason to fade or play someone mechanically

Output per player/construction:
- source ownership
- DFS Engine expected ownership
- ownership difference
- confidence
- field-construction notes

### 4. Simulation & Scenario Agent
Owns uncertainty and outcome distributions.

Responsibilities:
- use DFS Engine projections as the primary simulation mean/input while retaining source projections for sensitivity checks
- estimate ceiling, floor/failure, top-tail rates, correlated team/game outcomes, and scenario frequencies
- use empirical/calibrated sport-specific volatility and correlation; never invent unsupported SDs or correlation coefficients
- ingest native/vendor simulation outputs when useful but do not treat them as final authority

Canonical simulation policy lives in `core/SIMULATION.md`.

Output:
- player/team/game outcome distributions
- scenario probabilities
- top-tail and failure signals
- sensitivity/uncertainty notes

### 5. Sport Strategy & Game Script Agent
Owns sport-specific correlation and the slate thesis board.

Responsibilities:
- apply the relevant `sports/<sport>.md` rules
- create multiple coherent ways the slate can be won
- identify which field assumptions succeed or fail in each world
- connect leverage decisions to the players/teams that directly benefit
- identify construction archetypes appropriate to each script
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
- generate a broad legal candidate pool using Engine projection, expected ownership, simulation, salary, correlation, and contest rules
- treat optimization as candidate generation, not final authority
- select/reshape the final set around coherent scripts, leverage, duplication, and first-place equity
- allow exposures, stack structures, salary usage, and roster archetypes to emerge naturally
- never use arbitrary hard caps/floors/stack quotas unless required by site legality, contest rules, confirmed inactivity, or an explicit user constraint

Output:
- final portfolio
- script assignment for each lineup when practical
- key portfolio allocations

### 7. Portfolio Risk & Exposure Auditor
Owns final strategic QA.

Responsibilities:
- detect hidden concentration by player, stack/team, game, pitcher/QB pairing, salary construction, chalk combination, and script family
- distinguish intentional concentration from repeated optimizer convenience
- verify multiple credible paths to first remain represented
- verify all lineup rows are legal, unique as required, and upload-ready
- preserve the required projection/ownership/exposure audit

Required player audit:

| Player | Source Projection | DFS Engine Projection | Projection Diff | Source Projected Ownership | DFS Engine Expected Ownership | Ownership Diff | DFS Engine Exposure |
|---|---:|---:|---:|---:|---:|---:|---:|

When the user asks for direct file-only exposure or stack counts, calculate them from the delivered file without adding unrelated comparisons.

Output:
- upload-ready lineup file
- exposure audit
- stack/correlation allocation audit where relevant
- largest intentional deviations
- unresolved pre-lock risks

### 8. Post-Slate Learning Agent
Owns feedback and durable learning.

Responsibilities:
- compare source projection -> Engine projection -> actual result
- compare source ownership -> Engine expected ownership -> actual field ownership
- compare Engine exposure/scripts -> portfolio performance
- separately grade projection calibration, ownership calibration, market interpretation, simulation, sport/game-script judgment, correlation, duplication, and portfolio construction
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

A late material role, weather, lineup, or market change loops back to Market Projection and all affected downstream stages.

## Handoff Contract

Every agent passes forward:
- verified facts/source values
- derived values
- assumptions
- confidence
- unresolved uncertainty

Later stages must not silently overwrite source data or earlier facts. Derived estimates may change only because of explicit new evidence or a documented model decision.

## GPT-over-Math Final Authority

Quantitative systems generate evidence and candidates. The final portfolio requires GPT/AI strategic sign-off as defined in `core/ENGINE.md`.

GPT judgment must remain grounded in market projections, ownership, simulations, current news, sport correlation, contest structure, and portfolio interaction. It is not permission for ungrounded narrative overrides.

## Sport-Specific Extensions

Do not create permanent specialized agents unless they own a genuinely distinct sport-specific task that cannot be cleanly handled by the eight canonical agents. Prefer defining sport-specific responsibilities inside the Sport Strategy & Game Script Agent or Simulation & Scenario Agent.

Existing useful MLB responsibilities such as stack architecture, pitcher-failure leverage, duplication, and portfolio concentration remain mandatory concepts, but they are responsibilities inside the canonical agents rather than separate overlapping global agents.

Likewise NCAAF role certainty, QB archetypes, blowout/rotation behavior, usage concentration, pace, and correlation belong in `sports/ncaaf.md` and are executed by the canonical agents rather than requiring a growing list of independent agents.
