import csv
import json
from pathlib import Path
from src.config import FULL_DATA_FILE, NO_EVIDENCE_MESSAGE
from src.search import STRATEGIES, run_search
from src.tokenizer import tokenize, unique_tokens

ROOT = Path(__file__).resolve().parent

QUERY_FILE = ROOT / "data/evaluation_queries.json"
OUTPUT_FILE = ROOT / "docs/evaluation_results.csv"
TOP_K = 3
METHODS = ["linear", "index"]
def main():
    with QUERY_FILE.open("r", encoding="utf-8-sig") as file:
        queries = json.load(file)
    with Path(FULL_DATA_FILE).open("r", encoding="utf-8-sig") as file:
        passages = json.load(file)
    available_ids = {p["passage_id"] for p in passages}
    for item in queries:
        unknown_ids = set(item["relevant_passage_ids"]) - available_ids
        if unknown_ids:
            raise ValueError(
                f'{item["query_id"]} contains unknown IDs: {sorted(unknown_ids)}'
            )
        if item["answerable"] != bool(item["relevant_passage_ids"]):
            raise ValueError(
                f'{item["query_id"]}: answerable label conflicts with relevance IDs'
            )
    rows = []
    for item in queries:
        words = unique_tokens(tokenize(item["query"]))
        relevant = set(item["relevant_passage_ids"])
        for method in METHODS:
            for strategy in STRATEGIES:
                results = run_search(
                    method,
                    passages,
                    words,
                    max_results=TOP_K,
                    strategy=strategy,
                )
                retrieved = [
                    result["passage"]["passage_id"] for result in results
                ]
                hits = len(set(retrieved) & relevant)
                if item["answerable"]:
                    recall = hits / len(relevant)
                    no_evidence_correct = ""
                else:
                    recall = ""
                    no_evidence_correct = len(results) == 0
                rows.append({
                    "query_id": item["query_id"],
                    "query": item["query"],
                    "method": method,
                    "strategy": strategy.name,
                    "answerable": item["answerable"],
                    "relevant_ids": ";".join(sorted(relevant)),
                    "top3_ids": ";".join(retrieved),
                    "relevant_hits_at_3": hits,
                    "recall_at_3": recall,
                    "no_evidence_correct": no_evidence_correct,
                })
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("Evaluation complete.")
    print("Queries:", len(queries))
    print("Methods:", ", ".join(METHODS))
    print("Ranking strategies:", ", ".join(s.name for s in STRATEGIES))
    print("Top K:", TOP_K)
    print("Evaluation rows:", len(rows))
    print("Results saved to:", OUTPUT_FILE)
    print("\nMean Recall@3 for answerable queries:")
    for method in METHODS:
        for strategy in STRATEGIES:
            subset = [
                row for row in rows
                if row["method"] == method
                and row["strategy"] == strategy.name
                and row["answerable"]
            ]
            mean_recall = sum(row["recall_at_3"] for row in subset) / len(subset)
            print(f"  {method} | {strategy.name}: {mean_recall:.3f}")
    print("\nUnanswerable-query checks:")
    for method in METHODS:
        for strategy in STRATEGIES:
            subset = [
                row for row in rows
                if row["method"] == method
                and row["strategy"] == strategy.name
                and not row["answerable"]
            ]
            passed = sum(row["no_evidence_correct"] for row in subset)
            print(f"  {method} | {strategy.name}: {passed}/{len(subset)}")
    print("\nRequired no-evidence message:", NO_EVIDENCE_MESSAGE)
    print("Note: no-evidence checks measure empty results; CLI message display is separate.")
if __name__ == "__main__":
    main()
