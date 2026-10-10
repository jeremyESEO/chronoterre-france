# Dictionnaire et modèle logique

SQLite 3, clés étrangères activées lors de la construction ; colonnes normalisées, GeoJSON uniquement pour les géométries. Les octets bruts restent séparés. Les tables RTree sont des index techniques, pas des domaines métier.

## source

Une ligne représente un producteur ou diffuseur avec ses conditions.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| source_id | TEXT | oui | 1 |

| producer | TEXT | oui | — |

| url | TEXT | oui | — |

| license | TEXT | oui | — |

| limits | TEXT | oui | — |

## dataset_version

Une ligne représente une ressource collectée à une date.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| version_id | TEXT | oui | 1 |

| source_id | TEXT | oui | — |

| label | TEXT | oui | — |

| retrieved_at | TEXT | oui | — |

| coverage | TEXT | oui | — |

Relations : source_id → source.clé primaire.

## raw_file

Une ligne représente une réponse originale immuable.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| raw_id | TEXT | oui | 1 |

| version_id | TEXT | oui | — |

| path | TEXT | oui | — |

| url | TEXT | oui | — |

| sha256 | TEXT | oui | — |

| bytes | INTEGER | oui | — |

| retrieved_at | TEXT | oui | — |

Relations : version_id → dataset_version.clé primaire.

## department

Une ligne représente un contour départemental simplifié millésimé.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| code | TEXT | oui | 1 |

| name | TEXT | oui | — |

| region | TEXT | non | — |

| geometry | TEXT | oui | — |

| crs | TEXT | oui | — |

## commune

Une ligne représente une commune du référentiel collecté, code INSEE texte.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| code | TEXT | oui | 1 |

| name | TEXT | oui | — |

| department | TEXT | non | — |

| region | TEXT | non | — |

| longitude | REAL | non | — |

| latitude | REAL | non | — |

| population | INTEGER | non | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; department → department.code.

## postal_code

Une ligne représente une association commune-code postal, plusieurs-à-plusieurs.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| commune_code | TEXT | oui | 1 |

| postal_code | TEXT | oui | 2 |

Relations : commune_code → commune.code.

## climate_place

Une ligne représente une commune avec sa méthode climatique et sa référence.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| commune_code | TEXT | oui | 1 |

| domain | TEXT | oui | — |

| reference_start | INTEGER | oui | — |

| reference_end | INTEGER | oui | — |

| resolution | TEXT | oui | — |

| method | TEXT | oui | — |

| altitude_text | TEXT | non | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; commune_code → commune.code.

## scenario

Une ligne représente une nature de projection (TRACC ou référence).

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| scenario_id | TEXT | oui | 1 |

| label | TEXT | oui | — |

| kind | TEXT | oui | — |

| description | TEXT | oui | — |

## climate_model

Une ligne représente un ensemble de modèles publié, sans prétendre disposer des simulations individuelles.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| model_id | TEXT | oui | 1 |

| label | TEXT | oui | — |

| kind | TEXT | oui | — |

| details | TEXT | oui | — |

## period

Une ligne représente un horizon publié ; bornes annuelles NULL lorsqu’elles ne sont pas fournies.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| period_id | TEXT | oui | 1 |

| label | TEXT | oui | — |

| start_year | INTEGER | non | — |

| end_year | INTEGER | non | — |

| kind | TEXT | oui | — |

## indicator

Une ligne représente une variable, sa définition et son unité canonique.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| indicator_id | TEXT | oui | 1 |

| label | TEXT | oui | — |

| unit | TEXT | oui | — |

| definition | TEXT | oui | — |

| family | TEXT | oui | — |

| source_url | TEXT | oui | — |

## climate_value

Une ligne représente une commune × indicateur × horizon × saison pour le corpus Climadiag retenu.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| commune_code | TEXT | oui | 1 |

| indicator_id | TEXT | oui | 2 |

| period_id | TEXT | oui | 3 |

| season | TEXT | oui | 4 |

| value | REAL | oui | — |

| lower | REAL | non | — |

| upper | REAL | non | — |

| scenario_id | TEXT | oui | — |

| model_id | TEXT | oui | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; model_id → climate_model.clé primaire; scenario_id → scenario.clé primaire; period_id → period.clé primaire; indicator_id → indicator.clé primaire; commune_code → climate_place.clé primaire.

## hazard

Une ligne représente une famille d’aléa ou de risque recensé.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| hazard_id | TEXT | oui | 1 |

| label | TEXT | oui | — |

| category | TEXT | oui | — |

## commune_hazard

Une ligne représente une commune × aléa recensé, sans intersection à l’adresse.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| commune_code | TEXT | oui | 1 |

| hazard_id | TEXT | oui | 2 |

| raw_id | TEXT | oui | — |

| nature | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; hazard_id → hazard.clé primaire; commune_code → commune.code.

## bibliography

Une ligne représente une référence bibliographique PBDB.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| reference_id | TEXT | oui | 1 |

| citation | TEXT | oui | — |

| url | TEXT | oui | — |

## taxon

Une ligne représente un identifiant taxonomique accepté PBDB.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| taxon_id | TEXT | oui | 1 |

| accepted_name | TEXT | oui | — |

| rank | TEXT | non | — |

| phylum | TEXT | non | — |

| class_name | TEXT | non | — |

| family | TEXT | non | — |

## geological_interval

Une ligne représente un intervalle d’âge et ses bornes en millions d’années.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| interval_id | TEXT | oui | 1 |

| early_name | TEXT | oui | — |

| late_name | TEXT | non | — |

| max_ma | REAL | oui | — |

| min_ma | REAL | oui | — |

## fossil_site

Une ligne représente une collection PBDB localisée retenue ; plusieurs collections peuvent partager un point.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| site_id | INTEGER | oui | 1 |

