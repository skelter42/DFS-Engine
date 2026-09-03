# DFS Engine Process Governance

## Purpose

This file defines how the DFS Engine should evolve without becoming bloated, contradictory, or overfit to one slate. The repository is the canonical process brain. Chat sessions execute the process; GitHub stores durable logic.

## Process Manager Role

The process manager is responsible for keeping the Engine coherent across sports and slates. This includes:

- deciding whether a new idea belongs in core logic, a sport module, a dated learning note, or nowhere
- keeping shared logic centralized instead of duplicating it across sports
- challenging unnecessary complexity and removing redundant rules
- ensuring simulation, market research, ownership, correlation, game theory, portfolio construction, and post-slate learning connect in one repeatable flow
- preserving prior durable logic unless stronger evidence justifies changing it
- preventing one-slate results from becoming permanent rules
- making final lineup outputs operational and auditable

## Rule Placement

### Core
A rule belongs in `core/` when it generalizes across multiple sports or defines the operating system itself.

Examples:
- source triangulation
- simulation framework
- uncertainty handling
- ownership/leverage logic
- portfolio construction principles
- exposure auditing
- learning/promotion rules

### Sport Module
A rule belongs in `sports/<sport>.md` when it depends on that sport's scoring, roster construction, correlation, role structure, or outcome mechanics.

Examples:
- MLB 5-man stacks
- NFL QB-pass catcher correlation
- NBA minutes/usage redistribution
- NHL line correlation
- tennis opponent negative correlation

### Learning Registry / Dated Notes
A finding belongs in `learning/` when it is potentially useful but not yet strong enough to become permanent logic.

### Do Not Store
Do not store raw slate opinions, one-off player takes, isolated winner constructions, or conclusions based only on a single outcome unless they are needed as evidence for later review.

## Promotion Standard

A new rule should be promoted into durable logic only when at least one of the following is true:

1. It is structurally true because of DFS rules, scoring, correlation, contest mechanics, or basic probability.
2. It is supported by repeated evidence across multiple slates.
3. It materially improves backtested or forward-tested portfolio quality without simply fitting past winners.
4. It fixes a clear process failure that would recur if left unchanged.

Single-slate evidence should usually create a hypothesis, not a permanent rule.

## Deprecation Standard

Rules should be reduced, merged, or removed when they:

- duplicate another rule
- conflict with stronger evidence
- add complexity without changing decisions
- are too rigid for changing slate conditions
- were learned from noise or narrow samples
- encourage optimizer-like behavior that weakens game-script or portfolio reasoning

When removing a rule, preserve the reason in version history rather than leaving contradictory instructions elsewhere.

## Standard End-to-End Flow

1. Slate Intake
2. Data Validation
3. Projection Audit
4. Official News / Role Verification
5. Market and Industry Cross-Check
6. Sport-Specific Environment Analysis
7. Native Simulation / Outcome Distribution
8. Ownership / Leverage / Field Construction
9. Correlation and Game-Script Thesis Board
10. Candidate Lineup Generation
11. Duplication / Uniqueness Review
12. Portfolio Construction and Script Allocation
13. Portfolio Risk Audit
14. Source Ownership vs Engine Exposure Audit
15. Final News / Weather / Lineup Recheck
16. Deliver Uploadable Lineups and Audit Files
17. Post-Slate Counterfactual Review
18. Learning Registry Update
19. Promote, revise, or reject durable logic only when evidence supports it

## Simulation Integration

Simulation is an evidence layer, not the decision-maker. The simulator should estimate outcome distributions and portfolio behavior; the Engine should decide which outcomes are strategically worth owning.

Simulation outputs should feed:

- player ceiling and failure rates
- stack/team/game outcome rates where applicable
- lineup top-1%, top-0.1%, and first-place rates when field modeling is available
- portfolio overlap and hidden concentration
- leverage analysis
- exposure decisions

Do not rank lineups solely by simulated median or raw first-place rate without considering ownership, duplication, uncertainty, contest structure, and portfolio interaction.

## Source Hierarchy

No projection or ownership source is authoritative. The Engine should triangulate:

- Sim Savant baseline data when provided
- broader industry projections/ownership where available
- betting markets and implied environments
- official role/news information
- sport-specific matchup/context data
- native simulation outputs

Disagreement between sources is information. Large disagreements should trigger review rather than automatic averaging.

## Portfolio Governance

A lineup portfolio should represent a controlled set of distinct slate theses. Different lineups that depend on the same underlying outcome count as concentrated exposure even when the player combinations differ.

Audit concentration by sport-appropriate dimensions such as:

- player
- team/stack
- game environment
- pitcher/QB/goalie pairing
- salary construction
- chalk combination
- game-script family
- simulation outcome dependency

The goal is enough concentration to profit when a thesis is correct, without accidentally making every lineup the same bet.

## Required Deliverables

Every serious lineup build should return:

- uploadable lineup file
- major slate theses / scripts
- key stack or correlation allocations where applicable
- source projected ownership vs DFS Engine exposure with percentage-point differences
- explanation of the largest intentional deviations
- pre-lock/final status and unresolved uncertainty

## Change Management Principle

Prefer fewer strong rules over many narrow rules. The Engine should become more capable over time, not merely longer.
