# Benchmark Results
## Experiment Setup
- Dataset: generated synthetic corpus.
- Dataset sizes tested: 25, 50, and 100 passages.
- Query: `binary search`.
- Warm-up: one run per operation.
- Measured repetitions: 31.
- Statistic reported: median execution time.
- Timer: Python `time.perf_counter()`.
- Index construction was measured separately from retrieval.
- These measurements were collected on the student's laptop.
## Results

| Passages | Index build (µs) | Linear retrieval (µs) | Indexed retrieval (µs) | Candidate counts equal? |
|---:|---:|---:|---:|:---:|
| 25 | 2248.1 | 840.2 | 22.2 | Yes |
| 50 | 8136.6 | 1927.6 | 22.2 | Yes |
| 100 | 14042.0 | 3420.7 | 24.5 | Yes |
## Observations
1. Both retrieval methods returned the same candidate IDs for the tested query at all three dataset sizes.
2. Indexed retrieval was faster than linear retrieval in these measurements.
3. Index construction time increased with the dataset size in this experiment.
4. Indexed retrieval time did not increase consistently with dataset size. This may reflect timing noise and the small experiment.
5. The query returned five candidates at every tested size.
## Limitations
This experiment measures candidate retrieval, not complete end-to-end search or ranking. It uses one query and one synthetic corpus, so it does not establish general performance across all queries or real university documents.
The results are specific to the machine, Python environment, dataset, and implementation used. Repeat experiments with multiple representative queries before drawing broader conclusions.
The index-build cost must be considered when evaluating workloads with few searches. This report does not claim that indexed retrieval is always faster overall.
## Reproducibility
Run the following command from the project root:
```powershell
python .\benchmark.py
```
The script writes raw measurements to `docs/benchmark_results.csv`. Run the unit tests separately:
```powershell
python -m unittest discover -s tests
```
