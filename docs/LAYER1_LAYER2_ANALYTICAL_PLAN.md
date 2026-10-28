# Analytical plan: Sustainable AI Data Centre Capacity Optimizer

## Objective

Develop an auditable decision-support workflow that links observed infrastructure capacity to observed AI workload behavior, then evaluates capacity and resource-allocation strategies under operational scenarios. Sustainability claims are conditional until power/energy data is available.

## Layer 1 — infrastructure baseline (`asi_opensource_server_hourly`)

### Questions and measures

1. **Observed infrastructure footprint** — GPU count and CPU capacity by relative hour, cluster, and public GPU model bucket.
2. **Inventory dynamics** — number of distinct observed servers, changes over time, server presence/absence by hour (after checking coverage and duplicate keys).
3. **Capacity concentration / topology** — share of GPUs by cluster and ASW/rack-domain where identifiers are present; concentration and imbalance across clusters.
4. **Planning constraints** — inventory distribution by GPU model and cluster; avoid treating unlike GPU models as perfectly interchangeable without an explicit normalization assumption.
5. **Resilience exposure** — hypothetical loss of a selected share of observed GPU capacity by cluster/model; label this as a scenario, not observed outage history.
6. **Planning readiness** — capacity baseline and data-quality report for joining Layer 2.

### What Layer 1 cannot prove

- Actual workload demand or utilization.
- Whether a server was operational and schedulable, unless explicit status fields support it.
- Idle capacity, fragmentation, energy use, cooling efficiency, water use, or emissions.

### Layer 1 deliverables

- Schema and data-quality report.
- Hourly total GPU inventory and CPU capacity.
- Cluster/model/hour capacity summaries.
- Inventory variation charts and concentration analysis.
- Clearly labelled outage stress scenarios.

## Layer 2 — workload/resource-use analysis (`asi_opensource_pod_hourly` + Layer 1)

### Start by validating the schema

The official release describes pod-hourly as one row per pod observed on a GPU server in an hour. It may include zero-GPU-request pods, so GPU workload analyses should explicitly document filters such as `gpu_request > 0`. Inspect the exact schema before coding assumptions into the pipeline.

### Questions and measures

1. **Demand profile** — requested GPU/CPU/memory resources over relative hour; profile by workload/priority/model buckets where present.
2. **Observed use vs request** — compare resource utilization fields to resource requests only after verifying units, denominator, missingness and meaning.
3. **Potential under/over-allocation** — identify request/use gaps as signals for investigation, not automatically “waste” (bursty demand and service-level requirements matter).
4. **Scheduling performance** — schedule/ready delays where present; segment by workload or priority.
5. **Capacity adequacy** — compare workload requirements to server inventory on compatible keys and time buckets. Validate many-to-many relationships and avoid multiplying server capacity when joining pod rows.
6. **Optimization** — compare baseline allocation rules with a constrained allocation model; enforce capacity, GPU type compatibility, and workload priority/deadline constraints where the data supports them.
7. **Sustainability bridge** — estimate energy only if an explicit, documented GPU/server power model is introduced; ideally calibrate against power readings. Report sensitivity ranges and avoid presenting modeled results as measured energy.

### Join design

Aggregate pods to the correct infrastructure grain before joining to server inventory. Never directly join every pod row to every server row and then sum GPU capacity: that can duplicate capacity. Start with `day`, `hour`, `server_id` if the pod table has these keys; confirm they exist and have matching semantics in the actual schema. Aggregate to server-hour first, then join one-to-one/one-to-many with server-hour inventory and validate row counts.

## Recommended evaluation metrics

- Data quality: duplicate key count, null rates, partition coverage, row counts by day/hour.
- Infrastructure: observed GPUs, CPU cores, distinct servers, GPU-model/cluster concentration.
- Workload: GPU requests, observed GPU use/utilization (only where field semantics support it), request-use gap, scheduling delay.
- Planning: capacity shortfall by GPU type, service-level misses, number of servers added in scenario.
- Sustainability: modeled kWh per workload unit and kg CO2e per workload unit only with explicit assumptions and power/carbon-intensity inputs.

## Acceptance criteria before publishing

- Schema inspected and documented from the actual files.
- Key grain and join cardinality tested; no accidental capacity duplication.
- Relative time preserved; no fabricated calendar timestamps.
- Forecast baseline compared with a naive benchmark and evaluated on a chronological holdout.
- Optimization constraints and cost/penalty assumptions disclosed.
- Scenarios include sensitivity analysis; simulated outages are not presented as observed incidents.
- Sustainability results separated into measured, modeled, and unmeasured quantities.
- Every headline number reproduced from a saved output table and documented code path.
