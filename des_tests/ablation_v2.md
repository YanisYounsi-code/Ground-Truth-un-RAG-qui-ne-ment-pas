# Ablation de la recherche

40 questions de validation avec réponse (data/validation_v2.json). Pages de preuve cherchées dans les pages des passages classés.

| Configuration | R@5 | R@10 | MRR | nDCG@10 | R@5 graphique | R@5 multi-doc | R@5 synthese | R@5 tableau | R@5 temporel | R@5 texte |
|---|---|---|---|---|---|---|---|---|---|---|
| complet | 0.912 | 0.963 | 0.666 | 0.695 | 1.00 | 0.86 | 1.00 | 1.00 | 0.88 | 0.88 |
| sans_reranker | 0.750 | 0.887 | 0.590 | 0.599 | 0.75 | 0.86 | 1.00 | 0.67 | 0.67 | 0.75 |
| sans_dense | 0.688 | 0.762 | 0.552 | 0.547 | 1.00 | 0.79 | 1.00 | 0.50 | 0.50 | 0.75 |
| sans_bm25 | 0.925 | 0.975 | 0.660 | 0.707 | 1.00 | 0.86 | 1.00 | 0.83 | 1.00 | 0.88 |
| index_v1_seul | 0.138 | 0.138 | 0.263 | 0.156 | 0.00 | 0.50 | 0.17 | 0.00 | 0.12 | 0.00 |
