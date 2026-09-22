"""Configuration loading: the JSON files in ``config/`` are the tuning surface."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here] + list(here.parents):
        if (parent / "config" / "engine.json").exists():
            return parent
    return Path.cwd()


def _load(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return dict(default)


DEFAULT_ENGINE = {
    "version": "0.2.0",
    "site": "DraftKings",
    "score_weights": {"projection": 1, "ceiling": 0.22, "leverage": 0.18,
                      "correlation": 0.12, "value": 0.08, "volatility_penalty": 0.05},
    "portfolio": {"default_lineups": 20, "min_uniques": 2, "max_player_exposure": 0.65},
}

DEFAULT_PROFILES = {
    "large_field_gpp": {"projection_multiplier": 0.96, "ceiling_multiplier": 1.20,
                        "leverage_multiplier": 1.30, "correlation_multiplier": 1.20,
                        "max_player_exposure": 0.55, "min_uniques": 3},
}


@dataclass
class EngineConfig:
    root: Path
    engine: dict[str, Any] = field(default_factory=dict)
    contest_profiles: dict[str, Any] = field(default_factory=dict)
    routing: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, root: Path | str | None = None) -> "EngineConfig":
        base = Path(root) if root else repo_root()
        cfg = base / "config"
        return cls(
            root=base,
            engine=_load(cfg / "engine.json", DEFAULT_ENGINE),
            contest_profiles=_load(cfg / "contest_profiles.json", DEFAULT_PROFILES),
            routing=_load(cfg / "routing.json", {}),
        )

    def profile(self, name: str) -> dict[str, Any]:
        return self.contest_profiles.get(name, self.contest_profiles.get("large_field_gpp", {}))

    @property
    def score_weights(self) -> dict[str, float]:
        return self.engine.get("score_weights", DEFAULT_ENGINE["score_weights"])

    @property
    def portfolio_settings(self) -> dict[str, Any]:
        return self.engine.get("portfolio", DEFAULT_ENGINE["portfolio"])

    @property
    def site(self) -> str:
        raw = str(self.engine.get("site", "DraftKings")).lower()
        return "fd" if raw.startswith("fan") else "dk"
