# DFS Engine Process Governance

## Purpose

This file defines how the DFS Engine should evolve without becoming bloated, contradictory, or overfit to one slate. The repository is the canonical process brain. Chat sessions execute the process; GitHub stores durable logic.

`core/ENGINE.md` is the authoritative end-to-end operating contract. This file governs placement, promotion, deprecation, and consistency. Sport modules should contain only sport-specific mechanics and should not duplicate shared core rules.

## Process Manager Role

The process manager is responsible for keeping the Engine coherent across sports and slates. This includes:

- deciding whether a new idea belongs in core logic, a sport module, a dated learning note, or nowhere
- keeping shared logic centralized instead of duplicating it across sports
- challenging unnecessary complexity and removing redundant or stale rules
- ensuring raw source data, Engine-owned projections/ownership, Vegas/industry research, simulation, correlation, GPT/AI game-script judgment, portfolio construction, and post-slate learning connect in one repeatable flow
- preserving prior durable logic unless stronger evidence justifies changing it
- preventing one-slate results from becoming permanent rules
- making final lineup outputs operational and auditable

## Rule Placement

### Core
A rule belongs in `core/` when it generalizes across multiple sports or defines the operating system itself.

Examples:
- immutable source baselines
- Engine-owned projection and expected-ownership estimates
- mandatory industry/market and Vegas cross-checks
- simulation framework
- GPT-over-math hierarchy
- uncertainty handling
- ownership/leverage logic
- portfolio construction principles
- no arbitrary hard caps/floors
- exposure auditing
- learning/promotion rules

### Sport Module
A rule belongs in `sports/<sport>.md` when it depends on that sport's scoring, roster construction, correlation, role structure, or outcome mechanics.

Examples:
- MLB stack architecture and pitcher-vs-stack correlation
- NFL QB-pass catcher correlation
- NBA minutes/usage redistribution
- NHL line correlation
- tennis opponent negative correlation

Sport modules may reference core rules but should not restate them unless a sport-specific exception or implementation detail is necessary.

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

## Canonical End-to-End Flow

Use `core/ENGINE.md` for the detailed contract. The required sequence is:

1. Slate Intake
2. Data Validation / Official News
3. Preserve Raw Source Projection and Ownership
4. Mandatory Industry / Market / Vegas Cross-Check
5. Create DFS Engine Projection and DFS Engine Expected Ownership
6. Sport-Specific Environment / Role / Matchup Analysis
7. Native Simulation / Outcome Distribution using Engine estimates
8. Ownership / Leverage / Field Construction Analysis
9. Mathematical Candidate Lineup Generation
10. Mandatory GPT/AI Game-Script and Multi-Path Review
11. Portfolio Construction / Reshaping
12. Duplication / Hidden-Concentration / Portfolio Risk Audit
13. Audit Source vs Engine Projection, Source vs Engine Ownership, and Engine Exposure
14. Final GPT/AI Sign-Off
15. Final News / Weather / Vegas / Market Recheck
16. Rebuild if material inputs changed
17. Deliver Uploadable Lineups and Audit Files
18. Post-Slate Counterfactual and Calibration Review
19. Learning Registry Update
20. Promote, revise, deprecate, or reject durable logic only when evidence supports it

No serious build may skip the Industry/Market/Vegas layer, the Engine-owned projection/ownership layer, or the GPT/AI game-script judgment layer. If data is unavailable, the gap must be labeled rather than silently bypassed.

## Source and Engine Estimate Separation

Vendor/source numbers and DFS Engine estimates are distinct objects.

Preserve at minimum for each relevant player:

- source projection
- DFS Engine projection
- projection difference
- source projected ownership
- DFS Engine expected ownership
- ownership difference
- DFS Engine final exposure
- material adjustment drivers / uncertainty when applicable

Sim Savant is the default baseline when supplied. Source values remain unchanged for comparison. The Engine forms its own estimates from industry projections/ownership, Vegas markets, role/news, matchup/environment, sport-specific context, and calibrated simulation evidence. Do not mechanically average sources.

Downstream simulation, leverage, candidate generation, and portfolio decisions should use Engine estimates when available while retaining source values for sensitivity testing and post-slate calibration.

## Vegas / Market Requirement

Vegas is a mandatory evidence layer when relevant markets are available. Use sport-appropriate information such as:

- game totals
- moneylines / spreads
- implied team totals
- meaningful line movement
- market disagreement or uncertainty

Vegas is evidence, not truth. It must be interpreted alongside projections, news, matchup, environment, and industry context.

## Simulation Integration

Simulation is an evidence layer, not the decision-maker. The simulator should estimate outcome distributions and portfolio behavior; the Engine should decide which outcomes are strategically worth owning.

Simulation outputs should feed:

- player ceiling and failure rates
- stack/team/game outcome rates where applicable
- lineup top-1%, top-0.1%, and first-place rates when field modeling is available
- portfolio overlap and hidden concentration
- leverage analysis
- exposure decisions

Do not rank lineups solely by simulated median or raw first-place rate without considering ownership, duplication, uncertainty, contest structure, industry context, and portfolio interaction.

## GPT / AI Portfolio Authority

Math generates the candidate decision space. GPT/AI performs the mandatory strategic review above that math.

The AI pass must:

- identify multiple credible paths to first place
- challenge optimizer repetition and universal salary plugs
- distinguish true conviction from accidental mathematical concentration
- evaluate field assumptions and correlated failure paths
- preserve enough concentration to win when a thesis is right without making every lineup the same underlying bet
- reshape the portfolio when the candidate pool does not express the intended slate scripts

GPT/AI judgment must remain grounded in verified data and must not invent projections, ownership, Vegas lines, news, or simulation inputs.

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

Do not impose arbitrary hard exposure caps, floors, stack quotas, salary-spend rules, or diversification targets. Hard constraints are for site legality, contest rules, inactive players, invalid combinations, or explicit operational requirements. Use soft diagnostics to challenge concentration instead of mechanically blocking it.

## Required Deliverables

Every serious lineup build should return:

- uploadable lineup file
- major slate theses / game scripts
- key stack or correlation allocations where applicable
- source projection vs DFS Engine projection
- source projected ownership vs DFS Engine expected ownership
- DFS Engine expected ownership vs final exposure
- percentage-point differences and concise reasons for major deviations
- pre-lock/final status and unresolved uncertainty

## Post-Slate Calibration

When results arrive, separately grade:

- source projection vs Engine projection vs actual outcome
- source projected ownership vs Engine expected ownership vs actual field ownership
- simulation calibration
- Vegas/industry interpretation
- AI game-script judgment
- correlation and lineup construction
- exposure / portfolio allocation
- ordinary variance

A correct ownership estimate is still a model win if the player scores poorly. A player smashing does not automatically prove the pre-slate projection was wrong. Learn causally, not from outcome alone.

## Change Management Principle

Prefer fewer strong rules over many narrow rules. `core/ENGINE.md` owns the operating workflow; this file owns governance; sport files own sport mechanics; `core/LEARNING.md` owns learning rules. If the same rule appears in multiple places without a sport-specific reason, consolidate it rather than allowing parallel versions to drift.
