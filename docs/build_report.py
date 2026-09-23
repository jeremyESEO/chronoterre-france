"""Régénère le dossier PDF depuis les résultats réels et les figures livrées.

Facultatif : pip install -r docs/requirements-report.txt
Puis python docs/build_report.py
"""
from pathlib import Path
import json
import sys
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether,Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from PIL import Image as PILImage

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import read_json
from src.transform import analogues

FONTROOT=Path('/usr/share/fonts/truetype/dejavu')
if FONTROOT.exists():
    for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(FONTROOT/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
else:
    # Repli portable ; le rendu livré utilise DejaVu Sans incorporé.
    for alias,face in [('Body','Helvetica'),('Bold','Helvetica-Bold'),('Mono','Courier')]:
        pdfmetrics.registerFont(pdfmetrics.Font(alias,face,'WinAnsiEncoding'))

NAVY=colors.HexColor('#13283e');TEAL=colors.HexColor('#007e76');MUTED=colors.HexColor('#52667c');LIGHT=colors.HexColor('#eaf3f8');GOLD=colors.HexColor('#fff3df')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyFR',fontName='Body',fontSize=10,leading=15,textColor=NAVY,spaceAfter=10))
styles.add(ParagraphStyle(name='SmallFR',fontName='Body',fontSize=8.3,leading=12,textColor=MUTED,spaceAfter=7,wordWrap='CJK'))
styles.add(ParagraphStyle(name='H1FR',fontName='Bold',fontSize=21,leading=26,textColor=NAVY,spaceAfter=18))
styles.add(ParagraphStyle(name='H2FR',fontName='Bold',fontSize=12.5,leading=17,textColor=TEAL,spaceBefore=12,spaceAfter=8))
styles.add(ParagraphStyle(name='Kicker',fontName='Bold',fontSize=8.5,leading=13,textColor=TEAL,spaceAfter=9))
styles.add(ParagraphStyle(name='Cover',fontName='Bold',fontSize=43,leading=50,textColor=NAVY,spaceAfter=12))
styles.add(ParagraphStyle(name='CodeFR',fontName='Mono',fontSize=8,leading=12,textColor=NAVY,backColor=LIGHT,borderPadding=10,spaceAfter=12))
styles.add(ParagraphStyle(name='CellFR',fontName='Body',fontSize=8.5,leading=12,textColor=NAVY))
styles.add(ParagraphStyle(name='HeadCell',fontName='Bold',fontSize=8.5,leading=12,textColor=colors.white))

def P(text,style='BodyFR'):return Paragraph(text,styles[style])
def para(text):story.append(P(text))
def small(text):story.append(P(text,'SmallFR'))
def section(number,title):
    if story:story.append(PageBreak())
    story.extend([P(f'CHRONOTERRE  /  {number:02d}','Kicker'),P(title,'H1FR')])
def h(text):story.append(P(text,'H2FR'))
def table(rows,widths):
    values=[[P(escape(str(v)),'HeadCell' if i==0 else 'CellFR') for v in row] for i,row in enumerate(rows)]
    t=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,0),1,TEAL)]))
    story.extend([t,Spacer(1,12)])
def picture(path,width=491,maxheight=410):
    w,h=PILImage.open(path).size;scale=min(width/w,maxheight/h);story.extend([Image(str(path),width=w*scale,height=h*scale),Spacer(1,10)])
