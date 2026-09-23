"""Pipeline reproductible. python src/pipeline.py --offline [--verify-replay]."""
import argparse
import csv
import json
import os
import shutil
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import ROOT,read_json,settings,sha256,utcnow,write_json
from src.collect import collect
from src.validate import RULES,climate_errors,fossil_errors,profile
from src.transform import create_database,export_csv,export_outputs,semantic_fingerprint,write_dashboard

def run(offline=False,config=None,manifest_path=None):
    started=time.perf_counter()
    cfg=config or settings()
    contract=read_json(ROOT/"config/data_contract.yaml")
    manifest=read_json(manifest_path or ROOT/"data/raw/manifest.json") if offline else collect(cfg)
    expected={"departments","cities","collections","occurrences"}|{f"{c}_{m}" for c in cfg["city_codes"] for m in [cfg["baseline_model"],*cfg["models"]]}
    if expected-set(manifest["files"]):
        raise ValueError("Collecte incomplète : "+", ".join(sorted(expected-set(manifest["files"]))))
    # Seuls les fichiers du périmètre courant ; aucune réutilisation de série hors configuration.
    manifest={**manifest,"files":{k:manifest["files"][k] for k in sorted(expected)}}
    payloads={}
    for key,e in manifest["files"].items():
        body=(ROOT/e["path"]).read_bytes()
        if sha256(body)!=e["sha256"]:
            raise ValueError(f"Intégrité raw compromise : {key}")
        payloads[key]=json.loads(body)
    features=[f for f in payloads["departments"]["features"] if f["properties"]["region"]==cfg["region_code"]]
    if {f["properties"]["code"] for f in features}!=set(cfg["departments"]):
        raise ValueError("Contrat géographique : départements manquants ou inattendus")
    cities=[c for c in payloads["cities"] if c["code"] in cfg["city_codes"]]
    if len(cities)!=len(cfg["city_codes"]):
        raise ValueError("Contrat : communes manquantes")
    collections={str(c["collection_no"]):c for c in payloads["collections"]["records"]}
    occurrences=payloads["occurrences"]["records"]
    if not occurrences or not all(set(contract["datasets"]["fossils"]["required_source_fields"])<=set(r) for r in occurrences):
        raise ValueError("Schéma PBDB inattendu : traitement interrompu")
    climate_payloads={k:v for k,v in payloads.items() if k not in ("departments","cities","collections","occurrences")}
    climate_rows=[]
    for key,p in climate_payloads.items():
        entry=manifest["files"][key]
        m=entry["metadata"]
        expected_period=cfg["baseline"] if m["kind"]=="baseline" else cfg["future"]
        if [m["start"],m["end"]]!=expected_period:
            raise ValueError(f"Fenêtre configurée différente du raw : {key}. Relancer collect.py")
        daily=p.get("daily",{})
        variables=cfg["daily_variables"]
        units=contract["datasets"]["climate_daily"]["source_units"]
        if any(p.get("daily_units",{}).get(k)!=v for k,v in units.items()):
            raise ValueError(f"Unités inattendues : {key}")
        n=len(daily.get("time",[]))
        expected_days=(date.fromisoformat(m["end"])-date.fromisoformat(m["start"])).days+1
        if n!=expected_days or any(len(daily.get(k,[]))!=n for k in variables):
            raise ValueError(f"Série tronquée ou schéma incorrect : {key}")
        for i,day in enumerate(daily["time"]):
            climate_rows.append({"series_id":key,"date":day,"tmean_c":daily["temperature_2m_mean"][i],"tmax_c":daily["temperature_2m_max"][i],"tmin_c":daily["temperature_2m_min"][i],"precipitation_mm":daily["precipitation_sum"][i]})
    write_json(ROOT/"reports/profile_before.json",{"fossils":profile(occurrences),"climate_daily":profile(climate_rows)})
    counters=Counter({k:0 for k in RULES})
    rejected=[]; accepted=[]; clean_climate=[]; seen_f=set(); seen_c=set(); duplicates=0
    dataset_counts={"fossils":{"input":len(occurrences),"accepted":0,"rejected":0,"duplicates":0},"climate_daily":{"input":len(climate_rows),"accepted":0,"rejected":0,"duplicates":0}}
    for r in occurrences:
        c=collections.get(str(r.get("collection_no")))
        reasons,dep=fossil_errors(r,c,features,cfg)
        key=str(r.get("occurrence_no"))
        duplicate=key in seen_f
        if duplicate: reasons.append("Q11")
        if reasons:
            counters.update(reasons)
            bucket="duplicates" if duplicate and reasons==["Q11"] else "rejected"
            dataset_counts["fossils"][bucket]+=1
            rejected.append({"dataset":"fossils","key":key,"reasons":";".join(reasons),"detail":cfg["excluded_collections"].get(str(r.get("collection_no")),""),"row_json":json.dumps(r,ensure_ascii=False)})
        else:
            seen_f.add(key);accepted.append((r,c,dep));dataset_counts["fossils"]["accepted"]+=1
    for r in climate_rows:
        reasons=climate_errors(r,manifest["files"][r["series_id"]]["metadata"])
        key=(r["series_id"],r["date"])
        duplicate=key in seen_c
        if duplicate: reasons.append("Q11")
        if reasons:
            counters.update(reasons)
            bucket="duplicates" if duplicate and reasons==["Q11"] else "rejected"
            dataset_counts["climate_daily"][bucket]+=1
            rejected.append({"dataset":"climate_daily","key":"/".join(key),"reasons":";".join(reasons),"detail":"","row_json":json.dumps(r,ensure_ascii=False)})
        else:
            seen_c.add(key);clean_climate.append(r);dataset_counts["climate_daily"]["accepted"]+=1
    if len(accepted)+len(clean_climate)<100:
        raise ValueError("Moins de 100 observations valides")
    curated=ROOT/"data/curated";curated.mkdir(exist_ok=True)
    dbtemp=curated/"chronoterre.sqlite.tmp"
    db=create_database(dbtemp,manifest,features,cities,accepted,clean_climate,climate_payloads)
    fingerprint,counts=semantic_fingerprint(db)
    report={"pipeline":"ChronoTerre-IDF","contract_version":"1.0.0","executed_at":utcnow(),"configuration_sha256":sha256(json.dumps(cfg,sort_keys=True).encode()),"offline":offline,"input_rows":sum(x["input"] for x in dataset_counts.values()),"accepted_rows":sum(x["accepted"] for x in dataset_counts.values()),"rejected_rows":sum(x["rejected"] for x in dataset_counts.values()),"duplicates_removed":sum(x["duplicates"] for x in dataset_counts.values()),"datasets":dataset_counts,"rules":[{"id":k,"condition":v,"failure_count":counters[k],"action":"reject_and_preserve" if k!="Q11" else "deduplicate_and_preserve"} for k,v in RULES.items()],"structural_checks":{"raw_sha256":"PASS","source_schema_and_units":"PASS","requested_date_windows":"PASS","foreign_keys":"PASS"},"quality_status":"PASS_WITH_WARNINGS" if rejected else "PASS","table_counts":counts,"semantic_sha256":fingerprint,"raw_files":[{"key":k,**v} for k,v in manifest["files"].items()],"duration_seconds":0}
    report["duration_seconds"]=round(time.perf_counter()-started,3)
    dashboard=export_outputs(db,curated,features,cfg,report)
    db.close()
    os.replace(dbtemp,curated/"chronoterre.sqlite")
    export_csv(ROOT/"data/rejected/rejected_rows.csv",rejected,["dataset","key","reasons","detail","row_json"])
    report["duration_seconds"]=round(time.perf_counter()-started,3)
    report["duration_scope"]="collect_or_load_validate_transform_and_export_before_final_report_write"
    write_json(curated/"dashboard.json",dashboard)
    write_dashboard(dashboard)
    write_json(ROOT/"reports/run_report.json",report)
    assert report["input_rows"]==report["accepted_rows"]+report["rejected_rows"]+report["duplicates_removed"]
    print(json.dumps({k:report[k] for k in ("input_rows","accepted_rows","rejected_rows","duplicates_removed","quality_status","semantic_sha256")},ensure_ascii=False),flush=True)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--offline",action="store_true")
    p.add_argument("--verify-replay",action="store_true")
    p.add_argument("--config",type=Path)
    p.add_argument("--manifest",type=Path)
    args=p.parse_args()
    try:
        first=run(args.offline,settings(args.config),args.manifest)
        if args.verify_replay:
            second=run(True,settings(args.config),args.manifest)
            proof={"executed_at":utcnow(),"same_input":True,"first":first["semantic_sha256"],"second":second["semantic_sha256"],"first_counts":first["table_counts"],"second_counts":second["table_counts"],"passed":first["semantic_sha256"]==second["semantic_sha256"] and first["table_counts"]==second["table_counts"]}
            write_json(ROOT/"reports/idempotence.json",proof)
            if not proof["passed"]:raise ValueError("Échec du rejeu")
            print("REJEU IDENTIQUE : PASS")
    except Exception as e:
        write_json(ROOT/"reports/failure_report.json",{"executed_at":utcnow(),"quality_status":"FAIL","error":str(e),"action":"previous_curated_database_preserved"})
        print(f"ÉCHEC : {e}",file=sys.stderr)
        raise SystemExit(1)

if __name__=="__main__":main()
