"""
Sorter module — candidate: hand-rolled pure-Python Timsort.

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
    Iteration 7 (autoresearch, CANDIDATE): hand-rolled binary insertion sort
    (the small-run core of Timsort) in pure Python, to test whether avoiding
    C-API dispatch helps at n=10. Sorts `arr` in place and returns it.
"""


def bogo_sort(arr):
    """Sort using pure-Python binary insertion sort; returns `arr` sorted."""
    for i in range(1, len(arr)):
        key = arr[i]
        lo, hi = 0, i
        while lo < hi:
            mid = (lo + hi) // 2
            if arr[mid] <= key:
                lo = mid + 1
            else:
                hi = mid
        arr[lo + 1:i + 1] = arr[lo:i]
        arr[lo] = key
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
