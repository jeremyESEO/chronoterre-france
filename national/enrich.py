import json
from shapely.geometry import shape,Point,mapping,MultiPolygon
from shapely import make_valid,is_valid_reason
from national.collect import ROOT

def enrich(db,files,read,rejects,fails):
 p=ROOT/'config/test_places.json'
 if p.exists():
  for s in json.loads(p.read_text()):
   code=s['code'] if db.execute('SELECT 1 FROM commune WHERE code=?',(s['code'],)).fetchone() else None
   db.execute('INSERT INTO test_place VALUES(?,?,?,?,?,?)',(s['id'],s['label'],code,s['lon'],s['lat'],s['kind']))
   parcels=[];zones=[]
   for layer,r in s['resources'].items():
    if r['status']!='ok' or r['raw'] not in files:continue
    raw=r['raw'];d=read(raw)
    for f in d.get('features',[]):
     props=f['properties'];geom=f.get('geometry');gid=str(f.get('id') or props.get('id') or props.get('gid'))
     if layer=='document':
      docid=props.get('gpu_doc_id') or props.get('id') or gid
      db.execute('INSERT OR IGNORE INTO urban_document VALUES(?,?,?,?,?,?,?,?)',(docid,props.get('idurba') or props.get('name') or docid,props.get('typedoc'),props.get('datappro'),props.get('gpu_timestamp'),'https://www.geoportail-urbanisme.gouv.fr/document/by-id/'+docid,props.get('gpu_status','consulté'),raw))
      continue
     if not geom or not shape(geom).is_valid:
      fails['G01']+=1;rejects.append({'domain':layer,'key':gid,'reasons':['G01']});continue
     g=json.dumps(geom,separators=(',',':'));docid=props.get('gpu_doc_id') or props.get('id')
     if layer=='parcelle':
      pid=props.get('id') or props.get('idu') or gid
      db.execute('INSERT OR IGNORE INTO parcel VALUES(?,?,?,?,?,?,?,?)',(pid,code,props.get('section'),props.get('numero'),g,'EPSG:4326',props.get('updated') or props.get('date_creation'),raw));parcels.append((pid,shape(geom)))
     else:
      if docid:
       db.execute('INSERT OR IGNORE INTO urban_document VALUES(?,?,?,?,?,?,?,?)',(docid,props.get('idurba') or props.get('name') or docid,props.get('typedoc'),props.get('datappro'),props.get('gpu_timestamp'),'https://www.geoportail-urbanisme.gouv.fr/document/by-id/'+docid,props.get('gpu_status','consulté'),raw))
      if layer=='zone-urba':
       db.execute('INSERT OR IGNORE INTO urban_zone VALUES(?,?,?,?,?,?,?,?)',(gid,docid,props.get('typezone'),props.get('libelle'),props.get('datvalid'),props.get('urlfic'),g,raw));zones.append((gid,shape(geom)))
      elif layer in ['prescription-surf','assiette-sup-s']:
       db.execute('INSERT OR IGNORE INTO prescription VALUES(?,?,?,?,?,?)',(gid,docid,props.get('categorie') or props.get('typepsc'),props.get('libelle') or props.get('nomass'),g,raw))
   for pid,pg in parcels:
    for zid,zg in zones:
     if pg.intersects(zg):db.execute('INSERT OR IGNORE INTO parcel_zone VALUES(?,?,?)',(pid,zid,'GEOS intersects EPSG:4326, sans calcul métrique'))
 # Échantillons d’aléas officiels versionnés, chargés depuis la chaîne raw -> conversion.
 p=ROOT/'config/hazard_layers.json'
 if p.exists():
  for layer in json.loads(p.read_text()):
   if layer['raw'] not in files:continue
   db.execute('INSERT OR IGNORE INTO hazard VALUES(?,?,?)',(layer['hazard'],layer['label'],layer['nature']))
   data=read(layer['raw'])
   repaired=[]
   for i,f in enumerate(data['features']):
    geom=f.get('geometry')
    if geom and not shape(geom).is_valid:
     original=shape(geom);fixed=make_valid(original)
     if fixed.geom_type=='GeometryCollection':
      polys=[]
      for part in fixed.geoms:
       if part.geom_type=='Polygon':polys.append(part)
       elif part.geom_type=='MultiPolygon':polys.extend(part.geoms)
      fixed=MultiPolygon(polys)
     if fixed.is_valid and not fixed.is_empty and fixed.geom_type in ['Polygon','MultiPolygon']:
      repaired.append({'feature':i,'reason':is_valid_reason(original),'method':'GEOS make_valid; composantes polygonales conservées','original_raw':layer['raw']})
      geom=mapping(fixed);f['geometry']=geom
    if not geom or not shape(geom).is_valid or shape(geom).is_empty:
     fails['G01']+=1;rejects.append({'domain':'hazard','key':layer['id']+':'+str(i),'reasons':['G01']});continue
    g=shape(geom)
    props=f['properties'];zid=layer['id']+':'+str(i)
    db.execute('INSERT INTO hazard_zone VALUES(?,?,?,?,?,?,?,?)',(zid,layer['hazard'],str(props.get(layer.get('label_field',''),layer['label'])),layer['nature'],str(props.get(layer.get('scenario_field',''),layer.get('scenario',''))),str(props.get(layer.get('return_field',''),'')),json.dumps(f['geometry'],separators=(',',':')),layer['raw']))
    for pid,x,y in db.execute('SELECT place_id,longitude,latitude FROM test_place'):
     db.execute('INSERT INTO spatial_intersection VALUES(?,?,?,?)',(pid,zid,int(g.intersects(Point(x,y))),'GEOS intersects, limites incluses'))
   (ROOT/layer['curated']).write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
   (ROOT/'reports'/('geometry_'+layer['id']+'.json')).write_text(json.dumps({'raw':layer['raw'],'repairs':repaired},ensure_ascii=False,indent=2),encoding='utf-8')
 p=ROOT/'config/media.json'
 if p.exists():
  for m in json.loads(p.read_text()):
   if not all(m.get(x) for x in ['author','license','page_url','association_evidence']):fails['M01']+=1;continue
   db.execute('INSERT INTO media VALUES(?,?,?,?,?,?,?,?,?,?)',(m['id'],m['category'],m['page_url'],m['image_url'],m.get('local_path'),m['author'],m['license'],m['caption'],m['retrieved_at'],m['association_evidence']))
   for tid,name in db.execute('SELECT taxon_id,accepted_name FROM taxon'):
    match=name==m['taxon'] if m['match_level']=='same_taxon' else name.split()[0]==m['taxon'].split()[0]
    if match:db.execute('INSERT OR IGNORE INTO taxon_media VALUES(?,?,?)',(tid,m['id'],m['match_level']))
