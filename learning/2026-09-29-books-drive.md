# 2026-09-29 — Books drive, Savant is the fallback

- Sport: all Market Inputs
- Status: validated (NHL DraftKings main the same day, user lock)
- Evidence: Python scrape, 1,523 main-slate prices. Goals, assists, shots, and points were posted and two-sided. Blocked shots were not posted and were not filled. Saves were posted for Jakub Dobes only. Goalies without a saves price go negative from win and goals against alone, so they stayed on Savant. McDavid book number 17.60 from 0.61 goals, 1.03 assists, 3.72 shots. Savant 20.56.
- Durable lesson: Every sport, the book number drives when the scoring prices are posted. Savant is the fallback, not a vote. A missing price is not filled with a rate or an industry number. Industry is a check. No Odds API. Python scrape only.
- Engine impact: `core/PROJECTION_MODEL.md`, `core/MARKET_INPUTS_RUN.md`, `core/VEGAS_CONSENSUS.md`.
- Revisit condition: a pull that posts blocked shots and saves for the goalies. Those pieces join the book number. They do not get filled before that.
