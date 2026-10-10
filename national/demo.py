"""Socle TP rapide : une page PBDB réelle, mêmes règles, copie invalide isolée."""
import hashlib,json,sqlite3,time
from collections import Counter
from shapely.geometry import shape,Point
from shapely.strtree import STRtree
from national.collect import ROOT,dump,now
from national.validate import fossil_errors,norm

def run():
 start=time.monotonic();files=json.loads((ROOT/'data/raw/national_manifest.json').read_text())['files']
 def read(k):
  b=(ROOT/files[k]['path']).read_bytes()
  if hashlib.sha256(b).hexdigest()!=files[k]['sha256']:raise ValueError('Raw altéré')
  return json.loads(b)
 deps=read('departments')['features'];geoms=[shape(f['geometry']) for f in deps];tree=STRtree(geoms);names={norm(f['properties']['nom']):f['properties']['code'] for f in deps}
 sites={str(c['collection_no']):c for c in read('pbdb_colls_0')['records']};locations={}
 for id,c in sites.items():
  dep=None
  try:
   p=Point(float(c['lng']),float(c['lat']))
   for i in tree.query(p):
    if geoms[i].covers(p):dep=deps[i]['properties']['code'];break
  except (KeyError,ValueError,TypeError):pass
  if dep and norm(c.get('county','')) in names and names[norm(c['county'])]!=dep:dep=None
  locations[id]=dep
 exclusions=json.loads((ROOT/'config/france.json').read_text())['excluded_pbdb_collections'];rows=read('pbdb_occs_0')['records'];accepted=[];rejected=[];seen=set();fails=Counter()
 # Une donnée volontairement invalide n'existe que dans cette exécution pédagogique.
 simulated={'occurrence_no':-1,'collection_no':-1,'identified_name':'TEST_INVALIDE_ISOLE','min_ma':100,'max_ma':1}
 for r in [*rows,simulated]:
  id=r.get('occurrence_no');sid=str(r.get('collection_no'));errors=fossil_errors(r,sites.get(sid),locations.get(sid),exclusions)
  if id in seen:errors.append('U01')
  seen.add(id)
  if errors:rejected.append({'id':id,'rules':errors,'test_only':id==-1});fails.update(errors)
  else:accepted.append((int(id),int(sid),r.get('accepted_name') or r['identified_name'],float(r['min_ma']),float(r['max_ma']),r['primary_reference']))
 path=ROOT/'data/curated/demo_tp.sqlite';db=sqlite3.connect(path);db.executescript('DROP TABLE IF EXISTS occurrence; DROP TABLE IF EXISTS locality; CREATE TABLE locality(id INTEGER PRIMARY KEY,name TEXT,longitude REAL,latitude REAL); CREATE TABLE occurrence(id INTEGER PRIMARY KEY,site_id INTEGER REFERENCES locality,taxon TEXT,min_ma REAL,max_ma REAL,citation TEXT,CHECK(min_ma>=0 AND max_ma>=min_ma)); PRAGMA foreign_keys=ON;')
 for sid in sorted({r[1] for r in accepted}):
  c=sites[str(sid)];db.execute('INSERT INTO locality VALUES(?,?,?,?)',(sid,c['collection_name'],float(c['lng']),float(c['lat'])))
 db.executemany('INSERT INTO occurrence VALUES(?,?,?,?,?,?)',accepted);db.commit();digest=hashlib.sha256(json.dumps(sorted(accepted),ensure_ascii=False).encode()).hexdigest();db.close()
 dump(ROOT/'data/rejected/demo_tp.json',rejected)
 return {'at':now(),'real_input':len(rows),'test_only_input':1,'accepted_real':len(accepted),'rejected_real':len(rejected)-1,'failures':dict(fails),'sha256':digest,'seconds':round(time.monotonic()-start,2),'raw':files['pbdb_occs_0']}
def main():
 a=run();b=run();report={'first':a,'second':b,'same_keys_and_values':a['sha256']==b['sha256'],'production_modified':False};dump(ROOT/'reports/demo_tp.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
 if not report['same_keys_and_values']:raise RuntimeError('Rejeu différent')
if __name__=='__main__':main()
