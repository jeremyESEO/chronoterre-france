-- Q01 Couverture : inclure les départements sans occurrence retenue.
SELECT d.department_code,d.name,COUNT(DISTINCT s.site_id) AS collections,
 COUNT(o.occurrence_id) AS occurrences,COUNT(DISTINCT o.taxon_id) AS taxa
FROM department d LEFT JOIN fossil_site s USING(department_code)
LEFT JOIN fossil_occurrence o USING(site_id)
GROUP BY d.department_code ORDER BY occurrences DESC;

-- Q02 Collections les plus documentées : attention au biais d'effort de recherche.
SELECT s.site_id,s.name,COUNT(*) AS occurrences,COUNT(DISTINCT o.taxon_id) AS taxa
FROM fossil_occurrence o JOIN fossil_site s USING(site_id)
GROUP BY s.site_id ORDER BY taxa DESC LIMIT 10;

-- Q03 Quels groupes sont documentés pendant l'Éocène (recouvrement d'intervalles) ?
SELECT COALESCE(t.class_name,'Non renseigné') AS class_name,COUNT(*) AS occurrences,
 COUNT(DISTINCT o.taxon_id) AS taxa
FROM fossil_occurrence o JOIN taxon t USING(taxon_id) JOIN geo_interval i USING(interval_id)
WHERE i.max_ma>=33.9 AND i.min_ma<=56
GROUP BY t.class_name ORDER BY occurrences DESC;

-- Q04 Sous-requête : taxons signalés dans au moins trois collections distinctes.
SELECT t.accepted_name,COUNT(DISTINCT o.site_id) AS collections
FROM taxon t JOIN fossil_occurrence o USING(taxon_id)
WHERE t.taxon_id IN (SELECT taxon_id FROM fossil_occurrence GROUP BY taxon_id HAVING COUNT(DISTINCT site_id)>=3)
GROUP BY t.taxon_id ORDER BY collections DESC LIMIT 20;

-- Q05 Fonction de fenêtre : trois groupes les plus documentés par département.
WITH counts AS (
 SELECT s.department_code,COALESCE(t.class_name,'Non renseigné') AS class_name,COUNT(*) AS n
 FROM fossil_occurrence o JOIN fossil_site s USING(site_id) JOIN taxon t USING(taxon_id)
 GROUP BY s.department_code,t.class_name
), ranked AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY department_code ORDER BY n DESC,class_name) AS rank
 FROM counts
)
SELECT * FROM ranked WHERE rank<=3 ORDER BY department_code,rank;

-- Q06 Les cinq publications couvrant le plus d'occurrences de cet extrait.
SELECT b.reference_id,b.citation,COUNT(*) AS occurrences,COUNT(DISTINCT o.site_id) AS collections
FROM fossil_occurrence o JOIN bibliography b USING(reference_id)
GROUP BY b.reference_id ORDER BY occurrences DESC LIMIT 5;

-- Q07 Référence : moyennes d'indicateurs annuels sur les 30 années complètes.
SELECT c.name,ROUND(AVG(a.mean_c),2) AS mean_c,ROUND(AVG(a.hot_days),2) AS hot_days,
 ROUND(AVG(a.rain_mm),1) AS rain_mm,COUNT(*) AS complete_years
FROM v_climate_annual a JOIN city c USING(city_code)
WHERE a.kind='baseline' GROUP BY c.city_code ORDER BY hot_days DESC;

-- Q08 Jointure référence/futur pour chaque commune et chaque modèle.
WITH means AS (
 SELECT city_code,model_id,kind,AVG(mean_c) AS temp,AVG(hot_days) AS hot
 FROM v_climate_annual GROUP BY city_code,model_id,kind
)
SELECT c.name,f.model_id,ROUND(b.temp,2) AS baseline_c,ROUND(f.temp,2) AS future_c,
 ROUND(f.temp-b.temp,2) AS delta_c,ROUND(f.hot-b.hot,1) AS extra_hot_days
FROM means f JOIN means b ON b.city_code=f.city_code AND b.kind='baseline'
JOIN city c ON c.city_code=f.city_code WHERE f.kind='future' ORDER BY delta_c DESC;

-- Q09 Variabilité entre deux modèles : ce n'est pas un intervalle de confiance.
WITH means AS (
 SELECT city_code,model_id,kind,AVG(mean_c) AS temp FROM v_climate_annual GROUP BY city_code,model_id,kind
)
SELECT c.name,ROUND(MIN(f.temp-b.temp),2) AS min_delta_c,
 ROUND(MAX(f.temp-b.temp),2) AS max_delta_c,COUNT(*) AS models
FROM means f JOIN means b ON b.city_code=f.city_code AND b.kind='baseline'
JOIN city c ON c.city_code=f.city_code WHERE f.kind='future'
GROUP BY c.city_code ORDER BY max_delta_c DESC;

-- Q10 Évolution historique descriptive ; deux décennies, même réanalyse.
SELECT c.name,
 ROUND(AVG(CASE WHEN year BETWEEN 2011 AND 2020 THEN mean_c END)-
 AVG(CASE WHEN year BETWEEN 1991 AND 2000 THEN mean_c END),2) AS delta_decades_c
FROM v_climate_annual a JOIN city c USING(city_code)
WHERE a.kind='baseline' GROUP BY c.city_code ORDER BY delta_decades_c DESC;

-- Q11 Été à Vélizy : moyenne journalière, juin-juillet-août par année et modèle.
SELECT s.model_id,substr(d.date,1,4) AS year,ROUND(AVG(d.tmean_c),2) AS summer_c,
 SUM(CASE WHEN d.tmax_c>=30 THEN 1 ELSE 0 END) AS hot_summer_days
FROM climate_day d JOIN climate_series s USING(series_id)
WHERE s.city_code='78640' AND substr(d.date,6,2) IN ('06','07','08')
GROUP BY s.model_id,year HAVING COUNT(*)=92 ORDER BY s.model_id,year;

-- Q12 Plus longue série de jours chauds à Vélizy : segmentation par fenêtre.
WITH hot AS (
 SELECT d.series_id,d.date,julianday(d.date)-ROW_NUMBER() OVER(PARTITION BY d.series_id ORDER BY d.date) AS grp
 FROM climate_day d JOIN climate_series s USING(series_id)
 WHERE s.city_code='78640' AND d.tmax_c>=30
), spells AS (
 SELECT series_id,MIN(date) AS first_day,MAX(date) AS last_day,COUNT(*) AS days
 FROM hot GROUP BY series_id,grp
)
SELECT * FROM spells ORDER BY days DESC LIMIT 10;

-- Q13 Traçabilité intégrale d'une occurrence, de la publication au fichier brut.
SELECT o.occurrence_id,t.accepted_name,s.name,b.citation,r.path,r.sha256,r.fetched_at,src.name AS source
FROM fossil_occurrence o JOIN taxon t USING(taxon_id) JOIN fossil_site s USING(site_id)
JOIN bibliography b USING(reference_id) JOIN raw_file r ON o.raw_id=r.raw_id
JOIN source src USING(source_id) ORDER BY o.occurrence_id LIMIT 5;

-- Q14 Vérifier l'unicité de la clé métier climatique : résultat attendu vide.
SELECT series_id,date,COUNT(*) AS n FROM climate_day GROUP BY series_id,date HAVING COUNT(*)>1;

-- Q15 Évaluer les points climatiques réellement distincts (éviter la fausse précision).
SELECT model_id,grid_latitude,grid_longitude,COUNT(*) AS assigned_cities
FROM climate_series GROUP BY model_id,grid_latitude,grid_longitude
ORDER BY assigned_cities DESC,model_id;
