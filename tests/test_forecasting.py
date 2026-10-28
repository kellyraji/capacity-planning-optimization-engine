import pandas as pd
from src.cpoe.forecasting.models import forecast_next_period

def test_forecast_horizon():
    idx = pd.date_range("2026-01-01", periods=72, freq="h")
    df = pd.DataFrame({"forecast_signal": range(72)}, index=idx)
    result = forecast_next_period(df, seasonal_period=24, horizon=24)
    assert len(result) == 24
    assert result["forecast_demand"].notna().all()
