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
  - benchmark code
  - make faster
---

# AutoResearch — Autonomous Code Optimization

Use this skill to run an iterative optimization loop on a target file. The loop
generates hypotheses, edits code, benchmarks results, evaluates improvements,
and repeats until convergence.

## Before You Start

Tell the user what you are about to do:

> I'll run an AutoResearch optimization loop on `<file>`. The loop will:
> 1. Benchmark the current code
> 2. Analyze it for improvements
> 3. Apply an optimization
> 4. Benchmark the change
> 5. Keep improvements, revert regressions
> 6. Repeat until convergence

Then confirm or ask for:
- **Target file** (required, e.g. `bogo_sort.py`)
- **Metric** (default: `runtime`)
- **Metric unit** (default: `s`)
- **Direction** — `lower` or `higher` (default: `lower`)
- **Max runs** (default: `25`)
- **Benchmark command** (optional — defaults to timing `python <file>`)

## Import the Helpers

All state and benchmarking functions live in the helpers module. Import once at the top:

```python
from usr.plugins.autoresearch.helpers import state
```

## The Loop

### Phase 1: Initialize or Resume

Check whether `autoresearch.jsonl` exists.

**If it does not exist** — initialize:

```python
config = state.init_config(
    target_file="bogo_sort.py",
    metric="runtime",
    metric_unit="s",
    best_direction="lower",
    max_runs=25,
    benchmark_runs=3,
    benchmark_command=None,  # None = time python <file>
)
```

**If it exists** — load state and resume:

```python
s = state.load_state()
run_id = state.get_run_count() + 1
config = s["config"]
```

### Phase 2: Benchmark Baseline

```python
baseline = state.run_benchmark(target_file, benchmark_command, benchmark_runs)
```

- Returns `float` (median elapsed seconds) or `None` on failure.
- If `None`, stop and tell the user: "Benchmark failed on current source. Check the file and benchmark command."

### Phase 3: Read and Analyze

1. Read the target file using your file read tool.
2. Check previous runs for patterns:
   ```python
   prev = state.summarize_runs()
   ```
3. Analyze the code for optimization opportunities.
4. Formulate a clear hypothesis, e.g.:
   - "Replace bubble sort with Python's built-in sorted() for O(n log n) time"
   - "Use list comprehension instead of append loop to reduce overhead"
   - "Cache repeated expensive computation outside the loop"

### Phase 4: Edit

1. Save the source hash before editing:
   ```python
   source_hash_before = state.sha256(source_before)
   ```
2. Apply your optimization by editing the file using your file write tool.
3. Save a copy of the original source so you can revert if needed.

### Phase 5: Benchmark Modified Source

```python
new_metric = state.run_benchmark(target_file, benchmark_command, benchmark_runs)
```

If it fails (`None`):
1. Revert the file to the original source.
2. Log an error result (see Phase 7 with `status="error"`).
3. Tell the user: "Benchmark failed on modified source. File reverted."

### Phase 6: Evaluate

```python
source_hash_after = state.sha256(source_after)

if source_hash_before == source_hash_after:
    status = "skip"
else:
    improved = state.is_improvement(baseline, new_metric, best_direction)
    status = "keep" if improved else "discard"
```

- **keep** — optimization worked. Keep the file as-is.
- **discard** — no improvement. Revert the file to the original source.
- **skip** — file was not changed. Skip benchmark.

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

Generate sparklines for the result message:

```python
# Collect all metrics from state
s = state.load_state()
all_metrics = [r["metric"] for r in s["runs"]
               if r.get("type") != "config" and r.get("metric") is not None]

trend = state.sparkline(all_metrics)
bar = state.horizontal_bar(new_metric, min(all_metrics), max(all_metrics))
```

Show the result in this format:

```
## Run #3 Result
- Status: keep
- Before: 1.230000s
- After:  0.450000s
- Delta:  -63.41%
- Hypothesis: Replace bubble sort with sorted()
- Trend: ▁▃▅▇█ (3 runs)
- Range: 0.4500 ████████████░░░░ 4.2300

Best so far: Run #3 — 0.450000s (Replace bubble sort with sorted())
```

If the change was discarded, add:
> Call the skill again to try another approach.

### Phase 9: Check Convergence

```python
converged = state.check_convergence(window=3)
```

If `True` (last 3 runs all discarded):
- Tell the user: "Convergence detected: last 3 attempts did not improve the metric."
- Suggest: generating a dashboard, trying a fundamentally different approach, or stopping.

Check max runs:

```python
if state.get_run_count() >= config.get("maxRuns", 25):
    # Max runs reached — stop the loop
    pass
```

### Phase 10: Repeat or Stop

- **Converged or max runs** → generate dashboard, report final results, stop.
- **Otherwise** → go back to Phase 3 (Read and Analyze) for the next iteration.

## On-Demand Commands

The user can ask for these at any time during or after the loop:

### Generate Dashboard

```python
dashboard = state.generate_dashboard()
```

Writes `autoresearch-dashboard.md` and appends to `worklog.md`. Show the
dashboard content to the user.

### Show History

```python
history = state.format_history()
print(history)
```

### Validate State

```python
issues = state.validate_state()
if issues:
    print("Issues found:", issues)
else:
    print("State is valid.")
```

### Reset State

