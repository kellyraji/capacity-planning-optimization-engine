"""Create compact Layer 2 pod aggregates with DuckDB.

IMPORTANT: run schema inspection first. This script intentionally checks field names before aggregating.
Set POD_PARQUET_GLOB to the extracted partitioned Parquet files.
"""
import os
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
POD_GLOB = os.getenv('POD_PARQUET_GLOB', str(ROOT / 'data/RAW/asi_opensource_pod_hourly/**/*.parquet'))
OUT = ROOT / 'data/PROCESSED'
OUT.mkdir(parents=True, exist_ok=True)
DB = ROOT / 'data/ANALYTICS/cpoe.duckdb'
DB.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DB))
try:
    schema_df = con.execute('DESCRIBE SELECT * FROM read_parquet(?, hive_partitioning=true) LIMIT 0', [POD_GLOB]).df()
    cols = set(schema_df['column_name'].astype(str))
    print('Detected pod fields:', ', '.join(sorted(cols)))
    # Expected identifiers/time keys; confirm against the official schema before a full run.
    required = {'day','hour','server_id'}
    missing = required - cols
    if missing:
        raise RuntimeError(f'Cannot build server-hour aggregates: missing {sorted(missing)}. Inspect schema and update the script to actual keys.')
    # Choose available resource fields dynamically; preserve NULLs and only aggregate present columns.
    candidates = ['gpu_request','gpu_utilization','gpu_util','gpu_usage','cpu_request','cpu_utilization','memory_request','schedule_delay_sec','ready_delay_sec']
    numeric = [c for c in candidates if c in cols]
    if 'gpu_request' not in cols:
        print('WARNING: gpu_request field not found; this script will not apply the GPU-request-positive filter.')
    select_metrics = []
    for c in numeric:
        # Use only numeric columns from a known allow-list; aggregate by SUM for request fields and AVG for rates/delays.
        if c.endswith('_request'):
            select_metrics.append(f'SUM(TRY_CAST("{c}" AS DOUBLE)) AS sum_{c}')
        else:
            select_metrics.append(f'AVG(TRY_CAST("{c}" AS DOUBLE)) AS avg_{c}')
            select_metrics.append(f'COUNT("{c}") AS nonnull_{c}_rows')
    if not select_metrics:
        raise RuntimeError(f'No recognized metrics found. Update candidate fields after checking official schema. Actual fields: {sorted(cols)}')
    filter_sql = 'WHERE TRY_CAST(gpu_request AS DOUBLE) > 0' if 'gpu_request' in cols else ''
    query = f"""
        CREATE OR REPLACE TABLE layer2_pod_server_hour AS
        SELECT CAST(day AS VARCHAR) AS day,
               CAST(hour AS VARCHAR) AS hour,
               CAST(server_id AS VARCHAR) AS server_id,
               COUNT(*) AS pod_hour_rows,
               {', '.join(select_metrics)}
        FROM read_parquet(?, hive_partitioning=true)
        {filter_sql}
        GROUP BY 1,2,3
    """
    con.execute(query, [POD_GLOB])
    con.execute("COPY layer2_pod_server_hour TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'layer2_pod_server_hour.parquet')])
    print(f'Wrote {OUT / "layer2_pod_server_hour.parquet"}')
    print('NOTE: review each field meaning and units before interpreting averages/sums. This script is a starter, not a validated semantic mapping.')
finally:
    con.close()
