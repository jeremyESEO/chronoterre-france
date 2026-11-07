"""Documentation dérivée du schéma et des résultats, sans compteurs saisis à la main."""
import json,sqlite3,hashlib,shutil
from pathlib import Path
from national.collect import ROOT,dump
from national.validate import RULES
D=ROOT/'docs';D.mkdir(exist_ok=True)
def write(name,text): (D/name).write_text(text.strip()+'\n',encoding='utf-8')
db=sqlite3.connect('file:'+str(ROOT/'data/curated/france.sqlite')+'?mode=ro',uri=True)
grains={'source':'un producteur ou diffuseur avec ses conditions','dataset_version':'une ressource collectée à une date','raw_file':'une réponse originale immuable','department':'un contour départemental simplifié millésimé','commune':'une commune du référentiel collecté, code INSEE texte','postal_code':'une association commune-code postal, plusieurs-à-plusieurs','climate_place':'une commune avec sa méthode climatique et sa référence','scenario':'une nature de projection (TRACC ou référence)','climate_model':'un ensemble de modèles publié, sans prétendre disposer des simulations individuelles','period':'un horizon publié ; bornes annuelles NULL lorsqu’elles ne sont pas fournies','indicator':'une variable, sa définition et son unité canonique','climate_value':'une commune × indicateur × horizon × saison pour le corpus Climadiag retenu','hazard':'une famille d’aléa ou de risque recensé','commune_hazard':'une commune × aléa recensé, sans intersection à l’adresse','bibliography':'une référence bibliographique PBDB','taxon':'un identifiant taxonomique accepté PBDB','geological_interval':'un intervalle d’âge et ses bornes en millions d’années','fossil_site':'une collection PBDB localisée retenue ; plusieurs collections peuvent partager un point','fossil_occurrence':'un enregistrement bibliographique de taxon dans une collection, pas un animal','media':'un fichier et sa provenance, auteur, licence et légende','taxon_media':'une association taxon-image, avec niveau de correspondance','test_place':'un lieu public choisi pour tester la couverture','parcel':'une parcelle cadastrale de l’échantillon public','urban_document':'un document identifié par le fournisseur, avec dates connues','urban_zone':'une géométrie de zonage et son règlement lié','prescription':'une prescription surfacique ou une servitude collectée','parcel_zone':'une intersection parcelle-zone réelle, relation plusieurs-à-plusieurs','hazard_zone':'une enveloppe d’aléa et son scénario dans une version source','spatial_intersection':'un lieu de test × enveloppe avec résultat booléen'}
parts=['# Dictionnaire et modèle logique','SQLite 3, clés étrangères activées lors de la construction ; colonnes normalisées, GeoJSON uniquement pour les géométries. Les octets bruts restent séparés. Les tables RTree sont des index techniques, pas des domaines métier.']
for name,grain in grains.items():
 cols=db.execute('PRAGMA table_info('+name+')').fetchall();fks=db.execute('PRAGMA foreign_key_list('+name+')').fetchall();parts+=['## '+name,'Une ligne représente '+grain+'.','| Champ | Type | Obligatoire | Clé primaire |','|---|---|---|---|']
 for _,col,typ,req,default,pk in cols:parts.append(f'| {col} | {typ} | {"oui" if req or pk else "non"} | {pk or "—"} |')
 if fks:parts.append('Relations : '+ '; '.join(f'{f[3]} → {f[2]}.{f[4] or "clé primaire"}' for f in fks)+'.')
