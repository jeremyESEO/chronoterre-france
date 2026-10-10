# Analyses SQL réellement exécutées

Les fonctions area_m2 et intersects sont enregistrées par `python -m national.analyses`. Les autres requêtes sont du SQLite standard.

## 01 — Combien de communes ont une fiche climatique ?

Couverture des fiches, pas exhaustivité des indicateurs ni précision à une adresse.

```sql

SELECT (SELECT count(*) FROM commune) communes,(SELECT count(*) FROM climate_place) fiches,round(100.0*(SELECT count(*) FROM climate_place)/(SELECT count(*) FROM commune),2) couverture_pct;

```

```json

[
  {
    "communes": 34969,
    "fiches": 34938,
    "couverture_pct": 99.91
  }
]

```

1 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 02 — Quelle couverture climatique par domaine ?

Les domaines ultramarins restent distincts de la métropole.

```sql

SELECT domain,count(*) communes FROM climate_place GROUP BY domain ORDER BY communes DESC;

```

```json

[
  {
    "domain": "France hexagonale",
    "communes": 34746
  },
  {
    "domain": "Martinique",
    "communes": 34
  },
  {
    "domain": "Nouvelle-Calédonie",
    "communes": 33
  },
  {
    "domain": "Guadeloupe",
    "communes": 32
  },
  {
    "domain": "Réunion",
    "communes": 24
  },
  {
    "domain": "Guyane",
    "communes": 22
  },
  {
    "domain": "Polynésie-française-Société",
    "communes": 20
  },
  {
    "domain": "Mayotte",
    "communes": 17
  },
  {
    "domain": "Polynésie-française-Tuamotu",
    "communes": 4
  },
  {
    "domain": "Polynésie-française-Australes",
    "communes": 4
  },
  {
    "domain": "Saint-Martin-Saint-Barthélemy",
    "communes": 2
  }
]

```

11 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 03 — Combien de communes par indicateur à 2050 ?

Une commune peut avoir plusieurs saisons ; le dénominateur porte sur les communes.

```sql

SELECT i.indicator_id,i.label,i.unit,count(DISTINCT v.commune_code) communes FROM indicator i LEFT JOIN climate_value v ON v.indicator_id=i.indicator_id AND v.period_id='2050' GROUP BY i.indicator_id;

```

```json

[
  {
    "indicator_id": "AG1",
    "label": "Séquence sèche la plus longue",
    "unit": "j",
    "communes": 34938
  },
  {
    "indicator_id": "G1",
    "label": "Température moyenne",
    "unit": "°C",
    "communes": 34938
  },
  {
    "indicator_id": "G2",
    "label": "Jours de gel",
    "unit": "j/an",
    "communes": 34746
  },
  {
    "indicator_id": "G3",
    "label": "Cumul de précipitations",
    "unit": "mm",
    "communes": 34938
  },
  {
    "indicator_id": "G4",
    "label": "Jours avec précipitations",
    "unit": "j/saison",
    "communes": 34746
  },
  {
    "indicator_id": "R1",
    "label": "Jours de fortes précipitations",
    "unit": "j/saison",
    "communes": 34746
  },
  {
    "indicator_id": "R2",
    "label": "Précipitations quotidiennes remarquables",
    "unit": "mm/j",
    "communes": 34746
  },
  {
    "indicator_id": "R3",
    "label": "Élévation du niveau marin",
    "unit": "cm",
    "communes": 1091
  },
  {
    "indicator_id": "R4",
    "label": "Jours de danger météorologique de feu",
    "unit": "j/an",
    "communes": 34746
  },
  {
    "indicator_id": "R5",
    "label": "Jours avec sol sec",
    "unit": "j/saison",
    "communes": 34746
  },
  {
    "indicator_id": "S1",
    "label": "Jours très chauds",
    "unit": "j/an",
    "communes": 34809
  },
  {
    "indicator_id": "S2",
    "label": "Nuits chaudes",
    "unit": "nuits/an",
    "communes": 34746
  }
]

```

13 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 04 — Comment comparer les jours très chauds des lieux de test ?

Même indicateur et horizon ; les domaines et les références doivent aussi être examinés.

```sql

SELECT c.name,v.period_id,v.value,v.lower,v.upper,i.unit FROM test_place t JOIN commune c ON c.code=t.commune_code JOIN climate_value v ON v.commune_code=c.code JOIN indicator i USING(indicator_id) WHERE v.indicator_id='S1' AND v.season='annuel' AND v.period_id='2050' ORDER BY c.name;

```

