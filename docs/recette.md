# Recette de livraison et statuts

Reprise du 10 octobre 2026. Les rapports JSON sont les preuves d’exécution. Une vérification automatique ne remplace pas une vérification visuelle.

| Critère demandé | État effectivement vérifié | Reste à vérifier |
|---|---|---|
| Recherche hors IDF | Opérationnelle, tests API et DOM avec La Rochelle, Ajaccio et La Réunion | interaction et rendu navigateur |
| France → rue → parcelle | Implémenté ; fonds IGN réels, trois parcelles réelles collectées | zoom/clic et tuiles dans navigateur |
| Horizons/scénarios | Valeurs différentes 2030/2100 testées ; référence distincte ; seul TRACC disponible ; 2076 refusé | rendu carte et mobile |
| Dans/hors enveloppe | Intersections GEOS testées avec trois enveloppes Toulouse et point extérieur | superposition visuelle ; couverture locale seulement |
| Urbanisme et dates | 26 documents, trois parcelles et quatre relations parcelle-zone ; échantillon contrôlé | consultation générale live, prescriptions linéaires/ponctuelles et statut juridique PPR |
| Comparaison | DOM : deux lieux, seuil et priorité ; absence non valorisée | ergonomie jusqu’à quatre lieux dans navigateur |
| Médias | Cinq fichiers présents, associations taxon/genre et auteurs vérifiés ; fiche DOM avec image | chargement et taille visuelle dans navigateur ; aucune galerie complète |
| Fossiles et filtres | Base contrôlée, pagination API, fiche DOM, compteurs calculés | gestes de filtre et regroupement WebGL |
| Source en panne | HTTP 503 sans données fictives ; géocodeur indisponible en test DOM | panne réelle de tuiles et quota externe non provoqués |
| Export | Code conserve valeurs, colonnes, unité, période, source et limites | clic de téléchargement et impression navigateur non testés |
| Idempotence/intégrité | Deux reconstructions, empreintes identiques, FK/intégrité, règles et unités testées | aucun test de charge nationale PostGIS |
| Mobile/clavier/performance | CSS responsive, labels et contrôles prévus ; micro-mesures HTTP locales | rendu mobile, contraste mesuré, clavier, lecteur d’écran et chargement complet non testés |

## Essais exécutés

- `reports/france_tests.json` : 14 tests France, zéro échec et zéro erreur.
- Neuf tests V1 (`python -m unittest discover -s tests -p test_quality.py -v`) : réussis.
- `reports/front_dom.json` : sept parcours de logique DOM, réussis ; jsdom, pas navigateur.
- `reports/france_idempotence.json` : mêmes tables applicatives, mêmes clés et valeurs, même provenance.
- `reports/demo_tp.json` : socle rapide, 10 000 enregistrements réels en entrée, fixture invalide isolée, double rejeu.
- `reports/france_analyses.json` : 18 requêtes exécutées.
- `reports/performance_http.json` : cinq lectures HTTP de fiche 2050 pour neuf codes communaux, boucle locale, médiane et maximum. Ce ne sont pas des temps de rendu du site.
- `reports/provider_checks.json` : accès publics retestés avec status, type, URL finale, octets et durée ; une page de documentation HTTP 200 ne valide pas tous les endpoints de son API.
- `node --check dist/app.js` : syntaxe JavaScript vérifiée.

## Parcours manuel restant, sans sélectionner seulement les cas favorables

Paris (dense), La Rochelle (atlantique), Arles (méditerranéen), Tours/Toulouse (vallée), Chamonix (montagne), Guéret (rural), Ajaccio (Corse), Saint-Denis 97411 (outre-mer). Tester une rue sans parcelle et le cache d’Arles avec parcelle. Tester un taxon illustré (Gryphaea arcuata) et un autre sans image. Comparer un domaine métropolitain à La Réunion : l’avertissement doit rester visible. Couper le réseau pour distinguer instantané et fond externe.

Tester Tab, Entrée, Échap et les résultats de recherche ; viewport 390×844 ; zoom 200 % ; noms longs ; attribution ; fermeture du panneau et retour à la sélection précédente. Mesurer chargement à cache froid et chaud avec la connexion annoncée. Aucune capture de la V1 n’est présentée comme capture de la V2.

## Fonctions non réalisées

Carte nationale d’exposition infra-communale multi-aléas, hydrologie Explore2, recul côtier, îlot de chaleur national, vulnérabilité du bâti, analyse automatique des règlements, parcelles nationales préchargées, galerie Panoramax, localisations de visites vérifiées, quiz, analogues climatiques validés, backend PostGIS en ligne, mises à jour planifiées. Ces éléments ne sont pas annoncés comme terminés dans l’interface.

## Rejouer les tests DOM, facultatif

Installer Node.js et `npm install --no-save jsdom@26.1.0`, puis `node tests/front_dom.cjs`. Le test utilise les vrais instantanés embarqués et simule explicitement l’indisponibilité WebGL et du fournisseur d’adresses.

Un workflow CI est fourni pour un éventuel dépôt GitHub ; il n’a pas été exécuté par une plateforme CI pendant cette livraison.
