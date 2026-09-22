"""American/decimal odds handling, vig removal, and multi-book consensus.

Everything downstream of the sportsbook sweep starts here: a posted line
without its juice is not an expectation (``core/MARKET_INPUTS.md``), so the
engine always works in de-vigged fair probabilities.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from statistics import median
from typing import Iterable, Sequence

DevigMethod = str  # "multiplicative" | "additive" | "shin" | "power"


def american_to_decimal(american: float) -> float:
    if american == 0:
        raise ValueError("American odds of 0 are not a price")
    if american > 0:
        return 1.0 + american / 100.0
    return 1.0 + 100.0 / abs(american)


def decimal_to_american(decimal: float) -> float:
    if decimal <= 1.0:
        raise ValueError("Decimal odds must exceed 1.0")
    if decimal >= 2.0:
        return (decimal - 1.0) * 100.0
    return -100.0 / (decimal - 1.0)


def american_to_prob(american: float) -> float:
    """Implied probability *including* vig."""
    return 1.0 / american_to_decimal(american)


def prob_to_american(prob: float) -> float:
    if not 0.0 < prob < 1.0:
        raise ValueError("Probability must be strictly between 0 and 1")
    return decimal_to_american(1.0 / prob)


def _multiplicative(raw: Sequence[float]) -> list[float]:
    total = sum(raw)
    return [p / total for p in raw]


def _additive(raw: Sequence[float]) -> list[float]:
    overround = sum(raw) - 1.0
    n = len(raw)
    return [max(1e-9, p - overround / n) for p in raw]


def _power(raw: Sequence[float], tol: float = 1e-10) -> list[float]:
    """Solve for k with sum(p_i ** k) == 1; shrinks longshots more than favourites."""
    lo, hi = 0.2, 5.0
    for _ in range(200):
        k = 0.5 * (lo + hi)
        s = sum(p ** k for p in raw)
        if abs(s - 1.0) < tol:
            break
        if s > 1.0:
            lo = k
        else:
            hi = k
    k = 0.5 * (lo + hi)
    out = [p ** k for p in raw]
    return _multiplicative(out)


def _shin(raw: Sequence[float], tol: float = 1e-10) -> list[float]:
    """Shin (1993) insider-trading model. Reduces to multiplicative when z -> 0."""
    total = sum(raw)
    lo, hi = 0.0, 0.25
    for _ in range(200):
        z = 0.5 * (lo + hi)
        fair = [_shin_prob(p, total, z) for p in raw]
        s = sum(fair)
        if abs(s - 1.0) < tol:
            break
        if s > 1.0:
            lo = z
        else:
            hi = z
    z = 0.5 * (lo + hi)
    return _multiplicative([_shin_prob(p, total, z) for p in raw])


def _shin_prob(p: float, total: float, z: float) -> float:
    disc = z * z + 4.0 * (1.0 - z) * (p * p) / total
    return max(1e-9, (math.sqrt(max(disc, 0.0)) - z) / (2.0 * (1.0 - z)))


_DEVIG = {
    "multiplicative": _multiplicative,
    "additive": _additive,
    "power": _power,
    "shin": _shin,
}


#: Default haircut applied to a lone posted side (a typical single-side hold).
#: A one-sided price cannot be de-vigged -- there is nothing to balance it
#: against -- so this is an explicit modeling assumption, not a measurement.
DEFAULT_ONE_SIDED_MULTIPLIER = 1.0 / 1.045


def devig(raw_probs: Sequence[float], method: DevigMethod = "multiplicative",
          one_sided_multiplier: float = DEFAULT_ONE_SIDED_MULTIPLIER) -> list[float]:
    """Strip the bookmaker margin from a complete set of mutually exclusive outcomes."""
    if not raw_probs:
        return []
    if any(p <= 0 for p in raw_probs):
        raise ValueError("Raw implied probabilities must be positive")
    if len(raw_probs) == 1:
        return [min(0.999, raw_probs[0] * one_sided_multiplier)]
    fn = _DEVIG.get(method)
    if fn is None:
        raise ValueError(f"Unknown de-vig method: {method}")
    return fn(list(raw_probs))


def devig_two_way(
    over_american: float | None,
    under_american: float | None,
    method: DevigMethod = "multiplicative",
    one_sided_multiplier: float = DEFAULT_ONE_SIDED_MULTIPLIER,
) -> float | None:
    """Fair probability of the *over* from a two-sided price (or a lone side)."""
    if over_american is None and under_american is None:
        return None
    if under_american is None:
        return devig([american_to_prob(float(over_american))], method,
                     one_sided_multiplier)[0]
    if over_american is None:
        under_fair = devig([american_to_prob(float(under_american))], method,
                           one_sided_multiplier)[0]
        return 1.0 - under_fair
    raw = [american_to_prob(float(over_american)), american_to_prob(float(under_american))]
    return devig(raw, method)[0]


def hold_pct(prices: Sequence[float]) -> float:
    """Bookmaker hold (overround) for a set of American prices, as a fraction."""
    return sum(american_to_prob(p) for p in prices) - 1.0


@dataclass(frozen=True)
class BookQuote:
    """One book's two-sided price on one line of one market."""

    book: str
    line: float
    over: float | None = None
    under: float | None = None
    timestamp: str | None = None

    def fair_over(self, method: DevigMethod = "multiplicative",
                  one_sided_multiplier: float = DEFAULT_ONE_SIDED_MULTIPLIER
                  ) -> float | None:
        return devig_two_way(self.over, self.under, method, one_sided_multiplier)

    @property
    def two_sided(self) -> bool:
        return self.over is not None and self.under is not None


