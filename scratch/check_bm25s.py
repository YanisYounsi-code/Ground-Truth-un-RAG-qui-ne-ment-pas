"""Palier 1 : vérifie que le BM25 maison donne les mêmes scores que la librairie bm25s."""

import json
import os

os.environ.setdefault(
    "JAX_PLATFORMS", "cpu"
)  # bm25s peut importer JAX, qui réserve le GPU
import bm25s
import numpy as np

from scratch.bm25 import BM25
from scratch.tokenizer import tokenize

pages = json.load(open("index/scratch/pages.json", encoding="utf-8"))
questions = json.load(open("data/validation_v1.json", encoding="utf-8"))
questions = questions["questions"] if isinstance(questions, dict) else questions
corpus = [tokenize(p["text"]) for p in pages]

maison = BM25(k1=1.5, b=0.75)
maison.index(corpus)
reference = bm25s.BM25(k1=1.5, b=0.75, method="lucene")
reference.index(corpus, show_progress=False)

ecart_max, memes_top10 = 0.0, 0
for q in questions:
    toks = tokenize(q["question"])
    s_maison = maison.scores(toks)
    vecteur = np.zeros(len(pages))
    for i, s in s_maison.items():
        vecteur[i] = s
    s_ref = reference.get_scores(toks)
    ecart_max = max(ecart_max, float(np.abs(vecteur - s_ref).max()))
    memes_top10 += set(np.argsort(-vecteur)[:10]) == set(np.argsort(-s_ref)[:10])

print(f"Écart maximal entre les scores : {ecart_max:.2e}")
print(f"Top-10 identique pour {memes_top10} questions sur {len(questions)}")
