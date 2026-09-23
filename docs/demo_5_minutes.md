# Démonstration en 3 à 5 minutes

Préparer le terminal dans le dossier du projet, ouvrir le dashboard et les fichiers `README.md`, `reports/run_report.json`, `data/raw/manifest.json`. Aucun appel réseau n’est requis pendant la soutenance.

| Temps | Action | Ce qu’il faut expliquer |
|---|---|---|
| 0:00–0:25 | Montrer la question et la commune Vélizy | L’application permet d’explorer des preuves locales et de comparer des climats, sans déduire le futur des fossiles. |
| 0:25–0:55 | Ouvrir le manifeste puis un raw PBDB | Source identifiable, URL, date UTC, JSON original, empreinte SHA-256. |
| 0:55–1:35 | `python src/pipeline.py --offline --verify-replay` | Le pipeline profile, contrôle, sépare les rejets et charge la base. La deuxième exécution prouve l’idempotence. |
| 1:35–2:05 | `python src/demo_rejection.py` puis ouvrir sa preuve | Ligne synthétique isolée : pluie négative, date impossible et températures incohérentes ; jamais mélangée aux vraies données. |
| 2:05–2:35 | Ouvrir curated, le rapport et `idempotence.json` | Entrées = acceptées + rejetées + doublons. Même contenu trié des tables et même SHA-256 au rejeu. |
| 2:35–3:25 | Dans Le passé, rayon autour de Vélizy, groupe puis Surprenez-moi | Une vraie requête analytique combinant lieux, âges, taxons et référence. Montrer un lien bibliographique. |
| 3:25–4:10 | Horizon 2050, changer de modèle puis lire le classement | Distinguer période, modèle, couverture et score. « Aucun analogue proche » est possible dans un petit périmètre régional. |
| 4:10–4:40 | Les coulisses et une requête SQL | 11 règles, source des rejets, exemple de JOIN/GROUP BY ou fonction de fenêtre. |
| 4:40–5:00 | Donner une limite et une amélioration | Biais documentaire, coordonnées historiques et seulement deux modèles. Extension : meilleure géolocalisation ou validation climatique plus poussée. |

Si le pipeline est lent sur l’ordinateur de présentation, lancer la commande dès 0:25 et parler du raw pendant son exécution. Les preuves fournies permettent de discuter des résultats sans connexion réseau.

## Réponses à préparer

- **Pourquoi PBDB ?** Les âges et les références sont au cœur de la question ; GBIF est plus hétérogène sur ces champs pour les fossiles.
- **Quelle clé métier ?** `occurrence_no` pour les fossiles ; `(series_id, date)` pour le climat. Un nom de fossile n’est pas une clé unique.
- **Pourquoi 12 tables ?** Séparer les entités stables et éviter de recopier les citations ou les informations des communes à chaque jour/occurrence.
- **Pourquoi garder les rejets ?** Pour expliquer les exclusions et auditer le résultat ; la qualité n’est pas seulement un nettoyage silencieux.
- **Si une API tombe ?** Reprise par cache et nouvelles tentatives bornées ; exécution hors ligne possible ; échec clair si une pièce du lot manque.
- **Si le schéma change ?** Vérifications de structure et d’unités bloquantes, rapport d’échec, base précédente préservée.
- **Pourquoi changer ERA5-Land ?** Le test réel a montré des pluies absentes. ERA5-Seamless fournit les températures ERA5-Land et la pluie ERA5. Aucune pluie n’a été inventée.
- **Les deux modèles sont-ils deux scénarios ?** Non. Ils simulent le climat différemment sous un forçage proche RCP8.5.
- **Pourquoi certaines années manquent ?** Quelques jours incohérents sont rejetés ; une année incomplète n’alimente pas les indicateurs. Le nombre exact d’années apparaît dans l’interface.
- **Pourquoi pas une causalité passé/futur ?** Le lien est géographique et pédagogique. Les jeux n’ont ni la même résolution temporelle ni la même fonction scientifique.
- **Qui a réalisé le code ?** Présenter les outils et l’assistance utilisés de façon transparente, puis être capable d’expliquer une règle, une jointure et la preuve de rejeu.
