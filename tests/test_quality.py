"""Tests utiles : erreurs de sources, géographie, analogues et contraintes SQL."""
import copy
import math
import sqlite3
import unittest
from src.common import ROOT,inside_geometry,haversine,settings
from src.validate import climate_errors,fossil_errors
from src.transform import analogues

class QualityTests(unittest.TestCase):
    def setUp(self):
        self.row={"date":"2040-02-29","tmin_c":2,"tmean_c":5,"tmax_c":9,"precipitation_mm":4}
        self.meta={"start":"2030-01-01","end":"2049-12-31"}

    def test_valid_leap_day(self):
        self.assertEqual(climate_errors(self.row,self.meta),[])

    def test_impossible_date_and_window(self):
        for d in ["2041-02-29","2029-12-31","2050-01-01","2040-2-29"]:
            self.assertIn("Q10",climate_errors({**self.row,"date":d},self.meta))

    def test_negative_rain_is_rejected(self):
        self.assertIn("Q09",climate_errors({**self.row,"precipitation_mm":-1},self.meta))

    def test_missing_nan_and_inverted_temperatures(self):
        for v in [None,float("nan"),float("inf"),-100,99]:
            self.assertIn("Q08",climate_errors({**self.row,"tmean_c":v},self.meta))
        self.assertIn("Q08",climate_errors({**self.row,"tmin_c":20},self.meta))

    def test_polygon_hole_and_multipolygon(self):
        outer=[[0,0],[4,0],[4,4],[0,4],[0,0]];hole=[[1,1],[2,1],[2,2],[1,2],[1,1]]
        g={"type":"Polygon","coordinates":[outer,hole]}
        self.assertTrue(inside_geometry(3,3,g));self.assertFalse(inside_geometry(1.5,1.5,g));self.assertFalse(inside_geometry(8,8,g))
        self.assertTrue(inside_geometry(3,3,{"type":"MultiPolygon","coordinates":[[outer,hole]]}))

    def test_political_coordinates_and_unknown_origin_rejected(self):
        f=[{"properties":{"code":"75","nom":"Paris"},"geometry":{"type":"Polygon","coordinates":[[[0,0],[4,0],[4,4],[0,4],[0,0]]]}}]
        r={"occurrence_no":"1","collection_no":"197471","identified_name":"Test","max_ma":50,"min_ma":40,"reference_no":"1","primary_reference":"Reference"}
        c={"lat":2,"lng":2,"latlng_basis":"based on political unit"}
        errors,dep=fossil_errors(r,c,f,settings())
        self.assertEqual(dep,"75");self.assertIn("Q06",errors);self.assertIn("Q07",errors)
        errors,_=fossil_errors({**r,"min_ma":60},c,f,settings());self.assertIn("Q04",errors)

    def test_haversine_same_point(self):
        self.assertEqual(haversine(48.8,2.3,48.8,2.3),0)
        self.assertAlmostEqual(haversine(0,0,1,0),111.195,places=2)

    def test_analogue_scale_and_no_close_match(self):
        base={"city_code":"A","model_id":"era5_land","kind":"baseline","available":True,"monthly":[{"temp":10,"rain":50} for _ in range(12)]}
        future={**base,"city_code":"B","model_id":"M","kind":"future","monthly":[{"temp":14,"rain":50} for _ in range(12)]}
        r=analogues([base,future],"B","M",settings()["analogue"])
        self.assertAlmostEqual(r[0]["distance"],math.sqrt(8),places=5);self.assertFalse(r[0]["close"])
        self.assertEqual(analogues([base],"unknown","M",settings()["analogue"]),[])

    def test_sql_unique_and_foreign_keys(self):
        db=sqlite3.connect(":memory:");db.executescript((ROOT/"sql/schema.sql").read_text())
        with self.assertRaises(sqlite3.IntegrityError):db.execute("INSERT INTO climate_day VALUES('missing','2040-01-01',5,9,2,0)")
        db.execute("INSERT INTO source VALUES('x','x','x','https://x','x')")
        with self.assertRaises(sqlite3.IntegrityError):db.execute("INSERT INTO source VALUES('x','x','x','https://x','x')")
        db.close()

if __name__=="__main__":unittest.main()
