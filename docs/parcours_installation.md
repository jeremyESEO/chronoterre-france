# Trouver mon lieu de vie — extension du 11 octobre 2026

## Fonctionnement livré
Le bouton « Trouver mon lieu de vie » ouvre les préférences ; le parcours est aussi affiché au premier chargement sans sélection partagée. Choisir un horizon, éventuellement une région, une classe de population ou un rayon à vol d'oiseau autour d'une commune de référence. Les préférences restent dans le navigateur. Aucune adresse personnelle n'est mémorisée.

Le calcul porte sur 34 746 communes métropolitaines, Corse comprise. Il compare cinq indicateurs à source, horizon et référence constants : jours très chauds (S1), nuits chaudes (S2), gel (G2), jours avec précipitations en été (G4), séquence sèche estivale la plus longue (AG1). Pour les définitions et conventions de seuil, voir les fiches producteur et les métadonnées existantes. Les trois derniers indicateurs ne représentent ni luminosité, ni qualité de vie générale, ni disponibilité de l'eau potable.

Les seuils proposés sont des préférences de démonstration modifiables, pas des seuils scientifiques de danger. Valeurs par défaut : 10 j/an très chauds ; 20 nuits/an chaudes ; 40 j/an de gel ; 25 j/été de pluie ; 30 jours pour la séquence sèche maximale. Importance : respectivement 2, 3, 1, 1, 1. « Ignorer » met l'importance à zéro. Au moins un critère doit rester actif.

## Méthode, exclusions et classement
Pour chaque indicateur actif : valeur centrale <= maximum personnel signifie critère satisfait.
- Tous satisfaits : dans tous tes seuils.
- Au moins la moitié satisfaits : des compromis.
- Moins de la moitié : plus éloigné de tes critères.
- Une valeur centrale manquante : données insuffisantes ; toujours en fin de liste, même en tri inverse.

La catégorie détermine le premier ordre. À catégorie égale, le dépassement normalisé pondéré est :

`E = somme[importance_i × max(0, valeur_i − seuil_i) / max(1, seuil_i)]`

Le dénominateur plancher de 1 évite une division par zéro et correspond à une unité de l'indicateur. Ce nombre sert uniquement à départager les dépassements ; ce n'est ni une note scientifique, ni une probabilité, ni un score d'habitabilité. Les valeurs, les unités, les préférences et E sont exportées en JSON. Les communes respectant tous les seuils sont ex aequo (E=0) ; l'ordre alphabétique puis le code INSEE assurent un ordre reproductible sans prétendre que la première est la meilleure de France.

Le filtre strict garde uniquement les communes respectant tous les maxima. Région et population sont des filtres sur les champs du référentiel communal fourni. Population ne vaut pas typologie urbaine officielle. Le rayon est géodésique approché par Haversine avec rayon moyen terrestre de 6 371,0088 km, pas un temps de trajet. Les valeurs outre-mer restent accessibles dans les fiches classiques mais sont exclues du classement commun : références, seuils et domaines ne sont pas mélangés.

## Incertitudes et sensibilité
La catégorie est recalculée avec les bornes basses puis les bornes hautes de chaque indicateur fournies par Climadiag. Ce sont des bornes marginales : leur combinaison n'est pas un scénario climatique conjoint. Une catégorie inchangée à ces bornes ne garantit pas un classement stable, une faible incertitude scientifique ou un climat futur certain. Une borne manquante interdit ce test. Aucun scénario RCP/SSP n'est mélangé à la TRACC ; aucune interpolation 2076.

`reports/home_sensitivity.json` mesure l'effet de cinq jeux de pondérations et de seuils ±20 % sur les données 2050. Les poids ne changent pas les catégories, par construction. Les seuils, eux, changent réellement les résultats. La concordance du début de liste est à interpréter avec les ex aequo alphabétiques.

## Preuves et temporalité
Les index `dist/data/home-{ref,2030,2050,2100}.json` sont produits depuis les fichiers climatiques exportés de SQLite par `national.home_export`. Les réponses brutes d'origine, l'empreinte de chaque entrée et les métadonnées du producteur sont référencées dans `home-meta.json`. Le constructeur est intégré à l'export principal. La référence historique est 1976–2005 pour le domaine sélectionné ; ce n'est pas le climat actuel. Les fenêtres annuelles par modèle associées aux niveaux TRACC ne sont pas fournies par l'export utilisé.

Sources :
- https://climadiag-commune.meteofrance.com/ — Météo-France ; Licence Ouverte Etalab ; données déjà collectées et documentées dans le registre national.
- https://www.drias-climat.fr/accompagnement/sections/335 — lecture des projections, variabilité et moyennes pluriannuelles.

