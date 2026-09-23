"""Collecteur API. Sauvegarde les octets HTTP avant toute transformation.

Les réponses horodatées ne sont jamais modifiées. Les entrées existantes sont
vérifiées par SHA-256 et réutilisées, sauf --refresh. Aucun secret nécessaire.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import ROOT, read_json, settings, sha256, utcnow, write_json

def collect(config=None, refresh=False):
    cfg = config or settings()
    rawdir = ROOT / "data/raw"
    rawdir.mkdir(parents=True, exist_ok=True)
    pointer = rawdir / "manifest.json"
    old = read_json(pointer).get("files", {}) if pointer.exists() else {}
    files = {}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    def fetch(key, source, url, metadata=None):
        prior = old.get(key)
        if not refresh and prior and prior["url"] == url:
            b = (ROOT / prior["path"]).read_bytes()
            if sha256(b) != prior["sha256"]:
                raise ValueError(f"Intégrité raw compromise : {prior['path']}")
            files[key] = prior
            print(f"CACHE {key}", flush=True)
            return json.loads(b)
        for attempt in range(cfg["retries"]):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "ChronoTerre-ESEO/1.0 (academic data collector)", "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=cfg["timeout_seconds"]) as response:
                    body = response.read()
                    content_type = response.headers.get("Content-Type", "")
                path = rawdir / f"{stamp}_{key}_a{attempt+1}.json"
                with path.open("xb") as output:
                    output.write(body)
                obj = json.loads(body)  # parsing seulement après conservation exacte
                if isinstance(obj, dict) and (obj.get("error") or obj.get("errors") or obj.get("warnings")):
                    raise ValueError(f"Erreur/avertissement source {key}: {str(obj)[:400]}")
                files[key] = {"key": key, "source": source, "url": url, "path": str(path.relative_to(ROOT)), "sha256": sha256(body), "bytes": len(body), "fetched_at": utcnow(), "content_type": content_type, "metadata": metadata or {}}
                # Checkpoint : permet une reprise après une indisponibilité réseau.
                write_json(pointer, {"version": 1, "files": {**old, **files}})
                print(f"COLLECTE {key}: {len(body):,} octets", flush=True)
                if source in ("archive", "climate"):
                    time.sleep(cfg.get("request_interval_seconds", 15))
                return obj
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
                if attempt + 1 == cfg["retries"]:
                    raise RuntimeError(f"Source indisponible ({key}). Raw antérieur conservé. Relancer ou utiliser --offline. {error}") from error
                wait = max(2 ** attempt, 30 if getattr(error, "code", None) == 429 else 0)
                time.sleep(wait)

    fetch("departments", "etalab", cfg["endpoints"]["departments"])
    cities = fetch("cities", "geoapi", cfg["endpoints"]["cities"])
    params = {**cfg["bbox"], "vocab": "pbdb", "limit": "all"}
    fetch("collections", "pbdb", cfg["endpoints"]["pbdb"] + "colls/list.json?" + urllib.parse.urlencode({**params, "show": "loc,env,ref,rem,strat"}))
    fetch("occurrences", "pbdb", cfg["endpoints"]["pbdb"] + "occs/list.json?" + urllib.parse.urlencode({**params, "show": "coords,loc,env,ref,classext"}))
    selected = {c["code"]: c for c in cities if c["code"] in cfg["city_codes"]}
    if set(selected) != set(cfg["city_codes"]):
        raise ValueError(f"Communes introuvables : {set(cfg['city_codes']) - set(selected)}")
    for code in cfg["city_codes"]:
        city = selected[code]
        if city["codeDepartement"] not in cfg["departments"]:
            raise ValueError(f"Commune hors Île-de-France : {code}")
        lon, lat = city["centre"]["coordinates"]
        for kind, model, period in [("baseline", cfg["baseline_model"], cfg["baseline"])] + [("future", m, cfg["future"]) for m in cfg["models"]]:
            query = {"latitude": lat, "longitude": lon, "start_date": period[0], "end_date": period[1], "models": model, "daily": ",".join(cfg["daily_variables"]), "timezone": "GMT"}
            url = cfg["endpoints"]["archive" if kind == "baseline" else "climate"] + "?" + urllib.parse.urlencode(query)
            fetch(f"{code}_{model}", "archive" if kind == "baseline" else "climate", url, {"city_code": code, "model": model, "kind": kind, "start": period[0], "end": period[1], "requested_lat": lat, "requested_lon": lon})
    manifest = {"version": 1, "created_at": utcnow(), "configuration_sha256": sha256(json.dumps(cfg, sort_keys=True).encode()), "files": files}
    write_json(rawdir / f"manifest_{stamp}.json", manifest)
    write_json(pointer, manifest)
    return manifest

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--config", type=Path)
    args = p.parse_args()
    try:
        collect(settings(args.config), args.refresh)
    except Exception as e:
        print(f"ÉCHEC : {e}", file=sys.stderr)
        raise SystemExit(1)
