"""
Sorter module — optimized: built-in sorted() (Timsort, C-implemented).

Usage:
    python bogo_sort.py

History:
    Originally used bogo sort (random shuffling until sorted), which took
    ~7 seconds for a list of 10 elements.
    Iteration 1 (autoresearch): bubble sort (~0.009 ms).
    Iteration 2 (autoresearch): insertion sort (~0.006 ms).
    Iteration 3 (autoresearch): merge sort — discarded (slower at n=10).
    Iteration 4 (autoresearch): delegate to Python's built-in sorted()
    (Timsort in C). Sorts `arr` in place and returns it, preserving the
    original mutate-and-return contract.
"""


def bogo_sort(arr):
    """Sort using the built-in Timsort; sorts `arr` in place and returns it."""
    arr[:] = sorted(arr)
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
