# Running a slate

Plain instructions for building a real portfolio end to end. You run this on
your own computer — a Mac or PC you control, not a browser tab.

Budget 20 minutes for the one-time setup. After that a slate takes about five
minutes, most of it waiting.

---

## One-time setup

**1. Check you have Python 3.11 or newer.** Open Terminal (Mac: Cmd+Space, type
"Terminal") or PowerShell (Windows: Start, type "PowerShell") and run:

```bash
python3 --version
```

If it says 3.11 or higher, you're set. If it errors or shows something older,
install it from [python.org/downloads](https://www.python.org/downloads/) and
close and reopen the terminal.

**2. Download the engine and install it.**

```bash
git clone -b claude/dfs-lineup-props-engine-s3yloj https://github.com/skelter42/DFS-Engine.git
cd DFS-Engine
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
```

That last line prints a lot. As long as it ends without the word `error`,
you're fine.

**3. Prove it works** — this runs the whole pipeline on made-up data, no
internet needed:

```bash
dfs-engine demo --sport nfl --out slates/demo
```

About 30 seconds. Then open `slates/demo/report.html` in your browser. If you
see the report, the install is good and you never have to do steps 1–3 again.

**4. Get an odds API key.** Sign up at
[the-odds-api.com](https://the-odds-api.com) — the free tier covers a few
slates a month, paid tiers are cheap. Copy your key, then:

```bash
export ODDS_API_KEY=paste_your_key_here       # Windows: set ODDS_API_KEY=paste_your_key_here
```

You need to run that line each time you open a new terminal. (To make it
permanent on Mac, add it to the bottom of `~/.zshrc`.)

---

## Every slate

Open your terminal, then:

```bash
cd DFS-Engine
source .venv/bin/activate          # Windows: .venv\Scripts\activate
export ODDS_API_KEY=your_key       # Windows: set ODDS_API_KEY=your_key
```

### Step 1 — Download two files from DraftKings

From the contest lobby:

- **The salary file.** On the contest page, "Export to CSV". Saves as
  `DKSalaries.csv`. This is the player pool.
- **The entry template.** Enter the contests you want *first*, then go to
  My Contests → Lineups → "Export/Import Lineups" and download the template. It
  arrives as `DKEntries.csv`, one row per entry you own, with the roster columns
  blank. The engine fills those in for you.

Note where they saved — usually `~/Downloads`.

### Step 2 — Sweep the sportsbooks

```bash
dfs-engine fetch-props --sport nfl --out markets.json
dfs-engine inspect --markets markets.json
```

The second command prints what it found. **Read it.** You want to see a healthy
`prop_markets` count and several names under `books`. If `prop_markets` is 0 or
the `errors` list is long, stop — something is wrong upstream and the build
would be guessing. See troubleshooting below.

### Step 3 — Describe your contests

Open `examples/contests.json` in any text editor and edit it to match what you
actually entered. For each contest:

- `name` — must match the contest name in your DraftKings entry template
- `entries` — how many lineups you're entering there
- `field_size` — total entries in the contest
- `entry_fee` — the buy-in
- `priority` — 1 for your most important contest, 2 for the next, and so on

Save it. The `entries` numbers across all contests should add up to the number
of lineups you want built.

### Step 4 — Build

```bash
dfs-engine build --sport nfl \
    --players ~/Downloads/DKSalaries.csv \
    --markets markets.json \
    --contests examples/contests.json \
    --dk-template ~/Downloads/DKEntries.csv \
    --lineups 20 \
    --out slates/today
```

Two to three minutes. It prints its progress, then a summary.

### Step 5 — Look before you upload

Open `slates/today/report.html`. Four things to check, in order:

1. **Final audit says PASSED.** If it says FAILED, the reasons are listed —
   fix and rebuild rather than uploading.
2. **Projection confidence.** If most of your pool is tier C or D, the markets
   were thin and the build is leaning on assumptions. Re-run `fetch-props`
   closer to lock when more props are posted.
3. **Effective independent lineups.** If 20 lineups are worth 3 independent
   shots, you're less diversified than the lineup count suggests. That may be
   fine if you have a strong thesis — it should be a decision, not a surprise.
4. **Exposure against the field.** The big overweights are your actual
   positions this slate. If one of them doesn't match a view you'd defend out
   loud, that's the one to look at.

### Step 6 — Upload

`slates/today/dk_entries.csv` is your DraftKings template with the roster
columns filled in. Upload it back through the same Export/Import Lineups page.
Your Entry IDs and contest assignments are untouched — only the players were
written.

Then re-check news before lock. If anything material changed, rebuild: it's
three minutes.

---

## When something goes wrong

**`dfs-engine: command not found`** — you skipped `source .venv/bin/activate`.
Run it and try again.

**`fetch-props` finds nothing** — check `ODDS_API_KEY` is set (`echo
$ODDS_API_KEY` should print it), and that you have credits left on your plan.
Props usually post the day before for NFL; earlier than that there's nothing to
find.

**"template roster columns not found"** — you passed the salary file to
`--dk-template` instead of the entry template. They're different downloads.

**"no template row to go in"** — you built more lineups than you have entries.
Either enter more contests or lower `--lineups`.

**A player you know is out still appears** — the engine only knows what's in
the files. Either re-export the salary file after DraftKings removes them, or
add a `Status` column to the salary CSV with `OUT` on that row.

---

## Knobs worth turning

| Flag | What it does |
|---|---|
| `--lineups 20` | How many lineups to build |
| `--worlds 50000` | More simulated worlds: slower, steadier tail numbers. 20,000 is fine for exploring, 50,000+ for a serious build |
| `--candidates 300` | Bigger candidate pool to choose from |
| `--min-uniques 3` | Force more difference between lineups |
| `--selection uniqueness_ladder` | Switch to the projection-first flow: highest-projection pool, maximum uniqueness, then recover points |
| `--vendor savant.csv` | Feed in Sim Savant or another projection file as the fallback for players with no market |
| `--profile cash` | Optimize for cash games instead of tournaments |
| `--variant showdown` | Single-game showdown slates |

Run `dfs-engine build --help` for the full list, and
`dfs-engine scoring --sport nfl` to print the scoring table the engine is using
— worth checking against DraftKings once a season.

---

## What the engine will not do for you

It does the math. It does not know that a coach said something in a Friday
presser, that the wind is picking up, or that you have a read on a matchup the
market hasn't priced. The report tells you where it is confident and where it
is assuming; the decision to enter is still yours.
