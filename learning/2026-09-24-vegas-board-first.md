# 2026-09-24 — Vegas layer is board-first, not player-by-player

- Sport: all, enforced first on NFL Showdown (ATL @ GB TNF)
- Status: validated (process correction; user-approved permanent preference)
- Evidence: The 2026-09-24 ATL @ GB Market Inputs pass collected industry numbers and some props, but the first Vegas pass walked stars one name at a time. The user corrected the method: hit overall TD / yards / receptions boards, then gap-fill. The DK event ATTD/FTD/2+ ladder plus the Covers / SBD / Fantrax yards table covered the positive-Proj pool without sequential player pages. Composite numbers barely moved after the board sweep, which is the point — retrieval cost falls, coverage rises, and the audit can name the boards.
- Durable lesson: Never build the Vegas layer from a list of player searches. Required order is game markets → full-game ATTD ladder → full-game yards/receptions/attempts table → convert the positive-Proj pool → named search only for missing components. Articles that mention three props are not a board. Persist those tables in `history/YYYY-MM-DD-<slate>-vegas-boards.md` so the next pass copies a board, not a player list.
- Engine impact: Canonical file `core/VEGAS_BOARD_SWEEP.md`. Market Projection Agent and NFL module must follow it. A projection pass that cannot list a TD board and a yards board has not finished the Vegas layer.
- Slate artifact: `history/2026-09-24-ATL-GB-vegas-boards.md` (game board + ATTD ladder + yards/volume table used for the locked composite).
- Files updated: `core/VEGAS_BOARD_SWEEP.md`, `learning/REGISTRY.md`, `sports/nfl.md`, `core/AGENTS.md`, `core/MARKET_PROJECTIONS.md`, `core/SAVANT_PREP.md`, `history/2026-09-24-ATL-GB-vegas-boards.md`.
- Revisit condition: only if a sport has no public multi-player board; then document the exception rather than reverting to name-first as the default.
