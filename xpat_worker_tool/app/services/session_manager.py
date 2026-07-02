"""Session management for XPAT HTTP requests."""

from __future__ import annotations

import threading
from typing import Optional

import requests

from ..utils.config import REQUEST_HEADERS
from ..utils.logger import get_logger

logger = get_logger()


class SessionManager:
    """Maintains a shared requests.Session with required headers and cookies."""

    _instance: Optional["SessionManager"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self._last_refresh = None

    @classmethod
    def get_instance(cls) -> "SessionManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def refresh(self) -> None:
        """Refresh session cookies by hitting the XPAT home page.

        This helps keep the ASP.NET session alive.
        """
        url = "https://xpat.egov.mv/"
        try:
            logger.debug("Refreshing XPAT session cookies")
            self.session.get(url, timeout=10)
            self._last_refresh = True
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to refresh session cookies: %s", exc)

    def get_session(self) -> requests.Session:
        return self.session
