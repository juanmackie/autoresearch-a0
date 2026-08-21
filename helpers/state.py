import json
import os
import hashlib
import subprocess
import time
import statistics
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

STATE_FILE = "autoresearch.jsonl"
DASHBOARD_FILE = "autoresearch-dashboard.md"
WORKLOG_FILE = "worklog.md"
MAX_RUNS_DEFAULT = 25
BENCHMARK_RUNS = 3


# ------------------------------------------------------------------ #
#  State management
# ------------------------------------------------------------------ #

def load_state(state_file: str = STATE_FILE) -> Dict:
    if os.path.exists(state_file):
        runs: List[Dict] = []
        config: Optional[Dict] = None
        with open(state_file, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    runs.append(entry)
                    if entry.get("type") == "config" and config is None:
                        config = entry
                except json.JSONDecodeError:
                    pass
        return {"runs": runs, "config": config}
    return {"runs": [], "config": None}


def append_state(entry: Dict, state_file: str = STATE_FILE):
    with open(state_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, default=str) + "\n")


def init_config(target_file: str, metric: str, metric_unit: str,
                best_direction: str, max_runs: int, benchmark_runs: int,
                benchmark_command: Optional[str] = None,
                state_file: str = STATE_FILE) -> Dict:
    config = {
        "type": "config",
        "name": f"optimize-{os.path.basename(target_file)}",
        "targetFile": target_file,
        "metricName": metric,
        "metricUnit": metric_unit,
        "bestDirection": best_direction,
        "maxRuns": max_runs,
        "benchmarkRuns": benchmark_runs,
        "startedAt": datetime.now(timezone.utc).isoformat(),
    }
    if benchmark_command:
        config["benchmarkCommand"] = benchmark_command
    append_state(config, state_file)
    return config


def reset_state(state_file: str = STATE_FILE) -> str:
    if os.path.exists(state_file):
        backup = state_file + ".bak"
        os.replace(state_file, backup)
        return backup
    return ""


def validate_state(state_file: str = STATE_FILE) -> List[str]:
    state = load_state(state_file)
    runs = state["runs"]
    if not runs:
        return ["State is empty."]

    issues: List[str] = []
    has_config = any(r.get("type") == "config" for r in runs)
    if not has_config:
        issues.append("Missing config entry.")

    run_ids = [r.get("run") for r in runs if r.get("run") is not None]
    expected = list(range(1, len(run_ids) + 1))
    if run_ids != expected:
        issues.append(f"Run IDs not sequential: {run_ids}")

    for r in runs:
        if r.get("type") != "config" and "status" not in r:
            issues.append(f"Run #{r.get('run', '?')} missing 'status' field.")

    return issues


# ------------------------------------------------------------------ #
#  Benchmarking
# ------------------------------------------------------------------ #

def run_benchmark(target_file: str, benchmark_command: Optional[str],
                  benchmark_runs: int) -> Optional[float]:
    """Run the benchmark and return the median elapsed time, or None on failure."""
    if benchmark_command:
        return _run_command_benchmark(benchmark_command, benchmark_runs)
    return _run_python_benchmark(target_file, benchmark_runs)


def _run_command_benchmark(command: str, runs: int) -> Optional[float]:
    timings: List[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        try:
            proc = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=120
            )
            elapsed = time.perf_counter() - start
            if proc.returncode != 0:
                return None
            timings.append(elapsed)
        except (subprocess.TimeoutExpired, Exception):
            return None
    return statistics.median(timings)


