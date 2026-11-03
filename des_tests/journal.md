# Journal d'expériences

Une ligne par essai. Recherche mesurée sur les 77 questions de validation v1 qui ont une réponse
(une question vaut 1,3 point : un écart de 1 ou 2 points peut être du hasard).

| Date | Changement | R@5 | R@10 | MRR | nDCG@10 | Remarque |
|---|---|---|---|---|---|---|
| 28/10 | BM25 maison sur les pages, mots vides | 0,578 | 0,636 | 0,437 | 0,446 | identique à bm25s ; baseline du kit : R@5 0,558 |
| 03/11 | + racinisation légère + nombres recollés | 0,610 | 0,727 | 0,454 | 0,473 | +9 points de R@10 : « pharmacies » rejoint « pharmacie » |
