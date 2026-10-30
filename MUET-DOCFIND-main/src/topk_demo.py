"""Demo: how many key comparisons do the heap and the merge sort need?

Run:  python -m src.topk_demo

The numbers are COUNTS of comparisons on made-up, deterministic data, so they are the
same on every machine and every run (unlike timings). They support the explanation of
when a heap beats sorting all candidates: C large, k small.
"""

from src.topk import top_k_heap, top_k_sort


class CountedKey:
    """Wraps a key value and counts every comparison made on it."""
    comparisons = 0

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        CountedKey.comparisons += 1
        return self.value < other.value

    def __le__(self, other):
        CountedKey.comparisons += 1
        return self.value <= other.value

    def __gt__(self, other):
        CountedKey.comparisons += 1
        return self.value > other.value

    def __ge__(self, other):
        CountedKey.comparisons += 1
        return self.value >= other.value


def generated_items(count):
    """Deterministic made-up (score, id) pairs. No randomness."""
    items = []
    state = 12345
    for number in range(1, count + 1):
        state = (state * 1103515245 + 12345) % 2147483648
        items.append({"score": state % 50, "passage_id": f"P{number:05d}"})
    return items


def counted_key(item):
    return CountedKey((-item["score"], item["passage_id"]))


def count_comparisons(count, k):
    """Return (heap comparisons, merge sort comparisons, same answer?) for C = count."""
    items = generated_items(count)

    CountedKey.comparisons = 0
    by_heap = top_k_heap(items, k, counted_key)
    heap_comparisons = CountedKey.comparisons

    CountedKey.comparisons = 0
    by_sort = top_k_sort(items, k, counted_key)
    sort_comparisons = CountedKey.comparisons

    same = [x["passage_id"] for x in by_heap] == [x["passage_id"] for x in by_sort]
    return heap_comparisons, sort_comparisons, same


def main():
    print("Key comparisons needed to find the best k of C generated candidates")
    print(f"{'C':>8} {'k':>4} {'heap':>10} {'merge sort':>12}  same answer?")
    for count in [100, 1000, 10000]:
        for k in [3, 10]:
            heap_comparisons, sort_comparisons, same = count_comparisons(count, k)
            print(f"{count:>8} {k:>4} {heap_comparisons:>10} {sort_comparisons:>12}  {'yes' if same else 'NO'}")


if __name__ == "__main__":
    main()