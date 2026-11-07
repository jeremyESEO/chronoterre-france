# Feuille de route vers une plateforme nationale exploitable

Cette feuille de route décrit du travail prévu, pas des fonctionnalités déjà disponibles.

## 1 — Socle serveur
- [ ] Définir les besoins d'hébergement, la volumétrie et le budget.
- [ ] Livrer PostgreSQL/PostGIS, migrations et procédure de restauration.
- [ ] Développer une API serveur documentée OpenAPI.
- [ ] Ajouter validation, pagination, limites d'emprise, délais et quotas.
- [ ] Vérifier que l'interface interroge réellement le backend déployé.

## 2 — Données de risques
- [ ] Tester les accès officiels Géorisques sur des réponses réelles.
- [ ] Étendre les intersections inondations/argiles avec versions et couverture.
- [ ] Évaluer et intégrer l'historique BDIFF à son grain disponible.
- [ ] Évaluer les indices projetés FeuMeteo-2022 et leurs scénarios.
- [ ] Croiser végétation et données d'exposition sans inventer de probabilité de destruction.
- [ ] Versionner les imports, contrôles, rejets et mises à jour.

## 3 — Résidentiel et urbanisme
- [ ] Développer les observations climatiques Météo-France avec contrôles de séries.
- [ ] Renforcer les documents, zones, prescriptions et servitudes GPU.
- [ ] Évaluer les services, mobilité et données immobilières actuelles.
- [ ] Séparer adéquation personnelle, exposition et qualité de couverture.
- [ ] Livrer un dossier exportable par lieu avec sources et vérifications.

## 4 — Usages professionnels
- [ ] Définir le périmètre d'analyse d'exposition d'un portefeuille de biens.
- [ ] Développer authentification et gestion des données privées.
- [ ] Livrer imports, diagnostics de géocodage et exports traçables.
- [ ] Documenter les informations insuffisantes pour modéliser pertes et primes.

## 5 — Réception et déploiement
- [ ] Exécuter des parcours réels au navigateur, clavier et mobile.
- [ ] Mesurer la performance sur un périmètre annoncé.
- [ ] Tester des lieux contrastés, les pannes fournisseurs et la restauration.
- [x] Publier le dépôt GitHub et obtenir une première CI réussie.
- [ ] Déployer le backend et la base sur une infrastructure compatible.
- [ ] Confirmer URL, disponibilité, mises à jour et procédure de retour arrière.

Sources, licences, coûts et accès devront être confirmés avant engagement. GitHub héberge le code et le suivi ; GitHub Pages seul ne fait pas tourner le backend Python et PostGIS.
