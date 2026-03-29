# AutoResearch for Agent Zero

Autonomous code optimization experiment loop. The agent generates hypotheses, edits code, benchmarks results, evaluates improvements, and iterates until convergence.

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
├── tools/
│   └── autoresearch.py
├── prompts/
│   └── agent.system.tool.autoresearch.md
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

## How to Use

Just talk to the agent in natural language. The skill triggers and tool are detected automatically.

### Starting an optimization

| Say this | What happens |
|----------|-------------|
| `Optimize my bogo_sort.py` | Starts a full loop with defaults (runtime, lower is better) |
| `Speed up this algorithm` | Agent asks which file, then starts |
| `Run autoresearch on algo.py targeting memory` | Custom metric name |
| `Optimize sorter.py, higher is better` | For metrics where bigger is better (e.g. throughput) |
| `Benchmark and optimize parser.py using "python test_parser.py"` | Custom benchmark command |
| `Optimize engine.py, max 10 runs` | Cap iterations at 10 |

The agent will then:

1. Call the `autoresearch` tool to initialize and benchmark baseline.
2. Read the code, analyze it, formulate a hypothesis.
3. Edit the file with the optimization.
4. Call the `autoresearch` tool again to benchmark and evaluate.
5. The tool keeps improvements, reverts regressions, shows sparkline trends.
6. Repeat until convergence or max runs.

### Mid-loop commands

Say any of these during an active optimization:

| Command | Effect |
|---------|--------|
| `Generate the autoresearch dashboard` | Writes `autoresearch-dashboard.md` and appends to `worklog.md` |
| `Show autoresearch history` | Lists all runs with `[+]` kept, `[-]` discarded, `[!]` error, `[~]` skipped |
| `Reset autoresearch state` | Backs up state to `.bak`, starts fresh |
| `Validate autoresearch state` | Checks JSONL integrity, reports issues |
| `Show autoresearch status` | Quick overview of target, metric, runs, best result |
| `Stop autoresearch` | Agent halts the loop |

### Example prompts

```
User: Optimize my bogo_sort.py
User: Speed up this function — it's too slow
User: Run autoresearch on my sorting code, try to get under 0.01s
User: Generate the dashboard
User: Show me the history
User: Keep going, try a different approach
```

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

### Architecture

| Layer | File | What it does |
|-------|------|-------------|
| Tool | `tools/autoresearch.py` | Tool subclass — the agent calls this directly |
| Prompt | `prompts/agent.system.tool.autoresearch.md` | Tells the agent the tool's parameters and JSON format |
| Skill | `skills/autoresearch/SKILL.md` | Step-by-step workflow the agent follows |
| Helpers | `helpers/state.py` | Pure Python — state, benchmarking, sparklines, dashboard |
| Hooks | `hooks.py` | Install/uninstall lifecycle |
| Config | `plugin.yaml` + `default_config.yaml` | Plugin manifest and defaults |

### Key design decisions

- **Two-call pattern.** Each iteration requires two tool calls: one to get baseline + instructions, one to evaluate after editing. This keeps the tool simple and the agent focused on reasoning.
- **Pure Python helpers.** `helpers/state.py` imports only stdlib — `json`, `subprocess`, `statistics`, `hashlib`. No Agent Zero dependencies.
- **JSONL state.** Each run is appended as a single JSON line. Concurrency-safe, easy to inspect, survives restarts.
- **Auto-revert.** Discarded or errored edits are automatically reverted by the tool.
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

Run #2 — discard
Run #3 — discard
Run #4 — discard
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
