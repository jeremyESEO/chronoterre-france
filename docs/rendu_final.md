# Rendu final ESEO — point d’entrée

**Projet : ChronoTerre France.** Le guide final annonce une remise le **8 novembre 2026**. L’heure est à vérifier sur Moodle.

1. **Dépôt public** : https://github.com/jeremyESEO/chronoterre-france ; [démarrage Windows, Linux et macOS](../README.md#ouvrir-sous-windows).
2. **Synthèse académique de 5 pages** : `Synthese_finale_ChronoTerre.pdf`, fournie séparément pour le dépôt Moodle. Le dossier France de 15 pages dans `docs/` reste une annexe de développement issue du cadre des TP.
3. **Exigences et décisions** : [matrice au barème final](matrice_academique.md), [ADR 001](ADR_001.md), [gouvernance](gouvernance.md), [architecture et traçabilité](lineage.md).
4. **Preuves vérifiables** : [vérification de livraison](../reports/rendu_final_verification.json), [incident et reprise](../reports/rendu_final_incident.json), [rapport national](../reports/france_run.json), [rejeu](../reports/france_idempotence.json), [SQL](analyses_france.md).
5. **Défense** : [conducteur de 6 minutes et oral blanc](soutenance_france.md). La synthèse suffit à suivre le fil ; les annexes permettent de vérifier les détails.

## Où retrouver les livrables du guide

| Livrable (guide, p. 7–8) | Dans ChronoTerre |
|---|---|
| Code et tests | [Pipeline France](../national/pipeline.py), [collecte](../national/collect.py), [validation](../national/validate.py), [exports](../national/export.py), [tests](../tests). Le code V1 conservé est dans `src/`. |
| Données exemples | [Brut horodaté et manifeste](../data/raw/national_manifest.json), [CSV propre](../data/curated/france_demo_fossils.csv), [rejets motivés](../data/rejected/france_rejects.jsonl). Les blocs de la base France sont dans `data/curated/` ; la commande de restauration les vérifie et les assemble. |
| Documentation | [README](../README.md), [dictionnaire France](dictionnaire_france.md), [contrat France en Markdown](contrat_france.md), [ADR 001](ADR_001.md). Le contrat et les paramètres lus par le pipeline sont dans `config/`. |
| Architecture et traçabilité | [V1 en PNG](architecture.png), [V2 en SVG](architecture_v2.svg), [trajet d’une donnée jusqu’à sa fiche](lineage.md). |
| Rapports | [Profilage](../reports/france_profile_before.json), [qualité et exécution](../reports/france_run.json), [incident](../reports/rendu_final_incident.json) et [rejeu](../reports/france_idempotence.json). |
| Synthèse | PDF distinct de cinq pages : cadrage et sources → pipeline → qualité et incident → résultat → décisions et limites. |
| Démonstration | [Conducteur de six minutes](soutenance_france.md) ; le socle de démonstration s’exécute avec `python -m national.demo`. |

Le correcteur peut restaurer la base et consulter la démo locale sans clé fournisseur. La reconstruction nationale s’exécute depuis les raw archivés après installation des dépendances. Pour présenter en direct, ouvrir l’API locale et exécuter le socle court ; préparer le rapport de reconstruction complète à l’avance.

Avant de déposer : répéter sur son ordinateur, vérifier l’accès au dépôt sans connexion GitHub et joindre le PDF de 5 pages au lien. Le dépôt Moodle et la répétition de l’étudiant restent des actions personnelles.
