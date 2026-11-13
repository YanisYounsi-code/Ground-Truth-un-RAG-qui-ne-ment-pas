# Fiche système : Ground Truth

Yanis Younsi · novembre 2026 · répond seulement si une page le prouve (`[doc_id p.N]`), sinon `INTROUVABLE`.

| Étape | Choix | Effet mesuré (validation) |
|---|---|---|
| Lecture | PyMuPDF, tableaux réécrits en Markdown | chiffres sur la ligne de leur libellé : 85 % (0 % sans) |
| Scans | Tesseract français, pages de moins de 50 caractères | scans : R@5 de 0,11 à 0,89 |
| Découpage | phrases et intertitres (≈ 250 mots), datés | dans le bruit ; la date sert au temporel |
| Recherche | BM25 maison + dense bge-m3, RRF, reranker bge-reranker-v2-m3 | R@5 0,91 (0,61 au palier 1) |
| Génération | Ministral-3-3B, 1 appel, 6 passages datés, « le plus récent fait foi » | 6 s par question (limite 20 s) |
| Vérification | aveux → INTROUVABLE ; tout chiffre doit être dans un extrait | +0,14 ; hallucinations de 36 % à 22 % |
| Mise à jour | `run.sh update` : seuls les nouveaux PDF sont lus et encodés | sans elle, R@5 v2 = 0,14 |

**Scores** : validation v1 **+0,38** (toujours INTROUVABLE : +0,23) ; v2 **+0,125** (plancher 0). Open weights,
sans réseau après `setup.sh`, index en 30 min sur T4.

## Quand ne pas lui faire confiance

| Type de question | Score | Pourquoi |
|---|---|---|
| Valeur lue sur un graphique | −0,50 (v2) | la valeur n'est pas dans le texte : le modèle devine |
| Croiser deux documents | −0,14 (v2), −0,40 (v1) | un seul des deux documents est souvent utilisé |
| « Le chiffre le plus récent » | 0,00 (v2) | il reprend parfois l'ancienne édition |
| Tableau dense (moyenne / médiane voisines) | 7 des 22 erreurs v1 | la vérification ne voit rien : le chiffre est dans l'extrait |

**Fiable** : texte (+0,54 en v1), synthèses (+0,67 en v2), pièges (+0,83 en v1). **Limites** : règles mises au
point sur 100 questions ; une réponse juste est refusée si elle contient un calcul autre qu'un écart.
