"""Client for interacting with the XPAT verification endpoint."""

from __future__ import annotations

import re
import time
from datetime import datetime
from threading import Event
from typing import Optional

import requests

from .cache_manager import CacheManager
from .html_parser import parse_verification_html
from .session_manager import SessionManager
from ..models.worker import Worker
from ..utils.config import REQUEST_RETRIES, REQUEST_TIMEOUT, RATE_LIMIT_SECONDS, XPAT_VERIFY_URL
from ..utils.logger import get_logger

logger = get_logger()


def _sanitize_input(value: str, allow_digits: bool = True) -> str:
    """Sanitize a string to prevent injection into HTTP payload."""
    if not value:
        return ""

    allowed_re = r"[^A-Za-z0-9]" if allow_digits else r"[^A-Za-z]"
    cleaned = re.sub(allowed_re, "", value).strip()
    return cleaned


class XpatClient:
    """Performs XPAT work permit verification."""

    def __init__(self) -> None:
        self.session_manager = SessionManager.get_instance()
        self.cache = CacheManager()

    def verify_worker(
        self,
        work_permit_number: str,
        passport_number: str,
        stop_event: Optional[Event] = None,
    ) -> Worker:
        """Verify a single worker and return updated Worker model."""

        work_permit_number = _sanitize_input(work_permit_number)
        passport_number = _sanitize_input(passport_number)

        worker = Worker(
            work_permit_number=work_permit_number,
            passport_number=passport_number,
        )

        if not work_permit_number:
            worker.error = "Invalid work permit number"
            return worker

        cached = self.cache.get(work_permit_number)
        if cached:
            logger.info("Cache hit %s", work_permit_number)
            cached.last_verified = datetime.utcnow()
            cached.verification_time = datetime.utcnow().isoformat()
            return cached

        session = self.session_manager.get_session()
        self.session_manager.refresh()

        data = {
            "workPermitNumber": work_permit_number,
            "firstName": passport_number,
        }

        last_error: Optional[str] = None
        for attempt in range(1, REQUEST_RETRIES + 1):
            if stop_event and stop_event.is_set():
                worker.error = "Stopped by user"
                return worker

            try:
                logger.debug("Posting verification for %s (attempt %s)", work_permit_number, attempt)
                response = session.post(
                    XPAT_VERIFY_URL,
                    data=data,
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()

                parsed = parse_verification_html(response.text)
                worker.worker_name = parsed.get("worker_name")
                worker.passport_number = parsed.get("passport_number") or passport_number
                worker.company = parsed.get("company")
                worker.status = parsed.get("status")
                worker.issued_date = parsed.get("issued_date")
                worker.permit_valid_till = parsed.get("permit_valid_till")
                worker.work_site = parsed.get("work_site")
                worker.photo_url = parsed.get("photo_url")
                worker.verification_time = datetime.utcnow().isoformat()
                worker.last_verified = datetime.utcnow()

                if not worker.worker_name and not worker.status:
                    last_error = "Unexpected HTML format"
                    logger.warning("Could not extract fields for %s - Response status: %s", work_permit_number, response.status_code)
                    logger.debug("Response HTML snippet: %s", response.text[:500])
                else:
                    self.cache.set(worker)
                    logger.info("Worker verified %s", work_permit_number)
                    return worker

            except requests.RequestException as exc:
                last_error = f"Network error: {exc}"
                logger.error("Network error verifying %s: %s", work_permit_number, exc)

            except Exception as exc:  # pragma: no cover
                last_error = f"Unexpected error: {exc}"
                logger.exception("Unexpected error verifying %s", work_permit_number)

            time.sleep(RATE_LIMIT_SECONDS)

        worker.error = last_error or "Verification failed"
        return worker
