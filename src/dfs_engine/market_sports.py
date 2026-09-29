"""DraftKings MLB and NHL component scoring from auditable expectations.

Props replace their matching statistic, never the full fantasy projection.
Missing statistics and event bonuses require explicit numeric priors.  The
return value is the expected DK score, not the median of a joint score law.
"""

from __future__ import annotations

from math import isfinite

from .market_nfl import InsufficientMarket, _count_tail, estimate_stat, fair_over


def _component(player: dict, name: str) -> tuple[float, str, object | None]:
    quotes = player.get("markets", {}).get(name)
    if quotes:
        try:
            fit = estimate_stat(name, quotes, as_of_utc=player.get("as_of_utc"))
            return fit.mean, fit.method, fit
        except InsufficientMarket:
            pass
    prior = player.get("prior_stats", {})
    if name not in prior:
        raise InsufficientMarket(f"No priced {name} market or independent component prior")
    value = float(prior[name])
    if not isfinite(value) or value < 0:
        raise ValueError(f"Invalid {name} prior")
    return value, "independent_component_prior", None


def _components(player: dict, names: tuple[str, ...]):
    values, provenance, fitted = {}, {}, {}
    for name in names:
        value, source, estimate = _component(player, name)
        values[name], provenance[name] = value, source
        if estimate is not None:
            fitted[name] = estimate
    return values, provenance, fitted


def _probability(player: dict, name: str) -> tuple[float, str]:
    quotes = player.get("event_markets", {}).get(name, [])
    if quotes:
        probabilities = []
        for q in quotes:
            # Book and timestamp are mandatory on machine-ingested evidence.
            if not q.get("book") or not q.get("captured_at_utc"):
                raise ValueError(f"Missing book or timestamp for {name}")
            from .market_nfl import _utc
            age = (_utc(player["as_of_utc"]) - _utc(q["captured_at_utc"])).total_seconds()
            if age < 0 or age > 7200:
                continue
            probabilities.append(fair_over(q["yes"], q["no"]))
        if probabilities:
            probabilities.sort()
            middle = len(probabilities) // 2
            return (probabilities[middle] if len(probabilities) % 2 else
                    (probabilities[middle - 1] + probabilities[middle]) / 2,
                    "paired_event_market")
    if name not in player.get("event_priors", {}):
        raise InsufficientMarket(f"Missing event probability: {name}")
    value = float(player["event_priors"][name])
    if not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"Invalid {name} event prior")
    return value, "independent_event_prior"


def _bonus(player: dict, key: str, estimate: object | None, threshold: int) -> tuple[float, str]:
    if estimate is not None:
        return _count_tail(threshold, estimate.mean), "market_count_distribution"
    if key not in player.get("bonus_priors", {}):
        raise InsufficientMarket(f"Missing bonus probability: {key}")
    value = float(player["bonus_priors"][key])
    if not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"Invalid bonus probability: {key}")
    return value, "independent_bonus_prior"


def _result(score: float, values: dict, provenance: dict, bonus: dict | None = None) -> dict:
    if not isfinite(score) or score < 0:
        raise InsufficientMarket("Non-finite or negative fantasy projection; inspect inputs")
    return {"projection": round(score, 4), "stats": values,
            "provenance": provenance, "bonus_probs": bonus or {}}


def project_mlb_hitter(player: dict) -> dict:
    """Use hits + 2*TB + triples + HR to score all four hit types exactly.

    Expected values satisfy the same linear identity as realized box scores.
    Reject materially inconsistent prop/prior components instead of counting
    an HR in both total bases and a second full HR award.
    """
    names = ("hits", "total_bases", "triples", "home_runs", "rbi", "runs",
             "walks", "hbp", "stolen_bases")
    v, provenance, _ = _components(player, names)
    if v["total_bases"] + 0.15 < v["hits"] + 2*v["triples"] + 3*v["home_runs"]:
        raise InsufficientMarket("Hits/TB/HR components imply negative doubles")
    if v["hits"] + 0.15 < v["triples"] + v["home_runs"]:
        raise InsufficientMarket("Hit components imply negative singles")
    hit_points = v["hits"] + 2*v["total_bases"] + v["triples"] + v["home_runs"]
    points = (hit_points + 2*(v["rbi"] + v["runs"] + v["walks"] + v["hbp"])
              + 5*v["stolen_bases"])
    return _result(points, v, provenance)


