"""Single pre-lock DFS point estimate: industry baseline plus priced-stat deltas.

The baseline and component priors must be compatible DK projections from the
same independent source group(s). This path does not simulate outcomes,
construct lineups, estimate ownership or project contest finish rates.
"""

from __future__ import annotations

from math import isfinite
from statistics import median
from urllib.parse import urlparse

from .market_nfl import InsufficientMarket, _utc, estimate_stat


LINEAR = {
    ("MLB", "hitter"): {"rbi": 2, "runs": 2, "walks": 2, "hbp": 2,
                          "stolen_bases": 5},
    ("MLB", "pitcher"): {"outs": .75, "strikeouts": 2, "earned_runs": -2,
                           "hits_allowed": -.6, "walks_allowed": -.6,
                           "hbp_allowed": -.6},
    ("NHL", "skater"): {"goals": 8.5, "assists": 5, "shots": 1.5,
                          "blocks": 1.3, "shorthanded_points": 2,
                          "shootout_goals": 1.5},
    ("NHL", "goalie"): {"saves": .7, "goals_against": -3.5,
                          "goalie_goals": 8.5, "goalie_assists": 5},
}
EVENT_WEIGHTS = {
    ("MLB", "pitcher"): {"win": 4, "complete_game": 2.5,
                           "complete_game_shutout": 2.5, "no_hitter": 5},
    ("NHL", "goalie"): {"win": 6, "shutout": 4, "ot_loss": 2},
}
BONUS = {("NHL", "skater"): {"goals": ("hat_trick", 3),
                              "shots": ("five_shots", 5),
                              "blocks": ("three_blocks", 3)},
         ("NHL", "goalie"): {"saves": ("saves35", 35)}}


def industry_baseline(player: dict) -> tuple[float, list[str]]:
    """Median of independent current *forecasts*, converted to DK scoring.

    Historical DraftKings PPG, last-game points, salary/value displays and
    projections for a different slate are not industry model forecasts.
    """
    as_of = _utc(player["as_of_utc"])
    slate = player.get("slate")
    if not slate:
        raise ValueError("Industry projection requires exact slate identity")
    groups = {}
    for row in player.get("industry_fpts", []):
        url = urlparse(row.get("source_url", ""))
        if (row.get("site") != "DraftKings" or
            row.get("forecast_type") != "pregame_projection" or
            row.get("slate") != slate or not row.get("source_group") or
            url.scheme not in {"http", "https"} or not url.netloc):
            continue
        captured = _utc(row["as_of_utc"])
        if not 0 <= (as_of - captured).total_seconds() <= 21600:
            continue
        points = float(row["points"])
        if not isfinite(points):
            raise ValueError("Non-finite industry projection")
        group = row["source_group"]
        if group not in groups or captured > groups[group][0]:
            groups[group] = captured, points
    if not groups:
        raise InsufficientMarket("No current, site-correct independent numeric FPTS baseline")
    return median(v[1] for v in groups.values()), sorted(groups)


def central_projection(player: dict, sport: str, kind: str) -> dict:
    """Use the industry FPTS baseline and adjust only comparable priced stats.

    `component_priors` must be the corresponding industry expectations for
    each stat being adjusted. A missing prior leaves that quote unused.
    """
    key = (sport, kind)
    if key not in LINEAR:
        raise ValueError("Unsupported sport/role")
    baseline, sources = industry_baseline(player)
    priors = player.get("component_priors", {})
    deltas, skipped, fitted = {}, {}, {}
    weights_used = {}

    def weight(stat: str) -> float:
        # Equal evidence weight is a transparent starting point, not an
        # accuracy claim. Replace only with a held-out, role-specific fit.
        value = float(player.get("market_weights", {}).get(stat, .5))
        if not isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"Invalid market weight for {stat}")
        weights_used[stat] = value
        return value

    def fit(stat: str):
        if stat not in player.get("markets", {}):
            return None
        if stat not in priors:
            skipped[stat] = "missing matching industry component prior"
            return None
        try:
            value = estimate_stat(stat, player["markets"][stat],
                 as_of_utc=player["as_of_utc"],
                 dispersion_prior=player.get("dispersion_prior", {}).get(stat))
        except InsufficientMarket as exc:
            skipped[stat] = str(exc)
            return None
        prior = float(priors[stat])
        if not isfinite(prior) or prior < 0:
            raise ValueError(f"Invalid component prior: {stat}")
        fitted[stat] = value
        return weight(stat) * (value.mean - prior)

    for stat, dk_coefficient in LINEAR[key].items():
        delta = fit(stat)
        if delta is not None:
            deltas[stat] = dk_coefficient * delta

    if key == ("MLB", "hitter"):
        # Hits/TB are overlapping summaries. A priced HR or triple changes
        # hit count and bases when those markets are not themselves priced.
        h = fit("hits")
        tb = fit("total_bases")
        hr = fit("home_runs")
        triples = fit("triples")
        if (h is None) != (tb is None):
            skipped["hit_family"] = "hits and total bases require paired component coverage"
            h = tb = None
        if h is not None:
            deltas["hits"] = h
            deltas["total_bases"] = 2*tb
            if hr is not None:
                deltas["home_runs"] = hr
            if triples is not None:
                deltas["triples"] = triples
        else:
            if hr is not None:
                deltas["home_runs"] = 10*hr
            if triples is not None:
                deltas["triples"] = 8*triples
        # A sole hit/TB quote is recorded but never forced into a potentially
        # mispriced single/double/HR mix.
    if key in BONUS:
        for stat, (bonus_name, threshold) in BONUS[key].items():
            if stat not in fitted:
                continue
            prior = player.get("bonus_priors", {}).get(bonus_name)
            if prior is None:
                skipped[bonus_name] = "missing matching milestone probability prior"
                continue
            p = float(prior)
            if not isfinite(p) or not 0 <= p <= 1:
                raise ValueError("Invalid bonus prior")
            deltas[bonus_name] = 3*weights_used[stat]*(fitted[stat].count_at_least(threshold) - p)
    if key == ("NHL", "skater") and player.get("markets", {}).get("points"):
        point_delta = fit("points")
        if point_delta is not None:
            prior = player.get("bonus_priors", {}).get("three_points")
            if prior is None:
                skipped["three_points"] = "missing matching milestone probability prior"
            else:
                p = float(prior)
                if not isfinite(p) or not 0 <= p <= 1:
                    raise ValueError("Invalid bonus prior")
                deltas["three_points"] = 3*weights_used["points"]*(fitted["points"].count_at_least(3) - p)

    # Event market deltas require a matching prior. An ordinary team
    # moneyline is not accepted as a player's win event quote.
    for name, points_per_event in EVENT_WEIGHTS.get(key, {}).items():
        quotes = player.get("event_markets", {}).get(name, [])
        if not quotes:
            continue
        prior = player.get("event_priors", {}).get(name)
        if prior is None:
            skipped[name] = "missing matching event prior"
            continue
        from .market_sports import _probability
        p, origin = _probability(player, name)
        if origin != "paired_event_market":
            skipped[name] = "no usable paired event market"
            continue
        deltas[name] = points_per_event * weight(name) * (p - float(prior))

    estimate = baseline + sum(deltas.values())
    if not isfinite(estimate) or estimate < 0:
        raise InsufficientMarket("Adjusted DK score invalid; preserve original source")
    return {"projection": round(estimate, 4), "baseline": baseline,
            "industry_groups": sources, "component_deltas": deltas,
            "market_weights_used": weights_used,
            "unused_market_components": skipped,
            "provenance": {stat: "market_industry_blend_delta" for stat in deltas}}
