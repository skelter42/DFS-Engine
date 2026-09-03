# DFS Engine Contest History

## Purpose
Maintain a durable, privacy-safe index of contest-level results used by the DFS Engine learning loop.

Raw DraftKings standings exports and account-history files should **not** be committed to this public repository. They may contain usernames, entry IDs, financial/account information, or full-field data that does not belong in the public engine brain.

Store only sanitized contest metadata, derived metrics, and durable findings here.

## Ingestion Rules

For each standings export:

1. Deduplicate by DraftKings Contest ID.
2. Identify the user's entries in the field without persisting entry IDs or unnecessary account identifiers.
3. Record sport, contest ID, contest type, field size, best finish, best percentile, and useful aggregate portfolio metrics.
4. Extract field-level evidence such as winning score, ownership, duplication, stack/lineup structure, and top-percentile construction when available.
5. Feed reusable findings into `core/LEARNING.md` and `learning/REGISTRY.md` only when they satisfy the promotion standard.
6. Do not promote one-off winning-player takes or hindsight-only conclusions.

## Initial Ingest — 2026-09-03

First batch received from recent DraftKings full-contest standings exports.

- 9 unique contests ingested after deduplication.
- Duplicate export detected for Contest ID `194736777`; count once.
- User entries were successfully identifiable in the standings files.
- Example best-finish observations from the batch:
  - Contest `194812059`: best finish 13th of 2,378 (~top 0.5%).
  - Contest `194736777`: best finish 62nd of 5,945 (~top 1.0%).
  - Contest `194878465`: best finish 73rd of 5,945 (~top 1.2%).
  - Contest `194731101`: best finish 83rd of 5,548 (~top 1.5%).

## Metrics To Track Going Forward

Per contest:
- contest ID
- date
- sport
- slate / game type
- entry fee and max-entry format when known
- field size
- number of user entries
- best rank
- best percentile
- top 0.1%, top 1%, top 10%, and top 20% hit rates
- winning score
- user best score and score gap to winner
- actual player ownership
- lineup duplication
- primary/secondary stack or correlation structure
- pitcher/QB/etc. pairings when sport-relevant
- ownership leverage and game-script outcomes

Across contests:
- percentile hit rates by sport
- percentile hit rates by contest type
- ROI and profit when account-history data is joined
- ownership calibration error
- projection-vs-field performance
- portfolio concentration and diversification performance
- repeatable construction patterns among top finishers

## Workflow

`DraftKings Entry History -> Contest ID index -> Full Standings Export -> Field Analysis -> Contest History Metrics -> Post-Slate Learning -> Durable GitHub Rule Promotion`

This file is an index/contract, not a raw-data warehouse.
