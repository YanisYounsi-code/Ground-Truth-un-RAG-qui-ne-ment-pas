# Palier 1 : BM25 seul, dense seul, hybride

Index du palier 1 : chunks naïfs (250 mots, 50 de recouvrement), sans OCR, sans reranker.
77 questions de validation v1 avec réponse ; pages de preuve cherchées dans les pages des passages classés.
Mesure faite le 13/11 sur Colab (processeur), avec `pipeline.ablation` sur l'index `palier1`.

| Configuration | R@5 | R@10 | MRR | nDCG@10 | R@5 graphique | R@5 multi-doc | R@5 scan | R@5 synthèse | R@5 tableau | R@5 texte |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 seul (scratch/bm25.py) | 0,584 | 0,708 | 0,496 | 0,484 | 0,83 | 0,40 | 0,11 | 0,62 | 0,59 | 0,65 |
| Dense seul (bge-m3, scratch/dense.py) | 0,669 | 0,773 | 0,568 | 0,559 | 0,83 | 0,50 | 0,11 | 0,62 | 0,71 | 0,81 |
| Hybride (RRF) | 0,675 | 0,792 | 0,567 | 0,554 | 0,83 | 0,80 | 0,11 | 0,62 | 0,71 | 0,77 |

- **Le dense bat BM25** de 8,5 points de R@5, surtout sur le texte (0,81 contre 0,65) et les tableaux :
  les questions n'emploient pas les mots des documents (« longévité » / « espérance de vie »).
- **L'hybride gagne peu en moyenne, mais beaucoup sur le multi-doc** (0,80 contre 0,40 et 0,50) : les
  deux recherches trouvent chacune un des deux documents.
- **Les scans restent à 0,11** quelle que soit la recherche : sans OCR, leur page est vide. C'est ce qui a
  motivé l'OCR du palier 2.
- RAG de base associé (BM25 sur les pages, 5 pages au générateur) : score de confiance −0,04
  (`des_tests/rapports/val1_rag_base_report.json`) ; 5 échecs commentés : `des_tests/echecs_commentes.md`.
