import json

import pytest

from dfs_engine.cli import main
from dfs_engine.data.synthetic import build_demo_slate
from dfs_engine.ingest import load_player_pool, load_vendor_file
from dfs_engine.models import Contest
from dfs_engine.pipeline import BuildRequest, run_build
from dfs_engine.report.html import render_html
from dfs_engine.report.writers import write_all


@pytest.fixture(scope="module")
def build():
    slate = build_demo_slate("nfl", seed=7)
    contests = [
        Contest(name="Big", entries=6, field_size=100000, entry_fee=20, priority=1),
        Contest(name="Small", entries=4, field_size=3000, entry_fee=5, priority=2,
                profile="small_field_gpp"),
    ]
    request = BuildRequest(sport="nfl", players=slate.players, snapshot=slate.snapshot,
                           contests=contests, n_lineups=10, n_candidates=40,
                           n_worlds=4000, field_entries=600, synthetic=True)
    return run_build(request)


def test_build_produces_a_legal_audited_portfolio(build):
    assert len(build.portfolio.lineups) == 10
    assert build.portfolio.diagnostics["final_audit"]["passed"]
    assert build.meta["synthetic"] and "SYNTHETIC" in build.meta["warning"]
    for lu in build.portfolio.lineups:
        assert lu.salary <= build.rules.salary_cap
        assert lu.contest in {"Big", "Small"}


def test_build_preserves_the_three_projection_layers(build):
    for proj in build.projections.values():
        assert proj.coverage in {"A", "B", "C", "D"}
        if proj.coverage in {"A", "B"}:
            assert proj.market_projection is not None
            assert proj.n_markets >= 1
    assert build.portfolio.diagnostics["coverage"]["players"] == len(build.projections)


def test_reports_are_written_and_complete(build, tmp_path):
    paths = write_all(build, tmp_path)
    assert set(paths) == {"upload", "lineups_detail", "exposures", "projections",
                          "build_json", "audit", "html"}
    upload = paths["upload"].read_text().splitlines()
    assert upload[0].split(",") == list(build.rules.slot_names)
    assert len(upload) == 11                      # header + 10 lineups

    audit = paths["audit"].read_text()
    for heading in ("## Slate summary", "## Projection confidence", "## Slate thesis",
                    "## Portfolio", "## Source ownership vs engine exposure",
                    "## Correlation / stack summary", "## Multi-contest allocation audit",
                    "## Risk flags", "## Final audit"):
        assert heading in audit, heading
    assert "SYNTHETIC" in audit

    payload = json.loads(paths["build_json"].read_text())
    assert len(payload["lineups"]) == 10
    assert payload["meta"]["simulation"]["mode"] == "native_monte_carlo"

    html = paths["html"].read_text()
    assert "<title>" in html and "prefers-color-scheme" in html
    assert "Synthetic slate" in html


def test_html_report_escapes_content(build):
    html = render_html(build)
    assert "<script>" not in html.lower()
    assert html.startswith("<!doctype html>")


def test_player_pool_ingestion_reads_a_draftkings_export(tmp_path):
    csv_path = tmp_path / "pool.csv"
    csv_path.write_text(
        "Position,Name + ID,Name,ID,Roster Position,Salary,Game Info,TeamAbbrev,"
        "AvgPointsPerGame\n"
        "QB,Josh Allen (123),Josh Allen,123,QB,8200,KC@BUF 09/22/2026 01:00PM ET,BUF,23.4\n"
        "RB,James Cook (124),James Cook,124,RB/FLEX,6400,KC@BUF 09/22/2026 01:00PM ET,BUF,15.1\n"
        "DST,Bills  (125),Bills ,125,DST,3600,KC@BUF 09/22/2026 01:00PM ET,BUF,7.0\n")
    players, games = load_player_pool(csv_path, "nfl")
    assert len(players) == 3
    qb = players[0]
    assert qb.name == "Josh Allen" and qb.dfs_id == "123"
    assert qb.team == "BUF" and qb.opponent == "KC" and qb.home is True
    assert players[1].positions == ("RB", "FLEX")
    assert players[2].roster_role == "dst"
    assert players[2].name == "Bills "          # identity text preserved verbatim
    assert games[0].game_id == "KC@BUF"


def test_vendor_file_merges_without_rewriting_identity(tmp_path):
    pool = tmp_path / "pool.csv"
    pool.write_text("Name,ID,Position,Salary,TeamAbbrev\n"
                    "Jose Ramirez,9,3B,5400,CLE\n")
    vendor = tmp_path / "vendor.csv"
    vendor.write_text("Name,DFS ID,Proj,Own\n"
                      "José Ramírez,9,11.8,22.5\n")
    players, _ = load_player_pool(pool, "mlb", vendor=load_vendor_file(vendor))
    assert players[0].name == "Jose Ramirez"     # pool text wins, unchanged
    assert players[0].vendor_projection == 11.8  # accent-insensitive match still worked
    assert players[0].vendor_ownership == 22.5


def test_cli_demo_runs_end_to_end(tmp_path, capsys):
    code = main(["demo", "--sport", "nfl", "--out", str(tmp_path), "--lineups", "4",
                 "--candidates", "12", "--worlds", "1500", "--field", "300"])
    assert code == 0
    assert (tmp_path / "lineups.csv").exists()
    assert (tmp_path / "audit.md").exists()
    assert "PASSED" in capsys.readouterr().out


def test_cli_inspect_reads_a_saved_snapshot(tmp_path, capsys):
    from dfs_engine.markets import save_snapshot

    slate = build_demo_slate("nfl", seed=3)
    path = tmp_path / "snap.json"
    save_snapshot(slate.snapshot, path)
    assert main(["inspect", "--markets", str(path)]) == 0
    assert "prop_markets" in capsys.readouterr().out


def test_cli_project_writes_projections(tmp_path, capsys):
    from dfs_engine.markets import save_snapshot

    slate = build_demo_slate("nfl", seed=3)
    snap_path = tmp_path / "snap.json"
    save_snapshot(slate.snapshot, snap_path)
    pool_path = tmp_path / "pool.csv"
    lines = ["Position,Name,ID,Roster Position,Salary,Game Info,TeamAbbrev"]
    for p in slate.players[:40]:
        lines.append(f"{p.positions[0]},{p.name},{p.player_id},{p.positions[0]},"
                     f"{p.salary},{p.opponent}@{p.team},{p.team}")
    pool_path.write_text("\n".join(lines))
    out = tmp_path / "proj.csv"
    assert main(["project", "--sport", "nfl", "--players", str(pool_path),
                 "--markets", str(snap_path), "--out", str(out)]) == 0
    rows = out.read_text().splitlines()
    assert len(rows) == 41
    assert "vegas_backed_pct" in capsys.readouterr().out


def test_cli_scoring_prints_the_rules(capsys):
    assert main(["scoring", "--sport", "nfl", "--site", "dk"]) == 0
    assert "pass_yards" in capsys.readouterr().out


def test_build_is_reproducible():
    """Same inputs and seed must give the same portfolio, run to run and host to host."""
    def once():
        slate = build_demo_slate("nfl", seed=7)
        request = BuildRequest(sport="nfl", players=slate.players,
                               snapshot=slate.snapshot, n_lineups=5, n_candidates=15,
                               n_worlds=1200, field_entries=250, seed=4242,
                               synthetic=True)
        result = run_build(request)
        return [lu.signature() for lu in result.portfolio.lineups]

    assert once() == once()
