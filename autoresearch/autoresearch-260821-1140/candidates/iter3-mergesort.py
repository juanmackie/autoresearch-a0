"""
Sorter module — optimized: top-down merge sort.

Usage:
    python bogo_sort.py

History:
    Originally used bogo sort (random shuffling until sorted), which took
    ~7 seconds for a list of 10 elements.
    Iteration 1 (autoresearch): bubble sort (~0.009 ms).
    Iteration 2 (autoresearch): insertion sort (~0.006 ms).
    Iteration 3 (autoresearch): top-down merge sort — O(n log n) worst case.
    NOTE: unlike previous versions, merge sort builds a new list; the
    function still returns the fully sorted sequence and the caller's
    list contents are replaced in place to preserve the original
    mutate-and-return contract.
"""


def bogo_sort(arr):
    """Sort using top-down merge sort; sorts `arr` in place and returns it."""
    arr[:] = _merge_sort(arr)
    return arr


def _merge_sort(items):
    if len(items) <= 1:
        return items[:]
    mid = len(items) // 2
    left = _merge_sort(items[:mid])
    right = _merge_sort(items[mid:])
    return _merge(left, right)


def _merge(left, right):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


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
