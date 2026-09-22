"""Self-contained HTML build report.

One file, no external assets, openable straight from disk. It shows the same
content as ``audit.md`` but arranged for scanning: coverage first (can these
projections be trusted?), then the portfolio, then exposure versus expected
ownership, then the portfolio-level simulation.
"""

from __future__ import annotations

import html
from pathlib import Path

from ..pipeline import BuildResult
from .writers import slate_thesis

CSS = """
:root {
  --bg: #f6f7f9; --panel: #ffffff; --ink: #14181f; --muted: #5d6673;
  --line: #e2e6ec; --accent: #1f6feb; --good: #1a7f4b; --warn: #b4690e;
  --bad: #b42318; --chip: #eef2f7;
}
:root:not([data-theme="light"]) { }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f1216; --panel: #161b22; --ink: #e6edf3; --muted: #9aa5b1;
    --line: #262d36; --accent: #58a6ff; --good: #3fb950; --warn: #d29922;
    --bad: #f85149; --chip: #1f2630;
  }
}
:root[data-theme="dark"] {
  --bg: #0f1216; --panel: #161b22; --ink: #e6edf3; --muted: #9aa5b1;
  --line: #262d36; --accent: #58a6ff; --good: #3fb950; --warn: #d29922;
  --bad: #f85149; --chip: #1f2630;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.55 ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.wrap { max-width: 1180px; margin: 0 auto; padding: 32px 16px 80px; }
h1 { font-size: 26px; margin: 0 0 4px; letter-spacing: -0.01em; }
h2 { font-size: 18px; margin: 34px 0 12px; letter-spacing: -0.01em; }
h3 { font-size: 15px; margin: 20px 0 8px; color: var(--muted); font-weight: 600;
     text-transform: uppercase; letter-spacing: 0.06em; }
.sub { color: var(--muted); margin: 0 0 22px; font-size: 14px; }
.banner { background: color-mix(in srgb, var(--warn) 14%, var(--panel));
  border: 1px solid var(--warn); color: var(--ink); padding: 12px 14px;
  border-radius: 10px; margin-bottom: 20px; font-size: 14px; }
.grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(178px, 1fr)); }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  padding: 14px 16px; }
.card .k { color: var(--muted); font-size: 12px; text-transform: uppercase;
  letter-spacing: 0.06em; }
.card .v { font-size: 22px; font-weight: 650; margin-top: 4px;
  font-variant-numeric: tabular-nums; }
.card .n { color: var(--muted); font-size: 12px; margin-top: 2px; }
table { width: 100%; border-collapse: collapse; background: var(--panel);
  border: 1px solid var(--line); border-radius: 12px; overflow: hidden; font-size: 13.5px; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--line);
  white-space: nowrap; }
th { color: var(--muted); font-weight: 600; font-size: 11.5px; text-transform: uppercase;
  letter-spacing: 0.05em; background: var(--chip); position: sticky; top: 0; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
tr:last-child td { border-bottom: none; }
.scroll { overflow-x: auto; border-radius: 12px; }
.chip { display: inline-block; padding: 1px 8px; border-radius: 999px;
  background: var(--chip); color: var(--muted); font-size: 11.5px; margin-right: 4px; }
.pos { color: var(--good); } .neg { color: var(--bad); }
ul.notes { padding-left: 18px; } ul.notes li { margin: 5px 0; }
.wrapline { white-space: normal; min-width: 260px; color: var(--muted); font-size: 12.5px; }
footer { margin-top: 44px; color: var(--muted); font-size: 12.5px;
  border-top: 1px solid var(--line); padding-top: 14px; }
@media (max-width: 640px) { .wrap { padding: 20px 16px 60px; } h1 { font-size: 22px; } }
"""


def _esc(value) -> str:
    return html.escape(str(value))


def _pct(value, digits=2) -> str:
    try:
        return f"{float(value):.{digits}%}"
    except (TypeError, ValueError):
        return "-"


def _card(key: str, value: str, note: str = "") -> str:
    note_html = f'<div class="n">{_esc(note)}</div>' if note else ""
    return (f'<div class="card"><div class="k">{_esc(key)}</div>'
            f'<div class="v">{_esc(value)}</div>{note_html}</div>')


