"""Normalisation relationnelle, agrégations transparentes et export du dashboard."""
import csv
import json
import math
import sqlite3
from collections import defaultdict
from pathlib import Path
from src.common import ROOT, sha256, write_json

SOURCES = [
 ("pbdb", "Paleobiology Database", "PBDB contributors", "https://paleobiodb.org/", "CC BY 4.0"),
 ("archive", "Open-Meteo Historical Weather API", "Open-Meteo / Copernicus C3S / ECMWF", "https://open-meteo.com/en/docs/historical-weather-api", "CC BY 4.0 ; attribution C3S/ECMWF"),
 ("climate", "Open-Meteo Climate API", "Open-Meteo / CMIP6 HighResMIP / MRI / EC-Earth", "https://open-meteo.com/en/docs/climate-api", "CC BY 4.0 ; attribution producteurs CMIP6"),
 ("etalab", "Contours administratifs 2025, 100 m", "Etalab / IGN ADMIN EXPRESS", "https://github.com/etalab/contours-administratifs", "Licence Ouverte 2.0 (IGN ADMIN EXPRESS, métropole)"),
 ("geoapi", "API Découpage administratif", "DINUM / INSEE / IGN", "https://geo.api.gouv.fr/", "Licence Ouverte 2.0"),
]
MODELS = [
 ("era5_seamless", "ERA5-Seamless", "ECMWF / Copernicus C3S", "reanalysis", "Température ERA5-Land ; pluie ERA5 ; référence 1991–2020"),
 ("MRI_AGCM3_2_S", "MRI-AGCM3-2-S", "Meteorological Research Institute, Japon", "projection", "HighResMIP, forçage proche RCP8.5 ; correction ERA5-Land"),
 ("EC_Earth3P_HR", "EC-Earth3P-HR", "EC-Earth consortium / SMHI", "projection", "HighResMIP, forçage proche RCP8.5 ; correction ERA5-Land"),
]

def optional(value):
    return None if value is None or value == "" or (str(value).startswith("NO_") and str(value).endswith("_SPECIFIED")) else value

def raw_id(key, entry):
    return key + ":" + entry["sha256"][:12]

def export_csv(path, rows, fields=None):
    rows = list(rows)
    fields = fields or (list(rows[0]) if rows else [])
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def query(db, sql, params=()):
    return [dict(r) for r in db.execute(sql, params)]

def create_database(path, manifest, features, cities, accepted, climate_rows, climate_payloads):
    path = Path(path)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript((ROOT / "sql/schema.sql").read_text(encoding="utf-8"))
    db.executemany("INSERT INTO source VALUES(?,?,?,?,?)", SOURCES)
    for key,e in sorted(manifest["files"].items()):
        db.execute("INSERT INTO raw_file VALUES(?,?,?,?,?,?,?)", (raw_id(key,e),e["source"],e["path"],e["url"],e["sha256"],e["fetched_at"],e["bytes"]))
    rf = lambda k: raw_id(k,manifest["files"][k])
    for f in features:
        p = f["properties"]
        db.execute("INSERT INTO department VALUES(?,?,?,?)", (p["code"],p["nom"],p["region"],rf("departments")))
    for c in cities:
        lon,lat = c["centre"]["coordinates"]
        db.execute("INSERT INTO city VALUES(?,?,?,?,?,?)",(c["code"],c["nom"],c["codeDepartement"],lat,lon,rf("cities")))
    for r,c,dep in sorted(accepted,key=lambda x:int(x[0]["occurrence_no"])):
        interval = [r["early_interval"],r.get("late_interval", ""),float(r["max_ma"]),float(r["min_ma"])]
        interval_id = sha256(json.dumps(interval).encode())[:20]
        taxon_id = str(r.get("accepted_no") or "name:"+r["identified_name"])
        ref = int(r["reference_no"])
        db.execute("INSERT OR IGNORE INTO bibliography VALUES(?,?,?)", (ref,r["primary_reference"],f"https://paleobiodb.org/classic/displayReference?reference_no={ref}"))
        db.execute("INSERT OR IGNORE INTO taxon VALUES(?,?,?,?,?,?)",(taxon_id,r.get("accepted_name") or r["identified_name"],r.get("accepted_rank"),optional(r.get("phylum")),optional(r.get("class")),optional(r.get("family"))))
        db.execute("INSERT OR IGNORE INTO geo_interval VALUES(?,?,?,?,?)", (interval_id,*interval))
        db.execute("INSERT OR IGNORE INTO fossil_site VALUES(?,?,?,?,?,?,?,?,?,?)", (int(c["collection_no"]),c["collection_name"],dep,float(c["lat"]),float(c["lng"]),c.get("environment"),c.get("latlng_basis"),c.get("latlng_precision"),c.get("geogcomments"),rf("collections")))
        db.execute("INSERT INTO fossil_occurrence VALUES(?,?,?,?,?,?,?)",(int(r["occurrence_no"]),int(c["collection_no"]),taxon_id,ref,interval_id,r["identified_name"],rf("occurrences")))
    db.executemany("INSERT INTO climate_model VALUES(?,?,?,?,?)",MODELS)
    for key,payload in sorted(climate_payloads.items()):
        m = manifest["files"][key]["metadata"]
        db.execute("INSERT INTO climate_series VALUES(?,?,?,?,?,?,?,?,?)",(key,m["city_code"],m["model"],m["kind"],m["start"],m["end"],payload["latitude"],payload["longitude"],rf(key)))
    db.executemany("INSERT INTO climate_day VALUES(:series_id,:date,:tmean_c,:tmax_c,:tmin_c,:precipitation_mm)", climate_rows)
    db.commit()
    if db.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("Intégrité référentielle violée")
    db.execute("PRAGMA optimize")
    return db

