"""Serveur local lecture seule. Pas de journal des adresses ou des requêtes."""
import argparse,json,sqlite3,urllib.parse,urllib.request,webbrowser,re,math,time
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from pathlib import Path
from national.collect import ROOT
DB=ROOT/'data/curated/france.sqlite'
def query(db,s,p=()):return [dict(r) for r in db.execute(s,p)]
def bounded(q,k,default,low,high):
 try:v=float(q.get(k,[default])[0])
 except (ValueError,TypeError):raise ValueError(k+' doit être numérique')
 if not math.isfinite(v) or not low<=v<=high:raise ValueError(k+' hors limites')
 return v
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def json(self,status,data):
  b=json.dumps(data,ensure_ascii=False,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urllib.parse.urlsplit(self.path);q=urllib.parse.parse_qs(u.query)
  if not u.path.startswith('/api/v2/'):
   return super().do_GET()
  try:
   with sqlite3.connect(f'file:{DB}?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row;route=u.path[len('/api/v2/'):]
    if route=='health':return self.json(200,{'status':'ok','database':'SQLite','integrity':db.execute('PRAGMA quick_check').fetchone()[0]})
    if route=='meta':return self.json(200,json.loads((ROOT/'dist/data/meta.json').read_text()))
    if route=='search':
     s=q.get('q',[''])[0].strip()
     if not 2<=len(s)<=120:raise ValueError('q : 2 à 120 caractères')
     n=int(bounded(q,'limit',10,1,30));rows=query(db,"SELECT DISTINCT c.* FROM commune c LEFT JOIN postal_code p ON p.commune_code=c.code WHERE c.name LIKE ? OR p.postal_code=? OR c.code=? ORDER BY c.population DESC LIMIT ?",('%'+s+'%',s,s,n));return self.json(200,{'results':rows,'scope':'commune','provider':'DINUM / INSEE / IGN'})
    if route=='climate':
     code=q.get('code',[''])[0];h=q.get('horizon',['2050'])[0]
     if h not in ['ref','2030','2050','2100']:raise ValueError('Horizon non couvert ; 2076 n’est pas interpolé')
     places=query(db,'SELECT * FROM climate_place WHERE commune_code=?',(code,))
     if not places:return self.json(404,{'error':'no_data','message':'Aucune fiche climatique pour ce code'})
     return self.json(200,{'place':places[0],'period':h,'provenance':query(db,'SELECT r.url,r.sha256,r.retrieved_at,s.producer,s.license FROM raw_file r JOIN dataset_version d USING(version_id) JOIN source s USING(source_id) WHERE r.raw_id=?',(places[0]['raw_id'],))[0],'values':query(db,'SELECT v.*,i.label,i.unit,i.definition,i.source_url FROM climate_value v JOIN indicator i USING(indicator_id) WHERE commune_code=? AND period_id=?',(code,h))})
    if route=='fossils':
     b=q.get('bbox',[''])[0].split(',')
     if len(b)!=4:raise ValueError('bbox obligatoire : ouest,sud,est,nord')
     try:w,s,e,n=map(float,b)
     except ValueError:raise ValueError('bbox numérique obligatoire')
     if not all(math.isfinite(x) for x in [w,s,e,n]) or not(-180<=w<e<=180 and -90<=s<n<=90) or e-w>40 or n-s>30:raise ValueError('Emprise invalide ou trop grande (40° × 30° maximum)')
     limit=int(bounded(q,'limit',100,1,500));cursor=int(bounded(q,'after',0,0,1e12));params=[w,e,s,n,cursor];conditions=['o.occurrence_id>?']
     if q.get('class'):conditions.append('o.class_name=?');params.append(q['class'][0])
     if q.get('taxon'):conditions.append('o.accepted_name LIKE ?');params.append('%'+q['taxon'][0][:120]+'%')
     sql='SELECT o.* FROM fossil_index ix JOIN v_fossils o ON o.site_id=ix.site_id WHERE ix.max_lon>=? AND ix.min_lon<=? AND ix.max_lat>=? AND ix.min_lat<=? AND '+' AND '.join(conditions)+' ORDER BY o.occurrence_id LIMIT ?'
     rows=query(db,sql,params+[limit+1]);more=len(rows)>limit;rows=rows[:limit];return self.json(200,{'results':rows,'next_after':rows[-1]['occurrence_id'] if more else None,'limit':limit,'bbox':[w,s,e,n]})
    if route.startswith('sites/'):
     id=route.split('/')[-1]
     if not id.isdigit():raise ValueError('Identifiant numérique')
     sites=query(db,'SELECT * FROM fossil_site WHERE site_id=?',(id,))
     if not sites:return self.json(404,{'error':'not_found'})
     return self.json(200,{'site':sites[0],'occurrences':query(db,'SELECT * FROM v_fossils WHERE site_id=?',(id,))})
    if route=='hazards/point':
     x=bounded(q,'lon',None,-180,180);y=bounded(q,'lat',None,-90,90)
     try:from shapely.geometry import shape,Point
     except ImportError:return self.json(503,{'error':'dependency_missing','message':'Installer requirements-france.txt pour les intersections'})
     rows=[]
     for r in query(db,'SELECT * FROM hazard_zone'):
      if shape(json.loads(r.pop('geometry'))).intersects(Point(x,y)):rows.append(r)
     return self.json(200,{'point':[x,y],'intersections':rows,'scope':'Couches locales livrées seulement','warning':'Aucune intersection ne signifie pas absence de risque'})
    if route=='urban':
     x=bounded(q,'lon',None,-180,180);y=bounded(q,'lat',None,-90,90);layer=q.get('layer',['parcelle'])[0]
     if layer not in ['parcelle','document','zone-urba','prescription-surf','assiette-sup-s']:raise ValueError('Couche non autorisée')
     # Liste fixe d’URL : pas de proxy arbitraire / SSRF ; ni jeton ni saisie privée stockés.
     url='https://apicarto.ign.fr/api/'+('cadastre' if layer=='parcelle' else 'gpu')+'/'+layer+'?'+urllib.parse.urlencode({'geom':json.dumps({'type':'Point','coordinates':[x,y]})})
     try:
      with urllib.request.urlopen(url,timeout=15) as r:d=json.load(r)
     except Exception:return self.json(503,{'error':'provider_unavailable','message':'API Carto indisponible ; les autres données restent accessibles'})
     return self.json(200,{'data':d,'source':url,'scope':'point','retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    return self.json(404,{'error':'not_found','message':'Route inconnue'})
  except ValueError as e:return self.json(400,{'error':'invalid_parameter','message':str(e)})
  except Exception as e:return self.json(500,{'error':'internal_error','message':'Erreur de traitement ; vérifier la base et le rapport, sans utiliser de valeurs de remplacement'})
def main():
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8000);p.add_argument('--open',action='store_true');a=p.parse_args()
 if not DB.exists():raise SystemExit('Base manquante : python -m national.pipeline')
 server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(ROOT/'dist')))
 print(f'ChronoTerre : http://127.0.0.1:{a.port}',flush=True)
 if a.open:webbrowser.open(f'http://127.0.0.1:{a.port}')
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
