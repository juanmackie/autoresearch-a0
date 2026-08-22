"""Correctness verifier for bogo_sort.py.

Checks the sort function against 100 random seeded lists:
sizes 0-30 (uniformly sampled), with duplicates and edge cases
(empty, single element, already sorted, reverse sorted).

Usage:
    python benchmarks/verify.py [max_size]

    max_size defaults to 30. Use a smaller value when verifying an
    algorithm that is too slow for large inputs (e.g. bogo sort).

Output: "correct=True|False n=100" — exit code 0 iff all pass.
"""

import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bogo_sort import bogo_sort  # noqa: E402


def main() -> int:
    max_size = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    rng = random.Random(42)
    all_ok = True
    for i in range(100):
        n = rng.randint(0, 30)
        if i == 0:
            arr = []                       # empty edge case
        elif i == 1:
            arr = [7]                      # single element
        elif i == 2:
            arr = list(range(min(20, max_size)))          # already sorted
        elif i == 3:
            arr = list(range(min(20, max_size), -1, -1))  # reverse sorted
        else:
            arr = [rng.randint(-5, min(5, max_size)) for _ in range(min(n, max_size))]  # heavy duplicates
        original = arr[:]
        result = bogo_sort(arr[:])
        ok = result == sorted(original)
        all_ok = all_ok and ok
        if not ok:
            print(f"FAIL at case {i}: input={original} got={result}")
    print(f"correct={str(all_ok).lower()} n=100 max_size={max_size}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
