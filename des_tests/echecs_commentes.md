# 5 réponses ratées, commentées (RAG de base du palier 1, validation v1)

Source : `runs/val1_rag_base.json`, BM25 sur les pages + Ministral-3-3B, sans reranker ni porte d'abstention.
58 questions sur 100 perdent des points. Les 5 cas ci-dessous couvrent les trois causes possibles :
recherche (la bonne page n'est pas dans le contexte), génération (elle y est mais le modèle se trompe),
et le cas particulier des scans non lus.

| # | Question | Type | Points | Cause | Brique qui corrige |
|---|---|---|---|---|---|
| 1 | val1-001 exploitants PAC 2022/2023 | texte | -1 | recherche + mauvaise abstention | recherche dense (bge-m3) + détection des non-réponses |
| 2 | val1-003 pharmacies 2022 et 2015 | scan | 0 | page jamais lue | OCR Tesseract **en français** |
| 3 | val1-004 leçons zone euro | synthèse | -1 | génération | plus de passages (6 chunks) + reranker |
| 4 | val1-006 cours spot / barème | graphique | -1 | génération (chiffres dans l'image) | porte d'abstention calibrée |
| 5 | val1-007 longévité selon les revenus | synthèse | 0 | recherche (vocabulaire) | recherche dense + RRF |

## 1. val1-001 : « Combien d'exploitants touchaient les paiements européens en 2022 puis en 2023… »

- **Attendu** : de 308 000 à 276 600 bénéficiaires (cc-pac p.25).
- **Obtenu** : « En réalité, les extraits ne mentionnent pas explicitement… » suivi de chiffres hors sujet (cc-pac p.47).
- **Pourquoi ça rate** : la page de preuve parle de « bénéficiaires » et d'« agriculteur actif », la question
  d'« exploitants » et de « paiements européens ». BM25 ne compte que les mots identiques : il n'y a presque
  aucun mot en commun, donc la page 25 n'est pas dans le top 5. Ensuite, le modèle a bien compris qu'il n'avait
  pas l'information, mais au lieu d'écrire INTROUVABLE il a appliqué la règle « En réalité, » du prompt. Le
  barème le compte comme une réponse fausse : -1 au lieu de 0.
- **Ce qui corrige** : (a) la recherche dense bge-m3 rapproche les synonymes (exploitant ≈ bénéficiaire) ;
  (b) depuis le 10/11, la règle « En réalité » est réservée aux affirmations fausses explicites, et
  `lire_reponse` transforme toute phrase du type « les extraits ne mentionnent pas » en INTROUVABLE.

## 2. val1-003 : « D'après l'Insee, combien de pharmacies y avait-il en 2022, et en 2015 ? »

- **Attendu** : 22 700 officines en 2022, 23 400 en 2015 (insee-ip2036 p.2).
- **Obtenu** : INTROUVABLE (0 point, pas de pénalité).
- **Pourquoi ça rate** : insee-ip2036 est un **scan** : pymupdf n'y trouve aucun texte, la page est vide dans
  l'index, BM25 ne peut pas la trouver. Le modèle n'invente rien et s'abstient : c'est le bon comportement
  quand la preuve manque.
- **Ce qui corrige** : l'OCR des pages de moins de 50 caractères (palier 2). Sur Colab il a d'abord tourné en
  **anglais** (le paquet `tesseract-ocr-fra` n'était pas installé) : les accents et les nombres
  « 22 700 » sont mal lus. `setup.sh` installe maintenant le français s'il manque.

## 3. val1-004 : « Quelles leçons la Cour tire-t-elle des pays qui ont réussi à assainir leurs comptes ? »

- **Attendu** : quatre enseignements (consolidation choisie, mesures peu coûteuses + croissance, cadre
  institutionnel, mesures de crise temporaires).
- **Obtenu** : trois leçons ; les deux premières sont justes, la troisième (« combiner approches quantitative
  et narrative ») est une remarque de méthode, pas une leçon.
- **Pourquoi ça rate** : la recherche est bonne (p.20 au rang 1), mais la réponse est répartie sur 6 pages.
  Avec seulement les premières pages dans le contexte, le modèle n'a vu qu'une partie de la liste et a comblé
  le trou avec un autre passage. C'est un **échec de génération** dû à un contexte incomplet.
- **Ce qui corrige** : le chunking par structure garde un intertitre et sa liste ensemble ; le reranker fait
  remonter p.21 et la synthèse p.19-20 ; on passe 6 chunks (≈ 3 000 tokens) au lieu de pages entières
  tronquées. Limite qui reste : un modèle de 3 B résume mal une liste longue.

## 4. val1-006 : « Quelle année le cours spot a-t-il le moins dépassé le barème ? »

- **Attendu** : 2023 (moins de 1 000 heures).
- **Obtenu** : « En réalité, 2024… selon les données du graphique ».
- **Pourquoi ça rate** : la page de preuve est trouvée au rang 1, mais la réponse est **dans un graphique** :
  le texte extrait ne contient que le titre et les axes, pas la hauteur des barres. Le modèle n'a donc aucun
  chiffre et devine. Le « En réalité, » est en plus injustifié : la question n'affirmait rien.
- **Ce qui corrige** : rien dans notre pipeline ne lit les images (il faudrait un modèle vision, trop lourd
  pour le budget). La bonne stratégie est de **s'abstenir** : 0 au lieu de -1. C'est le rôle de la porte
  d'abstention calibrée et de la règle « En réalité » restreinte.

## 5. val1-007 : « Riches et pauvres face à la mort : que montre l'Insee sur la longévité selon les revenus ? »

- **Attendu** : l'espérance de vie croît avec le niveau de vie ; 17 ans d'écart ; risque × 7 à 50 ans…
  (insee-ip2085 p.1-3).
- **Obtenu** : INTROUVABLE.
- **Pourquoi ça rate** : la question dit « longévité », « riches », « pauvres », « revenus » ; le document dit
  « espérance de vie », « aisés », « modestes », « niveau de vie ». Zéro mot commun utile : BM25 ramène des
  pages sur d'autres sujets (ip2063, cc-pac). Le modèle s'abstient correctement.
- **Ce qui corrige** : la recherche dense (bge-m3 sait que longévité ≈ espérance de vie) fusionnée avec BM25
  par RRF, puis le reranker. C'est l'exemple le plus parlant pour justifier la recherche hybride.

## Ce que ces 5 cas m'ont appris

1. **Deux échecs sur cinq viennent du vocabulaire** : BM25 seul ne suffit pas, d'où la recherche hybride.
2. **Une abstention vaut mieux qu'une réponse devinée** : trois cas sur cinq coûtent -1 parce que le modèle
   répond sans preuve. D'où la porte d'abstention et le nettoyage des non-réponses.
3. **Les scans et les graphiques** sont des angles morts : l'OCR règle les scans, rien ne règle les graphiques
   dans notre budget, donc on vise l'abstention sur ces questions.
