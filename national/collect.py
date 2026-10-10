"""Collecte autorisée, cache vérifié, reprises et octets bruts immuables."""
import argparse, hashlib, json, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def now(): return datetime.now(timezone.utc).isoformat()
def dump(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8');q.replace(p)
class Collector:
 def __init__(self,refresh=False):
  self.refresh=refresh;self.path=ROOT/'data/raw/national_manifest.json'
  self.manifest=json.loads(self.path.read_text()) if self.path.exists() else {'version':2,'files':{},'attempts':[]}
 def fetch(self,key,source,url,headers=None,parse=True,timeout=90):
  old=self.manifest['files'].get(key)
  if old and not self.refresh and old['url']==url:
   b=(ROOT/old['path']).read_bytes()
   if hashlib.sha256(b).hexdigest()!=old['sha256']:raise ValueError('Raw corrompu: '+key)
   return json.loads(b) if parse else b
  for attempt in range(3):
   stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
   try:
    req=urllib.request.Request(url,headers={'User-Agent':'ChronoTerre-ESEO/2.0 (academic open data)','Accept':'application/json',**(headers or {})})
    with urllib.request.urlopen(req,timeout=timeout) as r:
     b=r.read();status=r.status;ct=r.headers.get('Content-Type','');rh={k:r.headers[k] for k in ['ETag','Last-Modified','Content-Range'] if k in r.headers}
    path=ROOT/'data/raw'/f'{stamp}_{key}.raw'
    with path.open('xb') as f:f.write(b)
    entry={'source':source,'url':url,'request_headers':headers or {},'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'fetched_at':now(),'content_type':ct,'status':status,'response_headers':rh}
    obj=json.loads(b) if parse else b
    if parse and isinstance(obj,dict) and (obj.get('errors') or obj.get('error')):raise ValueError(str(obj)[:200])
    self.manifest['files'][key]=entry;self.manifest['attempts'].append({'key':key,'at':now(),'status':status,'attempt':attempt+1});dump(self.path,self.manifest)
    print(f'{key}: {len(b):,} octets',flush=True);return obj
   except (urllib.error.URLError,TimeoutError,ValueError) as e:
    self.manifest['attempts'].append({'key':key,'at':now(),'status':'error','detail':str(e)[:200],'attempt':attempt+1});dump(self.path,self.manifest)
    if attempt==2:raise RuntimeError(f'{key}: accès fournisseur indisponible; cache antérieur conservé: {e}') from e
    time.sleep(2**attempt if getattr(e,'code',0)!=429 else 15)
 def close(self):
  dump(ROOT/'data/raw'/('national_manifest_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'),self.manifest)
def main():
 a=argparse.ArgumentParser();a.add_argument('--refresh',action='store_true');a.add_argument('--source',default='core',choices=['core','pbdb','geography']);args=a.parse_args();c=Collector(args.refresh)
 if args.source in ['core','geography']:
  c.fetch('communes','geoapi','https://geo.api.gouv.fr/communes?fields=nom,code,codeDepartement,codeRegion,codesPostaux,centre,population&format=json',timeout=180)
  c.fetch('departments','etalab','https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-100m.geojson')
 if args.source in ['core','pbdb']:
  for kind,show in [('colls','loc,env,ref,rem,strat'),('occs','coords,loc,env,ref,classext')]:
   offset=0;total=0
   while True:
    params={'cc':'FR','vocab':'pbdb','show':show,'limit':10000,'offset':offset}
    d=c.fetch(f'pbdb_{kind}_{offset}','pbdb','https://paleobiodb.org/data1.2/'+kind+'/list.json?'+urllib.parse.urlencode(params),timeout=180)
    rows=d.get('records',[]);total+=len(rows)
    if d.get('warnings'):raise ValueError('PBDB warning '+str(d['warnings']))
    if len(rows)<10000:break
    offset+=10000;time.sleep(1)
   print(kind,'total',total,flush=True)
 c.close()
if __name__=='__main__':main()
