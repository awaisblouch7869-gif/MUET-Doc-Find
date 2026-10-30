import csv
import json
import statistics
import time
from pathlib import Path
from src.search import linear_candidates
from src.inverted_index import InvertedIndex
from src.tokenizer import tokenize, unique_tokens

ROOT = Path(__file__).resolve().parent

DATA_FILE = ROOT / "data/full_corpus.json"
OUTPUT_FILE = ROOT / "docs/benchmark_results.csv"
QUERY = "binary search"
REPEATS = 31
SIZES = [25, 50, 100]
def median_microseconds(function):
    """Warm up once, then return median execution time in microseconds."""
    function()
    measurements = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        function()
        elapsed = time.perf_counter() - start
        measurements.append(elapsed * 1_000_000)
    return round(statistics.median(measurements), 3)
def main():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        passages = json.load(file)
    query_words = unique_tokens(tokenize(QUERY))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    print("Benchmark: linear scan vs. inverted index")
    print(f"Query: {QUERY!r}")
    print("Warm-up: 1 run per operation")
    print(f"Measured repetitions: {REPEATS}")
    print("Times are medians in microseconds.")
    print()
    for size in SIZES:
        subset = passages[:size]
        # Measure construction separately from retrieval.
        build_time = median_microseconds(
            lambda: build_index(subset)
        )
        index = build_index(subset)
        # Measure retrieval only; index construction is not included here.
        linear_time = median_microseconds(
            lambda: linear_candidates(subset, query_words)
        )
        index_time = median_microseconds(
            lambda: index.find_candidates(query_words)
        )
        linear_results = linear_candidates(subset, query_words)
        indexed_results = index.find_candidates(query_words)
        linear_ids = sorted(
            item["passage"]["passage_id"] for item in linear_results
        )
        indexed_ids = sorted(
            item["passage"]["passage_id"] for item in indexed_results
        )
        same_candidates = linear_ids == indexed_ids
        row = {
            "passages": size,
            "query": QUERY,
            "repetitions": REPEATS,
            "index_build_median_us": build_time,
            "linear_retrieval_median_us": linear_time,
            "index_retrieval_median_us": index_time,
            "linear_candidates": len(linear_ids),
            "index_candidates": len(indexed_ids),
            "candidate_ids_match": same_candidates,
        }
        rows.append(row)
        print(f"Passages: {size}")
        print(f"  Index build median:     {build_time} us")
        print(f"  Linear retrieval median:{linear_time:>10} us")
        print(f"  Index retrieval median: {index_time} us")
        print(f"  Linear candidates:      {len(linear_ids)}")
        print(f"  Index candidates:       {len(indexed_ids)}")
        print(f"  Candidate IDs match:    {same_candidates}")
        print()
        if not same_candidates:
            raise RuntimeError(
                f"Candidate mismatch for dataset size {size}."
            )
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved measured results to: {OUTPUT_FILE}")
def build_index(passages):
    index = InvertedIndex()
    for passage in passages:
        index.add_passage(passage)
    return index
if __name__ == "__main__":
    main()
