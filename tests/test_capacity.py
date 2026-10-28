import pandas as pd
from src.cpoe.capacity.planning import calculate_capacity_requirements

def test_capacity_requirement_is_above_footprint():
    idx = pd.date_range("2026-01-01", periods=2, freq="h")
    forecast = pd.DataFrame({"forecast_demand": [100, 110]}, index=idx)
    history = pd.DataFrame({"observed_gpu_capacity": [100, 100]}, index=idx)
    result, _, factor = calculate_capacity_requirements(forecast, history)
    assert factor > 1
    assert (result["required_capacity"] > result["forecast_demand"]).all()