def project_mlb_pitcher(player: dict) -> dict:
    names = ("outs", "strikeouts", "earned_runs", "hits_allowed",
             "walks_allowed", "hbp_allowed")
    v, provenance, _ = _components(player, names)
    win, provenance["win"] = _probability(player, "win")
    cg, provenance["complete_game"] = _probability(player, "complete_game")
    shutout, provenance["complete_game_shutout"] = _probability(player, "complete_game_shutout")
    no_hitter, provenance["no_hitter"] = _probability(player, "no_hitter")
    if shutout > cg + 0.01 or no_hitter > cg + 0.01:
        raise InsufficientMarket("Pitcher event probabilities are inconsistent")
    points = (0.75*v["outs"] + 2*v["strikeouts"] + 4*win
              - 2*v["earned_runs"] - 0.6*(v["hits_allowed"] + v["walks_allowed"]
                                               + v["hbp_allowed"])
              + 2.5*cg + 2.5*shutout + 5*no_hitter)
    return _result(points, v, provenance, {"win": win, "complete_game": cg,
                                         "complete_game_shutout": shutout,
                                         "no_hitter": no_hitter})


def project_nhl_skater(player: dict) -> dict:
    names = ("goals", "assists", "shots", "blocks", "shorthanded_points", "shootout_goals")
    v, provenance, fitted = _components(player, names)
    hat, provenance["hat_trick"] = _bonus(player, "hat_trick", fitted.get("goals"), 3)
    five, provenance["five_shots"] = _bonus(player, "five_shots", fitted.get("shots"), 5)
    three_blocks, provenance["three_blocks"] = _bonus(player, "three_blocks", fitted.get("blocks"), 3)
    # Points are goals + assists. An independent 3+ points market can supply
    # the milestone probability without double-counting its mean.
    points_fit = None
    if player.get("markets", {}).get("points"):
        try:
            points_fit = estimate_stat("points", player["markets"]["points"],
                                       as_of_utc=player.get("as_of_utc"))
        except InsufficientMarket:
            pass
    if points_fit is not None and abs(points_fit.mean - (v["goals"] + v["assists"])) > max(
            0.5, 0.4*(v["goals"] + v["assists"])):
        raise InsufficientMarket("Points market contradicts goal/assist expectations")
    three_points, provenance["three_points"] = _bonus(player, "three_points", points_fit, 3)
    if v["shorthanded_points"] > v["goals"] + v["assists"] + 0.01:
        raise InsufficientMarket("Shorthanded points exceed total points")
    score = (8.5*v["goals"] + 5*v["assists"] + 1.5*v["shots"] + 1.3*v["blocks"]
             + 2*v["shorthanded_points"] + 1.5*v["shootout_goals"]
             + 3*(hat + five + three_blocks + three_points))
    return _result(score, v, provenance, {"hat_trick": hat, "five_shots": five,
                 "three_blocks": three_blocks, "three_points": three_points})


def project_nhl_goalie(player: dict) -> dict:
    names = ("saves", "goals_against", "goalie_goals", "goalie_assists")
    v, provenance, fitted = _components(player, names)
    win, provenance["win"] = _probability(player, "win")
    shutout, provenance["shutout"] = _probability(player, "shutout")
    ot_loss, provenance["ot_loss"] = _probability(player, "ot_loss")
    saves35, provenance["saves35"] = _bonus(player, "saves35", fitted.get("saves"), 35)
    # A goalie can record a 0-GA shutout but lose a shootout.  Shutout need
    # not be a subset of wins; win and overtime/shootout loss are exclusive.
    if win + ot_loss > 1.01:
        raise InsufficientMarket("Goalie event probabilities are inconsistent")
    score = (0.7*v["saves"] - 3.5*v["goals_against"] + 6*win + 4*shutout
             + 2*ot_loss + 3*saves35 + 8.5*v["goalie_goals"]
             + 5*v["goalie_assists"])
    return _result(score, v, provenance, {"win": win, "shutout": shutout,
                                        "ot_loss": ot_loss, "saves35": saves35})


PROJECTORS = {("MLB", "hitter"): project_mlb_hitter,
              ("MLB", "pitcher"): project_mlb_pitcher,
              ("NHL", "skater"): project_nhl_skater,
              ("NHL", "goalie"): project_nhl_goalie}
