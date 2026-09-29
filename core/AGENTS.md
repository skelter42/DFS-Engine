# DFS Engine Agent Architecture

Projection work reads `CURRENT.md` first. Books drive. Savant is the fallback. Do not follow the industry-conglomerate language later in this file. That section is retired.

The DFS Engine is a coordinated decision system. Agents are mandatory reasoning responsibilities, not necessarily separate autonomous processes. GitHub stores the durable brain; chat executes the workflow.

## Design Rule

`core/ENGINE.md` is the canonical operating sequence. `core/AGENTS.md` defines ownership of each stage. `core/SIMULATION.md` is the single authoritative simulation specification. Sport files define only sport-specific implementation details. Agents and sport files must not restate global policy already defined in core files.

The Engine should use the fewest agents needed to create clear ownership and traceable handoffs. Avoid multiple agents solving the same problem under different names.

## Canonical Agent Team

### 1. Slate Intake & Validation Agent
Owns raw slate integrity and pre-generation eligibility.

Responsibilities:
- identify sport, site, slate, contest, entry count, lock state, and contest type
- ingest player pool, salaries, positions, source projections, ownership, and simulations when supplied
- validate IDs, names, teams, positions, roster eligibility, game inclusion, and malformed files
- preserve source columns unchanged
- identify missing inputs before downstream modeling
- apply a hard eligibility gate before any projection, simulation, or candidate-generation stage

Hard eligibility gate:
- exclude any player with a source projection of exactly 0 unless there is verified current evidence that the zero is stale and the player has an active role that warrants a rebuilt Engine projection
- exclude any player with a blank/missing source projection when there is no verified current active role or defensible market-derived projection
- exclude confirmed inactive/out/scratched players
- for sports with confirmed starters/lineups, require current role validation near lock before treating a player as lineup-eligible
- if a zero or missing source projection conflicts with verified active status, stop and resolve the conflict explicitly; do not silently pass the player through optimization
- eligibility is a hard structural gate, not an exposure preference or game-theory decision

Output:
- validated slate dataset
- explicit eligible-player universe
- excluded-player list with reason
- source inventory
- unresolved data gaps

### 2. Market Projection Agent
Owns the DFS Engine player projection (`Proj`).

Retired instruction below. Do not execute it. Read `CURRENT.md`. Books drive. Savant is the fallback. A missing price is not filled. Industry is a check. Python scrape only.

Output per player:
- book number, or Savant if the scoring prices were not posted
- the prices used
- Savant as the comparison, not a vote
