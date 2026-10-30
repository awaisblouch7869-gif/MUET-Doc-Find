import unittest

from src.loader import load_passages
from src.ranking import ranking_key
from src.search import linear_search
from src.hash_table import always_zero
from src.inverted_index import InvertedIndex
from src.tokenizer import tokenize, unique_tokens


def make_passage(passage_id, title, text, version="v1"):
    return {
        "passage_id": passage_id, "document_id": "D" + passage_id[1:], "title": title,
        "category": "Test", "source": "SYNTHETIC test data", "version": version,
        "date": "2026-01-01", "text": text,
    }


def words(query):
    return unique_tokens(tokenize(query))


def summary(matches):
    """Order-independent view of a result list: sorted (passage_id, score, matched words)."""
    rows = []
    for match in matches:
        rows.append((match["passage"]["passage_id"], match["score"], list(match["matched_words"])))
    return sorted(rows)


def build(passages, **settings):
    index = InvertedIndex(**settings)
    for passage in passages:
        index.add_passage(passage)
    return index


class TestBuildingAndLookup(unittest.TestCase):
    def test_empty_index(self):
        index = InvertedIndex()
        self.assertEqual(index.passage_count(), 0)
        self.assertEqual(index.vocabulary_size(), 0)
        self.assertEqual(index.total_postings(), 0)
        self.assertIsNone(index.get_postings("data"))
        self.assertEqual(index.find_candidates(words("data")), [])

    def test_one_passage_is_indexed_and_keeps_its_metadata(self):
        index = build([make_passage("P001", "Data Structures", "arrays and heaps", version="v7")])
        self.assertEqual(index.passage_count(), 1)
        self.assertEqual(index.get_postings("data").passage_ids(), ["P001"])
        self.assertEqual(index.get_passage("P001")["version"], "v7")
        self.assertEqual(index.get_passage("P001")["document_id"], "D001")
        self.assertIsNone(index.get_passage("P999"))

    def test_title_and_text_are_both_indexed(self):
        index = build([make_passage("P001", "Laboratory", "Bring your notebook")])
        self.assertIsNotNone(index.get_postings("laboratory"))
        self.assertIsNotNone(index.get_postings("notebook"))

    def test_stop_words_are_not_indexed(self):
        index = build([make_passage("P001", "The Lab", "the rules of the lab")])
        self.assertIsNone(index.get_postings("the"))
        self.assertIsNone(index.get_postings("of"))
        self.assertIsNotNone(index.get_postings("rules"))

    def test_repeated_word_in_one_passage_is_one_posting_with_higher_frequency(self):
        index = build([make_passage("P001", "Notice", "data data data")])
        postings = index.get_postings("data")
        self.assertEqual(len(postings), 1)
        self.assertEqual(postings.frequency_of("P001"), 3)

    def test_word_shared_by_passages_has_one_posting_per_passage(self):
        index = build([make_passage("P001", "Lab", "rules"), make_passage("P002", "Lab", "safety")])
        self.assertEqual(index.get_postings("lab").passage_ids(), ["P001", "P002"])

    def test_invalid_passages_are_rejected(self):
        index = InvertedIndex()
        with self.assertRaises(TypeError):
            index.add_passage("not a record")
        with self.assertRaises(ValueError):
            index.add_passage({"passage_id": "P001", "text": "no title"})
        with self.assertRaises(ValueError):
            index.add_passage(make_passage("P001", "   ", "text"))


class TestUpdatesAndRemoval(unittest.TestCase):
    def test_same_id_is_an_update_not_a_duplicate(self):
        index = InvertedIndex()
        self.assertTrue(index.add_passage(make_passage("P001", "Exam", "held in week eight", version="v1")))
        self.assertFalse(index.add_passage(make_passage("P001", "Exam", "moved to week nine", version="v2")))
        self.assertEqual(index.passage_count(), 1)
        self.assertIsNone(index.get_postings("held"))                     # old-only word is gone
        self.assertEqual(index.get_postings("moved").passage_ids(), ["P001"])
        self.assertEqual(index.get_postings("exam").passage_ids(), ["P001"])
        self.assertEqual(index.get_passage("P001")["version"], "v2")

    def test_remove_passage(self):
        index = build([make_passage("P001", "Lab", "rules"), make_passage("P002", "Lab", "safety")])
        self.assertTrue(index.remove_passage("P001"))
        self.assertEqual(index.get_postings("lab").passage_ids(), ["P002"])
        self.assertIsNone(index.get_postings("rules"))
        self.assertEqual(index.passage_count(), 1)

    def test_remove_missing_passage_returns_false(self):
        self.assertFalse(InvertedIndex().remove_passage("P001"))

    def test_removing_everything_leaves_an_empty_index(self):
        index = build([make_passage("P001", "Lab", "rules"), make_passage("P002", "Lab", "safety")])
        index.remove_passage("P001")
        index.remove_passage("P002")
        self.assertEqual(index.vocabulary_size(), 0)
        self.assertEqual(index.total_postings(), 0)