parts+=['## Choix et limites','Les identifiants INSEE sont des chaînes (Corse 2A/2B). Aucun rapprochement par simple nom. Les clés PBDB sont conservées. climate_value utilise une clé composite et WITHOUT ROWID ; ajouter plusieurs corpus ou modèles individuels imposerait une migration élargissant cette clé, et non un INSERT OR IGNORE silencieux. Les références géologiques conservent leurs bornes, pas un faux âge exact.','Index : commune(name), commune(department), climate_value(indicator_id,period_id,season), fossil_occurrence(site_id/taxon_id), RTree fossil_index. Les enveloppes locales sont peu nombreuses ; leurs intersections utilisent GEOS. Une base nationale de parcelles/aléas nécessiterait PostGIS et GiST. Les mises à jour communales ne sont pas réconciliées historiquement : une fiche sans code commun au millésime collecté est exclue et comptée.']
write('dictionnaire_france.md','\n\n'.join(parts))
write('modele_france.mmd','''erDiagram
 SOURCE ||--o{ DATASET_VERSION : publie
 DATASET_VERSION ||--o{ RAW_FILE : conserve
 COMMUNE ||--o{ CLIMATE_VALUE : situe
 INDICATOR ||--o{ CLIMATE_VALUE : definit
 PERIOD ||--o{ CLIMATE_VALUE : borne
 COMMUNE ||--o{ COMMUNE_HAZARD : recense
 HAZARD ||--o{ COMMUNE_HAZARD : qualifie
 FOSSIL_SITE ||--o{ FOSSIL_OCCURRENCE : regroupe
 TAXON ||--o{ FOSSIL_OCCURRENCE : identifie
 BIBLIOGRAPHY ||--o{ FOSSIL_OCCURRENCE : documente
 TAXON ||--o{ TAXON_MEDIA : illustre
 MEDIA ||--o{ TAXON_MEDIA : associe
 PARCEL ||--o{ PARCEL_ZONE : intersecte
 URBAN_ZONE ||--o{ PARCEL_ZONE : intersecte
 URBAN_DOCUMENT ||--o{ URBAN_ZONE : definit
''')
write('architecture_france.mmd','''flowchart TD
 A["Producteurs : MF, PBDB, IGN, DREAL, BRGM"] --> B["Collecteurs Python : délais et reprises bornées"]
 B --> C["Raw horodaté + manifeste + SHA-256"]
 C --> D["Profilage puis contrôles versionnés"]
 D --> E["Rejets motivés et journal des réparations"]
 D --> F["SQLite : contraintes et index RTree"]
 F --> G["Instantanés par département"]
 F --> H["API locale Python"]
 G --> I["Carte MapLibre et fiches"]
 I --> J["Services publics IGN au clic"]
 F --> K["18 analyses SQL et rapport académique"]
''')
dump(ROOT/'config/france_contract.json',{'dataset':'chronoterre_france','version':'2.0.1','owner':'Projet académique ESEO ChronoTerre','grains':grains,'crs':'EPSG:4326 ; distances géodésiques/haversine, surfaces ellipsoïdales WGS84','required_fossil_fields':['occurrence_no','collection_no','identified_name','reference_no','primary_reference','min_ma','max_ma'],'quality_rules':{k:{'name':v[0],'condition':v[1],'action':v[2]} for k,v in RULES.items()},'transformations':['code INSEE texte','NIVMER mètres bruts ×100 → cm','make_valid GEOS pour enveloppes invalides, journal sans modifier raw','aucune interpolation climatique','fossiles localisés sur contours départementaux 100 m'],'missing_data':'NULL ou absence explicitement présentée ; jamais zéro imputé','version_policy':'nouveau schéma ou sens de variable : arrêter, examiner, incrémenter le contrat et reconstruire'})
write('methode_france.md','''# Méthode et corrections de l’audit

La V1 est conservée dans une archive et une base distinctes. Ses 255 670 journées ne deviennent pas des projections nationales. La série ERA5 / Open-Meteo 1991–2020 et 2030–2049 reste consultable dans la V1 ; elle n’est pas soustraite à DRIAS. Les analogues climatiques ne sont pas réutilisés sans validation supplémentaire.

## Climat

Le JSONL réellement utilisé par l’application publique Climadiag est archivé sans modification (compression gzip réversible). Les communes sont jointes par code INSEE. EPCI et codes absents du référentiel sont comptés séparément. Un champ `mean` correspond ici à la médiane affichée par le fournisseur, ce que confirme son code public, conservé dans les preuves documentaires. Les bornes sont reprises, sans recalcul de quantiles ni interprétation comme probabilité d’habitabilité. Les fenêtres annuelles propres aux simulations ne figurent pas dans cet export : les colonnes de début et fin de période restent NULL.

Métropole : référence 1976–2005 ; outre-mer : 1991–2020 ; niveau marin : 1995–2014. Le niveau marin NIVMER brut est exprimé en mètres ; l’afficheur Climadiag applique une multiplication par 100. Cette conversion en cm est testée sur La Rochelle : 0,24 m brut → 24 cm en 2050. Ni cette valeur ni une altitude ne produisent une carte de submersion. Source BRGM de l’indicateur : https://doi.org/10.5802/crgeos.290 (lien indiqué par Climadiag ; article non inspecté intégralement dans cette session).

TRACC, horizon, modèle et scénario d’émissions sont des concepts distincts. L’application propose seulement les niveaux publiés pour 2030, 2050 et 2100. Pas de scénario alternatif, pas de prolongement Open-Meteo à 2076. Le +50 ans est calculé à partir de la date de référence 2026. Les seuils textuels 35 °C et 20 °C présentent une divergence entre titres et descriptions Climadiag : les valeurs agrégées restent celles reçues.

## Géographie et aléas

Coordonnées modernes WGS84 (EPSG:4326). Fonds web en pseudo-Mercator par le moteur de carte ; cette projection n’est jamais utilisée ici pour calculer une surface. Distances exploratoires haversine avec rayon terrestre moyen 6371,0088 km ; analyses de surface sur ellipsoïde WGS84 avec PyProj.Geod. Les contours administratifs simplifiés à 100 m limitent la précision des rattachements proches des frontières. Une maille climatique de 8 km ne devient pas une donnée de rue quand on zoome.

Deux enveloppes Toulouse présentent une topologie invalide (composante dégénérée et auto-intersection). GEOS make_valid rétablit une topologie valide, en conservant les composantes polygonales, et journalise l’opération. Les raw ne changent pas. Cette réparation technique ne vaut pas validation hydrologique et les tracés doivent être confrontés au portail producteur avant un usage réglementaire. Une géométrie urbaine invalide est rejetée. Les tests utilisent un point intérieur construit sur l’enveloppe et un point extérieur ; ce sont des coordonnées de test, pas des observations nouvelles.

Les scénarios de crue conservent leurs codes source ; aucune hauteur d’eau ou période de retour locale n’est inventée. Dossier pédagogique : https://www.georisques.gouv.fr/consulter-les-dossiers-thematiques/dossier-expert-sur-les-inondations . Le résultat d’intersection ne mesure ni population exposée, ni dommage, ni vulnérabilité du bâti.

## Fossiles et médias

PBDB : collections et occurrences paginées séparément, bibliographie et taxonomie normalisées. Exclusion des centroïdes politiques déclarés, des points hors contours français retenus, des contradictions départementales et des six collections explicitement problématiques de la V1. Aucun déplacement automatique vers un nom de ville. Les paléocoordonnées, institutions de conservation non vérifiées, tailles et reconstitutions sans source ne sont pas inventées.

Cinq médias Commons vérifiés : quatre spécimens illustratifs et une reconstitution publiée. Le squelette de Durfort est conservé au MNHN à Paris ; son musée n’est pas assimilé à son lieu de découverte. Les correspondances sont même taxon ou même genre, jamais spécimen local exact. Les fiches sans image affichent cette absence. L’aérien montre un secteur sans garantir une découverte à un numéro de rue ; l’année exacte de chaque tuile n’est pas connue.

## Comparaison

Profil multicritère sans score global. Les priorités sélectionnent les indicateurs affichés. La contrainte personnelle de chaleur compare une médiane à un seuil choisi et signale les manques ; ce n’est ni une norme sanitaire ni un verdict immobilier. Une exigence d’étude locale d’inondation reste à vérifier tant que la couverture n’est pas démontrée. Les domaines ultramarins et leurs saisons ne doivent pas être assimilés aux saisons métropolitaines. Fossiles et images n’interviennent pas dans le résultat.

## Urbanisme

API Carto : point → parcelle, puis géométrie entière de la première parcelle retournée → documents, zones, prescriptions surfaciques et servitudes surfaciques. Les objets linéaires et ponctuels de prescriptions ne sont pas intégrés ; les documents de PPR ne sont pas classés automatiquement par statut juridique. Les dates non fournies restent inconnues. Document U/AU, cadastre et intersection ne suffisent pas à autoriser une construction. Référence officielle : https://www.service-public.gouv.fr/particuliers/vosdroits/F1633 .
''')
write('api_france.md','''# API locale v2

Lancer `python -m national.serve`, base restaurée. Serveur lié à 127.0.0.1, lecture seule, sans journal de requêtes. Le serveur standard Python est destiné à la démonstration locale ; il ne constitue pas une infrastructure publique durcie.

| Route GET | Paramètres | Résultat / limites |
|---|---|---|
| /api/v2/health | aucun | intégrité SQLite |
| /api/v2/meta | aucun | sources, compteurs, couverture |
| /api/v2/search | q, limit=10 | commune/code postal ; q 2–120 caractères, limite 1–30 |
| /api/v2/climate | code, horizon=2050 | référence ou 2030/2050/2100 ; 2076 refusé |
| /api/v2/fossils | bbox, limit=100, after, class, taxon | emprise maximale 40°×30°, limite 1–500 ; curseur next_after |
| /api/v2/sites/{id} | identifiant PBDB | localité et occurrences |
| /api/v2/hazards/point | lon, lat | intersections GEOS avec couches livrées |
| /api/v2/urban | lon, lat, layer | proxy à liste fermée, au point uniquement, délai 15 s ; parcelle/document/zone-urba/prescription-surf/assiette-sup-s |

Exemples :

```text
http://127.0.0.1:8000/api/v2/search?q=17000
http://127.0.0.1:8000/api/v2/climate?code=17300&horizon=2100
http://127.0.0.1:8000/api/v2/fossils?bbox=-5,42,10,52&limit=10
http://127.0.0.1:8000/api/v2/hazards/point?lon=1.44&lat=43.60
```

Erreurs JSON : 400 paramètre invalide, 404 route/fiche absente, 503 fournisseur ou dépendance indisponible, 500 erreur interne sans valeur de remplacement. Le proxy local urbanisme reste une lecture au point ; l’interface utilise directement API Carto pour les intersections de parcelle complète. Aucune clé dans le navigateur. L’API de recherche locale ne géocode pas les adresses : le navigateur utilise l’IGN.

Instantanés Web : `dist/data/meta.json` décrit les colonnes des tableaux compacts de `climate/{département}.json` et `fossils/{département}.json`. Chaque valeur provient de SQLite. `communes.json`, `sites.json`, `references.json`, `media.json`, `hazards.geojson` complètent ces données. Les JSON exportés par l’interface conservent définition des indicateurs, unités, période, provenance et limites.
''')
write('sources_france.md','''# Matrice des sources et accès

Collecte nationale de référence : 25 septembre 2026. Reprise et tests : octobre 2026. Les horodatages réels et réponses figurent dans les manifestes ; aucune disponibilité permanente n’est promise. Les quotas chiffrés non confirmés restent « non établis », jamais illimités par supposition. Collectes séquentielles, temporisations et trois tentatives bornées pour le collecteur général. L’export climatique est en flux, cache vérifié, sans abonnement à une API privée.

| Source / accès exact | Licence et authentification | Couverture, grain et période | État, quotas, mise à jour |
|---|---|---|---|
| DINUM/IGN/INSEE — https://geo.api.gouv.fr/communes?fields=nom,code,codeDepartement,codeRegion,codesPostaux,centre,population&format=json | Licence Ouverte ; sans clé | communes du référentiel reçu, centres administratifs WGS84 | réponse nationale archivée ; quota non établi ; refresh manuel |
| Etalab/IGN — https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-100m.geojson | Licence Ouverte 2.0 ; sans clé | millésime 2025, contours 100 m, métropole et territoires présents | intégré ; pas une limite cadastrale |
| Météo-France — https://climadiag-commune.meteofrance.com/entities.jsonl | données publiques MF / DRIAS Etalab ; sans clé pour cet export public | fiches communales et EPCI, domaines séparés, niveaux TRACC 2030/2050/2100 | archivé 404 250 373 octets d’origine ; pas d’API contractuelle, changement possible |
| DRIAS — https://www.drias-climat.fr/accompagnement/sections/475 ; conditions https://www.drias-climat.fr/accompagnement/conditionsEDC | licence Etalab, accès aux exports détaillés selon portail | documentation des niveaux de réchauffement ; aucune simulation quotidienne importée | méthode consultée ; connecteur NetCDF non réalisé |
| PBDB — https://paleobiodb.org/data1.2/occs/list.json et colls/list.json | CC BY 4.0 ; sans clé ; https://github.com/paleobiodb/navigator | pays FR, pages de 10 000, coordonnées modernes et âges géologiques | réellement intégré ; offset/limit, quotas non établis, collecte manuelle |
| IGN Géoplateforme — https://data.geopf.fr/wmts ; https://data.geopf.fr/geocodage/search | fonds ouverts attribués IGN/DGFiP ; services publics sans clé pour les couches retenues | plan, ortho actuelle, pentes, cadastre, ortho 1950–1965 ; dates de prises de vue variables | couches issues du GetCapabilities ; pas de téléchargement massif des tuiles ; pas de SLA revendiqué |
| IGN API Carto — https://apicarto.ign.fr/api/doc/gpu.yml et cadastre.yml | Licence Ouverte pour données géographiques publiques ; textes selon producteur ; sans clé | parcelle/document/zone-urba/prescription-surf/assiette-sup-s ; EPSG:4326 | 45 réponses réelles pour neuf points ; live au clic, cache livré ; quotas non établis |
| Géorisques — https://www.georisques.gouv.fr/doc-api | données publiques selon jeu ; certaines API nécessitent jeton | inventaire communal via Climadiag ; pas d’enveloppes nationales intégrées | accès directs précédemment en échec 502/HTML ; aucun contournement ni jeton inventé |
| DREAL Occitanie — https://catalogue.picto-occitanie.fr/api/data/7c91530f-6a26-41e5-9dee-19adec8af824?srs=EPSG:4326 | vérifier fiche originale : métadonnée de licence manquante sur la copie data.gouv | trois surfaces Toulouse, source 2013, scénarios codés | accès testé et raw conservé ; topologie réparée et journalisée ; conditions détaillées dans complément de licence |
| Bordeaux Métropole/BRGM — https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_alearga_s/exports/geojson | Licence Ouverte, lien exact conservé dans le raw ri_alearga_s metadata | 127 objets bruts (126 géométries retenues), secteur Bordeaux uniquement | export et métadonnées intégrés ; horodatage d’export ≠ nouvelle étude géologique |
| Commons et auteurs — pages de chaque fichier dans media_registry.json | CC BY / CC BY-SA par fichier, auteurs conservés | cinq fichiers, même taxon ou genre | contrôles individuels ; pas le premier résultat automatique ; couverture calculée SQL 15 |
| Open-Meteo — https://open-meteo.com/en/docs/climate-api | conditions Open-Meteo et attribution CMIP6 ; voir V1 | documentation jusqu’à 2050 | conservé dans V1 seulement ; exclu de +50 ans |
| Explore2 / DRIAS-Eau — https://www.drias-eau.fr/ | à vérifier par export ; pas de clé contournée | débits/bassins, pas coupure d’eau à l’adresse | candidat, non intégré |
| Cerema/GéoLittoral, IPR | à vérifier par jeu | recul du trait de côte / chaleur urbaine locale | candidats, non intégrés ; aucune généralisation nationale |
| GBIF, MNHN | licences variables par donnée/média | spécimens et collections | candidats, pas de connecteur opérationnel livré |
| Panoramax — https://docs.panoramax.fr/ ; IGN Remonter le temps — https://remonterletemps.ign.fr/ | conditions par service/image | vues de lieux / archives aériennes | inspection documentaire uniquement ; pas de galerie de rue intégrée |

## Inspirations réellement inspectées

Climadiag : code public, métadonnées et réponse JSONL, repris pour séparation horizon/domaine et lecture par indicateur. GPU : documentation API et vraies réponses spatiales, repris pour la fiche de parcelle. PBDB : API paginée et collections/références, repris pour filtres spatiaux/taxonomiques. IGN : documentation et capabilities, repris pour fonds et attribution. Géorisques : documentation et essais en échec, pas d’inspection complète d’un parcours authentifié. Panoramax et Remonter le temps : pages/documentation seulement ; aucune prétention d’audit visuel approfondi.
''')
write('soutenance_france.md','''# Démonstration de 3 à 5 minutes

0:00–0:30 : question, usagers, deux parcours reliés par le territoire. Dire que la plateforme nationale est une extension du socle TP.

0:30–1:00 : ouvrir un manifeste, montrer URL, date, SHA et fichier raw d’origine. Expliquer que le ZIP climatique est une compression sans perte.

1:00–2:00 : exécuter `python -m national.demo`. Montrer la page PBDB réelle, le rejet `TEST_INVALIDE_ISOLE`, les effectifs et l’égalité des deux empreintes. Ouvrir `data/curated/demo_tp.sqlite`. La donnée invalide ne touche jamais la production.

2:00–3:15 : application : rechercher La Rochelle, passer 2030 → 2100, afficher les preuves. Comparer Ajaccio. Signaler la maille climatique, le +50 ans désactivé et l’absence de score d’habitabilité. Cette partie doit être répétée dans un navigateur avant la soutenance, la QA visuelle n’ayant pas été possible dans la session de livraison.

3:15–4:15 : passer aux fossiles, filtre taxonomique, découvrir une publication. Présenter une image illustrative et sa licence ; montrer aussi le cas sans image.

4:15–5:00 : SQL 15 couverture des médias, rapport de qualité et une limite : seulement deux couches locales d’aléas. Montrer la sauvegarde V1.

## Réponses techniques

- Décision : comparer des expositions documentées et préparer les vérifications, sans décider un achat.
- Choix des sources : producteurs identifiés, accès public réellement essayé, identifiants stables et provenance conservée.
- Clé métier : occurrence_no PBDB ; climat = commune + indicateur + période + saison dans ce corpus unique.
- Rejeu : base reconstruite atomiquement ; empreinte canonique des lignes triées de toutes les tables applicatives. Identité des clés et du contenu.
- Source en panne : cache existant et état d’erreur explicite ; aucune valeur fictive. Mise à jour manuelle.
- Changement de schéma : arrêt sur champ indispensable manquant, examen du raw, nouvelle version de contrat. Pas de changement silencieux de sens.
- Production nationale spatiale : PostgreSQL/PostGIS, jobs d’import, stockage de fichiers, supervision, quotas et revue de licences ; le serveur local n’est pas exposé tel quel.
- Pourquoi pas 2076 : les données proposent des niveaux/horizons, pas une trajectoire annuelle interpolable.
- Pourquoi pas un score : des manques, des échelles et des natures incompatibles ; un bon indicateur ne compense pas une restriction.
- V1 : tests conservés, données archivées ; pas de mélange ERA5/DRIAS ni de recyclage des compteurs.
''')
write('matrice_academique.md','''# Exigence → fichier → preuve

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
''')
write('postgis_evaluation.md','''# PostgreSQL/PostGIS : cible de montée en charge

PostGIS est adapté aux intersections nationales de parcelles et d’aléas, avec index GiST et requêtes spatiales en base. Documentation producteur : https://postgis.net/documentation/ . SQLite + RTree et GEOS sont retenus pour un ZIP académique sans serveur de base à installer et un hébergement statique réellement disponible. Les millions de valeurs climatiques ne nécessitent pas une intersection géométrique à chaque mouvement de carte.

Le SQL d’extension `sql/postgis_candidate.sql` est une proposition de migration spatiale **non exécutée** : aucun PostgreSQL/PostGIS n’est disponible dans l’environnement. Il n’est pas décrit comme une base déployée. Avant mise en production : importer les clés/versions normalisées, vérifier SRID, intégrité, comptages, sommes d’aires et résultats de points de contrôle ; mesurer plans EXPLAIN ANALYZE, pagination et charge concurrente. Les superficies locales métriques nécessitent une projection adaptée (Lambert-93 en métropole, projection locale adaptée outre-mer) ou geography sur ellipsoïde. Ne jamais mesurer des mètres directement sur les degrés.

La configuration de l’hébergeur est statique (`dist`). Une API Python et PostgreSQL nécessiteraient un hébergement supplémentaire avec budget et exploitation à définir ; aucun achat ni déploiement payant n’a été engagé.
''')
(ROOT/'sql/postgis_candidate.sql').write_text('''-- Cible spatiale complémentaire, NON EXÉCUTÉE ; PostgreSQL avec extension PostGIS requise.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE ct_version(id text PRIMARY KEY,producer text NOT NULL,retrieved_at timestamptz NOT NULL);
CREATE TABLE ct_zone(id text PRIMARY KEY,version_id text NOT NULL REFERENCES ct_version,kind text NOT NULL,geom geometry(MultiPolygon,4326) NOT NULL CHECK(ST_IsValid(geom)));
CREATE TABLE ct_parcel(id text PRIMARY KEY,version_id text NOT NULL REFERENCES ct_version,geom geometry(MultiPolygon,4326) NOT NULL CHECK(ST_IsValid(geom)));
CREATE INDEX ct_zone_gist ON ct_zone USING gist(geom);
CREATE INDEX ct_parcel_gist ON ct_parcel USING gist(geom);
-- Relations exactes et superficie ellipsoïdale : aucune mesure en degrés.
SELECT p.id parcel_id,z.id zone_id,ST_Area(ST_Intersection(p.geom,z.geom)::geography) area_m2 FROM ct_parcel p JOIN ct_zone z ON ST_Intersects(p.geom,z.geom);
''',encoding='utf-8')
print('Documentation structurée écrite')
