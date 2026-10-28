"""Palier 1 : métriques de recherche, au niveau des pages."""

import math


def pertinentes(question):
    """Ensemble des pages (doc_id, page) qui contiennent la preuve."""
    return {(e["doc_id"], e["page"]) for groupe in question["evidence"] for e in groupe}


def recall_at_k(classement, question, k):
    """Part des groupes de preuves (un par document) couverts dans le top-k."""
    top = set(classement[:k])
    groupes = question["evidence"]
    couverts = sum(1 for g in groupes if top & {(e["doc_id"], e["page"]) for e in g})
    return couverts / len(groupes)


def reciprocal_rank(classement, question):
    """1 / rang de la première page pertinente (0 si aucune)."""
    bonnes = pertinentes(question)
    for rang, p in enumerate(classement, start=1):
        if p in bonnes:
            return 1 / rang
    return 0.0


def ndcg_at_10(classement, question):
    """Gain cumulé actualisé : une bonne page rapporte plus si elle est haut placée."""
    bonnes = pertinentes(question)
    dcg = sum(
        1 / math.log2(r + 1)
        for r, p in enumerate(classement[:10], start=1)
        if p in bonnes
    )
    idcg = sum(1 / math.log2(r + 1) for r in range(1, min(len(bonnes), 10) + 1))
    return dcg / idcg if idcg else 0.0
