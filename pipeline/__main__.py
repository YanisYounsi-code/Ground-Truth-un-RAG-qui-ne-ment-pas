"""Point d'entrée : python -m pipeline index | update | answer | retrieve | generate."""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(prog="python -m pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("index", help="construit l'index du corpus v1")
    a.add_argument("--pdf-dir", required=True)
    a.add_argument("--index-dir", required=True)
    a.add_argument("--pages-from", default=None, help="réutilise les pages (et l'OCR) d'un autre index")

    u = sub.add_parser("update", help="ajoute de nouveaux PDF à un index existant")
    u.add_argument("--index-dir", required=True)
    u.add_argument("--pdf-dir", required=True)

    for nom in ("answer", "retrieve", "generate"):
        b = sub.add_parser(nom)
        b.add_argument("--index-dir", required=nom != "generate")
        b.add_argument("--questions", required=True)
        b.add_argument("--out", required=True)
        b.add_argument("--mode", default="hybrid", choices=["bm25", "dense", "hybrid"])
        b.add_argument("--no-rerank", action="store_true", help="sans reranker (ablation)")
        b.add_argument("--no-gate", action="store_true", help="sans porte d'abstention (calibration, ablation)")
        b.add_argument("--backend", default="hf", choices=["hf", "openai", "echo"])
        b.add_argument("--retrieval", default=None, help="fichier de recherche (par défaut : à côté de --out)")

    args = ap.parse_args()
    if args.cmd == "index":
        from .index import build_index

        build_index(args.pdf_dir, args.index_dir, pages_from=args.pages_from)
    elif args.cmd == "update":
        from .index import update_index

        update_index(args.index_dir, args.pdf_dir)
    else:
        recherche = args.retrieval or str(Path(args.out).with_suffix(".retrieval.json"))
        if args.cmd in ("answer", "retrieve"):
            if args.cmd == "answer":
                # La recherche tourne dans un processus séparé : quand il se termine, toute la mémoire
                # GPU de l'embedder et du reranker est rendue avant le chargement du générateur.
                cmd = [sys.executable, "-m", "pipeline", "retrieve", "--index-dir", args.index_dir,
                       "--questions", args.questions, "--out", args.out, "--mode", args.mode,
                       "--retrieval", recherche] + (["--no-rerank"] if args.no_rerank else [])
                subprocess.run(cmd, check=True)
            else:
                from .retrieve import retrieve_all

                retrieve_all(args.index_dir, args.questions, recherche, mode=args.mode, rerank=not args.no_rerank)
                return
        from .generate import answer_all

        answer_all(recherche, args.questions, args.out, backend=args.backend, gate=not args.no_gate)


if __name__ == "__main__":
    main()