| name | TEXT | oui | — |

| longitude | REAL | oui | — |

| latitude | REAL | oui | — |

| department | TEXT | non | — |

| environment | TEXT | non | — |

| coordinate_basis | TEXT | non | — |

| coordinate_precision | TEXT | non | — |

| geographic_comment | TEXT | non | — |

| stratigraphy | TEXT | non | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; department → department.code.

## fossil_occurrence

Une ligne représente un enregistrement bibliographique de taxon dans une collection, pas un animal.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| occurrence_id | INTEGER | oui | 1 |

| site_id | INTEGER | oui | — |

| taxon_id | TEXT | oui | — |

| reference_id | TEXT | oui | — |

| interval_id | TEXT | oui | — |

| identified_name | TEXT | oui | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; interval_id → geological_interval.clé primaire; reference_id → bibliography.clé primaire; taxon_id → taxon.clé primaire; site_id → fossil_site.clé primaire.

## media

Une ligne représente un fichier et sa provenance, auteur, licence et légende.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| media_id | TEXT | oui | 1 |

| category | TEXT | oui | — |

| page_url | TEXT | oui | — |

| image_url | TEXT | oui | — |

| local_path | TEXT | non | — |

| author | TEXT | oui | — |

| license | TEXT | oui | — |

| caption | TEXT | oui | — |

| retrieved_at | TEXT | oui | — |

| association_evidence | TEXT | oui | — |

## taxon_media

Une ligne représente une association taxon-image, avec niveau de correspondance.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| taxon_id | TEXT | oui | 1 |

| media_id | TEXT | oui | 2 |

| match_level | TEXT | oui | — |

Relations : media_id → media.clé primaire; taxon_id → taxon.clé primaire.

## test_place

Une ligne représente un lieu public choisi pour tester la couverture.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| place_id | TEXT | oui | 1 |

| label | TEXT | oui | — |

| commune_code | TEXT | non | — |

| longitude | REAL | oui | — |

| latitude | REAL | oui | — |

| kind | TEXT | oui | — |

Relations : commune_code → commune.code.

## parcel

Une ligne représente une parcelle cadastrale de l’échantillon public.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| parcel_id | TEXT | oui | 1 |

| commune_code | TEXT | non | — |

| section | TEXT | non | — |

| number | TEXT | non | — |

| geometry | TEXT | oui | — |

| crs | TEXT | oui | — |

| vintage | TEXT | non | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; commune_code → commune.code.

## urban_document

Une ligne représente un document identifié par le fournisseur, avec dates connues.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| document_id | TEXT | oui | 1 |

| label | TEXT | oui | — |

| type | TEXT | non | — |

| approval_date | TEXT | non | — |

| publication_date | TEXT | non | — |

| url | TEXT | oui | — |

| status | TEXT | oui | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire.

## urban_zone

Une ligne représente une géométrie de zonage et son règlement lié.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| zone_id | TEXT | oui | 1 |

| document_id | TEXT | non | — |

| zone_type | TEXT | non | — |

| label | TEXT | non | — |

| validity_date | TEXT | non | — |

| regulation_url | TEXT | non | — |

| geometry | TEXT | oui | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; document_id → urban_document.clé primaire.

## prescription

Une ligne représente une prescription surfacique ou une servitude collectée.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| prescription_id | TEXT | oui | 1 |

| document_id | TEXT | non | — |

| category | TEXT | non | — |

| label | TEXT | non | — |

| geometry | TEXT | oui | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; document_id → urban_document.clé primaire.

## parcel_zone

Une ligne représente une intersection parcelle-zone réelle, relation plusieurs-à-plusieurs.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| parcel_id | TEXT | oui | 1 |

| zone_id | TEXT | oui | 2 |

| method | TEXT | oui | — |

Relations : zone_id → urban_zone.clé primaire; parcel_id → parcel.clé primaire.

## hazard_zone

Une ligne représente une enveloppe d’aléa et son scénario dans une version source.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| zone_id | TEXT | oui | 1 |

| hazard_id | TEXT | non | — |

| label | TEXT | oui | — |

| nature | TEXT | oui | — |

| scenario | TEXT | non | — |

| return_period | TEXT | non | — |

| geometry | TEXT | oui | — |

| raw_id | TEXT | oui | — |

Relations : raw_id → raw_file.clé primaire; hazard_id → hazard.clé primaire.

## spatial_intersection

Une ligne représente un lieu de test × enveloppe avec résultat booléen.

| Champ | Type | Obligatoire | Clé primaire |

|---|---|---|---|

| place_id | TEXT | oui | 1 |

| zone_id | TEXT | oui | 2 |

| intersects | INTEGER | oui | — |

| method | TEXT | oui | — |

Relations : zone_id → hazard_zone.clé primaire; place_id → test_place.clé primaire.

## Choix et limites

Les identifiants INSEE sont des chaînes (Corse 2A/2B). Aucun rapprochement par simple nom. Les clés PBDB sont conservées. climate_value utilise une clé composite et WITHOUT ROWID ; ajouter plusieurs corpus ou modèles individuels imposerait une migration élargissant cette clé, et non un INSERT OR IGNORE silencieux. Les références géologiques conservent leurs bornes, pas un faux âge exact.

Index : commune(name), commune(department), climate_value(indicator_id,period_id,season), fossil_occurrence(site_id/taxon_id), RTree fossil_index. Les enveloppes locales sont peu nombreuses ; leurs intersections utilisent GEOS. Une base nationale de parcelles/aléas nécessiterait PostGIS et GiST. Les mises à jour communales ne sont pas réconciliées historiquement : une fiche sans code commun au millésime collecté est exclue et comptée.
