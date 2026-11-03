"""Calibre le seuil de la porte d'abstention sur la validation.

Entrée : une exécution SANS porte (--no-gate), où chaque prédiction garde le score du meilleur
passage, et le rapport détaillé de l'évaluation officielle (points par question).
Pour chaque seuil possible, on simule : sous le seuil, le système aurait répondu INTROUVABLE
(+1 sur une question sans réponse, 0 sinon) ; au-dessus, il garde les points obtenus.
On retient le seuil qui maximise le score de confiance, et on trace la courbe.

    python -m pipeline.calibrate --pred runs/val1_nogate.json --report runs/val1_report.json
    (plusieurs paires possibles : --pred A --report RA --pred B --report RB)
"""
import argparse
import json
from pathlib import Path

from . import settings


def lignes(pred_path, report_path):
    preds = json.loads(Path(pred_path).read_text(encoding="utf-8"))["predictions"]
    scores = {p["qid"]: p.get("score") for p in preds}
    details = json.loads(Path(report_path).read_text(encoding="utf-8"))["details"]
    return [{"qid": d["qid"], "answerable": d["answerable"], "points": d["points"],
             "score": scores.get(d["qid"])} for d in details]


def score_avec_seuil(rows, seuil):
    total = 0.0
    for r in rows:
        if r["score"] is not None and r["score"] < seuil:
            total += 0.0 if r["answerable"] else 1.0  # le système se serait tu
        else:
            total += r["points"]
    return total / len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", action="append", required=True)
    ap.add_argument("--report", action="append", required=True)
    ap.add_argument("--csv", default="runs/calibration.csv")
    ap.add_argument("--dry-run", action="store_true", help="affiche sans écrire settings.json")
    args = ap.parse_args()

    rows = [r for p, rep in zip(args.pred, args.report) for r in lignes(p, rep)]
    candidats = sorted({0.0, 1.01} | {r["score"] for r in rows if r["score"] is not None})
    courbe = [(s, score_avec_seuil(rows, s)) for s in candidats]
    meilleur = max(v for _, v in courbe)
    ex_aequo = [s for s, v in courbe if v == meilleur]
    seuil = ex_aequo[len(ex_aequo) // 2]  # milieu du plateau : moins sensible au hasard des 100 questions

    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    Path(args.csv).write_text("seuil;score_confiance\n" + "".join(f"{s:.4f};{v:.4f}\n" for s, v in courbe),
                              encoding="utf-8")
    sans_porte = score_avec_seuil(rows, 0.0)
    jamais = score_avec_seuil(rows, 1.01)
    print(f"{len(rows)} questions")
    print(f"  sans porte (répond toujours)  : {sans_porte:+.3f}")
    print(f"  toujours INTROUVABLE          : {jamais:+.3f}")
    print(f"  meilleur seuil = {seuil:.3f}         : {meilleur:+.3f}")
    for pct in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        print(f"    seuil {pct:.1f} -> {score_avec_seuil(rows, pct):+.3f}")
    print(f"Courbe complète : {args.csv}")
    if not args.dry_run:
        reglages = settings.load()
        reglages["threshold"] = round(seuil, 4)
        settings.save(reglages)
        print("Seuil écrit dans pipeline/settings.json")


if __name__ == "__main__":
    main()
