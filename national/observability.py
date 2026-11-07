"""Identifiants d'exécution et contrôle de l'âge des acquisitions, sans appel réseau."""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from uuid import uuid4

from national.collect import dump


class Run:
    def __init__(self, root: Path):
        self.root = root
        self.started = datetime.now(timezone.utc)
        self.clock = monotonic()
        self.run_id = f"{self.started:%Y%m%dT%H%M%SZ}-{uuid4().hex[:12]}"
        self.contract_version = None
        self.stages = []
        self.raw_verified = 0

    def step(self, name):
        self.stages.append({"name": name, "elapsed_seconds": round(monotonic() - self.clock, 2)})
        print(f"[{self.run_id}] {name}", flush=True)

    def metadata(self):
        return {
            "pipeline": "ChronoTerre France",
            "run_id": self.run_id,
            "contract_version": self.contract_version,
            "started_at": self.started.isoformat(),
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(monotonic() - self.clock, 2),
            "stages": self.stages.copy(),
            "raw_verified": self.raw_verified,
        }

    def save(self, report):
        dump(self.root / "reports" / "runs" / f"{self.run_id}.json", report)

    def failure(self, error):
        report = self.metadata()
        report.update(
            status="FAIL",
            stage=self.stages[-1]["name"] if self.stages else "initialisation",
            error={"type": type(error).__name__, "message": str(error)[:500]},
        )
        self.save(report)
        print(f"[{self.run_id}] Échec à {report['stage']} : {report['error']['message']}", flush=True)


def acquisition_freshness(files, policies, as_of):
    """La fraîcheur de collecte ne mesure pas le millésime du phénomène."""
    groups = defaultdict(list)
    for key, entry in files.items():
        groups[entry["source"]].append((key, entry.get("fetched_at")))
    result = {}
    for source, entries in sorted(groups.items()):
        dates, invalid = [], []
        for key, stamp in entries:
            try:
                date = datetime.fromisoformat(stamp)
                if date.tzinfo is None or date > as_of:
                    raise ValueError("horodatage sans fuseau ou futur")
                dates.append(date)
            except (ValueError, TypeError):
                invalid.append(key)
        days = (as_of - min(dates)).days if dates else None
        limit = policies.get(source, {}).get("review_after_days")
        result[source] = {
            "raw_files": len(entries),
            "oldest_acquired_at": min(dates).isoformat() if dates else None,
            "latest_acquired_at": max(dates).isoformat() if dates else None,
            "max_acquisition_age_days": days,
            "review_after_days": limit,
            "invalid_raw_timestamps": invalid,
            "status": "INVALID_TIMESTAMP" if invalid else "NO_POLICY" if limit is None
                      else "REVIEW_DUE" if days > limit else "WITHIN_POLICY",
        }
    return result
