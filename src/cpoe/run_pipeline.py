
from pathlib import Path

from cpoe.config import PROCESSED, SERVER_DATASET
from cpoe.forecasting.pipeline import run_forecast_pipeline
from cpoe.capacity.planning import calculate_capacity_requirements
from cpoe.optimization.model import optimize_capacity
from cpoe.simulation.scenarios import run_scenario_simulation


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # 1. Forecast the observed capacity footprint.
    forecast_results = run_forecast_pipeline(
        server_path=SERVER_DATASET,
        processed_dir=PROCESSED,
        horizon=24,
    )

    # 2. Convert the forecast into capacity requirements.
    capacity, capacity_summary, planning_factor = (
        calculate_capacity_requirements(
            forecast_results["forecast"],
            forecast_results["hourly"],
        )
    )

    capacity.to_csv(PROCESSED / "capacity_requirements.csv")
    capacity_summary.to_csv(PROCESSED / "capacity_summary.csv")

    # 3. Optimize server additions.
    solution = optimize_capacity(
        capacity_data=capacity,
        output_dir=PROCESSED,
    )

    solution.to_csv(PROCESSED / "optimization_solution.csv")

    optimization_summary = {
        "total_new_servers": int(solution["new_servers"].sum()),
        "peak_available_capacity": float(
            solution["available_capacity"].max()
        ),
        "minimum_headroom": float(solution["headroom"].min()),
        "total_shortage": float(solution["shortage"].sum()),
        "total_modeled_cost": float(
            solution["total_period_cost"].sum()
        ),
    }

    import pandas as pd

    pd.Series(optimization_summary, name="value").to_csv(
        PROCESSED / "optimization_summary.csv"
    )

    # 4. Run deterministic scenarios and Monte Carlo risk analysis.
    simulation_results = run_scenario_simulation(
        capacity_requirements=capacity,
        optimization_solution=solution,
        output_dir=PROCESSED,
        simulations=5000,
        seed=42,
    )

    print("\n=== CPOE PIPELINE COMPLETE ===")

    print("\nForecast validation:")
    print(forecast_results["metrics"].to_string(index=False))

    print("\nCapacity planning:")
    print(capacity_summary)

    print("\nOptimization:")
    print(pd.Series(optimization_summary))

    print("\nDeterministic scenarios:")
    print(simulation_results["scenarios"].to_string(index=False))

    print("\nMonte Carlo risk:")
    print(simulation_results["risk_summary"].to_string(index=False))


if __name__ == "__main__":
    main()
