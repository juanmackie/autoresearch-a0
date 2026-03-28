# AutoResearch for Agent Zero

Autonomous code optimization experiment loop. The agent generates hypotheses, edits code, benchmarks results, evaluates improvements, and iterates until convergence — all using its built-in tools.

## Install

### From a0-plugins (once merged)

Enable the plugin in Agent Zero. It will be discovered automatically.

### Manual install

1. Clone or download this repo.
2. Copy the entire folder into `usr/plugins/autoresearch/`.
3. Restart Agent Zero or refresh plugins.

```
usr/plugins/autoresearch/
├── __init__.py
├── plugin.yaml
├── default_config.yaml
├── hooks.py
├── helpers/
│   ├── __init__.py
│   └── state.py
├── skills/
│   └── autoresearch/
│       └── SKILL.md
├── bogo_sort.py          ← example (optional)
├── README.md
└── .gitignore
```

## Usage

Just ask the agent. The skill triggers are detected automatically.

```
Optimize my bogo_sort.py
Speed up this algorithm
Run autoresearch on algo.py targeting runtime
```

The agent will:

1. Ask for target file and metric settings (or use defaults).
2. Benchmark the current code as a baseline.
3. Analyze the code and propose a hypothesis.
4. Edit the file with the optimization.
5. Benchmark the change.
6. Keep improvements, revert regressions.
7. Show results with sparkline trends.
8. Repeat until convergence or max runs.

### At any time, ask the agent to:

- **"Generate the autoresearch dashboard"** — writes `autoresearch-dashboard.md`
- **"Show autoresearch history"** — list all past runs with status markers
- **"Reset autoresearch state"** — clear state and start fresh
- **"Validate autoresearch state"** — check JSONL integrity

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Hypothesize │────▶│  Edit Code   │────▶│  Benchmark    │
└─────────────┘     └──────────────┘     └───────┬───────┘
                                                  │
                    ┌──────────────┐     ┌────────▼──────┐
                    │  Log Result  │◀────│  Evaluate     │
                    └──────┬───────┘     └───────────────┘
                           │
                    ┌──────▼───────┐
                    │  Dashboard   │
                    └──────────────┘
```

The agent uses its built-in file read/write and terminal tools. The `helpers/state.py` module provides pure-Python utilities — no Agent Zero imports, no side effects.

### Architecture

| Layer | What it does |
|-------|-------------|
| `skills/autoresearch/SKILL.md` | Instructions the agent loads to know the full loop |
| `helpers/state.py` | Pure Python: state, benchmarking, sparklines, dashboard |
| `hooks.py` | Install/uninstall lifecycle hooks |
| `plugin.yaml` | Plugin manifest |

### Key design decisions

- **No Tool subclass.** Agent Zero doesn't use a `Tool` class system. The agent runs code via its built-in execution tools.
- **Pure Python helpers.** `helpers/state.py` imports only stdlib — `json`, `subprocess`, `statistics`, `hashlib`. No Agent Zero dependencies.
- **JSONL state.** Each run is appended as a single JSON line. Concurrency-safe, easy to inspect, survives restarts.
- **Auto-revert.** Discarded or errored edits are automatically reverted to the source backup.
- **Convergence detection.** 3 consecutive discards signals the agent to stop or try a different approach.

## State Files

| File | Purpose |
|------|---------|
| `autoresearch.jsonl` | Persistent experiment state (config + run results) |
| `autoresearch.jsonl.bak` | Backup after reset |
| `autoresearch-dashboard.md` | Auto-generated summary with timeline and deltas |
| `worklog.md` | Dashboard snapshots appended over time |

## Example: Bogo Sort

`bogo_sort.py` is included as a demo. It uses bogo sort (random shuffling) — intentionally slow.

```
User: Optimize bogo_sort.py

Agent: I'll run an AutoResearch loop on bogo_sort.py.
Target: bogo_sort.py | Metric: runtime (s) | Lower is better

Baseline: 4.230000s

Run #1
Hypothesis: Replace bogo_sort with Python's built-in sorted()
Result: keep
Before: 4.230000s → After: 0.001000s (Δ -99.98%)
Trend: ▁ (1 run)
Range: 0.0010 ████████░░░░░░░░ 4.2300

Run #2
Hypothesis: sorted() is already optimal for this input size.
Result: discard
Trend: ▁▁ (2 runs)

Run #3 — discard, Run #4 — discard
Convergence detected: Last 3 runs discarded.

Dashboard written to autoresearch-dashboard.md
```

## Submitting to a0-plugins

1. Push this repo to GitHub.
2. Fork [a0-plugins](https://github.com/agent0ai/a0-plugins).
3. Add `plugins/autoresearch/index.yaml`:
   ```yaml
   title: AutoResearch
   description: Autonomous code optimization experiment loop.
   github: https://github.com/YOUR_USER/autoresearch-a0
   tags:
     - optimization
     - benchmarking
     - experiments
   ```
4. Optionally add `plugins/autoresearch/thumbnail.png`.
5. Open a PR.

## License

MIT
