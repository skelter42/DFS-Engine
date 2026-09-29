# Claude projection pack — 2026-09-29

Worked example that led to projection model v4. The production rule is `core/PROJECTION_MODEL.md`.

```
Python pull of industry sites + book props
Both present   -> Proj = mean(industry median, de-vigged book consensus in site points)
One present    -> Proj = that one
Neither        -> Proj = Savant, unchanged
```

The pull is Python. A summarized page fetch is not the board. Own stays unchanged. Savant zeros stay 0. Savant is not a third equal vote.

## What is in this folder

| File | What it is |
|---|---|
| `DFS-Blended-Projection-Playbook.md` | Claude's NHL instructions. Useful for the no-vig math, the Poisson conversion, and the source list. Section 5 equal-weights Savant. v4 does not. |
| `nhl_blend_reference.py` | Four-game NHL script. Reads local CSVs. The production pull is `src/dfs_engine/projections/`. |
| `methodology.csv` | Sept 3 MLB market method. Dense rows are pure book consensus. |

## What carried into v4

- Pull the board in Python. Claude's pack returned on the order of 3,000 prop rows that way.
- No-vig: `p = p_over / (p_over + p_under)`.
- 1+ market to a count: `lambda = -ln(1 - p)`.
- Industry leaders and the book board both go into the one Proj.
