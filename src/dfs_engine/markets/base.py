"""Market source interface, HTTP plumbing, and on-disk snapshot caching.

Every sweep records which sources answered and which failed. ``core/ENGINE.md``
forbids inventing data, so a source that errors is logged into
``MarketSnapshot.errors`` and downgrades the coverage grade -- it never falls
back to a guess.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..models import MarketSnapshot

log = logging.getLogger("dfs_engine.markets")

DEFAULT_TIMEOUT = 20
DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)


class MarketSourceError(RuntimeError):
    pass


@dataclass
class HttpClient:
    """Thin requests wrapper with retries, caching hooks, and polite defaults."""

    timeout: int = DEFAULT_TIMEOUT
    retries: int = 3
    backoff: float = 1.5
    user_agent: str = DEFAULT_UA
    cache: "SnapshotCache | None" = None

    def get_json(self, url: str, params: dict | None = None,
                 headers: dict | None = None, cache_ttl: int | None = None) -> Any:
        if self.cache is not None and cache_ttl:
            hit = self.cache.get(url, params, ttl=cache_ttl)
            if hit is not None:
                return hit
        try:
            import requests  # imported lazily so offline runs need no network stack
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise MarketSourceError("requests is required for live market fetching") from exc

        hdrs = {"User-Agent": self.user_agent, "Accept": "application/json"}
        hdrs.update(headers or {})
        last: Exception | None = None
        for attempt in range(self.retries):
            try:
                resp = requests.get(url, params=params, headers=hdrs, timeout=self.timeout)
                if resp.status_code == 429:
                    time.sleep(self.backoff ** (attempt + 1))
                    continue
                resp.raise_for_status()
                data = resp.json()
                if self.cache is not None and cache_ttl:
                    self.cache.put(url, params, data)
                return data
            except Exception as exc:  # noqa: BLE001 - surfaced to the caller as an error entry
                last = exc
                if attempt + 1 < self.retries:
                    time.sleep(self.backoff ** attempt)
        raise MarketSourceError(f"GET {url} failed after {self.retries} attempts: {last}")


class SnapshotCache:
    """File cache keyed by URL+params. Keeps sweeps cheap and reproducible."""

    def __init__(self, root: str | Path = ".cache/markets") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, url: str, params: dict | None) -> Path:
        raw = url + "?" + json.dumps(params or {}, sort_keys=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()[:24]
        return self.root / f"{digest}.json"

    def get(self, url: str, params: dict | None, ttl: int) -> Any | None:
        path = self._path(url, params)
        if not path.exists():
            return None
        if ttl > 0 and time.time() - path.stat().st_mtime > ttl:
            return None
        try:
            return json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            return None

    def put(self, url: str, params: dict | None, data: Any) -> None:
        try:
            self._path(url, params).write_text(json.dumps(data))
        except (OSError, TypeError):  # pragma: no cover - cache is best effort
            log.debug("cache write failed for %s", url)


class MarketSource:
    """A place we can sweep for Vegas markets."""

    name: str = "base"
    books: tuple[str, ...] = ()

    def available(self) -> tuple[bool, str]:
        """(usable?, reason). Keeps missing API keys out of the traceback path."""
        return True, ""

    def fetch(self, sport: str, **kwargs: Any) -> MarketSnapshot:  # pragma: no cover
        raise NotImplementedError


def env_key(*names: str) -> str | None:
    for n in names:
        val = os.environ.get(n)
        if val:
            return val.strip()
    return None
