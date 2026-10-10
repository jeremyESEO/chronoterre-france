import math,re,unicodedata
from collections import Counter
RULES={
 'F01':('Identifiant et taxon','Identifiants PBDB numériques positifs, nom non vide','rejet'),
 'F02':('Coordonnées','WGS84 fini, point dans un contour départemental français','rejet'),
 'F03':('Provenance','Pas de coordonnées politiques ou de contradiction déjà connue','rejet'),
 'F04':('Âges','0 ≤ min_ma ≤ max_ma ≤ 4600 Ma','rejet'),
 'F05':('Référence','Identifiant et citation présents','rejet'),
 'U01':('Unicité','Clé métier unique','déduplication et comptage'),
 'C01':('Valeur climatique','Nombre fini dans les bornes physiques de son unité','rejet'),
 'C02':('Fourchette','Borne basse ≤ médiane ≤ borne haute','rejet'),
 'C03':('Série','Indicateur connu, commune jointe par code INSEE, horizon publié','rejet'),
 'G01':('Géométrie','Valide et non vide, référence connue','rejet'),
 'P01':('Raw','SHA-256 identique aux octets collectés','arrêt du pipeline'),
 'M01':('Média','Auteur, licence, page source et correspondance taxonomique','exclusion de la galerie'),
}
def finite(x):return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x)
def norm(x):return ''.join(c for c in unicodedata.normalize('NFKD',str(x).lower()) if c.isalnum())
def fossil_errors(r,c,department,exclusions):
 e=[]
 if not all(str(r.get(k,'')).isdigit() and int(r[k])>0 for k in ['occurrence_no','collection_no']) or not str(r.get('identified_name','')).strip():e.append('F01')
 if not c or not department:e.append('F02')
 if c and ('political' in c.get('latlng_basis','').lower() or str(c['collection_no']) in exclusions):e.append('F03')
 try:
  if not 0<=float(r['min_ma'])<=float(r['max_ma'])<=4600:e.append('F04')
 except (ValueError,KeyError,TypeError):e.append('F04')
 if not r.get('reference_no') or not r.get('primary_reference','').strip():e.append('F05')
 return e
def climate_errors(v,lo,hi,unit):
 e=[]
 if not finite(v) or (unit!='°C' and v<0) or (unit=='°C' and not -90<=v<=65) or (unit in ['j/an','nuits/an','j/saison','j'] and v>366):e.append('C01')
 if lo is not None and (not finite(lo) or not finite(hi) or not finite(v) or not lo<=v<=hi):e.append('C02')
 return e
class Profiler:
 def __init__(self):self.n=0;self.fields={};self.keys=set();self.duplicates=0
 def add(self,r,key):
  self.n+=1
  if key in self.keys:self.duplicates+=1
  self.keys.add(key)
  for k,v in r.items():
   f=self.fields.setdefault(k,{'types':Counter(),'missing':0,'min':None,'max':None,'modalities':Counter()});f['types'][type(v).__name__]+=1
   if v is None or v=='':f['missing']+=1
   elif finite(v):f['min']=v if f['min'] is None else min(f['min'],v);f['max']=v if f['max'] is None else max(f['max'],v)
   elif isinstance(v,str) and len(v)<80:f['modalities'][v]+=1
 def result(self):return {'rows':self.n,'columns':len(self.fields),'duplicate_business_keys':self.duplicates,'fields':{k:{**v,'types':dict(v['types']),'missing':v['missing']+self.n-sum(v['types'].values()),'modalities':v['modalities'].most_common(5)} for k,v in self.fields.items()}}
