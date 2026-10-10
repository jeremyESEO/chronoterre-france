-- 01 Combien de communes ont une fiche climatique ?
-- Couverture des fiches, pas exhaustivité des indicateurs ni précision à une adresse.
SELECT (SELECT count(*) FROM commune) communes,(SELECT count(*) FROM climate_place) fiches,round(100.0*(SELECT count(*) FROM climate_place)/(SELECT count(*) FROM commune),2) couverture_pct;

-- 02 Quelle couverture climatique par domaine ?
-- Les domaines ultramarins restent distincts de la métropole.
SELECT domain,count(*) communes FROM climate_place GROUP BY domain ORDER BY communes DESC;

-- 03 Combien de communes par indicateur à 2050 ?
-- Une commune peut avoir plusieurs saisons ; le dénominateur porte sur les communes.
SELECT i.indicator_id,i.label,i.unit,count(DISTINCT v.commune_code) communes FROM indicator i LEFT JOIN climate_value v ON v.indicator_id=i.indicator_id AND v.period_id='2050' GROUP BY i.indicator_id;

-- 04 Comment comparer les jours très chauds des lieux de test ?
-- Même indicateur et horizon ; les domaines et les références doivent aussi être examinés.
SELECT c.name,v.period_id,v.value,v.lower,v.upper,i.unit FROM test_place t JOIN commune c ON c.code=t.commune_code JOIN climate_value v ON v.commune_code=c.code JOIN indicator i USING(indicator_id) WHERE v.indicator_id='S1' AND v.season='annuel' AND v.period_id='2050' ORDER BY c.name;

-- 05 Quelle évolution publiée entre 2030 et 2100 ?
-- Différence entre niveaux publiés, pas prédiction annuelle ni interpolation.
WITH v AS (SELECT commune_code,period_id,value,LAG(value) OVER(PARTITION BY commune_code ORDER BY CAST(period_id AS INTEGER)) preceding FROM climate_value WHERE indicator_id='S1' AND season='annuel' AND period_id IN ('2030','2100')) SELECT c.name,v.value jours_2100,round(v.value-v.preceding,2) difference_2030_2100 FROM v JOIN commune c ON c.code=v.commune_code WHERE period_id='2100' AND c.code IN ('75056','17300','13004','2A004','97411');

-- 06 Quels aléas sont recensés dans les communes ?
-- Recensement communal ; aucun logement individuel ne peut être déclaré exposé à partir de ce tableau.
SELECT h.label,count(*) communes FROM commune_hazard ch JOIN hazard h USING(hazard_id) GROUP BY h.hazard_id ORDER BY communes DESC;

-- 07 Combien de géométries d’aléas sont intégrées ?
-- Couverture locale Toulouse et Bordeaux seulement.
SELECT hazard_id,raw_id,count(*) zones FROM hazard_zone GROUP BY hazard_id,raw_id;

-- 08 Quelles surfaces géodésiques pour les enveloppes de Toulouse ?
-- Surfaces calculées sur ellipsoïde WGS84 après réparation documentée. Scénarios se recouvrant : ne pas sommer.
SELECT label,scenario,round(area_m2(geometry)/1000000,3) km2 FROM hazard_zone WHERE hazard_id='river_flood';

-- 09 Les lieux de test intersectent-ils les couches livrées ?
-- Absence d’intersection souvent hors couverture ; ne signifie jamais sans risque.
SELECT p.label,z.hazard_id,sum(i.intersects) intersections,count(*) zones_examinees FROM spatial_intersection i JOIN test_place p USING(place_id) JOIN hazard_zone z USING(zone_id) GROUP BY p.place_id,z.hazard_id;

-- 10 Quelles parcelles recoupent plusieurs zones ?
-- Échantillon de parcelles, pas inventaire national ; plusieurs zones n’interdisent pas automatiquement un projet.
SELECT p.parcel_id,count(*) zones FROM parcel p JOIN parcel_zone z USING(parcel_id) GROUP BY p.parcel_id HAVING count(*)>1;

-- 11 Quels documents ont des dates renseignées ?
-- Complétude des métadonnées ; une date ne suffit pas à prouver l’opposabilité.
SELECT count(*) documents,sum(approval_date IS NOT NULL AND approval_date!='') approbations,sum(publication_date IS NOT NULL AND publication_date!='') publications FROM urban_document;

-- 12 Comment se répartissent les occurrences retenues ?
-- Biais de prospection et de publication : aucune mesure d’abondance animale.
SELECT d.code,d.name,count(*) occurrences,count(DISTINCT s.site_id) collections FROM fossil_occurrence o JOIN fossil_site s USING(site_id) JOIN department d ON d.code=s.department GROUP BY d.code ORDER BY occurrences DESC;

-- 13 Quels intervalles géologiques sont documentés ?
-- Intervalles de datation ; pas années de découverte.
SELECT i.early_name,count(*) occurrences FROM fossil_occurrence o JOIN geological_interval i USING(interval_id) GROUP BY i.early_name ORDER BY occurrences DESC LIMIT 25;

-- 14 Quelle précision de localisation est déclarée ?
-- Les champs source restent déclaratifs ; les contours administratifs sont simplifiés à 100 m.
SELECT coordinate_basis,coordinate_precision,count(*) collections FROM fossil_site GROUP BY coordinate_basis,coordinate_precision ORDER BY collections DESC;

-- 15 Quelle couverture des médias par catégorie ?
-- Illustrations taxonomiques ; aucune photo n’est présentée comme un spécimen local exact.
SELECT m.category,count(DISTINCT m.media_id) images,count(DISTINCT tm.taxon_id) taxons,count(DISTINCT o.occurrence_id) occurrences,round(100.0*count(DISTINCT o.occurrence_id)/(SELECT count(*) FROM fossil_occurrence),3) couverture_pct FROM media m LEFT JOIN taxon_media tm USING(media_id) LEFT JOIN fossil_occurrence o USING(taxon_id) GROUP BY m.category;

-- 16 Quelles publications documentent le plus d’occurrences ?
-- Concentration bibliographique et non abondance paléontologique.
SELECT b.reference_id,substr(b.citation,1,150) citation,count(*) occurrences FROM bibliography b JOIN fossil_occurrence o USING(reference_id) GROUP BY b.reference_id ORDER BY occurrences DESC LIMIT 10;

-- 17 Sensibilité à une contrainte personnelle de chaleur ?
-- Sensibilité d’une contrainte choisie, sans score ni verdict immobilier. Un manque ne satisfait jamais la contrainte.
WITH thresholds(t) AS (VALUES(5),(10),(20)) SELECT t,c.name,v.value,CASE WHEN v.value IS NULL THEN 'à documenter' WHEN v.value<=t THEN 'seuil respecté sur cet indicateur' ELSE 'seuil dépassé' END resultat FROM thresholds CROSS JOIN test_place p JOIN commune c ON c.code=p.commune_code LEFT JOIN climate_value v ON v.commune_code=c.code AND v.indicator_id='S1' AND v.period_id='2050' AND v.season='annuel' ORDER BY t,c.name;

-- 18 Quelles provenances et volumes ont été conservés ?
-- Octets avant compression sans perte ; les dates décrivent la collecte et non la date des phénomènes.
SELECT s.producer,count(*) fichiers,sum(r.bytes) octets_originaux,min(r.retrieved_at) debut,max(r.retrieved_at) fin FROM raw_file r JOIN dataset_version d USING(version_id) JOIN source s USING(source_id) GROUP BY s.source_id;