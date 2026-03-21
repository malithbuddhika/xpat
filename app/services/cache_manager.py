"""Simple disk-backed cache for verified workers."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from ..models.worker import Worker
from ..utils.config import CACHE_DIR, CACHE_FILE
from ..utils.logger import get_logger

logger = get_logger()


class CacheManager:
    """A minimal JSON cache to avoid re-verifying the same permits."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._cache: Dict[str, Dict] = {}
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._load_cache()

    def _load_cache(self) -> None:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to load cache: %s", exc)
                self._cache = {}

    def get(self, work_permit_number: str) -> Optional[Worker]:
        key = work_permit_number.strip().upper()
        entry = self._cache.get(key)
        if not entry:
            return None
        try:
            worker = Worker(
                work_permit_number=key,
                passport_number=entry.get("passport_number", ""),
                worker_name=entry.get("worker_name"),
                company=entry.get("company"),
                status=entry.get("status"),
                issued_date=entry.get("issued_date"),
                permit_valid_till=entry.get("permit_valid_till"),
                work_site=entry.get("work_site"),
                photo_url=entry.get("photo_url"),
                verification_time=entry.get("verification_time"),
            )
            return worker
        except Exception:
            return None

    def set(self, worker: Worker) -> None:
        key = worker.work_permit_number.strip().upper()
        with self._lock:
            self._cache[key] = {
                "passport_number": worker.passport_number,
                "worker_name": worker.worker_name,
                "company": worker.company,
                "status": worker.status,
                "issued_date": worker.issued_date,
                "permit_valid_till": worker.permit_valid_till,
                "work_site": worker.work_site,
                "photo_url": worker.photo_url,
                "verification_time": worker.verification_time,
            }
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(self._cache, f, ensure_ascii=False, indent=2)
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to write cache: %s", exc)
