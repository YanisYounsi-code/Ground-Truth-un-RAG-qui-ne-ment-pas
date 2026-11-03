"""Palier 1 : recherche dense, embeddings d'un modèle open weights, cosinus et top-k en NumPy.

Un embedding est une liste de nombres (un vecteur) qui représente le sens d'un texte.
Deux textes de sens proche ont des vecteurs proches, même s'ils n'ont aucun mot en commun.
"""

import numpy as np

MODELE = "BAAI/bge-m3"  # multilingue (français et anglais), open weights, 1 024 dimensions


class Encodeur:
    """Transforme des textes en vecteurs avec un modèle de Hugging Face."""

    def __init__(self, nom=MODELE, longueur_max=512):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.tok = AutoTokenizer.from_pretrained(nom)
        self.modele = AutoModel.from_pretrained(nom, dtype=dtype).to(self.device).eval()
        self.longueur_max = longueur_max

    def encode(self, textes, batch=32):
        """Renvoie une matrice (nombre de textes x dimension), une ligne de norme 1 par texte."""
        vecteurs = []
        for i in range(0, len(textes), batch):
            lot = self.tok(textes[i:i + batch], padding=True, truncation=True,
                           max_length=self.longueur_max, return_tensors="pt").to(self.device)
            with self.torch.no_grad():
                sortie = self.modele(**lot).last_hidden_state
            # bge-m3 représente le texte entier par le vecteur du premier token ([CLS])
            vecteurs.append(sortie[:, 0].float().cpu().numpy())
        matrice = np.concatenate(vecteurs) if vecteurs else np.zeros((0, 1), dtype=np.float32)
        return normaliser(matrice)


def normaliser(matrice):
    """Divise chaque ligne par sa norme : le produit scalaire devient alors le cosinus."""
    normes = np.linalg.norm(matrice, axis=1, keepdims=True)
    return (matrice / np.maximum(normes, 1e-12)).astype(np.float32)


def recherche(matrice, vecteur_question, k=10):
    """Les k lignes les plus proches de la question : [(numéro, cosinus)] triés, en NumPy pur."""
    scores = matrice @ vecteur_question  # un produit scalaire par chunk = le cosinus
    k = min(k, len(scores))
    meilleurs = np.argpartition(-scores, k - 1)[:k]  # les k meilleurs, dans le désordre
    meilleurs = meilleurs[np.argsort(-scores[meilleurs])]  # puis triés du meilleur au moins bon
    return [(int(i), float(scores[i])) for i in meilleurs]


if __name__ == "__main__":
    # Test sans modèle : 4 vecteurs en 2 dimensions
    m = normaliser(np.array([[1, 0], [0, 1], [1, 1], [-1, 0]], dtype=np.float32))
    q = normaliser(np.array([[1, 0.2]], dtype=np.float32))[0]
    print(recherche(m, q, k=3))  # attendu : 0 puis 2 puis 1
