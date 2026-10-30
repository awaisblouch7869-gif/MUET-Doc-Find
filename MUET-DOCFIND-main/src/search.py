"""Search methods: linear scan (baseline) and inverted index, plus ranking of the results.

Both methods return UNRANKED candidates first. Ranking is done afterwards by the SAME
code (src/ranking.py), so any difference between the methods can only come from retrieval.
"""

from typing import Any

from src.config import MAX_RESULTS
from src.inverted_index import InvertedIndex
from src.ranking import NormalizedCoverage, SharedTermCount, rank_candidates, ranking_key
from src.tokenizer import tokenize, unique_tokens

STRATEGIES = [SharedTermCount(), NormalizedCoverage()]


def linear_candidates(passages: list[dict[str, Any]], query_words: list[str]) -> list[dict[str, Any]]:
    """Check EVERY passage one by one. Return all passages that match, UNRANKED.

    query_words must already be a list of unique tokens (see src/tokenizer.py).
    """
    matches = []
    for passage in passages:
        passage_words = unique_tokens(tokenize(passage["title"] + " " + passage["text"]))

        matched_words = []
        for query_word in query_words:
            if query_word in passage_words:
                matched_words.append(query_word)

        if len(matched_words) > 0:
            matches.append({
                "passage": passage,
                "score": len(matched_words),
                "matched_words": matched_words,
            })
    return matches


def linear_search(passages: list[dict[str, Any]], query_words: list[str],
                  max_results: int = MAX_RESULTS) -> list[dict[str, Any]]:
    """Linear scan, then rank and keep the best max_results (uses Python's sorted(), as in Milestone 2)."""
    matches = linear_candidates(passages, query_words)
    ranked = sorted(matches, key=ranking_key)
    return ranked[:max_results]


def get_candidates(method: str, passages: list[dict[str, Any]], query_words: list[str]) -> list[dict[str, Any]]:
    """Retrieval step only: return the UNRANKED candidates using "linear" or "index"."""
    if method == "index":
        index = InvertedIndex()
        for passage in passages:
            index.add_passage(passage)
        return index.find_candidates(query_words)
    return linear_candidates(passages, query_words)


def run_search(method: str, passages: list[dict[str, Any]], query_words: list[str],
               max_results: int = MAX_RESULTS, strategy=None) -> list[dict[str, Any]]:
    """Find candidates with the chosen method, then rank them with the chosen strategy.

    The default strategy is Strategy 1 (shared-term count).
    """
    if strategy is None:
        strategy = STRATEGIES[0]
    candidates = get_candidates(method, passages, query_words)
    return rank_candidates(candidates, strategy, len(query_words), max_results)
