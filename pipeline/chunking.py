"""Trois stratégies de découpage, comparées dans l'ablation.

    naive       taille fixe avec recouvrement (scratch/chunker.py, palier 1)
    structure   suit la structure de la page : un chunk ne coupe jamais une phrase ni un tableau,
                et un intertitre (Figure, Tableau, 1., II. ...) ouvre un nouveau chunk
    contextual  structure + un en-tête de contexte (document, début de son titre, date, section)
                ajouté au texte indexé, pour que BM25 et l'embedder sachent de quoi parle un passage

Chaque chunk a `text` (ce que lit le LLM) et `index_text` (ce que voient BM25 et l'embedder).
"""
import re

from scratch.chunker import chunk_pages

# Un intertitre : « Figure 3 », « Tableau 2 », « Encadré », « 1. », « 2.3 », « II. », « Chapitre IV »...
INTERTITRE = re.compile(r"^(Figure|Tableau|Graphique|Encadré|Chapitre|Partie|Annexe|Recommandation"
                        r"|[IVX]{1,5}\s*[.–-]|\d{1,2}(\.\d{1,2})*\s*[.–-]?\s+[A-ZÀ-Ý])")
FIN_DE_PHRASE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÀ-Ý0-9«(])")


def _blocs(texte):
    """Découpe une page en blocs dans l'ordre : ('intertitre', ligne), ('texte', ...), ('tableau', ...)."""
    blocs, courant = [], []

    def fermer():
        if courant:
            blocs.append(("texte", " ".join(courant)))
            courant.clear()

    for ligne in (l.strip() for l in texte.split("\n")):
        if not ligne:
            continue
        if ligne.startswith("|"):  # ligne de tableau Markdown : le tableau reste d'un seul tenant
            fermer()
            if blocs and blocs[-1][0] == "tableau":
                blocs[-1] = ("tableau", blocs[-1][1] + "\n" + ligne)
            else:
                blocs.append(("tableau", ligne))
        elif INTERTITRE.match(ligne) and len(ligne.split()) <= 14:
            fermer()
            blocs.append(("intertitre", ligne))
        else:
            courant.append(ligne)
    fermer()
    return blocs


def chunk_structure(pages, taille=250, minimum=60):
    """Remplit des chunks phrase par phrase jusqu'à `taille` mots ; un intertitre ouvre un nouveau chunk
    dès que le chunk en cours a au moins `minimum` mots ; un tableau forme son propre chunk."""
    chunks = []
    for p in pages:
        phrases, n_mots, section, n = [], 0, "", 0

        def emettre():
            nonlocal phrases, n_mots, n
            if phrases:
                chunks.append({"chunk_id": f"{p['doc_id']}#{p['page']}#{n}", "doc_id": p["doc_id"],
                               "page": p["page"], "text": " ".join(phrases), "section": section})
                n += 1
            phrases, n_mots = [], 0

        for genre, contenu in _blocs(p["text"]):
            if genre == "tableau":
                emettre()
                phrases, n_mots = [contenu], len(contenu.split())
                emettre()
                continue
            if genre == "intertitre":
                if n_mots >= minimum:
                    emettre()
                section = contenu[:80]
            for phrase in FIN_DE_PHRASE.split(contenu):
                mots = len(phrase.split())
                if n_mots + mots > taille and n_mots >= minimum:
                    emettre()
                if mots > taille:  # « phrase » géante (liste de chiffres sans point) : découpe naïve
                    for c in chunk_pages([{"doc_id": "", "page": 0, "text": phrase}], taille, 50):
                        phrases, n_mots = [c["text"]], taille
                        emettre()
                    continue
                phrases.append(phrase)
                n_mots += mots
        emettre()
    return chunks


def decouper(pages, strategie="contextual", taille=250, recouvrement=50, titres=None):
    """Découpe les pages selon la stratégie ; `titres` : doc_id -> début du document (contextual)."""
    if strategie == "naive":
        chunks = chunk_pages(pages, taille=taille, recouvrement=recouvrement)
    else:
        chunks = chunk_structure(pages, taille=taille)
    dates = {(p["doc_id"], p["page"]): p.get("date", "") for p in pages}
    for c in chunks:
        c["date"] = dates.get((c["doc_id"], c["page"]), "")
        if strategie == "contextual":
            entete = [f"Document {c['doc_id']}"]
            if titres and titres.get(c["doc_id"]):
                entete.append(titres[c["doc_id"]])
            if c["date"]:
                entete.append(f"publié le {c['date']}")
            if c.get("section"):
                entete.append(f"section : {c['section']}")
            c["index_text"] = " · ".join(entete) + "\n" + c["text"]
        else:
            c["index_text"] = c["text"]
    return chunks


def titres_documents(pages, n_mots=20):
    """Début de la première page de chaque document : une approximation de son titre et de son sujet."""
    titres = {}
    for p in pages:
        if p["page"] == 1 and p["text"].strip():
            mots = [m for m in p["text"].split() if not m.startswith("|")]
            titres[p["doc_id"]] = " ".join(mots[:n_mots])
    return titres
