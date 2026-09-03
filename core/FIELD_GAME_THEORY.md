# DFS Field Game Theory & Bink Architecture

This document defines how the DFS Engine should think about a sharp tournament field. It is a strategic layer used by sport-specific engines, beginning with MLB.

## Core Assumption: The Field Is Sharp

Assume serious tournament opponents have access to strong projections, ownership projections, optimizers, betting markets, news, and standard DFS strategy. The Engine should not expect to win by merely identifying obvious high-projection plays.

The edge must come from how information is combined and how the portfolio is constructed:

- conditional leverage
- correlation
- lineup-level ownership interaction
- duplication avoidance
- pitcher/stack and opponent interactions
- salary construction
- first-place path selection
- portfolio allocation across those paths

Chalk is not bad because it is popular. Contrarianism is not automatically good. A fade or overweight should identify what the field believes, why that belief is reasonable, what evidence supports disagreement, and which portion of the field loses if the Engine is right.

## 1. Source Reliability Layer

The Engine must seek multiple independent projection and ownership sources whenever accessible. Sim Savant is one useful source, not the market truth.

For each source, record when possible:

- source name
- projection or ownership type
- timestamp/freshness
- whether lineups/news were incorporated
- historical reliability notes
- known model tendencies or blind spots
- whether the source is truly independent or derivative of another source

The Engine should distinguish:

- broad consensus
- thin consensus
- one-source opinion
- meaningful outlier
- stale or questionable data

Do not blindly average sources. AI interpretation determines whether disagreement represents information lag, model methodology, uncertainty, or a possible edge.

Over time, post-slate records should be used to evaluate which sources were most informative for actual fantasy production, actual ownership, market movement, and winning construction.

## 2. Field Construction Model

Player ownership alone is insufficient. The Engine must estimate how the sharp field will combine players.

Before lineup construction, model likely field behavior at the combination level:

- most common pitcher pairs
- most common primary stacks
- most common 5-man stack combinations
- common secondary stacks and one-offs
- chalk value clusters
- popular salary-saving combinations
- common salary-used ranges
- common batting-order combinations
- likely stack + pitcher pair interactions
- likely ownership concentration by game environment
- constructions likely to duplicate heavily

The goal is not perfect prediction of every opposing lineup. The goal is to identify where the field is likely to cluster and what conditions make those clusters fail together.

### Field Assumption Map

For each major field construction, record:

- what the field is likely to build
- why the field is likely to build it
- approximate popularity/confidence
- key dependency
- failure condition
- beneficiaries if it fails
- alternative construction that gains leverage

Example:

`Popular SP1 + popular SP2 + chalk 5-man offense + obvious salary value`

The Engine should ask whether a different secondary stack, pitcher pairing, wraparound stack, or salary structure creates a stronger first-place payoff without forcing bad plays.

## 3. Conditional Leverage

Evaluate leverage conditionally rather than treating low ownership as an objective.

A lineup can gain leverage because:

- it directly opposes a popular pitcher
- it uses a different branch of a popular stack
- it retains good chalk but changes the correlated secondary outcome
- it uses a pitcher combination the field underuses
- it avoids a value cluster that causes duplication
- it exploits a salary structure the field rarely reaches
- one event simultaneously helps the Engine and damages a large portion of the field

The preferred leverage is asymmetric: one plausible outcome improves our lineup while causing many competing lineups to fail.

## 4. Contest-Specific Bink Strategy

First-place strategy must respond to contest structure. Do not apply the same bink requirements to every tournament.

Inputs should include:

- field size
- max entries per user
- our number of entries
- entry fee
- payout concentration
- top prize
- minimum cash structure
- expected field sharpness
- likely duplication pressure

### Smaller Fields / Single Entry

Prefer stronger median/ceiling combinations and fewer fragile leverage bets. Uniqueness still matters, but do not sacrifice high-quality plays simply to become different.

### 5-Max / Moderate Fields

Own several high-confidence first-place paths with deliberate branching. Avoid five cosmetically different versions of the same thesis.

### 20-Max

Use meaningful scenario coverage with enough bullets inside the strongest paths to capitalize when the thesis is right. Balance within-path concentration and across-path coverage.

### 150-Max / Very Large Fields

Expand first-place path coverage and lineup-level game theory. More aggressive asymmetric leverage, construction variation, and duplication avoidance are justified, while still rejecting weak low-owned plays that have no credible winning path.

Contest strategy should be based on actual contest attributes when available rather than contest labels alone.

## 5. Lineup Traceability Contract

Every AI-built lineup must be auditable from evidence to portfolio slot.

Each lineup should store:

- contest
- first-place path ID
- primary win condition
- secondary win condition
- pitcher condition
- chalk dependency
- leverage event
- expected field construction being attacked or accepted
- key industry evidence
- source disagreements that mattered
- why this lineup deserves a portfolio slot
- what other lineups it is highly failure-correlated with

The desired chain is:

`industry evidence -> AI interpretation -> field assumption -> first-place path -> lineup construction -> portfolio exposure`

If the Engine cannot explain that chain, the lineup should be considered strategically incomplete even if it is legal and highly projected.

## 6. Bink Coverage vs Dead Overlap

A portfolio should maximize probability-weighted first-place coverage, not raw lineup diversity.

Two lineups that differ by players but require the same pitcher pair, primary stack, chalk outcome, and salary structure are largely the same bet.

Before final approval, identify:

- meaningful first-place paths owned
- strongest paths with no exposure
- intentionally faded paths and why
- largest dead-overlap cluster
- most fragile shared dependency
- most asymmetric leverage path
- number of lineups per path
- whether concentration is intentional

A strong path may deserve multiple coordinated bullets. A weak path should not receive a lineup solely to increase path count.

## 7. Post-Slate Field Calibration

Store and review, when data is available:

- projected ownership by source
- actual ownership
- projected field constructions
- actual winner construction
- top-1% construction patterns
- top-10% / top-20% patterns only when standings coverage is sufficient
- actual duplication when known
- our first-place path map
- our exposures
- whether the winning path was modeled
- whether we owned enough bullets in that path
- whether dead overlap wasted entries

Evaluate errors separately:

- source error
- ownership error
- field-construction error
- game-theory error
- path-allocation error
- lineup implementation error
- ordinary variance

Do not promote a new rule from one winner. Durable learning requires repeated evidence, causal support, or an explicit experimental designation.

## 8. Deterministic Code Boundary

AI remains the strategic portfolio manager. Deterministic code should support the AI by handling:

- CSV parsing and joins
- DK player IDs
- salary/position legality
- duplicate detection
- required uniques
- player/team/stack/pitcher exposure arithmetic
- contest assignment
- lineup traceability storage
- source snapshots
- result joins
- upload-ready CSV generation

Code should not silently replace AI game-theory decisions. If a lineup fails validation, return it for strategic repair while preserving its first-place-path intent.

## Required Operating Sequence

For a serious slate, the preferred reasoning chain is:

`GitHub brain -> slate intake -> industry projection/ownership research -> market/news/weather research -> field construction model -> AI disagreement analysis -> game scripts -> first-place paths -> contest-specific bink allocation -> AI lineup construction -> dead-overlap/risk audit -> deterministic validation -> final exposure audit -> post-slate learning`

This sequence is intended to create a repeatable tournament operating system without reducing DFS to a fixed optimizer formula.
