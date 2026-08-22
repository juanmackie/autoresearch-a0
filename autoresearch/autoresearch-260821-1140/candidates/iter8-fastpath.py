"""
Sorter module — optimized: built-in list.sort() with sorted-input fast path.

Usage:
    python bogo_sort.py

History:
    Originally used bogo sort (random shuffling until sorted), which took
    ~7 seconds for a list of 10 elements.
    Iteration 1 (autoresearch): bubble sort (~0.009 ms).
    Iteration 2 (autoresearch): insertion sort (~0.006 ms).
    Iteration 3 (autoresearch): merge sort — discarded (slower at n=10).
    Iteration 4 (autoresearch): built-in sorted() (~0.001 ms).
    Iteration 5 (autoresearch): numpy.sort — discarded (conversion overhead).
    Iteration 6 (autoresearch): in-place list.sort() (~0.0003 ms).
    Iteration 7 (autoresearch): pure-Python binary insertion — discarded.
    Iteration 8 (autoresearch, CANDIDATE): is_sorted() pre-check fast path —
    O(n) skip for already-sorted input, at the cost of one extra scan for
    unsorted input. Sorts `arr` in place and returns it, preserving the
    original mutate-and-return contract.
"""


def bogo_sort(arr):
    """Sort `arr` in place with Timsort; returns `arr` sorted.

    A pre-check skips the sort entirely when the input is already
    non-decreasing (O(n) best case).
    """
    if not is_sorted(arr):
        arr.sort()
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
