# Evaluation Report — Fast Document Retrieval Engine
**Project:** CS-251 DSA PBL  
**Evaluation dataset:** 150 synthetic passages  
**Evaluation queries:** 12 (10 answerable, 2 unanswerable)  
**Evaluation date:** 23 October 2026
## 1. Objective
Evaluate the retrieval engine using Recall@3, compare two retrieval methods and two ranking strategies, and check behavior for queries with no relevant evidence.
## 2. Experimental setup
- Retrieval methods: linear scan and custom inverted index.
- Ranking strategies: shared-term count and normalized coverage.
- Maximum returned results: 3.
- Relevance labels: predefined in `data/evaluation_queries.json`.
- Results: `docs/evaluation_results.csv`.
- Dataset: synthetic examples created for this project, not official university policy.
Both retrieval methods use the same ranking implementation. The evaluation uses the same query set and relevance labels for every configuration.
## 3. Results
| Retrieval method | Ranking strategy | Mean Recall@3 |
|---|---|---:|
| Linear scan | Shared-term count | 0.900 |
| Inverted index | Shared-term count | 0.900 |
| Linear scan | Normalized coverage | 1.000 |
| Inverted index | Normalized coverage | 1.000 |
Mean Recall@3 is calculated over the 10 answerable queries by averaging each query's recall. Unanswerable queries are excluded because they have no relevant passage IDs.
## 4. Unanswerable-query checks
Both unanswerable queries returned zero results in all four configurations:
| Retrieval method | Ranking strategy | Empty-result checks |
|---|---|---:|
| Linear scan | Shared-term count | 2/2 |
| Linear scan | Normalized coverage | 2/2 |
| Inverted index | Shared-term count | 2/2 |
| Inverted index | Normalized coverage | 2/2 |
The required message is `No supported evidence found`. The evaluation verifies empty result lists; it does not independently verify that the command-line interface displays the exact message for every empty query.
## 5. Analysis
Both retrieval methods achieved identical Recall@3 under each ranking strategy. This is consistent with the design in which both methods share the same ranking code.
Normalized coverage achieved a mean Recall@3 of 1.000 on this query set, compared with 0.900 for shared-term count.
The query `information retrieval` (Q10) explains the difference. With shared-term count, both methods returned P001, P002, and P003 in the top three, missing the relevant passage P149. Many synthetic passages contain generic retrieval-related wording, and equal scores are resolved by passage ID. With normalized coverage, P149 ranked first.
This is evidence that ranking strategy affects results on this dataset; it is not proof that normalized coverage is universally superior.
## 6. Limitations
1. The corpus is synthetic and does not represent official university documents.
2. The evaluation contains only 10 answerable and 2 unanswerable queries.
3. Repeated generic wording may create ties and influence ranking.
4. Relevance labels are manually defined and should be reviewed for semantic correctness.
5. These recall results do not measure answer generation, factual correctness of generated answers, or real-world RAG performance.
## 7. Reproducibility
From the project root, run:
```powershell
python .\evaluate.py
python -m unittest discover -s tests
```
The evaluation script recreates `docs/evaluation_results.csv`. The test suite previously passed all 154 tests.
## 8. Conclusion
On the current synthetic evaluation set, normalized coverage achieved higher Recall@3 than shared-term count. Linear scan and inverted-index retrieval produced matching recall results under both ranking strategies. Further evaluation with a larger, more varied, independently reviewed dataset is needed before making broader claims.
