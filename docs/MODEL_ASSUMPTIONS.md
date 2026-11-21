# Model assumptions and parameter register

This register separates source observations, transformations and illustrative inputs.

## Source observations

| Item | Treatment | Qualification |
|---|---|---|
| Server inventory | Aggregated by relative trace day/hour | Presence does not prove operational availability |
| GPU count | Summed from server-hourly records | Validate grain, nulls and duplicate keys |
| CPU capacity | Summed from server-hourly records | Not interchangeable with GPU capacity |
| Time | Relative day/hour mapped to an artificial anchor for time-series operations | Anchor is not real calendar time |
| Pod metrics | Optional second analytical layer | Confirm fields, units and semantics first |

## Capacity-planning inputs

Defined in `src/cpoe/capacity/planning.py`.

| Parameter | Default | Meaning |
|---|---:|---|
| Target utilisation | 0.70 | Planning ceiling |
| Usable-capacity factor | 0.90 | Assumed usable share of nominal capacity |
| Safety buffer | 0.10 | Additional reserve |
| GPUs per new server | 8 | Illustrative conversion |

Planning factor = `(1 + safety_buffer) / (target_utilisation * usable_capacity_factor)`. This does not measure actual utilisation or service-level performance.

## Optimisation inputs

Defined in `src/cpoe/optimization/model.py`.

| Parameter | Default | Qualification |
|---|---:|---|
| Capacity per server | 8 units | Assumed homogeneous server capacity |
| Server CAPEX | 1,000,000 cost units | Illustrative, not a quotation |
| Server OPEX | 1,000 cost units per period | Illustrative |
| Shortage penalty | 10,000,000 per capacity-unit period | Illustrative penalty weight |
| Maximum additions per period | 20,000 servers | Model bound, not procurement constraint |

The objective minimises modelled CAPEX, cumulative OPEX and shortage penalty. It does not yet model lead times, retirements, GPU-type compatibility, ramp constraints, power limits or workload priority.

## Scenario and Monte Carlo inputs

| Parameter | Current value |
|---|---|
| Deterministic required-capacity stress multipliers | Scenario-specific: 1.00, 1.10, 1.25, 1.20 |
| Deterministic capacity factors | 1.00 and 0.85 |
| Monte Carlo iterations | 5,000 |
| Random seed | 42 |
| Required-capacity stress multiplier | Normal(1.0, 0.08), truncated at zero |
| Capacity availability multiplier | Uniform(0.85, 1.0) |

Outputs are conditional stress-test results, not calibrated operational risk forecasts.

## Reporting rules

Every quantitative result should identify source and trace range, code commit, metric definition and unit, parameters, validation checks, and whether it is observed, calculated, simulated or assumed. Never publish illustrative cost units as euros or simulated shortage as actual downtime.
