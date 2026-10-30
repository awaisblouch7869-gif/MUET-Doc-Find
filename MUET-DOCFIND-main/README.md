# DOCFIND — Fast Document Retrieval Engine for a University RAG Assistant

DOCFIND is a console application (Python, standard library only for the core) that finds the passages most relevant to a user's query. It is the retrieval component of a university Retrieval-Augmented Generation (RAG) assistant, built for a Data Structures and Algorithms (DSA) project.

**Data note:** `data/passages.json` (5 passages) and `data/full_corpus.json` (150 passages, 30 document IDs, 5 categories) are **synthetic** demonstration data, not university policy. `data/muet_official_passages_compatible.json` (8 passages) is taken from official MUET documents (2025-26 prospectus and academic calendar).

## Features
- Custom hash table, postings lists and inverted index (all written for this project).
- Two retrieval methods: linear scan (baseline) and inverted index.
- Two ranking strategies compared on the same candidates: shared-term count and normalized coverage.
- Top-K selection with our own bounded heap or merge sort (no library heap or sort in `src/topk.py`).
- Deterministic tie-breaking (smaller `passage_id` first).
- Outdated-version flag (`OUTDATED` / `CURRENT`).
- Exact no-evidence message: `No supported evidence found`.

## Project structure
```text
dsa_retrieval_engine/
├── main.py                  console application (menu and command line)
├── generate_dataset.py      builds data/full_corpus.json (synthetic)
├── evaluate.py              12 labelled queries -> docs/evaluation_results.csv
├── benchmark.py             linear vs indexed timing -> docs/benchmark_results.csv
├── requirements.txt
├── src/
│   ├── config.py            data-file paths and search constants
│   ├── loader.py            load and validate passages (JSON)
│   ├── tokenizer.py         text -> lower-case word tokens
│   ├── hash_table.py        custom hash table
│   ├── postings.py          postings list (stored in the hash table)
│   ├── inverted_index.py    inverted index built on the two above
│   ├── search.py            linear scan, indexed search, run_search
│   ├── ranking.py           the two ranking strategies and rank_candidates
│   ├── topk.py              custom max-heap, merge sort, Top-K selection
│   ├── topk_demo.py         comparison-count demo (also used by a test)
│   └── versions.py          outdated-version detection
├── scripts/                 one-off steps that rebuild the official MUET data from PDFs
├── data/                    passages, corpus, evaluation queries, source PDFs
├── tests/                   unittest suite
└── docs/                    evaluation and benchmark reports, decision log
```

## Setup (Windows PowerShell)
Python 3.10 or newer is required (the project was developed with Python 3.14).

```powershell
cd "path\to\PBL DSA\dsa_retrieval_engine"     # the folder that contains main.py
python -m venv .venv                           # optional
.\.venv\Scripts\Activate.ps1                   # optional
python -m pip install -r requirements.txt
```
`colorama` only adds colours; the program also runs without it. `pypdf` is only needed for the `scripts/` folder.

## Run
```powershell
python main.py                                         # interactive menu
python main.py --full --index "binary search"          # inverted index, synthetic corpus
python main.py --full --linear "binary search"         # linear scan
python main.py --full --compare "binary search"        # compare both ranking strategies
python main.py --official --index "attendance semester"  # official MUET passages
python main.py --show                                  # list the 5 sample passages
```
Options: `--show --index --linear --compare --full --official`. Without `--full` or `--official`, the 5-passage sample set is used.

## Test, evaluate, benchmark
```powershell
python -m unittest discover -s tests      # run from the project folder
python generate_dataset.py                # rebuilds data/full_corpus.json
python evaluate.py                        # rewrites docs/evaluation_results.csv
python benchmark.py                       # rewrites docs/benchmark_results.csv (timings vary by machine)
```
Rebuilding the official MUET data (needs `pypdf`): `python scripts/extract_muet_pdf.py`, `python scripts/build_muet_passages.py`, `python scripts/build_calendar_passages.py`, `python scripts/prepare_official_dataset.py`. `data/muet_official_passages.json` is the prospectus passages followed by the calendar passages; no script merges them, so that step was done by hand.

## Ranking strategies
- **Shared-term count:** number of unique query words found in the passage.
- **Normalized coverage:** matched query words divided by the number of unique words in the passage title and text, which favours focused passages.

Both receive the same candidate set, so differences come only from the scoring rule.

## DSA concepts used
Hash table with separate chaining, inverted index, postings lists, binary-heap Top-K selection (O(C log k)), merge sort (O(C log C)), linear scan (O(N·L)), deterministic tie-breaking.

## Results (from the project's own documents)
- Evaluation: 12 labelled queries (10 answerable, 2 unanswerable). Mean Recall@3: shared-term count 0.900, normalized coverage 1.000 (both retrieval methods). Unanswerable-query checks: 2/2 in every configuration. Details: `docs/evaluation_report.md`.
- Benchmark (original run, the student's laptop; query `binary search`, 31 repetitions, median):

| Passages | Index build (µs) | Linear retrieval (µs) | Indexed retrieval (µs) |
|---:|---:|---:|---:|
| 25 | 2248.1 | 840.2 | 22.2 |
| 50 | 8136.6 | 1927.6 | 22.2 |
| 100 | 14042.0 | 3420.7 | 24.5 |

These cover candidate retrieval only and are specific to that machine. Details: `docs/benchmark_report.md`.

## Test status
After the cleanup and refactoring: `python -m unittest discover -s tests` ran 169 tests, all OK (Python 3.12 test environment; not run on Python 3.14 during the cleanup).

## Known limitations
- Keyword matching only; it does not understand meaning.
- Ranking scores are heuristic.
- The synthetic corpus is not official university material; evaluation and benchmark results apply only to that corpus and those queries.
- Tests load data with paths relative to the project folder, so run the test command from there.

## Academic integrity
Do not present synthetic passages as official rules. Report benchmark numbers only after running the documented experiment, and record team contributions according to the work each member actually did.
