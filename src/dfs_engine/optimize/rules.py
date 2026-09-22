"""Site roster rules -- the only hard constraints the engine accepts.

``core/ENGINE.md`` reserves hard constraints for structural necessities: site
legality, contest rules, confirmed inactives, and the source-projection
eligibility gate. Everything else (exposure, stacks, diversity) is expressed as
objective-level pressure, not as a wall.

Verify against the site before a real build; roster rules do change.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Slot:
    name: str
    eligible: tuple[str, ...]
    multiplier: float = 1.0  # showdown captain scoring/salary multiplier


@dataclass(frozen=True)
class RosterRules:
    site: str
    sport: str
    variant: str
    slots: tuple[Slot, ...]
    salary_cap: int
    min_salary: int = 0
    max_per_team: int | None = None          # skaters/hitters from one team
    max_per_team_excludes: tuple[str, ...] = ()  # positions exempt from that cap
    min_teams: int = 2
    min_games: int = 2
    forbid_same_game_opponents: bool = False  # tennis: one winner path per slot
    notes: str = ""

    @property
    def size(self) -> int:
        return len(self.slots)

    @property
    def slot_names(self) -> tuple[str, ...]:
        return tuple(s.name for s in self.slots)

    def slot_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in self.slots:
            out[s.name] = out.get(s.name, 0) + 1
        return out

    def eligible_slots(self, positions: tuple[str, ...]) -> list[int]:
        return [i for i, s in enumerate(self.slots)
                if any(p in s.eligible for p in positions)]


def _slots(spec: list[tuple[str, tuple[str, ...], int]]) -> tuple[Slot, ...]:
    out: list[Slot] = []
    for name, eligible, count in spec:
        out.extend(Slot(name, eligible) for _ in range(count))
    return tuple(out)


FLEX_NFL = ("RB", "WR", "TE")

DK_NFL_CLASSIC = RosterRules(
    site="dk", sport="nfl", variant="classic",
    slots=_slots([("QB", ("QB",), 1), ("RB", ("RB",), 2), ("WR", ("WR",), 3),
                  ("TE", ("TE",), 1), ("FLEX", FLEX_NFL, 1), ("DST", ("DST", "D", "DEF"), 1)]),
    salary_cap=50000, min_teams=2, min_games=2,
    notes="DraftKings NFL classic: 9 roster spots, $50k, 2+ teams and 2+ games.",
)

FD_NFL_CLASSIC = RosterRules(
    site="fd", sport="nfl", variant="classic",
    slots=_slots([("QB", ("QB",), 1), ("RB", ("RB",), 2), ("WR", ("WR",), 3),
                  ("TE", ("TE",), 1), ("FLEX", FLEX_NFL, 1), ("DEF", ("DST", "D", "DEF"), 1)]),
    salary_cap=60000, max_per_team=4, max_per_team_excludes=("DST", "D", "DEF"),
    min_teams=3, min_games=2,
    notes="FanDuel NFL: $60k cap, at most 4 from one team.",
)

DK_NBA_CLASSIC = RosterRules(
    site="dk", sport="nba", variant="classic",
    slots=_slots([("PG", ("PG",), 1), ("SG", ("SG",), 1), ("SF", ("SF",), 1),
                  ("PF", ("PF",), 1), ("C", ("C",), 1), ("G", ("PG", "SG"), 1),
                  ("F", ("SF", "PF"), 1), ("UTIL", ("PG", "SG", "SF", "PF", "C"), 1)]),
    salary_cap=50000, min_teams=2, min_games=2,
    notes="DraftKings NBA classic: 8 spots, $50k.",
)

DK_MLB_CLASSIC = RosterRules(
    site="dk", sport="mlb", variant="classic",
    slots=_slots([("P", ("P", "SP", "RP"), 2), ("C", ("C",), 1), ("1B", ("1B",), 1),
                  ("2B", ("2B",), 1), ("3B", ("3B",), 1), ("SS", ("SS",), 1),
                  ("OF", ("OF",), 3)]),
    salary_cap=50000, max_per_team=5, max_per_team_excludes=("P", "SP", "RP"),
    min_teams=2, min_games=2,
    notes="DraftKings MLB classic: 10 spots, $50k, max 5 hitters from one team.",
)

DK_NHL_CLASSIC = RosterRules(
    site="dk", sport="nhl", variant="classic",
    slots=_slots([("C", ("C",), 2), ("W", ("W", "LW", "RW"), 3), ("D", ("D",), 2),
                  ("G", ("G",), 1), ("UTIL", ("C", "W", "LW", "RW", "D"), 1)]),
    salary_cap=50000, min_teams=3, min_games=2,
    notes="DraftKings NHL classic: 9 spots, $50k, players from 3+ teams.",
)

DK_TENNIS_CLASSIC = RosterRules(
    site="dk", sport="tennis", variant="classic",
    slots=_slots([("P", ("P",), 6)]),
    salary_cap=50000, min_teams=6, min_games=6, forbid_same_game_opponents=True,
    notes="DraftKings tennis: 6 players, no two players from the same match "
          "(sports/tennis.md hard rule).",
)


def showdown(site: str, sport: str, cap: int = 50000,
             flex_positions: tuple[str, ...] = ("QB", "RB", "WR", "TE", "DST", "K")) -> RosterRules:
    return RosterRules(
        site=site, sport=sport, variant="showdown",
        slots=(Slot("CPT", flex_positions, 1.5),) + tuple(Slot("FLEX", flex_positions)
                                                          for _ in range(5)),
        salary_cap=cap, min_teams=2, min_games=1,
        notes="Showdown: captain scores and costs 1.5x. Duplication-sensitive format.",
    )


RULES: dict[tuple[str, str, str], RosterRules] = {
    ("dk", "nfl", "classic"): DK_NFL_CLASSIC,
    ("dk", "ncaaf", "classic"): DK_NFL_CLASSIC,
    ("fd", "nfl", "classic"): FD_NFL_CLASSIC,
    ("dk", "nba", "classic"): DK_NBA_CLASSIC,
    ("dk", "mlb", "classic"): DK_MLB_CLASSIC,
    ("dk", "nhl", "classic"): DK_NHL_CLASSIC,
    ("dk", "tennis", "classic"): DK_TENNIS_CLASSIC,
}


def get_rules(site: str, sport: str, variant: str = "classic") -> RosterRules:
    key = (site.lower(), sport.lower(), variant.lower())
    if key in RULES:
        return RULES[key]
    if variant.lower() == "showdown":
        return showdown(site, sport)
    raise KeyError(f"No roster rules for site={site} sport={sport} variant={variant}")


def lineup_is_legal(lineup, rules: RosterRules) -> tuple[bool, str]:
    """Verify a built roster against every hard site/contest constraint."""
    players = list(lineup.players)
    if len(players) != rules.size:
        return False, f"roster has {len(players)} players, expected {rules.size}"
    if len({p.player_id for p in players}) != len(players):
        return False, "the same player appears twice"
    if lineup.salary > rules.salary_cap:
        return False, f"salary {lineup.salary} exceeds the {rules.salary_cap} cap"
    if rules.min_salary and lineup.salary < rules.min_salary:
        return False, f"salary {lineup.salary} below the {rules.min_salary} minimum"
    if len({p.team for p in players}) < rules.min_teams:
        return False, f"fewer than {rules.min_teams} teams"
    games = {p.game_id or f"g:{p.team}" for p in players}
    if len(games) < rules.min_games:
        return False, f"fewer than {rules.min_games} games"
    if rules.max_per_team:
        excluded = {e.upper() for e in rules.max_per_team_excludes}
        counts: dict[str, int] = {}
        for p in players:
            if any(pos.upper() in excluded for pos in p.positions):
                continue
            counts[p.team] = counts.get(p.team, 0) + 1
        if counts and max(counts.values()) > rules.max_per_team:
            return False, f"more than {rules.max_per_team} players from one team"
    if rules.forbid_same_game_opponents and len(games) < len(players):
        return False, "two players from the same match"
    if lineup.slots:
        for player, slot_name in zip(players, lineup.slots):
            slot = next((s for s in rules.slots if s.name == slot_name), None)
            if slot is None:
                return False, f"unknown roster slot {slot_name}"
            if not any(pos in slot.eligible for pos in player.positions):
                return False, f"{player.name} is not eligible for {slot_name}"
    return True, ""
