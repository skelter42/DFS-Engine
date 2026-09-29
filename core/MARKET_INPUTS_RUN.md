# Market Inputs — Run Card

Same steps every slate. Inputs are the sport, the date, and the Savant file.

1. Keep Name, DFS ID, row order, Own.
2. Savant 0 stays 0. A non-zero Savant number is a projection input.
3. Scrape industry projection pages in Python. Keep every site that returns a slate table in DraftKings points. A paywall or a season-long page is not a source.
4. Scrape the prop board in Python. No Odds API. Record the row count. Reject a pull whose lines do not vary by player.
5. Projection median of Savant and the industry tables. Books join at half only if shots, blocks, and saves were posted. Otherwise books are 30 percent.
6. Report blend / projections-only / zeros.
7. Stop. Do not build lineups.

Read `core/PROJECTION_MODEL.md`. Files under `reference/` are examples. Do not run them.
