"""Inverted index: word -> postings list, built from our own hash table and postings lists.

Structure
---------
* self._terms    : HashTable   word        -> PostingsList (which passages contain the word)
* self._passages : HashTable   passage_id  -> IndexedPassage (the passage + the words we indexed)

Rules (these answer the PDF's questions)
----------------------------------------
* Same preprocessing as the linear scan: tokenize(title + " " + text).
* Repeated word in one passage  -> ONE posting with a higher term_frequency.
* Collisions                    -> handled inside HashTable (separate chaining).
* Adding a passage whose ID already exists is an UPDATE: the old version is
  removed from the index first, then the new version is indexed.
* Two different passage IDs with identical text are two separate passages.
* find_candidates() only FINDS and SCORES candidates. Ranking/top-k is a later milestone.
"""

from src.tokenizer import tokenize, unique_tokens
from src.hash_table import HashTable, default_hash
from src.postings import PostingsList


class IndexedPassage:
    """What we remember about one indexed passage."""

    def __init__(self, passage, terms):
        self.passage = passage   # the full original record (all metadata kept)
        self.terms = terms       # unique words we indexed for it (needed for removal)


class Candidate:
    """A passage that matched at least one query word, collected during a search."""

    def __init__(self, passage):
        self.passage = passage
        self.matched_words = []


class InvertedIndex:
    def __init__(self, initial_size=8, hash_function=default_hash):
        self._terms = HashTable(initial_size=initial_size, hash_function=hash_function)
        self._passages = HashTable()

    # ---------- building and changing the index ----------

    def _check_passage(self, passage):
        if not isinstance(passage, dict):
            raise TypeError("a passage must be a record (dict), but got " + type(passage).__name__)
        for field in ["passage_id", "title", "text"]:
            if field not in passage:
                raise ValueError("passage is missing the field '" + field + "'")
            if not isinstance(passage[field], str) or passage[field].strip() == "":
                raise ValueError("passage field '" + field + "' must be non-blank text")

    def add_passage(self, passage):
        """Index one passage. Returns True if it is new, False if it replaced an older version."""
        self._check_passage(passage)
        passage_id = passage["passage_id"]

        is_new = True
        if self._passages.contains(passage_id):
            self.remove_passage(passage_id)     # an update = remove the old version first
            is_new = False

        tokens = tokenize(passage["title"] + " " + passage["text"])
        for token in tokens:
            postings = self._terms.get(token)
            if postings is None:                # first time we see this word
                postings = PostingsList()
                self._terms.put(token, postings)
            postings.add_occurrence(passage_id)

        self._passages.put(passage_id, IndexedPassage(passage, unique_tokens(tokens)))
        return is_new

    def remove_passage(self, passage_id):
        """Take a passage out of the index. Returns True if it was there."""
        record = self._passages.get(passage_id)
        if record is None:
            return False
        for term in record.terms:
            postings = self._terms.get(term)
            postings.remove(passage_id)
            if len(postings) == 0:              # nobody uses this word any more
                self._terms.remove(term)
        self._passages.remove(passage_id)
        return True

    # ---------- looking things up ----------

    def get_postings(self, term):
        """The PostingsList for an (already tokenized) word, or None."""
        return self._terms.get(term)

    def get_passage(self, passage_id):
        """The original passage record, or None."""
        record = self._passages.get(passage_id)
        if record is None:
            return None
        return record.passage

    def find_candidates(self, query_words):
        """Find every passage that contains at least one query word.

        query_words must already be a list of unique tokens (same contract as linear_search).
        Returns a list of {"passage", "score", "matched_words"} records in NO particular
        order (ranking comes later). The score is the number of query words matched.
        """
        candidates = HashTable()      # passage_id -> Candidate
        for word in query_words:
            postings = self._terms.get(word)
            if postings is None:
                continue
            for passage_id in postings.passage_ids():
                candidate = candidates.get(passage_id)
                if candidate is None:
                    candidate = Candidate(self._passages.get(passage_id).passage)
                    candidates.put(passage_id, candidate)
                candidate.matched_words.append(word)

        results = []
        for passage_id in candidates.keys():
            candidate = candidates.get(passage_id)
            results.append({
                "passage": candidate.passage,
                "score": len(candidate.matched_words),
                "matched_words": candidate.matched_words,
            })
        return results

    # ---------- statistics ----------

    def passage_count(self):
        return len(self._passages)

    def passage_ids(self):
        return self._passages.keys()

    def vocabulary(self):
        return self._terms.keys()

    def vocabulary_size(self):
        return len(self._terms)

    def total_postings(self):
        """P: the number of (word, passage) pairs stored in the whole index."""
        total = 0
        for term in self._terms.keys():
            total += len(self._terms.get(term))
        return total

    def term_table_stats(self):
        """(buckets, load factor, longest chain, collisions) of the vocabulary hash table."""
        return (self._terms.bucket_count(), self._terms.load_factor(),
                self._terms.longest_chain(), self._terms.collision_count())


if __name__ == "__main__":
    import json

    with open("data/passages.json", "r", encoding="utf-8") as json_file:
        passages = json.load(json_file)

    index = InvertedIndex()
    for passage in passages:
        index.add_passage(passage)

    buckets, load, longest, collisions = index.term_table_stats()
    print("Built index from data/passages.json")
    print(f"passages indexed : {index.passage_count()}")
    print(f"vocabulary (V)   : {index.vocabulary_size()} unique words")
    print(f"postings (P)     : {index.total_postings()}")
    print(f"hash table       : buckets={buckets}  load factor={load:.3f}  "
          f"longest chain={longest}  collisions={collisions}")

    print()
    print("Postings for some words:")
    for word in ["data", "students", "examination", "football"]:
        postings = index.get_postings(word)
        print(f"  {word:<12} {postings.to_pairs() if postings is not None else 'not in the index'}")

    print()
    print("Candidate retrieval (unranked; shown sorted by passage_id):")
    for query in ["data structures", "examination schedule", "football", "students"]:
        words = unique_tokens(tokenize(query))
        found = index.find_candidates(words)
        print(f"query: {query}")
        if len(found) == 0:
            print("  No supported evidence found")
        for match in sorted(found, key=lambda m: m["passage"]["passage_id"]):
            print(f"  {match['passage']['passage_id']}  score {match['score']}  "
                  f"matched: {', '.join(match['matched_words'])}")