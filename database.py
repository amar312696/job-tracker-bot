import json
import os
import time
from typing import Set, Dict


class JobDatabase:
    def __init__(self, filepath: str = "seen_jobs.json", retention_days: int = 60):
        self.filepath = filepath
        self.retention_seconds = retention_days * 86400
        self.data: Dict[str, float] = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def is_seen(self, job_id: str) -> bool:
        return job_id in self.data

    def mark_seen(self, job_id: str):
        self.data[job_id] = time.time()

    def save(self):
        # Prune entries older than retention period
        cutoff = time.time() - self.retention_seconds
        pruned_data = {jid: ts for jid, ts in self.data.items() if ts >= cutoff}
        self.data = pruned_data

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
