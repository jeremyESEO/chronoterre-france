"""Small, reproducible decision index derived from the SQLite-generated climate shards."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
METRICS=[('S1','annuel'),('S2','annuel'),('G2','annuel'),('G4','été'),('AG1','été')]
def run():
 base=ROOT/'dist/data';meta=json.loads((base/'meta.json').read_text());out={h:[] for h in ['ref','2030','2050','2100']};inputs={}
 for p in sorted((base/'climate').glob('*.json')):
  inputs[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
  for code,c in json.loads(p.read_text()).items():
   # Only compare a compatible reference, geography and variable definition.
   if c['place']['domain']!='France hexagonale':continue
   if (c['place']['reference_start'],c['place']['reference_end'])!=(1976,2005):continue
   values={(r[0],r[1],r[2]):r[3:] for r in c['values']}
   for h in out:out[h].append([code]+[values.get((i,h,s),[None,None,None]) for i,s in METRICS])
 for h,rows in out.items():
  rows.sort(key=lambda r:r[0]);(base/f'home-{h}.json').write_text(json.dumps(rows,separators=(',',':'),allow_nan=False))
 provenance={'version':'1.0','metrics':[list(m) for m in METRICS],'columns':['code','S1','S2','G2','G4_ete','AG1_ete'],'value_columns':['central','lower','upper'],'reference':'1976–2005','domain':'France hexagonale et Corse','resolution':'Maille source 8 km ; point représentatif Météo-France, pas le logement','source':meta['raw']['climadiag'],'producer':'Météo-France / Climadiag Commune / DRIAS','license':'Licence Ouverte Etalab','scenario':'TRACC','period_method':'Fenêtres propres aux niveaux de réchauffement ; bornes annuelles par modèle non fournies dans l’export','counts':{h:len(r) for h,r in out.items()},'missing_rows':{h:sum(any(v[0] is None for v in r[1:]) for r in rows) for h,rows in out.items()},'input_sha256':inputs,'limits':['Adéquation aux préférences climatiques uniquement, pas une note d’habitabilité.','Aucun pronostic sur le bâti, la ressource en eau potable ou la valeur immobilière.','Les bornes par indicateur ne constituent pas des scénarios conjoints ni des probabilités.','Hors métropole : fiches conservées, classement non calculé.']}
 (base/'home-meta.json').write_text(json.dumps(provenance,ensure_ascii=False,separators=(',',':')))
 (ROOT/'reports/home_index.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2));print(provenance['counts'],provenance['missing_rows'])
if __name__=='__main__':run()
