SOURCES=[
('geoapi','DINUM / IGN / INSEE','https://geo.api.gouv.fr/','Licence Ouverte 2.0','Centres administratifs, pas des adresses.'),
('etalab','Etalab / IGN ADMIN EXPRESS 2025','https://github.com/etalab/contours-administratifs','Licence Ouverte 2.0','Contours simplifiés à 100 m ; rattachement spatial indicatif aux limites.'),
('pbdb','Paleobiology Database, contributeurs et publications citées','https://paleobiodb.org/data1.2/','CC BY 4.0','Inventaire bibliographique non exhaustif ; localisation historique variable.'),
('climadiag','Météo-France / DRIAS / BRGM pour le niveau marin','https://climadiag-commune.meteofrance.com/','Données publiques Météo-France / Licence Ouverte Etalab (DRIAS)','Niveaux de réchauffement TRACC ; le champ mean contient la médiane publiée, pas une moyenne calculée ici.'),
('gpu','IGN / collectivités / Géoportail de l’urbanisme','https://apicarto.ign.fr/api/doc/gpu','Licence Ouverte 2.0, documents selon producteur','Information consultée à la date de collecte ; vérifier opposabilité et règlement.'),
('cadastre','DGFiP / IGN','https://apicarto.ign.fr/api/doc/cadastre','Licence Ouverte 2.0','Parcellaire cadastral, pas un bornage ni un droit à construire.'),
('georisques','BRGM / ministère de la Transition écologique','https://www.georisques.gouv.fr/','Licence Ouverte 2.0','Services testés indisponibles lors de la collecte ; aucune absence de risque déduite.'),
('commons','Auteurs identifiés, Wikimedia Commons','https://commons.wikimedia.org/','Par fichier','Illustrations vérifiées, pas de preuve de découverte locale.'),
('dreal_occitanie','DREAL Occitanie','https://www.occitanie.developpement-durable.gouv.fr/politique-de-diffusion-des-donnees-a2051.html','Réutilisation des informations publiques ; licence précise non renseignée sur la fiche data.gouv','Source DREAL attribuée, millésime 2013 ; respecter les avertissements du producteur. Licence Ouverte 2.0 non présumée.'),
('bordeaux_metropole','Bordeaux Métropole / BRGM','https://datahub.bordeaux-metropole.fr/explore/dataset/ri_alearga_s/','Licence Ouverte, version du lien source conservée dans les métadonnées','Couverture Bordeaux Métropole uniquement ; date de mise à jour du portail distincte du millésime géologique.'),
]
U='https://climadiag-commune.meteofrance.com/'
INDICATORS=[
('G1','Température moyenne','°C','Température de l’air moyenne, par saison.','climat',U),
('G2','Jours de gel','j/an','Minimum quotidien inférieur à 0 °C.','climat',U),
('G3','Cumul de précipitations','mm','Cumul saisonnier ; 1 mm = 1 litre par m².','pluie',U),
('G4','Jours avec précipitations','j/saison','Cumul quotidien supérieur à 1 mm selon la définition publiée.','pluie',U),
('R1','Jours de fortes précipitations','j/saison','Cumul quotidien supérieur à 20 mm. Ne prédit pas une inondation à une adresse.','pluie',U),
('R2','Précipitations quotidiennes remarquables','mm/j','Seuil dépassé environ un jour sur cent, indicateur publié.','pluie',U),
('R3','Élévation du niveau marin','cm','Évolution moyenne du niveau marin depuis 1995–2014. Ni recul côtier, ni carte de submersion.','littoral',U),
('R4','Jours de danger météorologique de feu','j/an','Indice Forêt Météo supérieur à 40. Pas une probabilité de destruction du bâti.','incendie',U),
('R5','Jours avec sol sec','j/saison','Indice d’humidité superficielle des sols SWI inférieur à 0,4. Ne mesure pas le service d’eau potable.','sols',U),
('S1','Jours très chauds','j/an','Température maximale dépassant 35 °C selon le texte de définition Climadiag ; le titre fournisseur emploie ≥35 °C. Données inchangées.','chaleur',U),
('S2','Nuits chaudes','nuits/an','Température nocturne ne descendant pas sous 20 °C selon le texte fournisseur (titre : >20 °C).','chaleur',U),
('S3','Jours en vague de chaleur','j/an','Épisode estival d’au moins 5 jours avec maximum quotidien supérieur de plus de 5 °C à la normale.','chaleur',U),
('AG1','Séquence sèche la plus longue','j','Maximum saisonnier de jours consécutifs recevant moins de 1 mm par jour.','sols',U),
]
HAZARDS={'inondation':'Inondation','remonteeNappe':'Remontée de nappe','retraitGonflementArgile':'Retrait-gonflement des argiles','feuForet':'Feu de forêt','submersionMarine':'Submersion marine','mouvementTerrain':'Mouvement de terrain','avalanche':'Avalanche','reculTraitCote':'Recul du trait de côte'}
