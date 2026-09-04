# Lineup Output Contract

Every DFS Engine build should return a consistent, auditable package.

## Required Sections

### Slate Summary
- site
- sport
- slate name/date
- contest type and lineup count
- source projection set
- source ownership set

### Slate Thesis
Summarize the highest-confidence environments, strongest leverage spots, fragile chalk, and primary game-script assumptions.

### Portfolio
For each lineup, preserve the exact roster in site upload order and enough metadata to trace the construction back to the thesis.

### Exposure Table
Required columns:

| Player | Team | Position | Source Own % | Engine Exposure % | Difference (pp) | Reason |
|---|---|---|---:|---:|---:|---|

Difference is `Engine Exposure - Source Own` in percentage points.

### Correlation / Stack Summary
Use sport-appropriate structure such as MLB primary/secondary stacks, QB stacks, NHL lines, or game-stack combinations.

### Multi-Contest Allocation Audit
When entries span multiple contests, report for each contest:

- lineup count and uniqueness
- average projection and available ceiling/top-tail metrics
- average ownership, leverage, and duplication proxy
- script/anchor/correlation/risk-family distribution
- material player/team/game exposures
- quality-ladder position and any contest-specific tilt

Confirm that every contest is a viable standalone mini-portfolio and that the combined entries form one coordinated bankroll portfolio. Explicitly flag any contest that lacks a material script family or receives a disproportionate share of lower-quality candidates.

### Risk Flags
Identify late news, uncertain roles, weather, lineup confirmation, ownership uncertainty, or any assumption that can materially change the build.

### Final Audit
Confirm:
- salaries and roster legality
- no scratched/inactive players
- expected starters verified where relevant
- intended exposures achieved
- meaningful exposure deviations explained
- game-script portfolio is intentional rather than random

## Naming Convention for Future Slate Files

`slates/YYYY-MM-DD/<sport>/<site>-<slate-name>/`

Suggested contents:
- `inputs.md` — source/version notes, not necessarily raw proprietary files
- `thesis.md`
- `exposures.csv`
- `lineups.csv`
- `results.md`
- `learnings.md`

Raw user-provided files should only be committed when the user explicitly wants them stored in the repository and their licensing/contents allow it.