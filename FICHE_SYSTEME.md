# Fiche système : Ground Truth, un RAG qui ne ment pas

Yanis Younsi · I Lab ECE Paris · novembre 2026 · dépôt `YanisYounsi-code/Ground-Truth-un-RAG-qui-ne-ment-pas`

**Principe.** Répondre seulement quand une page du corpus le prouve, en citant `[doc_id p.N]`, et
sinon dire `INTROUVABLE`. Au barème (+1 juste, −1 faux, 0 abstention), une réponse ne vaut la peine
que si elle est juste plus d'une fois sur deux : le système est construit pour **vérifier avant de
parler**.

## Chaîne de traitement

| Étape | Choix | Pourquoi (mesuré sur la validation v1) |
|---|---|---|
| Lecture | PyMuPDF, tableaux réécrits en Markdown | 85 % des chiffres de tableau restent sur la ligne de leur libellé, contre 0 % sans |
| Scans | Tesseract en français, seulement sur les pages de moins de 50 caractères | scans : R@5 de 0,11 à 0,89 |
| Découpage | par phrases et intertitres (≈ 250 mots), tableaux entiers, en-tête document + date | la date sert aux questions temporelles |
| Recherche | BM25 codé à la main + dense bge-m3, fusion RRF | dense : +5 points de R@5 |
| Reclassement | bge-reranker-v2-m3 sur les 30 meilleurs | MRR de 0,69 à 0,80 |
| Génération | Ministral-3-3B officiel, 1 appel, 6 passages (≈ 3 000 tokens), date de chaque passage | la plus récente fait foi en cas de conflit |
| Vérification | aveux d'incertitude → INTROUVABLE ; chaque chiffre de la réponse doit être dans un extrait (ou être l'écart de deux chiffres ancrés) | +0,14 de score ; hallucinations de 36 % à 22 % |
| Mise à jour | `run.sh update` : lit et encode seulement les nouveaux PDF, BM25 reconstruit | v1 jamais réindexée |

## Résultats

| | Score de confiance | Hallucinations | R@5 |
|---|---|---|---|
| Toujours INTROUVABLE | +0,23 | 0 % | – |
| RAG de base (palier 1) | −0,04 | 46 % | 0,58 |
| **Pipeline final, validation v1** | **+0,38** | **22 %** | **0,91** |
| Pipeline final, validation v2 (40 questions, plancher 0) | +0,125 | 30 % | 0,91 |

Coûts sur un T4 : index v1 en 30 min (limite 2 h), mise à jour v2 sans relire la v1 (limite 20 min),
6 s par question (limite 30 s). Sans la mise à jour, le R@5 de la validation v2 tombe à 0,14. Modèles tous open weights, aucun réseau après `setup.sh`.

## Ce que j'ai appris

- **La recherche n'est plus le problème** (bonne page dans le top 5 neuf fois sur dix) : les erreurs
  restantes sont des erreurs de lecture d'un modèle de 3 milliards de paramètres (mauvaise case de
  tableau, valeur de graphique devinée, liste incomplète).
- **Une porte d'abstention sur le score du reranker ne marche pas** : ce score dit si la bonne page
  est trouvée, pas si le modèle va bien la lire. Je l'ai remplacée par une vérification de la réponse
  elle-même.
- **Les briques inutiles existent** : BM25 n'ajoute que +0,006 de R@5 au dense ; l'en-tête de contexte
  est dans le bruit. Je les ai gardées pour leur coût presque nul, en le disant.

## Limites connues

Graphiques (la valeur n'est pas dans le texte), synthèses longues, questions croisant deux documents ;
règles de vérification mises au point sur 100 questions, contrôlées sur la validation v2.
