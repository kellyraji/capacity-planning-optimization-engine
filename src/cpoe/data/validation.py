import pandas as pd

def validate_hourly_series(hourly: pd.DataFrame):
    required = [
        "observed_gpu_capacity",
        "observed_cpu_capacity",
        "active_servers",
        "active_clusters",
    ]
    missing = [c for c in required if c not in hourly.columns]
    if missing:
        raise ValueError(f"Hourly capacity data missing: {missing}")

    if hourly.index.duplicated().any():
        raise ValueError("Hourly capacity index contains duplicate timestamps.")

    if not hourly.index.is_monotonic_increasing:
        raise ValueError("Hourly capacity index must be sorted.")

    return True

def hourly_completeness(hourly: pd.DataFrame):
    expected = pd.date_range(hourly.index.min(), hourly.index.max(), freq="h")
    missing = expected.difference(hourly.index)
    return {
        "expected_hours": len(expected),
        "observed_hours": len(hourly),
        "missing_hours": len(missing),
    }
