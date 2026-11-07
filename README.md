# ChronoTerre — France

Quels territoires français correspondent à mon projet d’installation, compte tenu des risques documentés, des projections climatiques et des règles d’urbanisme accessibles ?

Deux parcours partagent la carte : **Habiter demain** (climat, risques, urbanisme, comparaison) et **Explorer le passé** (collections, occurrences, références, illustrations). Les fossiles n’entrent jamais dans un classement environnemental.

**Usager principal :** une personne préparant un déménagement. Elle compare trois indicateurs à horizon et source constants : jours très chauds, nuits chaudes et jours de gel. La comparaison aide à préparer des vérifications locales.

**Pour la correction ESEO :** [point d’entrée du rendu](docs/rendu_final.md), [barème et preuves](docs/matrice_academique.md), [ADR](docs/ADR_001.md) et [oral de 6 minutes](docs/soutenance_france.md).

## Ouvrir sous Windows

1. [Télécharger le ZIP complet](https://github.com/jeremyESEO/chronoterre-france/archive/refs/heads/main.zip) et choisir **Extraire tout**, ou cloner le dépôt. Python 3.11 ou 3.12 est recommandé.
2. Dans l’Explorateur, ouvrir le **dossier extrait qui contient ensemble** `requirements-france.txt`, `README.md` et `national/`. Si l’extraction a créé deux dossiers imbriqués, ouvrir le dossier intérieur.
3. Taper `powershell` dans la **barre d’adresse de l’Explorateur**, puis Entrée. Dans ce terminal, `Test-Path .\requirements-france.txt` doit afficher `True`. Exécuter ensuite ces trois commandes, une par une :

```powershell
py -3 -m pip install -r .\requirements-france.txt
py -3 -m national.restore
py -3 -m national.serve --open
```

Ouvrir [http://127.0.0.1:8000](http://127.0.0.1:8000) si le navigateur ne s’ouvre pas automatiquement. Garder le terminal ouvert ; **Ctrl+C** arrête le serveur. Les données livrées ne nécessitent ni compte ni clé fournisseur. Pour une utilisation suivante, relancer la dernière commande ou double-cliquer sur **Lancer_ChronoTerre_France.bat** depuis le dossier extrait.

Si pip indique **Could not open requirements file**, vérifier le dossier courant avec `Get-Location`. Pour retrouver le bon dossier dans Téléchargements, chercher le fichier extrait :

```powershell
Get-ChildItem "$env:USERPROFILE\Downloads" -Filter requirements-france.txt -File -Recurse
```

Ouvrir le dossier affiché, reprendre à l’étape 3. Si aucun résultat n’apparaît, vérifier que le ZIP complet a bien été extrait.

### Linux et macOS

Depuis la racine du clone ou du ZIP extrait :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-france.txt
python -m national.restore
python -m national.serve --open
```

L’installation initiale des dépendances requiert une connexion. Shapely et PyProj servent notamment au rejeu et aux intersections.

## Ce qui est livré et ses limites

La base contient plusieurs millions de valeurs réellement publiées par Météo-France et les occurrences PBDB retenues après contrôle ; les compteurs exacts sont dans `reports/france_run.json`. Recherche communale nationale et codes postaux, Corse incluse. L’outre-mer conserve son domaine spécifique. Adresses, fond IGN et urbanisme général nécessitent Internet.

Le site hébergé est un **instantané statique produit par SQLite**, avec appels directs aux services publics IGN pour les adresses et parcelles. L’API Python/SQLite fonctionne **localement** ; elle n’est pas présentée comme un serveur Python en ligne. Les fichiers sont découpés par département. Les mises à jour sont manuelles.

Le climat couvre les niveaux TRACC associés à 2030, 2050 et 2100. Date de référence du projet : 25/09/2026 ; +50 ans = 2076, désactivé faute de période correspondante. Pas d’interpolation ni d’extrapolation Open-Meteo. La référence historique n’est pas la météo actuelle.

Les enveloppes d’inondation couvrent Toulouse (source 2013), les argiles Bordeaux Métropole. L’inventaire communal d’aléas n’est pas une exposition à l’adresse. Les documents d’urbanisme sont consultés au clic ; trois parcelles et neuf lieux publics disposent d’un échantillon brut livré. Pas de verdict de constructibilité. Cinq images attribuées illustrent quelques taxons ; aucun spécimen exact local n’est revendiqué.

Le lancement de Chromium a échoué dans l’environnement de reprise. Le rendu visuel, les gestes en navigateur, le mobile et les captures restent à vérifier sur un autre poste. Voir `docs/recette.md` pour les essais automatisés exécutés et le reste à vérifier.

## Rejouer sans réseau

```powershell
py -3 -m national.migrate_v1
py -3 -m national.demo
py -3 -m national.pipeline --verify-replay
py -3 -m national.analyses
py -3 -m national.checks
```

`demo` est le socle TP rapide : une vraie page PBDB (10 000 lignes brutes), contrôles, SQLite, rejet pédagogique isolé et deux exécutions comparées. Il ne modifie pas la base France. L’extension nationale dépasse le cadre des deux séances de trois heures.

Le rejeu national vérifie les SHA-256 des 58 fichiers sources, reconstruit une base temporaire, contrôle son intégrité puis remplace la base France. **Ne pas lancer deux reconstructions simultanément.** La seconde reconstruction compare les clés et toutes les valeurs typées, pas seulement les effectifs. Une erreur détectée avant remplacement conserve la dernière base stable. Le remplacement de SQLite ne rend pas transactionnelle la publication de tous les fichiers Web.

## Nouvelle collecte (facultative, avec réseau)

```powershell
py -3 -m national.collect --refresh
py -3 -m national.collect_climate --refresh
py -3 -m national.collect_urban
py -3 -m national.collect_hazards
```

Le collecteur climatique réutilise par défaut son cache vérifié ; `--refresh` crée une nouvelle acquisition horodatée et conserve les manifestes antérieurs. Les endpoints et paramètres exacts, non secrets, figurent dans les manifestes. Les anciens fichiers bruts ne sont pas écrasés. Les services peuvent changer de schéma, d’URL ou de conditions : un échec n’est jamais remplacé par une valeur inventée.

## Organisation

- `national/` : collecte, validation, construction, exports, API et analyses France.
- `src/`, `app/` et `docs/README_V1.md` : composants conservés de la V1.
- `v1/ChronoTerre_IDF_original.zip` : version originale récupérable.
- `config/` : contrat, exclusions motivées, sources d’aléas, lieux d’essai et médias.
- `data/raw/` : octets originaux horodatés ; le gros JSONL climatique est compressé sans perte, son SHA porte sur les octets décompressés.
- `data/curated/` : SQLite compressé restaurable, CSV réel de démonstration, géométries.
- `data/rejected/` : rejets avec raisons, séparés du test volontairement invalide.
- `dist/` : application et instantanés générés depuis la base.
- `reports/` : profilage, intégrité, rejeu, tests, analyses et provenance.
- `docs/` : dossier, méthode, dictionnaire, sources, recette, soutenance.

## Ressources et coûts

Prévoir 2 Go d’espace disponible, Python 3.11+, et 4 Go de RAM conseillés pour reconstruire. La reconstruction complète peut prendre plusieurs minutes selon le disque et le processeur ; voir le temps réellement mesuré dans le rapport. Le JSONL source climatique fait environ 404 Mo avant compression. Les tailles exactes du ZIP et de la base sont livrées dans le bilan de livraison.

Aucun service payant souscrit. Fond, géocodage et consultations publiques restent soumis à disponibilité et politique d’usage des producteurs. Hors connexion, les fiches, comparaisons et images embarquées restent consultables via le serveur local ; aucun fond de carte mondial ou photographie IGN n’est préchargé. Les adresses saisies sont envoyées à l’IGN ; pas de journal d’adresses dans l’application, favoris communaux stockés sur l’appareil.

## Sources et licences

Voir `docs/sources_france.md`, `docs/media_registry.json` et les manifestes. Les licences des producteurs et des images prévalent sur celle du code. Ne pas attribuer l’ensemble des données à l’auteur du projet. Les images ont leurs crédits et licences propres, dont des obligations de partage à l’identique.

Les deux plus grandes archives sont découpées en blocs pour la limite du dépôt. `national.restore` et `national.pipeline` les recomposent automatiquement et vérifient leur SHA-256. Le découpage ne modifie pas les octets des archives originales.

## Nouveau : trouver mon lieu de vie

Depuis la carte, utilisez **Trouver mon lieu de vie**, réglez les maxima climatiques et cliquez sur **Explorer les résultats**. Le tri fonctionne dans les deux sens, à horizon constant, sur 34 746 communes de métropole et Corse. Les règles, exclusions, données récentes et limites sont dans [docs/parcours_installation.md](docs/parcours_installation.md).

Les index sont inclus ; aucune collecte nationale ne s'exécute dans le navigateur. La fiche **Climat à travers le temps** distingue projections et réanalyse récente : 8 lieux validés, 29 224 journées de 2016 à 2025. Données manquantes visibles. Le classement ne certifie ni un logement, ni un risque à l'adresse, ni la qualité de vie globale.

## Suivre l'avancement du projet

Le statut réel des fonctionnalités et les preuves sont dans [AVANCEMENT.md](AVANCEMENT.md). Les développements prévus vers une plateforme de production sont dans [ROADMAP.md](ROADMAP.md). Le [dépôt GitHub est public](https://github.com/jeremyESEO/chronoterre-france) et l’onglet [Actions](https://github.com/jeremyESEO/chronoterre-france/actions) permet de vérifier les derniers résultats.


## Architecture, qualité et reprise

[Architecture V1](docs/architecture.png) → [architecture V2](docs/architecture_v2.svg) → [trace d’une observation jusqu’à la fiche](docs/lineage.md). La décision SQLite et batch est argumentée dans [ADR 001](docs/ADR_001.md). Les règles sont dans le [contrat France 2.0.1](docs/contrat_france.md) et `national/validate.py` ; les enregistrements non acceptés sont conservés avec leurs motifs dans `data/rejected/`.

Le [rapport d’incident](reports/rendu_final_incident.json) montre l’arrêt P01 sur raw altéré, l’empreinte de la base stable inchangée et la reprise après restitution du fichier original. À chaque exécution, le pipeline consigne l’identifiant, le contrat, les étapes et l’ancienneté des acquisitions ; voir la [gouvernance](docs/gouvernance.md). Les conditions originales de Toulouse sont [documentées avec l’attribution et la date](docs/licence_dreal.md).

## Déclaration d’usage de l’IA

- **Outil utilisé :** ChatGPT/Codex.
- **Travaux assistés :** développement et revue du pipeline et de l’interface, diagnostic de la CI, documentation, synthèse et préparation de l’oral.
- **Vérifications réalisées dans le projet :** collecte PBDB courte, restauration et rejeu, tests Python et DOM, incident P01 et résultats SQL. Les preuves et leurs limites figurent dans [le rapport de vérification](reports/rendu_final_verification.json).
- **Apport personnel documenté :** Jérémy a défini le besoin et les critères du parcours d’installation, créé le dépôt public et signalé l’échec CI observé sur GitHub. Les développements et vérifications assistés sont distingués de ces contributions. La répétition et la défense sont personnelles.
