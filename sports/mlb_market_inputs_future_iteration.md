# MLB Market Inputs — Future Iteration Fixes

Status: validated process correction from the 2026-09-22 DraftKings Turbo Market Inputs pass (grade A-).
Applies to every future `Savant Prep` / `Market Inputs — MLB` run.
Does not change the composite philosophy in `core/MARKET_PROJECTIONS.md`.

## What failed on 2026-09-22

- Industry layer was real for starting pitchers (RG on-page FPTS, THE BAT X Wheeler 50th, FantasyPros components, Action/Dimers/PropCruncher K models) and thin for hitters.
- Full vendor grids were paywalled or on the wrong slate (DFF showed the later main slate, not Turbo).
- Chat HTML snippets are not 10 independent numeric sources.
- Savant-zero rule left posted starters at 0 (Greene, Story, Willson Contreras, Joey Ortiz, Frelick, Nick Gonzales, and others).
- Bench names with starter-sized Savant Proj were cut using lineup facts. That is allowed only as a role allocation, not as a narrative fade.
- Relievers with Own 0 stayed on Savant. Correct, but they must not be counted as researched coverage.

An A- pass is an honest stop when the user accepts it. It is not an A+ composite.

## Mandatory intake order (next run)

1. Identify site, slate window, and game list from the attached Savant file **before** any vendor pull. Turbo ≠ Main ≠ Night ≠ Showdown.
2. Ask for attached vendor CSVs if they are not already in the thread:
   - THE BAT / THE BAT X DK export
   - RotoGrinders projected-stats CSV for **this exact slate**
   - Stokastic or SaberSim export
   - Daily Fantasy Fuel CSV with the matching slate selected
   - LineStar / RotoWire / NumberFire if available
3. Do not start the industry blend from preview articles, First Look blurbs, or a single RG lineup-page FPTS cell and then call it 10 sources.
4. Run the Vegas board sweep in parallel (PropCruncher, Covers, Action, PropPrizm, FD Research, game ML/totals).
5. Convert components with site scoring. Do not average Yahoo/FD/DK outputs as if they were the same number.
6. Grade honestly. If vendor CSVs are missing, the ceiling is A- unless the user attaches them or explicitly accepts the grade.

## Slate-lock rule

Every industry number must be tagged with slate identity (site + start window + game list). Reject a DFF/RG/Stokastic row that belongs to a different window. Mixing Main-slate projections onto a Turbo file is a process error.

## Industry source counting rule

Count a source only if it supplies a **numeric DK (or convertible component) value for that player on this slate**.

Counts:
- THE BAT X player DK or component row
- RG projected-stats FPTS row
- DFF DK FP row
- Stokastic / SaberSim / LineStar / NumberFire / RotoWire numeric row
- FantasyPros components converted with DK weights

Does not count:
- Rankings, write-ups, podcasts, First Look adjectives
- A K-only model used as if it were a full DK projection (that is Vegas/model support, not a full industry FP source)
- Savant itself
- The same vendor quoted twice

Report `industry_source_count` as the number of distinct vendors that produced at least one usable numeric value on the positive-Proj pool, and separately report median sources **per researched player**. A slate with 8 vendor logos but 2 numbers per hitter is not A+.

## Role / lineup allocation (facts only)

Use posted batting order and pitcher role to allocate expectation. Do not invent points.

- Confirmed 1–9 hitter: research industry + Vegas. Do not cut to bench range.
- Not in posted 1–9: keep a reserve/PH number only if an industry source still projects that player today. If no industry source has him and he is not starting, do not leave a starter-sized Savant number in place.
- Opener vs bulk vs full start: this is a role fact. Kent-style bulk-behind-opener must use bulk workload (outs/IP/K/win%) not a full-start prior.
- Relievers with Savant Proj > 0 and Own 0: default Savant fallback unless a save/K/outs market exists. Exclude them from the active-pool coverage denominator used for the A/A+ gate if they were never realistically DFS-startable.

## Savant-zero vs posted starter

Default remains: source `Proj = 0` stays 0.

Future iteration exception — only when the user says **`unlock posted starters`**:
- If a player is in the official/posted 1–9 or is the confirmed starter/bulk arm **and** Savant Proj is 0, research that player and write a composite Proj.
- Document each unlock in the audit.
- Do not unlock the rest of the zero pool.

Without that phrase, leave zeros at 0 and list the posted-but-zero names in the audit so the user can opt in.

## DK conversion (keep using)

Hitters: 1B 3, 2B 5, 3B 8, HR 10, RBI 2, R 2, BB/HBP 2, SB 5.
Pitchers: IP 2.25, K 2, W 4, ER -2, H -0.6, BB/HBP -0.6, CG 2.5, SHO +2.5, NH 5.

When a vendor already publishes DK FPTS, use that column. When it publishes components, convert once. Never blend raw Yahoo points with DK points.

## A+ checklist (must all be true)

- [ ] Attached or live-exported numeric industry files for this exact slate (target 5+ vendor CSVs, 10+ if the public/paid ecosystem supports it)
- [ ] Vegas board sweep covering every confirmed SP (K + outs + one run-prevention market + ML) and every posted 1–9 hitter (hits or TB + HR + R or RBI + one more family)
- [ ] Juice / both sides used where posted
- [ ] Player totals reconciled to implied team totals / game totals
- [ ] Posted-but-Savant-zero starters either left at 0 with an explicit list, or unlocked by user request
- [ ] Per-player source count reported; hitter industry not faked from SP-only boards
- [ ] Output still `Name, DFS ID, Proj, Own`; Own unchanged unless ownership pass requested
- [ ] Stop. No lineups.

## User prompt that raises the grade

Attach vendor CSVs and/or say:

`Market Inputs — MLB — projections only. Unlock posted starters. Vendor files attached.`

If no vendor files are attached, the assistant must say so in the first research beat and cap the grade at A- unless the user accepts that cap.
