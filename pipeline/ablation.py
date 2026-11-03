"""Palier 2 : ablation de la recherche (sans générateur, donc rapide).

Pour chaque configuration (index, mode de recherche, reranker oui ou non), mesure sur la
validation la part des questions dont la page de preuve est retrouvée, par type de question.

    python -m pipeline.ablation --config complet=index/contextual:hybrid:rerank \
                                --config sans_reranker=index/contextual:hybrid:norerank ...
Résultat : des_tests/ablation_recherche.md (+ affichage).
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from groundtruth.io import load_questions
from scratch.metrics import ndcg_at_10, recall_at_k, reciprocal_rank

from .retrieve import Chercheur, pages_classees


def mesurer(index_dir, mode, rerank, questions):
    chercheur = Chercheur(index_dir, mode=mode, rerank=rerank)
    par_type = defaultdict(list)
    for q in questions:
        classement = [(p["doc_id"], p["page"]) for p in pages_classees(chercheur.chercher(q["question"]))]
        m = (recall_at_k(classement, q, 5), recall_at_k(classement, q, 10),
             reciprocal_rank(classement, q), ndcg_at_10(classement, q))
        par_type[q["type"]].append(m)
        par_type["total"].append(m)
    del chercheur
    try:
        import torch

        torch.cuda.empty_cache()
    except Exception:  # noqa: BLE001
        pass
    return {t: [sum(x[i] for x in v) / len(v) for i in range(4)] for t, v in par_type.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", action="append", required=True, help="nom=dossier_index:mode:rerank|norerank")
    ap.add_argument("--questions", default="data/validation_v1.json")
    ap.add_argument("--out", default="des_tests/ablation_recherche.md")
    args = ap.parse_args()
    questions = [q for q in load_questions(args.questions) if q["answerable"]]
    types = sorted({q["type"] for q in questions})
    lignes = ["| Configuration | R@5 | R@10 | MRR | nDCG@10 | " + " | ".join(f"R@5 {t}" for t in types) + " |",
              "|---|---|---|---|---|" + "---|" * len(types)]
    for spec in args.config:
        nom, reste = spec.split("=", 1)
        index_dir, mode, rr = reste.rsplit(":", 2)
        res = mesurer(index_dir, mode, rr == "rerank", questions)
        t = res["total"]
        lignes.append(f"| {nom} | {t[0]:.3f} | {t[1]:.3f} | {t[2]:.3f} | {t[3]:.3f} | "
                      + " | ".join(f"{res[ty][0]:.2f}" if ty in res else "–" for ty in types) + " |")
        print(lignes[-1], flush=True)
    texte = (f"# Ablation de la recherche\n\n{len(questions)} questions de validation avec réponse "
             f"({args.questions}). Pages de preuve cherchées dans les pages des passages classés.\n\n"
             + "\n".join(lignes) + "\n")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(texte, encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    main()
