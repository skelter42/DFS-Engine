# DFS Engine Learning Loop

## Objective
Improve future decision quality without overfitting to a single winning lineup or one unusual slate.

## Post-Slate Review Questions

1. What lineup/stack structures actually dominated the top of the contest?
2. Which pre-slate theses were directionally correct?
3. Which high-exposure players/teams failed, and was the failure process-driven or variance-driven?
4. Which low-exposure or omitted players materially hurt the portfolio?
5. Did ownership projections materially miss the field?
6. Did role/news changes arrive after the original build?
7. Was correlation used correctly?
8. Did the portfolio cover enough distinct game scripts without becoming random?
9. Were there unnecessary duplicates or overly similar lineups?
10. Would the same decision still be correct if the exact slate result were hidden?

## Error Taxonomy

- `projection_error` — expected fantasy production was materially misestimated
- `ownership_error` — expected field ownership/construction was materially wrong
- `role_error` — starting role, minutes, batting order, usage, etc. was wrong or stale
- `environment_error` — game/team environment was misread
- `correlation_error` — lineup components did not express a coherent outcome
- `portfolio_error` — exposures or diversification were poorly allocated
- `contest_error` — construction did not match contest size/payout structure
- `variance` — process was reasonable and outcome was simply noisy

## Promotion Rule

Do not change core logic because one lineup won. Promote a lesson only when it is structurally justified by one or more of:

- repeated evidence across slates
- a clear causal mechanism
- a backtest or meaningful sample
- a result that exposes a genuine process flaw rather than hindsight

## Durable Learning Format

Each promoted learning should record:

- date
- sport/slate type
- evidence
- old rule or assumption
- new rule
- confidence
- what would falsify the new rule

## Known Durable MLB Lesson

Primary five-man stacks deserve strong priority in MLB GPP construction, but stack structure alone is not enough. A lineup can share the winning core and still lose because of the secondary stack/value choices. Review the full lineup as a portfolio of correlated ceiling outcomes, not just whether it used a 5-man primary stack.

## Philosophy

The engine should become more calibrated over time, not more complicated for its own sake. Retire rules that do not improve decisions. Keep uncertainty visible.