"""Construction et mise à jour de l'index.

Contenu du dossier d'index :
    pages.json       une entrée par page physique {doc_id, page, text, source, date}
    chunks.json      les morceaux indexés {chunk_id, doc_id, page, text, index_text, date}
    embeddings.npy   un vecteur normalisé par chunk, dans le même ordre que chunks.json
    info.json        les réglages utilisés (parseur, chunking, modèle) pour les ablations
Le BM25 n'est pas enregistré : il se reconstruit en quelques secondes à partir des chunks.
"""
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from . import settings
from .chunking import decouper, titres_documents
from .ocr import ocr_pages
from .parsing import lire_pdf

MANIFEST = Path(__file__).resolve().parents[1] / "corpus" / "manifest.json"


def dates_des_documents():
    """doc_id -> date de publication (AAAA-MM-JJ), lue dans le manifeste du corpus."""
    try:
        docs = json.loads(MANIFEST.read_text(encoding="utf-8"))["documents"]
        return {d["doc_id"]: d.get("date", "") for d in docs}
    except (OSError, KeyError, ValueError):
        return {}


def lire_corpus(pdf_dir, reglages, deja_connus=(), ocr=True):
    """Pages des PDF du dossier (sauf documents déjà indexés), OCR des scans compris."""
    t0 = time.time()
    connus = set(deja_connus)
    chemins = [c for c in sorted(Path(pdf_dir).glob("*.pdf")) if c.stem not in connus]
    parseur = reglages.get("parser", "pymupdf_tables")
    # La détection des tableaux coûte environ 0,5 s par page : un processus par cœur du processeur
    with ProcessPoolExecutor(max_workers=os.cpu_count() or 1) as pool:
        pages = [p for doc in pool.map(lire_pdf, chemins, [parseur] * len(chemins)) for p in doc]
    for p in pages:
        p["source"] = reglages.get("parser", "pymupdf_tables")
    if ocr and reglages.get("ocr", True):
        ocr_pages(pdf_dir, pages)
    dates = dates_des_documents()
    for p in pages:
        p["date"] = dates.get(p["doc_id"], "")
    print(f"[index] {len(pages)} pages lues en {time.time() - t0:.0f} s")
    return pages


def decouper_pages(pages, reglages):
    return decouper(pages, strategie=reglages.get("chunking", "contextual"), taille=reglages["chunk_words"],
                    recouvrement=reglages["chunk_overlap"], titres=titres_documents(pages))


def encoder(chunks, reglages):
    from scratch.dense import Encodeur

    t0 = time.time()
    vecteurs = Encodeur(reglages["embed_model"]).encode([c["index_text"] for c in chunks])
    print(f"[index] {len(chunks)} chunks encodés en {time.time() - t0:.0f} s")
    return vecteurs


def sauver(index_dir, pages, chunks, embeddings, reglages):
    out = Path(index_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pages.json").write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    (out / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    np.save(out / "embeddings.npy", embeddings)
    info = {k: reglages.get(k) for k in ("parser", "ocr", "chunking", "chunk_words", "chunk_overlap", "embed_model")}
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")


def charger(index_dir):
    d = Path(index_dir)
    pages = json.loads((d / "pages.json").read_text(encoding="utf-8"))
    chunks = json.loads((d / "chunks.json").read_text(encoding="utf-8"))
    embeddings = np.load(d / "embeddings.npy")
    return pages, chunks, embeddings


def build_index(pdf_dir, index_dir, pages_from=None):
    """Indexe le corpus. `pages_from` : réutilise les pages (et l'OCR) d'un autre index, pour une ablation."""
    t0 = time.time()
    reglages = settings.load()
    if pages_from:
        pages = json.loads((Path(pages_from) / "pages.json").read_text(encoding="utf-8"))
        if not reglages.get("ocr", True):  # ablation sans OCR : on revide les pages lues par OCR
            pages = [dict(p, text="") if p.get("source") == "ocr" else p for p in pages]
    else:
        pages = lire_corpus(pdf_dir, reglages)
    chunks = decouper_pages(pages, reglages)
    print(f"[index] {len(pages)} pages, {len(chunks)} chunks (chunking {reglages.get('chunking')})")
    sauver(index_dir, pages, chunks, encoder(chunks, reglages), reglages)
    print(f"[index] terminé en {time.time() - t0:.0f} s")


def update_index(index_dir, pdf_dir):
    """Palier 3 : ajoute les nouveaux PDF sans réencoder les anciens."""
    t0 = time.time()
    reglages = settings.load()
    pages, chunks, embeddings = charger(index_dir)
    nouvelles = lire_corpus(pdf_dir, reglages, deja_connus={p["doc_id"] for p in pages})
    if not nouvelles:
        print("[update] aucun nouveau document")
        return
    nouveaux_chunks = decouper_pages(nouvelles, reglages)
    vecteurs = encoder(nouveaux_chunks, reglages)
    sauver(index_dir, pages + nouvelles, chunks + nouveaux_chunks, np.concatenate([embeddings, vecteurs]), reglages)
    print(f"[update] {len({p['doc_id'] for p in nouvelles})} documents, {len(nouvelles)} pages, "
          f"{len(nouveaux_chunks)} chunks ajoutés en {time.time() - t0:.0f} s")
