# ADR-001: Analytical stack and repository architecture

- **Status:** Accepted
- **Date:** 2026-11-21
- **Decision scope:** Local, reproducible analytical workflow for the Capacity Planning & Optimisation Engine

## Context

The project processes a large public infrastructure trace, derives an hourly capacity signal, applies forecasting and capacity-planning logic, and evaluates constrained expansion and risk scenarios. The implementation should remain understandable to industrial-engineering and analytics practitioners, runnable on a developer workstation for appropriately sized partitions, and transparent about its assumptions.

The repository is a research and portfolio decision-support project. It is not designed as a production service, distributed data platform or live infrastructure controller.

## Decisions

| Concern | Selected approach | Rationale |
|---|---|---|
| Primary language | Python | Provides one language for data handling, forecasting, optimisation, simulation, testing and notebook-based explanation. |
| Tabular computation | pandas and NumPy | Familiar dataframe and numerical interfaces for hourly time series, validation metrics and scenario calculations. |
| Analytical SQL | DuckDB | Supports local analytical queries over Parquet without requiring a separate database server. |
| Columnar storage | Parquet | Supports partitioned source data and column-oriented scans; raw archives remain outside Git. |
| Optimisation | PuLP with the CBC solver interface | Expresses the capacity-expansion problem as a transparent mixed-integer linear program with integer server-addition decisions. |
| Validation | pytest | Provides repeatable unit-level checks for core capacity and forecasting behaviours. |
| Exploration and communication | Jupyter notebooks | Separates the staged analytical narrative from reusable package logic in `src/cpoe/`. |
| Visual outputs | Matplotlib | Supports static charts for forecast, capacity and scenario interpretation. |

## Architectural pattern

The repository follows a local batch-analytics pattern:

1. **Data layer:** source Parquet partitions are inspected and validated; DuckDB scripts produce compact analytical aggregates.
2. **Analytical layer:** Python package modules provide data loading, capacity-signal construction, forecasting, capacity planning, optimisation and simulation.
3. **Orchestration layer:** `src/cpoe/run_pipeline.py` sequences the current end-to-end Python workflow.
4. **Presentation layer:** notebooks explain stages and visualise outputs; documentation records assumptions, validation requirements and interpretation limits.

The architecture favours a modular package for reusable logic, scripts for dataset preparation, and notebooks for human-readable analysis. It does not introduce a web API, orchestration platform, message broker or continuously running service because those capabilities are outside the current use case.

## Consequences and trade-offs

**Benefits**
- A practitioner can inspect the analytical stages and key assumptions without navigating a distributed production stack.
- DuckDB and Parquet enable efficient local analytical processing when partition selection and memory use are controlled.
- The optimisation formulation is explicit and can be extended with additional operational constraints.
- The notebook narrative and package implementation can be reviewed separately.

**Trade-offs and constraints**
- Very large source partitions can exceed local storage or memory budgets; staged processing and narrow pilots are required.
- The current optimisation model is a simplified homogeneous server-expansion model and depends on illustrative financial and capacity coefficients.
- A successful unit-test suite does not prove that a full source-data pipeline run is correct.
- The current seasonal-naive forecast targets observed GPU capacity footprint, not workload demand or GPU utilisation.
- The current architecture is not production-hardened for scheduling, monitoring, access control, high availability or live decision execution.

## Revisit this decision when

- The source dataset or workload layer requires distributed processing beyond practical local DuckDB/Parquet workflows.
- A production deployment requires orchestration, monitoring, APIs, security controls or operational support.
- Additional solver requirements justify a different optimisation backend.
- The analytical workflow is calibrated and validated sufficiently to support live operational decisions.

## Related documentation

- [Project glossary](GLOSSARY.md)
- [Model assumptions](MODEL_ASSUMPTIONS.md)
- [Validation plan and known limitations](VALIDATION_AND_LIMITATIONS.md)
