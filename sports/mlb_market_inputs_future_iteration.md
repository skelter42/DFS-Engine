# MLB Market Inputs — Future Iteration Fixes

Status: validated process correction from the 2026-09-22 DraftKings Turbo Market Inputs pass, plus user-approved defaults:

- 2026-09-22: The user does not attach paid vendor CSVs. The assistant scrapes public industry numbers and public Vegas props and does its best.
- 2026-09-23 FanDuel Main: **Industry and Vegas work together on the same player.** Coverage is measured on the active starter pool, not the raw positive-Proj file.

Do not stall a run waiting for THE BAT X / Stokastic / DFF / RG CSV uploads.

## Default operating mode

`Savant Prep` / `Market Inputs — MLB` means:

1. Attached Savant file only.
2. Identify site + exact slate window + game list.
3. Trust Savant zeros unless the user says `unlock posted starters`.
4. Exhaust **public** industry numeric pages and **public** Vegas boards **in parallel**.
5. Convert to site scoring. **Joint-blend** industry + Vegas + Savant prior. Reconcile to game totals with data only.
6. Write `Name, DFS ID, Proj, Own`. Own unchanged unless requested.
7. Grade honestly against the public-source ceiling. Deliver. Stop.

Paid vendor grids are optional upside if they appear in public HTML. They are not a prerequisite.

## Joint-blend doctrine (validated 2026-09-23)

Industry and Vegas are **co-primary on the same player**. They do not take turns.

- **Industry** answers who the player is (talent / component rates / site FPTS).
- **Vegas** answers what game they are in (player props when posted; otherwise implied team total + lineup slot + ML/win).
- **Savant** is the prior, not the vote.

Default weights when both layers exist:

- Starting pitchers with K/IP/win markets + industry FD/DK: `0.40 industry + 0.40 Vegas + 0.20 Savant`
- Posted 1–9 hitters with industry FPTS/components + team-total/slot: `0.40 industry + 0.32 Vegas-env + 0.28 Savant`
- Only one external layer: that layer 0.40–0.55, Savant the rest
- Neither layer after the sweep: Savant fallback

Do not label a posted starter `VEGAS_SUPPORTED` just because a team total exists and then skip industry. Pull both. If public industry did not print that name, say so and keep the Vegas-env + Savant blend — that is still not fallback.

Team-total + batting-order slot **is** the Vegas hitter layer when individual hits/TB/HR/R/RBI props are missing. It is not optional color. It is not a reason to drop industry.

## Coverage denominator (validated 2026-09-23)

**Do not grade fallback against the raw positive-Proj file.**

A main-slate Savant file often has 400+ positive rows. Most of those are relievers / PH / bench with Own ≈ 0 and no public market. Counting them as fallback makes an 80% fallback rate that is not the process failure.

Report two denominators every run:

1. **Active pool (the grade that matters)**  
   Starting pitchers (full start or bulk-behind-opener) + confirmed/projected batting-order 1–9.  
   Target: **0% Savant fallback** on this pool. Joint or Vegas-supported on every name.

2. **Full positive-Proj pool (honesty row)**  
   Relievers with Own 0 and no save/K/outs market may stay Savant fallback. Say that explicitly. Do not let that percentage be the headline.

An 80% fallback headline on the 459-row positive file is not acceptable reporting. If the active pool is covered, say the active pool first.

## Provenance labels

- **JOINT** — industry numeric + Vegas (props and/or team-total/slot) + Savant prior all moved the number.
- **VEGAS_DIRECT** — player props with juice did most of the Vegas work; industry still present.
- **VEGAS_SUPPORTED** — game/team/slot environment + Savant; no public industry print for that name.
- **INDUSTRY_BLEND** — public industry numeric + Savant; Vegas environment missing (should be rare on a posted 1–9).
- **SAVANT_FALLBACK** — both public layers thin after the sweep. Allowed for Own-0 relievers. Not allowed as the default for posted starters.

## Public industry sources to hit every run

Board / page first, same slate only:

- RotoGrinders lineup pages and any public FPTS / projected-stats HTML for this slate
- FantasyPros daily hitters and pitchers component tables
- NumberFire public MLB projections if the page loads
- Daily Fantasy Fuel public table **only if the slate selector matches** (Turbo vs Main vs Night)
- FantasyTeamAdvisors / similar public game-by-game FD or component pages
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
When hitter props are missing: implied team total × slot share is the Vegas layer.
Use juice and both sides when posted.

## Grade ceiling without vendor files

Honest public-scrape ceiling is usually **A-** on a Main or Turbo slate:
- SP industry + Vegas can be thick
- hitter industry is often a partial grid
- that is expected and allowed

Do not hold the file hostage for an A+ that requires paywalled CSVs the user will not attach.
Deliver the best public composite, report source counts, list posted-but-zero names, and stop.

A / A+ is still the target **when public boards actually produce that coverage**. It is not a reason to refuse delivery.

## Role / lineup allocation (facts only)

- Confirmed 1–9: research public industry **and** Vegas. Do not cut to bench range. Do not leave on Savant.
- Not in posted 1–9: reserve/PH only if a public industry source still projects him. Otherwise cut starter-sized Savant leftovers.
- Opener vs bulk vs full start is a role fact. Bulk-behind-opener uses bulk workload.
- Relievers with Own 0: Savant fallback unless a public save/K/outs market exists.
- Unposted late lineups (west games): use projected 1–9 from last posted order / probable bats; keep more Savant weight until the card is official.

## Savant-zero rule

Default: source `Proj = 0` stays 0.
Exception only on `unlock posted starters`.
Always list posted-but-zero names in the audit.

## Required delivery report

- Projection grade (honest public-scrape grade)
- Public industry sources actually used (names, not a hoped-for 10)
- Vegas boards used
- Provenance mix on the **active pool** first, then the full positive-Proj pool
- Largest composite vs Savant deltas
- Posted starters still at Savant 0

## What not to do

- Do not ask the user to drop BAT X / Stokastic / DFF files as a gate.
- Do not mix Main-slate public tables onto a Turbo file.
- Do not count a K-only model as a full DK/FD projection source.
- Do not write narrative into Proj.
- Do not build lineups.
- Do not report 80% fallback because 200 relievers were left at Savant.
- Do not let Vegas-env replace industry, or industry replace Vegas, when both exist.
