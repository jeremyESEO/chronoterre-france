# Guide final ESEO — Exigence, preuve et résultat

Barème du guide **Projet final Architecture BD et collecte de données**, p. 9, remise du 8 novembre 2026. Cette matrice remplace le barème des TP repris dans le dossier de développement de 15 pages. Elle décrit les preuves, sans attribuer de note.

| Critère | Points | Preuve à ouvrir |
|---|---:|---|
| Cadrage et utilité | 3 | [README](../README.md), question d’installation, usager et comparaison de trois KPI définis ci-dessous |
| Sources et conformité | 2 | [Matrice des sources](sources_france.md), manifestes, médias attribués, [conditions DREAL originales](licence_dreal.md), collecte publique sans contournement |
| Collecte reproductible | 3 | `national/collect.py`, `data/raw/national_manifest.json`, raw daté, URL, SHA-256, accès PBDB vérifié, restauration sans réseau |
| Qualité et robustesse | 3 | `national/validate.py`, `data/rejected/`, [rapport de rejeu](../reports/france_idempotence.json), [incident et reprise](../reports/rendu_final_incident.json) |
| Transformation et produit | 3 | Schéma `sql/france_schema.sql`, SQLite restaurable, `dist/data/`, API locale et 18 analyses SQL ; [une occurrence jusqu’à sa fiche](lineage.md) |
| Architecture et ADR | 2 | [V1](architecture.png), [V2](architecture_v2.svg), [ADR 001](ADR_001.md) : fichiers seuls, SQLite et PostGIS comparés |
| Observabilité et gouvernance | 2 | [Rapport de run](../reports/france_run.json), identifiant et étapes, fraîcheur par source, [politique](gouvernance.md), [traçabilité](lineage.md) |
| Documentation et démonstration | 2 | README et déclaration IA, [déroulé de 6 minutes](soutenance_france.md), [preuves de vérification](../reports/rendu_final_verification.json), synthèse de 5 pages jointe séparément au rendu |
| **Total** | **20** | |

## Question, utilisateur et KPI

Une personne préparant un déménagement souhaite comparer deux communes aux mêmes horizons climatiques et repérer les vérifications locales nécessaires. Le parcours fossile met en valeur la traçabilité d’une autre famille de données ; il n’entre pas dans le classement climatique.

| KPI métier | Définition et unité | Usage |
|---|---|---|
| Jours très chauds (S1) | Nombre annuel selon le seuil producteur de 35 °C, jours/an | Comparer l’intensité du compromis estival à horizon constant |
| Nuits chaudes (S2) | Nombre annuel selon le seuil producteur de 20 °C, nuits/an | Distinguer la chaleur nocturne de celle de jour |
| Jours de gel (G2) | Minimum quotidien inférieur à 0 °C, jours/an | Rendre visible le compromis hiver-été |

Les définitions exactes du fournisseur et les fourchettes sont dans `indicator` et les fiches. Les mesures de couverture et de qualité sont distinctes : part des communes avec une fiche (SQL 01), dates d’approbation renseignées dans l’échantillon (SQL 11), occurrences liées à un média (SQL 15). Elles ne mesurent pas le risque d’un lieu. Le socle traite une page de 10 000 enregistrements PBDB réels ; la ligne invalide volontaire est séparée et exclue des compteurs réels.

## Checklist des preuves

- [x] Question, usager et trois KPI explicites ; périmètre et limites documentés.
- [x] Sources, dates et conditions documentées, y compris Toulouse à partir de la fiche originale.
- [x] Version livrée sans clé requise, `.env` ignoré ; contrôle des motifs usuels de secrets sur les fichiers texte du rendu. Ce contrôle ne certifie pas tous les binaires.
- [x] Grain, clé métier, [dictionnaire](dictionnaire_france.md) et [contrat France versionné](../config/france_contract.json) ; [contrat YAML V1](../config/data_contract.yaml).
- [x] Raw original, contrôles automatisés, rejets motivés, base et exports générés automatiquement.
- [x] Rejeu du contenu métier identique ; incident P01 testé avec journal d’échec et reprise.
- [x] Produit de consultation, rapports et architectures V1/V2, ADR et provenance d’une fiche.
- [x] README, déclaration IA, commandes reproduites et déroulé oral dans le créneau demandé.
- [x] Dépôt public et synthèse finale préparés. La répétition personnelle et la remise Moodle incombent à l’étudiant.
