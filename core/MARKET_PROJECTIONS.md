# Market-Derived DFS Projections

## Purpose

The DFS Engine produces a **composite projection** as the source of truth for expected fantasy scoring.

A composite projection is built from:
1. **Multi-book Vegas / sportsbook player props and game markets** (primary)
2. **Multiple independent industry projection leaders** (active cross-check and gap-fill)
3. **Sim Savant / vendor projection** only as the final fallback when both market and industry coverage are genuinely insufficient

The goal is to stop trusting any single projection source. The final `Proj` value that is returned to Sim Savant is the composite number, not the original Savant number and not a single sportsbook line.
