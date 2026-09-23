# Évaluation des sources et attribution

Dates d’accès exactes : champ `fetched_at` de `data/raw/manifest.json`. L’état courant peut évoluer ; le lot fourni constitue la référence reproductible. Les accès utilisent des API ou des fichiers ouverts, sans scraping de pages ni compte nominatif.

## Comparaison de candidats

| Besoin | Candidat | Atouts | Limites | Décision |
|---|---|---|---|---|
| Fossiles et âge géologique | Paleobiology Database, API 1.2 | Identifiants d’occurrence/collection/taxon, âges, milieu, références ; filtre géographique | Couverture bibliographique inégale, coordonnées parfois approximatives ou erronées | Retenu, avec exclusions traçables. |
| Fossiles et spécimens de musées | GBIF occurrence API, données FossilSpecimen | API structurée, grands volumes, licences par jeu, recherche géographique | Âge géologique, contexte sédimentaire et références variables selon le jeu ; doublons possibles avec PBDB | Alternative évaluée, non fusionnée pour éviter un faux accroissement de couverture. |
| Climat passé | Open-Meteo Historical Weather, ERA5-Land seul | Températures cohérentes sur 30 ans | Pluie absente dans les réponses collectées : échec du besoin multivariable | Pilote conservé ; remplacé par ERA5-Seamless. |
| Climat passé | Open-Meteo Historical Weather, ERA5-Seamless | Température ERA5-Land + pluie ERA5, accès homogène | Résolutions différentes selon variable ; ce sont des réanalyses | Retenu et expliqué dans le modèle. |
| Climat futur | Open-Meteo Climate API, CMIP6 HighResMIP | Séries quotidiennes, plusieurs modèles, horizon 2050, accès sans clé pour le projet non commercial | Forçage proche RCP8.5, pas un menu de scénarios ; correction statistique pouvant produire de rares incohérences min/moy/max | Deux modèles retenus ; jours incohérents rejetés. |

GBIF a été évalué via sa documentation et son format ; aucun résultat de collecte GBIF n’est revendiqué. Les recherches bibliographiques n’ont pas servi à fabriquer des observations.

## Sources effectivement collectées

### 1. Paleobiology Database

- Producteur : communauté de chercheurs et contributeurs PBDB.
- Documentation : https://paleobiodb.org/data1.2/
- Occurrences : `https://paleobiodb.org/data1.2/occs/list.json`
- Collections : `https://paleobiodb.org/data1.2/colls/list.json`
- Paramètres : boîte lon 1,4–3,6 / lat 48,1–49,25 ; `vocab=pbdb`, `limit=all` ; coordonnées, localisation, milieu, référence et classification. L’étendue est volontairement limitée, puis le filtre polygonal élimine les voisins.
- Licence des données publiques : **CC BY 4.0**, confirmée par https://paleobiodb.org/navigator/ et https://creativecommons.org/2013/12/19/paleobiology-database-now-cc-by/.
- Attribution : Paleobiology Database et contributeurs ; publications conservées dans la table `bibliography`, citées dans les fiches.
- Règle de sélection : exclure les coordonnées « based on political unit », les points hors région, les références absentes et les contradictions documentées. La collection inconnue `197471` est explicitement placée à Paris à cause du musée : elle est rejetée, pas présentée comme un fossile parisien.
- Ne pas confondre occurrence, collection, localité, spécimen et espèce. La densité de points mesure aussi l’histoire de la recherche.

### 2. Open-Meteo Historical Weather API

- Documentation : https://open-meteo.com/en/docs/historical-weather-api
- Endpoint : `https://archive-api.open-meteo.com/v1/archive`
- Modèle final : `era5_seamless`. Températures issues d’ERA5-Land à 0,1° ; précipitations issues d’ERA5 à 0,25°. La maille renvoyée par l’API est enregistrée, mais ne décrit pas séparément la résolution de chaque variable.
- Période : 1991-01-01 à 2020-12-31, jours UTC ; températures en °C, précipitations en mm.
- Attribution : Open-Meteo, Copernicus Climate Change Service (C3S), ECMWF, ERA5 et ERA5-Land.
- Licence de diffusion API : CC BY 4.0 avec attribution. Sources ECMWF/Copernicus et conditions de réutilisation précisées dans la documentation du fournisseur.
- Le pilote `era5_land` est conservé dans raw et `reports/pilot_report.json` : la pluie y est NULL. Il n’est pas utilisé dans la base finale. Ce changement de source est une décision documentée, pas une imputation.

### 3. Open-Meteo Climate API

- Documentation : https://open-meteo.com/en/docs/climate-api
- Endpoint : `https://climate-api.open-meteo.com/v1/climate`
- Producteurs : CMIP6 HighResMIP, Meteorological Research Institute (MRI-AGCM3-2-S), consortium EC-Earth/SMHI (EC-Earth3P-HR) ; diffusion et correction statistique Open-Meteo.
- Modèles : `MRI_AGCM3_2_S` et `EC_Earth3P_HR`, 2030-01-01 à 2049-12-31.
- La documentation indique un forçage aussi proche que possible de RCP8.5 et une correction sur ERA5-Land. Les modèles ne sont pas des scénarios optimiste/pessimiste. Leur passé simulé n’est pas utilisé comme observation historique.
- Limite de l’API : 2050-01-01. Le dossier utilise donc « horizon 2050 » pour 2030–2049.
- Données diffusées sous CC BY 4.0, attribution aux producteurs et à Open-Meteo. Service gratuit non commercial : https://open-meteo.com/en/pricing et https://open-meteo.com/en/terms.
- Les longues périodes sont pondérées dans les quotas : les requêtes sont espacées, mises en cache et reprises après erreur. Aucun rechargement du dashboard ne relance la collecte fournisseur.

### 4. Contours et communes

- Contours départementaux Etalab, millésime 2025, simplification 100 m, dérivés d’IGN ADMIN EXPRESS en métropole.
- Source exacte : https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-100m.geojson
- Chaîne de production : https://github.com/etalab/contours-administratifs
- Licence : Licence Ouverte 2.0 pour IGN ADMIN EXPRESS et les données métropolitaines utilisées. La source OSM d’outre-mer décrite par ce dépôt n’est pas utilisée pour l’Île-de-France.
- Communes : https://geo.api.gouv.fr/communes?codeRegion=11&fields=nom,code,codeDepartement,centre&format=json
- Documentation : https://geo.api.gouv.fr/decoupage-administratif ; producteurs DINUM/INSEE/IGN ; Licence Ouverte.
- Le raw départemental national est conservé tel que reçu. Seuls les huit polygones `region=11` sont publiés dans curated et l’application. Le raw des communes couvre la région ; seules les dix communes choisies entrent dans la table `city`.

## Conditions de reproductibilité

L’URL, l’horodatage UTC, la taille et le SHA-256 sont enregistrés pour chaque réponse. `manifest.json` est un pointeur de cache mutable ; les réponses horodatées et les manifestes de lots complets sont immuables. Le rejeu hors ligne ne dépend pas d’une API disponible aujourd’hui ni de données mises à jour depuis la collecte.

Un fichier HTTP invalide sauvegardé avant parsing peut rester dans raw mais ne figure pas dans le manifeste validé. Il ne participe pas aux résultats. Le collecteur échoue explicitement si une série manque ; il ne remplace pas une API inaccessible par des données fabriquées.