def build_climate_summary(db, minimum_fraction=0.9):
    annual = query(db,"SELECT * FROM v_climate_annual ORDER BY series_id,year")
    series = query(db,"SELECT * FROM climate_series ORDER BY series_id")
    all_months = query(db,"""SELECT series_id,CAST(substr(date,1,4) AS INT) year,
      CAST(substr(date,6,2) AS INT) month,COUNT(*) days,AVG(tmean_c) temp,SUM(precipitation_mm) rain
      FROM climate_day GROUP BY series_id,year,month
      HAVING COUNT(*)=CAST(strftime('%d',date(substr(date,1,7)||'-01','+1 month','-1 day')) AS INT)
      ORDER BY series_id,year,month""")
    result=[]
    for s in series:
        a=[x for x in annual if x["series_id"]==s["series_id"]]
        expected = int(s["end_date"][:4])-int(s["start_date"][:4])+1
        if len(a)/expected<minimum_fraction:
            # Pas de total annuel extrapolé à partir d'années incomplètes.
            result.append({**s,"available":False,"complete_years":len(a),"expected_years":expected})
            continue
        summary={k:round(sum(x[k] for x in a)/len(a),3) for k in ("mean_c","rain_mm","hot_days","tropical_nights","frost_days")}
        months=[]
        for month in range(1,13):
            m=[x for x in all_months if x["series_id"]==s["series_id"] and x["month"]==month and x["year"] in {y["year"] for y in a}]
            months.append({"month":month,"temp":round(sum(x["temp"] for x in m)/len(m),3),"rain":round(sum(x["rain"] for x in m)/len(m),3)})
        result.append({**s,"available":True,"complete_years":len(a),"expected_years":expected,"excluded_years":sorted(set(range(int(s["start_date"][:4]),int(s["end_date"][:4])+1))-{x["year"] for x in a}),"summary":summary,"monthly":months})
    return result,annual

def analogues(climate,city_code,model_id,options):
    future=next((x for x in climate if x["city_code"]==city_code and x["model_id"]==model_id and x.get("available")),None)
    if not future:
        return []
    out=[]
    for base in climate:
        if base["kind"]!="baseline" or not base.get("available"):
            continue
        terms=[]
        for f,b in zip(future["monthly"],base["monthly"]):
            terms.extend([((f["temp"]-b["temp"])/options["temperature_scale_c"])**2,((f["rain"]-b["rain"])/options["precipitation_scale_mm"])**2])
        dist=math.sqrt(sum(terms)/24)
        out.append({"city_code":base["city_code"],"distance":round(dist,6),"close":dist<=options["close_distance_max"]})
    return sorted(out,key=lambda x:(x["distance"],x["city_code"]))

def semantic_fingerprint(db):
    """Empreinte du contenu ordonné, indépendante des pages internes SQLite."""
    import hashlib
    digest=hashlib.sha256()
    counts={}
    for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        columns=[r[1] for r in db.execute(f'PRAGMA table_info("{name}")')]
        order=",".join('"'+c+'"' for c in columns)
        digest.update(name.encode())
        n=0
        for row in db.execute(f'SELECT * FROM "{name}" ORDER BY {order}'):
            digest.update(json.dumps(list(row),ensure_ascii=False,separators=(",",":"),allow_nan=False).encode())
            digest.update(b"\n")
            n+=1
        counts[name]=n
    return digest.hexdigest(),counts

def export_outputs(db,outdir,features,cfg,report):
    fossils=query(db,"SELECT * FROM v_fossils ORDER BY occurrence_id")
    export_csv(outdir/"fossils.csv",fossils)
    export_csv(outdir/"climate_daily.csv",query(db,"SELECT * FROM climate_day ORDER BY series_id,date"))
    climate,annual=build_climate_summary(db,cfg["minimum_complete_year_fraction"])
    export_csv(outdir/"climate_annual.csv",annual)
    export_csv(outdir/"climate_summary.csv",[{"series_id":s["series_id"],"city_code":s["city_code"],"model_id":s["model_id"],"kind":s["kind"],"complete_years":s["complete_years"],**s.get("summary",{})} for s in climate])
    write_json(outdir/"departments.geojson",{"type":"FeatureCollection","features":features})
    # Citations et sites séparés pour alléger le navigateur sans perdre de traçabilité.
    compact=[{k:r[k] for k in ("occurrence_id","site_id","taxon_id","accepted_name","identified_name","class_name","phylum","family","early_name","late_name","max_ma","min_ma","reference_id")} for r in fossils]
    data={"meta":{"title":cfg["project"],"snapshot_at":report["executed_at"],"region":"Île-de-France","baseline":cfg["baseline"],"future":cfg["future"],"status":report["quality_status"],"fingerprint":report["semantic_sha256"],"analogue":cfg["analogue"]},"departments":{"type":"FeatureCollection","features":features},"cities":query(db,"SELECT * FROM city ORDER BY name"),"sites":query(db,"SELECT * FROM fossil_site ORDER BY site_id"),"fossils":compact,"references":query(db,"SELECT * FROM bibliography ORDER BY reference_id"),"sources":query(db,"SELECT * FROM source ORDER BY source_id"),"models":query(db,"SELECT * FROM climate_model ORDER BY model_id"),"climate":climate,"annual":annual,"quality":report}
    write_json(outdir/"dashboard.json",data)
    write_dashboard(data)
    return data

def write_dashboard(data):
    dist=ROOT/"dist"
    dist.mkdir(exist_ok=True)
    (dist/"data.js").write_text("window.CHRONOTERRE_DATA="+json.dumps(data,ensure_ascii=False,separators=(",",":"),allow_nan=False)+";\n",encoding="utf-8")
    return data
