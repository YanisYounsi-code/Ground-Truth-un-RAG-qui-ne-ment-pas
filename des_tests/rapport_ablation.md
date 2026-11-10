# Rapport d'ablation : Ground Truth (2 pages max)

Yanis Younsi · dépôt YanisYounsi-code/Ground-Truth-un-RAG-qui-ne-ment-pas

> Chiffres produits par `notebooks/paliers_1_2_colab.ipynb` sur Colab T4 (10/11) ; rapports d'évaluation
> officiels dans `des_tests/rapports/`. Soumission v1 : `submissions/v1/2026-11-10_1.json`.

## 1. Le pipeline complet

Pour chaque question : recherche BM25 (codé à la main) et dense (bge-m3, cosinus en NumPy) sur des
chunks contextuels, fusion RRF, reranker bge-reranker-v2-m3 sur les 30 meilleurs, porte
d'abstention sur le score du meilleur passage, puis un seul appel au générateur avec 6 passages
au plus (3 000 tokens). L'indexation lit le texte avec PyMuPDF, réécrit les tableaux en Markdown
et passe les 97 pages scannées par Tesseract.

| Système (validation v1, 100 questions) | Score de confiance | Hallucinations | Abstentions |
|---|---|---|---|
| Toujours INTROUVABLE | +0,23 | 0 % | 100 % |
| RAG de base (palier 1 : BM25 sur les pages, sans OCR) | −0,04 (`des_tests/rapports/val1_rag_base_report.json`) | 46 % | 26 % |
| Pipeline complet, premier prompt, sans porte | +0,135 (`des_tests/rapports/val1_complet_sansporte_report.json`) | 43 % | 15 % |
| **Pipeline final : prompt corrigé + vérification de la réponse** | **+0,38** (`des_tests/rapports/val1_complet_report.json`) | 22 % | 37 % |

## 2. Ce que chaque brique apporte à la recherche

Une brique retirée à la fois, sur les 77 questions de validation v1 qui ont une réponse
(`des_tests/ablation_recherche.md`, Colab T4, 10/11). R@5 = part des groupes de preuve dont une page
est dans les 5 premières pages retrouvées. Une question de plus ou de moins = environ 0,013 de R@5.

| Configuration | R@5 | R@10 | MRR | R@5 scan | R@5 multi-doc | Effet de la brique |
|---|---|---|---|---|---|---|
| **Complet** (hybride + reranker, chunks contextuels) | **0,909** | 0,948 | **0,799** | 0,89 | 0,60 | référence |
| Sans reranker | 0,857 | 0,935 | 0,686 | 0,89 | 0,80 | reranker : +5 pts de R@5, **+11 pts de MRR** |
| Sans dense (BM25 seul) | 0,857 | 0,903 | 0,747 | 0,89 | 0,60 | dense : +5 pts de R@5, surtout sur les tableaux (0,76 → 0,88) |
| Sans BM25 (dense seul) | 0,903 | 0,948 | 0,794 | 0,89 | 0,70 | BM25 : +0,6 pt seulement, dans le bruit |
| Chunking structure (sans en-tête) | 0,935 | 0,961 | 0,781 | 0,89 | 0,60 | l'en-tête ne gagne rien en R@5 (−2 questions), +2 pts de MRR |
| Chunking naïf (250 mots) | 0,929 | 0,961 | 0,761 | 0,89 | 0,70 | le découpage compte peu pour la recherche |
| Sans OCR | 0,799 | 0,818 | 0,709 | **0,11** | 0,70 | **OCR : +11 pts de R@5, scans de 0,11 à 0,89** |
| Sans tableaux Markdown | 0,909 | 0,948 | 0,798 | 0,89 | 0,60 | aucun effet sur la recherche |

Pour comparaison, le BM25 du palier 1 sur des pages entières faisait R@5 = 0,610 et MRR = 0,454.

Ce que j'en retiens :

- **L'OCR est la brique la plus rentable** : sans elle, 8 questions sur 9 portant sur un scan sont
  perdues d'avance, car leur page est vide dans l'index.
- **Le reranker sert surtout à bien classer** : il change peu le R@10, mais fait monter la bonne page
  en tête (MRR 0,686 → 0,799). C'est ce qui compte, puisque seuls 6 passages entrent dans le prompt.
- **La recherche dense fait le gros du travail** et BM25 n'ajoute presque rien en moyenne. Je le
  garde quand même : il coûte quelques secondes et il est fiable sur les noms propres et les
  chiffres exacts.
