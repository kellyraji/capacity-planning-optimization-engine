import numpy as np
import pandas as pd

def add_forecast_signal(hourly: pd.DataFrame):
    result = hourly.copy()
    result["forecast_signal"] = result["observed_gpu_capacity"]
    return result

def seasonal_naive_validate(hourly, seasonal_period=24, validation_horizon=None):
    if len(hourly) <= seasonal_period * 2:
        raise ValueError(
            f"At least {seasonal_period * 2} hourly observations are required."
        )

    horizon = validation_horizon or min(24, len(hourly) // 5)
    train = hourly.iloc[:-horizon]
    test = hourly.iloc[-horizon:]

    predictions = []
    for timestamp in test.index:
        previous = timestamp - pd.Timedelta(hours=seasonal_period)
        if previous in train.index:
            prediction = train.loc[previous, "forecast_signal"]
        else:
            prediction = train["forecast_signal"].tail(seasonal_period).mean()
        predictions.append(float(prediction))

    validation = test[["forecast_signal"]].rename(columns={"forecast_signal": "actual"})
    validation["prediction"] = predictions
    validation["absolute_error"] = (validation["actual"] - validation["prediction"]).abs()
    validation["squared_error"] = (validation["actual"] - validation["prediction"]) ** 2

    metrics = pd.Series({
        "MAE": validation["absolute_error"].mean(),
        "RMSE": np.sqrt(validation["squared_error"].mean()),
        "validation_hours": len(validation),
    }, name="seasonal_naive")

    return validation, metrics

def forecast_next_period(hourly, seasonal_period=24, horizon=24):
    history = hourly["forecast_signal"]
    future_index = pd.date_range(
        start=hourly.index.max() + pd.Timedelta(hours=1),
        periods=horizon,
        freq="h",
    )

    values = []
    for timestamp in future_index:
        previous = timestamp - pd.Timedelta(hours=seasonal_period)
        if previous in history.index:
            prediction = history.loc[previous]
        else:
            prediction = history.tail(seasonal_period).mean()
        values.append(max(float(prediction), 0.0))

    return pd.DataFrame({"forecast_demand": values}, index=future_index)
