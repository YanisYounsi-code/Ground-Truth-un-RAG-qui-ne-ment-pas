"""Palier 2 : comparaison des parseurs sur 30 pages difficiles annotées à la main.

1. Sélection (une fois) : 10 pages de tableau, 10 de graphique, 10 scannées, prises parmi les pages
   de preuve de la validation. Écrit le fichier d'annotation et une image PNG de chaque page.
       python -m pipeline.parsing_bench select
2. Annotation (à la main) : pour chaque page de des_tests/parsing_annotations.json, regarde son image
   (runs/parsing_png/) et complète `faits` : au moins 2 valeurs lisibles sur la page, chacune avec
   `valeur` (exactement comme imprimée) et `libelle` (les mots qui doivent être sur la même ligne
   que la valeur : le nom de la ligne du tableau, du point du graphique...). Puis "verifie": true.
3. Mesure :
       python -m pipeline.parsing_bench eval
   Pour chaque parseur : part des valeurs retrouvées dans le texte extrait (rappel des valeurs), et
   part des valeurs retrouvées sur la même ligne que leur libellé (lien valeur-libellé : c'est ce
   qui permet au LLM de savoir à quoi correspond un nombre).
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from groundtruth.normalize import value_present
from scratch.tokenizer import tokenize

ANNOTATIONS = Path("des_tests/parsing_annotations.json")
IMAGES = Path("runs/parsing_png")
TYPES = ("tableau", "graphique", "scan")


def selectionner(questions_path="data/validation_v1.json", par_type=10):
    from groundtruth.io import load_questions

    choisies, vues = [], set()
    for t in TYPES:
        n = 0
        for q in load_questions(questions_path):
            if q["type"] != t or not q["answerable"]:
                continue
            e = q["evidence"][0][0]
            cle = (e["doc_id"], e["page"])
            if cle in vues:
                continue
            vues.add(cle)
            choisies.append({"doc_id": e["doc_id"], "page": e["page"], "type": t, "qid": q["qid"],
                             "indice": q.get("source_quote", ""),
                             "faits": [{"valeur": v, "libelle": ""} for v in q.get("key_values", [])],
                             "verifie": False})
            n += 1
            if n == par_type:
                break
    # Moins de 10 pages d'un type dans la validation : on complète avec d'autres pages de scans
    if sum(c["type"] == "scan" for c in choisies) < par_type:
        from .ocr import SEUIL_VIDE
        import pymupdf

        for doc_id in ("insee-ip2041", "insee-ip2055", "insee-ip2075", "cc-pac-synthese"):
            with pymupdf.open(f"corpus/pdf/{doc_id}.pdf") as doc:
                for i in range(len(doc)):
                    if sum(c["type"] == "scan" for c in choisies) >= par_type:
                        break
                    if (doc_id, i + 1) not in vues and len(doc[i].get_text().strip()) < SEUIL_VIDE:
                        vues.add((doc_id, i + 1))
                        choisies.append({"doc_id": doc_id, "page": i + 1, "type": "scan", "qid": "",
                                         "indice": "", "faits": [], "verifie": False})
    return choisies


def rendre_images(pages):
    import pymupdf

    IMAGES.mkdir(parents=True, exist_ok=True)
    for p in pages:
        with pymupdf.open(f"corpus/pdf/{p['doc_id']}.pdf") as doc:
            doc[p["page"] - 1].get_pixmap(dpi=110).save(IMAGES / f"{p['type']}_{p['doc_id']}_p{p['page']}.png")


def lien(fait, texte):
    """La valeur figure-t-elle sur une ligne qui contient aussi les mots de son libellé ?"""
    mots = set(tokenize(fait["libelle"]))
    if not mots:
        return False
    for ligne in texte.split("\n"):
        if value_present(fait["valeur"], ligne) and mots <= set(tokenize(ligne)):
            return True
    return False


def evaluer(parseurs=("pymupdf", "pymupdf_tables", "tesseract")):
    import pymupdf

    from .parsing import PARSEURS

    pages = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
    pages = [p for p in pages if p["faits"]]
    non_verifiees = sum(not p.get("verifie") for p in pages)
    stats = {nom: defaultdict(lambda: [0, 0, 0]) for nom in parseurs}  # type -> [faits, retrouvés, liés]
    for p in pages:
        with pymupdf.open(f"corpus/pdf/{p['doc_id']}.pdf") as doc:
            page = doc[p["page"] - 1]
            for nom in parseurs:
                try:
                    texte = PARSEURS[nom](page)
                except Exception as e:  # noqa: BLE001  (Tesseract absent, par exemple)
                    print(f"[bench] {nom} impossible sur {p['doc_id']} p.{p['page']} : {e}")
                    texte = ""
                for f in p["faits"]:
                    for cle in (p["type"], "total"):
                        s = stats[nom][cle]
                        s[0] += 1
                        s[1] += value_present(f["valeur"], texte)
                        s[2] += lien(f, texte)
    lignes = ["| Parseur | " + " | ".join(f"{t} : valeurs / liens" for t in (*TYPES, "total")) + " |",
              "|---|" + "---|" * (len(TYPES) + 1)]
    for nom in parseurs:
        cellules = []
        for t in (*TYPES, "total"):
            n, ok, lies = stats[nom][t]
            cellules.append(f"{ok / n:.0%} / {lies / n:.0%}" if n else "–")
        lignes.append(f"| {nom} | " + " | ".join(cellules) + " |")
    n_faits = stats[parseurs[0]]["total"][0]
    tableau = "\n".join(lignes)
    resume = (f"{len(pages)} pages annotées, {n_faits} valeurs. Valeurs : part des valeurs retrouvées dans le "
              f"texte extrait. Liens : part retrouvée sur la même ligne que son libellé.")
    if non_verifiees:
        resume += f" ATTENTION : {non_verifiees} pages pas encore vérifiées à la main."
    Path("des_tests/parsing_resultats.md").write_text(f"# Comparaison des parseurs\n\n{resume}\n\n{tableau}\n",
                                                      encoding="utf-8")
    print(resume)
    print(tableau)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["select", "images", "eval"])
    args = ap.parse_args()
    if args.action == "select":
        if ANNOTATIONS.exists():
            print(f"{ANNOTATIONS} existe déjà : je ne l'écrase pas (supprime-le pour recommencer).")
            pages = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
        else:
            pages = selectionner()
            ANNOTATIONS.parent.mkdir(parents=True, exist_ok=True)
            ANNOTATIONS.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{len(pages)} pages écrites dans {ANNOTATIONS}")
        rendre_images(pages)
        print(f"Images dans {IMAGES}/")
    elif args.action == "images":
        rendre_images(json.loads(ANNOTATIONS.read_text(encoding="utf-8")))
    else:
        evaluer()


if __name__ == "__main__":
    main()
