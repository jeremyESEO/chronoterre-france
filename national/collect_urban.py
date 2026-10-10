"""Échantillon public contrasté ; aucun domicile personnel journalisé."""
import json,urllib.parse
from national.collect import Collector,ROOT,dump
SAMPLES=[
('paris','Paris - Hôtel de Ville','75056',2.3518,48.8566,'urbain dense'),
('larochelle','La Rochelle - mairie','17300',-1.152,46.16,'littoral atlantique'),
('arles','Arles - centre','13004',4.627,43.677,'vallée inondable / Méditerranée'),
('tours','Tours - Loire','37261',0.691,47.398,'vallée inondable'),
('chamonix','Chamonix - centre','74056',6.869,45.9237,'montagne'),
('gueret','Guéret - centre','23096',1.871,46.17,'commune rurale / centralité'),
('ajaccio','Ajaccio - mairie','2A004',8.7384,41.9192,'Corse'),
('reunion','Saint-Denis de La Réunion - mairie','97411',55.448, -20.879,'outre-mer'),
('rennes','Rennes - exemple IGN','35238',-1.691634,48.104237,'urbanisme'),
]
def main():
 c=Collector();c.path=ROOT/'data/raw/urban_manifest.json';c.manifest=json.loads(c.path.read_text()) if c.path.exists() else {'version':2,'files':{},'attempts':[]};out=[]
 for id,label,code,x,y,kind in SAMPLES:
  p={'id':id,'label':label,'code':code,'lon':x,'lat':y,'kind':kind,'resources':{}};geom={'type':'Point','coordinates':[x,y]}
  for layer in ['parcelle','document','zone-urba','prescription-surf','assiette-sup-s']:
   source='cadastre' if layer=='parcelle' else 'gpu';url='https://apicarto.ign.fr/api/'+source+'/'+layer+'?'+urllib.parse.urlencode({'geom':json.dumps(geom,separators=(',',':'))})
   key='urban_'+id+'_'+layer
   try:
    data=c.fetch(key,source,url,timeout=35);p['resources'][layer]={'raw':key,'status':'ok','count':len(data.get('features',[]))}
    if layer=='parcelle' and data.get('features'):geom=data['features'][0]['geometry']
   except Exception as e:p['resources'][layer]={'status':'error','message':str(e)}
  out.append(p);dump(ROOT/'config/test_places.json',out)
 c.close()
if __name__=='__main__':main()
