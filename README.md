# Sustainable AI Data Centre Capacity Optimizer (CPOE)

A portfolio project for data-centre infrastructure baselining, workload characterization, capacity planning, optimization, scenario risk, and carefully bounded sustainability analysis using Alibaba GPU Cluster Trace 2026.

## Data strategy

- **Layer 1 — infrastructure baseline:** `asi_opensource_server_hourly` (about 3.1 GB compressed according to the release download guide).
- **Layer 2 — workload and resource-use analysis:** `asi_opensource_pod_hourly` (about 352 GB compressed). This is the main analytical dataset for workload demand/utilization; process it with DuckDB over partitioned Parquet, not pandas `read_parquet` of the entire archive.
- Optional later: job execution summary and network hourly tables.

Official references:
- Dataset: https://github.com/alibaba/clusterdata/tree/master/cluster-trace-gpu-v2026
- Schema: https://github.com/alibaba/clusterdata/blob/master/cluster-trace-gpu-v2026/docs/schema.md
- Download guide: https://github.com/alibaba/clusterdata/blob/master/cluster-trace-gpu-v2026/docs/data_download.md

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Download/extract the server archive first. Keep original partitions under `data/RAW/asi_opensource_server_hourly/` (partition folders such as `day=.../hour=.../part-*.parquet`).
4. Run `python scripts/inspect_parquet_dataset.py --path "data/RAW/asi_opensource_server_hourly/**/*.parquet"` to inspect actual fields and types.
5. Run `python scripts/build_layer1_server_baseline.py` to create hourly infrastructure and cluster-level aggregates.
6. Before downloading the pod archive, review `docs/POD_DATASET_PLAYBOOK.md`. The pod archive is very large; start with a bounded pilot (a few days/hours), then scale by partition.
7. Set `POD_PARQUET_GLOB` to the extracted pod partitions and run `python scripts/build_layer2_pod_aggregates.py`. The script first inspects schema and fails with a clear message if expected fields differ; validate fields against the official schema.

## Data and interpretation guardrails

- `day`/`hour` are relative trace partitions, not real calendar timestamps.
- A server row is an observed inventory record, not proof every GPU is operational or available for allocation.
- Server inventory alone cannot measure utilization, idle GPUs, workload demand, electricity use, or carbon emissions.
- Pod-level resource requests and reported utilization are not the same as power draw. Estimate energy only with documented power assumptions or real measurements; report estimates as estimates.
- Do not claim realized energy/carbon savings from this trace without power data and a defensible counterfactual.
- Do not commit raw data, large derived data, or credentials to GitHub.

## Project layers

1. `docs/LAYER1_LAYER2_ANALYTICAL_PLAN.md` — research questions, metrics, limitations, and acceptance criteria.
2. `scripts/` — schema inspection and memory-conscious DuckDB aggregation.
3. `sql/` — example exploratory queries.
4. `notebooks/` — staged narrative analysis. Run top-to-bottom and validate generated artifacts before publishing.
5. `docs/EXECUTIVE_SUMMARY.md` — portfolio narrative; update with actual results only after running the analysis.

## Suggested machine setup

A local DuckDB database is the recommended starting point. It is a file-based analytical database and can query Parquet directly, scanning only required columns/partitions. Do not provision a hosted cloud database initially. Consider cloud object storage + a managed query engine only if local disk, RAM, or collaboration needs justify the cost and operational overhead.

## Reference
@inproceedings{asi_trace_2026,
  title = {Heterogeneity at Hyperscale: Characterization and Scheduling of Large Production AI Clusters at Alibaba},
  author = {Suyi Li and Lingyun Yang and Haoxuan Yu and Sheng Yao and Tianyuan Wu and Xiaoxiao Jiang and Hanfeng Lu and Kangjin Wang and Chenhao Wang and Shenglin Xu and Lun Wang and Qingyang Duan and Shenghao Liang and Xiu Lin and Wenchao Wu and Yinghao Yu and Guodong Yang and Liping Zhang and Wei Wang},
  booktitle = {20th USENIX Symposium on Operating Systems Design and Implementation (OSDI 26)},
  year = {2026}
}