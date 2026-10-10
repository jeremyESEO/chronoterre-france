import json,sqlite3,unittest,threading,urllib.request,urllib.error,time
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from shapely.geometry import shape,Point
from national.collect import ROOT
from national.validate import fossil_errors,climate_errors
from national.serve import Handler
class FranceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.db=sqlite3.connect('file:'+str(ROOT/'data/curated/france.sqlite')+'?mode=ro',uri=True)
  cls.http=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.url='http://127.0.0.1:'+str(cls.http.server_port)
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.db.close()
 def get(self,path):
  try:
   with urllib.request.urlopen(self.url+path,timeout=20) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_foreign_keys(self):self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
 def test_replay(self):self.assertTrue(json.loads((ROOT/'reports/france_idempotence.json').read_text())['equal'])
 def test_real_demo(self):self.assertGreater(self.db.execute('SELECT count(*) FROM fossil_occurrence').fetchone()[0],100)
 def test_outside_idf_corse_overseas(self):
  for code in ['17300','13004','74056','23096','2A004','97411']:
   s,d=self.get('/api/v2/climate?code='+code+'&horizon=2050');self.assertEqual(s,200);self.assertTrue(d['values'])
  self.assertNotEqual(self.get('/api/v2/climate?code=97411')[1]['place']['domain'],'France hexagonale')
 def test_horizons_not_interpolated(self):
  a=self.get('/api/v2/climate?code=17300&horizon=2030')[1]['values'];b=self.get('/api/v2/climate?code=17300&horizon=2100')[1]['values'];self.assertNotEqual([r['value'] for r in a],[r['value'] for r in b]);self.assertEqual(self.get('/api/v2/climate?code=17300&horizon=2076')[0],400)
 def test_sea_conversion(self):self.assertEqual(self.db.execute("SELECT value FROM climate_value WHERE commune_code='17300' AND indicator_id='R3' AND period_id='2050'").fetchone()[0],24)
 def test_search_postal(self):self.assertIn('17300',[r['code'] for r in self.get('/api/v2/search?q=17000')[1]['results']])
 def test_pagination_bbox(self):
  s,d=self.get('/api/v2/fossils?bbox=-5,42,10,52&limit=10');self.assertEqual(s,200);self.assertEqual(len(d['results']),10);ids={r['occurrence_id'] for r in d['results']};n=self.get('/api/v2/fossils?bbox=-5,42,10,52&limit=10&after='+str(d['next_after']))[1];self.assertFalse(ids.intersection(r['occurrence_id'] for r in n['results']));self.assertEqual(self.get('/api/v2/fossils?bbox=-180,-90,180,90')[0],400)
 def test_invalid_isolated_record(self):
  # Fixture volontairement fausse, jamais importée en production.
  self.assertIn('F01',fossil_errors({'occurrence_no':0,'collection_no':1,'identified_name':'test'},None,None,{}));self.assertIn('C01',climate_errors(float('nan'),None,None,'°C'));self.assertIn('C02',climate_errors(5,9,10,'j/an'))
 def test_geometry_inside_outside(self):
  geometries=[shape(json.loads(r[0])) for r in self.db.execute("SELECT geometry FROM hazard_zone WHERE hazard_id='river_flood'")];self.assertEqual(len(geometries),3)
  for g in geometries:self.assertTrue(g.is_valid)
  p=geometries[0].representative_point();d=self.get(f'/api/v2/hazards/point?lon={p.x}&lat={p.y}')[1];self.assertTrue(d['intersections']);d=self.get('/api/v2/hazards/point?lon=2.35&lat=48.85')[1];self.assertFalse(d['intersections']);self.assertIn('ne signifie pas',d['warning'])
 def test_parcel_multiple_zones(self):self.assertGreater(self.db.execute('SELECT count(*) FROM (SELECT parcel_id FROM parcel_zone GROUP BY parcel_id HAVING count(*)>1)').fetchone()[0],0)
 def test_media_files_and_associations(self):
  for path,author,licence in self.db.execute('SELECT local_path,author,license FROM media'):self.assertTrue((ROOT/'dist'/path).is_file());self.assertTrue(author and licence)
  self.assertEqual(self.db.execute("SELECT count(*) FROM taxon_media WHERE match_level='exact_specimen'").fetchone()[0],0)
 def test_errors(self):
  self.assertEqual(self.get('/api/v2/search?q=x')[0],400);self.assertEqual(self.get('/api/v2/climate?code=xxxx')[0],404);self.assertEqual(self.get('/api/v2/unknown')[0],404);self.assertEqual(self.get('/api/v2/urban?lon=1&lat=43&layer=secret')[0],400)
 def test_provider_failure_without_fake_data(self):
  from unittest.mock import patch
  from urllib.request import build_opener
  # Le client conserve son opener ; seul l'appel fournisseur du serveur est simulé en échec.
  client=build_opener()
  with patch('national.serve.urllib.request.urlopen',side_effect=TimeoutError('panne simulée')):
   try:client.open(self.url+'/api/v2/urban?lon=1&lat=43&layer=parcelle')
   except urllib.error.HTTPError as e:
    self.assertEqual(e.code,503);d=json.load(e);self.assertEqual(d['error'],'provider_unavailable');self.assertNotIn('data',d)
   else:self.fail('503 attendu')
if __name__=='__main__':unittest.main()
