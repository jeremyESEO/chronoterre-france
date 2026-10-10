"""Migration non destructive : contrôle V1, base France parallèle, retour vérifiable."""
import hashlib,sqlite3,json,zipfile
from national.collect import ROOT,dump
p=ROOT/'v1/ChronoTerre_IDF_original.zip';db=sqlite3.connect('file:'+str(ROOT/'data/curated/chronoterre.sqlite')+'?mode=ro',uri=True)
counts={r[0]:db.execute('SELECT count(*) FROM "'+r[0]+'"').fetchone()[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
r={'v1_archive_sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'v1_counts':counts,'v1_integrity':db.execute('PRAGMA integrity_check').fetchone()[0],'strategy':'V1 intacte ; nouvelle base france.sqlite issue des sources nationales, pas de mélange ERA5/DRIAS','rollback':'Extraire v1/ChronoTerre_IDF_original.zip dans un autre dossier ; utiliser son README. Pour le site, redéployer la version Sites 1.'}
with zipfile.ZipFile(p) as z:r['archive_check']=z.testzip()
dump(ROOT/'reports/migration_v1.json',r);print(json.dumps(r,ensure_ascii=False,indent=2))
