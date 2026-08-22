"""
Sorter module — candidate: NumPy sort.

Usage:
    python bogo_sort.py

History:
    Originally used bogo sort (random shuffling until sorted), which took
    ~7 seconds for a list of 10 elements.
    Iteration 1 (autoresearch): bubble sort (~0.009 ms).
    Iteration 2 (autoresearch): insertion sort (~0.006 ms).
    Iteration 3 (autoresearch): merge sort — discarded (slower at n=10).
    Iteration 4 (autoresearch): built-in sorted() (~0.001 ms).
    Iteration 5 (autoresearch, CANDIDATE): route through numpy.sort.
    Sorts `arr` in place and returns it, preserving the original
    mutate-and-return contract. Note: converts elements to float64 via
    numpy; output values compare equal for numeric inputs.
"""

import numpy as np


def bogo_sort(arr):
    """Sort using numpy.sort; sorts `arr` in place and returns it."""
    arr[:] = np.sort(np.asarray(arr)).tolist()
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
