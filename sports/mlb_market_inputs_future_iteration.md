# MLB Market Inputs — Future Iteration Fixes

Status: validated process correction from the 2026-09-22 DraftKings Turbo Market Inputs pass, plus user-approved default (2026-09-22):

**The user does not attach paid vendor CSVs. The assistant scrapes public industry numbers and public Vegas props and does its best.**

Do not stall a run waiting for THE BAT X / Stokastic / DFF / RG CSV uploads.

## Default operating mode

`Savant Prep` / `Market Inputs — MLB` means:

1. Attached Savant file only.
2. Identify site + exact slate window + game list.
3. Trust Savant zeros unless the user says `unlock posted starters`.
4. Exhaust **public** industry numeric pages and **public** Vegas boards.
5. Convert to site scoring. Blend. Reconcile to game totals with data only.
6. Write `Name, DFS ID, Proj, Own`. Own unchanged unless requested.
7. Grade honestly against the public-source ceiling. Deliver. Stop.

Paid vendor grids are optional upside if they appear in public HTML. They are not a prerequisite.

## Public industry sources to hit every run

Board / page first, same slate only:

- RotoGrinders lineup pages and any public FPTS / projected-stats HTML for this slate
- FantasyPros daily hitters and pitchers component tables
- NumberFire public MLB projections if the page loads
- Daily Fantasy Fuel public table **only if the slate selector matches** (Turbo vs Main vs Night)
- THE BAT / BAT X numbers only when a public percentile or table is actually visible
- Action Network / Dimers / PropCruncher model projections when they publish numeric K/IP/FP
- Any other public numeric DK or convertible component table found in the sweep

Does not count: rankings, First Look adjectives, podcasts, paywalled grids that do not render.

## Public Vegas sources to hit every run

Aggregator-first:

- PropCruncher multi-book K / outs
- Covers matchup prop sections
- Action Network player props
- PropPrizm
- FanDuel Research game + player pages
- Sportsbook game ML, total, team total

Pitchers: K, outs/IP, ER, H, BB, win/ML.
Hitters: hits, TB, HR, RBI, runs, BB, SB, H+R+RBI.
Use juice and both sides when posted.

## Grade ceiling without vendor files

Honest public-scrape ceiling is usually **A-** on a short Turbo slate:
- SP industry + Vegas can be thick
- hitter industry is often thin
- that is expected and allowed

Do not hold the file hostage for an A+ that requires paywalled CSVs the user will not attach.
Deliver the best public composite, report source counts, list posted-but-zero names, and stop.

A / A+ is still the target **when public boards actually produce that coverage**. It is not a reason to refuse delivery.

## Role / lineup allocation (facts only)

- Confirmed 1–9: research public industry + Vegas. Do not cut to bench range.
- Not in posted 1–9: reserve/PH only if a public industry source still projects him. Otherwise cut starter-sized Savant leftovers.
- Opener vs bulk vs full start is a role fact. Bulk-behind-opener uses bulk workload.
- Relievers with Own 0: Savant fallback unless a public save/K/outs market exists.

## Savant-zero rule

Default: source `Proj = 0` stays 0.
Exception only on `unlock posted starters`.
Always list posted-but-zero names in the audit.

## Required delivery report

- Projection grade (honest public-scrape grade)
- Public industry sources actually used (names, not a hoped-for 10)
- Vegas boards used
- Provenance mix on the positive-Proj pool
- Largest composite vs Savant deltas
- Posted starters still at Savant 0

## What not to do

- Do not ask the user to drop BAT X / Stokastic / DFF files as a gate.
- Do not mix Main-slate public tables onto a Turbo file.
- Do not count a K-only model as a full DK projection source.
- Do not write narrative into Proj.
- Do not build lineups.
