import numpy as np
import pandas as pd

DEFAULT_PLANNING = {
    "target_utilization": 0.70,
    "usable_capacity_factor": 0.90,
    "safety_buffer": 0.10,
    "gpus_per_new_server": 8,
}

def validate_planning_parameters(params):
    if not 0 < params["target_utilization"] <= 1:
        raise ValueError("target_utilization must be between 0 and 1.")
    if not 0 < params["usable_capacity_factor"] <= 1:
        raise ValueError("usable_capacity_factor must be between 0 and 1.")
    if not 0 <= params["safety_buffer"] < 1:
        raise ValueError("safety_buffer must be between 0 and 1.")
    if params["gpus_per_new_server"] <= 0:
        raise ValueError("gpus_per_new_server must be positive.")

def calculate_capacity_requirements(forecast, history, params=None):
    params = params or DEFAULT_PLANNING.copy()
    validate_planning_parameters(params)

    baseline = float(history["observed_gpu_capacity"].iloc[-1])
    planning_factor = (
        (1 + params["safety_buffer"])
        / (params["target_utilization"] * params["usable_capacity_factor"])
    )

    result = forecast.copy()
    result["required_capacity"] = result["forecast_demand"] * planning_factor
    result["baseline_capacity"] = baseline
    result["headroom"] = result["baseline_capacity"] - result["required_capacity"]
    result["additional_capacity"] = result["required_capacity"] - result["baseline_capacity"]
    result["planning_utilization"] = (
        result["forecast_demand"] / result["baseline_capacity"]
    )

    result["additional_servers"] = np.ceil(
        result["additional_capacity"].clip(lower=0)
        / params["gpus_per_new_server"]
    ).astype(int)

    result["risk_flag"] = np.select(
        [
            result["planning_utilization"] >= 0.90,
            result["planning_utilization"] >= 0.80,
        ],
        ["HIGH", "MEDIUM"],
        default="LOW",
    )

    summary = pd.Series({
        "peak_forecast_demand": result["forecast_demand"].max(),
        "peak_required_capacity": result["required_capacity"].max(),
        "minimum_headroom": result["headroom"].min(),
        "hours_negative_headroom": int((result["headroom"] < 0).sum()),
        "hours_high_risk": int((result["risk_flag"] == "HIGH").sum()),
        "max_additional_capacity": result["additional_capacity"].max(),
    }, name="value")

    return result, summary, planning_factor
