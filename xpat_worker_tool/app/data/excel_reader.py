"""Excel reading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
import re

import pandas as pd

from ..models.worker import Worker
from ..utils.config import REQUIRED_INPUT_COLUMNS
from ..utils.logger import get_logger

logger = get_logger()


def _sanitize_column_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def load_workers_from_excel(file_path: str) -> Tuple[pd.DataFrame, List[Worker]]:
    """Load workers from an Excel file.

    Returns the raw DataFrame and a list of Worker models with sanitized inputs.
    """

    path = Path(file_path)
    xls = pd.read_excel(
        path,
        engine="openpyxl",
        dtype=str,
        keep_default_na=False,
    )

    # Normalize incoming column names by removing non-alphanumeric characters
    # and mapping common header variants to canonical names.
    def _resolve_column_name(col: object) -> str:
        normalized = re.sub(r"\W+", "", str(col)).strip().lower()
        if normalized in {"workpermitnumber", "workpermit", "workpermitno", "permitnumber", "permit"}:
            return "WorkPermitNumber"
        if normalized in {"passportnumber", "passport", "passportno", "passno"}:
            return "PassportNumber"
        return str(col)

    norm_map = {col: _resolve_column_name(col) for col in xls.columns}
    df = xls.copy()
    df = df.rename(columns=norm_map)

    missing = [c for c in REQUIRED_INPUT_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Excel is missing required columns: {missing}")

    workers: List[Worker] = []
    for _, row in df.iterrows():
        work_permit = _sanitize_column_value(row.get("WorkPermitNumber"))
        passport = _sanitize_column_value(row.get("PassportNumber"))

        # Check if required fields are empty
        has_missing_data = not work_permit or not passport

        workers.append(Worker(
            work_permit_number=work_permit or "NO DATA",
            passport_number=passport or "NO DATA",
            missing_data=has_missing_data,
        ))

    logger.info("Loaded %s workers from %s", len(workers), file_path)
    return df, workers
