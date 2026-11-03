"""Recherche : BM25 (palier 1) + dense (palier 1), fusion RRF, puis reranker.

Pour chaque question, on garde les meilleurs passages avec leur score. Cette étape tourne dans
son propre processus, avant la génération : l'embedder et le reranker sont ainsi libérés de la
mémoire du GPU avant le chargement du générateur (7,7 Go au repos, 13 Go en pic sur 16 Go).
"""
import json
import time
from collections import defaultdict
from pathlib import Path

from scratch.bm25 import BM25
from scratch.dense import Encodeur, recherche
from scratch.tokenizer import tokenize

from . import settings
from .index import charger

GARDES = 12  # passages conservés par question pour construire le contexte


def rrf(classements, k=60):
    """Reciprocal Rank Fusion : chaque liste donne 1 / (k + rang) à ses éléments, on additionne.

    Fusionne des scores d'échelles différentes (BM25, cosinus) en ne regardant que les rangs.
    """
    scores = defaultdict(float)
    for classement in classements:
        for rang, (i, _) in enumerate(classement, start=1):
            scores[i] += 1 / (k + rang)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


class Chercheur:
    def __init__(self, index_dir, mode="hybrid", rerank=True):
        self.reglages = settings.load()
        self.pages, self.chunks, self.embeddings = charger(index_dir)
        self.mode = mode
        self.bm25 = None
        if mode in ("bm25", "hybrid"):
            self.bm25 = BM25()
            self.bm25.index([tokenize(c.get("index_text", c["text"])) for c in self.chunks])
        self.encodeur = Encodeur(self.reglages["embed_model"]) if mode in ("dense", "hybrid") else None
        self.reranker = None
        if rerank:
            from .rerank import Reranker

            self.reranker = Reranker(self.reglages["rerank_model"])

    def candidats(self, question):
        r = self.reglages
        listes = []
        if self.bm25 is not None:
            listes.append(self.bm25.search(tokenize(question), k=r["bm25_k"]))
        if self.encodeur is not None:
            vecteur = self.encodeur.encode([question])[0]
            listes.append(recherche(self.embeddings, vecteur, k=r["dense_k"]))
        if len(listes) == 1:
            return listes[0]
        return rrf(listes, k=r["rrf_k"])

    def chercher(self, question):
        """Liste triée de passages {chunk_id, doc_id, page, date, text, score}."""
        classement = self.candidats(question)[: self.reglages["rerank_k"]]
        passages = [dict(self.chunks[i], score=float(s)) for i, s in classement]
        if self.reranker is not None and passages:
            notes = self.reranker.scores(question, [p.get("index_text", p["text"]) for p in passages])
            for p, note in zip(passages, notes):
                p["score"] = float(note)
            passages.sort(key=lambda p: p["score"], reverse=True)
        return passages


def pages_classees(passages):
    """Pages distinctes dans l'ordre des passages : le champ `retrieved` des prédictions."""
    vues, pages = set(), []
    for p in passages:
        cle = (p["doc_id"], p["page"])
        if cle not in vues:
            vues.add(cle)
            pages.append({"doc_id": p["doc_id"], "page": p["page"]})
    return pages


def retrieve_all(index_dir, questions_path, out_path, mode="hybrid", rerank=True):
    from groundtruth.io import load_questions

    t0 = time.time()
    chercheur = Chercheur(index_dir, mode=mode, rerank=rerank)
    resultats = {}
    for q in load_questions(questions_path):
        passages = chercheur.chercher(q["question"])
        resultats[q["qid"]] = {
            "passages": passages[:GARDES],
            "retrieved": pages_classees(passages),
            "top_score": passages[0]["score"] if passages and rerank else None,
        }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(resultats, ensure_ascii=False), encoding="utf-8")
    print(f"[retrieve] {len(resultats)} questions en {time.time() - t0:.0f} s (mode {mode}, "
          f"reranker {'oui' if rerank else 'non'})")
