# ChronoTerre — Île-de-France

**Question centrale : quelles traces du vivant sont documentées autour des communes franciliennes, et dans quelle mesure leur climat projeté à l’horizon 2050 ressemble-t-il aux climats de référence de la région ?**

Projet académique ESEO 2026–2027 · Architectures BD et collecte de données.
L’exploration relie des lieux et deux échelles de temps, sans prétendre déduire le climat futur des fossiles.

## Démarrer en une minute

1. Extraire **tout le ZIP** dans un dossier.
2. Pour le dashboard seul, ouvrir `dist/index.html` dans un navigateur moderne. Il fonctionne sans Internet ; les liens vers les sources nécessitent Internet.
3. Pour le dashboard **connecté à l’API et à SQLite**, installer Python 3.11+ puis exécuter depuis le dossier du projet :

```bash
python src/serve.py --open
```

Sous Windows, `Lancer_ChronoTerre.bat` lance la même commande. Sur macOS/Linux : `sh lancer_chronoterre.sh` (ou remplacer `python` par `python3`). Le serveur écoute sur `http://127.0.0.1:8000`. Ctrl+C l’arrête. `--port 8001` permet de changer de port.

**Aucune dépendance Python externe, aucune clé API et aucun compte ne sont nécessaires.** Les vraies données et la base déjà alimentée sont incluses. Le dashboard hébergé, lorsqu’il est fourni, utilise un instantané issu du même pipeline ; l’API Python se lance localement.

## Reproduire les résultats hors ligne

```bash
python -m venv .venv
# Facultatif : activer .venv selon votre système.
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/pipeline.py --offline --verify-replay
python src/demo_rejection.py
python src/analyse.py
python src/serve.py --open
```

Le pipeline reconstruit la base à partir des réponses brutes fournies, compare deux exécutions et actualise le dashboard. Compter quelques dizaines de secondes selon l’ordinateur. Les rapports se trouvent dans `reports/`.

Pour refaire la collecte réseau (plusieurs minutes, respecter les quotas fournisseurs) :

```bash
python src/collect.py              # reprend et vérifie le cache existant
python src/collect.py --refresh    # nouvelles réponses, anciens fichiers conservés
python src/pipeline.py --offline --verify-replay
```

Les URL, dix communes, périodes et deux modèles se règlent dans `config/settings.json`. Un changement de périmètre, modèle ou fenêtre exige de relancer la collecte. Le projet livré reste limité à la région 11 ; il ne contient pas d’analogues étrangers.

## Manipuler le dashboard

- **Le passé** : recherche de nom ou de lieu, département, classe taxonomique, période et bornes d’âge, rayon autour d’une commune. Carte déplaçable et zoomable, fiches bibliographiques, découverte aléatoire, export CSV de la sélection.
- **Le climat de référence** : portrait 1991–2020, choix de commune et d’indicateur, courbes mensuelles de température et de pluie.
- **Horizon 2050** : projection 2030–2049, deux modèles, différences par rapport à la référence, étendue entre modèles, couverture des années, classement des analogues franciliens.
- **Les coulisses** : sources, licences, compteurs de contrôle et rapport téléchargeable.
- **Défi ChronoTerre** : quatre questions avec correction argumentée, dont deux calculées à partir du jeu réellement collecté.

Au clavier : Tab pour atteindre les contrôles ; dans la carte, flèches pour déplacer, `+` et `-` pour zoomer, Entrée sur les points pour les sélectionner. Sur écran tactile, glisser la carte et utiliser les boutons de zoom. L’interface s’adapte aux petits écrans.

## Ce que demandent les consignes et où le trouver

| Attendu | Preuve |
|---|---|
| Question, utilisateurs, 3 cas d’usage, 3 KPI | Ce README, `docs/cadrage.md` |
| Évaluation d’au moins 2 sources | `docs/source_assessment.md` |
| Sources structurées et >100 observations | `data/raw/manifest.json`, `reports/run_report.json` |
| Raw inchangé et horodaté | JSON dans `data/raw/`, URL et SHA-256 du manifeste |
| Profilage avant nettoyage | `reports/profile_before.json` |
| Grain, dictionnaire, contrat versionné | `config/data_contract.yaml`, `docs/data_dictionary.md` |
| Architecture et modèle relationnel | `docs/architecture.png`, `docs/schema.png`, `sql/schema.sql` |
| Au moins 5 contrôles avec action et compteur | 11 règles, `src/validate.py`, rapport d’exécution |
| Curated, normalisation et rejets | `data/curated/`, `data/rejected/rejected_rows.csv` |
| Idempotence démontrée | `reports/idempotence.json` |
| Ligne invalide et rejet expliqué | `src/demo_rejection.py`, `reports/demo_rejection.json` |
| Exécution et soutenance 3–5 minutes | `docs/demo_5_minutes.md` |
| Bonus pertinents | 12 tables SQLite, tests, 15 analyses SQL, API, CI, dashboard |

