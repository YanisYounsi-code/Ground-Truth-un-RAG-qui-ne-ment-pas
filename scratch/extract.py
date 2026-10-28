"""Palier 1 : lit tous les PDF du corpus et enregistre une entrée par page."""

import json
from pathlib import Path

import pymupdf

PDF_DIR = Path("corpus/pdf")
OUT = Path("index/scratch/pages.json")


def read_pages(pdf_dir):
    """Renvoie une liste de dictionnaires {doc_id, page, text}, une entrée par page."""
    pages = []
    for chemin in sorted(pdf_dir.glob("*.pdf")):
        doc = pymupdf.open(chemin)
        for numero, page in enumerate(doc, start=1):
            pages.append(
                {"doc_id": chemin.stem, "page": numero, "text": page.get_text()}
            )
        doc.close()
    return pages


if __name__ == "__main__":
    pages = read_pages(PDF_DIR)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False)
    vides = sum(1 for p in pages if len(p["text"].strip()) < 50)
    print(len(pages), "pages enregistrées,", vides, "pages presque vides (scans)")
