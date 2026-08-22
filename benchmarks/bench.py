"""Benchmark harness for bogo_sort.py.

Sorts a fixed seeded list of 10 elements, verifies correctness
(result == sorted(input)), and reports the median wall-clock time
of 3 runs in milliseconds.

Usage:
    python benchmarks/bench.py

Output (machine-parseable):
    correct=True|False median_ms=<float> runs=<ms,ms,ms>
"""

import random
import statistics
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bogo_sort import bogo_sort  # noqa: E402


def run_once() -> tuple[bool, float]:
    data = [5, 3, 8, 1, 9, 2, 7, 4, 6, 0]  # fixed seeded list, 10 elements
    expected = sorted(data)
    random.seed(1234)  # deterministic shuffle stream -> bounded, reproducible timing
    start = time.perf_counter()
    result = bogo_sort(data[:])
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return result == expected, elapsed_ms


def main() -> int:
    runs = []
    all_correct = True
    for _ in range(3):
        ok, ms = run_once()
        all_correct = all_correct and ok
        runs.append(ms)
    median_ms = statistics.median(runs)
    runs_str = ",".join(f"{ms:.3f}" for ms in runs)
    print(f"correct={str(all_correct).lower()} median_ms={median_ms:.3f} runs={runs_str}")
    return 0 if all_correct else 1


if __name__ == "__main__":
    sys.exit(main())
