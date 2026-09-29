# NFL component projection input (preview)

Run `dfs-engine --source savant.csv --inputs quotes.json --output preview.csv --audit audit.json` after `pip install -e .`. This first implementation supports DraftKings NFL offensive players only. It does not fetch odds, infer missing role volume, or produce kicker/DST projections. Audit the preview before uploading it.

`quotes.json` has `sport: "NFL"`, `site: "DraftKings"`, a slate name, `as_of_utc`, `lock_utc`, and a `players` object keyed by the source `DFS ID`. All times include a UTC offset. Every paired quote has a threshold, American over and under odds for **the same strike**, book, and `captured_at_utc`. Quotes more than two hours old are discarded. Market lines must belong to the same slate and player; the operator must validate that identity before supplying this file.

```json
{
  "sport": "NFL", "site": "DraftKings", "slate": "Week 4 main",
  "as_of_utc": "2026-10-04T15:30:00Z", "lock_utc": "2026-10-04T17:00:00Z",
  "players": {
    "12345": {
      "prior_stats": {
        "pass_yds": 0, "pass_tds": 0, "interceptions": 0,
        "rush_yds": 42, "receptions": 3, "rec_yds": 19,
        "offensive_tds": 0.55, "fumbles_lost": 0.04
      },
      "bonus_probs": {"pass_yds": 0, "rush_yds": 0.13, "rec_yds": 0.01},
      "sigma_prior": {"rush_yds": 27},
      "markets": {
        "rush_yds": [
          {"threshold": 44.5, "over": -115, "under": -105,
           "book": "example", "captured_at_utc": "2026-10-04T15:20:00Z"}
        ],
        "offensive_tds": [
          {"threshold": 1, "over": 125, "under": -150,
           "book": "example", "captured_at_utc": "2026-10-04T15:20:00Z"}
        ]
      }
    }
  }
}
```

The numbers above only demonstrate the schema and must not be used as live projections. Supply **independent, site-compatible component priors** for all missing stat markets, including explicit zero for components the player cannot reasonably accumulate. A single priced yard line requires an externally calibrated `sigma_prior`; two or more different priced strikes estimate a spread directly. For count stats, `threshold: 1` is 1+, `threshold: 2` is 2+, and the current distribution fit assumes Poisson. Count fit disagreement over 10 percentage points is rejected. A one-sided anytime TD price is insufficient to remove vig and is not accepted as a market component.

For yardage supplied only from a prior, `bonus_probs` must include the DK 300-yard passing and 100-yard rushing/receiving milestone chances. Market-fitted yardage supplies these probabilities itself. `offensive_tds` is *rushing plus receiving TDs*, so never add an anytime TD market to separate rushing and receiving TD priors. Passing TDs are separate. The model floors a normal yardage outcome at zero; this is a working approximation to calibrate against results, especially for low-volume players. CPT is multiplied by 1.5 only when the input row has `Roster Position=CPT`.

The CSV keeps original columns, rows and ownership. Savant zero stays zero. Uncovered positive rows keep their original projection with the failure reason in the JSON audit. The audit distinguishes market-supported components from industry priors. Do not call such a mixed preview an A-grade full-slate projection until its uncovered rows and source accuracy have been reviewed.
