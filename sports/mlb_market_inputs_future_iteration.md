# MLB Market Inputs — Future Iteration Fixes

Status: validated process correction from the 2026-09-22 DraftKings Turbo Market Inputs pass, plus user-approved defaults:

- 2026-09-22: The user does not attach paid vendor CSVs. The assistant scrapes public industry numbers and public Vegas props and does its best.
- 2026-09-23 FanDuel Main: **Industry and Vegas work together on the same player.** Coverage is measured on the active starter pool, not the raw positive-Proj file.
- 2026-09-29: Proj is the industry median, pulled to the Vegas band if it sits outside. Canonical rule: `core/MARKET_PROJECTIONS.md`. Fixed weights stay retired.

Do not stall a run waiting for THE BAT X / Stokastic / DFF / RG CSV uploads.

## Default operating mode

`Savant Prep` / `Market Inputs — MLB` means:

1. Attached Savant file only.
2. Identify site + exact slate window + game list.
3. Trust Savant zeros unless the user says `unlock posted starters`.
4. Exhaust **public** industry numeric pages and **public** Vegas boards **in parallel**.
5. Convert to site scoring. Set Proj with the industry-median + Vegas-band lock. Reconcile to game totals with data only.
6. Write `Name, DFS ID, Proj, Own`. Own unchanged unless requested.
7. Grade honestly against the public-source ceiling. Deliver. Stop.

Paid vendor grids are optional upside if they appear in public HTML. They are not a prerequisite.

## Joint-blend doctrine (validated 2026-09-23, estimator replaced 2026-09-29)

Industry and Vegas are pulled on the same player. They do not take turns. They are not equal votes.

- **Industry** is the candidate (talent / component rates / site FPTS).
- **Vegas** is the band (player props when posted). Game total is the slate check.
- **Savant** is the vessel and the fallback. It is not a vote.

Estimator: the industry-median + Vegas-band lock in `core/MARKET_PROJECTIONS.md`.

- Convert industry and Vegas to site scoring. Collapse source families to one vote.
- Three or more Tier A votes: median of Tier A. Otherwise median of the usable votes.
- Vegas contributes one de-vigged number. Band = that number ± the larger of 1.5 site points or 12% of it.
- Inside the band, keep the industry median. Outside, pull to the nearest edge.
- No converted prop: the industry median stands. Team total × the locked slot share in the override is an environment check, not site points and not a band.
- Savant does not vote when any usable industry vote exists.
- Neither layer after the sweep: Savant fallback.

Do not label a posted starter `VEGAS_SUPPORTED` just because a team total exists and then skip industry. Pull both. If public industry did not print that name, say so and keep the industry gap labeled. A team total alone is not a player projection.

## Coverage denominator (validated 2026-09-23)

**Do not grade fallback against the raw positive-Proj file.**

A main-slate Savant file often has 400+ positive rows. Most of those are relievers / PH / bench with Own ≈ 0 and no public market. Counting them as fallback makes an 80% fallback rate that is not the process failure.

Report two denominators every run:

1. **Active pool (the grade that matters)**  
   Starting pitchers (full start or bulk-behind-opener) + confirmed/projected batting-order 1–9.  
   Target: **0% Savant fallback** on this pool.

2. **Full positive-Proj pool (honesty row)**  
   Relievers with Own 0 and no save/K/outs market may stay Savant fallback. Say that explicitly. Do not let that percentage be the headline.

## Provenance labels

- **BAND_PULLED** — industry median sat outside the Vegas band and was moved to the nearest edge.
- **INDUSTRY_MEDIAN** — industry median sat inside the band, or no converted prop existed.
- **VEGAS_DIRECT** — a converted prop formed the band.
- **SAVANT_FALLBACK** — no usable industry vote after the sweep. Allowed for Own-0 relievers. Not allowed as the default for posted starters.

## Public industry sources to hit every run

Board / page first, same slate only. Tier A if they render numbers: RotoGrinders, FantasyPros consensus, NumberFire, Daily Fantasy Fuel when the slate selector matches, THE BAT / BAT X when a table is visible, Action Network / Dimers / PropCruncher when they publish numeric K/IP/FP.

Does not count: rankings, First Look adjectives, podcasts, paywalled grids that do not render.

## Public Vegas sources to hit every run

Aggregator-first: PropCruncher, Covers, Action Network, PropPrizm, FanDuel Research, sportsbook ML / total / team total.

Pitchers: K, outs/IP, ER, H, BB, win/ML. Those convert into the band.
Hitters: hits, TB, HR, RBI, runs, BB, SB, H+R+RBI. A converted prop forms the band. A missing prop does not.

## Grade ceiling without vendor files

Honest public-scrape ceiling is usually **A-** on a Main or Turbo slate. Deliver it. Do not hold the file for a paywalled grid.

## Savant-zero rule

Default: source `Proj = 0` stays 0. Exception only on `unlock posted starters`. Always list posted-but-zero names in the audit.

## What not to do

- Do not ask the user to drop BAT X / Stokastic / DFF files as a gate.
- Do not mix Main-slate public tables onto a Turbo file.
- Do not count a K-only model as a full DK/FD projection source.
- Do not write narrative into Proj.
- Do not build lineups.
- Do not give Vegas a peer vote against the industry median.
- Do not apply a fixed industry/Vegas/Savant weight.
