# Contrat de données France — 2.0.1

**Jeu :** `chronoterre_france`. **Responsable :** Projet académique ESEO ChronoTerre. Cette version lisible documente le [contrat de référence](../config/france_contract.json). Les types, les clés et les contraintes sont dans le [schéma SQL](../sql/france_schema.sql) ; le [dictionnaire](dictionnaire_france.md) précise le grain de chaque table.

## Grain et identifiants

| Objet | Une ligne représente… | Identifiant ou clé métier |
|---|---|---|
| `raw_file` | une réponse originale immuable | `raw_id` ; URL et empreinte conservées dans le manifeste. |
| `commune` | une commune du référentiel collecté, code INSEE texte | Code INSEE conservé en texte. |
| `climate_value` | une commune × indicateur × horizon × saison pour le corpus Climadiag retenu | Commune × indicateur × horizon × saison. |
| `fossil_occurrence` | un enregistrement bibliographique de taxon dans une collection, pas un animal | Identifiant d’occurrence PBDB, relié à la collection, au taxon et à la source. |

**Champs PBDB requis :** `occurrence_no`, `collection_no`, `identified_name`, `reference_no`, `primary_reference`, `min_ma`, `max_ma`.

**Référentiel géographique :** EPSG:4326 ; distances géodésiques/haversine, surfaces ellipsoïdales WGS84.

**Donnée manquante :** NULL ou absence explicitement présentée ; jamais zéro imputé.

## Règles de qualité

| ID | Contrôle | Condition | Action si non conforme |
|---|---|---|---|
| F01 | Identifiant et taxon | Identifiants PBDB numériques positifs, nom non vide | rejet |
| F02 | Coordonnées | WGS84 fini, point dans un contour départemental français | rejet |
| F03 | Provenance | Pas de coordonnées politiques ou de contradiction déjà connue | rejet |
| F04 | Âges | 0 ≤ min_ma ≤ max_ma ≤ 4600 Ma | rejet |
| F05 | Référence | Identifiant et citation présents | rejet |
| U01 | Unicité | Clé métier unique | déduplication et comptage |
| C01 | Valeur climatique | Nombre fini dans les bornes physiques de son unité | rejet |
| C02 | Fourchette | Borne basse ≤ médiane ≤ borne haute | rejet |
| C03 | Série | Indicateur connu, commune jointe par code INSEE, horizon publié | rejet |
| G01 | Géométrie | Valide et non vide, référence connue | rejet |
| P01 | Raw | SHA-256 identique aux octets collectés | arrêt du pipeline |
| M01 | Média | Auteur, licence, page source et correspondance taxonomique | exclusion de la galerie |

Les rejets sont conservés avec leur motif dans [le fichier dédié](../data/rejected/france_rejects.jsonl). Le [rapport national](../reports/france_run.json) présente les compteurs ; le [rapport d’incident](../reports/rendu_final_incident.json) montre un arrêt P01 et la reprise.

## Transformations et évolution

- code INSEE texte
- NIVMER mètres bruts ×100 → cm
- make_valid GEOS pour enveloppes invalides, journal sans modifier raw
- aucune interpolation climatique
- fossiles localisés sur contours départementaux 100 m

**Changement de schéma ou de sens d’une variable :** nouveau schéma ou sens de variable : arrêter, examiner, incrémenter le contrat et reconstruire.
