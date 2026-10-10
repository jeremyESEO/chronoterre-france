import json,sqlite3,csv
from collections import defaultdict
from pathlib import Path
from national.collect import ROOT,dump

def packed(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf-8')
def q(db,s,p=()):return [dict(x) for x in db.execute(s,p)]
def export(db,report,files):
 cfg=json.loads((ROOT/'config/france.json').read_text());out=ROOT/'dist/data';out.mkdir(exist_ok=True)
 cities=q(db,"SELECT c.*,group_concat(p.postal_code,' ') postal_codes,cp.domain FROM commune c LEFT JOIN postal_code p ON p.commune_code=c.code LEFT JOIN climate_place cp ON cp.commune_code=c.code GROUP BY c.code")
 packed(out/'communes.json',cities)
 # Compact columns documented in the API contract; every field is exported from SQLite.
 ccols=['indicator_id','period_id','season','value','lower','upper']
 depclimate=defaultdict(dict)
 for place in q(db,'SELECT cp.*,c.department FROM climate_place cp JOIN commune c ON c.code=cp.commune_code'):
  code=place['commune_code'];rows=[list(x) for x in db.execute('SELECT '+','.join(ccols)+' FROM climate_value WHERE commune_code=? ORDER BY indicator_id,period_id,season',(code,))]
  hazards=q(db,'SELECT h.hazard_id,h.label,ch.nature FROM commune_hazard ch JOIN hazard h USING(hazard_id) WHERE ch.commune_code=?',(code,))
  depclimate[place['department'] or code[:3]][code]={'place':place,'values':rows,'hazards':hazards}
 for dep,data in depclimate.items():packed(out/'climate'/(dep+'.json'),data)
 sites=q(db,'SELECT s.*,COUNT(o.occurrence_id) occurrences FROM fossil_site s JOIN fossil_occurrence o USING(site_id) GROUP BY s.site_id')
 packed(out/'sites.json',sites)
 fs=defaultdict(list)
 fcols=['occurrence_id','site_id','taxon_id','accepted_name','identified_name','class_name','phylum','early_name','min_ma','max_ma','reference_id','department']
 for row in db.execute('SELECT '+','.join(fcols)+' FROM v_fossils ORDER BY occurrence_id'):fs[row[-1]].append(list(row))
 for dep,rows in fs.items():packed(out/'fossils'/(dep+'.json'),rows)
 packed(out/'references.json',q(db,'SELECT * FROM bibliography'))
 packed(out/'media.json',{'media':q(db,'SELECT * FROM media'),'links':q(db,'SELECT * FROM taxon_media')})
 deps=q(db,'SELECT * FROM department');packed(out/'departments.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{k:v for k,v in d.items() if k!='geometry'},'geometry':json.loads(d['geometry'])} for d in deps]})
 hazard=q(db,'SELECT z.*,r.url source_url,r.retrieved_at FROM hazard_zone z JOIN raw_file r USING(raw_id)')
 packed(out/'hazards.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{k:v for k,v in z.items() if k!='geometry'},'geometry':json.loads(z['geometry'])} for z in hazard]})
 # Raw responses for the explicit public test points retain all provider attributes.
 samples=[];p=ROOT/'config/test_places.json'
 if p.exists():
  for s in json.loads(p.read_text()):
   item={**s,'data':{}}
   for layer,r in s['resources'].items():
    if r.get('raw') in files:item['data'][layer]=json.loads((ROOT/files[r['raw']]['path']).read_text())
   samples.append(item)
 packed(out/'test-places.json',samples)
 coverage={'metropole':'Climat Climadiag et fossiles PBDB selon les enregistrements collectés ; recherche de toutes les communes.','overseas':'Commune recherchable si fournie par l’API Découpage ; climat uniquement si une fiche spécifique est jointe par code. Fossiles limités au pays FR de PBDB, pas de généralisation aux territoires ayant un autre code.','risks':'Inventaire communal Climadiag ; géométries uniquement dans les zones documentées du registre. Aucun diagnostic national à la parcelle.','urban':'Consultation publique API Carto au clic ; cache de l’échantillon livré. Hors ligne : uniquement les points de test.'}
 metadata={'title':'ChronoTerre — France','version':cfg['version'],'reference_date':cfg['reference_date'],'plus50_year':int(cfg['reference_date'][:4])+cfg['target_plus_years'],'snapshot_at':max(e['fetched_at'] for e in files.values()),'built_at':report['executed_at'],'mode':'snapshot national + API SQLite locale facultative','counts':report['counts'],'sources':q(db,'SELECT * FROM source'),'indicators':q(db,'SELECT * FROM indicator'),'climate_columns':ccols,'fossil_columns':fcols,'fossil_departments':list(fs),'climate_departments':list(depclimate),'classes':[r[0] for r in db.execute('SELECT DISTINCT class_name FROM taxon WHERE class_name IS NOT NULL ORDER BY class_name')],'periods':[r[0] for r in db.execute('SELECT DISTINCT early_name FROM geological_interval ORDER BY early_name')],'coverage':coverage,'raw':{k:{x:e.get(x) for x in ['source','url','sha256','fetched_at','bytes','response_headers']} for k,e in files.items()}}
 packed(out/'meta.json',metadata);packed(out/'quality.json',report)
 # CSV de démonstration strictement réel, stable et reproductible.
 with (ROOT/'data/curated/france_demo_fossils.csv').open('w',newline='',encoding='utf-8') as f:
  rows=q(db,'SELECT * FROM v_fossils ORDER BY occurrence_id LIMIT 500');w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else fcols);w.writeheader();w.writerows(rows)
 from national.home_export import run as export_home
 export_home()
 print('Instantané Web exporté depuis SQLite',flush=True)
