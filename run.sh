#!/usr/bin/env bash
# Contrat du run final. L'orga exécute EXACTEMENT ces commandes sur un GPU T4 16 Go, sans réseau
# (sauf setup.sh) :
#
#   bash setup.sh                                           # réseau autorisé : dépendances + poids
#   bash run.sh index  <dossier_pdf_v1> <dossier_index>     # corpus v1 (110 docs) : 2 h max
#   bash run.sh update <dossier_index> <dossier_pdf_v2>     # ajout des 20 docs v2 : 20 min max
#   bash run.sh answer <dossier_index> <questions.json> <sortie.json>   # 30 s par question en moyenne
#
# Pipeline : OCR des scans + chunks + BM25 maison + dense bge-m3 + RRF + reranker + porte
# d'abstention calibrée + générateur officiel (voir pipeline/).
set -euo pipefail
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1   # aucun appel réseau après setup.sh
cmd="$1"; shift
case "$cmd" in
  index)  python -m pipeline index  --pdf-dir "$1" --index-dir "$2" ;;
  update) python -m pipeline update --index-dir "$1" --pdf-dir "$2" ;;
  answer) python -m pipeline answer --index-dir "$1" --questions "$2" --out "$3" --backend hf ;;
  *) echo "usage: run.sh index|update|answer ..." >&2; exit 1 ;;
esac
