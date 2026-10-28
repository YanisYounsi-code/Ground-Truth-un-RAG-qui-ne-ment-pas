"""Palier 1 : évalue le BM25 maison sur les questions de validation qui ont une réponse."""

import json

from scratch.bm25 import BM25
from scratch.metrics import ndcg_at_10, recall_at_k, reciprocal_rank
from scratch.tokenizer import tokenize

pages = json.load(open("index/scratch/pages.json", encoding="utf-8"))
questions = json.load(open("data/validation_v1.json", encoding="utf-8"))
questions = questions["questions"] if isinstance(questions, dict) else questions

moteur = BM25()
moteur.index([tokenize(p["text"]) for p in pages])

res = {"R@5": [], "R@10": [], "MRR": [], "nDCG@10": []}
for q in questions:
    if not q["answerable"]:
        continue
    top = moteur.search(tokenize(q["question"]), k=10)
    classement = [(pages[i]["doc_id"], pages[i]["page"]) for i, _ in top]
    res["R@5"].append(recall_at_k(classement, q, 5))
    res["R@10"].append(recall_at_k(classement, q, 10))
    res["MRR"].append(reciprocal_rank(classement, q))
    res["nDCG@10"].append(ndcg_at_10(classement, q))

for nom, valeurs in res.items():
    print(f"{nom:8s} {sum(valeurs) / len(valeurs):.3f}")
print(len(res["R@5"]), "questions avec réponse")
