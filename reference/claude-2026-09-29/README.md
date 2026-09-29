# Claude projection pack — 2026-09-29

External reference. Not the production model.

Production stays projection model v3 (`core/PROJECTION_MODEL.md`, `core/VEGAS_CONSENSUS.md`):

```
Props exist  -> Proj = multi-book de-vigged consensus, in site points
No props     -> Proj = DFS-site median
Neither      -> Proj = Savant, unchanged
```

Do not equal-weight Savant or a DFS site into a Vegas number. Own stays unchanged. Savant zeros stay 0.

## What is in this folder

| File | What it is |
|---|---|
| `DFS-Blended-Projection-Playbook.md` | Claude's NHL blend instructions (2026-09-29). Equal-weight mean of Sim Savant, Daily Fantasy Fuel, and a props-implied number. Conflicts with v3 on the blend weights. |
| `nhl_blend_reference.py` | Reference implementation of that playbook. Four-game NHL slate. |
| `Blend-Audit-09-29-2026.csv` | Audit from that run. `Own` was left unchanged. Biggest SS deltas: McDavid −2.15, Draisaitl −2.24, Eichel −2.28, Stone −2.22. |
| `summary.csv`, `hitter-projections.csv`, `pitcher-projections.csv`, `methodology.csv` | Sept 3, 2026 DK MLB market workbook, exported from the xlsx. 108 hitters (9 per team by book-market observation count) and 12 starters. |

The original xlsx was not committed (binary). The four CSVs are the sheets.

## What is usable

- No-vig: two-way `p = p_over / (p_over + p_under)`. American odds: `+X → 100/(X+100)`, `−X → X/(X+100)`.
- 1+ market to a count: `λ = −ln(1 − p)`.
- NHL DK conversion in the playbook (goals, assists, SOG, blocks, Poisson bonus tails) and the goalie saves solve.
- Audit shape: one row per player, every input, final number, delta vs the base file.
- MLB workbook method is closer to v3. When book-market observations are dense, `Market Weight = 1` and `DK Projection = Raw Market DK`. Sparse rows (under 35 observations) are blended toward a role prior. That prior blend is not v3.
- MLB hitter scoring in the workbook: `3×1B + 5×2B + 8×3B + 10×HR + 2×R + 2×RBI + 2×(BB+HBP) + 5×SB`.
- MLB pitcher scoring in the workbook: `2×K + 0.75×outs − 0.6×hits − 0.6×walks − 2×ER`.

## What is not production

- Playbook section 5 (equal-weight SS + each service + props) is retired relative to v3.
- Rescaling props to the services' mean and standard deviation changes the level of the board. v3 keeps the de-vigged consensus in site points and does not rescale it onto Savant.
- One-sided hold factors in the playbook (0.87 anytime-goal, 0.92 points O0.5) are a Claude assumption, not a locked engine constant.
- The Sept 3 workbook's robust prior (75% lineup-slot median, 25% winsorized DK average) is a coverage fallback, not the v3 fallback. v3 fallback is the DFS-site median, then Savant unchanged.
