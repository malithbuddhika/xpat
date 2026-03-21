"""Data models used by the application."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Worker:
    work_permit_number: str
    passport_number: str
    worker_name: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    issued_date: Optional[str] = None
    permit_valid_till: Optional[str] = None
    work_site: Optional[str] = None
    verification_time: Optional[str] = None
    photo_url: Optional[str] = None
    error: Optional[str] = None
    last_verified: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Serialize worker to a dict for DataFrame output."""
        result = asdict(self)
        result["WorkPermitNumber"] = result.pop("work_permit_number")
        result["PassportNumber"] = result.pop("passport_number")
        result["WorkerName"] = result.pop("worker_name")
        result["Company"] = result.pop("company")
        result["Status"] = result.pop("status")
        result["IssuedDate"] = result.pop("issued_date")
        result["PermitValidTill"] = result.pop("permit_valid_till")
        result["WorkSite"] = result.pop("work_site")
        result["VerificationTime"] = result.pop("verification_time")
        result["WorkerPhotoURL"] = result.pop("photo_url")
        result["Error"] = result.pop("error")
        result["LastVerified"] = (
            self.last_verified.isoformat() if self.last_verified else None
        )
        return result
