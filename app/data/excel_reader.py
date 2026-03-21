"""Excel reading helpers."""

from __future__ import annotations

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
    xls = pd.read_excel(path, engine="openpyxl")

    missing = [c for c in REQUIRED_INPUT_COLUMNS if c not in xls.columns]
    if missing:
        raise ValueError(f"Excel is missing required columns: {missing}")

    df = xls.copy()
    df = df.rename(columns={c: c.strip() for c in df.columns})

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
