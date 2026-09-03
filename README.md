# DFS Engine

A persistent, versioned decision system for building and improving DFS lineups across sports.

## Mission

The DFS Engine is not a single projection model. It is a portfolio-construction framework that combines projections, ownership, contest context, slate structure, game-script analysis, leverage, correlation, and post-slate learning.

The goal is repeatable decision quality: ingest slate inputs, cross-check them against broader market information, build diversified but intentional portfolios, compare final exposures to source projections, and learn from results without overfitting.

## Operating Principles

1. Never treat one projection source as authoritative.
2. Separate player projection quality from portfolio construction quality.
3. Optimize for contest-specific expected value, not median lineup projection alone.
4. Use correlation and game-script logic where the sport supports it.
5. Respect uncertainty. Diversification should cover plausible slate outcomes, not randomize blindly.
6. Always compare source projected ownership with DFS Engine final exposure.
7. Record durable lessons after slates; do not memorialize noise.
8. Prefer explicit rules, schemas, and versioned logic over chat-only memory.

## Repository Map

- `core/ENGINE.md` — master slate workflow and portfolio rules
- `core/AGENTS.md` — agent responsibilities and handoffs
- `core/LEARNING.md` — post-slate learning framework
- `sports/mlb.md` — MLB-specific construction logic
- `sports/ncaaf.md` — college football construction logic
- `sports/tennis.md` — tennis construction logic
- `sports/nba.md` — NBA construction logic
- `sports/nhl.md` — NHL construction logic
- `sports/nfl.md` — NFL construction logic
- `schemas/` — durable input/output contracts
- `learning/` — future dated durable learnings

## Standard Output Contract

Every lineup build should include:

- slate thesis and major game environments
- key leverage points and fragility risks
- final lineup portfolio
- stack/correlation summary where applicable
- source projected ownership vs DFS Engine exposure, side by side, with percentage-point difference
- concise explanation of the largest exposure deviations

This repository is the canonical DFS Engine brain. New chats should read the relevant files before making slate-specific decisions, and durable improvements should be written back here.