```json

[
  {
    "name": "Ajaccio",
    "period_id": "2050",
    "value": 2.0,
    "lower": 0.88,
    "upper": 6.19,
    "unit": "j/an"
  },
  {
    "name": "Arles",
    "period_id": "2050",
    "value": 6.0,
    "lower": 1.98,
    "upper": 10.46,
    "unit": "j/an"
  },
  {
    "name": "Chamonix-Mont-Blanc",
    "period_id": "2050",
    "value": 0.0,
    "lower": 0.0,
    "upper": 0.33,
    "unit": "j/an"
  },
  {
    "name": "Guéret",
    "period_id": "2050",
    "value": 3.05,
    "lower": 1.53,
    "upper": 4.92,
    "unit": "j/an"
  },
  {
    "name": "La Rochelle",
    "period_id": "2050",
    "value": 2.75,
    "lower": 1.45,
    "upper": 3.79,
    "unit": "j/an"
  },
  {
    "name": "Paris",
    "period_id": "2050",
    "value": 4.3,
    "lower": 2.09,
    "upper": 5.74,
    "unit": "j/an"
  },
  {
    "name": "Rennes",
    "period_id": "2050",
    "value": 2.7,
    "lower": 1.05,
    "upper": 4.58,
    "unit": "j/an"
  },
  {
    "name": "Saint-Denis",
    "period_id": "2050",
    "value": 0.0,
    "lower": 0.0,
    "upper": 0.1,
    "unit": "j/an"
  },
  {
    "name": "Tours",
    "period_id": "2050",
    "value": 4.7,
    "lower": 2.41,
    "upper": 7.01,
    "unit": "j/an"
  }
]

```

9 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 05 — Quelle évolution publiée entre 2030 et 2100 ?

Différence entre niveaux publiés, pas prédiction annuelle ni interpolation.

```sql

WITH v AS (SELECT commune_code,period_id,value,LAG(value) OVER(PARTITION BY commune_code ORDER BY CAST(period_id AS INTEGER)) preceding FROM climate_value WHERE indicator_id='S1' AND season='annuel' AND period_id IN ('2030','2100')) SELECT c.name,v.value jours_2100,round(v.value-v.preceding,2) difference_2030_2100 FROM v JOIN commune c ON c.code=v.commune_code WHERE period_id='2100' AND c.code IN ('75056','17300','13004','2A004','97411');

```

```json

[
  {
    "name": "Arles",
    "jours_2100": 16.3,
    "difference_2030_2100": 13.1
  },
  {
    "name": "La Rochelle",
    "jours_2100": 6.55,
    "difference_2030_2100": 5.3
  },
  {
    "name": "Ajaccio",
    "jours_2100": 5.45,
    "difference_2030_2100": 4.3
  },
  {
    "name": "Paris",
    "jours_2100": 8.45,
    "difference_2030_2100": 6.15
  },
  {
    "name": "Saint-Denis",
    "jours_2100": 0.0,
    "difference_2030_2100": 0.0
  }
]

```

5 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 06 — Quels aléas sont recensés dans les communes ?

Recensement communal ; aucun logement individuel ne peut être déclaré exposé à partir de ce tableau.

```sql

SELECT h.label,count(*) communes FROM commune_hazard ch JOIN hazard h USING(hazard_id) GROUP BY h.hazard_id ORDER BY communes DESC;

```

```json

[
  {
    "label": "Retrait-gonflement des argiles",
    "communes": 34476
  },
  {
    "label": "Remontée de nappe",
    "communes": 34123
  },
  {
    "label": "Mouvement de terrain",
    "communes": 27345
  },
  {
    "label": "Inondation",
    "communes": 19261
  },
  {
    "label": "Feu de forêt",
    "communes": 9656
  },
  {
    "label": "risqueCotier",
    "communes": 1454
  },
  {
    "label": "icu",
    "communes": 951
  },
  {
    "label": "Avalanche",
    "communes": 639
  },
  {
    "label": "Recul du trait de côte",
    "communes": 126
  },
  {
    "label": "cyclone",
    "communes": 109
  },
  {
    "label": "feuForetDOM",
    "communes": 33
  },
  {
    "label": "cycloneNC",
    "communes": 33
  }
]

```

13 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 07 — Combien de géométries d’aléas sont intégrées ?

Couverture locale Toulouse et Bordeaux seulement.

