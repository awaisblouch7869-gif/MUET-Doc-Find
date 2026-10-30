import contextlib
import io
import unittest

from main import main
from src.config import NO_EVIDENCE_MESSAGE


def run_cli(arguments):
    """Run main() with the given arguments and return everything it printed."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        main(arguments)
    return buffer.getvalue()


class TestCommandLine(unittest.TestCase):
    def test_no_evidence_message_is_exact_for_both_methods(self):
        for method in ("--linear", "--index"):
            output = run_cli(["--full", method, "zzzzqqqq"])
            self.assertEqual(output.strip().splitlines()[-1], "No supported evidence found")
        self.assertEqual(NO_EVIDENCE_MESSAGE, "No supported evidence found")

    def test_no_evidence_message_is_exact_in_compare_mode(self):
        output = run_cli(["--full", "--compare", "zzzzqqqq"])
        self.assertEqual(output.strip().splitlines()[-1], "No supported evidence found")

    def test_blank_query_is_rejected_politely(self):
        output = run_cli(["--index", "   "])
        self.assertIn("Blank query", output)

    def test_unknown_option_is_rejected(self):
        self.assertIn("unknown option '--bogus'", run_cli(["--bogus", "x"]))

    def test_both_methods_find_the_same_top_passage(self):
        linear = run_cli(["--full", "--linear", "binary search"])
        index = run_cli(["--full", "--index", "binary search"])
        first = lambda text: next(l for l in text.splitlines() if l.startswith("passage_id"))
        self.assertEqual(first(linear), first(index))


if __name__ == "__main__":
    unittest.main()