def _run_python_benchmark(target_file: str, runs: int) -> Optional[float]:
    timings: List[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        try:
            proc = subprocess.run(
                ["python", target_file],
                capture_output=True, text=True, timeout=120,
            )
            elapsed = time.perf_counter() - start
            if proc.returncode != 0:
                return None
            timings.append(elapsed)
        except (subprocess.TimeoutExpired, Exception):
            return None
    return statistics.median(timings)


# ------------------------------------------------------------------ #
#  Evaluation
# ------------------------------------------------------------------ #

def is_improvement(before: float, after: float, direction: str) -> bool:
    if direction == "lower":
        return after < before
    return after > before


def build_result_entry(run_id: int, target_file: str, hypothesis: str,
                       description: str, metric_before: Optional[float],
                       metric_after: Optional[float], metric_unit: str,
                       best_direction: str, source_hash_before: str,
                       source_hash_after: str, status: str,
                       notes: Optional[str] = None) -> Dict:
    entry = {
        "run": run_id,
        "targetFile": target_file,
        "hypothesis": hypothesis,
        "description": description,
        "metricBefore": metric_before,
        "metric": metric_after,
        "metricUnit": metric_unit,
        "bestDirection": best_direction,
        "status": status,
        "sourceHashBefore": source_hash_before,
        "sourceHashAfter": source_hash_after,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gitCommit": git_commit_hash(),
    }
    if notes:
        entry["notes"] = notes
    if metric_before and metric_after and metric_before != 0:
        delta = metric_after - metric_before
        entry["deltaPercent"] = round(delta / metric_before * 100, 4)
    return entry


def find_best_run(runs: List[Dict]) -> Optional[Dict]:
    kept = [r for r in runs if r.get("status") == "keep" and r.get("metric") is not None]
    if not kept:
        return None
    config = next((r for r in runs if r.get("type") == "config"), {})
    direction = config.get("bestDirection", "lower")
    if direction == "lower":
        return min(kept, key=lambda r: r["metric"])
    return max(kept, key=lambda r: r["metric"])


def find_worst_run(runs: List[Dict]) -> Optional[Dict]:
    all_runs = [r for r in runs if r.get("type") != "config" and r.get("metric") is not None]
    if not all_runs:
        return None
    config = next((r for r in runs if r.get("type") == "config"), {})
    direction = config.get("bestDirection", "lower")
    if direction == "lower":
        return max(all_runs, key=lambda r: r["metric"])
    return min(all_runs, key=lambda r: r["metric"])


# ------------------------------------------------------------------ #
#  Dashboard
# ------------------------------------------------------------------ #

def generate_dashboard(state_file: str = STATE_FILE,
                       dashboard_file: str = DASHBOARD_FILE) -> str:
    state = load_state(state_file)
    if not state["config"]:
        return "No experiment state found."

    config = state["config"]
    runs = [r for r in state["runs"] if r.get("type") != "config"]
    kept = [r for r in runs if r.get("status") == "keep"]
    discarded = [r for r in runs if r.get("status") == "discard"]
    errors = [r for r in runs if r.get("status") == "error"]
    skipped = [r for r in runs if r.get("status") == "skip"]

    best = find_best_run(state["runs"])
    worst = find_worst_run(state["runs"])

    metric_name = config.get("metricName", "metric")
    metric_unit = config.get("metricUnit", "")
    direction = config.get("bestDirection", "lower")
    target = config.get("targetFile", "unknown")

    md: List[str] = []
    md.append("# AutoResearch Dashboard\n")
    md.append(f"**Target:** `{target}`  ")
    md.append(f"**Metric:** {metric_name} ({metric_unit})  ")
    md.append(f"**Direction:** {direction} is better  ")
    md.append(f"**Started:** {config.get('startedAt', 'N/A')}  ")
    md.append(f"**Total runs:** {len(runs)}  \n")

    md.append("\n## Summary\n")
    md.append("| Stat | Value |\n|------|-------|\n")
    md.append(f"| Total runs | {len(runs)} |\n")
    md.append(f"| Kept | {len(kept)} |\n")
    md.append(f"| Discarded | {len(discarded)} |\n")
    md.append(f"| Errors | {len(errors)} |\n")
    md.append(f"| Skipped | {len(skipped)} |\n")

    if best:
        md.append(f"| **Best run** | #{best['run']} — {best['metric']:.6f}{metric_unit} |\n")
    if worst and best and worst["run"] != best["run"]:
        md.append(f"| Worst run | #{worst['run']} — {worst['metric']:.6f}{metric_unit} |\n")
    if best and runs and runs[0].get("metric") is not None:
        baseline = runs[0].get("metricBefore", runs[0].get("metric"))
        if baseline:
            if direction == "lower":
                improvement = (baseline - best["metric"]) / baseline * 100
            else:
                improvement = (best["metric"] - baseline) / baseline * 100
            md.append(f"| Improvement vs baseline | {improvement:+.2f}% |\n")

    # Sparkline trend
    all_metrics = [r["metric"] for r in runs if r.get("metric") is not None]
    if all_metrics:
        trend = sparkline(all_metrics)
        md.append(f"\n**Trend:** `{trend}` ({len(all_metrics)} runs)\n")
        if best and worst:
            bar = horizontal_bar(best["metric"], min(all_metrics), max(all_metrics))
            md.append(f"**Best position:** `{min(all_metrics):.4f} {bar} {max(all_metrics):.4f}`\n")

    md.append("\n## Run Timeline\n")
    md.append("| # | Status | Before | After | Delta % | Description |\n")
    md.append("|---|--------|--------|-------|---------|-------------|\n")
    for r in runs:
        rid = r.get("run", "?")
        st = r.get("status", "?")
        before = r.get("metricBefore")
        after = r.get("metric")
        before_s = f"{before:.6f}" if before is not None else "---"
        after_s = f"{after:.6f}" if after is not None else "---"
        if before and after and before != 0:
            delta_pct = (after - before) / before * 100
            delta_s = f"{delta_pct:+.2f}%"
        else:
            delta_s = "---"
        desc = r.get("description", "")[:60]
        md.append(f"| {rid} | {st} | {before_s} | {after_s} | {delta_s} | {desc} |\n")

    if kept:
        md.append("\n## Winning Hypotheses\n")
        for r in kept:
            md.append(f"### Run #{r.get('run')}\n")
            md.append(f"- **Hypothesis:** {r.get('hypothesis', 'N/A')}\n")
            md.append(f"- **Description:** {r.get('description', 'N/A')}\n")
            md.append(f"- **Metric:** {r.get('metric', '?'):.6f}{metric_unit} (was {r.get('metricBefore', '?'):.6f})\n")
            md.append(f"- **Git hash:** {r.get('gitCommit', 'N/A')}\n\n")

    if discarded:
        md.append("\n## Discarded Experiments\n")
        for r in discarded:
            md.append(f"- **Run #{r.get('run')}:** {r.get('description', 'N/A')} — {r.get('metric', '?'):.6f}{metric_unit} (was {r.get('metricBefore', '?'):.6f})\n")

    content = "\n".join(md)
    with open(dashboard_file, "w", encoding="utf-8") as fh:
        fh.write(content)

    append_worklog(content)
    return content


# ------------------------------------------------------------------ #
#  History
# ------------------------------------------------------------------ #

def format_history(state_file: str = STATE_FILE) -> str:
    state = load_state(state_file)
    runs = [r for r in state["runs"] if r.get("type") != "config"]
    if not runs:
        return "No runs recorded yet."

    status_markers = {"keep": "+", "discard": "-", "error": "!", "skip": "~"}
    lines = ["## AutoResearch History\n"]
    for r in runs:
        rid = r.get("run", "?")
        st = r.get("status", "?")
        marker = status_markers.get(st, "?")
        m = r.get("metric")
        m_s = f"{m:.6f}" if m is not None else "---"
        desc = r.get("description", "")[:50]
        lines.append(f"- [{marker}] Run #{rid}: {m_s} — {desc}")

    metrics = [r["metric"] for r in runs if r.get("metric") is not None]
    if metrics:
        trend = sparkline(metrics)
        lines.append(f"\n`{trend}` ({len(metrics)} runs)")

    return "\n".join(lines)


# ------------------------------------------------------------------ #
#  Summarize runs (for in-context display)
# ------------------------------------------------------------------ #

def summarize_runs(state_file: str = STATE_FILE, last_n: int = 5) -> str:
    state = load_state(state_file)
    results = [r for r in state["runs"] if r.get("type") != "config"]
    if not results:
        return "No previous runs."

    status_markers = {"keep": "+", "discard": "-", "error": "!", "skip": "~"}
    lines = []
    for r in results[-last_n:]:
        rid = r.get("run", "?")
        st = r.get("status", "?")
        marker = status_markers.get(st, "?")
        m = r.get("metric")
        m_s = f"{m:.6f}" if m is not None else "---"
        lines.append(f"  [{marker}] Run #{rid}: {m_s}")

    metrics = [r["metric"] for r in results if r.get("metric") is not None]
    if metrics:
        trend = sparkline(metrics)
        lines.append(f"  Trend: {trend}")

    return "\n".join(lines)


# ------------------------------------------------------------------ #
#  Sparklines
# ------------------------------------------------------------------ #

def sparkline(values: List[float], width: int = 20) -> str:
    bars = " ▁▂▃▄▅▆▇█"
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if lo == hi:
        return bars[4] * min(len(values), width)
    if len(values) > width:
        step = len(values) / width
        sampled = [values[int(i * step)] for i in range(width)]
    else:
        sampled = values
    span = hi - lo
    return "".join(bars[min(8, int((v - lo) / span * 8))] for v in sampled)


def horizontal_bar(value: float, lo: float, hi: float, width: int = 16) -> str:
    if hi == lo:
        return "█" * (width // 2) + "░" * (width - width // 2)
    ratio = max(0.0, min(1.0, (value - lo) / (hi - lo)))
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


# ------------------------------------------------------------------ #
#  Misc helpers
# ------------------------------------------------------------------ #

def sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def git_commit_hash() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return hashlib.sha1(str(time.time()).encode()).hexdigest()[:7]


def append_worklog(content: str, worklog_file: str = WORKLOG_FILE):
    try:
        with open(worklog_file, "a", encoding="utf-8") as fh:
            fh.write(f"\n---\n## AutoResearch Dashboard — {datetime.now(timezone.utc).isoformat()}\n")
            fh.write(content)
            fh.write("\n")
    except Exception:
        pass


def get_run_count(state_file: str = STATE_FILE) -> int:
    state = load_state(state_file)
    return len([r for r in state["runs"] if r.get("type") != "config"])


def check_convergence(state_file: str = STATE_FILE, window: int = 3) -> bool:
    state = load_state(state_file)
    recent = [r for r in state["runs"] if r.get("type") != "config"][-window:]
    return len(recent) >= window and all(r.get("status") == "discard" for r in recent)
