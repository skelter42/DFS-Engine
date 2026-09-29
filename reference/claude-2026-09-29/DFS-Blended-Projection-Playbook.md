> Status: reference only. Do not use section 5 blend weights. Production is projection model v3: a two-sided prop is the projection, a DFS site is the fallback, Savant is last and unchanged. See README.md in this folder.

# DFS Blended Projection Playbook

**What this is:** instructions for an AI assistant to take one DFS projection file (e.g., Sim Savant export), cross-check it against other projection services and sportsbook props, and return a corrected **blended** projection file in the **same format**. First built for NHL on DraftKings (9/29/2026). The steps apply to any sport; sport-specific notes are in section 6.

---

## 1. Inputs and output

- **Input:** base projection CSV (Sim Savant format: `Name, DFS ID, Proj, Own`). Rows with `Proj = 0.00` are players the base source considers out or not playing.
- **Output 1 (upload file):** identical columns, identical row order, identical DFS IDs. Only `Proj` changes. `Own` is untouched.
- **Output 2 (audit file):** one row per player with every input: base proj, each other service, prop-implied numbers, final blend, and the delta against the base.
- **Always verify:** same row count, names and IDs match row by row, no null projections.

## 2. Workflow

1. **Identify the slate.** Confirm the date, the games, and whether it's regular season or preseason (preseason has few or no props). Check the salary file / DFS IDs for late additions (new IDs often mean a same-day trade or signing).
2. **Pull other projection services** (at least one, ideally 2–3). Record team and position from them, since the base file may not include those.
3. **Pull Vegas game lines** for every game: moneylines and totals. Remove the vig (see section 4) and convert to win probability and implied team totals.
4. **Pull the player prop boards.** Use every market available (see section 6 for each sport). Prefer two-way markets (over and under) so the vig can be removed properly.
5. **Check news** for injuries, scratches, confirmed starters, trades, and projected lineups. Override any source that's stale: an OUT player is 0 regardless of what a service says.
6. **Build the props-implied projection** for each player (section 4).
7. **Blend** (section 5), write both files, verify, and deliver.
8. **Flag in the summary:** the biggest disagreements between sources, any news overrides, risky players (e.g., a pending trade or immigration paperwork), and data you couldn't get.

## 3. Sources and access notes

### Projection services
| Source | Access | Notes |
|---|---|---|
| Daily Fantasy Fuel `dailyfantasyfuel.com/{sport}/projections/draftkings` | Free, full table | Best free source. The fetch tool truncates, so request rows in chunks (1–20, 21–90, 91–end). Can be stale on late scratches and same-day trades. |
| RotoWire, Stokastic, LineStar, FantasyData, 5v5 Hockey, SaberSim | JS-loaded or paywalled | Couldn't be scraped. Use only if the user exports a CSV. |

### Props
| Source | What worked | Caveats |
|---|---|---|
| **Covers** `covers.com/sport/{sport-path}/player-props` → per-game `covers.com/sport/{...}/matchup/{id}/odds` | Anytime-goal (or the equivalent) + Points O0.5 for nearly every player, over/under, best price across books | Some sections (SOG, assists, saves, blocks) are collapsed and unreadable. Stale injured or traded players are still listed. Watch for mixed-up players with the same or similar names. |
| **DraftKings Sportsbook JSON** `sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/{leagueId}` then `/categories/{cat}/subcategories/{sub}` | Event list, goalie saves O/U were reliable | Only reachable through a web-fetch tool that summarizes, not raw. Some feeds came back garbled (every SOG line showing 1.5, odds changing between pulls). **Sanity-check** each feed: do the lines vary by player the way you'd expect? Event-level endpoints returned 404. Milestone ladders returned only the 1+ rung. |
| **The Odds API** (user has an account) | Not yet used | **Best option:** raw JSON for full DK player-prop boards across all markets. Use it whenever the key is available. |
| Articles (DK Network, FanDuel Research, Dimers, TheLines, SportsBettingDime) | Spot checks | Only a few props each. Good for cross-checking. |

NHL DraftKings IDs found: league 42133. Categories/subcategories: Saves O/U 1064/16550 · SOG O/U 1189/12040 · SOG milestones 1189/16544 · ATGS 1190/14495 · Points O/U 1675/16213 · Points milestones 1675/16545 · Assists O/U 1676/16215 · Blocks 1679/16548 · PP points 550/20350. Other sports have different IDs. Find them by fetching the league endpoint and any category, then asking for the list of subcategories.

### Game lines
- `bettorsinsider.com/game/{league}/{away}-{home}/{yyyymmdd}/`: ML, total, spread (its goalie/starter fields were unreliable)
- sportsgrid.com game pages, Covers / FanDuel Research best-bets articles

### News
- League official site status reports and game previews (projected lineups), plus TSN/ESPN/beat writers for injuries.

## 4. Math

**Implied probability from American odds:** `+X → 100/(X+100)`; `−X → X/(X+100)`.

