"""OCR des pages sans texte (les documents « numérisés » du corpus), avec Tesseract.

Une page dont PyMuPDF ne sort presque rien est une image : on la rend en image puis on la lit
avec Tesseract, en français si le modèle de langue est installé. Si Tesseract manque, on le
signale et on continue : la page reste vide, comme avec la baseline.
"""
import io

SEUIL_VIDE = 50  # moins de 50 caractères extraits : la page est considérée comme un scan


def langue_tesseract():
    """'fra' si le modèle français est installé, sinon 'eng', ou None si Tesseract est absent."""
    try:
        import pytesseract

        langues = pytesseract.get_languages(config="")
    except Exception:  # noqa: BLE001
        return None
    if "fra" in langues:
        return "fra"
    return "eng" if "eng" in langues else None


def ocr_pages(pdf_dir, pages, dpi=200):
    """Remplace le texte des pages quasi vides par le texte lu par OCR. Renvoie le nombre de pages lues."""
    vides = [p for p in pages if len(p["text"].strip()) < SEUIL_VIDE]
    if not vides:
        return 0
    langue = langue_tesseract()
    if langue is None:
        print(f"[ocr] Tesseract absent : {len(vides)} pages scannées resteront vides (lance setup.sh)")
        return 0
    if langue != "fra":
        print("[ocr] modèle français absent (paquet tesseract-ocr-fra) : lecture en anglais, moins fiable")
    import pymupdf
    import pytesseract
    from PIL import Image

    lues, ouverts = 0, {}
    for p in vides:
        chemin = f"{pdf_dir}/{p['doc_id']}.pdf"
        if chemin not in ouverts:
            ouverts[chemin] = pymupdf.open(chemin)
        pixmap = ouverts[chemin][p["page"] - 1].get_pixmap(dpi=dpi)
        image = Image.open(io.BytesIO(pixmap.tobytes("png")))
        try:
            texte = pytesseract.image_to_string(image, lang=langue)
        except pytesseract.TesseractError as e:
            print(f"[ocr] {p['doc_id']} p.{p['page']} illisible : {e}")
            continue
        if texte.strip():
            p["text"], p["source"] = texte, "ocr"
            lues += 1
    for doc in ouverts.values():
        doc.close()
    print(f"[ocr] {lues} pages lues par OCR ({langue}) sur {len(vides)} pages sans texte")
    return lues
