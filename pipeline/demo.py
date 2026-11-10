"""Démo live (soutenance) : pose des questions au pipeline complet et montre comment il a répondu.

    python -m pipeline.demo --index-dir /content/idx/final "Combien de pharmacies en France en 2022 ?"
    python -m pipeline.demo --index-dir /content/idx/final --fichier questions_jury.txt   (une par ligne)

Les questions passent exactement par le même chemin que `run.sh answer` (recherche, puis génération
et vérification). Pour chaque question, on affiche :
  - la réponse et ses citations ;
  - si le système s'est abstenu après vérification, ce que le modèle avait écrit et pourquoi c'est refusé ;
  - les 3 meilleurs passages trouvés, avec leur date et leur score de reranker.
"""
import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-dir", required=True)
    ap.add_argument("questions", nargs="*")
    ap.add_argument("--fichier", help="fichier texte, une question par ligne")
    ap.add_argument("--out", default="runs/demo.json")
    args = ap.parse_args()

    questions = list(args.questions)
    if args.fichier:
        questions += [l.strip() for l in Path(args.fichier).read_text(encoding="utf-8").splitlines() if l.strip()]
    if not questions:
        ap.error("donne au moins une question")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    chemin_q = Path(args.out).with_name("demo_questions.json")
    chemin_q.write_text(json.dumps({"questions": [{"qid": f"demo-{i:02d}", "question": q}
                                                  for i, q in enumerate(questions, 1)]},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    env = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")  # comme à la finale : sans réseau
    subprocess.run([sys.executable, "-m", "pipeline", "answer", "--index-dir", args.index_dir,
                    "--questions", str(chemin_q), "--out", args.out], check=True, env=env)

    preds = {p["qid"]: p for p in json.loads(Path(args.out).read_text(encoding="utf-8"))["predictions"]}
    recherche = json.loads(Path(args.out).with_suffix(".retrieval.json").read_text(encoding="utf-8"))
    for i, q in enumerate(questions, 1):
        qid = f"demo-{i:02d}"
        p, r = preds[qid], recherche[qid]
        print("\n" + "=" * 100)
        print(f"QUESTION {i} : {q}")
        print("-" * 100)
        print(textwrap.fill(f"RÉPONSE : {p['answer']}", 100))
        if p["citations"]:
            print("SOURCES : " + ", ".join(f"[{c['doc_id']} p.{c['page']}]" for c in p["citations"]))
        if p["answer"] == "INTROUVABLE" and p.get("raw"):
            print(textwrap.fill(f"(le modèle avait écrit : {p['raw'].split('SOURCES')[0].strip()[:300]})", 100))
            if p.get("verif"):
                print(f"(refusé par la vérification : {p['verif']})")
        print("Meilleurs passages :")
        for x in r["passages"][:3]:
            extrait = " ".join(x["text"].split())[:160]
            print(f"  [{x['doc_id']} p.{x['page']} · {x.get('date', '')} · score {x['score']:.3f}] {extrait}…")


if __name__ == "__main__":
    main()
