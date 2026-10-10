# Méthode et corrections de l’audit

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
