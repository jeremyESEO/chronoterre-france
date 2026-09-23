"""Exécute les 15 analyses SQL et conserve leurs résultats calculés."""
import json
import sqlite3
import sys
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import ROOT,write_json,utcnow
from src.transform import query

def main():
    db=sqlite3.connect((ROOT/"data/curated/chronoterre.sqlite").as_uri()+"?mode=ro",uri=True)
    db.row_factory=sqlite3.Row
    queries=(ROOT/"sql/analyses.sql").read_text(encoding="utf-8").split(";")
    # Les commentaires peuvent contenir ';' : sqlite3.complete_statement assure le découpage.
    statements=[];buffer=''
    for line in (ROOT/"sql/analyses.sql").read_text(encoding="utf-8").splitlines(True):
        buffer+=line
        if sqlite3.complete_statement(buffer):statements.append(buffer);buffer=''
    results=[]
    for statement in statements:
        title=next(line[3:] for line in statement.splitlines() if line.startswith('-- Q'))
        rows=query(db,statement)
        results.append({"question":title,"rows":len(rows),"results":rows})
    write_json(ROOT/"reports/sql_results.json",{"executed_at":utcnow(),"queries":results})
    db.close();print(f"{len(results)} analyses SQL exécutées → reports/sql_results.json")

if __name__=="__main__":main()
