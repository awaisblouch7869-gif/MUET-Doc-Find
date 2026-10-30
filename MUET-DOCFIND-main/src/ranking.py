"""Ranking: put candidate passages in order, best first.

A "strategy" is a small object that knows how to turn a candidate into a score.

Strategy 1: SharedTermCount    = how many of the query's unique words the passage contains.
Strategy 2: NormalizedCoverage = matched query words divided by the number of unique
            words in the passage ("match density"). A short passage that is mostly
            about the query beats a long passage that mentions it in passing.

Why Strategy 2 does NOT divide by the number of query words: that number is the same
for every candidate of one query, so the ORDER would never change and the comparison
would be pointless. Dividing by the passage length makes the strategies differ.

Both strategies are given the SAME candidates, so any difference in order comes only
from the scoring rule.

Tie-break (deterministic): when two passages have the same score, the one with
the smaller passage_id comes first. IDs are compared as TEXT, so give every ID
the same width (P001, P002, ... P100), otherwise "P10" would sort before "P9".

Choosing the best k: this module no longer uses a library sort. It calls our own
routines in src/topk.py: a bounded heap (default) or our own merge sort.
Both give identical results. (src/search.py's linear_search still uses Python's sorted()
from Milestone 2; that is a declared library operation in the baseline only.)
"""

from src.tokenizer import tokenize, unique_tokens
from src.topk import top_k_heap, top_k_sort

SELECTORS = ["heap", "sort"]


class SharedTermCount:
    """Strategy 1: score = number of query words found in the passage."""

    name = "shared-term count"

    def score(self, matched_words, query_word_count, passage=None):
        return len(matched_words)

    def show(self, score):
        return str(score)


class NormalizedCoverage:
    """Strategy 2: score = matched query words / unique words in the passage."""

    name = "normalized coverage"

    def score(self, matched_words, query_word_count, passage=None):
        if passage is None:
            raise ValueError("NormalizedCoverage needs the passage to measure its length.")
        passage_length = len(unique_tokens(tokenize(passage["title"] + " " + passage["text"])))
        if passage_length == 0:
            return 0.0
        return len(matched_words) / passage_length

    def show(self, score):
        return f"{score:.3f}"


def ranking_key(match):
    """Sort key: higher score first, then smaller passage_id first."""
    return (-match["score"], match["passage"]["passage_id"])


def rank_candidates(candidates, strategy, query_word_count, max_results, selector="heap"):
    """Score every candidate with the strategy, order them, and keep the best max_results.

    candidates: records with "passage" and "matched_words" (from either search method).
    selector: "heap" (bounded heap, O(C log k)) or "sort" (merge sort of everything, O(C log C)).
    Returns new records {"passage", "score", "matched_words"}; the input list is not changed.
    """
    if not isinstance(max_results, int) or max_results < 1:
        raise ValueError("max_results must be a whole number of at least 1.")
    if selector not in SELECTORS:
        raise ValueError(f"selector must be one of: {', '.join(SELECTORS)}.")

    scored = []
    for candidate in candidates:
        scored.append({
            "passage": candidate["passage"],
            "score": strategy.score(candidate["matched_words"], query_word_count, candidate["passage"]),
            "matched_words": candidate["matched_words"],
        })

    if selector == "heap":
        return top_k_heap(scored, max_results, ranking_key)
    return top_k_sort(scored, max_results, ranking_key)