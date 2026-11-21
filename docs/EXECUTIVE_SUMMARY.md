# Executive summary — Capacity Planning & Optimisation Engine

## Purpose

This project demonstrates an industrial-engineering decision-support workflow for infrastructure capacity baselining, short-horizon forecasting, capacity planning, constrained expansion and operational risk analysis. It uses the public Alibaba GPU Cluster Trace 2026 as a case study and keeps assumptions, transformations and limitations explicit.

## Decision problem

Infrastructure planners need to understand the observed capacity footprint, translate a forecast into a planning requirement, and evaluate expansion choices under financial and operational constraints. The central question is how to turn a measured infrastructure baseline and an explicit set of planning assumptions into a defensible capacity plan.

## Current analytical workflow

1. **Data engineering:** inspect and validate server-hourly Parquet data, then use DuckDB to aggregate a trace-relative hourly infrastructure baseline.
2. **Capacity signal:** calculate observed GPU capacity as the aggregate GPU inventory recorded across observed servers at each hour.
3. **Forecasting:** apply a 24-hour seasonal-naive benchmark to the observed GPU capacity footprint and evaluate it on a chronological holdout using MAE and RMSE.
4. **Capacity planning:** convert forecast capacity into required planning capacity using an explicit target-utilisation assumption, usable-capacity factor and safety buffer; calculate headroom and risk flags.
5. **Optimisation:** use a mixed-integer linear programming model to evaluate staged server additions against illustrative CAPEX, OPEX and shortage-penalty coefficients.
6. **Risk analysis:** stress-test the required-capacity plan under deterministic cases and seeded Monte Carlo variation in required capacity and capacity availability.

## Planned analytical extensions

- **Workload layer:** use validated pod-hourly fields to analyse resource requests, reported utilisation and scheduling delays. These are distinct measures and must not be conflated with observed server inventory.
- **Forecast improvement:** compare the current seasonal-naive benchmark with persistence and other candidates using rolling-origin backtesting; add a separate workload-demand forecast only when a defensible demand signal is defined.
- **Operational constraints:** incorporate resource compatibility, lead times, expansion limits, workload priority and other constraints where source data supports them.
- **Energy analysis:** introduce measured power or a transparent calibrated power model and carbon-intensity factors before estimating energy or emissions.

## Current outputs

- Hourly observed infrastructure capacity footprint.
- Forecast-capacity series and chronological holdout metrics.
- Capacity requirements, headroom and planning risk flags.
- Modelled server additions, availability, shortage and cost components.
- Deterministic scenario and Monte Carlo stress-test summaries.

## Status and limitations

The repository does not include the large source archives. The complete workflow must be executed and validated against the downloaded trace release before publishing numerical findings. Relative `day` and `hour` partitions represent trace time, not calendar dates. Server inventory is not proof that every GPU is operational, schedulable or available. The current forecast is of observed GPU capacity—not workload demand or GPU utilisation.

Planning factors, server capacity, financial coefficients and stress-test distributions are illustrative. Simulated shortage is conditional on those assumptions and is not a measured failure probability. No realised cost savings, energy savings or carbon reductions are claimed.

## Professional relevance

The project brings together industrial engineering, capacity planning, data analytics and operations research. Its emphasis is on traceable assumptions, analytical validation and translating quantitative signals into structured operational decisions, using public data rather than proprietary employer information.
