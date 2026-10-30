"""Postings list: the list of passages that contain ONE word, as a linked list.

An inverted index maps each word to a postings list. Each node in the list
(a "posting") says: "this word appears in passage <passage_id>, <term_frequency> times".

Design decisions
----------------
* One posting per passage. If a word appears 3 times in the same passage, we do
  NOT create 3 postings. We keep one posting and raise its term_frequency to 3.
* A posting stores the passage_id (text), not a position number, so it stays
  valid and traceable even if passages are added or updated later.
* New postings are added at the END (tail), so the list keeps insertion order.
* A tail pointer makes "add at the end" cheap. Finding an existing posting
  means walking the list from the front.

This file imports nothing.
"""


class Posting:
    """One node: which passage, how many times the word occurs there, and the next node."""

    def __init__(self, passage_id, term_frequency=1):
        self.passage_id = passage_id
        self.term_frequency = term_frequency
        self.next = None


class PostingsList:
    def __init__(self):
        self._head = None     # first posting (None when the list is empty)
        self._tail = None     # last posting
        self._length = 0      # number of postings = number of passages containing the word

    def _check_id(self, passage_id):
        if not isinstance(passage_id, str):
            raise TypeError("passage_id must be a string, but got " + type(passage_id).__name__)
        if passage_id.strip() == "":
            raise ValueError("passage_id must not be blank.")

    def _find_posting(self, passage_id):
        """Walk from the front. Return the Posting for passage_id, or None."""
        node = self._head
        while node is not None:
            if node.passage_id == passage_id:
                return node
            node = node.next
        return None

    def add_occurrence(self, passage_id):
        """Record ONE occurrence of the word in the given passage.

        Returns True if this created a new posting (first time this passage
        is seen), or False if it only raised an existing term_frequency.
        """
        self._check_id(passage_id)

        existing = self._find_posting(passage_id)
        if existing is not None:
            existing.term_frequency += 1
            return False

        new_posting = Posting(passage_id, 1)
        if self._tail is None:            # the list was empty
            self._head = new_posting
        else:
            self._tail.next = new_posting
        self._tail = new_posting
        self._length += 1
        return True

    def remove(self, passage_id):
        """Delete the posting for a passage. Returns True if it existed."""
        self._check_id(passage_id)
        previous = None
        node = self._head
        while node is not None:
            if node.passage_id == passage_id:
                if previous is None:
                    self._head = node.next        # removing the first posting
                else:
                    previous.next = node.next     # skip over it
                if node is self._tail:
                    self._tail = previous         # the last posting changed
                self._length -= 1
                return True
            previous = node
            node = node.next
        return False

    def contains(self, passage_id):
        self._check_id(passage_id)
        return self._find_posting(passage_id) is not None

    def frequency_of(self, passage_id):
        """How many times the word occurs in this passage (0 if not at all)."""
        self._check_id(passage_id)
        node = self._find_posting(passage_id)
        if node is None:
            return 0
        return node.term_frequency

    def __len__(self):
        return self._length

    def passage_ids(self):
        """The passage IDs, in list order."""
        result = []
        node = self._head
        while node is not None:
            result.append(node.passage_id)
            node = node.next
        return result

    def to_pairs(self):
        """A plain list of (passage_id, term_frequency) pairs, in list order."""
        result = []
        node = self._head
        while node is not None:
            result.append((node.passage_id, node.term_frequency))
            node = node.next
        return result

    def total_occurrences(self):
        """Sum of all term frequencies: how often the word occurs in the whole collection."""
        total = 0
        node = self._head
        while node is not None:
            total += node.term_frequency
            node = node.next
        return total


if __name__ == "__main__":
    postings = PostingsList()

    print("Word 'students' is found in P002, then P003 (twice), then P005:")
    for passage_id in ["P002", "P003", "P003", "P005"]:
        created = postings.add_occurrence(passage_id)
        print(f"  add_occurrence({passage_id!r}) -> new posting created: {created}")
    print(f"  postings            : {postings.to_pairs()}")
    print(f"  passages containing : {len(postings)}")
    print(f"  total occurrences   : {postings.total_occurrences()}")

    print()
    print("Passage P003 is edited, so its old posting is removed:")
    print(f"  remove('P003') -> {postings.remove('P003')}")
    print(f"  postings            : {postings.to_pairs()}")

    print()
    print("The new version of P003 is indexed again (it joins at the END):")
    postings.add_occurrence("P003")
    print(f"  postings            : {postings.to_pairs()}")
    print(f"  frequency_of('P003'): {postings.frequency_of('P003')}")
    print(f"  frequency_of('P001'): {postings.frequency_of('P001')}")