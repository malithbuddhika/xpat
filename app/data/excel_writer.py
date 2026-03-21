"""Excel/CSV writing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from ..models.worker import Worker
from ..utils.config import OUTPUT_COLUMNS
from ..utils.logger import get_logger

logger = get_logger()


def _normalize_key(value: Optional[str]) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _map_workers_by_permit(workers: List[Worker]) -> Dict[str, Worker]:
    return {w.work_permit_number.strip().upper(): w for w in workers}


def export_to_excel(
    base_df: pd.DataFrame,
    workers: List[Worker],
    output_path: str,
    include_index: bool = False,
) -> None:
    """Export results to a new Excel file."""
    df = base_df.copy()
    mapping = _map_workers_by_permit(workers)

    for col in OUTPUT_COLUMNS:
        df[col] = ""

    for idx, row in df.iterrows():
        key = _normalize_key(row.get("WorkPermitNumber"))
        if not key:
            continue
        worker = mapping.get(key)
        if not worker:
            continue
        df.at[idx, "WorkerName"] = worker.worker_name or ""
        df.at[idx, "Company"] = worker.company or ""
        df.at[idx, "Status"] = worker.status or ""
        df.at[idx, "IssuedDate"] = worker.issued_date or ""
        df.at[idx, "PermitValidTill"] = worker.permit_valid_till or ""
        df.at[idx, "WorkSite"] = worker.work_site or ""
        df.at[idx, "VerificationTime"] = worker.verification_time or ""
        df.at[idx, "WorkerPhotoURL"] = worker.photo_url or ""

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.suffix.lower() == ".csv":
        df.to_csv(output_file, index=include_index)
    else:
        df.to_excel(output_file, engine="openpyxl", index=include_index)

    logger.info("Exported results to %s", output_file)
