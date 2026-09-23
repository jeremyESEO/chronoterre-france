"""Règles explicites : chaque ligne invalide conserve toutes ses raisons."""
from collections import Counter
from datetime import date
import math
import unicodedata
from src.common import department_at

RULES = {
 "Q01": "Identifiants et nom de taxon obligatoires",
 "Q02": "Coordonnées WGS84 numériques finies dans leurs bornes",
 "Q03": "Point situé dans un département de la région 11",
 "Q04": "Âges numériques finis : 0 ≤ min_ma ≤ max_ma ≤ 4600",
 "Q05": "Publication identifiée et citation non vide",
 "Q06": "Exclusion des coordonnées basées seulement sur une unité politique",
 "Q07": "Absence de contradiction géographique connue ou de provenance inconnue",
 "Q08": "Températures finies : −90 ≤ min ≤ moyenne ≤ max ≤ 65 °C",
 "Q09": "Précipitation finie entre 0 et 1500 mm/j",
 "Q10": "Date ISO réelle et comprise dans la fenêtre demandée",
 "Q11": "Unicité de la clé métier dans le lot",
}

def normalize(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if c.isalnum())

def finite(x):
    try:
        return not isinstance(x, bool) and x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False

def positive_int(x):
    return str(x).isdigit() and int(x) > 0

def fossil_errors(row, collection, features, cfg):
    errors = []
    if not all(positive_int(row.get(k)) for k in ("occurrence_no", "collection_no")) or not row.get("identified_name") or not collection:
        errors.append("Q01")
    loc = collection or row
    lat, lon = loc.get("lat"), loc.get("lng")
    dep = None
    if not finite(lat) or not finite(lon) or not -90 <= float(lat) <= 90 or not -180 <= float(lon) <= 180:
        errors.append("Q02")
    else:
        dep = department_at(float(lon), float(lat), features)
        if not dep:
            errors.append("Q03")
    a, b = row.get("max_ma"), row.get("min_ma")
    if not finite(a) or not finite(b) or not 0 <= float(b) <= float(a) <= 4600:
        errors.append("Q04")
    if not positive_int(row.get("reference_no")) or not row.get("primary_reference", "").strip():
        errors.append("Q05")
    if loc.get("latlng_basis") == "based on political unit":
        errors.append("Q06")
    conflict = str(row.get("collection_no")) in cfg["excluded_collections"]
    # Départements déclarés : comparaison uniquement quand le libellé est reconnu.
    known = {normalize(f["properties"]["nom"]): f["properties"]["code"] for f in features}
    outside = {normalize(x) for x in ["Yonne","Oise","Eure","Eure-et-Loir","Eure-et-Loire","Aisne","Marne","Calvados","Picardie","Picardie Region","Haute-Normandie","Centre","Nord-Pas-de-Calais-Picardie"]}
    for name in (loc.get("state", ""), loc.get("county", "")):
        name = normalize(name.strip())
        if name in outside or (name in known and dep and known[name] != dep):
            conflict = True
    if conflict:
        errors.append("Q07")
    return errors, dep

def climate_errors(row, metadata):
    errors = []
    temps = [row.get(k) for k in ("tmin_c", "tmean_c", "tmax_c")]
    if not all(finite(x) for x in temps) or not -90 <= float(temps[0]) <= float(temps[1]) <= float(temps[2]) <= 65:
        errors.append("Q08")
    p = row.get("precipitation_mm")
    if not finite(p) or not 0 <= float(p) <= 1500:
        errors.append("Q09")
    try:
        day = date.fromisoformat(row["date"])
        if day.isoformat() != row["date"] or not metadata["start"] <= row["date"] <= metadata["end"]:
            errors.append("Q10")
    except (ValueError, TypeError, KeyError):
        errors.append("Q10")
    return errors

def profile(rows):
    """Profilage avant contrôle : types bruts, nulls, bornes, fréquences, doublons exacts."""
    import json
    fields = sorted({k for r in rows for k in r})
    result = {"rows": len(rows), "columns": len(fields), "fields": {}}
    for key in fields:
        values = [r.get(key) for r in rows]
        missing = sum(x is None or x == "" for x in values)
        valid = [x for x in values if x is not None and x != ""]
        numeric = [float(x) for x in valid if isinstance(x, (int,float)) and finite(x)]
        result["fields"][key] = {"types": dict(Counter(type(x).__name__ for x in valid)), "missing": missing, "missing_rate": round(missing/len(rows),6) if rows else 0, "min": min(numeric) if numeric else None, "max": max(numeric) if numeric else None, "top_values": Counter(str(x) for x in valid).most_common(5)}
    result["exact_duplicates"] = len(rows)-len({json.dumps(x, sort_keys=True) for x in rows})
    return result
