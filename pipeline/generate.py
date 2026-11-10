"""Génération : porte d'abstention, assemblage du contexte, appel au générateur officiel, citations.

Un seul appel au générateur par question (le budget en autorise 4) : chaque appel plein coûte
environ 9 s sur T4, et la porte d'abstention en économise sur les questions sans bonne preuve.
"""
import json
import re
import time
from pathlib import Path

from . import settings

ABSTENTION = "INTROUVABLE"
LIMITE_ENTREE = 4096
MARGE = 32  # tokens de sécurité sous la limite officielle

SYSTEME = (
    "Tu réponds à des questions sur des rapports publics français (Insee, Cour des comptes), "
    "uniquement à partir des extraits fournis. Chaque extrait commence par sa référence "
    "[doc_id p.N] et sa date de publication.\n"
    "Règles :\n"
    "1. Si les extraits ne permettent pas de répondre avec certitude, réponds exactement : INTROUVABLE\n"
    "2. Recopie les chiffres exactement comme dans les extraits, avec leur unité et leur année.\n"
    "3. Uniquement si la question affirme explicitement un fait que les extraits contredisent "
    "(par exemple une baisse alors que les extraits montrent une hausse), commence par « En réalité, » "
    "et corrige l'affirmation avec les chiffres des extraits. Si les extraits ne contiennent simplement "
    "pas l'information, réponds INTROUVABLE, sans rien ajouter.\n"
    "4. Si deux extraits donnent des chiffres différents pour la même chose, retiens le plus récent "
    "(date de publication la plus tardive).\n"
    "5. Réponds en une à trois phrases, dans la langue de la question.\n"
    "6. Termine par une dernière ligne au format : SOURCES: [doc_id p.N], [doc_id p.N]"
)


def extrait(p):
    date = f" · publié le {p['date']}" if p.get("date") else ""
    return f"[{p['doc_id']} p.{p['page']}{date}]\n{p['text']}"


def messages(question, passages):
    contexte = "\n\n".join(extrait(p) for p in passages)
    return [{"role": "system", "content": SYSTEME},
            {"role": "user", "content": f"Extraits :\n\n{contexte}\n\nQuestion : {question}"}]


def assembler(gen, question, passages, reglages):
    """Ajoute les meilleurs passages un par un tant que le prompt tient dans le budget de tokens."""
    budget = min(LIMITE_ENTREE - MARGE, reglages["context_tokens"] + 400)  # 400 = consignes + question
    retenus = []
    for p in passages[: reglages["context_chunks"]]:
        if gen.count_tokens(messages(question, retenus + [p])) > budget:
            break
        retenus.append(p)
    if not retenus and passages:  # garde au moins le meilleur passage, raccourci si besoin
        p = dict(passages[0])
        while gen.count_tokens(messages(question, [p])) > LIMITE_ENTREE - MARGE:
            p["text"] = p["text"][: int(len(p["text"]) * 0.8)]
        retenus = [p]
    return retenus


# Formulations par lesquelles le modèle avoue ne pas trouver l'information (vues sur la validation v1)
NON_REPONSE = re.compile(
    r"(les |ces )?extraits (fournis )?(ne |n')(mentionne|contien|permett|precis|donne|fourni|indiqu|presente|traite)"
    r"|aucun(e)? (information|donnee|chiffre|mention|element|indication)"
    r"|(ne sont|n'est) pas (directement |explicitement |clairement |precisement )?"
    r"(mentionne|disponible|precise|indique|fourni|present|calculable|donne)"
    r"|(donnees|chiffres|informations|documents) (disponibles |fournis |de la cour des comptes |de l'insee )?"
    r"(ne |n')(permett|distingu|precis|mention|fourni|indiqu|donne|couvr)"
    r"|pas d'information|impossible de (repondre|determiner|preciser)|je ne (peux|dispose) pas"
)


def _sans_accents(texte):
    import unicodedata

    texte = unicodedata.normalize("NFKD", texte.lower().replace("\u2019", "'"))
    return "".join(c for c in texte if not unicodedata.combining(c))


def lire_reponse(brut, retenus):
    """Sépare la réponse de la ligne SOURCES et ne garde que les citations présentes dans le contexte."""
    texte = brut.strip()
    reponse = re.split(r"\n?\s*SOURCES\s*:", texte, flags=re.IGNORECASE)[0].strip()
    reponse = reponse.replace("**", "")  # gras Markdown : inutile pour le juge, gêne la lecture des chiffres
    if reponse.strip(" .").upper() == ABSTENTION or texte.upper().startswith(ABSTENTION):
        return ABSTENTION, []
    if NON_REPONSE.search(_sans_accents(reponse[:300])):
        # Le modèle explique qu'il n'a pas l'information au lieu d'écrire INTROUVABLE : noté comme une
        # réponse fausse (-1) alors qu'une abstention vaut 0 ou +1. On la convertit en abstention.
        return ABSTENTION, []
    disponibles = {(p["doc_id"], p["page"]) for p in retenus}
    citations = []
    for doc_id, page in re.findall(r"\[([\w\-]+)\s+p\.?\s*(\d+)", texte):
        cle = (doc_id, int(page))
        if cle in disponibles and cle not in citations:
            citations.append(cle)
    if not citations and retenus:  # le modèle n'a pas cité : on cite le passage le mieux classé
        citations.append((retenus[0]["doc_id"], retenus[0]["page"]))
    return reponse, [{"doc_id": d, "page": p} for d, p in citations[:5]]


def answer_all(retrieval_path, questions_path, out_path, backend="hf", gate=True):
    from groundtruth.generator import OfficialGenerator
    from groundtruth.io import load_questions, write_predictions

    t0 = time.time()
    reglages = settings.load()
    seuil = reglages.get("threshold") if gate else None
    recherche = json.loads(Path(retrieval_path).read_text(encoding="utf-8"))
    gen = OfficialGenerator(backend=backend)
    predictions = []
    for q in load_questions(questions_path):
        r = recherche[q["qid"]]
        pred = {"qid": q["qid"], "retrieved": r["retrieved"], "score": r["top_score"]}
        if seuil is not None and r["top_score"] is not None and r["top_score"] < seuil:
            pred.update(answer=ABSTENTION, citations=[], gate="abstention")  # aucun appel au LLM
        else:
            gen.start_question(q["qid"])
            retenus = assembler(gen, q["question"], r["passages"], reglages)
            brut = gen.chat(messages(q["question"], retenus), max_new_tokens=reglages["max_new_tokens"])
            reponse, citations = lire_reponse(brut, retenus)
            pred.update(answer=reponse, citations=citations, raw=brut)
        predictions.append(pred)
        print(f"{q['qid']}: {pred['answer'][:90]}")
    write_predictions(out_path, predictions, run_name=f"pipeline seuil={seuil}")
    n = len(predictions)
    print(f"[answer] {n} questions en {time.time() - t0:.0f} s ({(time.time() - t0) / max(n, 1):.1f} s / question)")
