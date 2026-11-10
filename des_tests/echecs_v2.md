# 8 réponses ratées commentées

22 questions perdent des points sur 40 (runs/val2.json).

## 1. val2-001 (temporel, réponse fausse, -1)

- **Question** : Supermarchés, hypers, épiceries, surgelés : de combien les quantités vendues aux particuliers par les magasins d'alimentation ont-elles augmenté en 2024, selon le chiffre le plus à jour ?
- **Réponse attendue** : Selon l'estimation révisée (compte du commerce 2025), les ventes au détail du commerce alimentaire en magasin ont progressé de 0,8 % en volume en 2024.
- **Réponse du système** : En 2024, les supermarchés ont vu leurs ventes augmenter de +2,2 % en volume, tandis que les petites surfaces d’alimentation générale et magasins de produits surgelés ont connu un rebond de +4,4 % en volume.

Les hypermarchés ont enregistré un repli de -0,5 % en volume.


- **Pages de preuve** : insee-ip2111 p.2
- **Top 5 retrouvé** : insee-ip2058 p.3, insee-ip2111 p.2, insee-ip2058 p.2, insee-ip2111 p.3, insee-ip2058 p.1
- **Cause** : échec de génération
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_

## 2. val2-002 (texte, abstention, +0)

- **Question** : Sur la décennie allant jusqu'au début de 2024, de combien a augmenté l'impôt sur les propriétés bâties acquitté par les ménages qui occupent leur propre bien ?
- **Réponse attendue** : La taxe foncière payée par les propriétaires occupants a augmenté de 50 % en dix ans, entre début 2014 et début 2024, beaucoup plus vite que les revenus (+25 %).
- **Réponse du système** : INTROUVABLE
- **Pages de preuve** : insee-ip2128 p.1
- **Top 5 retrouvé** : cc-finances-locales-2026 p.40, cc-finances-locales-2026 p.201, cc-finances-locales-2026 p.212, insee-ip2105 p.3, cc-finances-locales-2026 p.213
- **Cause** : échec de recherche
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_

## 3. val2-003 (multi-doc, réponse fausse, -1)

- **Question** : D'après l'Insee, combien gagnaient en moyenne chaque mois les indépendants hors micro-entreprise en 2023, puis en 2024, et de combien d'euros ce revenu a-t-il augmenté d'une année sur l'autre ?
- **Réponse attendue** : Les non-salariés classiques perçoivent en moyenne 4 040 euros par mois en 2023 et 4 150 euros par mois en 2024, soit 110 euros de plus.
- **Réponse du système** : En 2023, les indépendants hors micro-entreprise (non-salariés classiques hors agriculture) percevaient en moyenne 4 150 euros par mois en euros constants.
En 2024, ce revenu était de 4 150 euros par mois (inchangé en euros constants), sans variation entre les deux années.
- **Pages de preuve** : insee-ip2060 p.1, insee-ip2060 p.2, insee-ip2114 p.1, insee-ip2114 p.2
- **Top 5 retrouvé** : insee-ip2114 p.3, insee-ip2114 p.1, insee-ip2060 p.3, insee-ip2060 p.2, insee-ip2114 p.2
- **Cause** : échec de génération
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_

## 4. val2-005 (temporel, réponse fausse, -1)

- **Question** : Trace the successive estimates of France's 2023 economic growth in Insee's annual national accounts: by how much was the figure revised upward with each new release?
- **Réponse attendue** : La croissance du PIB de 2023 a été relevée deux fois : à +1,4 % en mai 2025 (+0,5 point par rapport à l'estimation de mai 2024, qui était donc d'environ 0,9 %), puis à +1,6 % en mai 2026 (+0,2 point).
- **Réponse du système** : En 2023, la croissance du PIB en volume a été révisée comme suit :
- Première estimation (comptes trimestriels) : +1,1 % (estimée lors du premier trimestre 2025).
- Compte semi-définitif : +1,4 % (+0,5 point de révision).
- Compte définitif : +1,4 % (inchangé par rapport au semi-définitif dans les extraits fournis).
- **Pages de preuve** : insee-ip2053 p.4, insee-ip2053 p.1, insee-ip2077 p.2, insee-ip2105 p.4, insee-ip2105 p.1, insee-ip2112 p.1
- **Top 5 retrouvé** : insee-ip2053 p.4, insee-ip2053 p.1, insee-ip2053 p.3, insee-ip2063 p.1, insee-ip2097 p.4
- **Cause** : échec de recherche
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_

