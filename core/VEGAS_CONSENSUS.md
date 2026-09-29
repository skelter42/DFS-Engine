# Book layer of the blend

This is the sportsbook half of `core/PROJECTION_MODEL.md`. It is not the whole Proj when an industry number also exists.

Sources: DraftKings, FanDuel, BetMGM, plus any other book the Python pull returns. One price from each that posts the player. Median them.

Plus price: `100 / (odds + 100)`. +200 is 33%.

Minus price: `odds / (odds + 100)`. −150 is 60%.

A Kalshi yes price is already the probability. 40 cents is 40%.

Both sides: strip the vig, `p = p_over / (p_over + p_under)`. One side: still convert.

The probability is the expected count. Multiply by the site points for that event and add the pieces. A goal is 8.5. A shot is 1.6. An assist is 5. A save is 0.7. A strikeout is 2. An inning is 2.25.

Pull this layer in Python (`src/dfs_engine/projections/pull.py`). A summarized fetch is not a price.