```python
backup_path = state.reset_state()
print(f"State reset. Backup saved to {backup_path}")
```

## Helper Functions Reference

All functions are in `usr.plugins.autoresearch.helpers.state`:

### State Management

| Function | Returns | Description |
|----------|---------|-------------|
| `load_state()` | `dict` | Load JSONL state. Returns `{"runs": [...], "config": {...}}` |
| `append_state(entry)` | `None` | Append a result entry to the JSONL file |
| `init_config(...)` | `dict` | Initialize experiment config header |
| `reset_state()` | `str` | Rename state file to `.bak`, return backup path |
| `validate_state()` | `list[str]` | Check state integrity, return list of issues |
| `get_run_count()` | `int` | Number of non-config entries recorded |

### Benchmarking

| Function | Returns | Description |
|----------|---------|-------------|
| `run_benchmark(file, cmd, runs)` | `float \| None` | Run benchmark, return median elapsed time. `cmd=None` times `python <file>` |

### Evaluation

| Function | Returns | Description |
|----------|---------|-------------|
| `is_improvement(before, after, dir)` | `bool` | Check if `after` is better than `before` given direction |
| `build_result_entry(...)` | `dict` | Build a complete result entry for logging |
| `find_best_run(runs)` | `dict \| None` | Find the best "keep" run |
| `find_worst_run(runs)` | `dict \| None` | Find the worst run across all statuses |
| `check_convergence(window=3)` | `bool` | True if last N runs were all "discard" |

### Reporting

| Function | Returns | Description |
|----------|---------|-------------|
| `generate_dashboard()` | `str` | Generate full markdown dashboard, write to file, return content |
| `format_history()` | `str` | Format compact history with `[+]`/`[-]`/`[!]`/`[~]` markers |
| `summarize_runs(last_n=5)` | `str` | Summarize recent runs for in-context display |

### Visualization

| Function | Returns | Description |
|----------|---------|-------------|
| `sparkline(values, width=20)` | `str` | Unicode sparkline: `▁▂▃▄▅▆▇█` |
| `horizontal_bar(value, lo, hi, width=16)` | `str` | Bar chart: `████████░░░░░░░░` |

### Utilities

| Function | Returns | Description |
|----------|---------|-------------|
| `sha256(content)` | `str` | Short SHA-256 hash (16 chars) |
| `git_commit_hash()` | `str` | Short git hash, or random fallback |

## JSONL State Format

Each line in `autoresearch.jsonl` is a JSON object:

**Config line (first line):**
```json
{
  "type": "config",
  "name": "optimize-bogo_sort.py",
  "targetFile": "bogo_sort.py",
  "metricName": "runtime",
  "metricUnit": "s",
  "bestDirection": "lower",
  "maxRuns": 25,
  "benchmarkRuns": 3,
  "startedAt": "2026-03-28T12:00:00+00:00"
}
```

**Result line (one per run):**
```json
{
  "run": 1,
  "targetFile": "bogo_sort.py",
  "hypothesis": "Replace bogo sort with sorted()",
  "description": "Replaced random shuffle loop with built-in sorted()",
  "metricBefore": 4.23,
  "metric": 0.001,
  "metricUnit": "s",
  "bestDirection": "lower",
  "status": "keep",
  "sourceHashBefore": "a1b2c3d4e5f67890",
  "sourceHashAfter": "f6e5d4c3b2a10987",
  "timestamp": "2026-03-28T12:01:30+00:00",
  "gitCommit": "abc1234",
  "deltaPercent": -99.9764
}
```

Status values: `keep`, `discard`, `error`, `skip`.

## Full Example Session

```
User: Optimize my bogo_sort.py

Agent: I'll run an AutoResearch optimization loop on bogo_sort.py.

Target: bogo_sort.py
Metric: runtime (s) — lower is better
Max runs: 25

[Imports helpers, initializes config, benchmarks baseline]

Baseline: 4.230000s (median of 3 runs)

Run #1
Hypothesis: Replace bogo_sort's random shuffle with Python's built-in sorted().
  sorted() uses Timsort — O(n log n) vs bogo sort's expected O(n!).
Description: Replaced bogo_sort() body with: return sorted(arr)
[Edits file, benchmarks]

Result: keep
Before: 4.230000s
After:  0.001000s
Delta:  -99.98%
Trend: ▁ (1 run)
Range: 0.0010 ████████░░░░░░░░ 4.2300

Best so far: Run #1 — 0.001000s

Run #2
Hypothesis: Pre-allocate the result list with known size.
[Edits file, benchmarks]

Result: discard (0.001200s — slower than 0.001000s)
File reverted.

Run #3 — discard
Run #4 — discard

Convergence detected: Last 3 runs discarded.
The sorted() optimization in Run #1 appears to be the best achievable improvement.

Dashboard written to autoresearch-dashboard.md
```

## Notes

- The agent uses its built-in tools (file read/write, bash, code execution).
- State persists across sessions via `autoresearch.jsonl`.
- The helper module does NOT import any Agent Zero internals — it is pure Python.
- All benchmarking runs in a subprocess with a 120s timeout.
- Benchmark uses median of N runs to reduce variance.
- The agent should save the original source before editing so it can revert.
- Sparklines auto-downsample to 20 characters for readability.