## Réanalyse récente : collecte réelle, limitée
Le connecteur `national.collect_recent` a demandé 2016–2025 pour dix communes contrastées via l'API historique Open-Meteo, modèle explicitement fixé à ERA5-Land. Huit séries de température complètes sont retenues : Paris, La Rochelle, Arles, Tours, Chamonix, Guéret, Saint-Denis de La Réunion et Toulouse. Soit **29 224 journées**. Ajaccio a des températures manquantes ; Rennes a rencontré HTTP 429 à la collecte. Le rejeu hors réseau signale l'absence de réponse en cache. Ces cas ne sont pas interpolés. Les neuf réponses brutes reçues, y compris celle d'Ajaccio, sont conservées et référencées.

Il s'agit d'une réanalyse combinant observations et modèle, pas de relevés de stations. Résolution native 0,1° (~11 km), coordonnées de maille retournées conservées, correction d'altitude désactivée (`elevation=nan`) et modèle constant. Les minima quotidiens >=20 °C ne sont pas présentés comme un calcul horaire de nuits tropicales. Les précipitations sont toutes nulles dans les réponses reçues : valeur manquante, aucun zéro ajouté, aucun cumul calculé. Elles restent nulles dans le stockage typé.

Source et conditions vérifiées : https://open-meteo.com/en/docs/historical-weather-api et https://open-meteo.com/en/terms . Données Open-Meteo : CC BY 4.0 ; producteurs ECMWF/Copernicus. L'accès API gratuit est destiné aux usages non commerciaux ; une exploitation commerciale exige de revoir les conditions ou l'hébergement. Aucun abonnement engagé. Le site ne déclenche aucune nouvelle collecte par visite ou déplacement de carte.

Cette série s'affiche séparément dans « Climat à travers le temps ». Aucun delta ERA5-Land / DRIAS, aucune extrapolation des dix années, aucune contribution au classement national. Pas encore de normales observées nationales ou de confort quotidien personnalisé.

## Base complémentaire et rejeu
`data/curated/recent.sqlite` contient trois tables :
- raw_file : une réponse identifiée par SHA-256, chemin, URL exacte, date, taille ;
- weather_place : un point demandé par code INSEE, coordonnées demandées/retournées, fuseau, clé étrangère raw_sha ;
- daily : une journée par (code INSEE, date), Tmax, Tmin, précipitations nullable, contraintes Tmax>=Tmin et précipitations>=0, FK vers weather_place.

Cette base complémentaire est jointe conceptuellement à la base nationale par code INSEE ; elle n'a pas de FK physique inter-fichier. Le site utilise son export JSON statique. Les paramètres publics sont conservés dans l'URL de collecte ; aucune clé requise. Délais bornés à 50 s, deux tentatives maximales. Commande manuelle, aucune programmation.

Windows ou Linux, depuis le projet :
```
python -m national.home_export
python -m national.collect_recent --replay-only
python -m national.serve --open
```
Pour renouveler les séries sans écraser les raw existants, conserver le dossier actuel et utiliser un nouveau répertoire de campagne en adaptant OUT ; la commande sans `--replay-only` réutilise les réponses déjà présentes. Le connecteur ne constitue pas un planificateur de mises à jour.

Contrôles : unités, 3 653 dates complètes et uniques par série, températures numériques et bornées, Tmin<=Tmax, précipitations nullable/non négatives, nombre exact de jours par année. Rejets avec raisons. Rejeu vérifié par empreinte des trois tables triées, pas seulement par effectifs : `reports/home_replay.json`.

## Vérifications et limites de réception
- `tests/home.cjs` : logique de seuils, trous de données, tri inverse, fidélité aux sources, Corse/outre-mer, parcours DOM avec vrais fichiers, changement d'horizon, export et provenance, graphique/série récente, absence de série, conservation du mode fossiles.
- `tests/front_dom.cjs` : neuf groupes de régression du site existant.
- `tests/home_sensitivity.cjs` : calcul et tri nationaux mesurés dans Node, hors réseau, WebGL et rendu.
- Pas de navigateur interactif disponible dans cet environnement : mobile, clavier réel et interactions WebGL non certifiés. Une capture de publication ne remplace pas cette recette.

Limites : données de risques à l'adresse toujours locales ; aucune sécurité déduite du classement. Aucun prix, emploi, temps de trajet, ensoleillement, vent ou îlot de chaleur nouveau collecté. La checklist logement est préparatoire, sans modèle thermique, et ne modifie pas les résultats. La comparaison de robustesse entre scénarios d'émissions reste non réalisée. Le nouveau parcours est une aide au tri climatique, pas une décision immobilière.

## Retour à la version stable
La version 4 publiée, commit `91416a0eed83fbe60fdcaf597a2228f7670474c1`, précède cette extension. Republier cette version via Sites conserve l'identité et les droits d'accès. Aucun fichier de la V1 n'est modifié ; aucune table de la base nationale n'est supprimée.
