import json
import os
import tempfile
import unittest

from src.config import DATA_FILE, FULL_DATA_FILE, OFFICIAL_DATA_FILE
from src.loader import REQUIRED_FIELDS, check_fields, load_passages


def write_temp(text, encoding="utf-8"):
    handle, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(handle, "w", encoding=encoding) as file:
        file.write(text)
    return path


def good_passage():
    return {field: "x" for field in REQUIRED_FIELDS}


class TestLoadPassages(unittest.TestCase):
    def test_all_configured_data_files_load_and_are_valid(self):
        for path in (DATA_FILE, FULL_DATA_FILE, OFFICIAL_DATA_FILE):
            passages = load_passages(path)
            self.assertGreater(len(passages), 0, path)
            self.assertEqual(check_fields(passages), [], path)

    def test_corpus_sizes(self):
        self.assertEqual(len(load_passages(DATA_FILE)), 5)
        self.assertEqual(len(load_passages(FULL_DATA_FILE)), 150)

    def test_file_that_starts_with_a_bom_can_be_read(self):
        path = write_temp("[]", encoding="utf-8-sig")
        self.addCleanup(os.remove, path)
        self.assertEqual(load_passages(path), [])

    def test_top_level_must_be_a_list(self):
        path = write_temp(json.dumps({"passage_id": "P1"}))
        self.addCleanup(os.remove, path)
        with self.assertRaises(ValueError):
            load_passages(path)

    def test_broken_json_is_reported_as_value_error(self):
        path = write_temp("[{ not json")
        self.addCleanup(os.remove, path)
        with self.assertRaises(ValueError):
            load_passages(path)

    def test_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_passages("data/does_not_exist.json")


class TestCheckFields(unittest.TestCase):
    def test_good_passage_has_no_problems(self):
        self.assertEqual(check_fields([good_passage()]), [])

    def test_missing_field_is_reported(self):
        passage = good_passage()
        del passage["version"]
        problems = check_fields([passage])
        self.assertEqual(len(problems), 1)
        self.assertIn("version", problems[0])

    def test_empty_and_non_text_fields_are_reported(self):
        passage = good_passage()
        passage["text"] = "   "
        passage["date"] = 2025
        self.assertEqual(len(check_fields([passage])), 2)

    def test_non_object_entry_is_reported(self):
        self.assertEqual(len(check_fields(["not a passage"])), 1)


if __name__ == "__main__":
    unittest.main()
