import unittest

from src.search import run_search, get_candidates, STRATEGIES
from src.ranking import SharedTermCount, NormalizedCoverage, rank_candidates
from src.tokenizer import tokenize, unique_tokens


def make_passage(passage_id, title, text, version="v1"):
    return {"passage_id": passage_id, "document_id": "D01", "title": title,
            "category": "Test", "source": "SYNTHETIC test data", "version": version,
            "date": "2026-01-01", "text": text}


def candidate(passage, matched_words):
    return {"passage": passage, "matched_words": matched_words}


def ids(results):
    return [match["passage"]["passage_id"] for match in results]


LONG = make_passage("P001", "Notes", "hash tables arrays heaps sorting searching linked lists")
SHORT = make_passage("P002", "Notes", "hash")
CORPUS = [
    LONG,
    SHORT,
    make_passage("P003", "Other", "tables heaps"),
    make_passage("P004", "Other", "tables heaps", version="v2"),
    make_passage("P005", "Misc", "completely unrelated words here"),
]


class TestNormalizedCoverage(unittest.TestCase):
    def test_shorter_passage_scores_higher_for_the_same_matches(self):
        strategy = NormalizedCoverage()
        short_score = strategy.score(["hash"], 1, SHORT)
        long_score = strategy.score(["hash"], 1, LONG)
        self.assertGreater(short_score, long_score)

    def test_more_matches_in_the_same_passage_score_higher(self):
        strategy = NormalizedCoverage()
        self.assertGreater(strategy.score(["hash", "tables"], 2, LONG), strategy.score(["hash"], 2, LONG))

    def test_score_is_matches_divided_by_unique_passage_words(self):
        strategy = NormalizedCoverage()
        length = len(unique_tokens(tokenize(LONG["title"] + " " + LONG["text"])))
        self.assertAlmostEqual(strategy.score(["hash", "tables"], 2, LONG), 2 / length)

    def test_passage_with_no_words_scores_zero(self):
        empty = make_passage("P009", "", "")
        self.assertEqual(NormalizedCoverage().score(["hash"], 1, empty), 0.0)

    def test_passage_is_required(self):
        with self.assertRaises(ValueError):
            NormalizedCoverage().score(["hash"], 1)

    def test_name_and_display(self):
        self.assertEqual(NormalizedCoverage().name, "normalized coverage")
        self.assertEqual(NormalizedCoverage().show(0.5), "0.500")
        self.assertEqual(SharedTermCount().show(2), "2")


class TestStrategiesOnTheSameCandidates(unittest.TestCase):
    def test_the_two_strategies_can_disagree_on_identical_candidates(self):
        candidates = [candidate(LONG, ["hash", "tables"]), candidate(SHORT, ["hash"])]
        first = rank_candidates(candidates, SharedTermCount(), 2, 3)
        second = rank_candidates(candidates, NormalizedCoverage(), 2, 3)
        self.assertEqual(ids(first), ["P001", "P002"])
        self.assertEqual(ids(second), ["P002", "P001"])

    def test_same_candidates_are_scored_not_changed(self):
        candidates = [candidate(LONG, ["hash", "tables"]), candidate(SHORT, ["hash"])]
        rank_candidates(candidates, NormalizedCoverage(), 2, 3)
        self.assertEqual(ids([{"passage": c["passage"]} for c in candidates]), ["P001", "P002"])

    def test_tie_goes_to_smaller_passage_id_for_strategy_2(self):
        a = make_passage("P003", "Other", "tables heaps")
        b = make_passage("P004", "Other", "tables heaps")
        for order in ([candidate(a, ["tables"]), candidate(b, ["tables"])],
                      [candidate(b, ["tables"]), candidate(a, ["tables"])]):
            self.assertEqual(ids(rank_candidates(order, NormalizedCoverage(), 1, 3)), ["P003", "P004"])

    def test_two_strategies_are_registered_with_different_names(self):
        self.assertEqual(len(STRATEGIES), 2)
        self.assertNotEqual(STRATEGIES[0].name, STRATEGIES[1].name)


class TestSearchWithEitherStrategy(unittest.TestCase):
    def words(self, query):
        return unique_tokens(tokenize(query))

    def view(self, results):
        return [(m["passage"]["passage_id"], m["score"], m["matched_words"]) for m in results]

    def test_linear_and_index_agree_under_both_strategies(self):
        for strategy in STRATEGIES:
            for query in ["hash tables", "heaps", "hash", "tables heaps sorting", "football", "unrelated words"]:
                query_words = self.words(query)
                self.assertEqual(self.view(run_search("linear", CORPUS, query_words, strategy=strategy)),
                                 self.view(run_search("index", CORPUS, query_words, strategy=strategy)),
                                 (strategy.name, query))

    def test_both_methods_give_the_same_candidates(self):
        query_words = self.words("hash tables heaps")
        linear = sorted(c["passage"]["passage_id"] for c in get_candidates("linear", CORPUS, query_words))
        index = sorted(c["passage"]["passage_id"] for c in get_candidates("index", CORPUS, query_words))
        self.assertEqual(linear, index)

    def test_default_strategy_is_still_shared_term_count(self):
        results = run_search("index", CORPUS, self.words("hash tables"))
        self.assertEqual(results[0]["score"], 2)
        self.assertEqual(ids(results)[0], "P001")

    def test_unknown_words_give_no_results_for_both_strategies(self):
        for strategy in STRATEGIES:
            self.assertEqual(run_search("index", CORPUS, self.words("football"), strategy=strategy), [])

    def test_empty_corpus_gives_no_results(self):
        for strategy in STRATEGIES:
            self.assertEqual(run_search("index", [], self.words("hash"), strategy=strategy), [])
            self.assertEqual(run_search("linear", [], self.words("hash"), strategy=strategy), [])

    def test_results_are_the_same_on_every_run(self):
        first = self.view(run_search("index", CORPUS, self.words("tables heaps"), strategy=STRATEGIES[1]))
        second = self.view(run_search("index", CORPUS, self.words("tables heaps"), strategy=STRATEGIES[1]))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()