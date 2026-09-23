# API locale ChronoTerre v1

Démarrage : `python src/serve.py`. Base URL : `http://127.0.0.1:8000/api/v1`. JSON UTF-8, lecture seule, aucun secret. La version web hébergée propose la même exploration sur un instantané ; elle n’héberge pas le serveur Python.

| Route GET | Paramètres | Réponse |
|---|---|---|
| `/health` | aucun | statut et version |
| `/bootstrap` | aucun | jeu compact du dashboard |
| `/cities` | aucun | dix communes |
| `/fossils` | `department`, `class`, `q`, `min_ma`, `max_ma`, `city`, `radius`, `limit`, `offset` | occurrences filtrées avec total et pagination |
| `/climate` | `city=78640` | référence et projections de la commune |
| `/analogues` | `city=78640&model=MRI_AGCM3_2_S` | classement régional et distance normalisée |
| `/quality` | aucun | rapport d’exécution |

Exemples à ouvrir directement dans le navigateur :

```text
http://127.0.0.1:8000/api/v1/fossils?department=78&min_ma=33.9&max_ma=56&limit=5
http://127.0.0.1:8000/api/v1/fossils?city=78640&radius=30&limit=20
http://127.0.0.1:8000/api/v1/climate?city=78640
http://127.0.0.1:8000/api/v1/analogues?city=78640&model=EC_Earth3P_HR
```

`limit` est compris entre 1 et 500, `offset` est positif ou nul, le rayon entre 1 et 200 km et les âges entre 0 et 4600 Ma, borne récente ≤ borne ancienne. Les intervalles d’âge sont sélectionnés par recouvrement. Les distances utilisent la formule de Haversine et restent indicatives compte tenu des coordonnées de source.

Codes HTTP : 200 résultat, 400 paramètres invalides, 404 route inconnue, 503 base indisponible. Les requêtes SQL utilisent des paramètres liés ; aucun endpoint n’exécute un SQL fourni par l’utilisateur. SQLite est ouverte en mode `ro` et le serveur écoute seulement sur l’interface locale.

## Exemple Python

```python
import json
from urllib.request import urlopen
url = 'http://127.0.0.1:8000/api/v1/fossils?department=78&limit=3'
data = json.load(urlopen(url))
print(data['total'], data['items'][0]['identified_name'])
```

## Évolutions raisonnables

Le modèle distingue producteurs, fichiers bruts, lieux et séries : une autre région peut être ajoutée avec un contrat et des sources explicitement adaptés. Une vraie mise en production demanderait un serveur HTTP adapté, une planification de collecte, de l’observabilité, une stratégie de sauvegarde et de versionnement des données. L’API de démonstration n’inclut ni comptes ni écritures, car ils n’aident pas à répondre à la question académique.
