"""Restauration sans réseau de la base compressée, vérifiée et atomique."""
import gzip,hashlib,json,shutil
from national.collect import ROOT
from national.materialize import materialize
materialize()
p=ROOT/'data/curated/france.sqlite';z=p.with_suffix('.sqlite.gz');m=ROOT/'reports/database_archive.json'
if not p.exists():
 if not z.exists():raise SystemExit('Archive absente : installer requirements-france.txt puis python -m national.pipeline')
 temp=p.with_suffix('.restore.tmp')
 with gzip.open(z,'rb') as src,temp.open('wb') as dst:shutil.copyfileobj(src,dst,1048576)
 h=hashlib.file_digest(temp.open('rb'),'sha256').hexdigest()
 if h!=json.loads(m.read_text())['uncompressed_sha256']:temp.unlink();raise SystemExit('Empreinte incorrecte')
 temp.replace(p)
print('Base disponible :',p)
