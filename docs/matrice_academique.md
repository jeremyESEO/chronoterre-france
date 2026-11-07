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

## Les 20 cases du guide final, page 11

Les preuves décrivent le périmètre remis ; la validation du barème appartient à l’enseignant.

- [x] **01 — Problème, usager et KPI.** La question et les trois indicateurs ci-dessus structurent la synthèse et l’oral.
- [x] **02 — Sources et licences.** [Registre](sources_france.md), [images](media_registry.json), [conditions originales de la DREAL](licence_dreal.md), date et attribution dans l’application.
- [x] **03 — Secrets et données sensibles.** Sources publiques, essai invalide isolé, aucun secret requis ; le [contrôle de motifs](../reports/rendu_final_verification.json) n’a rien détecté dans le code, la configuration et la documentation texte examinés.
- [x] **04 — Grain et clé métier.** [Dictionnaire](dictionnaire_france.md) et [schéma SQL](../sql/france_schema.sql).
- [x] **05 — Raw original.** [Manifeste](../data/raw/national_manifest.json) ; `pbdb_occs_0` contient la page PBDB de 10 000 enregistrements, conservée avec URL et SHA-256.
- [x] **06 — Contrat versionné.** [France 2.0.1](../config/france_contract.json) et [YAML de la V1](../config/data_contract.yaml).
- [x] **07 — Règles automatiques.** 12 règles consignées dans le [rapport national](../reports/france_run.json), avec action et nombre d’échecs.
- [x] **08 — Rejets conservés et expliqués.** `data/rejected/france_rejects.jsonl` : 5 761 rejets motivés, toutes familles confondues ; le test invalide reste à part.
- [x] **09 — Rejeu sans doublons incorrects.** [Deux reconstructions](../reports/france_idempotence.json), mêmes clés et contenu métier.
- [x] **10 — Curated automatique.** `python -m national.pipeline` construit SQLite et les exports depuis les réponses archivées ; la base livrée se restaure aussi séparément.
- [x] **11 — Produit utile.** [Recherche, fiches et comparaison vérifiées](../reports/rendu_final_verification.json) avec valeurs, source et limites. Le rendu visuel en navigateur reste à vérifier.
- [x] **12 — Incident testé.** [Arrêt P01, conservation de la base stable et reprise](../reports/rendu_final_incident.json).
- [x] **13 — Rapport d’exécution.** [Run horodaté](../reports/france_run.json) : identifiant, contrat, métriques, durée, statut et alertes de fraîcheur.
- [x] **14 — Architectures V1 et V2.** [V1 Île-de-France](architecture.png), [V2 France](architecture_v2.svg) et [trajet d’une observation](lineage.md).
- [x] **15 — ADR.** [Décision motivée](ADR_001.md) : fichiers seuls, SQLite et PostGIS, conséquences et condition de réexamen.
- [x] **16 — README reproductible.** [Installation, commandes, limites et reprise](../README.md) ; le lanceur Windows reste à vérifier sur Windows.
- [x] **17 — Synthèse de 4 à 6 pages.** `Synthese_finale_ChronoTerre.pdf`, cinq pages vérifiées et fournies séparément ; le dossier de 15 pages est une annexe.
- [x] **18 — Usage de l’IA déclaré.** [README](../README.md#déclaration-dusage-de-lia), outil, tâches, vérifications et contribution personnelle.
- [x] **19 — Rejeu en environnement propre.** Clone et environnement Python isolés lors de l’audit, puis [rejeu du lot final](../reports/france_idempotence.json) ; [Actions](https://github.com/jeremyESEO/chronoterre-france/actions) vérifie la restauration et les tests sur un nouvel environnement.
- [x] **20 — Lien de remise prêt.** [Dépôt public](https://github.com/jeremyESEO/chronoterre-france), [instructions pour la correction](rendu_final.md) et synthèse distincte.

- [ ] Répéter la [soutenance de six minutes](soutenance_france.md) sur le poste utilisé en cours.
- [ ] Déposer sur Moodle le lien public et le PDF à la date et à l’heure indiquées.
