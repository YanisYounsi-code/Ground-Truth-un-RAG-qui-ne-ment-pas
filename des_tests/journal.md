# Journal d'expériences

Une ligne par essai. Recherche mesurée sur les 77 questions de validation v1 qui ont une réponse
(une question vaut 1,3 point : un écart de 1 ou 2 points peut être du hasard).

| Date | Changement | R@5 | R@10 | MRR | nDCG@10 | Remarque |
|---|---|---|---|---|---|---|
| 28/10 | BM25 maison sur les pages, mots vides | 0,578 | 0,636 | 0,437 | 0,446 | identique à bm25s ; baseline du kit : R@5 0,558 |
| 03/11 | + racinisation légère + nombres recollés | 0,610 | 0,727 | 0,454 | 0,473 | +9 points de R@10 : « pharmacies » rejoint « pharmacie » |
| 10/11 | Pipeline complet (Colab T4) : hybride BM25 + bge-m3, RRF, reranker, chunks contextuels, OCR | 0,909 | 0,948 | 0,799 | 0,787 | index 30 min 22 s ; ablation : `rapport_ablation.md` section 2 |

## Génération (score de confiance, validation v1, 100 questions)

| Date | Changement | Score | Hallucinations | Remarque |
|---|---|---|---|---|
| 10/11 | RAG de base (BM25 pages, sans OCR) | −0,04 | 46 % | « toujours INTROUVABLE » fait +0,23 |
| 10/11 | Pipeline complet, premier prompt | +0,135 | 43 % | « En réalité » mis partout ; la porte sur le reranker ne sépare rien |
| 10/11 | Règle « En réalité » restreinte + non-réponses → INTROUVABLE | +0,24 | 36 % | 10 « les extraits ne mentionnent pas » convertis |
| 10/11 | + vérification des chiffres et des aveux d'incertitude | +0,38 | 22 % | 6,3 s par question ; soumission v1 `2026-11-10_1` |

## Palier 3 (validation v2, 40 questions, toutes avec réponse)

| Date | Changement | R@5 | MRR | Score | Remarque |
|---|---|---|---|---|---|
| 10/11 | Index v1 seul (avant la mise à jour) | 0,138 | 0,263 | – | les preuves sont surtout dans les documents v2 |
| 10/11 | `run.sh index` + `run.sh update` (v1 + v2), pipeline complet | 0,912 | 0,666 | +0,125 | 6,1 s par question ; soumission v2 `2026-11-10_1` |
| 10/11 | Aveux cherchés dans toute la réponse (et plus seulement les 300 premiers caractères) | – | – | – | corrige val2-024 ; v1 inchangée (+0,37) |

