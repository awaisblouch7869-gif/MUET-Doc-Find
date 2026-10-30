"""Our own hash table (maps a text key to any value), written from scratch.

How it works
------------
* The table is an ARRAY of buckets. Each bucket holds a linked list (a "chain")
  of entries, so two keys that land in the same bucket can live together.
  This way of handling collisions is called SEPARATE CHAINING.
* default_hash() turns a key into a big number. "number % bucket_count" picks
  the bucket.
* When the table gets too full (load factor = entries / buckets is above
  max_load_factor) it doubles its bucket count and re-places every entry.

This file imports nothing. It deliberately does not use Python's built-in
dictionary, set, or any other ready-made hash structure.
"""


class Node:
    """One entry in a chain: a key, its value, and a link to the next entry."""

    def __init__(self, key, value, next_node=None):
        self.key = key
        self.value = value
        self.next = next_node


def default_hash(key):
    """Our own string hash (the classic 'djb2' idea, written as a plain loop).

    Python's built-in hash() gives different numbers on different runs for
    strings, so we do NOT use it. This function gives the same answer every
    time, on every computer. The % 4294967296 keeps the number within 32 bits.
    """
    hash_value = 5381
    for character in key:
        hash_value = (hash_value * 33 + ord(character)) % 4294967296
    return hash_value


class HashTable:
    def __init__(self, initial_size=8, max_load_factor=0.75, hash_function=default_hash):
        if not isinstance(initial_size, int) or initial_size < 1:
            raise ValueError("initial_size must be a whole number of at least 1.")
        if max_load_factor <= 0:
            raise ValueError("max_load_factor must be greater than 0.")
        self._buckets = [None] * initial_size   # the array; None means "empty bucket"
        self._count = 0                         # how many entries are stored
        self._max_load_factor = max_load_factor
        self._hash_function = hash_function

    # ---------- helpers (names start with _ : for internal use) ----------

    def _check_key(self, key):
        if not isinstance(key, str):
            raise TypeError("keys must be strings, but got " + type(key).__name__)

    def _index_for(self, key, bucket_count):
        return self._hash_function(key) % bucket_count

    def _find_node(self, key):
        """Walk along the key's chain. Return its Node, or None if absent."""
        node = self._buckets[self._index_for(key, len(self._buckets))]
        while node is not None:
            if node.key == key:
                return node
            node = node.next
        return None

    def _resize(self, new_bucket_count):
        """Make a bigger array and move every existing Node into it."""
        new_buckets = [None] * new_bucket_count
        for head in self._buckets:
            node = head
            while node is not None:
                next_node = node.next                      # remember it BEFORE relinking
                index = self._index_for(node.key, new_bucket_count)
                node.next = new_buckets[index]             # put node at the front of its new chain
                new_buckets[index] = node
                node = next_node
        self._buckets = new_buckets

    # ---------- main operations ----------

    def put(self, key, value):
        """Add key -> value. If the key exists, replace its value.

        Returns True if a new entry was added, False if an old one was updated.
        """
        self._check_key(key)
        node = self._find_node(key)
        if node is not None:
            node.value = value
            return False

        index = self._index_for(key, len(self._buckets))
        self._buckets[index] = Node(key, value, self._buckets[index])  # new node goes at the front
        self._count += 1

        if self._count / len(self._buckets) > self._max_load_factor:
            self._resize(len(self._buckets) * 2)
        return True

    def get(self, key, default=None):
        """Return the value stored for key, or default if the key is absent."""
        self._check_key(key)
        node = self._find_node(key)
        if node is None:
            return default
        return node.value

    def contains(self, key):
        """Return True if the key is stored."""
        self._check_key(key)
        return self._find_node(key) is not None

    def remove(self, key):
        """Delete the key. Returns True if it was there, False if not."""
        self._check_key(key)
        index = self._index_for(key, len(self._buckets))
        previous = None
        node = self._buckets[index]
        while node is not None:
            if node.key == key:
                if previous is None:
                    self._buckets[index] = node.next   # it was the first node in the chain
                else:
                    previous.next = node.next          # skip over it
                self._count -= 1
                return True
            previous = node
            node = node.next
        return False

    def __len__(self):
        return self._count

    def keys(self):
        """All keys, in a fixed order: bucket by bucket, front of chain to back."""
        result = []
        for head in self._buckets:
            node = head
            while node is not None:
                result.append(node.key)
                node = node.next
        return result

    # ---------- statistics (used for tests, the report and memory estimates) ----------

    def bucket_count(self):
        return len(self._buckets)

    def load_factor(self):
        return self._count / len(self._buckets)

    def bucket_keys(self, index):
        """The keys stored in one bucket, front of the chain first."""
        result = []
        node = self._buckets[index]
        while node is not None:
            result.append(node.key)
            node = node.next
        return result

    def longest_chain(self):
        longest = 0
        for index in range(len(self._buckets)):
            length = len(self.bucket_keys(index))
            if length > longest:
                longest = length
        return longest

    def collision_count(self):
        """How many entries share a bucket with an entry that arrived before them."""
        collisions = 0
        for index in range(len(self._buckets)):
            length = len(self.bucket_keys(index))
            if length > 1:
                collisions += length - 1
        return collisions


def always_zero(key):
    """A deliberately terrible hash used only to force collisions in demos/tests."""
    return 0


if __name__ == "__main__":
    words = ["data", "structures", "course", "outline", "arrays",
             "linked", "lists", "hash", "tables", "heaps"]

    table = HashTable()
    for position, word in enumerate(words):
        table.put(word, position)

    print("DEMO 1: normal table with our default_hash")
    print(f"entries={len(table)}  buckets={table.bucket_count()}  "
          f"load factor={table.load_factor():.3f}  longest chain={table.longest_chain()}  "
          f"collisions={table.collision_count()}")
    for word in words[:4]:
        print(f"  {word:<10} hash={default_hash(word)}  bucket={default_hash(word) % table.bucket_count()}")
    for index in range(table.bucket_count()):
        print(f"  bucket {index:>2}: {table.bucket_keys(index)}")

    print()
    print("DEMO 2: forced collisions (every key goes to bucket 0)")
    bad = HashTable(initial_size=4, hash_function=always_zero)
    for word in ["a", "b", "c"]:
        bad.put(word, word.upper())
    print(f"  bucket 0: {bad.bucket_keys(0)}  (newest key is at the front)")
    print(f"  get('a') = {bad.get('a')}   get('b') = {bad.get('b')}   get('c') = {bad.get('c')}")
    print(f"  longest chain={bad.longest_chain()}  collisions={bad.collision_count()}")