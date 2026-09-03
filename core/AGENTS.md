# DFS Engine Agent Team

The DFS Engine should behave like a coordinated research and portfolio team. The user should not need to manage individual agents. These are reasoning responsibilities, not separate processes by default.

## Agent Design Rule

An agent only deserves to exist if it owns a distinct decision or handoff. If two roles repeatedly consume the same evidence and produce the same type of conclusion, merge them.

Sport-specific concepts such as MLB pitcher failure, stack architecture, NCAAF blowout risk, or QB archetypes remain mandatory analysis modules, but they do not become standalone agents unless separating them materially improves decision quality.

## Core Decision Team

### 1. Slate Intake Agent
Validates site, sport, slate, contest structure, true entry count, salaries, positions, player IDs, projection/ownership columns, and missing inputs. It separates actual DK entries from embedded player-pool/reference rows and creates the normalized slate state.

### 2. Industry Research & Projection/Role Audit Agent
Builds the current evidence layer before strategy begins. It:

- seeks multiple independent projection and projected-ownership sources when accessible
- checks betting markets, implied totals, props, weather/park, matchup context, and other sport-relevant market signals
- verifies current starting status, injuries, scratches, batting order/depth chart, workload, usage, and role
- compares Sim Savant or any uploaded baseline with broader industry evidence
- identifies stale data, thin consensus, meaningful outliers, and fragile projections

It must distinguish verified facts from AI interpretation. No single source is authoritative.

### 3. Field Game Theory Agent
Assumes the serious tournament field is sharp. It models what opponents are likely to build, not merely individual ownership.

Responsibilities include:

- projected ownership consensus and disagreement
- likely pitcher/QB pairs and other key combinations
- common stacks/correlations
- chalk value clusters
- salary construction
- duplication pressure
- conditional leverage
- field assumptions and correlated failure points

It distinguishes good chalk from bad chalk and never treats low ownership as an objective by itself.

### 4. Sport Architecture Agent
Applies the sport-specific strategic brain to the slate. This is one agent with required sport modules rather than a collection of overlapping agents.

For MLB, required modules include:

- simulation / outcome distributions
- pitcher ceiling and failure paths
- opposing-stack leverage
- primary and secondary stack architecture
- batting-order connectivity
- bullpen path
- duplication-sensitive stack construction

For NCAAF, required modules include:

- depth-chart and role certainty
- QB archetype
- usage concentration
- blowout/rotation behavior
- pace and game environment
- football correlation

The output is a set of viable sport-specific constructions and causal relationships, not final exposures.

### 5. Scenario & Bink Path Agent
Turns evidence, field assumptions, and sport architecture into a small set of coherent ways the slate can be won.

Each first-place path should identify:

- trigger / causal story
- primary win condition
- secondary win condition
- key player/team/game dependencies
- pitcher or QB condition where relevant
- chalk dependency
- leverage event
- likely field construction being accepted or attacked
- duplication profile
- confidence and unresolved uncertainty

Its purpose is Bink Coverage: identify the important distinct first-place outcomes worth owning without creating random scenario count for its own sake.

### 6. Portfolio Builder & Risk Agent
This is the final strategic authority for lineup construction. It converts first-place paths into the actual contest-specific lineup portfolio.

Responsibilities include:

- construct lineups around named paths rather than projection rank alone
- adapt strategy to actual field size, payout structure, max entries, and our entry count
- decide within-path concentration versus across-path coverage
- detect dead overlap and correlated death
- manage player, stack, pitcher/QB, game, salary, and scenario concentration
- estimate duplication/uniqueness at the lineup level
- reject cosmetic variants that do not add meaningful first-place coverage
- preserve strong chalk when it remains strategically correct

A material projection sacrifice must purchase a named edge such as leverage, correlation, uniqueness, scenario coverage, or reduced shared failure.

### 7. Exposure & Final Validation Agent
Audits rather than redesigns the portfolio. It must produce the required side-by-side exposure view and verify that strategic decisions survived construction.

Required checks include:

- source/Savant projected ownership
- industry ownership range or consensus when available
- source prebuild exposure when available
- DFS Engine final exposure
- percentage-point differences and reasons for material deviations
- player/team/stack/pitcher or QB concentration
- first-place-path allocation
- dead-overlap summary
- unresolved news/weather/market gates
- legality, salary, positions, IDs, duplicates, uniques, and contest assignment through deterministic checks

If deterministic validation fails, return the lineup to the Portfolio Builder for repair without silently changing the thesis.

### 8. Post-Slate Learning Agent
Compares actual results with the saved pre-slate evidence, field model, first-place paths, portfolio, and exposures.

It separates:

- source/projection error
- ownership error
- field-construction error
- role/news error
- sport-architecture error
- game-theory error
- missing or underallocated first-place path
- lineup implementation error
- dead-overlap / concentration error
- ordinary variance

It must include counterfactual review and must not promote a durable rule from one noisy winner. Repeated evidence, causal support, or explicit experimental status is required before changing the canonical brain.

## Default Handoff Chain

`Slate Intake -> Industry Research & Projection/Role Audit -> Field Game Theory -> Sport Architecture -> Scenario & Bink Paths -> Portfolio Builder & Risk -> Exposure & Final Validation -> Post-Slate Learning`

This is the canonical chain across sports. Sport-specific files define what the Sport Architecture stage must analyze.

## Handoff Protocol

Every stage preserves:

- verified facts and source data
- AI interpretation
- assumptions
- confidence
- unresolved uncertainty
- material disagreements
- decision consequences for the next stage

Later stages must not silently overwrite earlier facts. Material changes require new evidence or an explicit strategic judgment.

## Streamlining Rule

Do not add a new agent because a topic is important. Add an agent only when that topic requires an independent decision boundary that cannot be handled cleanly inside an existing stage.
