# AutoResearch for Agent Zero

Autonomous code optimization experiment loop. Generates hypotheses, edits code, runs benchmarks, evaluates results, and iterates until convergence — fully agent-driven using built-in tools.

## Install

1. Clone this repo into your Agent Zero plugins directory (`usr/plugins/autoresearch/`), or submit a PR to [a0-plugins](https://github.com/agent0ai/a0-plugins).
2. Enable the plugin in your Agent Zero config.

## Structure

```
autoresearch/
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
├── bogo_sort.py
├── README.md
└── .gitignore
```

## Usage

The agent discovers the skill automatically. Just say:

```
Optimize my bogo_sort.py
```

or

```
Run autoresearch on algo.py targeting runtime
```

The agent will follow the SKILL.md instructions to run the full optimization loop using its built-in tools.

### Manual Skill Commands

You can also ask the agent to:

- **Generate dashboard** — "Generate the autoresearch dashboard"
- **Show history** — "Show autoresearch history"
- **Reset state** — "Reset autoresearch state"
- **Validate state** — "Validate autoresearch state"

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

The agent uses its built-in file read/write and terminal tools. The `helpers/state.py` module provides pure-Python utilities for state management, benchmarking, sparklines, and dashboard generation.

## State Files

- **`autoresearch.jsonl`** — persistent JSONL state (config + run results)
- **`autoresearch-dashboard.md`** — auto-generated summary with timeline and deltas
- **`worklog.md`** — dashboard snapshots appended over time

## Example: Bogo Sort

Copy `bogo_sort.py` into your project and say "Optimize bogo_sort.py". The agent will iteratively improve it (the original repo achieved a 7,802× speedup).

## Submitting to a0-plugins

1. Push this repo to GitHub.
2. Fork [a0-plugins](https://github.com/agent0ai/a0-plugins).
3. Add a folder `plugins/autoresearch/` containing:
   - `index.yaml` with your repo URL
   - `thumbnail.png` (optional)
4. Open a PR.

## License

MIT
