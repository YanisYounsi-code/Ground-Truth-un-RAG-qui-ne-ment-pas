"""Réglages du pipeline, lus dans pipeline/settings.json (versionné avec le code).

Le seuil d'abstention calibré y est écrit par `python -m pipeline.calibrate` : il fait partie du
code figé à la finale, pas de l'index, qui est reconstruit par l'orga.
Pour une ablation, la variable d'environnement GT_SETTINGS peut désigner un autre fichier, et
GT_OVERRIDE quelques réglages au format JSON (ex. GT_OVERRIDE='{"chunking": "naive"}').
"""
import json
import os
from pathlib import Path

CHEMIN = Path(os.environ.get("GT_SETTINGS", Path(__file__).with_name("settings.json")))


def load():
    reglages = json.loads(CHEMIN.read_text(encoding="utf-8"))
    reglages.update(json.loads(os.environ.get("GT_OVERRIDE", "{}")))
    return reglages


def save(reglages):
    CHEMIN.write_text(json.dumps(reglages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
