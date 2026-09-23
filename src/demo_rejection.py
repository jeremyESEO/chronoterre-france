"""Démonstration d'une ligne invalide, isolée des véritables données collectées."""
import sys
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import ROOT,utcnow,write_json
from src.validate import climate_errors,RULES

def main():
    good={"series_id":"DEMO_SYNTHETIQUE","date":"2040-07-10","tmean_c":24.0,"tmax_c":29.0,"tmin_c":18.0,"precipitation_mm":0.2}
    bad={**good,"date":"2040-02-30","precipitation_mm":-12.0,"tmin_c":35.0}
    meta={"start":"2030-01-01","end":"2049-12-31"}
    reasons=climate_errors(bad,meta)
    assert not climate_errors(good,meta)
    assert set(reasons)=={"Q08","Q09","Q10"}
    result={"executed_at":utcnow(),"synthetic_test_only":True,"production_data_modified":False,"valid_row":good,"invalid_row":bad,"rejected":True,"reasons":[{"id":k,"condition":RULES[k]} for k in reasons]}
    write_json(ROOT/"reports/demo_rejection.json",result)
    print("DÉMO : ligne synthétique rejetée pour température incohérente, pluie négative et date impossible.")
    print("Données réelles intactes. Preuve : reports/demo_rejection.json")

if __name__=="__main__":main()