def render_html(result: BuildResult) -> str:
    meta = result.meta
    d = result.portfolio.diagnostics
    pm = result.portfolio.metrics
    cov = d.get("coverage", {})
    mc = d.get("market_coverage", {})
    sport = str(meta.get("sport", "")).upper()
    site = str(meta.get("site", "")).upper()

    parts: list[str] = []
    a = parts.append

    a("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    a("<meta name='viewport' content='width=device-width, initial-scale=1'>")
    a(f"<title>{_esc(sport)} Portfolio Report</title>")
    a(f"<style>{CSS}</style></head><body><div class='wrap'>")

    a(f"<h1>{_esc(sport)} {_esc(site)} portfolio</h1>")
    a(f"<p class='sub'>{_esc(meta.get('generated_at', ''))} &middot; engine "
      f"{_esc(meta.get('engine_version', ''))} &middot; "
      f"{len(result.portfolio.lineups)} lineups &middot; "
      f"sources: {_esc(', '.join(meta.get('market_sources') or ['none']))}</p>")

    if meta.get("synthetic"):
        a(f"<div class='banner'><strong>Synthetic slate.</strong> "
          f"{_esc(meta.get('warning', ''))}</div>")

    # Headline metrics
    a("<div class='grid'>")
    a(_card("Vegas-backed pool", f"{cov.get('vegas_backed_pct', 0)}%",
            f"tier A+B of {cov.get('players', 0)} players"))
    a(_card("Market weight", f"{cov.get('mean_market_weight', 0)}",
            "mean weight on market vs vendor prior"))
    a(_card("Any lineup top 1%", _pct(pm.get("any_top1_rate", 0)),
            "of simulated worlds"))
    a(_card("Any lineup top 0.1%", _pct(pm.get("any_top01_rate", 0), 3),
            "of simulated worlds"))
    a(_card("Effective lineups", f"{pm.get('effective_lineups', 0):.1f}",
            f"of {pm.get('n_lineups', 0)} entered"))
    a(_card("Worlds simulated", f"{meta.get('simulation', {}).get('iterations', 0):,}",
            f"{meta.get('simulation', {}).get('factors', 0)} latent factors"))
    a("</div>")

    # Thesis
    a("<h2>Slate thesis</h2><ul class='notes'>")
    for line in slate_thesis(result):
        a(f"<li>{_esc(line)}</li>")
    a("</ul>")

    # Coverage
    a("<h2>Projection confidence</h2><div class='scroll'><table>")
    a("<tr><th>Tier</th><th>Meaning</th><th class='num'>Players</th>"
      "<th class='num'>Share</th></tr>")
    for tier, info in (cov.get("tiers") or {}).items():
        a(f"<tr><td>{_esc(tier)}</td><td>{_esc(info['label'])}</td>"
          f"<td class='num'>{info['count']}</td><td class='num'>{info['pct']}%</td></tr>")
    a("</table></div>")
    a(f"<p class='sub'>Sweep touched {mc.get('players_with_any_market', 0)} of "
      f"{mc.get('pool_size', 0)} players ({mc.get('coverage_pct', 0)}%) across books: "
      f"{_esc(', '.join(mc.get('books') or ['none']))}.</p>")

    # Portfolio
    a("<h2>Portfolio</h2><div class='scroll'><table>")
    a("<tr><th>#</th><th>Contest</th><th class='num'>Salary</th><th class='num'>Proj</th>"
      "<th class='num'>Ceiling</th><th class='num'>Own sum</th><th class='num'>Top 1%</th>"
      "<th class='num'>Top 0.1%</th><th class='num'>Dup</th><th>Script</th><th>Roster</th></tr>")
    for i, lu in enumerate(result.portfolio.lineups, start=1):
        m = lu.metrics
        roster = ", ".join(f"{s} {p.name}" for p, s in zip(lu.players, lu.slots))
        a(f"<tr><td class='num'>{i}</td><td>{_esc(lu.contest or '-')}</td>"
          f"<td class='num'>${lu.salary:,}</td><td class='num'>{lu.projection:.1f}</td>"
          f"<td class='num'>{float(m.get('ceiling_sum', 0)):.1f}</td>"
          f"<td class='num'>{float(m.get('total_ownership', 0)):.0f}%</td>"
          f"<td class='num'>{_pct(m.get('top1_rate', 0))}</td>"
          f"<td class='num'>{_pct(m.get('top01_rate', 0), 3)}</td>"
          f"<td class='num'>{float(m.get('dup_estimate', 0)):.1f}</td>"
          f"<td><span class='chip'>{_esc(lu.labels.get('risk', ''))}</span>"
          f"{_esc(lu.labels.get('stack', ''))}</td>"
          f"<td class='wrapline'>{_esc(roster)}</td></tr>")
    a("</table></div>")

    # Exposure
    a("<h2>Source ownership vs engine exposure</h2><div class='scroll'><table>")
    a("<tr><th>Player</th><th>Team</th><th>Pos</th><th>Coverage</th>"
      "<th class='num'>Engine proj</th><th class='num'>Engine own</th>"
      "<th class='num'>Exposure</th><th class='num'>Diff (pp)</th><th>Reason</th></tr>")
    for row in d.get("exposure_table", []):
        diff = float(row["difference_pp"])
        cls = "pos" if diff > 0 else ("neg" if diff < 0 else "")
        a(f"<tr><td>{_esc(row['name'])}</td><td>{_esc(row['team'])}</td>"
          f"<td>{_esc(row['position'])}</td><td>{_esc(row['coverage'])}</td>"
          f"<td class='num'>{row['engine_projection']}</td>"
          f"<td class='num'>{row['engine_ownership']}%</td>"
          f"<td class='num'>{row['exposure_pct']}%</td>"
          f"<td class='num {cls}'>{diff:+.1f}</td>"
          f"<td class='wrapline'>{_esc(row['reason'])}</td></tr>")
    a("</table></div>")

    # Allocation
    a("<h2>Contest allocation</h2><div class='scroll'><table>")
    a("<tr><th>Contest</th><th class='num'>Lineups</th><th class='num'>Unique</th>"
      "<th class='num'>Avg proj</th><th class='num'>Avg top 1%</th>"
      "<th class='num'>Avg own</th><th>Risk families</th><th>Flags</th></tr>")
    for row in d.get("allocation_audit", []):
        a(f"<tr><td>{_esc(row.get('contest'))}</td>"
          f"<td class='num'>{row.get('lineups')}</td>"
          f"<td class='num'>{row.get('unique_lineups')}</td>"
          f"<td class='num'>{row.get('avg_projection')}</td>"
          f"<td class='num'>{_pct(row.get('avg_top1_rate', 0))}</td>"
          f"<td class='num'>{row.get('avg_total_ownership')}%</td>"
          f"<td>{_esc(row.get('risk_families'))}</td>"
          f"<td class='wrapline'>{_esc('; '.join(row.get('flags', [])) or 'none')}</td></tr>")
    a("</table></div>")

    # Portfolio simulation + hidden concentration
    a("<h2>Portfolio simulation</h2><div class='grid'>")
    a(_card("Mean pairwise correlation", f"{pm.get('world_overlap', 0):.3f}",
            "lineup scores across worlds"))
    a(_card("Tail worlds shared", _pct(pm.get("winning_world_overlap", 0), 1),
            "top-1% worlds won by 2+ lineups"))
    a(_card("Expected payout", f"{pm.get('total_expected_payout', 0):.5f}",
            "share of the prize pool"))
    a(_card("Team HHI", f"{pm.get('concentration', {}).get('team_hhi', 0)}",
            f"{int(pm.get('concentration', {}).get('distinct_teams', 0))} teams used"))
    a("</div>")
    hc = d.get("hidden_concentration", {})
    a("<h3>Hidden concentration in tail worlds</h3><p class='sub'>")
    a("Teams: " + _esc(", ".join(f"{t['team']} {t['share_pct']}%"
                                 for t in hc.get("top_teams", []))) + "<br>")
    a("Games: " + _esc(", ".join(f"{g['game']} {g['share_pct']}%"
                                 for g in hc.get("top_games", []))) + "</p>")

    # Risk + audit
    flags = d.get("risk_flags", []) + d.get("ownership_flags", [])
    a("<h2>Risk flags</h2><ul class='notes'>")
    if flags:
        for flag in flags:
            a(f"<li>{_esc(flag)}</li>")
    else:
        a("<li>None raised by the automated checks. Re-run closer to lock for late news.</li>")
    a("</ul>")

    fa = d.get("final_audit", {})
    a("<h2>Final audit</h2><ul class='notes'>")
    a(f"<li><strong>Status: {'PASSED' if fa.get('passed') else 'FAILED'}</strong></li>")
    for check in fa.get("checks", []):
        a(f"<li>{_esc(check)}</li>")
    for failure in fa.get("failures", []):
        a(f"<li class='neg'><strong>{_esc(failure)}</strong></li>")
    a("</ul>")

    a("<footer>Mathematical output only. <code>core/ENGINE.md</code> requires an explicit "
      "strategic review of this portfolio before entry: confirm the exposures express "
      "intended slate theses rather than optimizer repetition, and re-run after late news."
      "</footer>")
    a("</div></body></html>")
    return "\n".join(parts)


def write_html(result: BuildResult, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(result), encoding="utf-8")
    return path
