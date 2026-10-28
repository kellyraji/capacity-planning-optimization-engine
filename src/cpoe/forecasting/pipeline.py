
from pathlib import Path

import numpy as np
import pandas as pd

from cpoe.data.loader import build_hourly_capacity_footprint


def run_forecast_pipeline(
    server_path,
    processed_dir,
    horizon=24,
    validation_hours=24,
):
    """
    Forecast the observed GPU capacity footprint using a 24-hour
    seasonal-naive benchmark.

    Important: this forecasts observed capacity, not workload demand
    or GPU utilization.
    """
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    if horizon < 1:
        raise ValueError("horizon must be at least 1.")

    if validation_hours < 1:
        raise ValueError("validation_hours must be at least 1.")

    # Build the historical capacity footprint.
    hourly = build_hourly_capacity_footprint(Path(server_path))

    if "observed_gpu_capacity" not in hourly.columns:
        raise ValueError(
            "Missing observed_gpu_capacity in hourly capacity data."
        )

    if hourly.empty:
        raise ValueError("The hourly capacity dataset is empty.")

    # Ensure timestamps are usable.
    if "trace_timestamp" in hourly.columns:
        hourly["trace_timestamp"] = pd.to_datetime(
            hourly["trace_timestamp"], errors="coerce"
        )
        hourly = hourly.set_index("trace_timestamp")

    if not isinstance(hourly.index, pd.DatetimeIndex):
        raise ValueError(
            "Hourly data must have a DatetimeIndex or a "
            "'trace_timestamp' column."
        )

    hourly = hourly.sort_index()

    # Clean and aggregate the capacity signal at hourly frequency.
    hourly["observed_gpu_capacity"] = pd.to_numeric(
        hourly["observed_gpu_capacity"], errors="coerce"
    )

    hourly["observed_gpu_capacity"] = (
        hourly["observed_gpu_capacity"]
        .replace([np.inf, -np.inf], np.nan)
    )

    series = hourly["observed_gpu_capacity"].dropna()

    if series.empty:
        raise ValueError("No valid GPU capacity observations were found.")

    # Aggregate duplicate timestamps and insert missing hours.
    series = series.groupby(level=0).mean().sort_index()

    series = series.resample("h").mean()

    # Do not silently treat missing hours as zero capacity.
    # Interpolate only short gaps; fail if longer gaps remain.
    series = series.interpolate(
        method="time",
        limit=2,
        limit_area="inside",
    )

    if series.isna().any():
        missing_count = int(series.isna().sum())
        raise ValueError(
            f"The hourly series contains {missing_count} missing values "
            "after short-gap interpolation. Inspect the trace timestamps "
            "or define a justified missing-data policy before forecasting."
        )

    series = series.clip(lower=0)

    if len(series) < 48:
        raise ValueError(
            "At least 48 hourly observations are required for "
            "24-hour seasonal forecasting and validation."
        )

    # ---------------------------------------------------------
    # 1. Out-of-sample validation
    # ---------------------------------------------------------
    validation_hours = min(validation_hours, len(series) // 3)

    validation_start = len(series) - validation_hours

    actual = series.iloc[validation_start:]

    # Compare each observation with the same hour 24 hours earlier.
    prediction_start = validation_start - 24
    prediction_end = prediction_start + validation_hours

    validation_predictions = series.iloc[
        prediction_start:prediction_end
    ]

    if len(validation_predictions) != len(actual):
        raise ValueError(
            "Insufficient history for seasonal-naive validation."
        )

    actual_values = actual.to_numpy(dtype=float)
    predicted_values = validation_predictions.to_numpy(dtype=float)

    errors = actual_values - predicted_values

    metrics = pd.DataFrame([{
        "validation_observations": len(errors),
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors ** 2))),
    }])

    validation = pd.DataFrame(
        {
            "actual_capacity": actual_values,
            "forecast_capacity": predicted_values,
            "absolute_error": np.abs(errors),
        },
        index=actual.index,
    )
    validation.index.name = "trace_timestamp"

    # ---------------------------------------------------------
    # 2. Forecast the next horizon hours
    # ---------------------------------------------------------
    last_timestamp = series.index.max()

    future_index = pd.date_range(
        start=last_timestamp + pd.Timedelta(hours=1),
        periods=horizon,
        freq="h",
    )

    # Repeat the previous day's observed capacity pattern.
    forecast_values = series.reindex(
        future_index - pd.Timedelta(hours=24)
    )

    # For horizons longer than the available daily history,
    # use the latest observed value as a transparent fallback.
    forecast_values = forecast_values.fillna(float(series.iloc[-1]))
    forecast_values = forecast_values.clip(lower=0)

    forecast = pd.DataFrame(
        {"forecast_demand": forecast_values.to_numpy(dtype=float)},
        index=future_index,
    )
    forecast.index.name = "trace_timestamp"

    # ---------------------------------------------------------
    # 3. Capacity planning assumptions
    # ---------------------------------------------------------
    target_utilization = 0.70
    usable_capacity_factor = 0.90
    safety_buffer = 0.10

    planning_factor = (
        (1 + safety_buffer)
        / (target_utilization * usable_capacity_factor)
    )

    forecast["required_capacity"] = (
        forecast["forecast_demand"] * planning_factor
    )

    baseline_capacity = float(series.iloc[-1])

    forecast["baseline_capacity"] = baseline_capacity

    forecast["headroom"] = (
        baseline_capacity - forecast["required_capacity"]
    )

    forecast["additional_capacity"] = (
        forecast["required_capacity"] - baseline_capacity
    ).clip(lower=0)

    # ---------------------------------------------------------
    # 4. Save outputs for downstream pipeline stages
    # ---------------------------------------------------------
    hourly.to_csv(processed_dir / "hourly_capacity_footprint.csv")
    validation.to_csv(
        processed_dir / "forecast_validation_detail.csv"
    )
    metrics.to_csv(
        processed_dir / "forecast_validation.csv",
        index=False,
    )
    forecast.to_csv(processed_dir / "workload_forecast.csv")

    summary = pd.DataFrame([{
        "historical_hours": len(series),
        "historical_peak_capacity": float(series.max()),
        "historical_mean_capacity": float(series.mean()),
        "forecast_peak_capacity": float(forecast["forecast_demand"].max()),
        "peak_required_capacity": float(forecast["required_capacity"].max()),
        "baseline_capacity": baseline_capacity,
        "planning_factor": planning_factor,
    }])

    summary.to_csv(
        processed_dir / "forecast_summary.csv",
        index=False,
    )

    print("\n=== FORECAST VALIDATION ===")
    print(metrics.to_string(index=False))

    print("\n=== FORECAST SUMMARY ===")
    print(summary.to_string(index=False))

    return {
        "hourly": hourly,
        "forecast": forecast,
        "metrics": metrics,
        "summary": summary,
    }