```sql

SELECT hazard_id,raw_id,count(*) zones FROM hazard_zone GROUP BY hazard_id,raw_id;

```

```json

[
  {
    "hazard_id": "rga",
    "raw_id": "rga_bordeaux",
    "zones": 126
  },
  {
    "hazard_id": "river_flood",
    "raw_id": "flood_toulouse",
    "zones": 3
  }
]

```

2 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 08 — Quelles surfaces géodésiques pour les enveloppes de Toulouse ?

Surfaces calculées sur ellipsoïde WGS84 après réparation documentée. Scénarios se recouvrant : ne pas sommer.

```sql

SELECT label,scenario,round(area_m2(geometry)/1000000,3) km2 FROM hazard_zone WHERE hazard_id='river_flood';

```

```json

[
  {
    "label": "SIN_3",
    "scenario": "04Fai",
    "km2": 72.781
  },
  {
    "label": "SIN_2",
    "scenario": "02Moy",
    "km2": 56.523
  },
  {
    "label": "SIN_1",
    "scenario": "01For",
    "km2": 19.974
  }
]

```

3 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 09 — Les lieux de test intersectent-ils les couches livrées ?

Absence d’intersection souvent hors couverture ; ne signifie jamais sans risque.

```sql

SELECT p.label,z.hazard_id,sum(i.intersects) intersections,count(*) zones_examinees FROM spatial_intersection i JOIN test_place p USING(place_id) JOIN hazard_zone z USING(zone_id) GROUP BY p.place_id,z.hazard_id;

```

```json

[
  {
    "label": "Ajaccio - mairie",
    "hazard_id": "rga",
    "intersections": 0,
    "zones_examinees": 126
  },
  {
    "label": "Ajaccio - mairie",
    "hazard_id": "river_flood",
    "intersections": 0,
    "zones_examinees": 3
  },
  {
    "label": "Arles - centre",
    "hazard_id": "rga",
    "intersections": 0,
    "zones_examinees": 126
  },
  {
    "label": "Arles - centre",
    "hazard_id": "river_flood",
    "intersections": 0,
    "zones_examinees": 3
  },
  {
    "label": "Chamonix - centre",
    "hazard_id": "rga",
    "intersections": 0,
    "zones_examinees": 126
  },
  {
    "label": "Chamonix - centre",
    "hazard_id": "river_flood",
    "intersections": 0,
    "zones_examinees": 3
  },
  {
    "label": "Guéret - centre",
    "hazard_id": "rga",
    "intersections": 0,
    "zones_examinees": 126
  },
  {
    "label": "Guéret - centre",
    "hazard_id": "river_flood",
    "intersections": 0,
    "zones_examinees": 3
  },
  {
    "label": "La Rochelle - mairie",
    "hazard_id": "rga",
    "intersections": 0,
    "zones_examinees": 126
  },
  {
    "label": "La Rochelle - mairie",
    "hazard_id": "river_flood",
    "intersections": 0,
    "zones_examinees": 3
  },
  {
    "label": "Paris - Hôtel de Ville",
    "hazard_id": "rga",
    "intersections": 0,
    "zones_examinees": 126
  },
  {
    "label": "Paris - Hôtel de Ville",
    "hazard_id": "river_flood",
    "intersections": 0,
    "zones_examinees": 3
  }
]

```

18 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 10 — Quelles parcelles recoupent plusieurs zones ?

Échantillon de parcelles, pas inventaire national ; plusieurs zones n’interdisent pas automatiquement un projet.

```sql

SELECT p.parcel_id,count(*) zones FROM parcel p JOIN parcel_zone z USING(parcel_id) GROUP BY p.parcel_id HAVING count(*)>1;

```

```json

[
  {
    "parcel_id": "13004000AB0130",
    "zones": 2
  }
]

```

1 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 11 — Quels documents ont des dates renseignées ?

Complétude des métadonnées ; une date ne suffit pas à prouver l’opposabilité.

```sql

SELECT count(*) documents,sum(approval_date IS NOT NULL AND approval_date!='') approbations,sum(publication_date IS NOT NULL AND publication_date!='') publications FROM urban_document;

```

```json

[
  {
    "documents": 26,
    "approbations": 0,
    "publications": 26
  }
]

```

1 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 12 — Comment se répartissent les occurrences retenues ?

Biais de prospection et de publication : aucune mesure d’abondance animale.

