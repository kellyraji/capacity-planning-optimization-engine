# Executive summary — Sustainable AI Data Centre Capacity Optimizer

## Purpose

This project develops a data-driven framework for understanding observed AI data-centre infrastructure, characterizing GPU workload demand, and evaluating capacity decisions under operational uncertainty. It applies industrial engineering, forecasting, optimization, scenario analysis and data engineering to a public GPU trace.

## Decision problem

AI infrastructure operators must balance service-level needs and workload growth against constrained GPU capacity, operational risk and the cost and environmental implications of running infrastructure. Poorly matched requests, placement and capacity decisions can contribute to underused resources or avoidable expansion, but utilization alone does not establish energy waste.

## Method

**Layer 1 — Infrastructure baseline:** use the server-hourly table to measure observed GPU/CPU footprint, inventory dynamics, cluster/model concentration and hypothetical outage exposure.

**Layer 2 — Workload analysis:** use the pod-hourly table to analyze resource requests, reported utilization and scheduling delays where available. Aggregate at a validated server-hour grain before joining infrastructure inventory.

**Decision layer:** forecast a clearly defined target, compare capacity plans under transparent constraints, and evaluate baseline/stress scenarios. Use a naive benchmark and chronological holdout for forecast validation.

**Sustainability layer:** quantify energy/carbon only when measured power or a transparent, calibrated power model and carbon-intensity assumptions are available. Separate measured results from estimates.

## Expected outputs

- Reproducible data-quality and schema report.
- Infrastructure capacity baseline and time-series summaries.
- Workload/request-use aggregates and scheduling indicators.
- Forecast validation results, capacity scenarios and optimization outputs.
- Sustainability sensitivity analysis with explicit assumptions and limitations.

## Current status and limitations

This repository is a project scaffold and analytical implementation pack. It does not include the large Alibaba source archives, and the full pipeline must be run and validated against the downloaded release before any numeric findings are reported. Relative `day` and `hour` partitions are trace time, not calendar dates. Server inventory is not proof of operational availability; workload utilization is not power consumption.

## Professional relevance

The project demonstrates industrial engineering and data analytics through capacity planning, workload characterization, optimization, risk analysis and decision support. It is designed to be auditable and publicly reproducible without using proprietary employer data.
