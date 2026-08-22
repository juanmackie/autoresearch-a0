"""
Sorter module — optimized: insertion sort.

Usage:
    python bogo_sort.py

History:
    Originally used bogo sort (random shuffling until sorted), which took
    ~7 seconds for a list of 10 elements.
    Iteration 1 (autoresearch): replaced with bubble sort (~0.009 ms).
    Iteration 2 (autoresearch): replaced with insertion sort — same O(n^2)
    worst case but fewer comparisons/swaps in practice, O(n) on sorted input.
    Identical signature: sorts `arr` in place and returns it.
"""


def bogo_sort(arr):
    """Sort the list in place using insertion sort and return it.

    Preserves the original function's contract: same signature,
    mutates `arr`, returns `arr` in non-decreasing order.
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
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
