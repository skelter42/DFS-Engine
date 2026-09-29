# Book projection

This is the projection. Savant is the fallback when this layer is missing, not a second vote.

## Pull

Python scrape of a real sportsbook. DraftKings, FanDuel, BetMGM, plus any other book the pull returns. One price from each book that posts the player. Median the books.

No Odds API. A summarized fetch is not a price. A season-long page is not a slate price.

## Price

Plus price: `100 / (odds + 100)`. +200 is 33%.

Minus price: `odds / (odds + 100)`. −150 is 60%.

Both sides: `p = p_over / (p_over + p_under)`. One side: use the posted side. Do not invent the other side.

A 0.5 line is a 1+ market. Expected count = `-ln(1 - p)`. A higher line is solved so the Poisson probability of clearing that line equals p.

## Site points

Multiply the expected count by the site points for that stat. Add the pieces that were actually priced.

NHL skater, DraftKings: 8.5 per goal, 5 per assist, 1.5 per shot, 1.3 per block. Blocks only if a blocked-shot price was posted. Bonuses are the Poisson chance of 3+ goals, 3+ points, 5+ shots, and 3+ blocks, 3 points each, and only for a stat that was priced.

NHL goalie, DraftKings: 6 times win probability, minus 3.5 times opponent implied goals, plus 0.7 per save. Win comes from the de-vigged moneyline. Goals against come from the opponent implied total. No saves price: do not write the number. It goes negative. Savant stays.

Other sports use the same rule and that sport's scoring. A strikeout is 2 on DraftKings MLB. An out is 0.75. Do not borrow another sport's point value.

## Confirmed

2026-09-29 NHL main. 1,523 prices. Shots, assists, goals, points posted. Blocked shots not posted. Saves posted for Jakub Dobes only. McDavid book number 17.60 from 0.61 goals, 1.03 assists, 3.72 shots.
