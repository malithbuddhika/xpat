"""Excel reading helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

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
    xls = pd.read_excel(path, engine="openpyxl", dtype=str, keep_default_na=False)

    def _resolve_column_name(col: object) -> str:
        raw = str(col).strip()
        normalized = re.sub(r"[^A-Za-z0-9]", "", raw).lower()
        if any(token in normalized for token in ["workpermitnumber", "workpermit", "workpermitno", "permitnumber", "permit"]):
            return "WorkPermitNumber"
        if any(token in normalized for token in ["passportnumber", "passport", "passportno", "passno"]):
            return "PassportNumber"
        return raw

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

        workers.append(Worker(
            work_permit_number=work_permit,
            passport_number=passport,
        ))

    logger.info("Loaded %s workers from %s", len(workers), file_path)
    return df, workers
