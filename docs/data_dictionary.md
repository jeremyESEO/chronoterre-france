# Grain, relations et dictionnaire

## Grains

- **Fossile** : une occurrence PBDB (`occurrence_no`), reliant un taxon à une collection et une référence. Une collection est un contexte de collecte, pas nécessairement un emplacement unique. Un taxon peut être un genre, une famille ou une espèce.
- **Climat quotidien** : un jour UTC d’une série ; la série décrit une commune demandée, un modèle, une fenêtre et les coordonnées de maille renvoyées. La clé est `(series_id, date)`.
- **Climat annuel dérivé** : une série et une année complète ; il s’agit d’une vue SQL, pas d’une treizième table persistante.
- **Géographie** : un code INSEE pour une commune, un code départemental pour un département de la région 11.

Le dictionnaire initial détaillé de 14 champs fossiles et de 6 champs climatiques figure dans `config/data_contract.yaml`, avec type, unité, exigence et description. Voici le modèle physique final.

## Douze tables et relations

| Table | Clé primaire | Colonnes principales | Relations |
|---|---|---|---|
| `source` | `source_id` TEXT | name, owner, url, license | 1 source → N fichiers bruts |
| `raw_file` | `raw_id` TEXT | path, request_url, sha256, fetched_at, byte_count | FK source_id ; fichier → objets collectés |
| `department` | `department_code` TEXT | name, region_code=11 | FK raw_id ; 1 département → N communes/collections |
| `city` | `city_code` TEXT | name, latitude, longitude | FK department_code, raw_id ; 1 commune → N séries |
| `bibliography` | `reference_id` INTEGER | citation, url | 1 publication → N occurrences |
| `taxon` | `taxon_id` TEXT | accepted_name, rank, phylum, class_name, family | 1 taxon → N occurrences |
| `geo_interval` | `interval_id` TEXT | early_name, late_name, max_ma, min_ma | 1 intervalle exact de source → N occurrences |
| `fossil_site` | `site_id` INTEGER | name, latitude, longitude, environment, coordinate_basis, coordinate_precision, geographic_comment | FK department_code, raw_id ; 1 collection → N occurrences |
| `fossil_occurrence` | `occurrence_id` INTEGER | identified_name | FK site_id, taxon_id, reference_id, interval_id, raw_id |
| `climate_model` | `model_id` TEXT | name, institution, kind, scenario | 1 modèle → N séries |
| `climate_series` | `series_id` TEXT | kind, start_date, end_date, grid_latitude, grid_longitude | FK city_code, model_id, raw_id ; 1 série → N jours |
| `climate_day` | `(series_id,date)` | tmean_c, tmax_c, tmin_c, precipitation_mm | FK series_id |

Les tables internes de statistiques créées par SQLite ne sont pas des entités métier et ne sont pas comptées parmi ces douze tables.

## Types et unités

Les identifiants administratifs sont des chaînes : un code est une étiquette, pas une quantité à additionner. Les identifiants d’occurrence, collection et référence PBDB sont convertis en entiers positifs. Le taxon reste une chaîne pour permettre un repli explicite `name:<nom>` si l’identifiant accepté manque.

Dates : ISO `YYYY-MM-DD` ; horodatages de collecte : UTC ISO 8601 avec `Z`. Latitude/longitude : degrés WGS84. Âges : millions d’années avant le présent ; `max_ma` est la borne ancienne et `min_ma` la borne récente. Températures : °C à 2 m ; pluie : cumul mm/j. Les valeurs NULL des champs facultatifs ne deviennent ni chaîne « null » ni valeur zéro.

## Cardinalités et normalisation

Une occurrence référence exactement une collection, un taxon accepté, un intervalle et une publication. Chacune de ces dimensions peut être référencée par plusieurs occurrences. La relation collections ↔ taxons est donc N–N, matérialisée par les occurrences. Le nom identifié propre à la publication reste sur l’occurrence, tandis que le nom accepté reste sur le taxon.

Une série climatique référence exactement une commune et un modèle ; leur association sur une période est unique. Un jour ne peut pas exister sans sa série. Les coordonnées de la commune demandée et celles de la maille renvoyée sont séparées, car elles ne sont pas interchangeables.

Le producteur, la licence, la citation et le nom de la commune ne sont pas recopiés à chaque ligne quotidienne. Cette séparation évite les anomalies de mise à jour. Les classes/familles sont des attributs du taxon dans ce périmètre ; le projet ne cherche pas à modéliser tout l’arbre taxonomique et ses révisions.

## Contraintes et index

`PRAGMA foreign_keys=ON` est activé à la création. PK, FK, UNIQUE, NOT NULL et CHECK vérifient les relations, la région, les coordonnées, les bornes d’âge, les dates structurées, les températures et la pluie. Le parsing applicatif vérifie réellement les dates calendaires ; le CHECK SQLite sur leur longueur ne suffit pas seul.

Index : occurrence par collection, occurrence par taxon, collection par département. La clé primaire composée des jours organise naturellement les requêtes par série/date (`WITHOUT ROWID`). `PRAGMA optimize` génère les statistiques du planificateur.

Vues : `v_fossils` prépare la jointure complète des fiches ; `v_climate_annual` calcule les indicateurs annuels et exclut les années incomplètes. Les analyses de `sql/analyses.sql` illustrent agrégations, jointures, sous-requêtes, CTE et fenêtres.
