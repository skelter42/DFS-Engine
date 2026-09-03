# DFS Engine Agent Team

The DFS Engine should behave like a coordinated research and portfolio team. Agents may be implemented as separate processes later; for now these roles are mandatory reasoning passes.

## Core Agents

### 1. Slate Intake Agent
Validates contest, site, slate, player pool, salaries, positions, projection columns, ownership columns, and missing data. Rejects malformed inputs before optimization.

### 2. Projection Audit Agent
Compares baseline projections with alternate industry signals and identifies meaningful disagreements. It does not automatically replace the baseline; it produces a confidence adjustment and a list of fragile projections.

### 3. News & Role Agent
Verifies current starting status, injuries, scratches, batting order or lineup position, expected minutes/usage, depth-chart changes, and other role information. It flags changes that materially affect DFS value.

### 4. Market Environment Agent
Uses betting markets and relevant contextual data to identify high-upside environments, overrated environments, and possible market movement. Examples include implied team totals, totals/spreads, park/weather, pace, and matchup quality as sport-appropriate.

### 5. Cross-Sport Simulation / Outcome Distribution Agent
Runs or ingests Monte Carlo outcome distributions using the framework in `core/SIMULATION.md`. It evaluates volatility, ceiling and failure paths, top-tail rates, correlated game outcomes, and portfolio overlap.

It must not use one generic normal-distribution assumption for every sport. Sport modules define the appropriate standard deviations, distribution shapes, role uncertainty, and correlation structures. When empirical volatility or correlation data is unavailable, modeled assumptions must be labeled explicitly rather than invented as facts.

### 6. Ownership & Leverage Agent
Evaluates projected ownership, likely field constructions, chalk fragility, leverage pivots, and duplication risk. It distinguishes good chalk from bad chalk rather than fading popularity mechanically.

### 7. Correlation / Game Script Agent
Builds coherent slate narratives and identifies lineups that benefit together. It creates multiple plausible game scripts rather than one deterministic prediction and uses simulation results as evidence for how frequently those scripts occur.

### 8. Portfolio Builder Agent
Combines projection, simulated top-tail outcomes, ownership, leverage, correlation, and contest structure to construct the actual lineup set. It manages exposures across the portfolio, not lineup by lineup in isolation.

### 9. Exposure Auditor Agent
Produces the required side-by-side source projected ownership vs DFS Engine exposure list with percentage-point difference. It challenges the largest deviations and catches accidental concentration.

### 10. Post-Slate Learning Agent
Compares results with pre-slate theses and simulation expectations. It categorizes misses into projection error, simulation-calibration error, ownership error, role/news error, correlation error, portfolio/exposure error, or ordinary variance. Only repeated or clearly structural findings become durable engine rules.

## MLB Specialized Agents

These are mandatory for MLB slate builds in addition to the core agents.

### 11. MLB Simulation Calibration Pass
Specializes the shared simulation layer for hitter and pitcher distributions, team-run correlation, pitcher-vs-opposing-hitter negative correlation, strikeout ceiling, blow-up risk, and stack outcome families. Sim Savant simulation outputs may be used as an input but should be challenged with current context rather than treated as final truth.

### 12. Stack Architecture Agent
Evaluates full-stack construction quality rather than only individual hitter quality. It scores primary 5-man stacks, secondary correlations, wraparound combinations, lineup-order connectivity, salary efficiency, platoon fit, and full-stack ownership. It should identify stacks that are individually popular but collectively over-owned, as well as under-owned combinations with coherent ceiling.

### 13. Pitcher Failure / Opposing Stack Agent
Explicitly models where popular pitchers can fail and connects those failure paths to opposing bats and stacks. It compares pitcher ownership, strikeout ceiling, contact quality allowed, platoon splits, park, weather, bullpen context, and opposing stack leverage. Pitcher fades should be tied to coherent offensive leverage rather than random avoidance.

### 14. Duplication / Lineup Uniqueness Agent
Estimates lineup duplication risk using salary usage, common pitcher pairings, chalk stack combinations, popular value bats, roster construction, and likely field behavior. It seeks enough uniqueness for contest-winning equity without sacrificing excessive projection or correlation.

