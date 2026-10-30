import unittest

from src.tokenizer import tokenize, unique_tokens


class TestTokenize(unittest.TestCase):
    def test_lowercases_words(self):
        self.assertEqual(tokenize("Data STRUCTURES"), ["data", "structures"])

    def test_punctuation_is_removed(self):
        self.assertEqual(tokenize("Lab rules, (strict)!"), ["lab", "rules", "strict"])

    def test_hyphen_splits_a_word(self):
        self.assertEqual(tokenize("mid-term"), ["mid", "term"])

    def test_apostrophes_are_deleted_not_split(self):
        self.assertEqual(tokenize("student's"), ["students"])
        self.assertEqual(tokenize("student\u2019s"), ["students"])

    def test_digits_are_kept(self):
        self.assertEqual(tokenize("Week 8 of v2"), ["week", "8", "v2"])

    def test_stop_words_are_removed(self):
        self.assertEqual(tokenize("the attendance of the students"), ["attendance", "students"])

    def test_meaningful_words_are_not_stop_words(self):
        self.assertEqual(tokenize("must not"), ["must", "not"])

    def test_repeated_terms_are_kept_by_tokenize(self):
        self.assertEqual(tokenize("data data DATA"), ["data", "data", "data"])

    def test_unique_tokens_removes_repeats_and_keeps_order(self):
        self.assertEqual(unique_tokens(["data", "lab", "data", "lab", "exam"]), ["data", "lab", "exam"])

    def test_empty_and_blank_text_gives_no_tokens(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   "), [])
        self.assertEqual(tokenize("!!! ???"), [])

    def test_only_stop_words_gives_no_tokens(self):
        self.assertEqual(tokenize("the of and"), [])

    def test_same_input_gives_same_output(self):
        text = "The Midterm Examination, moved to Week 9!"
        self.assertEqual(tokenize(text), tokenize(text))

    def test_non_text_input_raises_error(self):
        with self.assertRaises(TypeError):
            tokenize(None)


if __name__ == "__main__":
    unittest.main()