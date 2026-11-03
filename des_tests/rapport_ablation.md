# Rapport d'ablation : Ground Truth (2 pages max)

Yanis Younsi · dépôt YanisYounsi-code/Ground-Truth-un-RAG-qui-ne-ment-pas

> Squelette à compléter avec les chiffres produits par `notebooks/paliers_1_2_colab.ipynb`.
> Chaque `…` renvoie au fichier qui donne la valeur.

## 1. Le pipeline complet

Pour chaque question : recherche BM25 (codé à la main) et dense (bge-m3, cosinus en NumPy) sur des
chunks contextuels, fusion RRF, reranker bge-reranker-v2-m3 sur les 30 meilleurs, porte
d'abstention sur le score du meilleur passage, puis un seul appel au générateur avec 6 passages
au plus (3 000 tokens). L'indexation lit le texte avec PyMuPDF, réécrit les tableaux en Markdown
et passe les 97 pages scannées par Tesseract.

| Système (validation v1, 100 questions) | Score de confiance | Hallucinations | Abstentions |
|---|---|---|---|
| Toujours INTROUVABLE | +0,23 | 0 % | 100 % |
| RAG de base (palier 1 : BM25, chunks naïfs) | … (`runs/val1_rag_base_report.json`) | … | … |
| Pipeline complet sans porte | … (`runs/val1_complet_sansporte_report.json`) | … | … |
| **Pipeline complet avec porte** | … (`runs/val1_complet_report.json`) | … | … |

## 2. Ce que chaque brique apporte à la recherche

Une brique retirée à la fois (`des_tests/ablation_recherche.md`). R@5 = part des questions dont
la page de preuve est dans les 5 premières pages retrouvées.

| Configuration | R@5 | R@10 | MRR | Effet de la brique |
|---|---|---|---|---|
| Complet | … | … | … | référence |
| Sans reranker | … | … | … | … |
| Sans dense (BM25 seul) | … | … | … | … |
| Sans BM25 (dense seul) | … | … | … | … |
| Chunking structure (sans en-tête de contexte) | … | … | … | … |
| Chunking naïf | … | … | … | … |
| Sans OCR | … | … | … | à lire sur les questions scan |
| Sans tableaux Markdown | … | … | … | à lire sur les questions tableau |

Au palier 1, la racinisation légère du tokeniseur a fait passer le R@10 du BM25 sur les pages de
0,636 à 0,727 (`des_tests/journal.md`).

## 3. Parsing : 30 pages annotées

`des_tests/parsing_resultats.md` : part des valeurs retrouvées dans le texte extrait, et part
retrouvée sur la même ligne que son libellé, pour PyMuPDF brut, PyMuPDF + tableaux et Tesseract.

…

## 4. Abstention

Courbe du score de confiance en fonction du seuil (`des_tests/calibration.png`). Seuil retenu : …
(milieu du meilleur plateau, pour limiter le surapprentissage sur 100 questions).

…

## 5. Où le système hallucine encore

D'après `des_tests/echecs.md` et les détails par type des rapports d'évaluation : …

## 6. Les briques qui ne servent à rien

…
