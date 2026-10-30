import unittest

from src.loader import load_passages
from src.search import linear_search
from src.tokenizer import tokenize, unique_tokens


def make_passage(passage_id, title, text):
    """Build a small passage record for testing (only the fields the search uses)."""
    return {"passage_id": passage_id, "title": title, "text": text}


def words(query):
    """Turn a query string into unique tokens, exactly like main.py does."""
    return unique_tokens(tokenize(query))


def ids(results):
    """Return just the passage IDs of a result list, in order."""
    return [match["passage"]["passage_id"] for match in results]


class TestLinearSearchRules(unittest.TestCase):
    def test_higher_score_comes_first(self):
        passages = [
            make_passage("P001", "Notice", "data only"),
            make_passage("P002", "Data Structures", "arrays"),
        ]
        results = linear_search(passages, words("data structures"))
        self.assertEqual(ids(results), ["P002", "P001"])
        self.assertEqual(results[0]["score"], 2)
        self.assertEqual(results[1]["score"], 1)

    def test_tie_is_broken_by_passage_id_ascending(self):
        passages = [
            make_passage("P002", "Lab", "rules"),
            make_passage("P001", "Lab", "rules"),
        ]
        self.assertEqual(ids(linear_search(passages, words("lab"))), ["P001", "P002"])

    def test_at_most_three_results(self):
        passages = [make_passage("P00" + str(n), "Lab", "rules") for n in range(1, 6)]
        self.assertEqual(len(linear_search(passages, words("lab"))), 3)

    def test_no_match_gives_empty_list(self):
        passages = [make_passage("P001", "Lab", "rules")]
        self.assertEqual(linear_search(passages, words("football")), [])

    def test_empty_corpus_gives_empty_list(self):
        self.assertEqual(linear_search([], words("lab")), [])

    def test_case_and_punctuation_are_ignored(self):
        passages = [make_passage("P001", "Notice", "Lab FILES!")]
        self.assertEqual(ids(linear_search(passages, words("lab, files?"))), ["P001"])

    def test_whole_words_only(self):
        passages = [make_passage("P001", "Notice", "database systems")]
        self.assertEqual(linear_search(passages, words("data")), [])

    def test_repeated_query_words_count_once(self):
        passages = [make_passage("P001", "Notice", "data")]
        results = linear_search(passages, words("data data DATA"))
        self.assertEqual(results[0]["score"], 1)

    def test_stop_words_in_query_are_ignored(self):
        passages = [make_passage("P001", "Notice", "data")]
        self.assertEqual(linear_search(passages, words("the data")), linear_search(passages, words("data")))

    def test_title_is_searched_too(self):
        passages = [make_passage("P001", "Laboratory Rules", "nothing relevant here")]
        self.assertEqual(ids(linear_search(passages, words("laboratory"))), ["P001"])

    def test_same_query_gives_same_results(self):
        passages = [make_passage("P002", "Lab", "x"), make_passage("P001", "Lab", "y")]
        self.assertEqual(ids(linear_search(passages, words("lab"))), ids(linear_search(passages, words("lab"))))


class TestLinearSearchOnSampleData(unittest.TestCase):
    """These depend on data/passages.json being the 5 sample passages from Milestone 1."""

    def setUp(self):
        self.passages = load_passages("data/passages.json")

    def test_data_structures(self):
        self.assertEqual(ids(linear_search(self.passages, words("data structures"))), ["P001", "P002"])

    def test_examination_schedule(self):
        self.assertEqual(ids(linear_search(self.passages, words("examination schedule"))), ["P004", "P005"])

    def test_football_has_no_results(self):
        self.assertEqual(linear_search(self.passages, words("football")), [])

    def test_blank_query_has_no_words(self):
        self.assertEqual(words("   "), [])


if __name__ == "__main__":
    unittest.main()