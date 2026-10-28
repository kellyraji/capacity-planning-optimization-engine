
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA = PROJECT_ROOT / "data"
PROCESSED = DATA / "processed"

# Output directories
OUTPUTS = PROJECT_ROOT / "outputs"
FIGURES = OUTPUTS / "figures"

# Source database
SOURCE_DB = DATA / "source.duckdb"
SERVER_DATASET = SOURCE_DB

# Forecasting configuration
SYNTHETIC_TRACE_ANCHOR = "2026-01-01"
SEASONAL_PERIOD_HOURS = 24
FORECAST_HORIZON_HOURS = 24

# Ensure required directories exist
for path in (PROCESSED, FIGURES):
    path.mkdir(parents=True, exist_ok=True)
