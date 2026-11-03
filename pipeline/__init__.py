"""Pipeline Ground Truth (palier 2 et suivants).

    python -m pipeline index  --pdf-dir corpus/pdf    --index-dir index/
    python -m pipeline update --index-dir index/      --pdf-dir corpus/pdf_v2
    python -m pipeline answer --index-dir index/      --questions data/validation_v1.json --out runs/val1.json

Réutilise les briques codées à la main au palier 1 (scratch/) et y ajoute l'OCR des scans,
la fusion BM25 + dense, le reranker, la porte d'abstention et le générateur officiel.
"""
import os as _os

# Comme le kit : JAX (importé par certaines librairies) réserve sinon 75 % de la mémoire du GPU.
_os.environ.setdefault("JAX_PLATFORMS", "cpu")
_os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
