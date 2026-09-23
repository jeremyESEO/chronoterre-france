"""Dashboard local + API JSON en lecture seule, sans installation tierce.

python src/serve.py --open ; http://127.0.0.1:8000
"""
import argparse
import json
import sqlite3
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlparse
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import ROOT,haversine,read_json,settings
from src.transform import analogues,query

DB=ROOT/"data/curated/chronoterre.sqlite"

class Handler(SimpleHTTPRequestHandler):
    def json_response(self,value,status=200):
        body=json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-cache")
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers();self.wfile.write(body)

    def do_GET(self):
        url=urlparse(self.path)
        if url.path=="/runtime.js":
            b=b'window.CHRONOTERRE_API="/api/v1";'
            self.send_response(200);self.send_header("Content-Type","application/javascript");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b);return
        if not url.path.startswith("/api/"):
            return super().do_GET()
        args={k:v[-1] for k,v in parse_qs(url.query).items()}
        try:
            db=sqlite3.connect(DB.as_uri()+"?mode=ro",uri=True)
            db.row_factory=sqlite3.Row
            with db:
                if url.path=="/api/v1/health":
                    result={"status":"ok","api_version":"1.0","database":"read-only","region":"11"}
                elif url.path=="/api/v1/bootstrap":
                    result=read_json(ROOT/"data/curated/dashboard.json")
                elif url.path=="/api/v1/cities":
                    result={"items":query(db,"SELECT * FROM city ORDER BY name")}
                elif url.path=="/api/v1/quality":
                    result=read_json(ROOT/"reports/run_report.json")
                elif url.path=="/api/v1/fossils":
                    limit=int(args.get("limit",100));offset=int(args.get("offset",0))
                    if not 1<=limit<=500 or offset<0:raise ValueError("limit : 1–500 ; offset ≥ 0")
                    where=[];params=[]
                    for name,col in [("department","department_code"),("class","class_name")]:
                        if args.get(name):where.append(col+" = ?");params.append(args[name])
                    if args.get("q"):
                        where.append("(accepted_name LIKE ? OR site_name LIKE ?)");params.extend(["%"+args["q"]+"%"]*2)
                    lo=float(args.get("min_ma",0));hi=float(args.get("max_ma",4600))
                    if not 0<=lo<=hi<=4600:raise ValueError("Âges : 0 ≤ min_ma ≤ max_ma ≤ 4600")
                    where.extend(["max_ma >= ?","min_ma <= ?"]);params.extend([lo,hi])
                    sql="SELECT * FROM v_fossils WHERE "+" AND ".join(where)+" ORDER BY occurrence_id"
                    rows=query(db,sql,params)
                    if args.get("city"):
                        city=db.execute("SELECT * FROM city WHERE city_code=?",(args["city"],)).fetchone()
                        if not city:raise ValueError("Commune inconnue")
                        radius=float(args.get("radius",30))
                        if not 1<=radius<=200:raise ValueError("Rayon : 1–200 km")
                        rows=[{**r,"distance_km":round(haversine(city["latitude"],city["longitude"],r["latitude"],r["longitude"]),2)} for r in rows]
                        rows=sorted((r for r in rows if r["distance_km"]<=radius),key=lambda r:(r["distance_km"],r["occurrence_id"]))
                    result={"total":len(rows),"limit":limit,"offset":offset,"items":rows[offset:offset+limit]}
                elif url.path=="/api/v1/climate":
                    data=read_json(ROOT/"data/curated/dashboard.json")
                    city=args.get("city","78640")
                    result={"city_code":city,"items":[x for x in data["climate"] if x["city_code"]==city]}
                    if not result["items"]:raise ValueError("Commune inconnue")
                elif url.path=="/api/v1/analogues":
                    data=read_json(ROOT/"data/curated/dashboard.json")
                    city=args.get("city","78640");model=args.get("model","MRI_AGCM3_2_S")
                    rows=analogues(data["climate"],city,model,settings()["analogue"])
                    if not rows:raise ValueError("Commune, modèle ou série indisponible")
                    result={"city_code":city,"model":model,"scope":"10 communes franciliennes de l'échantillon","method":"RMSE mensuelle normalisée : température / 1 °C ; pluie / 20 mm, 24 composantes","items":rows}
                else:
                    self.json_response({"error":"Route inconnue","documentation":"docs/api.md"},404);return
            db.close()
            self.json_response(result)
        except (ValueError,TypeError) as e:
            self.json_response({"error":str(e)},400)
        except (sqlite3.Error,OSError):
            self.json_response({"error":"Base indisponible. Exécuter python src/pipeline.py --offline."},503)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--port",type=int,default=8000);p.add_argument("--open",action="store_true")
    args=p.parse_args()
    if not DB.exists():raise SystemExit("Base absente : python src/pipeline.py --offline")
    server=ThreadingHTTPServer(("127.0.0.1",args.port),partial(Handler,directory=str(ROOT/"dist")))
    url=f"http://127.0.0.1:{args.port}"
    print(f"ChronoTerre : {url} — Ctrl+C pour arrêter.",flush=True)
    if args.open:threading.Timer(0.5,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=="__main__":main()