### 15. Portfolio Risk Manager Agent
Audits the entire lineup set for hidden concentration. It measures exposure not only by player, but also by primary stack, secondary stack, pitcher pairing, game environment, salary construction, simulated winning world, and game script. Its job is to prevent the portfolio from making the same underlying bet repeatedly while still preserving concentration when the Engine has a strong edge.

## NCAAF Specialized Agents

These are mandatory for college-football slate builds in addition to the core agents. Detailed behavior lives in `sports/ncaaf.md`.

### 16. Depth Chart & Role Certainty Agent
Verifies starting QBs, RB rotations, WR/TE starters, transfers, suspensions, and injury uncertainty. It assigns role confidence and penalizes fragile backup-dependent projections.

### 17. QB Archetype Agent
Classifies QBs by rushing floor, passing volume, favorite/underdog script, red-zone rushing, and ceiling path. It prevents the Engine from treating all similarly projected QBs as interchangeable.

### 18. Usage Concentration Agent
Measures carries, targets, routes, goal-line usage, and offensive concentration so the Engine can distinguish durable volume from committee-driven median projection.

### 19. Blowout & Rotation Agent
Models large-spread outcomes as separate passing, rushing, starter-ceiling, rotation, and favorite-disappointment branches instead of applying one generic blowout penalty.

### 20. Game Environment & Pace Agent
Ranks games by four-quarter fantasy potential using total, spread, pace, offensive efficiency, explosive-play ability, pass rate, and expected competitiveness.

### 21. CFB Correlation Agent
Builds QB/pass-catcher stacks, opponent bring-backs, rushing-heavy favorite constructions, and trailing-underdog volume combinations consistent with actual offensive roles.

### 22. Script Portfolio Agent
Assigns each lineup to a plausible slate narrative and intentionally allocates portfolio weight across game-script families.

### 23. CFB Duplication & Construction Agent
Audits common double-QB structures, chalk pairings, popular value, salary usage, and repeated lineup cores to preserve first-place equity.

### 24. CFB Portfolio Risk Agent
Audits concentration by player, team, game, QB pairing, script family, favorite/underdog archetype, and chalk combination.

## MLB Default Handoff Chain

Slate Intake -> Projection Audit -> News & Role -> Market Environment -> Cross-Sport Simulation / MLB Calibration -> Ownership & Leverage -> Stack Architecture -> Pitcher Failure / Opposing Stack -> Correlation / Game Script -> Portfolio Builder -> Duplication / Lineup Uniqueness -> Portfolio Risk Manager -> Exposure Auditor -> Post-Slate Learning.

## NCAAF Default Handoff Chain

Slate Intake -> Projection Audit -> Depth Chart & Role Certainty -> News & Role -> Market Environment -> Cross-Sport Simulation -> QB Archetype -> Usage Concentration -> Blowout & Rotation -> Game Environment & Pace -> Ownership & Leverage -> CFB Correlation -> Script Portfolio -> Portfolio Builder -> CFB Duplication & Construction -> CFB Portfolio Risk -> Exposure Auditor -> Post-Slate Learning.

## Other Sports

NFL, NBA, NHL, tennis, golf, and future sports inherit the Cross-Sport Simulation / Outcome Distribution Agent automatically. Each sport module should define or progressively learn its own variance, distribution, and correlation assumptions rather than copying MLB or another sport.

## Post-Slate Counterfactual Review

For MLB and NCAAF, the Post-Slate Learning Agent must include a counterfactual pass. It should ask what would have happened if one major decision had been correct while another was held constant.

Examples:
- if the primary stack/game script hit, did another roster decision still sink the lineup?
- if the leverage thesis was correct, was exposure too low to benefit?
- if the field chalk failed as expected, did the Engine choose the right alternatives?
- for NCAAF, if the right game environment was identified, did the correct QB archetype and role players appear in enough builds?
- was the miss caused by process or ordinary variance?

The purpose is to avoid learning the wrong lesson from final standings alone.

## Handoff Protocol

Each pass should preserve:

- facts and source data
- assumptions
- derived adjustments
- confidence level
- unresolved uncertainty

Later agents should not silently overwrite earlier facts. Any change must be traceable to new evidence or an explicit model decision.
