import unittest

from src.versions import get_outdated_passage_ids


def passage(passage_id, document_id, version):
    return {"passage_id": passage_id, "document_id": document_id, "title": "T",
            "category": "Test", "source": "SYNTHETIC test data", "version": version,
            "date": "2026-01-01", "text": "x"}


class TestOutdatedPassages(unittest.TestCase):
    def test_older_version_of_a_document_is_outdated_and_newest_is_not(self):
        passages = [passage("P001", "D01", "v1"), passage("P002", "D01", "v2")]
        self.assertEqual(get_outdated_passage_ids(passages), {"P001"})

    def test_every_passage_of_an_older_version_is_outdated(self):
        passages = [passage("P001", "D01", "v1"), passage("P002", "D01", "v1"),
                    passage("P003", "D01", "v2"), passage("P004", "D01", "v2")]
        self.assertEqual(get_outdated_passage_ids(passages), {"P001", "P002"})

    def test_versions_are_compared_as_numbers_not_as_text(self):
        passages = [passage("P001", "D01", "v2"), passage("P002", "D01", "v10")]
        self.assertEqual(get_outdated_passage_ids(passages), {"P001"})

    def test_capital_v_is_accepted(self):
        passages = [passage("P001", "D01", "V1"), passage("P002", "D01", "V2")]
        self.assertEqual(get_outdated_passage_ids(passages), {"P001"})

    def test_documents_are_judged_independently(self):
        passages = [passage("P001", "D01", "v1"),
                    passage("P002", "D02", "v1"), passage("P003", "D02", "v2")]
        self.assertEqual(get_outdated_passage_ids(passages), {"P002"})

    def test_a_single_version_is_never_outdated(self):
        passages = [passage("P001", "D01", "v1"), passage("P002", "D01", "v1")]
        self.assertEqual(get_outdated_passage_ids(passages), set())

    def test_three_versions_only_the_newest_is_current(self):
        passages = [passage("P001", "D01", "v1"), passage("P002", "D01", "v2"), passage("P003", "D01", "v3")]
        self.assertEqual(get_outdated_passage_ids(passages), {"P001", "P002"})

    def test_empty_collection(self):
        self.assertEqual(get_outdated_passage_ids([]), set())

    def test_input_order_does_not_matter(self):
        forward = [passage("P001", "D01", "v1"), passage("P002", "D01", "v2")]
        backward = list(reversed(forward))
        self.assertEqual(get_outdated_passage_ids(forward), get_outdated_passage_ids(backward))

    def test_input_is_not_changed(self):
        passages = [passage("P001", "D01", "v1"), passage("P002", "D01", "v2")]
        get_outdated_passage_ids(passages)
        self.assertEqual([p["passage_id"] for p in passages], ["P001", "P002"])
        self.assertEqual(passages[0]["version"], "v1")

    def test_unreadable_version_is_skipped_without_crashing(self):
        # Documents CURRENT behaviour: such a passage is never marked outdated, so
        # it is shown as CURRENT. That is a known weakness (see the report/limitations).
        passages = [passage("P001", "D01", "draft"), passage("P002", "D01", "v1"),
                    passage("P003", "D01", "v2"), passage("P004", "D01", "1.2"), passage("P005", "D01", "v")]
        self.assertEqual(get_outdated_passage_ids(passages), {"P002"})


if __name__ == "__main__":
    unittest.main()