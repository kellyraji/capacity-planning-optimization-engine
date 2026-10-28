import pandas as pd
from src.cpoe.data.validation import validate_hourly_series, hourly_completeness

def test_hourly_validation():
    idx = pd.date_range("2026-01-01", periods=3, freq="h")
    df = pd.DataFrame({
        "observed_gpu_capacity": [8, 16, 24],
        "observed_cpu_capacity": [32, 64, 96],
        "active_servers": [1, 2, 3],
        "active_clusters": [1, 1, 2],
    }, index=idx)
    assert validate_hourly_series(df) is True
    assert hourly_completeness(df)["missing_hours"] == 0