class TestCandidates(unittest.TestCase):
    def setUp(self):
        self.index = build([
            make_passage("P001", "Data Structures", "arrays"),
            make_passage("P002", "Notice", "data only"),
            make_passage("P003", "Lab", "nothing relevant"),
        ])

    def test_scores_and_matched_words(self):
        found = summary(self.index.find_candidates(words("data structures")))
        self.assertEqual(found, [("P001", 2, ["data", "structures"]), ("P002", 1, ["data"])])

    def test_unknown_word_gives_no_candidates(self):
        self.assertEqual(self.index.find_candidates(words("football")), [])

    def test_empty_query_gives_no_candidates(self):
        self.assertEqual(self.index.find_candidates([]), [])

    def test_near_duplicate_passages_with_different_ids_are_both_found(self):
        index = build([make_passage("P001", "Lab", "wear a coat"), make_passage("P002", "Lab", "wear a coat")])
        self.assertEqual(len(index.find_candidates(words("coat"))), 2)


class TestCollisionsInTheIndex(unittest.TestCase):
    def test_all_words_in_one_bucket_still_gives_correct_results(self):
        passages = [make_passage("P001", "Data Structures", "arrays heaps"),
                    make_passage("P002", "Lab Rules", "heaps and safety")]
        normal = build(passages)
        crowded = build(passages, hash_function=always_zero)
        self.assertEqual(crowded.term_table_stats()[2], crowded.vocabulary_size())   # one long chain
        for query in ["data", "heaps", "lab safety", "football", "arrays rules"]:
            self.assertEqual(summary(crowded.find_candidates(words(query))),
                             summary(normal.find_candidates(words(query))))


class TestSameResultsAsLinearScan(unittest.TestCase):
    def check_same(self, passages, index, queries):
        for query in queries:
            query_words = words(query)
            linear_all = linear_search(passages, query_words, max_results=1000)
            self.assertEqual(summary(index.find_candidates(query_words)), summary(linear_all), query)

            # after applying the SAME ranking rule, the top 3 are identical too
            ranked = sorted(index.find_candidates(query_words), key=ranking_key)[:3]
            self.assertEqual([m["passage"]["passage_id"] for m in ranked],
                             [m["passage"]["passage_id"] for m in linear_search(passages, query_words)], query)

    def test_on_the_sample_data(self):
        passages = load_passages("data/passages.json")
        index = build(passages)
        self.check_same(passages, index, [
            "data structures", "examination schedule", "football", "students",
            "lab files", "midterm examination week", "the", "", "hash tables heaps sorting",
        ])

    def test_on_a_generated_corpus_with_many_overlapping_words(self):
        vocabulary = ["alpha", "beta", "gamma", "delta", "lab", "exam", "notice", "data",
                      "rules", "week", "marks", "viva"]
        passages = []
        for number in range(30):
            chosen = []
            for position in range(5 + number % 4):                   # 5 to 8 words, with repeats
                chosen.append(vocabulary[(number * 7 + position * 3) % len(vocabulary)])
            passages.append(make_passage("P" + str(100 + number), "Doc " + vocabulary[number % 12], " ".join(chosen)))
        index = build(passages)

        queries = list(vocabulary)
        for first in range(len(vocabulary)):
            queries.append(vocabulary[first] + " " + vocabulary[(first * 5 + 2) % len(vocabulary)])
        queries.append("alpha beta gamma delta lab")
        queries.append("unknownword")
        self.check_same(passages, index, queries)


class TestStatisticsAndDeterminism(unittest.TestCase):
    def test_statistics_match_an_independent_count(self):
        passages = load_passages("data/passages.json")
        index = build(passages)
        expected_postings = 0
        all_terms = []
        for passage in passages:
            terms = unique_tokens(tokenize(passage["title"] + " " + passage["text"]))
            expected_postings += len(terms)
            for term in terms:
                if term not in all_terms:
                    all_terms.append(term)
        self.assertEqual(index.passage_count(), len(passages))
        self.assertEqual(index.total_postings(), expected_postings)
        self.assertEqual(index.vocabulary_size(), len(all_terms))

    def test_building_twice_gives_identical_layout(self):
        passages = load_passages("data/passages.json")
        first = build(passages)
        second = build(passages)
        self.assertEqual(first.vocabulary(), second.vocabulary())
        self.assertEqual(first.term_table_stats(), second.term_table_stats())


if __name__ == "__main__":
    unittest.main()