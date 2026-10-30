# Project Decision Log
**Project:** Fast Document Retrieval Engine for a University RAG Assistant
## 2026-10-23 — Python implementation
**Decision:** Implement the project in Python.
**Reason:** Python was approved for the project despite the brief preferring C++17.
**Impact:** The implementation and automated tests use Python. Keep evidence of the instructor's approval with the submission.
## 2026-10-23 — Custom data structures
**Decision:** Implement the hash table, inverted index, postings lists, and Top-K selection as project components.
**Reason:** The project demonstrates Data Structures and Algorithms rather than relying entirely on built-in indexing and heap libraries.
**Impact:** The code can be inspected and tested against the project requirements.
## 2026-10-23 — Preserve the original test corpus
**Decision:** Keep the original five-passage dataset in `data/passages.json` and use `data/full_corpus.json` for the larger evaluation corpus.
**Reason:** Existing tests depend on the original dataset, while evaluation requires a larger corpus.
**Impact:** The two datasets serve different purposes and should not be confused.
## 2026-10-23 — Expand the synthetic corpus
**Decision:** Generate 150 passages across five categories and 30 distinct document IDs.
**Reason:** The initial corpus had only five distinct document IDs, which did not meet the requirement for at least 20 documents.
**Impact:** The generated corpus now meets the passage, document, and category counts. Its content is synthetic and is not official university policy.
## 2026-10-23 — Compare ranking strategies
**Decision:** Evaluate shared-term count and normalized coverage using both linear scan and inverted-index retrieval.
**Reason:** This allows ranking quality to be compared while keeping the retrieval method as a separate variable.
**Impact:** The current evaluation contains 48 configuration-query rows across 12 queries.
## 2026-10-23 — Record measured evaluation results
**Decision:** Save benchmark and evaluation results as CSV files and document the experiment setup and limitations.
**Reason:** Recorded outputs make the evaluation easier to inspect and reproduce.
**Impact:** Current results are limited to the synthetic dataset and the defined evaluation queries.
## 2026-10-23 — Initialize Git
**Decision:** Track the main implementation, datasets, tests, and reports in Git.
**Reason:** Version control preserves a record of the submitted project state.
**Impact:** Initial commit `a0338e6` contains 29 files. Backup and demo files remain untracked and have not been deleted.
## Follow-up items
- Verify the final submission requirements against the instructor's brief.
- Confirm the command-line interface prints the exact no-evidence message.
- Prepare the final report and presentation.
- Record actual team contributions and test ownership.
- Rerun tests and evaluation before final submission.

## 2026-10-24 — Project cleanup and restructuring
**Decision:** Removed superseded backup copies (older `main_*` versions, `src/ranking_*` copies, `src/topk_wrong_backup.py`, `tests/test_topk_backup.py`, duplicate/backup data files, and the already-applied `patch_official_menu.py`); split `main.py` into `src/config.py`, `src/loader.py`, `src/search.py` and `src/versions.py`; moved the official-data build steps into `scripts/`; added `requirements.txt`; corrected `.gitignore` (it wrongly ignored `src/topk_demo.py`, which a test needs).
**Reason:** Fewer duplicate files and a clearer structure for explanation and evaluation. A verified backup of the previous state was made first.
**Impact:** Console output was compared before and after on 17 commands and was identical; the test suite passes (169 tests).
