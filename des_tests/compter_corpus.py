"""Compte les documents et les pages du corpus, par version et par source."""
import json
from collections import Counter
from pathlib import Path

import pymupdf

docs = json.loads(Path("corpus/manifest.json").read_text(encoding="utf-8"))["documents"]
print("Documents par version et source :", Counter((d["corpus_version"], d["source"]) for d in docs))

for dossier in ("corpus/pdf", "corpus/pdf_v2"):
    pages = Counter()
    for chemin in Path(dossier).glob("*.pdf"):
        with pymupdf.open(chemin) as doc:
            pages["insee" if chemin.stem.startswith("insee") else "cour"] += len(doc)
    print(dossier, ":", sum(pages.values()), "pages", dict(pages))
