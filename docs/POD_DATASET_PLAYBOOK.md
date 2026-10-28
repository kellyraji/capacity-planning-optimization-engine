# Pod-hourly data playbook: handling a very large Parquet dataset

## Recommendation

Do **not** create a hosted/online database as the first step. Start with partitioned Parquet files + DuckDB locally. DuckDB can query Parquet directly and push column selection and filters into the scan. This avoids importing the entire dataset into pandas or paying for a managed warehouse before you know the workload and cost.

## Suggested staged workflow

1. **Inspect without loading everything.** List files, inspect schema and partition layout, confirm available disk space.
2. **Pilot a narrow slice.** Select a small set of `day=` partitions and a few columns; test filters, nulls, units, duplicates, and query time.
3. **Build compact hourly aggregates.** Use DuckDB SQL to aggregate pods at server-hour or cluster-hour grain. Store outputs as Parquet under `data/PROCESSED/`, not as giant CSV files.
4. **Persist only useful tables.** Use a local `data/ANALYTICS/cpoe.duckdb` for small/medium aggregates and metadata. Keep the full raw trace in Parquet.
5. **Scale incrementally.** Process day partitions in batches if one broad query exceeds RAM/disk/time. Make each batch idempotent and log completed partitions.
6. **Join after aggregation.** Reduce pod rows to server-hour before joining server inventory, and validate join cardinality.
7. **Version the analysis.** Save a manifest containing source URL, download date, partition range, file counts, schema snapshot, code version, filters and assumptions.
8. **Only consider cloud later.** Use object storage + managed query compute if local hardware is insufficient, or you need team access/reproducible hosted dashboards. Budget storage, query scans, egress and access control first.

## Why not a cloud SQL database initially?

- A row-oriented transactional database is not the best first landing zone for hundreds of GB of compressed analytical Parquet.
- Loading everything into a managed warehouse adds ingestion, storage, permissions and cost management.
- You may not need all pod-level rows for the portfolio; most analysis can run on narrow columns and aggregated outputs.
- Local DuckDB is easy to reproduce in GitHub instructions and works well for analytical SQL on Parquet.

## Hardware and storage reality

The official download guide lists the pod archive at roughly 352 GB compressed. The extracted size can be much larger, so check free disk space before downloading and allow room for intermediate outputs. If you cannot comfortably store and process the full release, use a small, well-documented partition sample for development and use cloud object storage/query compute only for the full-scale run. Do not imply that a sample represents the entire trace.

## Safe first pilot

- Download the server archive first (roughly 3.1 GB compressed per the official guide).
- For pods, download/extract only if the provider permits selective access; otherwise plan for the full archive size before starting. The release is partitioned by relative day/hour after extraction.
- Query a few `day=.../hour=...` Parquet partitions and project only the fields required for your first research question.
- Save the schema and pilot metrics, then decide whether to scale up.

## References

- Official download guide: https://github.com/alibaba/clusterdata/blob/master/cluster-trace-gpu-v2026/docs/data_download.md
- Official schema: https://github.com/alibaba/clusterdata/blob/master/cluster-trace-gpu-v2026/docs/schema.md
- DuckDB Parquet queries: https://duckdb.org/docs/current/data/parquet/overview
- DuckDB query Parquet directly: https://duckdb.org/docs/current/guides/file_formats/query_parquet
