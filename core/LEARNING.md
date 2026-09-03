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

## Mandatory Projection & Ownership Calibration Archive

For every final slate build, preserve the pre-lock baseline needed for later calibration. At minimum, retain or reconstruct:

- Sim Savant player projection
- Sim Savant projected ownership
- DFS Engine adjusted projection / ceiling view or confidence tier
- DFS Engine expected ownership / field-construction view when it differs from Savant
- DFS Engine final exposure
- relevant stack/team/game-script allocation
- the reason for any material projection, ownership, or exposure deviation

Do not evaluate Savant only by whether a player scored well. Projection calibration and ownership calibration are separate questions.

### Projection calibration
After results arrive, compare the source projection and the Engine-adjusted expectation against realized fantasy production over appropriate samples. Track systematic bias by sport-relevant archetypes rather than overreacting to one result. Examples include position, salary tier, role, matchup type, batting-order slot, pitcher archetype, usage tier, or game environment.

The key questions are:

- Was Savant systematically too high or too low on this archetype?
- Was the Engine adjustment directionally better or worse?
- Was the miss caused by role/news/environment changes after projection time?
- Was the outcome ordinary variance despite a sound projection process?

### Ownership calibration
When contest files provide actual ownership, compare:

- Savant projected ownership vs actual field ownership
- DFS Engine expected ownership vs actual field ownership
- DFS Engine exposure vs actual field ownership

Track both absolute error and directional error. The goal is to learn where the field is consistently more or less concentrated than Savant expects and whether the Engine's game-theory read improves that estimate.

For stack-based sports, also compare team/stack ownership and common lineup constructions when recoverable from contest results. Individual ownership accuracy alone may miss the real field-construction error.

### Calibration separation rule
Never treat a profitable exposure decision as proof that the underlying projection or ownership estimate was accurate. A player can be correctly overweight for leverage despite an imperfect projection; likewise, an accurate projection can still produce a poor tournament exposure decision.

Evaluate four layers independently:

1. source projection quality
2. source ownership quality
3. DFS Engine projection/ownership adjustment quality
4. final portfolio/exposure quality

Only after separating those layers should a durable lesson be promoted.

## Post-Slate Review Questions

1. What lineup/stack structures actually dominated the top of the contest?
2. Which pre-slate theses were directionally correct?
3. Which high-exposure players/teams failed, and was the failure process-driven or variance-driven?
4. Which low-exposure or omitted players materially hurt the portfolio?
5. How accurate were Sim Savant ownership projections versus actual ownership?
6. How accurate was the DFS Engine's own ownership/field view versus actual ownership?
7. Where did Savant projections and DFS Engine adjusted expectations disagree, and which view was better calibrated?
8. Did role/news changes arrive after the original build?
9. Was correlation used correctly?
10. Did the portfolio cover enough distinct game scripts without becoming random?
11. Were there unnecessary duplicates or overly similar lineups?
12. Would the same decision still be correct if the exact slate result were hidden?

## Error Taxonomy

- `projection_error` — expected fantasy production was materially misestimated
- `ownership_error` — expected field ownership/construction was materially wrong
- `engine_adjustment_error` — DFS Engine changed a source projection/ownership read in the wrong direction or by an unjustified magnitude
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

Projection and ownership calibration changes should normally require repeated evidence or a meaningful sample. One slate may create a hypothesis or temporary confidence adjustment, but not a permanent source haircut/boost unless a structural input error is proven.

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