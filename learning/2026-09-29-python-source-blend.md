# 2026-09-29 — Python pull, then blend industry and the books

- Sport: all Market Inputs / Savant Prep
- Status: validated (user instruction the same day)
- Evidence: Claude's pack got a usable projection by taking industry projection leaders and sportsbook props. The pull that worked was Python, on the order of 3,000 prop rows. A summarized page fetch does not return that board.
- Durable lesson: Market Inputs runs in Python. Industry numeric sites and the de-vigged book board are co-primary. Both present: mean of the industry median and the book consensus, in site points. One present: that one. Neither: Savant, unchanged. Savant 0 stays 0. Own stays unchanged. Do not treat a chat summary of a prop page as the board.
- Engine impact: replaces the Vegas-only v3 card. Owner is `core/PROJECTION_MODEL.md`. Pull is `src/dfs_engine/projections/`.
- Revisit condition: only if a logged slate shows the blend losing to Vegas-alone or industry-alone on absolute error.
