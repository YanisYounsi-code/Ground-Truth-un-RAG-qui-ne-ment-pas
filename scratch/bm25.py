"""Palier 1 : BM25 (Okapi) codé à la main, avec un index inversé."""

import math
from collections import Counter, defaultdict


class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1  # saturation : au-delà de quelques occurrences, un mot n'apporte presque plus rien
        self.b = b  # normalisation par la longueur : une page longue est pénalisée

    def index(self, docs_tokens):
        """docs_tokens : une liste de listes de mots, un élément par document (page ou chunk)."""
        self.n_docs = len(docs_tokens)
        self.longueurs = [len(toks) for toks in docs_tokens]
        self.longueur_moy = sum(self.longueurs) / self.n_docs
        # Index inversé : mot -> {numéro du document: nombre d'occurrences}
        self.inverse = defaultdict(dict)
        for i, toks in enumerate(docs_tokens):
            for mot, tf in Counter(toks).items():
                self.inverse[mot][i] = tf
        # IDF : un mot présent dans peu de documents pèse lourd
        self.idf = {}
        for mot, postings in self.inverse.items():
            df = len(postings)
            self.idf[mot] = math.log(1 + (self.n_docs - df + 0.5) / (df + 0.5))

    def scores(self, requete_tokens):
        """Score BM25 de chaque document qui contient au moins un mot de la requête."""
        scores = defaultdict(float)
        for mot in requete_tokens:  # un mot répété dans la question compte deux fois
            if mot not in self.inverse:
                continue
            for i, tf in self.inverse[mot].items():
                norme = 1 - self.b + self.b * self.longueurs[i] / self.longueur_moy
                # Variante Lucene : sans le facteur (k1 + 1) de la formule d'origine. Il multiplie
                # tous les scores par la même constante, donc le classement ne change pas.
                scores[i] += self.idf[mot] * tf / (tf + self.k1 * norme)
        return scores

    def search(self, requete_tokens, k=10):
        """Les k meilleurs documents, sous forme de liste [(numéro, score)] triée."""
        scores = self.scores(requete_tokens)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
