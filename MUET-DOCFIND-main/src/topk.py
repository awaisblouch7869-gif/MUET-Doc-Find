
"""Custom heap and merge-sort implementations for Top-K selection."""


class MaxHeap:
    """Binary max-heap stored in a Python list."""

    def __init__(self, key):
        self.data = []
        self.key = key

    def __len__(self):
        return len(self.data)

    def push(self, item):
        self.data.append(item)
        child = len(self.data) - 1

        while child > 0:
            parent = (child - 1) // 2
            if self.key(self.data[parent]) >= self.key(self.data[child]):
                break
            self.data[parent], self.data[child] = (
                self.data[child], self.data[parent]
            )
            child = parent

    def pop(self):
        if not self.data:
            raise IndexError("pop from empty heap")

        self.data[0], self.data[-1] = self.data[-1], self.data[0]
        result = self.data.pop()

        parent = 0
        size = len(self.data)

        while True:
            left = 2 * parent + 1
            right = left + 1
            largest = parent

            if left < size and self.key(self.data[left]) > self.key(
                self.data[largest]
            ):
                largest = left

            if right < size and self.key(self.data[right]) > self.key(
                self.data[largest]
            ):
                largest = right

            if largest == parent:
                break

            self.data[parent], self.data[largest] = (
                self.data[largest], self.data[parent]
            )
            parent = largest

        return result


def top_k_heap(items, k, key):
    """Return the best k items using O(C log k) heap selection."""
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return []

    heap = MaxHeap(key)

    for item in items:
        heap.push(item)
        if len(heap) > k:
            heap.pop()

    return merge_sort(heap.data, key)


def merge_sort(items, key):
    """Stable merge sort; returns a new sorted list."""
    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def sorted_by_merge(items, key):
    return merge_sort(items, key)


def top_k_sort(items, k, key):
    """Sort all items with merge sort, then return the first k."""
    if k < 0:
        raise ValueError("k must be non-negative")
    return merge_sort(items, key)[:k]
