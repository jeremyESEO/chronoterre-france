"""Fonctions partagées sans dépendance tierce."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import os

ROOT = Path(__file__).resolve().parents[1]

def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, path)

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def settings(path=None):
    return read_json(path or ROOT / "config/settings.json")

def inside_ring(lon, lat, ring):
    inside = False
    j = len(ring) - 1
    for i, (x, y, *_) in enumerate(ring):
        xj, yj = ring[j][:2]
        if (y > lat) != (yj > lat) and lon < (xj-x)*(lat-y)/(yj-y)+x:
            inside = not inside
        j = i
    return inside

def inside_geometry(lon, lat, geometry):
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    return any(inside_ring(lon, lat, p[0]) and not any(inside_ring(lon, lat, h) for h in p[1:]) for p in polygons)

def department_at(lon, lat, features):
    for f in features:
        if inside_geometry(lon, lat, f["geometry"]):
            return f["properties"]["code"]
    return None

def haversine(lat1, lon1, lat2, lon2):
    r = math.pi / 180
    a = math.sin((lat2-lat1)*r/2)**2 + math.cos(lat1*r)*math.cos(lat2*r)*math.sin((lon2-lon1)*r/2)**2
    return 6371 * 2 * math.asin(min(1, math.sqrt(a)))