```sql

SELECT d.code,d.name,count(*) occurrences,count(DISTINCT s.site_id) collections FROM fossil_occurrence o JOIN fossil_site s USING(site_id) JOIN department d ON d.code=s.department GROUP BY d.code ORDER BY occurrences DESC;

```

```json

[
  {
    "code": "26",
    "name": "Drôme",
    "occurrences": 3018,
    "collections": 375
  },
  {
    "code": "40",
    "name": "Landes",
    "occurrences": 2791,
    "collections": 447
  },
  {
    "code": "34",
    "name": "Hérault",
    "occurrences": 2014,
    "collections": 383
  },
  {
    "code": "74",
    "name": "Haute-Savoie",
    "occurrences": 1613,
    "collections": 176
  },
  {
    "code": "04",
    "name": "Alpes-de-Haute-Provence",
    "occurrences": 1612,
    "collections": 329
  },
  {
    "code": "14",
    "name": "Calvados",
    "occurrences": 1543,
    "collections": 207
  },
  {
    "code": "11",
    "name": "Aude",
    "occurrences": 1457,
    "collections": 418
  },
  {
    "code": "01",
    "name": "Ain",
    "occurrences": 1386,
    "collections": 214
  },
  {
    "code": "13",
    "name": "Bouches-du-Rhône",
    "occurrences": 1287,
    "collections": 168
  },
  {
    "code": "62",
    "name": "Pas-de-Calais",
    "occurrences": 1275,
    "collections": 177
  },
  {
    "code": "60",
    "name": "Oise",
    "occurrences": 1153,
    "collections": 90
  },
  {
    "code": "12",
    "name": "Aveyron",
    "occurrences": 1076,
    "collections": 424
  }
]

```

95 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 13 — Quels intervalles géologiques sont documentés ?

Intervalles de datation ; pas années de découverte.

```sql

SELECT i.early_name,count(*) occurrences FROM fossil_occurrence o JOIN geological_interval i USING(interval_id) GROUP BY i.early_name ORDER BY occurrences DESC LIMIT 25;

```

```json

[
  {
    "early_name": "Lutetian",
    "occurrences": 2119
  },
  {
    "early_name": "Middle Oxfordian",
    "occurrences": 1785
  },
  {
    "early_name": "Late Valanginian",
    "occurrences": 1628
  },
  {
    "early_name": "Early Hauterivian",
    "occurrences": 1511
  },
  {
    "early_name": "Bartonian",
    "occurrences": 1374
  },
  {
    "early_name": "Chattian",
    "occurrences": 1223
  },
  {
    "early_name": "Ypresian",
    "occurrences": 1130
  },
  {
    "early_name": "Burdigalian",
    "occurrences": 1126
  },
  {
    "early_name": "Late Albian",
    "occurrences": 964
  },
  {
    "early_name": "Late Oxfordian",
    "occurrences": 951
  },
  {
    "early_name": "Aquitanian",
    "occurrences": 928
  },
  {
    "early_name": "Langhian",
    "occurrences": 915
  }
]

```

25 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 14 — Quelle précision de localisation est déclarée ?

Les champs source restent déclaratifs ; les contours administratifs sont simplifiés à 100 m.

```sql

SELECT coordinate_basis,coordinate_precision,count(*) collections FROM fossil_site GROUP BY coordinate_basis,coordinate_precision ORDER BY collections DESC;

```

```json

[
  {
    "coordinate_basis": "based on nearby landmark",
    "coordinate_precision": "3",
    "collections": 1497
  },
  {
    "coordinate_basis": "based on nearby landmark",
    "coordinate_precision": "2",
    "collections": 1040
  },
  {
    "coordinate_basis": "based on nearby landmark",
    "coordinate_precision": "minutes",
    "collections": 906
  },
  {
    "coordinate_basis": "estimated from map",
    "coordinate_precision": "4",
    "collections": 595
  },
  {
    "coordinate_basis": "based on nearby landmark",
    "coordinate_precision": "seconds",
    "collections": 561
  },
  {
    "coordinate_basis": "estimated from map",
    "coordinate_precision": "seconds",
    "collections": 477
  },
  {
    "coordinate_basis": "stated in text",
    "coordinate_precision": "seconds",
    "collections": 421
  },
  {
    "coordinate_basis": "estimated from map",
    "coordinate_precision": "3",
    "collections": 393
  },
  {
    "coordinate_basis": "estimated from map",
    "coordinate_precision": "minutes",
    "collections": 336
  },
  {
    "coordinate_basis": null,
    "coordinate_precision": "minutes",
    "collections": 201
  },
  {
    "coordinate_basis": "based on nearby landmark",
    "coordinate_precision": "1",
    "collections": 165
  },
  {
    "coordinate_basis": "estimated from map",
    "coordinate_precision": "2",
    "collections": 165
  }
]

```

