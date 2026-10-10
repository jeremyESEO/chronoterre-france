"""Reconstruit SQLite et les fichiers Web à partir des seuls raw. Pas de collecte implicite."""
import argparse,csv,gzip,hashlib,json,os,sqlite3,time
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from shapely.geometry import Point,shape
from shapely.strtree import STRtree
from national.collect import ROOT,dump,now
from national.metadata import SOURCES,INDICATORS,HAZARDS
from national.validate import *
def packed(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf-8')
def query(db,s,p=()):return [dict(x) for x in db.execute(s,p)]
def openraw(e):return gzip.open(ROOT/e['path'],'rb') if e['path'].endswith('.gz') else (ROOT/e['path']).open('rb')
def fingerprint(db):
 h=hashlib.sha256();counts={}
 for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'fossil_index%' ORDER BY name"):
  h.update(name.encode());n=0;cols=[x[1] for x in db.execute('PRAGMA table_info('+name+')')]
  for row in db.execute('SELECT * FROM '+name+' ORDER BY '+','.join('"'+c+'"' for c in cols)):
   h.update(json.dumps(list(row),ensure_ascii=False,separators=(',',':')).encode());h.update(b'\n');n+=1
  counts[name]=n
 return h.hexdigest(),counts
def main():
 from national.materialize import materialize
 materialize()
 parser=argparse.ArgumentParser();parser.add_argument('--verify-replay',action='store_true');args=parser.parse_args();start=time.monotonic();cfg=json.loads((ROOT/'config/france.json').read_text());files={}
 for name in ['national_manifest.json','climate_manifest.json','urban_manifest.json','hazard_manifest.json']:
  p=ROOT/'data/raw'/name
  if p.exists():files.update(json.loads(p.read_text())['files'])
 if 'climadiag' not in files:raise RuntimeError('Collecte climatique absente ; lancer python -m national.collect_climate')
 for key,e in files.items():
  h=hashlib.sha256()
  with openraw(e) as f:
   for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
  if h.hexdigest()!=e['sha256']:raise ValueError('P01 '+key)
 path=ROOT/'data/curated/france.sqlite';tmp=path.with_suffix('.tmp');tmp.unlink(missing_ok=True);db=sqlite3.connect(tmp);db.row_factory=sqlite3.Row;db.executescript((ROOT/'sql/france_schema.sql').read_text());db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
 db.executemany('INSERT INTO source VALUES(?,?,?,?,?)',SOURCES)
 for key,e in files.items():
  if not db.execute('SELECT 1 FROM source WHERE source_id=?',(e['source'],)).fetchone():db.execute('INSERT INTO source VALUES(?,?,?,?,?)',(e['source'],e.get('producer',e['source']),e['url'],e.get('license','Licence Ouverte 2.0'),e.get('limits','Voir manifeste')))
  db.execute('INSERT INTO dataset_version VALUES(?,?,?,?,?)',(key,e['source'],key,e['fetched_at'],e.get('coverage','Voir source et registre de couverture')))
  db.execute('INSERT INTO raw_file VALUES(?,?,?,?,?,?,?)',(key,key,e['path'],e['url'],e['sha256'],e['bytes'],e['fetched_at']))
 def read(k):
  with openraw(files[k]) as f:return json.load(f)
 deps=read('departments')['features'];geoms=[shape(d['geometry']) for d in deps];tree=STRtree(geoms)
 for d in deps:
  p=d['properties'];db.execute('INSERT INTO department VALUES(?,?,?,?,?)',(p['code'],p['nom'],p.get('region'),json.dumps(d['geometry']),'EPSG:4326'))
 names={norm(d['properties']['nom']):d['properties']['code'] for d in deps};dep_codes={d['properties']['code'] for d in deps}
 communes=read('communes');cities={};city_profile=Profiler()
 for c in communes:
  city_profile.add(c,c['code']);xy=c.get('centre',{}).get('coordinates',[None,None]);code=c['code'];dep=c.get('codeDepartement');dep=dep if dep in dep_codes else None
  db.execute('INSERT INTO commune VALUES(?,?,?,?,?,?,?,?)',(code,c['nom'],dep,c.get('codeRegion'),*xy,c.get('population'),'communes'));cities[code]=c
  for pc in set(c.get('codesPostaux',[])):db.execute('INSERT INTO postal_code VALUES(?,?)',(code,pc))
 db.executemany('INSERT INTO indicator VALUES(?,?,?,?,?,?)',INDICATORS)
 db.executemany('INSERT INTO scenario VALUES(?,?,?,?)',[('TRACC','TRACC','warming_level','Trajectoire d’adaptation ; pas un scénario d’émissions choisi par l’utilisateur'),('reference','Référence','historical','Référence homogène du producteur')])
 db.executemany('INSERT INTO climate_model VALUES(?,?,?,?)',[('TRACC-MET','Ensemble TRACC / Explore2','ensemble','17 couples GCM/RCM, régionalisation ~8 km ; médiane et bornes publiées par Climadiag'),('CLIMADIAG-OM','Ensemble Climadiag outre-mer','ensemble','Méthode et résolution spécifiques au domaine ; aucune assimilation au jeu métropolitain')])
 db.executemany('INSERT INTO period VALUES(?,?,?,?,?)',[('ref','Référence fournie par territoire',None,None,'reference'),('2030','Niveau TRACC associé à 2030',None,None,'warming_level'),('2050','Niveau TRACC associé à 2050',None,None,'warming_level'),('2100','Niveau TRACC associé à 2100',None,None,'warming_level')])
 units={r[0]:r[2] for r in INDICATORS};fails=Counter();rejects=[];climate_profile=Profiler();entity_profile=Profiler();skipped=Counter();nclimate=0
 with openraw(files['climadiag']) as f:
  for line in f:
   c=json.loads(line);code=str(c['identifiant_insee']);entity_profile.add({k:v for k,v in c.items() if k!='indicateurs'},code)
   if code not in cities or c.get('type','').lower()!='commune':skipped['EPCI_ou_code_absent_du_COG']+=1;continue
   domain=c.get('domaine') or 'France hexagonale';over=domain!='France hexagonale';years=(1991,2020) if over else (1976,2005);indicators=c.get('indicateurs',[])
   db.execute('INSERT INTO climate_place VALUES(?,?,?,?,?,?,?,?)',(code,domain,*years,'Spécifique au domaine, voir source' if over else 'Maille source 8 km ; point représentatif choisi par Météo-France','Valeurs agrégées publiées ; fenêtres par niveau de réchauffement, bornes annuelles par modèle non livrées',next((i.get('alti_text') for i in indicators if i.get('alti_text')),None),'climadiag'))
   for risk in c.get('risques',[]):
    db.execute('INSERT OR IGNORE INTO hazard VALUES(?,?,?)',(risk,HAZARDS.get(risk,risk),'inventaire_communal'))
    db.execute('INSERT OR IGNORE INTO commune_hazard VALUES(?,?,?,?)',(code,risk,'climadiag','Risque recensé à la commune dans Climadiag, d’après Géorisques ; périmètre infra-communal non déduit'))
   seen=set()
   for ind in indicators:
    iid=ind['id']
    if iid not in units:continue
    # R3 a une autre référence et une convention de projection : conservé séparément, jamais soustrait à une température.
    for h,rows in zip(['2030','2050','2100'],ind.get('data',[])):
     for r in rows:
      season=r.get('label') or 'annuel';climate_profile.add({'indicator':iid,'period':h,'season':season,**r},(code,iid,h,season))
      for period,v,lo,hi in [('ref',r.get('ref'),None,None),(h,r.get('mean'),r.get('min'),r.get('max'))]:
       key=(code,iid,period,season)
       if key in seen:continue
       # Le JSON Climadiag livre NIVMER en mètres ; son interface multiplie par 100.
       if iid=='R3':v,lo,hi=[None if x is None else round(x*100,8) for x in [v,lo,hi]]
       seen.add(key);errors=climate_errors(v,lo,hi,units[iid])
       if errors:
        fails.update(errors);rejects.append({'domain':'climate','key':'|'.join(key),'reasons':errors,'row':r});continue
       db.execute('INSERT INTO climate_value VALUES(?,?,?,?,?,?,?,?,?,?)',(*key,v,lo,hi,'reference' if period=='ref' else 'TRACC','CLIMADIAG-OM' if over else 'TRACC-MET','climadiag'));nclimate+=1
 print('Valeurs climatiques',nclimate,flush=True)
 collections={};collection_raw={}
 for k in files:
  if k.startswith('pbdb_colls_'):
   for r in read(k)['records']:collections[str(r['collection_no'])]=r;collection_raw[str(r['collection_no'])]=k
 locations={}
 for id,c in collections.items():
  dep=None
  try:
   x,y=float(c['lng']),float(c['lat']);point=Point(x,y)
   for j in tree.query(point):
    if geoms[j].covers(point):dep=deps[j]['properties']['code'];break
  except (KeyError,ValueError,TypeError):pass
  # Ne corrige pas les coordonnées à partir des noms ; conserve un rejet traçable.
  if dep and any(norm(c.get(k,'')) in names and names[norm(c[k])]!=dep for k in ['county']):dep=None
  locations[id]=dep
 profile=Profiler();seen=set();nocc=0
 for k in files:
  if not k.startswith('pbdb_occs_'):continue
  for r in read(k)['records']:
   oid=r.get('occurrence_no');profile.add(r,oid);sid=str(r.get('collection_no'));c=collections.get(sid);dep=locations.get(sid);errors=fossil_errors(r,c,dep,cfg['excluded_pbdb_collections'])
   if oid in seen:errors.append('U01')
   seen.add(oid)
   if errors:
    fails.update(errors);rejects.append({'domain':'fossil','key':oid,'reasons':errors,'row':r});continue
   tid=str(r.get('accepted_no') or 'name:'+r['identified_name']);ref=str(r['reference_no']);interval=[r['early_interval'],r.get('late_interval'),float(r['max_ma']),float(r['min_ma'])];iid=hashlib.sha256(json.dumps(interval).encode()).hexdigest()[:20]
   db.execute('INSERT OR IGNORE INTO taxon VALUES(?,?,?,?,?,?)',(tid,r.get('accepted_name') or r['identified_name'],r.get('accepted_rank'),r.get('phylum'),r.get('class'),r.get('family')))
   db.execute('INSERT OR IGNORE INTO bibliography VALUES(?,?,?)',(ref,r['primary_reference'],'https://paleobiodb.org/classic/displayReference?reference_no='+ref))
   db.execute('INSERT OR IGNORE INTO geological_interval VALUES(?,?,?,?,?)',(iid,*interval))
   db.execute('INSERT OR IGNORE INTO fossil_site VALUES(?,?,?,?,?,?,?,?,?,?,?)',(int(sid),c['collection_name'],float(c['lng']),float(c['lat']),dep,c.get('environment'),c.get('latlng_basis'),c.get('latlng_precision'),c.get('geogcomments'),c.get('formation') or c.get('stratgroup'),collection_raw[sid]))
   db.execute('INSERT OR IGNORE INTO fossil_index VALUES(?,?,?,?,?)',(int(sid),float(c['lng']),float(c['lng']),float(c['lat']),float(c['lat'])))
   db.execute('INSERT INTO fossil_occurrence VALUES(?,?,?,?,?,?,?)',(int(oid),int(sid),tid,ref,iid,r['identified_name'],k));nocc+=1
 print('Fossiles acceptés',nocc,flush=True)
 # Urbanisme, géométries et médias ne sont importés que s’ils ont réellement été collectés.
 from national.enrich import enrich
 enrich(db,files,read,rejects,fails)
 db.commit();fk=list(db.execute('PRAGMA foreign_key_check'));integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
 if fk or integrity!='ok':raise RuntimeError('Intégrité SQLite: '+str(fk))
 digest,counts=fingerprint(db);report={'executed_at':now(),'duration_seconds':round(time.monotonic()-start,2),'status':'PASS_WITH_LIMITS','counts':counts,'fossil_input':profile.n,'fossil_accepted':nocc,'rejected':len(rejects),'failures':dict(fails),'climate_outside_scope':dict(skipped),'rules':[{ 'id':k,'name':v[0],'condition':v[1],'action':v[2],'failures':fails[k]} for k,v in RULES.items()],'semantic_sha256':digest,'foreign_keys':'ok','integrity':integrity,'raw_verified':len(files)}
 dump(ROOT/'reports/france_profile_before.json',{'communes':city_profile.result(),'fossils':profile.result(),'climate_entities':entity_profile.result(),'climate_values':climate_profile.result()})
 with (ROOT/'data/rejected/france_rejects.jsonl').open('w') as f:
  for r in rejects:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 dump(ROOT/'reports/france_run.json',report)
 from national.export import export
 export(db,report,files)
 db.close();tmp.replace(path)
 if args.verify_replay:
  # Deuxième vraie reconstruction depuis les mêmes raw, puis comparaison de contenu typé.
  import subprocess
  subprocess.run([os.sys.executable,'-m','national.pipeline'],cwd=ROOT,check=True)
  second=json.loads((ROOT/'reports/france_run.json').read_text());ok=digest==second['semantic_sha256'] and counts==second['counts'];dump(ROOT/'reports/france_idempotence.json',{'first':digest,'second':second['semantic_sha256'],'equal':ok,'counts_equal':counts==second['counts'],'method':'Deux reconstructions complètes ; SHA-256 des lignes triées de toutes les tables applicatives, provenance incluse'})
  if not ok:raise ValueError('Rejeu différent')
 print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
