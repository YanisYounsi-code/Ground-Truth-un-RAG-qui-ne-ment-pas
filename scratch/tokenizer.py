"""Palier 1 : découpe un texte en mots comparables entre la question et les pages."""

import re
import unicodedata

# Mots trop fréquents pour aider à distinguer les pages (écrits sans accents).
MOTS_VIDES = {
    "le",
    "la",
    "les",
    "l",
    "un",
    "une",
    "des",
    "de",
    "du",
    "d",
    "et",
    "ou",
    "en",
    "au",
    "aux",
    "a",
    "ce",
    "ces",
    "cet",
    "cette",
    "il",
    "elle",
    "ils",
    "elles",
    "on",
    "se",
    "sa",
    "son",
    "ses",
    "leur",
    "leurs",
    "qui",
    "que",
    "qu",
    "quoi",
    "dont",
    "ne",
    "pas",
    "par",
    "pour",
    "sur",
    "dans",
    "avec",
    "sans",
    "est",
    "sont",
    "plus",
    "y",
    "s",
    "n",
    "c",
    "j",
    "m",
    "t",
    "ete",
    "etre",
}


def tokenize(texte):
    """Minuscules, accents retirés, découpage sur tout ce qui n'est ni lettre ni chiffre."""
    texte = texte.lower()
    texte = unicodedata.normalize("NFKD", texte)  # "é" devient "e" + accent séparé
    texte = "".join(
        c for c in texte if not unicodedata.combining(c)
    )  # on jette les accents
    mots = re.findall(r"[a-z0-9]+", texte)
    return [m for m in mots if m not in MOTS_VIDES]


if __name__ == "__main__":
    print(tokenize("Les dépenses de santé ont augmenté"))
    print(tokenize("D'après l'Insee, combien de pharmacies en 2022 ?"))
