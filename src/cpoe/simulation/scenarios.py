
from pathlib import Path

import numpy as np
import pandas as pd


def run_scenario_simulation(
    capacity_requirements,
    optimization_solution,
    output_dir,
    simulations=5000,
    seed=42,
):
    """Stress-test capacity plans using deterministic and random scenarios."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    def load_frame(data):
        if isinstance(data, (str, Path)):
            return pd.read_csv(data, index_col=0, parse_dates=True)
        return data.copy()

    cap = load_frame(capacity_requirements)
    solution = load_frame(optimization_solution)

    if "required_capacity" not in cap:
        raise ValueError("Capacity data must contain required_capacity.")
    if "available_capacity" not in solution:
        raise ValueError("Optimization output must contain available_capacity.")

    # Align both series on the same forecast timestamps.
    frame = pd.concat(
        [
            cap["required_capacity"].rename("required"),
            solution["available_capacity"].rename("available"),
        ],
        axis=1,
        join="inner",
    ).dropna()

    if frame.empty:
        raise ValueError("No overlapping timestamps in capacity and solution.")
    if simulations < 1:
        raise ValueError("simulations must be at least 1.")

    required = frame["required"].clip(lower=0)
    available = frame["available"].clip(lower=0)

    scenarios = {
        "Base": (1.00, 1.00),
        "High demand": (1.10, 1.00),
        "Demand surge": (1.25, 1.00),
        "Capacity outage": (1.00, 0.85),
        "Combined stress": (1.20, 0.85),
    }

    rows = []
    for name, (demand_factor, capacity_factor) in scenarios.items():
        stressed_required = required * demand_factor
        stressed_available = available * capacity_factor
        shortage = (stressed_required - stressed_available).clip(lower=0)

        rows.append({
            "scenario": name,
            "peak_required_capacity": float(stressed_required.max()),
            "minimum_available_capacity": float(stressed_available.min()),
            "peak_shortage": float(shortage.max()),
            "hours_with_shortage": int((shortage > 0).sum()),
            "total_shortage_capacity_hours": float(shortage.sum()),
        })

    deterministic = pd.DataFrame(rows)
    deterministic.to_csv(output_dir / "scenario_results.csv", index=False)

    # Monte Carlo stress test. These are explicit illustrative assumptions:
    # demand multiplier ~ N(1.0, 0.08), truncated at zero;
    # capacity availability is reduced by a random 0–15% outage.
    rng = np.random.default_rng(seed)
    demand_factors = np.maximum(
        rng.normal(1.0, 0.08, size=simulations), 0
    )
    capacity_factors = rng.uniform(0.85, 1.0, size=simulations)

    peak_shortages = np.empty(simulations)
    hours_short = np.empty(simulations, dtype=int)

    required_values = required.to_numpy(dtype=float)
    available_values = available.to_numpy(dtype=float)

    for i in range(simulations):
        stressed_required = required_values * demand_factors[i]
        stressed_available = available_values * capacity_factors[i]
        shortages = np.maximum(stressed_required - stressed_available, 0)

        peak_shortages[i] = shortages.max()
        hours_short[i] = int((shortages > 0).sum())

    mc_results = pd.DataFrame({
        "peak_shortage": peak_shortages,
        "hours_with_shortage": hours_short,
    })
    mc_results.to_csv(
        output_dir / "monte_carlo_results.csv", index=False
    )

    risk_summary = pd.DataFrame([{
        "simulations": simulations,
        "probability_of_shortage": float((peak_shortages > 0).mean()),
        "mean_peak_shortage": float(peak_shortages.mean()),
        "p90_peak_shortage": float(np.quantile(peak_shortages, 0.90)),
        "p95_peak_shortage": float(np.quantile(peak_shortages, 0.95)),
        "p99_peak_shortage": float(np.quantile(peak_shortages, 0.99)),
    }])
    risk_summary.to_csv(
        output_dir / "monte_carlo_risk_summary.csv", index=False
    )

    print("\nDeterministic scenarios:")
    print(deterministic.to_string(index=False))
    print("\nMonte Carlo risk summary:")
    print(risk_summary.to_string(index=False))

    return {
        "scenarios": deterministic,
        "monte_carlo_results": mc_results,
        "risk_summary": risk_summary,
    }


# Alias for code that uses the shorter function name.
run_simulation = run_scenario_simulation
