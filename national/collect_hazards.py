"""Exports locaux officiels ; couverture strictement bornée, pas de faux national."""
import json
from national.collect import Collector,ROOT,dump
SOURCES=[
{'id':'toulouse-flood','raw':'flood_toulouse','source':'dreal_occitanie','producer':'DREAL Occitanie','label':'Surfaces inondables du TRI de Toulouse','hazard':'river_flood','nature':'enveloppe_aléa','url':'https://catalogue.picto-occitanie.fr/api/data/7c91530f-6a26-41e5-9dee-19adec8af824?srs=EPSG:4326','scenario_field':'scenario','label_field':'id_s_inond','coverage':'TRI Toulouse uniquement ; entrée 2013-07-18 ; ne pas confondre avec un PPRI','curated':'data/curated/flood_toulouse.geojson'},
{'id':'bordeaux-rga','raw':'rga_bordeaux','source':'bordeaux_metropole','producer':'Bordeaux Métropole / BRGM','label':'Retrait-gonflement des argiles, Bordeaux Métropole','hazard':'rga','nature':'exposition_cartographiée','url':'https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_alearga_s/exports/geojson','label_field':'alea','coverage':'Bordeaux Métropole uniquement ; métadonnées du portail conservées, ne pas assimiler au zonage national révisé sans vérification','curated':'data/curated/rga_bordeaux.geojson'}]
def main():
 c=Collector();c.path=ROOT/'data/raw/hazard_manifest.json';c.manifest=json.loads(c.path.read_text()) if c.path.exists() else {'version':2,'files':{},'attempts':[]}
 for s in SOURCES:
  d=c.fetch(s['raw'],s['source'],s['url']);c.manifest['files'][s['raw']].update({k:s[k] for k in ['coverage','producer']});c.manifest['files'][s['raw']]['license']='Licence Ouverte 2.0';dump(c.path,c.manifest);dump(ROOT/s['curated'],d)
 c.fetch('rga_metadata','bordeaux_metropole','https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_alearga_s')
 dump(ROOT/'config/hazard_layers.json',SOURCES);c.close()
if __name__=='__main__':main()
