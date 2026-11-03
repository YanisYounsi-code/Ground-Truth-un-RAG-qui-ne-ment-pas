"""Reranker : un modèle qui lit ensemble la question et un passage, et note leur pertinence.

Plus lent que BM25 ou la recherche dense (il relit chaque paire), donc on ne l'applique qu'aux
30 meilleurs candidats. Son score, ramené entre 0 et 1, sert aussi de signal de confiance
pour la porte d'abstention.
"""


class Reranker:
    def __init__(self, nom, longueur_max=512):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.tok = AutoTokenizer.from_pretrained(nom)
        self.modele = AutoModelForSequenceClassification.from_pretrained(nom, dtype=dtype).to(self.device).eval()
        self.longueur_max = longueur_max

    def scores(self, question, passages, batch=16):
        """Un score entre 0 et 1 par passage (sigmoïde du score brut du modèle)."""
        resultats = []
        for i in range(0, len(passages), batch):
            lot = self.tok([question] * len(passages[i:i + batch]), passages[i:i + batch], padding=True,
                           truncation=True, max_length=self.longueur_max, return_tensors="pt").to(self.device)
            with self.torch.no_grad():
                logits = self.modele(**lot).logits.view(-1).float()
            resultats.extend(self.torch.sigmoid(logits).cpu().tolist())
        return resultats
