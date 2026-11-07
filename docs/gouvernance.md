# Gouvernance, fraîcheur et reprise

| Responsabilité | Règle du projet |
|---|---|
| Corpus remis | Jérémy, mainteneur du dépôt `jeremyESEO/chronoterre-france`, suit les versions, les licences et les rapports. Les producteurs restent responsables de leurs jeux et méthodes. |
| Données conservées | Conserver le lot de référence livré, les manifestes, le contrat, les rejets et les preuves de reconstruction pendant la période de correction et de recours. Après cette période, conserver le lot reproductible du rendu ; revoir les lots intermédiaires locaux et supprimer ceux devenus inutiles après vérification des conditions des producteurs. Pas de purge automatique ni de réécriture de l’historique public. |
| Minimisation | Référentiels publics, lieux d’essai publics, aucun secret nécessaire pour le lot livré. `.env` est ignoré. Pas de journal des adresses saisies ; le géocodage en ligne les transmet au service public IGN. Les essais délibérément invalides restent à part. |
| Cadence | Import par lots déclenché par le mainteneur avant une nouvelle remise ou lorsqu’un nouveau millésime est utile. Aucun rafraîchissement planifié n’est déployé. Le catalogue, le schéma, le millésime et les conditions sont vérifiés avant d’adopter un nouveau lot. |

## Contrôle de fraîcheur

`config/governance.json` contient les seuils internes : 30 jours pour l’échantillon urbanisme/cadastre, 90 pour le référentiel des communes, PBDB et Climadiag, 180 pour les couches locales d’aléa et 365 pour les contours millésimés. Ils indiquent quand **revoir l’acquisition**, pas l’âge maximal accepté du phénomène ni une promesse du fournisseur.

À la reconstruction, le pipeline calcule l’âge du téléchargement le plus ancien par source. Une page récente ne masque pas les autres pages d’un lot. `REVIEW_DUE` invite à vérifier la source avant réutilisation ; le lot figé demeure rejouable. `INVALID_TIMESTAMP` et `NO_POLICY` distinguent un défaut de métadonnée d’une donnée fraîche. Le téléchargement, la date de révision d’un jeu et son millésime sont affichés séparément lorsque disponibles. Pour le rendu, urbanisme et cadastre restent des échantillons historiques : vérifier la source officielle pour une décision réelle. Les réanalyses météorologiques complémentaires sont gérées dans leur propre manifeste, hors du bilan du pipeline principal.

## Journal et métriques

`reports/france_run.json` représente la dernière reconstruction réussie. Chaque essai reçoit un identifiant dans `reports/runs/<run_id>.json` : heures UTC, contrat, étapes, durée et compteurs de raw contrôlés. Le fichier d’échec contient le stade et l’erreur ; il ne remplace pas le dernier rapport réussi. Les journaux d’essais locaux sont ignorés par Git. Les preuves du rendu sont choisies et conservées dans `reports/rendu_final_*.json`.

Les champs `input_rows`, `accepted_rows`, `rejected_rows` et `duplicates_removed` concernent **les occurrences PBDB**. Un doublon compte dans les doublons écartés, même s’il a aussi un autre motif ; son enregistrement rejeté reste conservé. `rejected_by_domain` couvre toutes les familles. Pour Climadiag, les entités en entrée, les communes intégrées et les valeurs produites sont de grains différents ; il ne faut pas les sommer. Le taux de rejet PBDB se calcule par `rejected_rows / input_rows`, les doublons étant séparés. Un taux d’échec de runs exige un historique de runs défini ; aucun taux global à long terme n’est revendiqué.

## Reprendre un lot défaillant

1. Lire le `run_id`, le stade et le message. Un `P01 <raw_id>` identifie un fichier dont le SHA-256 ne correspond pas au manifeste.
2. Conserver le rapport. Revenir à la réponse originale correspondant à l’empreinte et vérifier sa provenance ; ne pas recalculer une empreinte pour faire accepter un fichier altéré.
3. Relancer `python -m national.pipeline --verify-replay` dans un seul processus de lancement, sans autre reconstruction concurrente. Contrôler l’intégrité, les compteurs et l’égalité des empreintes métier. Après une coupure pendant l’export, régénérer le lot Web complet avant de le republier.

Le [rapport d’incident](../reports/rendu_final_incident.json) documente une altération contrôlée en copie de travail, l’arrêt avant écriture, la base stable inchangée, puis la reprise. La durée et les dates du rapport de run varient ; l’empreinte métier n’inclut pas ces métadonnées d’exécution.
