"""Manual, bounded ERA5-Land collection. Real raw responses, cache, typed SQLite, full-year checks."""
import sys,json,urllib.request,urllib.parse,hashlib,sqlite3,time,calendar,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/raw/recent';OUT.mkdir(exist_ok=True)
def run():
 cities={c['code']:c for c in json.loads((ROOT/'dist/data/communes.json').read_text())};codes=[p['code'] for p in json.loads((ROOT/'config/test_places.json').read_text())]+['31555']
 db=sqlite3.connect(ROOT/'data/curated/recent.sqlite');db.executescript('PRAGMA foreign_keys=ON;CREATE TABLE IF NOT EXISTS raw_file(sha256 TEXT PRIMARY KEY,path TEXT NOT NULL,url TEXT NOT NULL,retrieved_at TEXT NOT NULL,bytes INTEGER NOT NULL);CREATE TABLE IF NOT EXISTS weather_place(code TEXT PRIMARY KEY,longitude REAL,latitude REAL,grid_longitude REAL,grid_latitude REAL,timezone TEXT,raw_sha TEXT REFERENCES raw_file(sha256));CREATE TABLE IF NOT EXISTS daily(code TEXT REFERENCES weather_place(code),date TEXT,tmax REAL,tmin REAL,precip_mm REAL,CHECK(tmax>=tmin),CHECK(precip_mm>=0),PRIMARY KEY(code,date));')
 results={};failures=[];manifest=[]
 for code in codes:
  c=cities[code];params={'latitude':c['latitude'],'longitude':c['longitude'],'start_date':'2016-01-01','end_date':'2025-12-31','daily':'temperature_2m_max,temperature_2m_min,precipitation_sum','models':'era5_land','timezone':'auto','elevation':'nan'};url='https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(params);matches=sorted(OUT.glob(code+'_*.json'))
  try:
   if matches:path=matches[-1];body=path.read_bytes();stamp=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat()
   else:
    if '--replay-only' in sys.argv:raise ValueError('Aucune réponse mise en cache ; collecte externe non relancée')
    for attempt in range(2):
     try:
      with urllib.request.urlopen(url,timeout=50) as response:body=response.read()
      break
     except Exception:
      if attempt:raise
      time.sleep(2)
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();path=OUT/f'{code}_{stamp.replace(":","")}.json';path.write_bytes(body)
   sha=hashlib.sha256(body).hexdigest();entry={'code':code,'url':url,'path':str(path.relative_to(ROOT)),'sha256':sha,'retrieved_at':stamp,'bytes':len(body)};manifest.append(entry)
   d=json.loads(body);daily=d['daily'];units=d['daily_units'];assert units['temperature_2m_max']=='°C' and units['precipitation_sum']=='mm'
   days=daily['time'];assert len(days)==3653 and len(set(days))==3653
   expected=[(datetime.date(2016,1,1)+datetime.timedelta(days=i)).isoformat() for i in range(3653)];assert days==expected
   rows=list(zip(days,daily['temperature_2m_max'],daily['temperature_2m_min'],daily['precipitation_sum']));assert len(rows)==3653
   assert all(all(isinstance(v,(int,float)) for v in r[1:3]) and -90<=r[2]<=r[1]<=65 and (r[3] is None or 0<=r[3]<=2000) for r in rows), 'Températures incomplètes ou hors bornes'
   db.execute('INSERT OR IGNORE INTO raw_file VALUES(?,?,?,?,?)',(sha,entry['path'],url,stamp,len(body)));db.execute('INSERT OR REPLACE INTO weather_place VALUES(?,?,?,?,?,?,?)',(code,c['longitude'],c['latitude'],d['longitude'],d['latitude'],d['timezone'],sha));db.executemany('INSERT OR REPLACE INTO daily VALUES(?,?,?,?,?)',[(code,*r) for r in rows]);db.commit()
   annual=[]
   for y in range(2016,2026):
    rr=[r for r in rows if r[0].startswith(str(y))];assert len(rr)==365+calendar.isleap(y)
    annual.append({'year':y,'days':len(rr),'hot_days':sum(r[1]>=35 for r in rr),'warm_min_days':sum(r[2]>=20 for r in rr),'frost_days':sum(r[2]<0 for r in rr),'rain_mm':round(sum(r[3] for r in rr),1) if all(r[3] is not None for r in rr) else None})
   results[code]={'name':c['name'],'annual':annual,'grid':{'latitude':d['latitude'],'longitude':d['longitude'],'elevation':d.get('elevation')},'requested':{'latitude':c['latitude'],'longitude':c['longitude']},'timezone':d['timezone'],'provenance':entry};print(code,'OK',flush=True)
  except Exception as e:failures.append({'code':code,'error':str(e),'url':url});print(code,str(e),flush=True)
 content={'producer':'ECMWF / Copernicus, diffusion Open-Meteo','model':'ERA5-Land','nature':'Réanalyse : observations et modèle, pas un relevé de station ni une prévision','resolution':'0,1° (environ 11 km), altitude de la maille ; correction d’altitude désactivée','period':'2016–2025','license':'CC BY 4.0 pour les données diffusées par Open-Meteo','documentation':'https://open-meteo.com/en/docs/historical-weather-api','limits':'10 communes demandées ; couverture effective indiquée par fiche. Précipitations absentes des réponses ERA5-Land reçues : non calculées. Aucune extrapolation. Pas de soustraction avec les valeurs DRIAS. Minima quotidiens ≥20 °C, pas un calcul horaire des nuits. Moyennes calculées sur années complètes seulement.','places':results,'failures':failures}
 (ROOT/'dist/data/recent.json').write_text(json.dumps(content,ensure_ascii=False,separators=(',',':')));(ROOT/'data/raw/recent_manifest.json').write_text(json.dumps(manifest,indent=2));(ROOT/'reports/recent_collection.json').write_text(json.dumps({'accepted_places':len(results),'days':db.execute('SELECT COUNT(*) FROM daily').fetchone()[0],'failures':failures,'foreign_keys':db.execute('PRAGMA foreign_key_check').fetchall(),'checks':['units','complete 3653 dates','unique dates','numeric ranges','tmin <= tmax','complete annual denominators']},indent=2));db.close()
if __name__=='__main__':run()
