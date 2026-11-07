# Exigence → fichier → preuve

La matrice synthétise les 13 pages des consignes du cours. Aucun conflit de barème identifié. Le socle court est `national.demo`, l’extension nationale est explicitement un travail supplémentaire.

| Barème | Fichiers | Preuve |
|---|---|---|
| Problème et cas d’usage, 3 points | README, dossier | question unique, trois cas et KPI ci-dessous |
| Sources et conformité, 3 | sources_france.md, manifestes, registre médias | URLs, réponses réelles, licences, limites et échecs |
| Modèle et architecture, 3 | dictionnaire, modèles .mmd, sql/france_schema.sql, config/france_contract.json | grains, PK/FK, relations N–N, contrôles |
| Collecte reproductible, 3 | national/collect*.py, data/raw | réponses immuables datées, paramètres dans URL, empreintes |
| Qualité et rejets, 3 | national/validate.py, reports/france_profile_before.json, france_run.json, data/rejected | 12 règles, compteurs et raisons ; avant nettoyage |
| Transformation et curated, 2 | national/pipeline.py, france.sqlite, dist/data | colonnes typées, déduplication, conversion des unités |
| Idempotence et rapport, 2 | france_idempotence.json, demo_tp.json | deux exécutions complètes, mêmes lignes triées et mêmes clés |
| Documentation et démonstration, 1 | README, soutenance, tests | lancement Windows, démonstration invalide isolée, limites honnêtes |

## Trois cas d’usage et trois KPI

1. En tant que personne préparant un déménagement, comparer les mêmes indicateurs climatiques sur deux à quatre communes. **KPI couverture climatique** = communes avec au moins une fiche / communes recherchables ×100, calcul SQL 01. Ce KPI ne mesure pas la sécurité d’un lieu.
2. En tant que famille examinant un terrain, retrouver les contraintes et les preuves connues. **KPI complétude documentaire** = documents avec date d’approbation renseignée / documents collectés ×100, SQL 11. Dénominateur limité à l’échantillon, pas à tous les PLU français.
3. En tant que curieux, comprendre une découverte et son illustration. **KPI couverture des médias fossiles** = occurrences liées à au moins une image de catégorie fossil / occurrences retenues ×100, SQL 15 ; les relations de même genre restent explicitement qualifiées.

Au moins 100 observations : le socle exploite une page PBDB de 10 000 enregistrements réels et sa sélection contrôlée. La fixture invalide est ajoutée en mémoire uniquement et marquée test_only. Elle est exclue du numérateur des observations réelles.
