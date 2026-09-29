# Market Inputs — Run Card

Same steps every sport. Inputs are the sport, the date, and the Savant file.

1. Keep Name, DFS ID, row order, Own.
2. Savant 0 stays 0. Do not research those rows.
3. Scrape the sportsbook prop board in Python. No Odds API. No page summary. Write the raw rows and record the count. Reject the pull if the lines do not vary by player.
4. Convert only posted prices. Strip the vig when both sides are posted. One side: convert that side, do not invent the other. A missing market stays missing.
5. Proj is the book number when the scoring markets for that player are posted. Otherwise Savant. A goalie without a saves price is not a book projection.
6. Write the import CSV. Preserve Name, DFS ID, row order, Own, and all other original columns; change only Proj where the book number qualifies. Savant 0 stays 0.
7. Write a row-by-row reconciliation showing Name, DFS ID, original Savant Proj, book number (blank when unavailable), final Proj, books / savant-fallback / zero status, and the exact posted prices used (book, player, market, line, side, odds, source URL, and pull timestamp). Include the raw row count, rejected-pull reason if applicable, and books / savant-fallback / zeros counts. Do not manufacture a book number for missing markets. Savant is the comparison column, not a vote.
8. Stop after the import CSV and reconciliation. Do not build lineups.

Read `core/PROJECTION_MODEL.md` and `core/VEGAS_CONSENSUS.md`. Files under `reference/` are examples. Do not run them.
