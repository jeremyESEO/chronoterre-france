# Du fichier source à la fiche

[Architecture V1 (PNG)](architecture.png) : premier pipeline Île-de-France. [Architecture V2 (SVG)](architecture_v2.svg) : collecte et traitement national livrés. Les deux versions sont conservées distinctement.

| Étape | Exemple vérifiable : occurrence PBDB 76598 |
|---|---|
| Origine | `pbdb_occs_0` dans `data/raw/national_manifest.json` : URL de la page PBDB, date et SHA-256. La réponse brute comporte `occurrence_no=76598` et `collection_no=4917`. |
| Contrôle | `national/validate.py` vérifie identifiant, coordonnées, provenance, âge et référence ; l’occurrence est retenue. `national.demo` la retrouve dans son lot de 10 000 observations. |
| Base | `fossil_occurrence.occurrence_id=76598`, `site_id=4917`, `raw_id=pbdb_occs_0`. Les tables des taxons, collections, intervalles et références complètent l’occurrence. La clé `raw_id` relie la ligne aux octets d’origine. |
| Produit | `GET /api/v2/sites/4917` sur le serveur local : collection « Normandy HLF32 », occurrence `76598`, genre `Gryphaea`. Les exports départementaux desservent aussi la carte. |
| Interprétation | Un enregistrement documente une occurrence ; il ne mesure ni l’abondance ancienne ni un aléa actuel. |

Pour le climat, `climate_value.raw_id='climadiag'` relie la valeur à l’export JSONL archivé. Par exemple, `17300 × S2 × 2050 × annuel` donne 23,35 nuits chaudes par an en valeur centrale pour La Rochelle. La source, l’unité, l’horizon et les limites sont exposés avec la fiche. Deux communes se comparent au même horizon et avec la même définition.
