# Soutenance ChronoTerre — répétition de 6 minutes

Objectif : suivre une donnée depuis le producteur jusqu’à une fiche, puis expliquer comment ChronoTerre aide à comparer deux lieux. Le créneau demandé est de 5 à 7 minutes. Le texte proposé sert de repère ; reformule-le avec tes mots et garde les preuves à l’écran.

## Préparation, avant de lancer le chronomètre

1. Depuis le clone, installer les dépendances et restaurer la base : `python -m pip install -r requirements-france.txt` puis `python -m national.restore`. Sur Windows, `py -3` peut remplacer `python`.
2. Dans un premier terminal, lancer `python -m national.serve --open`. Garder un second terminal au dossier du projet pour `python -m national.demo`.
3. Préouvrir l’[application locale](http://127.0.0.1:8000), la [fiche API 4917](http://127.0.0.1:8000/api/v2/sites/4917), le [rapport d’incident](../reports/rendu_final_incident.json) et l’[ADR](ADR_001.md). Préparer la comparaison La Rochelle/Ajaccio à 2050 ; le tableau du PDF sert de secours si le fond de carte n’est pas disponible.
4. Dans `data/raw/national_manifest.json`, chercher `pbdb_occs_0`. Dans la réponse associée, chercher `"occurrence_no":76598` ou `76598`. Ne pas lancer la reconstruction nationale pendant l’oral : les preuves déjà exécutées sont disponibles.

## Conducteur chronométré

| Temps | Geste et phrase repère |
|---|---|
| **0:00–0:40** | Ouvrir la page 1 : « Une personne qui hésite entre deux communes veut comprendre les différences de climat et les vérifications qui restent nécessaires. » |
| **0:40–1:30** | Montrer `pbdb_occs_0` : URL, date d’acquisition et SHA-256 ; distinguer raw et curated. |
| **1:30–2:40** | Lancer `python -m national.demo` ; montrer 10 000 entrées réelles, 7 971 retenues, 2 029 rejetées et le cas synthétique isolé. |
| **2:40–3:30** | Ouvrir le JSON d’incident : `P01`, `FAIL`, empreinte stable et reprise. Ne modifier aucun fichier en direct. |
| **3:30–4:30** | Ouvrir `/api/v2/sites/4917`, retrouver `76598` et montrer la référence. |
| **4:30–5:20** | Comparer La Rochelle et Ajaccio en 2050 dans l’application, ou afficher le tableau page 4. |
| **5:20–6:00** | Afficher l’ADR : expliquer SQLite, batch, un seuil de fraîcheur et une limite. Terminer sur la vérification locale. |

## Texte à dire, avec les gestes du tableau

### 0:00 — Le besoin

« ChronoTerre France s’adresse à quelqu’un qui prépare un déménagement. Ma question est : comment comparer deux communes à partir d’indicateurs documentés, puis savoir ce qu’il faut vérifier localement ? Je vais montrer trois indicateurs : les jours très chauds, les nuits chaudes et les jours de gel. L’idée est de rendre le compromis lisible. Le parcours fossile illustre aussi le trajet d’une donnée depuis sa source jusqu’à une fiche. »

### 0:40 — La collecte

« Pour le climat, j’utilise les valeurs communales publiées dans Climadiag. Pour les fossiles, PBDB fournit un identifiant d’occurrence, une collection et une référence. Les communes sont reliées au référentiel par leur code INSEE. Ici, le manifeste de la première page PBDB donne l’URL, la date et l’empreinte du fichier. Le raw est la réponse telle qu’elle a été reçue. Je peux donc le relire même si l’API est indisponible. Les données propres, dites curated, sont construites à partir de ce lot après vérification. »

### 1:30 — Le traitement et la qualité

« Je lance le socle court sur une vraie page. Il traite dix mille observations : sept mille neuf cent soixante et onze sont retenues, deux mille vingt-neuf rejetées. Les règles vérifient notamment l’identifiant, le rattachement géographique, l’ordre des âges et la présence d’une référence. Une valeur invalide est ajoutée à part pour la démonstration ; elle ne modifie pas la base nationale. Le rapport montre aussi deux empreintes identiques après rejeu. Les clés empêchent les doublons, et l’empreinte vérifie le contenu des lignes. Deux bases avec le même nombre de lignes pourraient pourtant avoir des valeurs différentes. La reconstruction complète a été vérifiée séparément, sur les cinquante-huit fichiers du lot. »

### 2:40 — L’incident et la reprise

« Dans une copie, le test d’incident a ajouté un octet au fichier brut PBDB. La règle P01 a arrêté la reconstruction au contrôle du fichier. Le journal porte un identifiant de run, l’étape et l’erreur. Le rapport réussi et l’empreinte du fichier SQLite sont restés identiques. La reprise consiste à remettre la réponse d’origine correspondant à l’empreinte, puis à relancer. Je ne recalcule pas le SHA pour faire passer un fichier corrompu. La preuve conserve le run en échec et les runs de reprise. »

### 3:30 — Une ligne jusqu’à son usage

« Je suis maintenant l’occurrence 76598. Le raw contient cet identifiant et le numéro de collection 4917. Dans la base, la ligne conserve `raw_id`, qui permet de remonter à la page PBDB. Elle est reliée au taxon, au site et à la bibliographie. La route de consultation du site restitue le même identifiant. C’est un exemple de traçabilité entre une collecte, un contrôle, une table et un usage. Le genre est Gryphaea. Une occurrence est un enregistrement documenté, pas une mesure du nombre d’animaux qui vivaient dans la région. »

### 4:30 — Ce que montre la comparaison

« À l’horizon 2050, La Rochelle présente 2,75 jours très chauds et 23,35 nuits chaudes par an dans les valeurs centrales publiées. Ajaccio présente 2 jours très chauds et 66,25 nuits chaudes. Le gel est moins fréquent à Ajaccio dans ce même corpus. La comparaison dépend donc du critère choisi ; je garde le même horizon et les mêmes définitions. Ce sont des projections représentatives de la commune. Pour un terrain, il faut consulter les documents locaux ; une couche d’aléa non disponible ne renseigne pas le risque. »

### 5:20 — Le choix d’architecture

« J’ai retenu SQLite parce que je peux faire les jointures et contrôler les clés, tout en livrant une base portable. Le batch permet de reproduire un instantané des sources. Le pipeline signale l’âge des acquisitions ; le délai de revue est une règle du projet. Si le besoin devient une interrogation nationale des parcelles et des aléas, je comparerai PostGIS sur des requêtes mesurées. Pour le rendu actuel, je peux expliquer la chaîne, montrer ses résultats et identifier ce qui reste à vérifier. »

## Oral blanc : questions, puis repères pour corriger tes réponses

Enregistre-toi ou réponds à voix haute en 20 à 40 secondes avant de lire la colonne de droite. Fais une première répétition avec le conducteur, puis une seconde avec seulement les sept phrases repères.

| Question probable | Réponse à savoir expliquer |
|---|---|
| Pourquoi ces sources ? | PBDB relie chaque occurrence à une collection et une référence ; Climadiag fournit des indicateurs communaux et des horizons documentés. Les référentiels permettent la jointure par code. |
| Différence raw et curated ? | Raw = octets collectés, date, URL, SHA. Curated = valeurs validées, typées et jointes. Un rejet reste à part avec ses raisons. |
| Quelle est ta clé métier ? | `occurrence_no` pour PBDB ; commune, indicateur, horizon, saison pour les valeurs Climadiag livrées. |
| Pourquoi SQLite plutôt que des JSON ou PostGIS ? | Les JSON restent utiles en entrée et en diffusion ; SQLite assure relations, unicité et installation locale. PostGIS répondrait à un besoin plus fort d’intersections spatiales et de concurrence. |
| Pourquoi du batch ? | Les données historiques et les niveaux projetés sont des lots datés. Le rejeu doit fonctionner hors réseau. Les appels IGN à la demande ne constituent pas un pipeline temps réel. |
| Comment prouves-tu l’idempotence ? | Deux reconstructions indépendantes, mêmes clés et mêmes valeurs triées, même empreinte métier. Les heures et run_id peuvent varier. |
| Un fournisseur tombe, que fais-tu ? | Délais et tentatives bornées ; cache vérifié et état d’erreur. Le jeu archivé permet de rejouer. Si l’intégrité échoue, restaurer le bon raw avant de relancer. |
| Que mesure l’alerte de fraîcheur ? | L’âge d’acquisition du lot. Elle ne change ni le millésime du jeu ni la période climatique. Le responsable du dépôt décide du rafraîchissement et conserve le lot de référence. |
| Pourquoi +50 ans n’est-il pas 2050 ? | Référence 2026, donc environ 2076. Les niveaux disponibles sont ceux de la source. Pas d’interpolation présentée comme projection. |
| Qu’est-ce qui n’est pas démontré ? | Une exposition nationale à l’adresse, une autorisation de construire et des tests réels sur tous les navigateurs. Les tests DOM vérifient la logique sans rendu de la carte. |
| Quelle a été la contribution de l’IA ? | Distinguer les choix que tu as fixés, l’assistance au développement et à la documentation, et tes propres vérifications. Montrer une règle de qualité et une décision que tu sais expliquer. |

Cible de répétition : **entre 5 min 30 et 6 min 30, gestes inclus**. Si tu dépasses, raccourcis la découverte fossile et conserve raw, incident, preuve de rejeu et choix d’architecture. Si tu vas trop vite, explique pourquoi une absence de donnée ne signifie pas zéro. La répétition personnelle est à faire sur ton ordinateur avant la remise.
