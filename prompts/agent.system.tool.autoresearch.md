### autoresearch

Autonomous code optimization experiment loop. Use this tool to iteratively optimize code by generating hypotheses, editing files, benchmarking changes, and evaluating results.

**When to use:** When the user asks to optimize, speed up, or improve code performance through experimentation.

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| action | No | optimize | One of: optimize, dashboard, history, validate, reset, status |
| file | Yes (first call) | — | Target source file to optimize (e.g. `bogo_sort.py`) |
| metric | No | runtime | Metric being measured |
| metric_unit | No | s | Unit label |
| best_direction | No | lower | `lower` or `higher` |
| max_runs | No | 25 | Maximum experiment iterations |
| benchmark_command | No | — | Custom shell command (default: times `python <file>`) |
| benchmark_runs | No | 3 | Number of benchmark runs per iteration |
| hypothesis | No | — | Your optimization hypothesis (set after editing the file) |
| description | No | — | What you changed (set after editing the file) |

**Workflow — two calls per iteration:**

1. First call — get baseline and instructions:
```json
{
  "thoughts": ["Starting optimization loop on bogo_sort.py"],
  "headline": "Initialize AutoResearch optimization",
  "tool_name": "autoresearch",
  "tool_args": {
    "action": "optimize",
    "file": "bogo_sort.py",
    "metric": "runtime",
    "best_direction": "lower"
  }
}
```

2. Read the response, analyze the code, hypothesize, edit the file.

3. Second call — benchmark and evaluate your change:
```json
{
  "thoughts": ["Hypothesis: replace bogo sort with sorted()"],
  "headline": "Evaluate optimization run",
  "tool_name": "autoresearch",
  "tool_args": {
    "action": "optimize",
    "file": "bogo_sort.py",
    "hypothesis": "Replace bogo sort with Python built-in sorted() for O(n log n) time",
    "description": "Replaced random shuffle loop with return sorted(arr)"
  }
}
```

4. The tool benchmarks the change and tells you if it was kept or discarded.
5. Repeat from step 2 until convergence or max runs.

**Other actions:**

- `action=dashboard` — generate `autoresearch-dashboard.md`
- `action=history` — show all past runs
- `action=validate` — check state integrity
- `action=reset` — clear state, start fresh
- `action=status` — quick overview of current experiment
