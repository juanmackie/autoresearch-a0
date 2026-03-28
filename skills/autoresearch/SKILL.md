---
name: autoresearch
description: >
  Autonomous code optimization experiment loop. Use when the user asks to
  optimize, speed up, or improve code through iterative experimentation.
version: 1.0.0
tags: ["optimization", "benchmarking", "experiments", "code-improvement"]
triggers:
  - optimize code
  - speed up
  - improve performance
  - run experiments
  - autoresearch
  - benchmark loop
---

# AutoResearch — Autonomous Code Optimization

Use this skill to run an iterative optimization loop on a target file. The loop
generates hypotheses, edits code, benchmarks results, evaluates improvements,
and repeats until convergence.

## Quick Start

Tell the user what you are doing, then follow the loop below.

```
Target file: <file.py>
Metric: runtime (s) — lower is better
```

## The Loop

### Phase 1: Initialize or Resume

Check whether `autoresearch.jsonl` exists in the working directory.

- **If it does not exist**, ask the user for:
  1. Target file path (e.g. `bogo_sort.py`)
  2. Metric name (default: `runtime`)
  3. Metric unit (default: `s`)
  4. Direction: `lower` or `higher` (default: `lower`)
  5. Max runs (default: `25`)
  6. Benchmark command (optional — defaults to timing `python <file>`)

  Then use the helper to initialize:
  ```python
  from usr.plugins.autoresearch.helpers import state
  state.init_config(target_file, metric, metric_unit, best_direction, max_runs, benchmark_runs, benchmark_command)
  ```

- **If it exists**, load it and continue from the current run count.

### Phase 2: Benchmark Baseline

Run the benchmark on the current source to get a baseline value.

```python
from usr.plugins.autoresearch.helpers import state
baseline = state.run_benchmark(target_file, benchmark_command, benchmark_runs)
```

If the benchmark fails, stop and tell the user to check the file/command.

### Phase 3: Read and Analyze

1. Read the target file using your file read tool.
2. Analyze the code for optimization opportunities.
3. Formulate a hypothesis (e.g. "Replace bubble sort with sorted() for O(n log n)").
4. Check previous runs for patterns:
   ```python
   state.summarize_runs()
   ```

### Phase 4: Edit

Apply your optimization hypothesis by editing the file. Save the source hash
before editing for comparison:

```python
source_hash_before = state.sha256(source_before)
```

### Phase 5: Benchmark Modified Source

```python
new_metric = state.run_benchmark(target_file, benchmark_command, benchmark_runs)
```

If it fails, revert the file to the backup and log an error.

### Phase 6: Evaluate

```python
improved = state.is_improvement(baseline, new_metric, best_direction)
status = "keep" if improved else "discard"
```

- **keep**: The optimization worked. Keep the file as-is.
- **discard**: No improvement. Revert the file to the original source.

### Phase 7: Log Result

```python
result = state.build_result_entry(
    run_id=run_id,
    target_file=target_file,
    hypothesis=hypothesis,
    description=description,
    metric_before=baseline,
    metric_after=new_metric,
    metric_unit=metric_unit,
    best_direction=best_direction,
    source_hash_before=source_hash_before,
    source_hash_after=source_hash_after,
    status=status,
)
state.append_state(result)
```

### Phase 8: Report to User

Show a concise result with sparklines:

```python
trend = state.sparkline(all_metrics)
bar = state.horizontal_bar(new_metric, min(all_metrics), max(all_metrics))
```

Output format:
```
Run #3 Result
- Status: keep
- Before: 1.230000s
- After:  0.450000s
- Delta:  -63.41%
- Hypothesis: Replace bubble sort with sorted()
- Trend: ▁▃▅▇█ (3 runs)
- Range: 0.4500 ████████████░░░░ 4.2300

Best so far: Run #3 — 0.450000s (Replace bubble sort with sorted())
```

### Phase 9: Check Convergence

```python
converged = state.check_convergence(window=3)
```

If the last 3 runs were all discarded, inform the user:
- The optimization has likely converged.
- Suggest generating a dashboard or trying a different approach.
- If max_runs reached, stop.

### Phase 10: Repeat

Go back to Phase 3 (Read and Analyze) for the next iteration.

## Commands

The user can also ask for these at any time:

### Generate Dashboard

```python
dashboard = state.generate_dashboard()
```

Writes `autoresearch-dashboard.md` and appends to `worklog.md`. Show the
dashboard content to the user.

### Show History

```python
history = state.format_history()
```

### Validate State

```python
issues = state.validate_state()
```

### Reset State

```python
backup = state.reset_state()
```

## Helper Functions Reference

All functions are in `usr.plugins.autoresearch.helpers.state`:

| Function | Returns | Description |
|----------|---------|-------------|
| `load_state()` | `dict` | Load JSONL state |
| `append_state(entry)` | `None` | Append entry to JSONL |
| `init_config(...)` | `dict` | Write config header |
| `reset_state()` | `str` | Reset state, returns backup path |
| `validate_state()` | `list` | Returns list of issues |
| `run_benchmark(file, cmd, runs)` | `float` or `None` | Run benchmark, return median time |
| `is_improvement(before, after, dir)` | `bool` | Check if new metric is better |
| `build_result_entry(...)` | `dict` | Build a result entry |
| `find_best_run(runs)` | `dict` or `None` | Find best kept run |
| `find_worst_run(runs)` | `dict` or `None` | Find worst run |
| `generate_dashboard()` | `str` | Generate markdown dashboard |
| `format_history()` | `str` | Format run history |
| `summarize_runs()` | `str` | Summarize recent runs |
| `sparkline(values)` | `str` | Unicode sparkline |
| `horizontal_bar(val, lo, hi)` | `str` | Horizontal bar chart |
| `sha256(content)` | `str` | Short SHA-256 hash |
| `git_commit_hash()` | `str` | Short git hash |
| `get_run_count()` | `int` | Number of runs recorded |
| `check_convergence(window)` | `bool` | Check if last N runs discarded |

## Example Session

```
User: Optimize my bogo_sort.py

Agent: I'll run an AutoResearch optimization loop on bogo_sort.py.
Target: bogo_sort.py
Metric: runtime (s) — lower is better

[Initializes config, benchmarks baseline: 4.23s]

Run #1
Hypothesis: Replace bogo_sort with Python's built-in sorted()
[Benchmarks: 0.001s]
Result: keep (Δ -99.98%)
Trend: ▁ (1 run)

Run #2
Hypothesis: The sorted() approach is already optimal for this case.
[No change — skip]

Convergence detected after 3 discarded attempts.
Dashboard written to autoresearch-dashboard.md
```

## Notes

- The agent uses its built-in tools (file read/write, bash, code execution).
- State persists across sessions via `autoresearch.jsonl`.
- The helper module does NOT import any Agent Zero internals — it is pure Python.
- All benchmarking runs in a subprocess with a 120s timeout.