def code(text):story.append(Preformatted(text,styles['CodeFR']))
def number(n):return f'{n:,}'.replace(',',' ')
def dec(n,k=1):return f'{n:.{k}f}'.replace('.',',')
def frame(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#cbd9e2'));canvas.line(48,794,547,794);canvas.setFont('Body',8);canvas.setFillColor(MUTED);canvas.drawString(48,806,'CHRONOTERRE  •  ÎLE-DE-FRANCE');canvas.drawRightString(547,806,'ESEO 2026–2027');canvas.line(48,43,547,43);canvas.drawString(48,28,'Architectures BD et collecte de données  |  Dossier technique');canvas.drawRightString(547,28,str(doc.page))

r=read_json(ROOT/'reports/run_report.json');D=read_json(ROOT/'data/curated/dashboard.json');sql=read_json(ROOT/'reports/sql_results.json');cfg=read_json(ROOT/'config/settings.json');proof=read_json(ROOT/'reports/idempotence.json')
bs=next(s for s in D['climate'] if s['city_code']=='78640' and s['kind']=='baseline')
fs=[s for s in D['climate'] if s['city_code']=='78640' and s['kind']=='future']
story=[]

story.extend([Spacer(1,50),P('PROJET PERSONNEL DE COLLECTE DE DONNÉES','Kicker'),P('ChronoTerre','Cover'),P('Une région, plusieurs mondes.','H1FR')])
para('Explorer les traces du vivant en Île-de-France et comparer le climat de référence à deux projections à l’horizon 2050.')
story.append(Spacer(1,24))
table([['Périmètre','Données réellement intégrées'],['Île-de-France · 8 départements',f"{number(r['table_counts']['fossil_occurrence'])} occurrences paléontologiques"],['10 communes climatiques',f"{number(r['table_counts']['climate_day'])} journées climatiques validées"],['Référence 1991–2020 · futur 2030–2049','12 tables relationnelles · 15 analyses SQL'],['Pipeline + API + dashboard interactif','11 règles par ligne · rejeu vérifié sans doublons']],[232,259])
h('La question centrale')
para('<b>Quelles traces du vivant sont documentées autour des communes franciliennes, et dans quelle mesure leur climat projeté à l’horizon 2050 ressemble-t-il aux climats de référence de la région ?</b>')
small('Lot collecté le 23 septembre 2026. Les chiffres de ce dossier sont calculés à partir du lot livré, et non ajoutés à la main au dashboard. Les références détaillées sont conservées dans la base et les fichiers raw.')
small('Les deux branches se rejoignent par les lieux et l’exploration. Le projet ne prétend pas prédire la présence future d’espèces à partir des fossiles.')

section(1,'Cadrage et utilité')
para('ChronoTerre s’adresse aux habitants curieux, étudiants et médiateurs scientifiques. Un lieu familier devient un point d’entrée vers des preuves paléontologiques et des comparaisons climatiques vérifiables. L’utilisateur peut modifier sa sélection et retrouver la source derrière chaque résultat.')
h('Trois cas d’usage')
table([['Utilisateur','Besoin et finalité'],['Habitant','Je veux rechercher les fossiles documentés autour de ma commune afin de découvrir un passé local relié à une publication.'],['Étudiant','Je veux comparer une référence climatique à deux projections afin de comprendre les écarts et les limites des modèles.'],['Enseignant','Je veux rejouer le pipeline et consulter les rejets afin de vérifier sa fiabilité et sa reproductibilité.']],[100,391])
h('Trois KPI')
table([['KPI','Définition'],['Couverture documentaire','Nombre de collections et de taxons distincts selon les filtres ; ce n’est pas une mesure de l’abondance ancienne.'],['Écart de température','Moyenne annuelle projetée moins moyenne annuelle de référence, par commune et par modèle, avec couverture temporelle.'],['Meilleur analogue','Minimum de distance entre profils mensuels température/pluie, parmi dix communes franciliennes.']],[155,336])
h('Un périmètre volontairement local')
para('Les huit départements sont présents. Les dix communes climatiques sont Paris, Vélizy-Villacoublay, Cergy, Meaux, Melun, Fontainebleau, Évry-Courcouronnes, Saint-Denis, Créteil et Antony. La version livrée ne compare aucune ville étrangère.')
small('Le socle des deux séances de 3 h est la collecte, le contrat, le contrôle, le stockage et le rejeu. Le climat, l’API et le dashboard constituent des extensions fournies, à présenter après les preuves du pipeline.')

section(2,'Choisir des sources qui répondent vraiment')
table([['Candidat','Atouts','Décision / limite'],['PBDB API 1.2','Identifiants, âges, milieu, références','Retenu ; couverture bibliographique et positions imparfaites.'],['GBIF FossilSpecimen','Spécimens de nombreux musées, API','Alternative évaluée ; contexte géologique hétérogène, doublons possibles avec PBDB.'],['ERA5-Land seul','Températures sur 30 ans','Pilote non retenu : pluie absente dans les réponses.'],['ERA5-Seamless','Température ERA5-Land + pluie ERA5','Retenu, résolutions distinctes selon variable.'],['Open-Meteo Climate','Deux modèles CMIP6 HighResMIP','Retenu ; forçage proche RCP8.5, pas une prévision météo.']],[111,172,208])
h('Accès, attribution et preuve')
para('PBDB est diffusée sous CC BY 4.0. Les publications originales restent citées occurrence par occurrence ; les articles complets ne sont pas copiés. Open-Meteo diffuse les données avec attribution aux producteurs CMIP6, Copernicus et ECMWF. Le service gratuit est utilisé dans le cadre non commercial du projet, avec cache et espacement des requêtes.')
para('La géographie vient des contours Etalab/IGN ADMIN EXPRESS, millésime 2025, simplifiés à 100 m, et de l’API Découpage administratif pour les centres des communes. Les données métropolitaines utilisées relèvent de la Licence Ouverte.')
small('Documentation principale : paleobiodb.org/data1.2/ ; open-meteo.com/en/docs/historical-weather-api ; open-meteo.com/en/docs/climate-api ; geo.api.gouv.fr/decoupage-administratif ; github.com/etalab/contours-administratifs. URL exactes, conditions, licences et dates : docs/source_assessment.md et data/raw/manifest.json.')
h('Une décision guidée par le profilage')
para('Le premier test ERA5-Land a renvoyé des précipitations NULL. Ces valeurs n’ont pas été transformées en zéros. Le choix final ERA5-Seamless utilise la température ERA5-Land et la pluie ERA5. Les raw du pilote et son rapport sont conservés pour rendre la décision vérifiable.')

section(3,'Architecture et fonctionnement du pipeline')
picture(ROOT/'docs/architecture.png',maxheight=320)
h('Ordre des opérations')
para('Le collecteur sauvegarde les octets reçus avant tout parsing. Le manifeste associe le fichier à l’URL complète, à la date UTC, à la taille et au SHA-256. Les paramètres de source et de période proviennent du fichier de configuration. Les erreurs réseau déclenchent des tentatives bornées ; une collecte incomplète bloque le traitement.')
para('Le pipeline vérifie l’intégrité des fichiers, les unités et la structure des tableaux. Il produit un profil avant nettoyage : effectif, types, valeurs manquantes, doublons exacts, bornes et fréquences. Les contrôles par ligne séparent ensuite données acceptées et rejets motivés.')
para('La transformation construit les dimensions et faits SQLite, exporte les CSV et génère le jeu compact du navigateur. Un fichier de base temporaire n’est publié qu’après validation des contraintes. Les réponses brutes ne sont jamais réécrites.')
small('Le manifeste courant est un pointeur de cache ; les réponses horodatées et les manifestes des lots complets sont immuables. Les fichiers sources nationaux sont conservés tels que reçus ; curated et le dashboard ne publient que le périmètre régional retenu.')

section(4,'Modèle relationnel et cardinalités')
picture(ROOT/'docs/schema.png',maxheight=450)
para('Une occurrence relie une collection, un taxon, un intervalle géologique et une publication. Les collections et les taxons sont en relation N–N via les occurrences. Une série climatique relie une commune et un modèle sur une fenêtre ; chaque jour appartient à une seule série.')
para('Le producteur, la licence, la citation et les coordonnées de la commune ne sont pas répétés à chaque observation quotidienne. Les coordonnées demandées et celles de la maille renvoyée sont séparées. Les deux branches partagent les départements et la traçabilité des fichiers bruts.')
small('Schéma complet avec PK, FK, UNIQUE, NOT NULL et CHECK : sql/schema.sql. Index sur les recherches par collection, taxon et département. La clé composée des journées organise les accès par série/date. Deux vues : v_fossils et v_climate_annual.')

section(5,'Grain, dictionnaire et contrat versionné')
para('<b>Fossiles :</b> une occurrence PBDB documentée, et non un animal compté. <b>Climat :</b> un jour UTC d’une série commune/modèle/période. Le modèle ne mélange jamais ces deux grains dans une même table de faits.')
table([['Champ initial','Type / unité','Rôle'],['occurrence_no','Entier positif','Clé métier fossile'],['collection_no','Entier positif','Collection et contexte de collecte'],['identified_name','Texte','Nom identifié dans la publication'],['accepted_no / accepted_name','Texte','Taxon accepté PBDB'],['lat / lng','Réel / degré WGS84','Coordonnées de la collection'],['min_ma / max_ma','Réel / Ma','Bornes récente et ancienne'],['reference_no','Entier positif','Publication source'],['series_id + date','Texte + date ISO','Clé métier climatique'],['tmin_c / tmean_c / tmax_c','Réel / °C','Températures quotidiennes à 2 m'],['precipitation_mm','Réel / mm/j','Cumul journalier de pluie']],[181,135,175])
h('Contrat 1.0.0')
para('Le contrat décrit les champs, les unités, les clés, les valeurs facultatives, les contrôles bloquants et la politique d’agrégation. Il est écrit en JSON, syntaxe valide en YAML 1.2, afin de le lire sans bibliothèque Python externe. Le pipeline utilise ses champs structurants et ses unités attendues.')
para('Les identifiants INSEE restent des chaînes. Les dates sont validées avec un vrai calendrier, pas seulement une expression régulière. Les marqueurs de classification absente sont normalisés en NULL. Les noms identifiés et les noms acceptés sont conservés séparément pour ne pas effacer l’information originale.')
small('Dictionnaire initial complet de 14 champs fossiles et 6 champs climatiques : config/data_contract.yaml. Dictionnaire des douze tables, relations et types : docs/data_dictionary.md.')

section(6,'Contrôler, rejeter et expliquer')
table([['ID','Condition résumée','Échecs']]+[[x['id'],x['condition'],x['failure_count']] for x in r['rules']],[43,390,58])
para('Chaque ligne rejetée conserve son jeu, sa clé, toutes les règles en échec, un détail éventuel et la ligne d’origine sérialisée. Une ligne peut échouer à plusieurs règles : les compteurs ne doivent pas être additionnés pour calculer un nombre de rejets.')
para('Q03 traduit un choix de périmètre, pas nécessairement une erreur de source. Q06 est volontairement conservatrice : même une occurrence réellement francilienne est écartée si sa géolocalisation n’est fondée que sur une unité politique. Q07 exclut notamment une tortue placée à Paris alors que la source signale une provenance inconnue et le lieu du musée.')
small('Les contrôles structurels sont bloquants : intégrité raw, schéma, unités, tableaux, fenêtres et clés étrangères. En cas d’échec, le programme produit un rapport d’échec et ne remplace pas la base antérieure.')

section(7,'Résultats d’exécution et preuve de rejeu')
table([['Jeu','Entrées','Acceptées','Rejetées','Doublons']]+[[name,number(v['input']),number(v['accepted']),number(v['rejected']),number(v['duplicates'])] for name,v in r['datasets'].items()]+[['TOTAL',number(r['input_rows']),number(r['accepted_rows']),number(r['rejected_rows']),number(r['duplicates_removed'])]],[117,92,98,92,92])
para(f"Bilan exact : {number(r['input_rows'])} = {number(r['accepted_rows'])} + {number(r['rejected_rows'])} + {r['duplicates_removed']}. Statut <b>{r['quality_status']}</b> : des exclusions sont attendues et expliquées. Les journées climatiques représentent la majorité du volume ; un bon taux global ne doit pas masquer les limites de couverture des fossiles.")
h('Idempotence : même entrée, même contenu')
para('Le pipeline reconstruit la base, applique les contraintes puis remplace le fichier de sortie. Chaque table applicative est triée et ses valeurs sont hachées ; cette empreinte est indépendante des pages internes SQLite. Le test fourni compare les empreintes et les effectifs de deux exécutions consécutives.')
small('Empreinte 1 : '+proof['first']+'<br/>Empreinte 2 : '+proof['second'])
para('<b>Résultat : identiques.</b> Aucun accroissement de données au rejeu ; les comptes des douze tables sont identiques. Les rapports d’exécution peuvent avoir des horodatages différents, ce qui est normal.')
h('Démontrer une donnée invalide')
code('python src/demo_rejection.py\npython -m unittest discover -s tests -v')
para('La démonstration crée une ligne synthétique isolée : 30 février 2040, précipitations négatives, température minimale supérieure à la moyenne. Elle est rejetée par Q08, Q09 et Q10 et n’est jamais introduite dans la production. Neuf tests vérifient les cas limites du calendrier, les nombres non finis, la géographie, les analogues et les contraintes SQL.')

section(8,'Exploiter la base avec SQL')
para('Quinze analyses sont livrées dans sql/analyses.sql et leurs résultats calculés dans reports/sql_results.json. Elles couvrent jointures, LEFT JOIN, GROUP BY, HAVING, sous-requête, CTE, fonctions de fenêtre, évolution temporelle et provenance.')
h('Exemple 1 — couverture par département')
code('SELECT d.name, COUNT(o.occurrence_id) AS occurrences,\n       COUNT(DISTINCT o.taxon_id) AS taxa\nFROM department d\nLEFT JOIN fossil_site s USING(department_code)\nLEFT JOIN fossil_occurrence o USING(site_id)\nGROUP BY d.department_code\nORDER BY occurrences DESC;')
table([['Département','Collections','Occurrences','Taxons']]+[[x['name'],x['collections'],x['occurrences'],x['taxa']] for x in sql['queries'][0]['results']],[218,90,93,90])
small('Les Yvelines dominent cet extrait ; cette différence ne démontre pas une biodiversité ancienne supérieure. Grignon et d’autres localités ont été beaucoup documentés. Les taxa par département ne s’additionnent pas en un total régional : un taxon peut être partagé.')

section(9,'Du climat quotidien aux comparaisons')
para('Les indicateurs annuels sont calculés uniquement sur des années complètes. La moyenne de période donne le même poids à chaque année. Les mois utilisent les mêmes années retenues. Une synthèse exige au moins 90 % d’années complètes ; les dates exclues sont affichées.')
h('Exemple calculé : Vélizy-Villacoublay')
table([['Série','Années','T. moyenne','Jours ≥ 30 °C/an','Pluie/an'],['Référence 1991–2020',bs['complete_years'],dec(bs['summary']['mean_c'])+' °C',dec(bs['summary']['hot_days']),dec(bs['summary']['rain_mm'],0)+' mm']]+[[s['model_id'].replace('_','-'),f"{s['complete_years']}/20",dec(s['summary']['mean_c'])+' °C',dec(s['summary']['hot_days']),dec(s['summary']['rain_mm'],0)+' mm'] for s in fs],[165,60,88,95,83])
para('À Vélizy, l’écart moyen est d’environ +1,1 °C avec MRI et +1,2 °C avec EC-Earth dans le lot analysé. Les jours chauds passent d’environ 4,4 par an en référence à 17,1 avec MRI ou 11,3 avec EC-Earth. Ces valeurs sont des résultats exploratoires de modèles, pas des prévisions de journées exactes.')
para('EC-Earth exclut l’année 2035 à Vélizy après rejet d’un jour aux températures incohérentes. Sa moyenne porte sur 19 années et celle de MRI sur 20. La comparaison reste informative mais ses fenêtres effectives diffèrent. L’étendue entre deux modèles n’est pas un intervalle de confiance et ne couvre pas toute l’incertitude climatique.')
h('Exemple 2 — événements consécutifs')
code("WITH hot AS (\n SELECT series_id, date,\n  julianday(date) - ROW_NUMBER() OVER(\n    PARTITION BY series_id ORDER BY date) AS grp\n FROM climate_day WHERE tmax_c >= 30\n)\nSELECT series_id, MIN(date), MAX(date), COUNT(*) AS days\nFROM hot GROUP BY series_id, grp\nORDER BY days DESC LIMIT 10;")
small('Ce SQL identifie des séquences de jours chauds. Ce n’est pas une définition médicale ou réglementaire de la canicule. Les nuits ≥ 20 °C utilisent la température minimale quotidienne UTC comme proxy, et non une mesure nocturne horaire exacte.')

section(10,'La recherche de ressemblances climatiques')
para('Chaque climat est décrit par 24 composantes : douze températures mensuelles moyennes et douze cumuls mensuels moyens de pluie. Pour éviter de comparer des °C à des mm, les écarts de température sont divisés par 1 °C et les écarts de pluie par 20 mm.')
code('D = sqrt( somme_mois [ (écart_T / 1 °C)^2\n                    + (écart_P / 20 mm)^2 ] / 24 )')
para('Un score petit signifie une meilleure proximité sur ces deux profils. Le seuil D ≤ 1 est pédagogique, fixé à l’avance et documenté ; il n’est pas issu d’une validation scientifique. La recherche reste strictement régionale, avec dix candidats, et inclut le climat de référence de la commune étudiée.')
rows=[]
names={c['city_code']:c['name'] for c in D['cities']}
for s in fs:
    best=analogues(D['climate'],'78640',s['model_id'],cfg['analogue'])[0]
    rows.append([s['model_id'].replace('_','-'),names[best['city_code']],dec(best['distance'],2),'Oui' if best['close'] else 'Non'])
table([['Futur de Vélizy','Référence la plus proche','Distance','D ≤ 1']]+rows,[178,154,76,83])
para('Dans ce lot, Melun est le candidat le plus proche pour le futur de Vélizy avec les deux modèles. Cela ne signifie ni climat identique, ni même météo quotidienne, ni même biodiversité. Une autre sélection de variables, d’échelles ou de communes pourrait modifier le classement.')
h('Ne pas forcer une réponse séduisante')
para('Si tous les candidats dépassent le seuil, l’application annonce « aucun analogue proche » puis montre le moins éloigné. Le programme ne convertit pas la distance en probabilité ni en pourcentage scientifique de similarité. La barre de classement n’est qu’une représentation monotone du score.')
h('Améliorations possibles')
para('Comparer la robustesse du classement à plusieurs échelles de normalisation, augmenter le nombre de modèles, évaluer la sensibilité aux années exclues et enrichir les communes candidates dans le même périmètre. Ces améliorations demandent une collecte et un protocole documentés, pas de nouveaux chiffres saisis manuellement.')

section(11,'Dashboard, API et expérience ludique')
for filename in ['dashboard_past.jpg']:
    p=ROOT/'docs'/filename
    if p.exists():picture(p,maxheight=310)
para('Le dashboard propose quatre vues : fossiles, climat de référence, horizon 2050 et coulisses. Les filtres modifient réellement la carte, les effectifs et les exports. Les fiches détaillent les bornes d’âge, le contexte et la publication. La carte se déplace, se zoome et permet de sélectionner les lieux.')
para('La découverte aléatoire tire une occurrence dans la sélection courante. Le quiz fournit des réponses expliquées, dont certaines calculées depuis les jeux collectés. Il n’ajoute pas de faux fossiles ni d’observations inventées.')
small('L’API locale en lecture seule expose /health, /cities, /fossils, /climate, /analogues, /quality et /bootstrap sous /api/v1. La recherche SQL utilise des paramètres liés. Le dashboard autonome ou hébergé utilise un instantané du pipeline ; le serveur Python fournit l’API locale et la base SQLite. Aucune interrogation fournisseur n’est déclenchée par les filtres.')

section(12,'Reproduction, validation et soutenance')
code('python -m pip install -r requirements.txt\npython -m unittest discover -s tests -v\npython src/pipeline.py --offline --verify-replay\npython src/demo_rejection.py\npython src/analyse.py\npython src/serve.py --open')
para('Python 3.11+ suffit. Les données collectées sont livrées : la démonstration ne dépend pas d’Internet. Pour refaire la collecte, collect.py réutilise son cache et --refresh crée de nouveaux fichiers sans modifier les anciens. Les dépendances de génération du présent PDF sont facultatives et séparées du pipeline.')
table([['Preuve','Résultat / emplacement'],['Tests de qualité','9 tests unitaires réussis ; tests/test_quality.py'],['Rejeu complet','Empreintes et effectifs identiques ; reports/idempotence.json'],['API HTTP','11 vérifications, dont 400 et 404 ; reports/api_checks.json'],['SQL','15 analyses exécutées ; reports/sql_results.json'],['Démonstration invalide','Q08 + Q09 + Q10 ; reports/demo_rejection.json'],['Interface','Filtres, fiches, modèle, commune, graphique, quiz et export ; reports/validation.json']],[155,336])
h('Déroulé de cinq minutes')
para('Question et utilisateur → source et raw → exécution complète avec rejeu → ligne synthétique invalide → curated et rapport → carte et fiche → comparaison climatique → une limite et une amélioration. Le script détaillé et les réponses aux questions attendues figurent dans docs/demo_5_minutes.md.')
h('Correspondance avec le barème')
small('Problème/cas d’usage (3) : cadrage et KPI. Sources (3) : comparaison, licences, manifeste. Modèle/architecture (3) : grain, contrat, schéma. Collecte (3) : configuration, raw et reprise. Qualité (3) : règles, compteurs et rejets. Curated (2) : CSV/SQLite typés. Idempotence/rapport (2) : empreinte et bilan. Documentation/démo (1) : README et soutenance.')
para('Les limites centrales restent le biais documentaire, l’incertitude de localisation, les résolutions climatiques et le faible nombre de modèles. Elles sont exposées dans l’application : elles font partie du résultat académique, pas d’une note de bas de page oubliée.')

output=ROOT/'docs/Dossier_ChronoTerre_IDF.pdf'
doc=SimpleDocTemplate(str(output),pagesize=(595.28,841.89),rightMargin=52,leftMargin=52,topMargin=65,bottomMargin=58,title='ChronoTerre — Île-de-France | Dossier académique',author='Projet académique ESEO',subject='Architecture relationnelle, collecte, qualité et dashboard')
doc.build(story,onFirstPage=frame,onLaterPages=frame)
print(output)
