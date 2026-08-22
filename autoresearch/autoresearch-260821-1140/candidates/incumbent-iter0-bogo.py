"""
Bogo Sort — intentionally slow for AutoResearch optimization demos.

Usage:
    python bogo_sort.py

This script sorts a small list using bogo sort (random shuffling).
Expected runtime is several seconds for a list of 10 elements.
An agent optimizing this would likely:
  1. Replace bogo sort with a faster algorithm (bubble, quick, timsort, etc.)
  2. Use Python's built-in sorted()
  3. Reduce input size while preserving behavior
"""

import random


def bogo_sort(arr):
    """Sort by repeatedly shuffling until sorted."""
    while not is_sorted(arr):
        random.shuffle(arr)
    return arr


def is_sorted(arr):
    """Check if the list is in non-decreasing order."""
    for i in range(len(arr) - 1):
        if arr[i] > arr[i + 1]:
            return False
    return True


def main():
    data = [5, 3, 8, 1, 9, 2, 7, 4, 6, 0]
    print(f"Input:  {data}")
    result = bogo_sort(data[:])  # sort a copy
    print(f"Sorted: {result}")


if __name__ == "__main__":
    main()
