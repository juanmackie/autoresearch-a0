"""
Bogo Sort module — now optimized: bubble sort.

Usage:
    python bogo_sort.py

History:
    Originally used bogo sort (random shuffling until sorted), which took
    ~7 seconds for a list of 10 elements.
    Iteration 1 (autoresearch): replaced with bubble sort — deterministic
    O(n^2) worst case, identical signature and sorted output, sorts in place
    and returns the same list object, just like the original.
"""

import random


def bogo_sort(arr):
    """Sort the list in place using bubble sort and return it.

    Preserves the original function's contract: same signature,
    mutates `arr`, returns `arr` in non-decreasing order.
    """
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
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
