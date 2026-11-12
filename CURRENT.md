# Current process — read this first

Projection model v6. Every sport. This file wins if another file disagrees.

- Python scrape of a real sportsbook board.
- Two-sided scoring markets: Proj is the de-vigged book number, in site points.
- One-sided scoring markets: Proj may use a one-sided implied estimate; vig is retained.
- Required scoring markets missing: Proj is Savant, unchanged.
- Savant 0 stays 0.

De-vigging applies only when both sides of the same market are posted. A one-sided quote may be converted from the posted side, but its implied probability remains vig-included. For an Under-only quote, the Over complement is only a proxy; it is not a de-vigged or fair Over probability. Label one-sided estimates in the reconciliation and do not silently combine them with paired-side de-vigged prices. A push-capable whole-number line remains unavailable unless a push-aware solve is supported.

Books drive. Savant is the fallback, not a vote. A missing price is not filled with a rate, a season average, or an industry number. Industry is a check. No Odds API. A page summary is not a source. Own stays unchanged. Write the import CSV and a reconciliation showing the book number, original Savant projection, exact posted prices, and price treatment used. Then stop. Do not build lineups unless asked.

Read next:

1. core/MARKET_INPUTS_RUN.md
2. core/PROJECTION_MODEL.md
3. core/VEGAS_CONSENSUS.md

Do not follow v3, v4, or v5. Do not follow an industry blend, a 50/50, a 70/30, or equal-weight Savant. Do not run anything in reference/.
