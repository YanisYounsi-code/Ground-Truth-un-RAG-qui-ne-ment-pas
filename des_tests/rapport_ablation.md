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

Une brique retirée à la fois, sur les 77 questions de validation v1 qui ont une réponse
(`des_tests/ablation_recherche.md`, Colab T4, 10/11). R@5 = part des groupes de preuve dont une page
est dans les 5 premières pages retrouvées. Une question de plus ou de moins = environ 0,013 de R@5.

| Configuration | R@5 | R@10 | MRR | R@5 scan | R@5 multi-doc | Effet de la brique |
|---|---|---|---|---|---|---|
| **Complet** (hybride + reranker, chunks contextuels) | **0,909** | 0,948 | **0,799** | 0,89 | 0,60 | référence |
| Sans reranker | 0,857 | 0,935 | 0,686 | 0,89 | 0,80 | reranker : +5 pts de R@5, **+11 pts de MRR** |
| Sans dense (BM25 seul) | 0,857 | 0,903 | 0,747 | 0,89 | 0,60 | dense : +5 pts de R@5, surtout sur les tableaux (0,76 → 0,88) |
| Sans BM25 (dense seul) | 0,903 | 0,948 | 0,794 | 0,89 | 0,70 | BM25 : +0,6 pt seulement, dans le bruit |
| Chunking structure (sans en-tête) | 0,935 | 0,961 | 0,781 | 0,89 | 0,60 | l'en-tête ne gagne rien en R@5 (−2 questions), +2 pts de MRR |
| Chunking naïf (250 mots) | 0,929 | 0,961 | 0,761 | 0,89 | 0,70 | le découpage compte peu pour la recherche |
| Sans OCR | 0,799 | 0,818 | 0,709 | **0,11** | 0,70 | **OCR : +11 pts de R@5, scans de 0,11 à 0,89** |
| Sans tableaux Markdown | 0,909 | 0,948 | 0,798 | 0,89 | 0,60 | aucun effet sur la recherche |

Pour comparaison, le BM25 du palier 1 sur des pages entières faisait R@5 = 0,610 et MRR = 0,454.

Ce que j'en retiens :

- **L'OCR est la brique la plus rentable** : sans elle, 8 questions sur 9 portant sur un scan sont
  perdues d'avance, car leur page est vide dans l'index.
- **Le reranker sert surtout à bien classer** : il change peu le R@10, mais fait monter la bonne page
  en tête (MRR 0,686 → 0,799). C'est ce qui compte, puisque seuls 6 passages entrent dans le prompt.
- **La recherche dense fait le gros du travail** et BM25 n'ajoute presque rien en moyenne. Je le
  garde quand même : il coûte quelques secondes et il est fiable sur les noms propres et les
  chiffres exacts.
- **Les écarts entre découpages (2 questions sur 77) sont dans le bruit.** Je garde les chunks
  contextuels, pour leur meilleur MRR et parce que le seuil a été calibré avec eux ; je revérifierai
  sur la validation v2.
- **Les tableaux en Markdown n'aident pas à retrouver la page** : leur effet est à mesurer sur la
  génération (lecture des chiffres sur la bonne ligne, section 3).
- **Le point faible est le multi-doc** (R@5 = 0,60) : il faut retrouver deux documents à la fois et
  les 5 premières places sont souvent prises par le même. Sans reranker, ce score monte à 0,80 :
  probablement parce que le reranker fait remonter plusieurs passages du document le plus pertinent.
  Piste : garder au moins un passage de chaque document dans le top 5. Ce sont peu de questions
  (une de plus = +0,10), donc à confirmer sur la validation v2.

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
