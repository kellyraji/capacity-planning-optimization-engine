# Project glossary

This glossary defines the terms used across the README, source modules, notebooks and analytical documentation. The definitions describe this repository's implementation; they should not be interpreted as universal service-level or infrastructure standards.

## Capacity and forecasting

| Term | Definition in this project |
|---|---|
| **Observed GPU capacity** | The hourly GPU inventory footprint calculated by summing GPU counts across server records observed in the trace. It is an inventory signal, not proof of operational or schedulable capacity. |
| **Capacity footprint** | The observed infrastructure quantity represented by the server-hourly data at a given trace hour. |
| **Capacity signal** | The time series derived from the observed GPU capacity footprint and used as the current forecast input. |
| **Forecast capacity** | The model output estimating the future observed GPU capacity footprint. The canonical dataframe field is `forecast_capacity`; the pipeline output is `capacity_forecast.csv`. It is not a workload-demand or utilisation forecast. |
| **Workload demand** | Resource demand associated with workloads, for example pod resource requests or measured consumption. It is a separate analytical concept and is not the target of the current forecast. |
| **Baseline capacity** | The latest observed GPU capacity footprint used as the starting reference in the current planning calculation. It is not a verified measure of available operational capacity. |
| **Required planning capacity** | The capacity level calculated by applying the planning factor to forecast capacity. It incorporates the target-utilisation, usable-capacity and safety-buffer assumptions. |
| **Headroom** | Available or baseline capacity minus required planning capacity. Positive headroom indicates modelled capacity above the requirement; negative headroom indicates a modelled gap. Before optimisation, the comparison uses the baseline; after optimisation, it can use planned available capacity. |
| **Planning utilisation** | In the current implementation, the ratio of forecast capacity to baseline capacity. It is a planning indicator, not telemetry-derived GPU utilisation. |
| **Seasonal-naive forecast** | A benchmark that predicts a value using the corresponding observation from the previous seasonal cycle; the current benchmark uses a 24-hour daily cycle. |
| **Chronological holdout** | A validation method that reserves the latest observations as a test period and uses earlier observations as the historical reference, preserving time order. |
| **MAE** | Mean absolute error: the average absolute difference between forecast and actual values, expressed in the target's units. |
| **RMSE** | Root mean squared error: the square root of the average squared forecast error, expressed in the target's units and more sensitive to larger errors than MAE. |

## Capacity planning and optimisation

| Term | Definition in this project |
|---|---|
| **Target utilisation** | An assumed planning ceiling used in the capacity-planning formula; it is not measured utilisation. |
| **Usable-capacity factor** | An assumed proportion of nominal capacity treated as usable for planning. It requires calibration for a real operating environment. |
| **Safety buffer** | An explicit reserve added by the planning formula to provide allowance above the forecast signal. |
| **Capacity expansion** | The modelled decision to add server capacity over successive planning periods. |
| **MILP** | Mixed-integer linear programming: an optimisation method with linear objective/constraints and decision variables that may be integer-valued. Here, server additions are integer decision variables. |
| **Decision variable** | A variable selected by the optimisation solver; in this model, the number of new servers added in each period and the modelled shortage. |
| **CAPEX** | Capital expenditure. The model uses an illustrative per-server capital cost coefficient, not a supplier quotation. |
| **OPEX** | Operating expenditure. The model uses an illustrative per-server, per-period operating cost coefficient. |
| **Shortage penalty** | An illustrative objective-function coefficient used to penalise capacity shortfall. It is not a measured financial loss. |

## Risk analysis and data engineering

| Term | Definition in this project |
|---|---|
| **Required-capacity stress multiplier** | A scenario or random factor applied to required planning capacity to test sensitivity. It is a modelled stress assumption, not an observed demand-growth rate. |
| **Capacity-availability factor** | A scenario or random factor applied to planned available capacity to represent a hypothetical capacity reduction. It is not a measured outage distribution. |
| **Deterministic scenario analysis** | Recalculation of model outputs under a defined set of fixed stress assumptions. |
| **Monte Carlo simulation** | Repeated evaluation using randomly sampled input factors to examine the distribution of modelled outcomes. Results are conditional on the chosen distributions and parameters. |
| **DuckDB** | An embedded analytical SQL database used for local querying and aggregation of columnar data. |
| **Parquet** | A column-oriented file format used to store and process analytical datasets efficiently. |
| **Trace-relative time** | The relative day/hour or timestamp representation supplied or derived from the trace. It should not be presented as real calendar time without a documented mapping. |

## Naming conventions

- Use **observed GPU capacity** for the trace-derived inventory footprint.
- Use **forecast capacity** for the current forecasting target and `forecast_capacity` for its code field.
- Use **workload demand** only for a workload-derived demand signal; do not use it as a synonym for observed GPU inventory.
- Use **required planning capacity** for the result after planning assumptions are applied.
- Use **required-capacity stress** for the deterministic and Monte Carlo scenario multipliers.
- Describe modelled costs, shortages and probabilities as **illustrative or conditional outputs** unless calibrated and validated against operational evidence.