- **Les écarts entre découpages (2 questions sur 77) sont dans le bruit.** Je garde les chunks
  contextuels, pour leur meilleur MRR et parce que le seuil a été calibré avec eux ; je revérifierai
  sur la validation v2.
- **Les tableaux en Markdown n'aident pas à retrouver la page** : leur effet est à mesurer sur la
  génération (lecture des chiffres sur la bonne ligne, section 3).
- **Le point faible est le multi-doc** (R@5 = 0,60) : il faut retrouver deux documents à la fois et
  les 5 premières places sont souvent prises par le même. Sans reranker, ce score monte à 0,80 :
  probablement parce que le reranker fait remonter plusieurs passages du document le plus pertinent.
  Piste : garder au moins un passage de chaque document dans le top 5. Ce sont peu de questions
  (une de plus = +0,10), donc à confirmer sur la validation v2.

Au palier 1, la racinisation légère du tokeniseur a fait passer le R@10 du BM25 sur les pages de
0,636 à 0,727 (`des_tests/journal.md`).

## 3. Parsing : 22 pages annotées, 42 valeurs

Pages de preuve de la validation (10 tableaux, 10 graphiques, 10 scans ; 8 pages sans valeur
lisible sont écartées). Pour chaque valeur : la valeur exacte et son libellé (le nom de la ligne du
tableau, du segment du graphique). Libellés repris de la citation source de la validation. Chaque
valeur a été vérifiée : 38 sont retrouvées telles quelles dans le texte d'au moins un parseur, les 4
qui ne figurent que dans l'image d'un graphique (cc-informatique-quantique p.39 et p.88) ont été
lues sur l'image de la page. Résultat : `des_tests/parsing_resultats.md`.

| Parseur | Tableau : valeurs / liens | Graphique : valeurs / liens | Scan : valeurs / liens |
|---|---|---|---|
| PyMuPDF brut | 100 % / 0 % | 43 % / 0 % | 0 % / 0 % |
| **PyMuPDF + tableaux en Markdown** | 100 % / **85 %** | 43 % / 0 % | 0 % / 0 % |
| Tesseract (OCR, français) | 80 % / 40 % | 0 % / 0 % | **100 % / 53 %** |

*Valeurs* : la valeur est dans le texte extrait. *Liens* : elle est sur la même ligne que son libellé.

- **Sur les tableaux, PyMuPDF trouve tous les chiffres mais casse le lien avec leur ligne** : il lit
  colonne par colonne, et « 11,3 » se retrouve loin de « Vin ». Réécrits en Markdown, 85 % des
  chiffres sont sur la ligne de leur libellé : c'est ce qui permet au modèle de savoir à quoi
  correspond un nombre. D'où le choix de `pymupdf_tables`, même si la recherche ne change pas
  (section 2) : le gain est pour la lecture, pas pour trouver la page.
- **Sur les scans, seul l'OCR lit quelque chose** ; il est appliqué uniquement aux pages sans texte
  (moins de 50 caractères), car sur les pages normales il est moins bon que PyMuPDF (80 % contre 100 %
  sur les tableaux) et beaucoup plus lent.
- **Les graphiques restent un angle mort** : moins de la moitié des valeurs sont imprimées en texte,
  et jamais à côté de leur libellé. Sur ces questions, la bonne stratégie est l'abstention (section 4).

## 4. Abstention : la porte sur le score du reranker ne marche pas, la vérification de la réponse oui

Barème : +1 juste et cité, −1 faux, 0 abstention (+1 sur une question piège). Répondre ne rapporte
donc en moyenne que si la réponse est juste plus d'une fois sur deux.

| Validation v1 (100 questions) | Score | Justes | Fausses | Abstentions |
|---|---|---|---|---|
| Toujours INTROUVABLE | +0,23 | 0 | 0 | 100 |
| Pipeline complet, premier prompt, sans porte (`val1_complet_sansporte`) | +0,135 | 37 | 39 | 15 |
| Porte sur le score du reranker, meilleur seuil (0,9996) | +0,26 | presque aucune réponse | | |
| Prompt corrigé + non-réponses converties (`val1_complet`) | +0,24 | 41 | 32 | 20 |
| + vérification des chiffres et des aveux d'incertitude (`val1_complet`, relancé le 10/11) | **+0,38** | 39 | 20 | 37 |

**Pourquoi la porte ne marche pas.** Le score du reranker dit si le bon passage a été trouvé ; il l'est
9 fois sur 10 (R@5 = 0,91). Mes erreurs viennent de la **génération** : le modèle a la bonne page
mais lit mal un tableau, calcule faux ou devine la valeur d'un graphique. Le score est alors élevé
quand même, et la courbe de calibration (`des_tests/calibration.png`) monte jusqu'à « toujours
s'abstenir ». Un tel seuil revient à ne plus répondre : je ne l'ai pas gardé. La calibration ne
retient désormais un seuil que s'il gagne au moins 2 questions sur 100.

