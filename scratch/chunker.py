"""Palier 1 : chunker naïf, des morceaux de taille fixe avec recouvrement.

Chaque morceau reste à l'intérieur d'une seule page : il garde donc son (doc_id, page),
ce qui permet de citer la page exacte de la preuve.
"""


def chunk_pages(pages, taille=250, recouvrement=50):
    """Découpe chaque page en morceaux de `taille` mots qui se recouvrent de `recouvrement` mots.

    Le recouvrement évite qu'une phrase utile soit coupée en deux sans être entière nulle part.
    """
    pas = taille - recouvrement
    chunks = []
    for p in pages:
        mots = p["text"].split()
        if not mots:
            continue  # page vide (scan non lu) : rien à indexer
        debut, n = 0, 0
        while True:
            morceau = mots[debut:debut + taille]
            chunks.append({
                "chunk_id": f"{p['doc_id']}#{p['page']}#{n}",
                "doc_id": p["doc_id"],
                "page": p["page"],
                "text": " ".join(morceau),
            })
            if debut + taille >= len(mots):
                break  # la fin de la page est couverte
            debut += pas
            n += 1
    return chunks


if __name__ == "__main__":
    page = {"doc_id": "test", "page": 1, "text": " ".join(f"mot{i}" for i in range(600))}
    for c in chunk_pages([page]):
        mots = c["text"].split()
        print(c["chunk_id"], len(mots), "mots, de", mots[0], "à", mots[-1])
