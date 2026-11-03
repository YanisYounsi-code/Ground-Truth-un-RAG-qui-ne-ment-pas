"""Extraction du texte des pages : trois approches, comparées sur 30 pages annotées (parsing_bench).

    pymupdf         le texte brut de PyMuPDF (la baseline du palier 1)
    pymupdf_tables  le texte brut + chaque tableau détecté réécrit en Markdown, lignes et colonnes
                    gardées (« |Europe du Sud|11|11|16|11|7| » sous « |Origines|2006|2010|2014|... »)
    tesseract       la page rendue en image puis lue par OCR

Dans l'index, les pages sans texte (scans) passent toujours par l'OCR (pipeline/ocr.py).
"""
import io


def texte_pymupdf(page):
    return page.get_text()


def tableaux_markdown(page):
    """Les tableaux détectés par PyMuPDF, en Markdown ; chaîne vide si aucun."""
    try:
        tableaux = page.find_tables().tables
    except Exception:  # noqa: BLE001  (détection impossible sur certaines pages)
        return ""
    blocs = []
    for t in tableaux:
        try:
            md = t.to_markdown().strip()
        except Exception:  # noqa: BLE001
            continue
        if md.count("|") >= 6:  # au moins deux colonnes : sinon ce n'est pas un vrai tableau
            blocs.append(md)
    return "\n\n".join(blocs)


def texte_pymupdf_tables(page):
    texte = page.get_text()
    md = tableaux_markdown(page)
    return f"{texte}\n\nTableaux de la page :\n{md}" if md else texte


def texte_tesseract(page, dpi=200, langue="fra"):
    import pytesseract
    from PIL import Image

    image = Image.open(io.BytesIO(page.get_pixmap(dpi=dpi).tobytes("png")))
    return pytesseract.image_to_string(image, lang=langue)


PARSEURS = {"pymupdf": texte_pymupdf, "pymupdf_tables": texte_pymupdf_tables, "tesseract": texte_tesseract}


def lire_pdf(chemin, parseur="pymupdf_tables"):
    """[{doc_id, page, text}] pour un PDF, avec le parseur choisi."""
    import pymupdf
    from pathlib import Path

    extraire = PARSEURS[parseur]
    pages = []
    with pymupdf.open(chemin) as doc:
        for numero, page in enumerate(doc, start=1):
            pages.append({"doc_id": Path(chemin).stem, "page": numero, "text": extraire(page)})
    return pages
