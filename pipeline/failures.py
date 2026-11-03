"""Palier 1 : sélectionne des réponses ratées à commenter, en séparant les deux causes possibles.

    échec de recherche   la page de preuve n'était pas dans les 5 premiers résultats
    échec de génération  la page était là, mais la réponse est fausse ou le système s'est tu

    python -m pipeline.failures --pred runs/val1_rag.json --report runs/val1_rag_report.json \
                                --gold data/validation_v1.json --out des_tests/echecs.md
"""
import argparse
import json
from pathlib import Path

from groundtruth.io import load_questions
from scratch.metrics import recall_at_k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--gold", default="data/validation_v1.json")
    ap.add_argument("--out", default="des_tests/echecs.md")
    ap.add_argument("--n", type=int, default=5)
    args = ap.parse_args()
    preds = {p["qid"]: p for p in json.loads(Path(args.pred).read_text(encoding="utf-8"))["predictions"]}
    details = {d["qid"]: d for d in json.loads(Path(args.report).read_text(encoding="utf-8"))["details"]}
    rates = []
    for q in load_questions(args.gold):
        d, p = details[q["qid"]], preds.get(q["qid"], {})
        if d["points"] > 0:
            continue
        if q["answerable"]:
            classement = [(r["doc_id"], r["page"]) for r in p.get("retrieved", [])]
            cause = "génération" if recall_at_k(classement, q, 5) == 1 else "recherche"
        else:
            cause = "hallucination sur une question piège"
        rates.append((q, p, d, cause))
    # Des types et des causes variés : un échec de chaque sorte avant d'en prendre un second
    choisis, vus = [], set()
    for q, p, d, cause in rates:
        if (q["type"], cause) not in vus:
            vus.add((q["type"], cause))
            choisis.append((q, p, d, cause))
    choisis = (choisis + [r for r in rates if r not in choisis])[: args.n]
    blocs = [f"# {args.n} réponses ratées commentées\n\n{len(rates)} questions perdent des points sur "
             f"{len(details)} ({args.pred}).\n"]
    for i, (q, p, d, cause) in enumerate(choisis, 1):
        pages = ", ".join(f"{e['doc_id']} p.{e['page']}" for g in q["evidence"] for e in g) or "aucune"
        trouvees = ", ".join(f"{r['doc_id']} p.{r['page']}" for r in p.get("retrieved", [])[:5])
        blocs.append(
            f"## {i}. {q['qid']} ({q['type']}, {d['outcome']}, {d['points']:+g})\n\n"
            f"- **Question** : {q['question']}\n- **Réponse attendue** : {q.get('answer', '')}\n"
            f"- **Réponse du système** : {p.get('answer', '')}\n- **Pages de preuve** : {pages}\n"
            f"- **Top 5 retrouvé** : {trouvees}\n- **Cause** : échec de {cause}\n"
            f"- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_\n")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(blocs), encoding="utf-8")
    print("\n".join(blocs))


if __name__ == "__main__":
    main()