40 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 15 — Quelle couverture des médias par catégorie ?

Illustrations taxonomiques ; aucune photo n’est présentée comme un spécimen local exact.

```sql

SELECT m.category,count(DISTINCT m.media_id) images,count(DISTINCT tm.taxon_id) taxons,count(DISTINCT o.occurrence_id) occurrences,round(100.0*count(DISTINCT o.occurrence_id)/(SELECT count(*) FROM fossil_occurrence),3) couverture_pct FROM media m LEFT JOIN taxon_media tm USING(media_id) LEFT JOIN fossil_occurrence o USING(taxon_id) GROUP BY m.category;

```

```json

[
  {
    "category": "fossil",
    "images": 4,
    "taxons": 12,
    "occurrences": 491,
    "couverture_pct": 1.02
  },
  {
    "category": "organism",
    "images": 1,
    "taxons": 1,
    "occurrences": 10,
    "couverture_pct": 0.021
  }
]

```

2 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 16 — Quelles publications documentent le plus d’occurrences ?

Concentration bibliographique et non abondance paléontologique.

```sql

SELECT b.reference_id,substr(b.citation,1,150) citation,count(*) occurrences FROM bibliography b JOIN fossil_occurrence o USING(reference_id) GROUP BY b.reference_id ORDER BY occurrences DESC LIMIT 10;

```

```json

[
  {
    "reference_id": "68770",
    "citation": "S. Reboulet. 1996. L'évolution des ammonites du Valanginien-Hauterivien inférieur du bassin Vocontien et de la plate-form Provençale (sud-est de la Fr",
    "occurrences": 2554
  },
  {
    "reference_id": "15196",
    "citation": "M. Delamette, J. Charollais, and D. Decrouez, M. Caron. 1997. Les grès verts helvétiques (Aptien moyen-Albien supérieur) de Haute-Savoie, Valais et Va",
    "occurrences": 1512
  },
  {
    "reference_id": "47284",
    "citation": "C. Meister. 1986. Les ammonites du Carixien des Causses (France). Schweizerische Paläontologische Abhandlungen 109:1-209",
    "occurrences": 984
  },
  {
    "reference_id": "41",
    "citation": "F. T. Fürsich. 1999. Unpublished data.",
    "occurrences": 876
  },
  {
    "reference_id": "53744",
    "citation": "Y. Alméras. 1970. Les terebratulidae du Dogger dans le Mâconnais, le mont d'Or lyonnais et le Jura méridional: Étude systématique et biostratigraphiqu",
    "occurrences": 868
  },
  {
    "reference_id": "32631",
    "citation": "J. -C. Fischer. 1969. Geologie, Paleontologie et Paleoecologie du Bathonien au sud-ouest du Massif Ardennais. Memoires du Museum National D'Histoire N",
    "occurrences": 853
  },
  {
    "reference_id": "66",
    "citation": "A. Jaccard. 1869. Jura Vaudois et Neuchatelois. Matériaux pour la carte géologique de la Suisse 6:1-340",
    "occurrences": 663
  },
  {
    "reference_id": "52216",
    "citation": "Y. Alméras and P. Fauré. 2000. Les brachiopodes liasiques des Pyrénées: paléontologie, biostratigraphie, paléobiogéographie et paléoenvironnements. St",
    "occurrences": 649
  },
  {
    "reference_id": "42882",
    "citation": "M. Bécaud. 2006. Les Harpoceratinae, Hildoceratinae et Parinoceratinae du Toarcien de la Vendée et des Deux-Sèvres (France). Documents des Laboratoire",
    "occurrences": 424
  },
  {
    "reference_id": "4230",
    "citation": "R. Enay. 1966. L'Oxfordien dans la moitié sud du Jura francais - etude stratigraphique. Documents des laboratoires de géologie de la faculté des scièn",
    "occurrences": 415
  }
]

```

10 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 17 — Sensibilité à une contrainte personnelle de chaleur ?

Sensibilité d’une contrainte choisie, sans score ni verdict immobilier. Un manque ne satisfait jamais la contrainte.

