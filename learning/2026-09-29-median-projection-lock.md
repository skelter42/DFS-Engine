# 2026-09-29 — Proj is the median, not a weighted mean

- Sport: all Market Inputs / Savant Prep
- Status: validated (user-directed process lock)
- Evidence: The 2026-09-28 card made the composite the only projection object, but left the blend as a menu. MLB override and future-iteration files still used fixed means and a Savant prior weight. The user asked for the best median projection, then asked for that estimator to be published.
- Durable lesson:
  - Convert every source to the target site scoring before any blend.
  - Collapse copied families to one vote. A consensus and a reprint are not two sources. Component-only cites do not count as a vote unless they convert to a full site projection.
  - Vegas contributes at most one vote: the de-vigged multi-book expectation, converted once. Books do not each vote. Game total / team total is the reconciliation check.
  - Proj is the median of the remaining votes. Even count: mean of the two central votes. One external vote: that vote. None: Savant fallback.
  - Savant does not vote when any usable external vote exists.
  - If the medians imply a game total the board rejects, drop or haircut the offending vote and recompute. Do not switch to a weighted mean.
  - Zeros stay 0. Own stays unchanged unless an ownership pass is requested.
  - Do not refit this off one slate.
- Engine impact: retired the MLB `0.40 / 0.40 / 0.20` and `0.40 / 0.32 / 0.28` weights. Canonical owner is `core/MARKET_PROJECTIONS.md`. Executable card is `core/MARKET_INPUTS_RUN.md`.
- Revisit condition: change the estimator only if locked medians are systematically worse than both layers alone on absolute error across a real sample.
