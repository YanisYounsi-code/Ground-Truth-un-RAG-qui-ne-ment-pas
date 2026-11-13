# Questions d'entraînement pour la démo live (réponses attendues)

À lancer avec : `python -m pipeline.demo --index-dir /tmp/index --fichier questions_demo.txt`
Questions écrites à partir du corpus, distinctes des questions de validation, de classement et de red team.

| # | Type | Réponse attendue | Preuve |
|---|---|---|---|
| 1 | scan | 36,4 équipements pour 10 000 habitants | insee-ip2041 p.2 |
| 2 | tableau | 765 euros par mois | insee-ip2067 p.2 (figure 3) |
| 3 | note de graphique | 28 % | insee-ip2061 p.3 |
| 4 | piège | INTROUVABLE (le corpus ne parle pas du chômage allemand) | – |
| 5 | anglais | 6 570 heures (plus des trois quarts de l'année) | cc-effacements-electricite p.38 |

Pour la vraie démo, le jury pose ses propres questions : l'important est d'expliquer ce que le script
affiche (sources, passages, et pourquoi le système s'abstient quand il le fait).