**Removing the vig:**
- Two-way market: `p = p_over / (p_over + p_under)`
- One-way market (e.g., anytime scorer with no under): multiply by a hold factor. Used **0.87** for anytime-goal and **0.92** for one-way points O0.5.

**Game lines → team environment:** remove the vig from the ML to get win probability. Split the total into home/away expected goals (or runs, points) by solving a Poisson model where P(home wins) equals the vig-free win probability.

**Prop probability → expected count:** for a "1+" style market, `λ = −ln(1 − p)` (Poisson).

**NHL skater props-implied DK points** (the example build):
- λG from anytime-goal odds; λPts from Points O0.5; λA = max(λPts − λG, 0.25·λG)
- If only goal odds: λA = λG × 1.4 for forwards (skip defensemen who only have goal odds — too little info)
- If only points odds: λG = λPts × 0.42 for forwards, × 0.20 for defensemen
- SOG ≈ λG / shooting% (forwards 8–14% scaling with λG; defensemen 4.5–7.5%); blocks flat (F 0.5, D 1.4) unless there's a blocks prop
- DK: 8.5·G + 5·A + 1.5·SOG + 1.3·BLK + 3·P(G≥3) + 3·P(Pts≥3) + 3·P(SOG≥5) + 3·P(BLK≥3) (Poisson tails)

**NHL goalie:** solve for the mean saves μ where P(saves > line) equals the vig-free over price. GA = opponent implied goals × 0.93 (removes empty-netters).
DK = 0.7·μ + 6·P(win) − 3.5·GA + 4·e^(−GA) + 2·P(OTL) + 3·P(saves ≥ 35)

**Calibration (important):** the props-implied numbers are on a different scale than the services. Rescale them to match the services' **mean and standard deviation** across matched players (skaters), or shift them by the mean difference (goalies). That way props change how players rank, not the slate's overall level. Plain multiplication squeezes the stars down, because fixed pieces like the blocks floor inflate low-end players. Check the correlation between the props-implied numbers and the service average (0.96 for the NHL build); it's a sanity check.

## 5. Blend rules

- Base (services only) = mean of the available services. If the base source has 0 (out), keep 0 unless news says the player is active.
- Final = **equal-weight mean of base source, each other service, and the props-implied projection** (when props exist).
- Players with no usable props: mean of the services.
- News overrides beat everything: a confirmed OUT player is 0.
- Optional (used in v1 before full props): nudge each team's skaters partway toward the Vegas team total, `factor = (k·implied / team_sum)^0.5`. Skip it once player props are in, or you'll count the game environment twice.

## 6. Adapting to other sports (DraftKings)

| Sport | Prop markets to pull | Props → DK conversion notes |
|---|---|---|
| **MLB** | Hits, total bases, HR, RBI, runs, SB, H+R+RBI; pitcher Ks, outs recorded, ER, hits allowed, win | Hitter: singles/2B/3B/HR from TB + HR + hits; DK 3/5/8/10, RBI 2, R 2, BB 2, SB 5. Pitcher: 2.25·outs/3 (IP), 2·K, −2·ER, −0.6·H, −0.6·BB, +4 win. Team implied runs from the ML + total. |
| **NFL** | Pass yds/TD/INT, rush yds/att, rec yds/receptions, ATTD | DK: 0.04/pass yd, 4 pass TD, −1 INT, 0.1/rush-rec yd, 6 TD, 1 PPR, 300/100/100-yd bonuses +3. Use ATTD for TDs, and O/U medians plus a spread assumption for yardage. |
| **NBA** | Points, rebounds, assists, 3PM, steals, blocks, turnovers, PRA | DK: 1 pt, 0.5 3PM bonus, 1.25 reb, 1.5 ast, 2 stl, 2 blk, −0.5 TO, double-double +1.5, triple-double +3. Minutes/injury news drive most variance. |
| **NASCAR** | Win, top 3/5/10, H2H matchups | Place differential + finish points + laps led/fastest laps. Convert the finishing-position distribution from win/top-N odds. |
| **Golf / Tennis / Soccer** | Outright, top-N, make cut; aces, games; shots, SOT, ATGS | Build a finish/stat distribution from the ladder odds, then apply the DK scoring. |

Always use **two-way lines when available**, sanity-check every feed (lines should vary sensibly by player), and put the props-implied numbers on the services' scale before averaging.

## 7. Pitfalls found

- A service still projected an injured player (RNH at 8.6 while OUT) → check news before blending.
- A same-day trade (new DFS ID, missing from a service) → carry base value and flag the risk.
- The same odds showing up for two players (Howden = Barbashev) → possible scrape error; flag it.
- Name mismatches: "Mitchell"/"Mitch", "Joseph"/"Joe", "William"/"Will", "Zachary"/"Zack", "(F)" suffixes. Normalize before merging.
- Summarized-fetch tools can invent or flatten data from large JSON. Cross-check a few players against a second source.
- Bash/curl to sportsbook domains may be blocked by a proxy; the web-fetch tool may still work.
