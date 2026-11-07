# Avancement de ChronoTerre — France

État mis à jour le 7 novembre 2026. Le dépôt GitHub est public. Pour le guide final ESEO, partir du [point d’entrée de remise](docs/rendu_final.md) : synthèse séparée, ADR, suivi des runs et oral de 6 minutes.

## Pour le professeur

1. Lire README.md pour lancer l'application et restaurer la base.
2. Consulter docs/matrice_academique.md pour les exigences et preuves.
3. Consulter reports/ pour les résultats réellement calculés et tests locaux.
4. Lire docs/parcours_installation.md pour la méthode du classement et les limites.
5. Suivre ROADMAP.md et les futures issues/PR pour la refonte de production.

## Éléments livrés

| Élément | État | Preuves et limites |
|---|---|---|
| Collecte et base nationale relationnelle | Réalisé | national/, sql/france_schema.sql, raw et manifestes ; restauration reproductible |
| Recherche communale nationale et carte | Réalisé avec limites de recette | dist/ ; carte de publication inspectée, tests DOM ; recette navigateur complète non réalisée |
| Fossiles nationaux | Réalisé avec couverture fournisseur | 48 126 occurrences retenues ; rapports et provenance PBDB |
| Climat communal | Réalisé avec limites de résolution | 34 938 fiches ; projection représentative de commune, pas du logement |
| Parcours d'installation climatique | Réalisé | 34 746 communes comparables métropole/Corse, 5 critères ; home-core.js, home.js, home-meta.json |
| Réanalyse 2016–2025 | Réalisé sur échantillon | 8 lieux, 29 224 journées ; recent.sqlite, manifestes ; pas une couverture nationale de stations |
| Inondation et argiles | Réalisé localement | Toulouse et secteur Bordeaux ; aucun diagnostic national à l'adresse |
| Urbanisme | Couverture et accès limités | Connecteur API Carto et échantillon ; aucune décision automatique de constructibilité |
| API de consultation | Réalisé localement | national/serve.py et docs/api_france.md ; pas de backend de production hébergé |
| Analyses SQL et démonstration académique | Réalisé | sql/france_analyses.sql, rapports, démonstration isolée |
| PostgreSQL/PostGIS et API de production | Prévu | Non déployé ; ROADMAP.md |
| Analyse assurantielle de portefeuilles | Prévu | Aucun modèle de sinistralité ou de tarification livré |

## Versions déjà publiées sur Sites

| Version | Changement | Commit source |
|---|---|---|
| 2 | Extension nationale, pipeline, API locale et interface | c605366ab4f6d1e8604792432a5c8fc417936808 |
| 3 | Correction du refus des fichiers GeoJSON selon leur type MIME | 34f9296beeceb4a7b609ad36dc750a3dd3fabe56 |
| 4 | Limites de zoom du relief IGN | 91416a0eed83fbe60fdcaf597a2228f7670474c1 |
| 5 | Parcours d'installation, index national et réanalyse récente | c22ce237eadde0c3d0a183f9afd1384a9369c853 |
| 6 | Démarrage robuste du parcours chargé tardivement | bc28734758fe6d71e3022d4f043b45bb4143ecf6 |

Site actuel : https://chronoterre-idf.jeremyhercent.chatgpt.site ; accès réservé aux personnes déjà autorisées. La création de ce dépôt ne change pas l'audience du site.

## Vérifications

Rapports locaux : home_tests.json, home_delayed.json, home_replay.json, home_sensitivity.json et front_dom.json. Ils décrivent leurs limites. Les tests DOM ne sont pas une recette WebGL/mobile. Les workflows sont consultables dans [GitHub Actions](https://github.com/jeremyESEO/chronoterre-france/actions). Les essais du rendu sont décrits dans [les preuves de vérification](reports/rendu_final_verification.json).

## Organisation du suivi

Chaque développement doit avoir une issue décrivant le besoin, les sources et les critères de réception. Les PR indiqueront les changements, tests exécutés, couverture réelle et limitations. Les fonctionnalités futures ne sont cochées qu'après livraison et preuve. L'historique des développements est repris sur GitHub. Les identifiants ci-dessus désignent les commits des publications Sites d'origine ; la copie publique exclut le texte intégral du support de cours, ce qui change certains identifiants Git.
