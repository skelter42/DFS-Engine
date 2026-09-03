# DFS Engine Learning Loop

## Objective
Improve future decision quality without overfitting to a single winning lineup or one unusual slate.

## Automatic Learning Writeback

For every meaningful DFS Engine session, learning review is the default final stage. The user should not need to ask for it separately.

Trigger automatic learning review after any of the following:

- a lineup portfolio is built or materially revised
- final-lock news causes strategic changes
- contest results are reviewed
- a what-if/replay analysis produces a reusable process insight
- an input/parsing/routing mistake reveals a preventable workflow flaw

The Engine should automatically decide whether anything from the session is durable enough to save. If yes, write the reusable lesson to GitHub during the same chat session. If no durable lesson exists, do not manufacture one.

Save only reusable knowledge such as process improvements, validated strategic principles, agent handoff changes, contest-specific construction logic, repeated projection/ownership calibration findings, and post-slate causal lessons.

Do not permanently save one-off player takes, raw slate opinions, hindsight-only winner chasing, isolated variance, or facts that can be regenerated from current data.

The intended loop is:

Chat inputs -> GitHub brain loaded -> agents run -> portfolio/output -> session learning review -> durable writeback to GitHub -> stronger next session.

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

Process corrections that prevent avoidable mistakes may be promoted immediately when the causal mechanism is clear.

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