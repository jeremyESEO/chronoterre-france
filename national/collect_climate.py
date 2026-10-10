"""Archive JSONL public utilisé par Climadiag, téléchargement en flux."""
import argparse,hashlib,json,urllib.request,gzip
from datetime import datetime,timezone
from national.collect import ROOT,now,dump
URL='https://climadiag-commune.meteofrance.com/entities.jsonl'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
 manifest=ROOT/'data/raw/climate_manifest.json'
 if manifest.exists() and not args.refresh:
  m=json.loads(manifest.read_text());e=m['files']['climadiag']
  h=hashlib.sha256()
  with (gzip.open(ROOT/e['path'],'rb') if e['path'].endswith('.gz') else (ROOT/e['path']).open('rb')) as f:
   for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
  if h.hexdigest()!=e['sha256']:raise ValueError('Raw corrompu')
  print('Cache climatique vérifié');return
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');p=ROOT/'data/raw'/f'{stamp}_climadiag.jsonl';h=hashlib.sha256();n=0
 req=urllib.request.Request(URL,headers={'User-Agent':'ChronoTerre-ESEO/2.0'})
 with urllib.request.urlopen(req,timeout=240) as r,p.open('xb') as f:
  if r.status!=200:raise ValueError('Export incomplet '+str(r.status))
  for chunk in iter(lambda:r.read(1048576),b''):
   f.write(chunk);h.update(chunk);n+=len(chunk)
   if n%(64*1048576)==0:print(n,'octets',flush=True)
  headers={k:r.headers[k] for k in ['ETag','Last-Modified','Content-Length'] if k in r.headers}
  if headers.get('Content-Length') and n!=int(headers['Content-Length']):raise ValueError('Taille incomplète')
 e={'source':'climadiag','url':URL,'path':str(p.relative_to(ROOT)),'sha256':h.hexdigest(),'bytes':n,'fetched_at':now(),'status':200,'response_headers':headers}
 dump(manifest,{'version':2,'files':{'climadiag':e}});dump(ROOT/'data/raw'/f'climate_manifest_{stamp}.json',{'version':2,'files':{'climadiag':e}});print('Climadiag téléchargé',n,flush=True)
if __name__=='__main__':main()
