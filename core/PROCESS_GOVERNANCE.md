# DFS Engine Process Governance

## Purpose

This file governs how the DFS Engine evolves without becoming bloated, contradictory, stale, or overfit.

Authoritative ownership:
- `core/ENGINE.md` = canonical end-to-end operating contract
- `core/AGENTS.md` = ownership of reasoning stages and handoffs
- `core/MARKET_PROJECTIONS.md` = shared market-derived projection framework
- `core/SIMULATION.md` = shared simulation framework
- `core/LEARNING.md` = post-slate learning and calibration rules
- `sports/<sport>.md` = sport-specific mechanics only
- `learning/` = hypotheses and not-yet-promoted findings

No other file should independently redefine the full workflow.

## Process Manager Role

The process manager keeps the Engine coherent across sports and slates by:
- placing new logic in the correct owner file
- merging duplicate rules instead of adding parallel versions
- removing stale or contradictory instructions
- preserving source-vs-derived data separation
- preventing one-slate outcomes from becoming permanent rules
- keeping the operating system simple enough to execute reliably in chat
- ensuring every serious build reaches an auditable final portfolio

## Rule Placement

### Core
Store a rule in `core/` when it generalizes across sports or defines the operating system.

Examples:
- source immutability
- market-derived projection methodology
- Engine-owned expected ownership
- simulation principles
- GPT-over-math authority
- portfolio construction principles
- no arbitrary hard caps/floors
- audit contracts
- learning/promotion rules

### Sport Module
Store a rule in `sports/<sport>.md` only when it depends on sport scoring, roster mechanics, role structure, correlation, or outcome mechanics.

Examples:
- MLB prop-to-DK stat conversion, stack architecture, pitcher-vs-stack leverage
- NFL/NCAAF QB/pass-catcher correlation
- NBA minutes/usage redistribution
- NHL line/power-play correlation
- tennis opponent negative correlation

Sport modules should reference core policy rather than restating it.

### Learning Registry
Store a finding in `learning/` when it is plausible and worth tracking but not strong enough to become permanent logic.

### Do Not Store
Do not persist:
- raw slate opinions
- one-off player takes
- complete chat transcripts
- noisy outcome-driven conclusions
- duplicated restatements of existing rules
- optimizer artifacts that do not generalize

## Promotion Standard

Promote a rule into durable logic only when at least one is true:
1. it is structurally true because of scoring, DFS rules, correlation, contest mechanics, or probability;
2. it is supported repeatedly across slates;
3. it materially improves backtests or forward tests without merely fitting past winners;
4. it fixes a clear recurring process failure.

Single-slate evidence should normally create a hypothesis, not a permanent rule.

## Deprecation / Merge Standard

Merge, reduce, or remove a rule when it:
- duplicates another rule
- conflicts with stronger evidence
- adds complexity without changing decisions
- creates rigid behavior where slate-dependent judgment is needed
- came from narrow or noisy evidence
- causes multiple files or agents to own the same decision

Preserve the reason in Git history; do not leave deprecated wording beside the replacement.

## Single-Source Architecture

The Engine must avoid policy duplication.

When adding or revising logic:
1. identify the canonical owner file;
2. update that file;
3. replace duplicate wording elsewhere with a short reference if needed;
4. verify no contradictory version remains;
5. prefer one clear rule over several near-equivalent rules.

If two agents appear to solve the same problem, merge their responsibilities unless the separation produces a genuinely distinct output.

## Canonical Operating Sequence

Do not maintain a second detailed workflow here. Execute the sequence in `core/ENGINE.md` using ownership defined in `core/AGENTS.md`.

At a high level only:

**validated slate data -> market/Engine projection -> Engine expected ownership -> simulation/scenarios -> sport/game-script strategy -> candidate generation -> GPT portfolio construction -> risk/exposure audit -> final live-data check -> delivery -> post-slate learning**

Material late news or market movement loops back to the affected upstream stage and all dependent outputs.

## Market-First Projection Governance

The preferred projection hierarchy is now market-first when sufficient player-level props exist.

- Use multi-book player props to derive expected fantasy scoring when coverage is strong.
- De-vig and aggregate markets robustly rather than trusting one book.
- Translate expected stat events into site scoring using sport-specific rules.
- Assign a market coverage/confidence grade.
- When coverage is sparse, shrink toward an independent prior such as vendor/industry projection plus verified role/context.
- Never manufacture missing prop information.
- Keep source/vendor projections immutable for comparison and sensitivity testing.

Detailed methodology belongs only in `core/MARKET_PROJECTIONS.md` and sport modules.

## Projection, Ownership, Exposure Separation

These are three different objects and must never be conflated:

1. **DFS Engine Projection** = what the player is expected to score.
2. **DFS Engine Expected Ownership** = what the field is expected to do.
3. **DFS Engine Exposure** = what our portfolio chooses to do.

Projection feeds simulation. Expected ownership feeds leverage/field modeling. Exposure is the final portfolio decision after game theory and correlation.

## GPT-over-Math Governance

Math and simulations define plausible outcomes and generate candidates. GPT/AI has final portfolio authority, but only as a grounded strategic layer.

GPT/AI should challenge:
- hidden concentration
- universal salary/value plugs
- repeated optimizer constructions
- duplicated game-script families
- fragile chalk assumptions
- portfolios that contain many lineups but only one underlying bet

GPT/AI must not invent data or override strong evidence with unsupported narrative.

## Portfolio Governance

A portfolio should contain multiple credible paths to first while retaining enough concentration to profit meaningfully when a thesis is correct.

Do not impose arbitrary hard exposure caps/floors, stack quotas, team quotas, salary-spend rules, or cosmetic diversification targets. Use soft diagnostics and portfolio comparisons. Hard constraints are reserved for site legality, contest rules, confirmed inactive players, invalid combinations, or explicit user requirements.

## Required Audit Contract

Every serious lineup build must preserve enough data to report:

| Player | Source Projection | DFS Engine Projection | Projection Diff | Source Projected Ownership | DFS Engine Expected Ownership | Ownership Diff | DFS Engine Exposure |
|---|---:|---:|---:|---:|---:|---:|---:|

When the user explicitly asks for a file-only exposure or stack report, calculate directly from the delivered lineup file and do not add unrelated comparison layers.

## Post-Slate Governance

Use `core/LEARNING.md` for detailed learning rules. At minimum separate:
- projection calibration
- ownership calibration
- market interpretation
- simulation calibration
- sport/game-script judgment
- correlation/construction
- duplication/portfolio allocation
- ordinary variance

A good outcome does not automatically validate the process, and a bad outcome does not automatically invalidate it.

## Change Management Principle

Prefer fewer strong rules over many narrow rules. The Engine should become easier to execute and audit as it learns, not merely longer.
