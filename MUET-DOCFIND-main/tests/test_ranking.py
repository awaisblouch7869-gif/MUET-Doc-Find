import unittest

from main import parse_arguments
from src.loader import load_passages
from src.search import run_search
from src.ranking import SharedTermCount, rank_candidates, ranking_key
from src.tokenizer import tokenize, unique_tokens


def candidate(passage_id, matched_words):
    return {"passage": {"passage_id": passage_id, "title": "T", "text": "x", "version": "v9"},
            "matched_words": matched_words}


def ids(results):
    return [match["passage"]["passage_id"] for match in results]


class TestSharedTermCount(unittest.TestCase):
    def test_score_is_number_of_matched_words(self):
        strategy = SharedTermCount()
        self.assertEqual(strategy.score(["data", "structures"], 3), 2)
        self.assertEqual(strategy.score(["data"], 3), 1)

    def test_strategy_has_a_name(self):
        self.assertEqual(SharedTermCount().name, "shared-term count")


class TestRankCandidates(unittest.TestCase):
    def rank(self, candidates, max_results=3):
        return rank_candidates(candidates, SharedTermCount(), 3, max_results)

    def test_higher_score_first(self):
        results = self.rank([candidate("P001", ["a"]), candidate("P002", ["a", "b", "c"]), candidate("P003", ["a", "b"])])
        self.assertEqual(ids(results), ["P002", "P003", "P001"])
        self.assertEqual([match["score"] for match in results], [3, 2, 1])

    def test_tie_goes_to_smaller_passage_id(self):
        results = self.rank([candidate("P003", ["a"]), candidate("P001", ["a"]), candidate("P002", ["a"])])
        self.assertEqual(ids(results), ["P001", "P002", "P003"])

    def test_input_order_does_not_change_the_result(self):
        first = [candidate("P002", ["a"]), candidate("P001", ["a", "b"]), candidate("P003", ["a"])]
        second = [first[2], first[0], first[1]]
        self.assertEqual(ids(self.rank(first)), ids(self.rank(second)))

    def test_only_the_best_k_are_kept(self):
        many = [candidate("P00" + str(n), ["a"]) for n in range(1, 8)]
        self.assertEqual(ids(self.rank(many, max_results=3)), ["P001", "P002", "P003"])
        self.assertEqual(len(self.rank(many, max_results=1)), 1)

    def test_fewer_candidates_than_k_is_fine(self):
        self.assertEqual(len(self.rank([candidate("P001", ["a"])], max_results=3)), 1)

    def test_no_candidates_gives_empty_list(self):
        self.assertEqual(self.rank([]), [])

    def test_bad_max_results_is_rejected(self):
        for bad in [0, -1, "3", None]:
            with self.assertRaises(ValueError):
                self.rank([candidate("P001", ["a"])], max_results=bad)

    def test_metadata_is_preserved_and_input_is_not_changed(self):
        original = [candidate("P002", ["a"]), candidate("P001", ["a"])]
        results = self.rank(original)
        self.assertEqual(results[0]["passage"]["version"], "v9")
        self.assertEqual(results[0]["matched_words"], ["a"])
        self.assertEqual(ids([{"passage": item["passage"]} for item in original]), ["P002", "P001"])

    def test_ids_are_compared_as_text(self):
        # Documented limitation: use fixed-width IDs (P001...), or "P10" sorts before "P9".
        results = self.rank([candidate("P9", ["a"]), candidate("P10", ["a"])])
        self.assertEqual(ids(results), ["P10", "P9"])

    def test_ranking_key_orders_by_score_then_id(self):
        better = {"passage": {"passage_id": "P005"}, "score": 2}
        worse = {"passage": {"passage_id": "P001"}, "score": 1}
        self.assertLess(ranking_key(better), ranking_key(worse))


class TestBothMethodsGiveTheSameRankedResults(unittest.TestCase):
    def words(self, query):
        return unique_tokens(tokenize(query))

    def view(self, results):
        return [(m["passage"]["passage_id"], m["score"], m["matched_words"]) for m in results]

    def test_on_the_sample_data(self):
        passages = load_passages("data/passages.json")
        for query in ["data structures", "examination schedule", "football", "students",
                      "lab files", "midterm examination week", "the", "hash tables heaps sorting"]:
            query_words = self.words(query)
            self.assertEqual(self.view(run_search("linear", passages, query_words)),
                             self.view(run_search("index", passages, query_words)), query)

    def test_expected_top_results_on_the_sample_data(self):
        passages = load_passages("data/passages.json")
        for method in ["linear", "index"]:
            self.assertEqual(ids(run_search(method, passages, self.words("data structures"))), ["P001", "P002"])
            self.assertEqual(ids(run_search(method, passages, self.words("examination schedule"))), ["P004", "P005"])
            self.assertEqual(run_search(method, passages, self.words("football")), [])

    def test_results_are_the_same_on_every_run(self):
        passages = load_passages("data/passages.json")
        query_words = self.words("students")
        first = self.view(run_search("index", passages, query_words))
        second = self.view(run_search("index", passages, query_words))
        self.assertEqual(first, second)

    def test_k_is_respected(self):
        passages = load_passages("data/passages.json")
        self.assertEqual(len(run_search("index", passages, self.words("students"), max_results=2)), 2)
        self.assertEqual(len(run_search("linear", passages, self.words("students"), max_results=1)), 1)


class TestParseArguments(unittest.TestCase):
    def test_options_and_query_are_separated(self):
        self.assertEqual(parse_arguments(["data", "--index", "structures"]), (["--index"], ["data", "structures"]))

    def test_no_arguments(self):
        self.assertEqual(parse_arguments([]), ([], []))

    def test_only_an_option(self):
        self.assertEqual(parse_arguments(["--show"]), (["--show"], []))


if __name__ == "__main__":
    unittest.main()