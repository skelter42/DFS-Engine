# Prompt for another agent

Paste this at the start of a Claude or ChatGPT session. Attach the Savant CSV.

---

Use the GitHub repo skelter42/DFS-Engine. Read CURRENT.md first. Then read only core/MARKET_INPUTS_RUN.md, core/PROJECTION_MODEL.md, and core/VEGAS_CONSENSUS.md. Those three are the process. If any other file disagrees, ignore that file.

This is Market Inputs, not lineups. Sport and date are in my message. The attached CSV is the Savant file.

Scrape the sportsbook prop board in Python. Do not use the Odds API. Do not use a page summary. Record the raw row count. Reject a pull whose lines do not vary by player.

Convert only posted prices. Strip the vig when both sides are posted. Do not invent the other side. Do not fill a missing market with a rate or an industry number.

Proj is the book number when the scoring prices for that player are posted. Otherwise leave Savant. A Savant 0 stays 0. Own stays unchanged. Keep Name, DFS ID, and row order.

Write the import CSV and a reconciliation that shows the book number, Savant, and the prices used. Stop.

---
