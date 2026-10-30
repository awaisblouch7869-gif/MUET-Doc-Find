import unittest

from src.topk import top_k_heap, top_k_sort
from src.topk_demo import count_comparisons
from src.ranking import SharedTermCount, NormalizedCoverage, rank_candidates, ranking_key


def generated_numbers(count, seed=7):
    """Deterministic made-up numbers (no randomness, so every run is identical)."""
    values = []
    state = seed
    for _ in range(count):
        state = (state * 1103515245 + 12345) % 2147483648
        values.append(state % 1000)
    return values


def generated_items(count, seed=7):
    """Items with UNIQUE keys: (-score, passage_id), like the real ranking key."""
    return [{"score": value % 10, "passage_id": f"P{number:04d}"}
            for number, value in enumerate(generated_numbers(count, seed), start=1)]


def item_key(item):
    return (-item["score"], item["passage_id"])


def ids(items):
    return [item["passage_id"] for item in items]


class TestTopKAgainstTheLibrarySortAsAnOracle(unittest.TestCase):
    def test_heap_and_merge_sort_both_equal_sorting_everything(self):
        for count in [0, 1, 2, 5, 40, 250]:
            items = generated_items(count)
            for k in [1, 2, 3, 10, 500]:
                expected = ids(sorted(items, key=item_key)[:k])
                self.assertEqual(ids(top_k_heap(items, k, item_key)), expected, (count, k))
                self.assertEqual(ids(top_k_sort(items, k, item_key)), expected, (count, k))

    def test_result_is_best_first(self):
        keys = [item_key(item) for item in top_k_heap(generated_items(100), 5, item_key)]
        self.assertEqual(keys, sorted(keys))

    def test_input_order_does_not_change_the_result(self):
        items = generated_items(60)
        self.assertEqual(ids(top_k_heap(items, 3, item_key)),
                         ids(top_k_heap(list(reversed(items)), 3, item_key)))

    def test_input_list_is_not_changed(self):
        items = generated_items(20)
        before = ids(items)
        top_k_heap(items, 3, item_key)
        top_k_sort(items, 3, item_key)
        self.assertEqual(ids(items), before)

    def test_k_larger_than_the_number_of_items(self):
        self.assertEqual(len(top_k_heap(generated_items(4), 10, item_key)), 4)

    def test_negative_k_is_rejected(self):
        with self.assertRaises(ValueError):
            top_k_heap([1], -1, lambda x: x)
        with self.assertRaises(ValueError):
            top_k_sort([1], -1, lambda x: x)

    def test_topk_source_uses_no_library_heap_or_sort(self):
        with open("src/topk.py", "r", encoding="utf-8") as source_file:
            source = source_file.read()
        for forbidden in ["heapq", "sorted(", ".sort(", "import "]:
            self.assertNotIn(forbidden, source, forbidden)


class TestHeapDoesLessWorkWhenKIsSmall(unittest.TestCase):
    def test_heap_needs_fewer_comparisons_than_sorting_everything(self):
        for count in [1000, 5000]:
            heap_comparisons, sort_comparisons, same = count_comparisons(count, 3)
            self.assertTrue(same)
            self.assertLess(heap_comparisons, sort_comparisons, count)

    def test_comparison_counts_are_the_same_on_every_run(self):
        self.assertEqual(count_comparisons(500, 3), count_comparisons(500, 3))


class TestRankCandidatesSelectors(unittest.TestCase):
    def make(self, passage_id, matched):
        return {"passage": {"passage_id": passage_id, "title": "T", "text": "x y z"},
                "matched_words": matched}

    def test_heap_and_sort_selectors_give_identical_rankings(self):
        candidates = [self.make(f"P{number:04d}", ["w"] * (value % 4 + 1))
                      for number, value in enumerate(generated_numbers(120), start=1)]
        for strategy in [SharedTermCount(), NormalizedCoverage()]:
            for k in [1, 3, 7, 200]:
                by_heap = rank_candidates(candidates, strategy, 4, k, selector="heap")
                by_sort = rank_candidates(candidates, strategy, 4, k, selector="sort")
                self.assertEqual([m["passage"]["passage_id"] for m in by_heap],
                                 [m["passage"]["passage_id"] for m in by_sort])
                self.assertEqual([m["score"] for m in by_heap], [m["score"] for m in by_sort])

    def test_ties_go_to_the_smaller_id_with_the_heap(self):
        many = [self.make(f"P{n:03d}", ["a"]) for n in range(9, 0, -1)]
        results = rank_candidates(many, SharedTermCount(), 1, 3)
        self.assertEqual([m["passage"]["passage_id"] for m in results], ["P001", "P002", "P003"])

    def test_unknown_selector_is_rejected(self):
        with self.assertRaises(ValueError):
            rank_candidates([], SharedTermCount(), 1, 3, selector="bubble")

    def test_results_follow_the_ranking_key_order(self):
        candidates = [self.make("P003", ["a", "b"]), self.make("P001", ["a"]), self.make("P002", ["a", "b"])]
        results = rank_candidates(candidates, SharedTermCount(), 2, 3)
        self.assertEqual([m["passage"]["passage_id"] for m in results], ["P002", "P003", "P001"])
        self.assertEqual([ranking_key(m) for m in results], sorted(ranking_key(m) for m in results))


if __name__ == "__main__":
    unittest.main()