## Structure

```text
config/      settings.json ; data_contract.yaml (JSON valide en YAML 1.2)
data/raw/    réponses originales, manifestes de lots et cache courant
data/curated/chronoterre.sqlite ; fossils.csv ; climate_daily.csv
             climate_annual.csv ; climate_summary.csv ; dashboard.json
data/rejected/rejected_rows.csv
src/         collect.py ; validate.py ; transform.py ; pipeline.py
             serve.py ; analyse.py ; demo_rejection.py
sql/         schema.sql ; analyses.sql
tests/       test_quality.py
reports/     run_report.json ; profile_before.json ; idempotence.json
             sql_results.json ; demo_rejection.json ; validation.json
docs/        dossier, schémas, sources, dictionnaire, API, soutenance
dist/        dashboard autonome HTML/CSS/JS et données générées
```

## Sources et droits

PBDB (CC BY 4.0), Open-Meteo et producteurs CMIP6/Copernicus (données CC BY 4.0 avec attribution), géographie Etalab/IGN et API Découpage administratif (Licence Ouverte). Les URL exactes, dates et empreintes de chaque réponse figurent dans le manifeste. Les publications paléontologiques sont citées occurrence par occurrence ; les articles complets ne sont pas recopiés. L’usage du service gratuit Open-Meteo est non commercial, avec quotas ; les filtres du dashboard n’interrogent pas ce service.

## Qualité et choix méthodologiques

- Fossiles : identifiants, référence et âge contrôlés ; inclusion spatiale dans les huit contours franciliens ; coordonnées politiques et contradictions de provenance exclues. Le fichier de configuration documente six exclusions connues par identifiant de collection.
- Climat : dates, unités, tableaux, températures, précipitations et unicité contrôlés. Les valeurs manquantes ne sont jamais remplacées par zéro.
- La première collecte ERA5-Land seule ne fournissait pas la pluie. Le choix final **ERA5-Seamless** associe la température ERA5-Land et la pluie ERA5. Les fichiers du pilote et son rapport sont gardés comme trace de cette décision, mais ne sont pas utilisés dans la base finale.
- Quelques jours EC-Earth présentent des températures min/moy/max incompatibles : ils sont rejetés, sans correction arbitraire. Les indicateurs reposent sur des **années complètes**. Une synthèse est affichée si au moins 90 % des années attendues sont complètes ; le nombre et les années exclues sont exposés. Les profils mensuels utilisent ces mêmes années. Les fenêtres effectives peuvent donc différer entre modèles.
- La base est reconstruite dans un fichier temporaire, contrôlée puis remplacée atomiquement. Les PK/UNIQUE empêchent les doublons. Le rejeu compare toutes les valeurs triées des 12 tables applicatives, pas seulement les nombres de lignes.

## Limites à expliquer

Les fossiles publiés ne constituent pas un recensement exhaustif. Une collection n’est pas forcément un lieu unique ; un taxon n’est pas forcément une espèce. Les points et les distances sont indicatifs. Le filtrage sur des contours à 100 m ne corrige pas l’incertitude des localisations historiques.

Le climat est régional : ERA5-Land est à 0,1° pour la température, ERA5 à 0,25° pour la pluie ; le futur est corrigé et ramené par le fournisseur vers une maille d’environ 10 km. Les coordonnées uniques renvoyées par ERA5-Seamless ne décrivent pas séparément toutes les mailles des variables. Ne pas interpréter ces données à l’échelle d’une rue.

Les deux projections HighResMIP utilisent un forçage proche RCP8.5. Leur étendue n’est pas un intervalle de confiance. Les analogues sont limités à dix communes, avec un score pédagogique température/pluie et un seuil explicite ; « aucun analogue proche » est un résultat valide. Aucune causalité entre fossiles et changement climatique n’est testée.

## Socle TP et extensions

Pour les deux séances de 3 h, le socle à maîtriser est **collecte PBDB → raw → contrôles → curated/SQLite → rapport → rejeu**. Le climat, l’API, la carte et le quiz sont des extensions déjà fournies. La soutenance commence par le pipeline et ses preuves, puis montre le dashboard. Le dossier évite de présenter l’ensemble de cette application comme un travail réalisé en six heures sans préparation.

Développement visuel facultatif : Node 20.19+ ou 22.12+, `npm ci`, puis `npm run dev`. Cela n’est pas requis pour exécuter le projet ni pour le remettre. Les fichiers `dist/` sont les sources web autonomes ; ne pas lancer un build Vite qui les effacerait.
