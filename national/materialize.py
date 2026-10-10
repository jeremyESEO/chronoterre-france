"""Recompose les archives découpées pour respecter la limite de taille du dépôt."""
import hashlib,json
from national.collect import ROOT

def materialize():
 manifest=ROOT/'config/storage_parts.json'
 if not manifest.exists():return
 for e in json.loads(manifest.read_text()):
  target=ROOT/e['path']
  if target.exists():continue
  temp=target.with_suffix(target.suffix+'.assemble.tmp');h=hashlib.sha256()
  with temp.open('wb') as out:
   for part in e['parts']:
    with (ROOT/part).open('rb') as inp:
     for chunk in iter(lambda:inp.read(1048576),b''):out.write(chunk);h.update(chunk)
  if h.hexdigest()!=e['sha256']:temp.unlink();raise ValueError('Archive découpée corrompue : '+e['path'])
  temp.replace(target)
if __name__=='__main__':materialize()
