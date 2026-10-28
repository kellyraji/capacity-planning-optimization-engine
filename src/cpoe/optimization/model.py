
from pathlib import Path

import pandas as pd
from pulp import (
    LpMinimize,
    LpProblem,
    LpStatus,
    LpVariable,
    PULP_CBC_CMD,
    lpSum,
    value,
)


def optimize_capacity(
    capacity_data,
    output_dir=None,
    capacity_per_server=8.0, #assumed
    capex_per_server=1_000_000.0,
    opex_per_server_period=1_000.0,
    # Illustrative cost per capacity unit of shortage per hourly period.
    # Replace with a defensible business estimate when available.
    shortage_penalty=10_000_000.0, #Assumed
    max_new_servers_period=20000,
):
    """
    Optimize integer server additions over the forecast horizon.

    Commercial parameters are illustrative, not actual data-centre costs.
    """
    if isinstance(capacity_data, (str, Path)):
        cap = pd.read_csv(capacity_data, index_col=0, parse_dates=True)
    else:
        cap = capacity_data.copy()

    required_columns = {"required_capacity", "baseline_capacity"}
    missing = required_columns - set(cap.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    cap = cap.sort_index()
    required = pd.to_numeric(
        cap["required_capacity"], errors="raise"
    ).clip(lower=0).tolist()
    baseline = float(cap["baseline_capacity"].iloc[0])

    if not required or capacity_per_server <= 0:
        raise ValueError("Forecast must be non-empty and server capacity positive.")
    if baseline < 0 or max_new_servers_period < 0:
        raise ValueError("Baseline and expansion limit must be non-negative.")

    periods = range(len(required))
    model = LpProblem("capacity_expansion", LpMinimize)

    additions = {
        t: LpVariable(
            f"new_servers_{t}",
            lowBound=0,
            upBound=max_new_servers_period,
            cat="Integer",
        )
        for t in periods
    }
    shortage = {
        t: LpVariable(f"shortage_{t}", lowBound=0)
        for t in periods
    }

    capex = lpSum(capex_per_server * additions[t] for t in periods)

    opex = lpSum(
        opex_per_server_period
        * lpSum(additions[k] for k in range(t + 1))
        for t in periods
    )

    shortage_cost = lpSum(
        shortage_penalty * shortage[t] for t in periods
    )

    model += capex + opex + shortage_cost

    for t in periods:
        available = baseline + capacity_per_server * lpSum(
            additions[k] for k in range(t + 1)
        )
        model += available + shortage[t] >= required[t]

    model.solve(PULP_CBC_CMD(msg=False))

    status = LpStatus[model.status]
    if status != "Optimal":
        raise RuntimeError(f"Optimization failed: {status}")

    solution = cap.copy()
    solution["new_servers"] = [
        int(round(value(additions[t]) or 0)) for t in periods
    ]
    solution["cumulative_servers"] = solution["new_servers"].cumsum()
    solution["available_capacity"] = (
        baseline + capacity_per_server * solution["cumulative_servers"]
    )
    solution["shortage"] = [
        max(0.0, float(value(shortage[t]) or 0)) for t in periods
    ]
    solution["headroom"] = (
        solution["available_capacity"] - solution["required_capacity"]
    )
    solution["capex"] = solution["new_servers"] * capex_per_server
    solution["period_opex"] = (
        solution["cumulative_servers"] * opex_per_server_period
    )
    solution["total_period_cost"] = (
        solution["capex"]
        + solution["period_opex"]
        + solution["shortage"] * shortage_penalty
    )

    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        solution.to_csv(output_dir / "optimization_solution.csv")

    solver_objective = value(model.objective)
    reported_cost = solution["total_period_cost"].sum()

    print(f"Solver status: {status}")
    print(f"New servers: {int(solution['new_servers'].sum())}")
    print(f"CAPEX: {solution['capex'].sum():,.2f}")
    print(f"OPEX: {solution['period_opex'].sum():,.2f}")
    print(f"Shortage cost: {(solution['shortage'] * shortage_penalty).sum():,.2f}")
    print(f"Reported total cost: {reported_cost:,.2f}")
    print(f"Solver objective: {solver_objective:,.2f}")
    print(f"Cost reconciliation difference: {reported_cost - solver_objective:,.2f}")

    print("\nServer additions by period:")
    print(solution[["new_servers", "cumulative_servers"]].to_string())

    print("\nExpansion limit check:")
    print("Maximum additions in any period:",
        solution["new_servers"].max())
    print("Periods at expansion limit:",
        (solution["new_servers"] >= max_new_servers_period).sum())
    print("Total periods:", len(solution))
    print("Maximum possible additions:",
        max_new_servers_period * len(solution))

    return solution
