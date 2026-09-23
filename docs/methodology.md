# Méthode de calcul

## Fossiles et géographie

Les limites de recherche PBDB dépassent légèrement l’Île-de-France. La fonction point-dans-polygone vérifie les anneaux extérieurs et les trous des Polygon/MultiPolygon. Les points hors des huit départements sont rejetés. Les contours généralisés et les coordonnées historiques restent imparfaits : un classement proche d’une frontière administrative doit être interprété prudemment.

La règle Q06 exclut conservativement toutes les coordonnées rattachées à une unité politique. Cela peut retirer des occurrences effectivement franciliennes mais trop imprécises pour une exploration de proximité. La règle Q07 détecte les territoires déclarés incompatibles et six collections de provenance manifestement ambiguë. Elle ne prétend pas détecter toutes les erreurs historiques.

Les filtres temporels retiennent un fossile lorsque `[min_ma,max_ma]` recoupe la fenêtre choisie. Les bornes des menus sont des repères pédagogiques arrondis ; les âges originaux PBDB restent stockés. Les distances utilisent la formule sphérique de Haversine, rayon terrestre 6371 km. Elles n’intègrent ni routes ni accessibilité aux sites.

## Climat

Une température annuelle moyenne est la moyenne des températures moyennes journalières d’une année complète. La température de période est la moyenne des températures annuelles : chaque année a le même poids. La pluie annuelle est un cumul quotidien, puis la moyenne des cumuls annuels.

- Jour chaud : température maximale ≥ 30 °C.
- Nuit dite tropicale dans l’interface : température minimale quotidienne ≥ 20 °C, proxy fondé sur la journée UTC, pas une observation nocturne horaire exacte.
- Jour de gel : température minimale < 0 °C.

La relation `tmin ≤ tmean ≤ tmax` est imposée strictement. Les rares inversions d’un dixième ou deux dans EC-Earth sont mises en quarantaine ; le programme ne corrige pas leurs valeurs. Une année comprenant un jour rejeté est exclue des indicateurs. Une série reste analysable si au moins 90 % de ses années sont complètes. Le rapport et l’interface exposent les années exclues. Les mêmes années complètes servent aux profils mensuels de cette série. Une comparaison entre modèles peut donc inclure des fenêtres effectives différentes : cette limite est affichée.

ERA5-Seamless est utilisé explicitement, sans mode automatique Best Match : température ERA5-Land et pluie ERA5. Les pluies historiquement nulles du pilote ERA5-Land seul ne sont jamais traitées comme du temps sec. Le service réalise sa propre interpolation/correction spatiale ; l’application conserve le résultat sans prétendre disposer de mesures locales directes.

Les projections HighResMIP sont corrigées statistiquement par Open-Meteo sur ERA5-Land. L’application compare ces valeurs à la référence et ne recalcule pas elle-même la correction. Les comparaisons sont exploratoires, notamment pour les précipitations et les extrêmes, sensibles au modèle et à la résolution.

## Distance entre climats

Pour le futur de la commune A et la référence de la commune B :

```text
D(A,B) = sqrt( somme sur les 12 mois [ ((T_A-T_B)/1 °C)^2
                                    + ((P_A-P_B)/20 mm)^2 ] / 24 )
```

Les profils couvrent les températures mensuelles moyennes et les cumuls mensuels moyens de pluie. Les unités sont neutralisées par deux échelles fixées à l’avance. Température et pluie contribuent chacune pour 12 composantes. Une valeur basse indique une proximité de ces deux profils seulement.

Le seuil D ≤ 1 qualifie un analogue « proche » dans cette démonstration ; c’est un choix explicite de conception, pas un seuil validé par une publication scientifique. La propre commune fait partie des candidats de référence et est signalée. Le classement comprend seulement dix communes régionales ; le meilleur candidat peut être éloigné. Un résultat au-dessus du seuil affiche « aucun analogue proche ».

La longueur des barres de l’interface est `100/(1+D)` %, une échelle de visualisation monotone. Ce n’est ni une probabilité ni un « pourcentage de similarité ». La valeur numérique affichée reste D.

## Ce qui n’est pas estimé

Aucune reconstruction de température préhistorique, aucune future présence d’espèce, aucune probabilité de montée locale des eaux, aucune météo à une date future précise, aucun effet causal entre les deux jeux. Les deux branches se rejoignent par la géographie et l’expérience d’exploration, pas par une régression trompeuse à des échelles incompatibles.
