# PostgreSQL/PostGIS : cible de montée en charge

PostGIS est adapté aux intersections nationales de parcelles et d’aléas, avec index GiST et requêtes spatiales en base. Documentation producteur : https://postgis.net/documentation/ . SQLite + RTree et GEOS sont retenus pour un ZIP académique sans serveur de base à installer et un hébergement statique réellement disponible. Les millions de valeurs climatiques ne nécessitent pas une intersection géométrique à chaque mouvement de carte.

Le SQL d’extension `sql/postgis_candidate.sql` est une proposition de migration spatiale **non exécutée** : aucun PostgreSQL/PostGIS n’est disponible dans l’environnement. Il n’est pas décrit comme une base déployée. Avant mise en production : importer les clés/versions normalisées, vérifier SRID, intégrité, comptages, sommes d’aires et résultats de points de contrôle ; mesurer plans EXPLAIN ANALYZE, pagination et charge concurrente. Les superficies locales métriques nécessitent une projection adaptée (Lambert-93 en métropole, projection locale adaptée outre-mer) ou geography sur ellipsoïde. Ne jamais mesurer des mètres directement sur les degrés.

La configuration de l’hébergeur est statique (`dist`). Une API Python et PostgreSQL nécessiteraient un hébergement supplémentaire avec budget et exploitation à définir ; aucun achat ni déploiement payant n’a été engagé.