```sql

WITH thresholds(t) AS (VALUES(5),(10),(20)) SELECT t,c.name,v.value,CASE WHEN v.value IS NULL THEN 'à documenter' WHEN v.value<=t THEN 'seuil respecté sur cet indicateur' ELSE 'seuil dépassé' END resultat FROM thresholds CROSS JOIN test_place p JOIN commune c ON c.code=p.commune_code LEFT JOIN climate_value v ON v.commune_code=c.code AND v.indicator_id='S1' AND v.period_id='2050' AND v.season='annuel' ORDER BY t,c.name;

```

```json

[
  {
    "t": 5,
    "name": "Ajaccio",
    "value": 2.0,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 5,
    "name": "Arles",
    "value": 6.0,
    "resultat": "seuil dépassé"
  },
  {
    "t": 5,
    "name": "Chamonix-Mont-Blanc",
    "value": 0.0,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 5,
    "name": "Guéret",
    "value": 3.05,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 5,
    "name": "La Rochelle",
    "value": 2.75,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 5,
    "name": "Paris",
    "value": 4.3,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 5,
    "name": "Rennes",
    "value": 2.7,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 5,
    "name": "Saint-Denis",
    "value": 0.0,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 5,
    "name": "Tours",
    "value": 4.7,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 10,
    "name": "Ajaccio",
    "value": 2.0,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 10,
    "name": "Arles",
    "value": 6.0,
    "resultat": "seuil respecté sur cet indicateur"
  },
  {
    "t": 10,
    "name": "Chamonix-Mont-Blanc",
    "value": 0.0,
    "resultat": "seuil respecté sur cet indicateur"
  }
]

```

27 lignes calculées ; résultat intégral dans reports/france_analyses.json.

## 18 — Quelles provenances et volumes ont été conservés ?

Octets avant compression sans perte ; les dates décrivent la collecte et non la date des phénomènes.

```sql

SELECT s.producer,count(*) fichiers,sum(r.bytes) octets_originaux,min(r.retrieved_at) debut,max(r.retrieved_at) fin FROM raw_file r JOIN dataset_version d USING(version_id) JOIN source s USING(source_id) GROUP BY s.source_id;

```

```json

[
  {
    "producer": "Bordeaux Métropole / BRGM",
    "fichiers": 2,
    "octets_originaux": 1314890,
    "debut": "2026-09-25T13:40:30.263134+00:00",
    "fin": "2026-09-25T13:40:38.341883+00:00"
  },
  {
    "producer": "DGFiP / IGN",
    "fichiers": 9,
    "octets_originaux": 3663,
    "debut": "2026-09-25T13:38:01.853426+00:00",
    "fin": "2026-09-25T13:44:27.471173+00:00"
  },
  {
    "producer": "Météo-France / DRIAS / BRGM pour le niveau marin",
    "fichiers": 1,
    "octets_originaux": 404250373,
    "debut": "2026-09-25T13:44:38.503615+00:00",
    "fin": "2026-09-25T13:44:38.503615+00:00"
  },
  {
    "producer": "DREAL Occitanie",
    "fichiers": 1,
    "octets_originaux": 543545,
    "debut": "2026-09-25T13:40:21.931334+00:00",
    "fin": "2026-09-25T13:40:21.931334+00:00"
  },
  {
    "producer": "Etalab / IGN ADMIN EXPRESS 2025",
    "fichiers": 1,
    "octets_originaux": 2753929,
    "debut": "2026-09-25T13:28:49.125462+00:00",
    "fin": "2026-09-25T13:28:49.125462+00:00"
  },
  {
    "producer": "DINUM / IGN / INSEE",
    "fichiers": 1,
    "octets_originaux": 6235656,
    "debut": "2026-09-25T13:28:35.333494+00:00",
    "fin": "2026-09-25T13:28:35.333494+00:00"
  },
  {
    "producer": "IGN / collectivités / Géoportail de l’urbanisme",
    "fichiers": 36,
    "octets_originaux": 8311133,
    "debut": "2026-09-25T13:38:09.150925+00:00",
    "fin": "2026-09-25T13:45:16.675736+00:00"
  },
  {
    "producer": "Paleobiology Database, contributeurs et publications citées",
    "fichiers": 7,
    "octets_originaux": 60777863,
    "debut": "2026-09-25T13:31:00.380679+00:00",
    "fin": "2026-09-25T13:32:04.964900+00:00"
  }
]

```

8 lignes calculées ; résultat intégral dans reports/france_analyses.json.