## 5. val2-006 (multi-doc, abstention, +0)

- **Question** : Selon le compte provisoire de l'agriculture établi par l'Insee, combien les exploitants devraient-ils percevoir en 2025 de subventions d'exploitation, et selon la Cour des comptes, combien la politique agricole européenne verse-t-elle chaque année en France sur 2023-2027 ?
- **Réponse attendue** : D'après le compte provisoire de l'agriculture, les subventions d'exploitation atteindraient 8,0 milliards d'euros en 2025 ; selon la Cour, la PAC déploie plus de 9 Md€ de financements européens par an de 2023 à 2027 (près de 56 % des subventions publiques à l'agriculture).
- **Réponse du système** : INTROUVABLE
- **Pages de preuve** : insee-ip2116 p.4, insee-ip2116 p.2, cc-pac p.9, cc-pac p.14, cc-pac-synthese p.3, cc-pac-synthese p.5, cc-pac-synthese p.6
- **Top 5 retrouvé** : cc-pac p.14, cc-pac p.9, cc-pac-synthese p.5, cc-pac-synthese p.6, insee-ip2062 p.4
- **Cause** : échec de recherche
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_

## 6. val2-014 (texte, réponse fausse, -1)

- **Question** : Selon les comptes nationaux 2025, à combien se monte le déficit commercial de la France en 2025 ?
- **Réponse attendue** : En 2025, la balance commerciale de la France est déficitaire de 14,4 milliards d'euros, une dégradation de 3,7 Md€ après -10,7 Md€ en 2024.
- **Réponse du système** : Selon les comptes nationaux 2025, le déficit commercial de la France s’améliore à -3,7 milliards d’euros (Md€) en 2025.
- **Pages de preuve** : insee-ip2105 p.3
- **Top 5 retrouvé** : insee-ip2053 p.3, insee-ip2105 p.3, cc-rspfp-2026 p.38, cc-finances-locales-2026 p.9, cc-rspfp-2026 p.25
- **Cause** : échec de génération
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_

## 7. val2-015 (graphique, réponse fausse, -1)

- **Question** : En 2024, hors énergies renouvelables et économies d'énergie, sur quel enjeu environnemental les usines ont-elles mis le plus d'argent en équipements antipollution ?
- **Réponse attendue** : Hors énergies renouvelables et économies d'énergie, c'est la protection de l'air et du climat qui arrive en tête des investissements antipollution de l'industrie en 2024, avec environ 330 millions d'euros, devant les eaux usées (environ 295 millions).
- **Réponse du système** : En 2024, hors énergies renouvelables et économies d’énergie, les usines ont investi le plus dans la protection de l’air et du climat (notamment les équipements limitant les émissions polluantes), avec un montant total de 2,7 milliards d’euros pour les investissements spécifiques antipollution.
- **Pages de preuve** : insee-ip2124 p.2
- **Top 5 retrouvé** : insee-ip2124 p.2, insee-ip2124 p.3, insee-ip2124 p.4, insee-ip2124 p.1, insee-ip2071 p.1
- **Cause** : échec de génération
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_

## 8. val2-024 (tableau, réponse fausse, -1)

- **Question** : Selon le compte des administrations publiques 2025 de l'Insee, combien les collectivités et organismes publics locaux ont-ils encaissé au total en 2025, et quelle progression sur un an ?
- **Réponse attendue** : En 2025, les recettes des administrations publiques locales s'élèvent à 319,9 milliards d'euros, en hausse de 2,3 % par rapport à 2024.
- **Réponse du système** : En 2025, les administrations publiques locales (collectivités territoriales et organismes divers d’administration locale) ont encaissé un total de 15,6 Md€ en déficit (recettes inférieures aux dépenses), soit une amélioration de -2,2 Md€ par rapport à 2024 (déficit de 17,8 Md€).
Les données précises sur les recettes brutes ne sont pas explicitement fournies dans les extraits, mais le déficit global des APUL s’est réduit de 2,2 Md€ en un an.
- **Pages de preuve** : insee-ip2106 p.3
- **Top 5 retrouvé** : insee-ip2106 p.4, insee-ip2106 p.1, cc-finances-locales-2026 p.24, insee-ip2054 p.1, insee-ip2106 p.3
- **Cause** : échec de génération
- **Commentaire** : _à rédiger : pourquoi ça a raté, et quelle brique pourrait le corriger_
