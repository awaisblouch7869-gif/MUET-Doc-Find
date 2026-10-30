
import unittest

from src.topk import MaxHeap, top_k_heap, top_k_sort, merge_sort


class TestTopK(unittest.TestCase):
    def test_heap_pop_returns_largest_first(self):
        heap = MaxHeap(lambda x: x)
        for value in [3, 1, 8, 2, 7]:
            heap.push(value)

        self.assertEqual([heap.pop() for _ in range(5)], [8, 7, 3, 2, 1])

    def test_empty_heap_pop_raises(self):
        heap = MaxHeap(lambda x: x)
        with self.assertRaises(IndexError):
            heap.pop()

    def test_heap_keeps_maximum_at_root(self):
        heap = MaxHeap(lambda x: x)
        for value in [4, 9, 2, 7, 1]:
            heap.push(value)
            self.assertEqual(heap.data[0], max(heap.data))

    def test_merge_sort_sorts_numbers(self):
        self.assertEqual(merge_sort([5, 1, 4, 2, 3], lambda x: x), [1, 2, 3, 4, 5])

    def test_merge_sort_is_stable(self):
        items = [(2, "A"), (1, "B"), (2, "C"), (1, "D")]
        result = merge_sort(items, lambda x: x[0])
        self.assertEqual(result, [(1, "B"), (1, "D"), (2, "A"), (2, "C")])

    def test_heap_top_k(self):
        values = [9, 1, 7, 3, 8, 2]
        self.assertEqual(top_k_heap(values, 3, lambda x: x), [1, 2, 3])

    def test_sort_top_k(self):
        values = [9, 1, 7, 3, 8, 2]
        self.assertEqual(top_k_sort(values, 3, lambda x: x), [1, 2, 3])

    def test_heap_and_sort_agree(self):
        values = [9, 1, 7, 3, 8, 2]
        key = lambda x: -x
        self.assertEqual(
            top_k_heap(values, 3, key),
            top_k_sort(values, 3, key),
        )

    def test_k_zero(self):
        self.assertEqual(top_k_heap([1, 2], 0, lambda x: x), [])
        self.assertEqual(top_k_sort([1, 2], 0, lambda x: x), [])

    def test_negative_k_rejected(self):
        with self.assertRaises(ValueError):
            top_k_heap([1, 2], -1, lambda x: x)
        with self.assertRaises(ValueError):
            top_k_sort([1, 2], -1, lambda x: x)

    def test_k_larger_than_input(self):
        self.assertEqual(
            top_k_heap([2, 1], 5, lambda x: x),
            [1, 2],
        )
        self.assertEqual(
            top_k_sort([2, 1], 5, lambda x: x),
            [1, 2],
        )

    def test_merge_sort_does_not_change_input(self):
        values = [4, 1, 3, 2]
        original = values.copy()
        merge_sort(values, lambda x: x)
        self.assertEqual(values, original)


if __name__ == "__main__":
    unittest.main()