**Ce qui marche : vérifier la réponse elle-même**, sans appel supplémentaire au modèle :

1. *Non-réponses* : « les extraits ne mentionnent pas… », « INTROUVABLE » au milieu d'une phrase,
   « chiffre non explicitement donné » → INTROUVABLE (+0,06).
2. *Ancrage des chiffres* : chaque nombre de la réponse doit figurer dans un des extraits fournis ou
   dans la question, selon les règles de la notation officielle (arrondi de 0,5 %, « 2,6 millions »
   = « 2 600 000 »). Sinon, le modèle l'a inventé ou mal calculé → INTROUVABLE (+0,08 de plus). Exemples :
   val1-043 « diminué de 59 850 €/MW », val1-051 et val1-071 (pièges : 31,1 Mhl et 18 000 imprimeries
   obtenus par un calcul faux). Coût : 2 réponses justes perdues sur 39 (val1-036, un écart
   calculé ; val1-044).

Limite : ces règles ont été mises au point sur la validation v1 ; je les mesure sur la validation v2
pour vérifier qu'elles ne sont pas surajustées.

## 5. Où le système se trompe encore

22 réponses à −1 sur 100 avec le pipeline final (`des_tests/rapports/val1_complet_report.json`).
Dans presque tous les cas, la page de preuve était dans le contexte : **ce sont des erreurs de
lecture, pas de recherche**.

| Cause | Questions | Exemple |
|---|---|---|
| Mauvaise case d'un tableau (le bon chiffre est dans l'extrait) | 7 : 020, 039, 043, 072, 075, 083, 100 | val1-100 : la moyenne 1 043 au lieu de la médiane 1 514, sur la même ligne |
| Graphique : la valeur n'est pas dans le texte, le modèle devine | 4 : 006, 041, 055, 060 | val1-006 : 2024 au lieu de 2023 |
| Synthèse incomplète (il manque des éléments de la liste) | 3 : 004, 068, 079 | val1-004 : 3 leçons sur 4, dont une inventée |
| Multi-doc : un seul des deux documents utilisé | 2 : 040, 058 | val1-040 : le chiffre du rapport algues vertes, pas celui du rapport PAC |
| Mauvais passage ou réponse partielle | 4 : 009, 064, 065, 086 | val1-009 : 23 M€ juste, mais il manque les 2,45 Md€ |
| Piège non détecté | 2 : 069, 093 | val1-093 : question sur 2025, le modèle répond avec 2024 |

La vérification des chiffres ne peut rien contre la première cause : le chiffre faux est bien dans
l'extrait, simplement pas à la bonne case. C'est la limite principale d'un modèle de 3 milliards de
paramètres face à un tableau. Pistes pour le palier 3, sans changer de générateur :
- utiliser un 2ᵉ appel (le budget en autorise 4) pour faire relire la réponse : « quelle ligne et
  quelle colonne du tableau donnent ce chiffre ? » ;
- sur les questions de type graphique (mots « graphique », « courbe », « quelle année a vu le plus… »),
  exiger que la valeur soit écrite dans l'extrait, sinon s'abstenir ;
- multi-doc : garder au moins un passage de chacun des deux meilleurs documents.

## 6. Les briques qui ne servent à rien (ou presque)

| Brique | Effet mesuré | Décision |
|---|---|---|
| Porte d'abstention sur le score du reranker | meilleur seuil = presque tout refuser (section 4) | **retirée** (`threshold: null`) |
| BM25 dans la recherche hybride | +0,006 de R@5 par rapport au dense seul | gardée : coûte quelques secondes, utile sur les noms et chiffres exacts |
| En-tête de contexte dans les chunks | −0,026 de R@5, +0,018 de MRR (2 questions sur 77) | gardée par défaut, dans le bruit ; à revoir sur la validation v2 |
| Tableaux en Markdown, pour la recherche | 0 sur R@5 | gardés : +85 points de liens valeur-libellé (section 3), utiles à la lecture |
| OCR sur les pages qui ont déjà du texte | moins bon que PyMuPDF (80 % contre 100 % des valeurs sur les tableaux) | non utilisé : OCR seulement sous 50 caractères |

Ce qui compte vraiment : l'OCR des scans (+11 points de R@5), le reranker (+11 points de MRR), la
recherche dense (+5 points de R@5) et, côté génération, la vérification de la réponse (+0,14 de
score de confiance).
