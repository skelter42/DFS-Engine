# 2026-09-29 — Industry median, Vegas band

- Sport: all Market Inputs / Savant Prep
- Status: validated (user-directed process lock)
- Evidence: An equal-vote median lets a pile of similar public pages outvote a posted prop. A fixed Savant weight pulls the number back toward the import file. The user asked for a repeatable process that keeps the outlier protection and lets the market correct a player the industry is collectively wrong on.
- Durable lesson:
  - Lock role before the number. Confirmed out stays 0.
  - Convert to site scoring, then collapse copied families to one vote.
  - Tier A votes if three or more exist. Tier B fills gaps only.
  - Industry candidate is the median of the votes that remain.
  - Vegas is one de-vigged, site-converted number. The band is that number ± the larger of 1.5 site points or 12% of it.
  - Inside the band, keep the industry median. Outside, pull to the nearest edge. No converted prop: industry median stands.
  - Savant does not vote when any usable industry vote exists.
  - Do not refit the band width off one slate.
- Engine impact: replaces the equal-vote median lock. Canonical owner is `core/MARKET_PROJECTIONS.md`. Executable card is `core/MARKET_INPUTS_RUN.md`.
- Revisit condition: change the estimator only if, over a real sample, the band-pulled median loses to either layer alone on absolute error.
