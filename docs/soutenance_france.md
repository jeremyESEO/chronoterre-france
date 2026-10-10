# Démonstration de 3 à 5 minutes

0:00–0:30 : question, usagers, deux parcours reliés par le territoire. Dire que la plateforme nationale est une extension du socle TP.

0:30–1:00 : ouvrir un manifeste, montrer URL, date, SHA et fichier raw d’origine. Expliquer que le ZIP climatique est une compression sans perte.

1:00–2:00 : exécuter `python -m national.demo`. Montrer la page PBDB réelle, le rejet `TEST_INVALIDE_ISOLE`, les effectifs et l’égalité des deux empreintes. Ouvrir `data/curated/demo_tp.sqlite`. La donnée invalide ne touche jamais la production.

2:00–3:15 : application : rechercher La Rochelle, passer 2030 → 2100, afficher les preuves. Comparer Ajaccio. Signaler la maille climatique, le +50 ans désactivé et l’absence de score d’habitabilité. Cette partie doit être répétée dans un navigateur avant la soutenance, la QA visuelle n’ayant pas été possible dans la session de livraison.

3:15–4:15 : passer aux fossiles, filtre taxonomique, découvrir une publication. Présenter une image illustrative et sa licence ; montrer aussi le cas sans image.

4:15–5:00 : SQL 15 couverture des médias, rapport de qualité et une limite : seulement deux couches locales d’aléas. Montrer la sauvegarde V1.

## Réponses techniques

- Décision : comparer des expositions documentées et préparer les vérifications, sans décider un achat.
- Choix des sources : producteurs identifiés, accès public réellement essayé, identifiants stables et provenance conservée.
- Clé métier : occurrence_no PBDB ; climat = commune + indicateur + période + saison dans ce corpus unique.
- Rejeu : base reconstruite atomiquement ; empreinte canonique des lignes triées de toutes les tables applicatives. Identité des clés et du contenu.
- Source en panne : cache existant et état d’erreur explicite ; aucune valeur fictive. Mise à jour manuelle.
- Changement de schéma : arrêt sur champ indispensable manquant, examen du raw, nouvelle version de contrat. Pas de changement silencieux de sens.
- Production nationale spatiale : PostgreSQL/PostGIS, jobs d’import, stockage de fichiers, supervision, quotas et revue de licences ; le serveur local n’est pas exposé tel quel.
- Pourquoi pas 2076 : les données proposent des niveaux/horizons, pas une trajectoire annuelle interpolable.
- Pourquoi pas un score : des manques, des échelles et des natures incompatibles ; un bon indicateur ne compense pas une restriction.
- V1 : tests conservés, données archivées ; pas de mélange ERA5/DRIAS ni de recyclage des compteurs.
