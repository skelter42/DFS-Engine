# Projection Model v5

One number from every board Python can scrape.

```
Non-zero Savant is an input, not just the skeleton
Industry sites that return a slate table are inputs
Prop board is an input
Projection median = median of Savant and the industry tables that have the player
Full prop board     -> Proj = mean(projection median, de-vigged book number)
Partial prop board  -> Proj = 0.70 x projection median + 0.30 x book number
No props            -> Proj = projection median
Savant 0            -> 0
```

A partial board is goals and points only. Shots, blocks, and saves were not posted, so the book number is a conversion, not a price. It does not get half the vote until those markets are scraped.

No Odds API. Python scrapes the industry pages and the prop pages. A summarized fetch is not a source.

Own stays unchanged. A season-long stat page is not a slate projection.

The executable card is `core/MARKET_INPUTS_RUN.md`.
