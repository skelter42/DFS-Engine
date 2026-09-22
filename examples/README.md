# Example inputs

| File | What it is |
|---|---|
| `contests.json` | Contest set passed to `dfs-engine build --contests`. Drives allocation priority, field size and payout shape. |
| `props_template.csv` | Flat prop table for `dfs-engine fetch-props --csv`. Use this to feed in any aggregator export (Action Network, PropCruncher, a manual sweep). `stat` accepts canonical names or book labels. |
| `games_template.csv` | Game lines to merge with a prop CSV via `--games-csv`. Team totals are derived from `total` + `spread_home` when not supplied directly. |

The player pool is the site's own salary export (DraftKings: `Position, Name + ID,
Name, ID, Roster Position, Salary, Game Info, TeamAbbrev, AvgPointsPerGame`). A
vendor projection file passed with `--vendor` is matched on an accent- and
punctuation-insensitive key, but the pool's identity text is written back
unchanged.
