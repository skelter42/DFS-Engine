# 2026-09-29 — Vegas drives the projection

- Sport: all Market Inputs / Savant Prep
- Status: validated (user correction the same day v2 shipped)
- Evidence: v2 made Proj a 50/50 of the DFS-site median and the prop. The user said that commit got lost. The job is the prop board. An over at +150 is a probability, the book edge comes out, the books get consensus'd, and that probability becomes site points. Industry is only for a player the board does not price. Savant is only when there is no prop and no site number, and then it is left unchanged.
- Durable lesson:
  - Vegas consensus is the projection when a two-sided prop exists.
  - Do not blend a DFS site into a Vegas number.
  - Do not blend Savant into either.
  - One-sided prices and articles are not a consensus.
  - Do not invent a prop from a team total.
- Engine impact: retires v2. Canonical owner is `core/PROJECTION_MODEL.md` v3. Executable card is `core/MARKET_INPUTS_RUN.md`.
- Revisit condition: only if the user changes the order, or three logged slates show Vegas-alone losing to another estimator on absolute error.
