# LinkedIn project showcase pack

## Project title

**Capacity Planning & Optimisation Engine | Python, DuckDB, Forecasting, MILP & Monte Carlo Simulation**

## One-line description

A public-data industrial-engineering project connecting infrastructure capacity baselining, time-series forecasting, constrained expansion planning and operational risk simulation.

## Project summary

I developed a modular decision-support workflow to explore a recurring industrial-engineering question: how can an organisation translate an observed capacity footprint into a structured, assumption-led capacity plan?

Using the Alibaba GPU Cluster Trace 2026 as a public case study, the workflow includes DuckDB aggregation of partitioned Parquet data, an hourly infrastructure capacity signal, a 24-hour seasonal-naive forecast with chronological holdout validation, capacity requirements based on explicit utilisation and reserve assumptions, a mixed-integer optimisation model for staged server additions, and deterministic plus Monte Carlo stress testing.

The current forecast is of observed GPU inventory/capacity, not workload demand. Cost and scenario parameters are illustrative, not realised operational results.

## LinkedIn post draft

**What if capacity planning could connect forecasting, investment decisions and operational risk in one workflow?**

I have been developing a **Capacity Planning & Optimisation Engine**—a portfolio project bringing together industrial engineering, Python analytics and operations research.

The objective is to move beyond reporting capacity figures and build a structured way to examine capacity requirements, expansion choices and uncertainty.

The workflow brings together:

⚙️ **Data engineering:** DuckDB and partitioned Parquet for infrastructure data aggregation.

📈 **Forecasting:** a 24-hour seasonal-naive benchmark with chronological holdout validation.

🏭 **Capacity planning:** utilisation targets, usable-capacity assumptions, safety buffers and headroom assessment.

🧮 **Optimisation:** a mixed-integer linear programming model to evaluate staged server additions against modelled costs and shortage penalties.

🎯 **Risk analysis:** deterministic stress cases and Monte Carlo simulation to explore how required-capacity variation and assumed capacity availability affect the plan.

What matters most is connecting analytical output to operational decisions: understanding what the model assumes, where constraints may emerge, and how sensitive a proposed plan is to uncertainty.

I am using a public GPU cluster trace so the work can be explored without relying on proprietary employer data.

This is an evolving technical project. The current forecast models observed infrastructure capacity—not workload demand—and financial and risk parameters are illustrative. Validation and transparent assumptions are part of the engineering, not an afterthought.

**Good capacity planning is not just about predicting demand; it is about translating evidence and uncertainty into defensible decisions.**

GitHub repository: https://github.com/kellyraji/capacity-planning-optimization-engine

I welcome perspectives from professionals working in industrial engineering, capacity planning, operations research and data analytics.

#CapacityPlanning #IndustrialEngineering #OperationsResearch #Python #DataAnalytics #SupplyChainAnalytics #OperationalExcellence

## LinkedIn Featured item

**Name:** Capacity Planning & Optimisation Engine

**Description:** A Python-based industrial-engineering analytics project combining infrastructure baselining, forecasting, constrained capacity expansion and Monte Carlo risk analysis using public data.

**Link:** https://github.com/kellyraji/capacity-planning-optimization-engine
