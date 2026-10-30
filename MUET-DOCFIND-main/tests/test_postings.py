import unittest

from src.hash_table import HashTable
from src.postings import PostingsList


class TestBasics(unittest.TestCase):
    def test_new_list_is_empty(self):
        postings = PostingsList()
        self.assertEqual(len(postings), 0)
        self.assertEqual(postings.passage_ids(), [])
        self.assertEqual(postings.to_pairs(), [])
        self.assertEqual(postings.total_occurrences(), 0)
        self.assertFalse(postings.contains("P001"))
        self.assertEqual(postings.frequency_of("P001"), 0)

    def test_first_occurrence_creates_a_posting(self):
        postings = PostingsList()
        self.assertTrue(postings.add_occurrence("P001"))
        self.assertEqual(len(postings), 1)
        self.assertEqual(postings.frequency_of("P001"), 1)

    def test_postings_keep_insertion_order(self):
        postings = PostingsList()
        postings.add_occurrence("P002")
        postings.add_occurrence("P001")
        self.assertEqual(postings.passage_ids(), ["P002", "P001"])

    def test_invalid_passage_id_is_rejected(self):
        postings = PostingsList()
        with self.assertRaises(TypeError):
            postings.add_occurrence(5)
        with self.assertRaises(ValueError):
            postings.add_occurrence("   ")


class TestDuplicateOccurrences(unittest.TestCase):
    def test_repeated_word_in_same_passage_raises_frequency_not_length(self):
        postings = PostingsList()
        self.assertTrue(postings.add_occurrence("P001"))
        self.assertFalse(postings.add_occurrence("P001"))
        self.assertFalse(postings.add_occurrence("P001"))
        self.assertEqual(len(postings), 1)
        self.assertEqual(postings.frequency_of("P001"), 3)

    def test_non_adjacent_duplicate_is_still_merged(self):
        postings = PostingsList()
        postings.add_occurrence("P001")
        postings.add_occurrence("P002")
        postings.add_occurrence("P001")
        self.assertEqual(postings.to_pairs(), [("P001", 2), ("P002", 1)])

    def test_total_occurrences_adds_up_all_frequencies(self):
        postings = PostingsList()
        for passage_id in ["P001", "P001", "P002", "P003", "P003", "P003"]:
            postings.add_occurrence(passage_id)
        self.assertEqual(len(postings), 3)
        self.assertEqual(postings.total_occurrences(), 6)


class TestRemoveAndUpdate(unittest.TestCase):
    def build(self):
        postings = PostingsList()
        for passage_id in ["P001", "P002", "P003"]:
            postings.add_occurrence(passage_id)
        return postings

    def test_remove_middle(self):
        postings = self.build()
        self.assertTrue(postings.remove("P002"))
        self.assertEqual(postings.passage_ids(), ["P001", "P003"])

    def test_remove_first(self):
        postings = self.build()
        postings.remove("P001")
        self.assertEqual(postings.passage_ids(), ["P002", "P003"])

    def test_remove_last_then_add_still_appends_correctly(self):
        postings = self.build()
        postings.remove("P003")
        postings.add_occurrence("P004")
        self.assertEqual(postings.passage_ids(), ["P001", "P002", "P004"])

    def test_remove_missing_returns_false(self):
        postings = self.build()
        self.assertFalse(postings.remove("P999"))
        self.assertEqual(len(postings), 3)

    def test_remove_everything_then_reuse(self):
        postings = self.build()
        for passage_id in ["P001", "P002", "P003"]:
            postings.remove(passage_id)
        self.assertEqual(len(postings), 0)
        self.assertEqual(postings.to_pairs(), [])
        postings.add_occurrence("P010")
        self.assertEqual(postings.to_pairs(), [("P010", 1)])

    def test_update_means_remove_then_add_again_and_joins_the_end(self):
        postings = self.build()
        postings.remove("P002")
        postings.add_occurrence("P002")
        self.assertEqual(postings.passage_ids(), ["P001", "P003", "P002"])


class TestWorksTogetherWithOurHashTable(unittest.TestCase):
    def test_hash_table_can_store_postings_lists_as_values(self):
        table = HashTable()
        for word, passage_id in [("data", "P001"), ("lab", "P003"), ("data", "P002")]:
            if not table.contains(word):
                table.put(word, PostingsList())
            table.get(word).add_occurrence(passage_id)
        self.assertEqual(table.get("data").passage_ids(), ["P001", "P002"])
        self.assertEqual(table.get("lab").passage_ids(), ["P003"])
        self.assertEqual(len(table), 2)

    def test_same_steps_give_same_result(self):
        first = PostingsList()
        second = PostingsList()
        for passage_id in ["P003", "P001", "P003"]:
            first.add_occurrence(passage_id)
            second.add_occurrence(passage_id)
        self.assertEqual(first.to_pairs(), second.to_pairs())


if __name__ == "__main__":
    unittest.main() 