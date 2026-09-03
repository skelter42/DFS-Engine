# Durable Learning Registry

This registry tracks reusable DFS Engine improvements promoted from slate review into canonical knowledge.

## Promotion Standard

A learning should be promoted when it is reusable beyond one slate and supported by one or more of:

- repeated evidence across slates
- clear causal reasoning plus supporting results
- a robust portfolio-construction principle
- a process correction that prevents avoidable errors
- a user-approved permanent preference

Do not promote:

- one-off player takes
- hindsight-only winner chasing
- isolated ownership misses without a reusable cause
- stack structures merely because one slate winner used them
- raw slate data that can be regenerated

## Statuses

- `hypothesis` — plausible, not yet strong enough to alter canonical rules
- `validated` — strong enough to guide future builds
- `deprecated` — previously useful but superseded

## Entry Template

### YYYY-MM-DD — Short title
- Sport:
- Status:
- Evidence:
- Durable lesson:
- Engine impact:
- Files updated:
- Revisit condition:

## Seeded Durable Learnings

### 2026-09-03 — Multi-source projection discipline
- Sport: all
- Status: validated
- Evidence: projection-source disagreement and context changes can materially alter optimal portfolios.
- Durable lesson: never treat one projection or ownership source as authoritative; cross-check against market/context and broader industry information when available.
- Engine impact: required pre-build cross-check stage.
- Files updated: `core/ENGINE.md`, sport brains.
- Revisit condition: only if empirical tracking demonstrates a superior calibrated source/blend.

### 2026-09-03 — Exposure audit is mandatory
- Sport: all
- Status: validated
- Evidence: portfolio intent is not auditable from lineups alone.
- Durable lesson: every delivered lineup set includes source projected ownership, DFS Engine final exposure, and percentage-point difference.
- Engine impact: mandatory output contract.
- Files updated: `README.md`, `schemas/`, `core/ENGINE.md`.
- Revisit condition: none; reporting requirement remains even if ownership source changes.

### 2026-09-03 — MLB primary stack priority without overfitting
- Sport: MLB
- Status: validated
- Evidence: recent slate review reinforced the upside of complete primary stacks while also showing that lineup loss can come from secondary-stack/player-selection errors rather than primary structure itself.
- Durable lesson: prioritize coherent full primary stacks in tournaments, but diagnose misses at player, secondary-stack, pitcher, ownership, and environment levels rather than assuming stack structure was the sole cause.
- Engine impact: MLB construction and post-slate error taxonomy.
- Files updated: `sports/mlb.md`, `core/LEARNING.md`.
- Revisit condition: track by slate size and contest type.

### 2026-09-03 — Load the GitHub brain before running a slate
- Sport: all
- Status: validated
- Evidence: the chat-first workflow is intended to use GitHub as the canonical process brain, and skipping that read risks drift from the stored agent definitions and sport-specific logic.
- Durable lesson: when a user asks to run the DFS Engine, load the relevant GitHub core rules, agent definitions, sport brain, routing/config, and applicable durable learnings before slate-specific analysis.
- Engine impact: mandatory first step in every Engine run; chat memory may supplement but may not replace the canonical GitHub read.
- Files updated: `learning/REGISTRY.md`.
- Revisit condition: only if the architecture changes away from GitHub as canonical memory.

### 2026-09-03 — Distinguish projected ownership from Savant prebuild exposure
- Sport: all, especially MLB
- Status: validated
- Evidence: a player can have modest projected field ownership but be heavily concentrated in Savant's generated prebuild. Treating those as the same signal hides portfolio-level risk.
- Durable lesson: always track three separate quantities when available: source projected ownership, source/prebuild portfolio exposure, and DFS Engine final exposure. Large gaps between projected ownership and source prebuild exposure require explicit review.
- Engine impact: exposure audit and portfolio-risk passes must compare both field ownership and baseline portfolio concentration, not only ownership vs final exposure.
- Files updated: `learning/REGISTRY.md`.
- Revisit condition: none; this is a structural distinction.

### 2026-09-03 — Parse DK entry files before assuming lineup count
- Sport: all DraftKings
- Status: validated
- Evidence: DraftKings CSVs can combine live entries with embedded player-pool rows; counting all rows as entries can materially distort contest and portfolio logic.
- Durable lesson: separate actual entries from player-pool/reference rows during Intake and verify contest IDs, entry IDs, contest names, and roster fields before determining portfolio size.
- Engine impact: Slate Intake Agent must establish true entry count and contest mix before optimization or exposure calculations.
- Files updated: `learning/REGISTRY.md`.
- Revisit condition: if DraftKings changes export structure.

### 2026-09-03 — Contest types need separate portfolio logic
- Sport: all
- Status: validated
- Evidence: one slate file can contain 20-max, 5-max, and single-entry contests simultaneously; cloning one construction philosophy across them ignores payout structure, duplication risk, and acceptable variance.
- Durable lesson: partition entries by contest type before portfolio construction. Multi-entry, small-max, and single-entry builds may share slate theses but should use different concentration, uniqueness, and leverage tolerances.
- Engine impact: contest-aware portfolio builder and risk audit become mandatory whenever mixed contest types are present.
- Files updated: `learning/REGISTRY.md`.
- Revisit condition: refine thresholds with tracked ROI by contest type.

### 2026-09-03 — Prelock and final-lock are distinct Engine states
- Sport: MLB
- Status: validated
- Evidence: MLB batting-order confirmation can materially change role, plate appearances, stack connectivity, ownership, and value; a strategically sound prelock build may still be invalid as a final upload.
- Durable lesson: label MLB outputs PRELOCK until required starting lineups/news checks are complete. Finalization requires rerunning News & Role, projection adjustments, stack architecture, portfolio risk, and exposure audit after meaningful lineup changes.
- Engine impact: prevents premature 'final' labels and forces a last-mile rerun when official orders matter.
- Files updated: `learning/REGISTRY.md`.
- Revisit condition: none for MLB classic slates.

### 2026-09-03 — Projection sacrifice must purchase a strategic edge
- Sport: all GPPs
- Status: validated
- Evidence: game-script diversification can improve first-place paths even when it lowers median projection, but arbitrary low-projection diversification is not useful.
- Durable lesson: accept projection loss only when it buys identifiable leverage, correlation, uniqueness, script coverage, or reduced hidden portfolio concentration. Every material projection sacrifice should have a named strategic reason.
- Engine impact: Portfolio Builder and Risk Manager must explain the tradeoff between median projection and first-place equity rather than treating lower ownership as automatically better.
- Files updated: `learning/REGISTRY.md`.
- Revisit condition: calibrate acceptable projection-loss bands by contest type as results accumulate.
