# Projection Model v6

Books drive. Savant is the fallback. Every sport.

- Python scrape of a real sportsbook board.
- Two-sided scoring markets: Proj is the de-vigged book number, in site points.
- One-sided scoring markets: Proj may use a one-sided implied estimate; vig is retained.
- Required scoring markets missing: Proj is Savant, unchanged.
- Savant 0 stays 0.

De-vigging applies only when both sides of the same market are posted. A one-sided quote may be converted from the posted side, but its implied probability remains vig-included. For an Under-only quote, the Over complement is only a proxy; it is not a de-vigged or fair Over probability. Label one-sided estimates in the reconciliation and do not silently combine them with paired-side de-vigged prices. A push-capable whole-number line remains unavailable unless a push-aware solve is supported.

A scoring market is a posted price for a stat that scores. Goals, assists, shots, blocks, saves, wins, goals against, strikeouts, outs, yards, receptions. If the price is not in the pull, that piece is missing. Do not fill it with a rate, a season average, or an industry number.

Industry sites are a check. They are not a vote.

No Odds API. A summarized page fetch is not a price. Record the raw row count. Reject a pull whose lines do not vary by player.

Own stays unchanged.

Confirmed 2026-09-29, NHL DraftKings main, four games. Python pull, 1,523 prices. Goals, assists, shots, and points were posted, two-sided, DraftKings, FanDuel, BetMGM, theScore. Blocked shots were not posted, so they were not filled. Saves were posted for one goalie. Goalies without a saves price stayed on Savant, because win and goals against alone go negative. McDavid: 0.61 goals, 1.03 assists, 3.72 shots, book number 17.60, Savant 20.56.

The executable card is core/MARKET_INPUTS_RUN.md. Conversion is core/VEGAS_CONSENSUS.md.
