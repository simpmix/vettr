import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# SEC EDGAR Requirements:
# The SEC requires a specific User-Agent format: 'OrganizationName contact@domain.com'
# Ref: https://www.sec.gov/os/accessing-edgar-data
SEC_USER_AGENT = os.getenv("VETTR_SEC_USER_AGENT", "VettrResearchTerminal admin@vettr-terminal.io")

# API Configuration
SERVER_HOST = os.getenv("VETTR_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("VETTR_PORT", "8000"))

# Request headers for SEC requests
SEC_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

# Request headers for standard SEC www endpoints (ticker list, etc.)
SEC_WWW_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
}
