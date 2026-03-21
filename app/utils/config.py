"""Application configuration constants."""

from pathlib import Path

# XPAT verification endpoint
XPAT_VERIFY_URL = "https://xpat.egov.mv/EmploymentApproval/EmploymentApproval/WorkPermitVerify"

# Request defaults
REQUEST_TIMEOUT = 10  # seconds
REQUEST_RETRIES = 3
REQUEST_HEADERS = {
    "Origin": "https://xpat.egov.mv",
    "Referer": "https://xpat.egov.mv/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Threading and performance
MAX_WORKERS = 8
RATE_LIMIT_SECONDS = 0.2  # Pause between requests to avoid server blocking

# Paths
ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"
CACHE_DIR = ROOT_DIR / "cache"
CACHE_FILE = CACHE_DIR / "verified_cache.json"

# UI
APP_NAME = "XPAT Worker Automation Tool"

# Excel
REQUIRED_INPUT_COLUMNS = ["WorkPermitNumber", "PassportNumber"]
OUTPUT_COLUMNS = [
    "WorkerName",
    "Company",
    "Status",
    "IssuedDate",
    "PermitValidTill",
    "WorkSite",
    "VerificationTime",
    "WorkerPhotoURL",
]