@dataclass
class ConsensusPoint:
    """Robust cross-book fair probability for a single (market, line) pair."""

    line: float
    prob_over: float
    n_books: int
    books: list[str] = field(default_factory=list)
    two_sided_books: int = 0
    dispersion: float = 0.0

    @property
    def weight(self) -> float:
        """Evidence weight: more books, two-sided prices, tight agreement -> heavier."""
        base = math.log1p(self.n_books) + 0.5 * math.log1p(self.two_sided_books)
        return base / (1.0 + 8.0 * self.dispersion)


def consensus_over_prob(
    quotes: Iterable[BookQuote],
    method: DevigMethod = "multiplicative",
    trim: float = 0.0,
    one_sided_multiplier: float = DEFAULT_ONE_SIDED_MULTIPLIER,
) -> ConsensusPoint | None:
    """Median/trimmed-mean consensus of de-vigged over probabilities at one line.

    ``core/MARKET_INPUTS.md`` forbids cherry-picking a single book; this uses a
    robust centre and reports cross-book dispersion so the projection layer can
    downweight markets where books disagree.
    """
    quotes = list(quotes)
    if not quotes:
        return None
    lines = {round(q.line, 3) for q in quotes}
    if len(lines) != 1:
        raise ValueError("consensus_over_prob expects quotes on a single line")
    fair = []
    books: list[str] = []
    two_sided = 0
    for q in quotes:
        p = q.fair_over(method, one_sided_multiplier)
        if p is None or not 0.0 < p < 1.0:
            continue
        fair.append(p)
        books.append(q.book)
        two_sided += int(q.two_sided)
    if not fair:
        return None
    ordered = sorted(fair)
    if trim > 0 and len(ordered) >= 4:
        k = max(1, int(len(ordered) * trim))
        ordered = ordered[k:-k] or ordered
    centre = median(ordered)
    spread = (max(fair) - min(fair)) / 2.0 if len(fair) > 1 else 0.0
    return ConsensusPoint(
        line=quotes[0].line,
        prob_over=centre,
        n_books=len(fair),
        books=books,
        two_sided_books=two_sided,
        dispersion=spread,
    )
