from datetime import timedelta
import os

# ========================================
# Configuration
# ========================================

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": True,  # Don't run if previous month failed
    "email_on_failure": True,
    "email_on_retry": False,
    "email": os.getenv("ALERT_EMAIL"),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

# Data quality thresholds
MIN_ROWS_PER_MONTH = 10000  # Minimum expected rows
MAX_ROWS_PER_MONTH = 10000000  # Maximum expected rows
MIN_FILE_SIZE_MB = 10
MAX_FILE_SIZE_MB = 500