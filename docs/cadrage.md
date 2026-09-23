# Cadrage fonctionnel et académique

## Question et décision

**Quelles traces du vivant sont documentées autour des communes franciliennes, et dans quelle mesure leur climat projeté à l’horizon 2050 ressemble-t-il aux climats de référence de la région ?**

L’utilisateur cible est un étudiant, un habitant curieux ou un médiateur scientifique. Il choisit une commune, une période et un indicateur afin d’identifier une découverte à explorer ou une différence climatique à expliquer. Il peut vérifier la référence derrière un résultat et distinguer une information documentée d’une extrapolation.

## Trois cas d’usage

1. En tant qu’habitant francilien, je veux rechercher les fossiles documentés dans un rayon autour de ma commune, afin de découvrir un passé local que je peux relier à une publication.
2. En tant qu’étudiant, je veux comparer la référence climatique à deux projections sur la même commune, afin d’expliquer les écarts et les limites entre modèles.
3. En tant qu’enseignant, je veux rejouer la collecte transformée depuis les fichiers bruts et consulter les rejets, afin de vérifier la fiabilité et la reproductibilité du travail.

## Trois KPI principaux

| KPI | Calcul | Usage et précaution |
|---|---|---|
| Couverture paléontologique | COUNT(DISTINCT site_id) et COUNT(DISTINCT taxon_id) selon le filtre | Mesure ce qui est documenté, pas l’abondance ancienne. |
| Écart de température moyenne | Moyenne annuelle projetée − moyenne annuelle de référence, en °C | Calcul par commune et modèle, avec le nombre d’années complètes. |
| Distance au meilleur analogue régional | Minimum de la RMSE sur 12 températures et 12 pluies mensuelles normalisées | Restreint aux dix communes candidates ; seuil « proche » ≤ 1. |

Indicateurs techniques complémentaires : nombre d’entrées, lignes acceptées, rejets, doublons, échecs par règle, complétude temporelle, empreinte des tables.

## Périmètre arrêté

Région 11 : Paris, Seine-et-Marne, Yvelines, Essonne, Hauts-de-Seine, Seine-Saint-Denis, Val-de-Marne, Val-d’Oise. Les coordonnées PBDB sont d’abord cherchées dans une boîte englobante, puis filtrées par les polygones départementaux. L’extrait brut contient donc des voisins hors région ; la zone curated et l’application n’en contiennent pas.

Dix communes pour le climat : Paris, Vélizy-Villacoublay, Cergy, Meaux, Melun, Fontainebleau, Évry-Courcouronnes, Saint-Denis, Créteil, Antony. Les centres sont fournis par l’API Découpage administratif. Ce choix couvre les huit départements sans prétendre représenter toutes les situations locales.

Référence : 1991–2020. Futur : 2030–2049, nommé horizon 2050 car l’API s’arrête au 1er janvier 2050. Les fossiles conservent leurs intervalles d’âge propres en millions d’années. Ces échelles ne sont pas assemblées en une fausse série chronologique continue.

## Faisabilité et progression

Séance 1 proposée : cadrage (30 min), deux sources candidates (30 min), grain/contrat/modèle (45 min), collecte PBDB et raw (45 min), contrôles initiaux et architecture (30 min).

Séance 2 proposée : profilage et nettoyage (45 min), SQLite et CSV (45 min), rejets/tests/rejeu (45 min), rapport et démonstration (45 min). Les extensions climatiques et web servent à prolonger ce socle préparé ; elles ne remplacent pas les attendus évalués.
