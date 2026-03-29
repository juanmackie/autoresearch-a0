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

Use this skill to run an iterative optimization loop on a target file. The
`autoresearch` tool handles state management, benchmarking, evaluation, and
reporting. Your job is to hypothesize and edit the code.

## Before You Start

Tell the user what you are about to do:

> I'll run an AutoResearch optimization loop on `<file>`. The loop will:
> 1. Benchmark the current code
> 2. Analyze it for improvements
> 3. Apply an optimization
> 4. Benchmark the change
> 5. Keep improvements, revert regressions
> 6. Repeat until convergence

Confirm or ask for:
- **Target file** (required, e.g. `bogo_sort.py`)
- **Metric** (default: `runtime`)
- **Metric unit** (default: `s`)
- **Direction** — `lower` or `higher` (default: `lower`)
- **Max runs** (default: `25`)
- **Benchmark command** (optional — defaults to timing `python <file>`)

## The Tool

Call the `autoresearch` tool with `tool_name: autoresearch`. The tool accepts
these parameters via `tool_args`:

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| action | No | optimize | optimize, dashboard, history, validate, reset, status |
| file | First call | — | Target file |
| metric | No | runtime | Metric name |
| metric_unit | No | s | Unit label |
| best_direction | No | lower | `lower` or `higher` |
| max_runs | No | 25 | Max iterations |
| benchmark_command | No | — | Custom shell command |
| benchmark_runs | No | 3 | Runs per benchmark |
| hypothesis | No | — | Your optimization hypothesis |
| description | No | — | What you changed |

## The Loop

### Step 1: Initialize

Call the tool to start a new experiment:

```json
{
  "thoughts": ["Starting optimization on bogo_sort.py"],
  "headline": "Initialize AutoResearch",
  "tool_name": "autoresearch",
  "tool_args": {
    "action": "optimize",
    "file": "bogo_sort.py",
    "metric": "runtime",
    "metric_unit": "s",
    "best_direction": "lower"
  }
}
```

The tool will:
- Initialize `autoresearch.jsonl` with a config header
- Benchmark the current source as a baseline
- Return the baseline value, previous run summary, and sparkline trend

### Step 2: Analyze and Hypothesize

1. Read the target file using your file read tool.
2. Analyze the code for optimization opportunities.
3. Check the tool response for previous run patterns and sparkline trend.
4. Formulate a clear hypothesis, e.g.:
   - "Replace bubble sort with Python's built-in sorted() for O(n log n) time"
   - "Use list comprehension instead of append loop to reduce overhead"
   - "Cache repeated expensive computation outside the loop"

### Step 3: Edit the File

Apply your optimization hypothesis by editing the file using your file write
tool. Save the original source first so the tool can revert on failure.

### Step 4: Evaluate

Call the tool again with your hypothesis and description:

```json
{
  "thoughts": ["Evaluating: replaced bogo sort with sorted()"],
  "headline": "Evaluate optimization run",
  "tool_name": "autoresearch",
  "tool_args": {
    "action": "optimize",
    "file": "bogo_sort.py",
    "hypothesis": "Replace bogo sort with Python built-in sorted() for O(n log n)",
    "description": "Replaced random shuffle loop with return sorted(arr)"
  }
}
```

The tool will:
- Read the modified source and hash it
- Benchmark the modified code (median of N runs)
- Compare against baseline: **keep** if improved, **discard** if not
- Revert the file on discard
- Log the result to `autoresearch.jsonl`
- Return a result summary with sparkline trend and range bar

### Step 5: Check Results

Read the tool response. It includes:
- **Status:** keep, discard, skip, or error
- **Before / After** metric values and delta percentage
- **Trend:** sparkline showing metric trajectory across all runs
- **Range:** horizontal bar showing where the result falls
- **Best so far:** the best kept run
- **Convergence:** if last 3 runs were discarded

### Step 6: Repeat or Stop

- **Converged** → tell the user, suggest dashboard or new approach.
- **Max runs reached** → stop, suggest dashboard.
- **Otherwise** → go back to Step 2.

## On-Demand Commands

Ask the agent or call the tool directly:

| What to say | Tool action |
|-------------|-------------|
| "Generate the autoresearch dashboard" | `action=dashboard` |
| "Show autoresearch history" | `action=history` |
| "Reset autoresearch state" | `action=reset` |
| "Validate autoresearch state" | `action=validate` |
| "Show autoresearch status" | `action=status` |

Example call:
```json
{
  "tool_name": "autoresearch",
  "tool_args": {
    "action": "dashboard"
  }
}
```

## State Files

| File | Purpose |
|------|---------|
| `autoresearch.jsonl` | Persistent experiment state (config + run results) |
| `autoresearch.jsonl.bak` | Backup after reset |
| `autoresearch-dashboard.md` | Auto-generated summary with timeline |
| `worklog.md` | Dashboard snapshots appended over time |

## JSONL State Format

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

## Full Example

```
User: Optimize my bogo_sort.py

Agent: I'll run an AutoResearch loop on bogo_sort.py.
Target: bogo_sort.py | Metric: runtime (s) | Lower is better

[Agent calls autoresearch tool with action=optimize, file=bogo_sort.py]

Tool response: Baseline 4.230000s. Call again with hypothesis and description.

[Agent reads bogo_sort.py, analyzes it, edits to use sorted()]

[Agent calls autoresearch tool with action=optimize, hypothesis=..., description=...]

Tool response:
  ## Run #1 Result
  - Status: keep
  - Before: 4.230000s
  - After:  0.001000s
  - Delta:  -99.98%
  - Hypothesis: Replace bogo sort with sorted()
  - Trend: ▁ (1 run)
  - Range: 0.0010 ████████░░░░░░░░ 4.2300

  Best so far: Run #1 — 0.001000s

[Agent continues — Run #2 discards, Run #3 discards, Run #4 discards]

Tool response: Convergence detected. Last 3 runs discarded.

[Agent calls autoresearch tool with action=dashboard]
```

## Notes

- The `autoresearch` tool handles all state, benchmarking, evaluation, and file revert.
- You focus on hypothesis generation and code editing.
- Benchmark runs in a subprocess with a 120s timeout.
- Benchmark uses median of N runs to reduce variance.
- The tool auto-reverts discarded edits — you don't need to revert manually.
- Sparklines auto-downsample to 20 characters for readability.
