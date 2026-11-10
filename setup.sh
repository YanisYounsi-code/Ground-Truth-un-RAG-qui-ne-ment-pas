#!/usr/bin/env bash
# Phase d'installation de la finale : seule phase où le réseau est disponible.
# Installe les dépendances, Tesseract (OCR des scans) et télécharge TOUS les poids utilisés.
set -euo pipefail
pip install -q -r requirements.txt
# Tesseract + le modèle de langue française, pour lire les 10 documents numérisés.
# Colab a déjà Tesseract mais SANS le français : on installe le paquet français s'il manque.
if ! (command -v tesseract >/dev/null 2>&1 && tesseract --list-langs 2>/dev/null | grep -qx fra); then
  if command -v apt-get >/dev/null 2>&1; then
    SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    $SUDO apt-get -qq update && $SUDO apt-get -qq install -y tesseract-ocr tesseract-ocr-fra >/dev/null \
      || echo "ATTENTION : Tesseract français non installé, les pages scannées seront lues en anglais"
  else
    echo "ATTENTION : apt-get absent, installe tesseract-ocr et tesseract-ocr-fra à la main"
  fi
fi
tesseract --list-langs 2>/dev/null | grep -qx fra && echo "OCR : Tesseract français prêt" || echo "ATTENTION : pas de Tesseract français"
python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("mistralai/Ministral-3-3B-Instruct-2512")   # générateur officiel (obligatoire)
for repo in [
    "BAAI/bge-m3",                              # embedder (recherche dense)
    "BAAI/bge-reranker-v2-m3",                  # reranker
    "Qwen/Qwen3-4B-Instruct-2507",              # juge officiel, pour évaluer sur la validation
]:
    snapshot_download(repo, ignore_patterns=["onnx/*", "*.onnx", "*.h5", "*.msgpack", "*.ot"])
PY
