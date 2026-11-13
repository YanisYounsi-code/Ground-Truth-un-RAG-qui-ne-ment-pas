# Rapport d'ablation : Ground Truth

Yanis Younsi · détails complets : `des_tests/ablation_details.md` · rapports : `des_tests/rapports/`

**Pipeline.** PyMuPDF + tableaux en Markdown, OCR Tesseract des pages vides, chunks par phrases et
intertitres datés, BM25 maison + dense bge-m3 (RRF), reranker sur les 30 premiers, un appel à Ministral-3-3B
(6 passages, ≈ 3 000 tokens), vérification de la réponse. T4 : index en 30 min, 6 s par question.

## 1. Score de confiance (validation v1, 100 questions)

| Système | Score | Hallucinations |
|---|---|---|
| Toujours INTROUVABLE | +0,23 | 0 % |
| RAG de base du palier 1 (BM25 sur les pages, sans OCR) | −0,04 | 46 % |
| Pipeline complet, premier prompt | +0,135 | 43 % |
| + règle « En réalité » restreinte, non-réponses → INTROUVABLE | +0,24 | 36 % |
| **+ vérification de la réponse (pipeline final)** | **+0,38** | **22 %** |

Validation v2 (40 questions, toutes avec réponse, donc plancher 0) : **+0,125**, R@5 0,91.

## 2. Une brique retirée à la fois (recherche, 77 questions v1 avec réponse)

| Configuration | R@5 | MRR | Effet |
|---|---|---|---|
| **Complet** | **0,909** | **0,799** | référence |
| Sans OCR | 0,799 | 0,709 | **−11 pts** ; questions scan : R@5 de 0,89 à 0,11 |
| Sans reranker | 0,857 | 0,686 | −5 pts de R@5, **−11 pts de MRR** |
| Sans dense (BM25 seul) | 0,857 | 0,747 | −5 pts (−22 pts sur la v2, plus reformulée) |
| Sans BM25 (dense seul) | 0,903 | 0,794 | −0,6 pt : **dans le bruit** |
| Chunking structure, sans en-tête | 0,935 | 0,781 | dans le bruit (naïf : 0,929 ; sans tableaux Markdown : 0,909) |
| Index v1 seul, questions v2 | 0,138 | 0,263 | la mise à jour v2 est indispensable |

Une question vaut 1,3 point de R@5 : un écart d'une ou deux questions n'est pas significatif. **Ne servent
à rien ou presque** : BM25 en plus du dense et l'en-tête de contexte, gardés pour leur coût presque nul ;
la porte sur le score, retirée (section 4). **Comptent le plus** : l'OCR, le reranker, le dense et la vérification.

## 3. Parsing (30 pages difficiles sélectionnées ; 42 valeurs annotées avec leur libellé)

| Parseur | Tableau : valeur / sur la ligne de son libellé | Graphique | Scan |
|---|---|---|---|
| PyMuPDF brut | 100 % / 0 % | 43 % / 0 % | 0 % / 0 % |
| **PyMuPDF + tableaux Markdown** | 100 % / **85 %** | 43 % / 0 % | 0 % / 0 % |
| Tesseract | 80 % / 40 % | 0 % / 0 % | **100 %** / 53 % |

Le Markdown ne change pas la recherche mais garde chaque chiffre à côté de son libellé, ce qui permet au
générateur de lire la bonne ligne. L'OCR n'est appliqué qu'aux pages vides : ailleurs il est moins bon et
20 fois plus lent. Les graphiques restent un angle mort.

## 4. Abstention : ce qui n'a pas marché, ce qui a marché

**Porte sur le score du reranker (calibrée, abandonnée).** La courbe (`des_tests/calibration.png`) monte
jusqu'au seuil qui refuse presque tout : le score dit si la bonne page est trouvée (9 fois sur 10), pas si
le modèle va bien la lire. Sur le pipeline final, un seuil vers 0,96 gagnerait 3 questions, mais dans une
zone où la courbe oscille de ±3 questions : seuil non retenu tant que la validation v2 ne le confirme pas.

**Vérification de la réponse (+0,14), sans appel supplémentaire au modèle :**
1. un aveu d'incertitude (« les extraits ne mentionnent pas », « pas explicitement », en français ou en
   anglais) devient INTROUVABLE ;
2. chaque nombre de la réponse doit figurer dans un extrait ou dans la question (mêmes règles d'arrondi que
   la notation officielle), ou être l'écart de deux nombres ancrés de la réponse (révisions du palier 3).
   Sinon il a été inventé ou mal calculé : INTROUVABLE. Coût : 2 réponses justes perdues sur 39.

## 5. Où le système hallucine encore

22 réponses à −1 sur 100 (v1), presque toujours avec la bonne page dans le contexte : ce sont des
erreurs de lecture. 7 mauvaises cases de tableau (la moyenne 1 043 au lieu de la médiane 1 514, sur la
même ligne : la vérification ne peut rien, le chiffre est bien dans l'extrait), 4 réponses partielles,
4 valeurs de graphique devinées, 3 synthèses incomplètes, 2 multi-doc n'utilisant qu'un document,
2 pièges non détectés.

Sur la v2, s'ajoutent les éditions périmées : le modèle prend parfois le chiffre de l'édition v1 alors que
la v2, plus récente, est dans le contexte (temporel : 0,00 sur 12 questions).
