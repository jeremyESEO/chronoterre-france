# API locale v2

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
