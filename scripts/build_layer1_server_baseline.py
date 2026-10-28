"""Build Layer 1 aggregates using DuckDB; adjust glob after inspecting the extracted dataset."""
import os
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
SERVER_GLOB = os.getenv('SERVER_PARQUET_GLOB', str(ROOT / 'data/RAW/asi_opensource_server_hourly/**/*.parquet'))
OUT = ROOT / 'data/PROCESSED'
OUT.mkdir(parents=True, exist_ok=True)
DB = ROOT / 'data/ANALYTICS/cpoe.duckdb'
DB.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DB))
try:
    schema = con.execute('DESCRIBE SELECT * FROM read_parquet(?, hive_partitioning=true) LIMIT 0', [SERVER_GLOB]).df()
    cols = set(schema['column_name'].astype(str))
    required = {'server_id','cluster_id','gpu_count','cpu_capacity_cores','gpu_spec_public'}
    missing = required - cols
    if missing:
        raise RuntimeError(f'Missing expected fields {sorted(missing)}. Actual fields: {sorted(cols)}. Review official schema.')
    time_cols = {'day','hour'} & cols
    if time_cols != {'day','hour'}:
        raise RuntimeError(f'Expected day/hour partition columns; found {sorted(time_cols)}. Check hive_partitioning and dataset layout.')
    con.execute(f"""
        CREATE OR REPLACE TABLE layer1_server_hour AS
        SELECT CAST(day AS VARCHAR) AS day,
               CAST(hour AS VARCHAR) AS hour,
               CAST(cluster_id AS VARCHAR) AS cluster_id,
               CAST(gpu_spec_public AS VARCHAR) AS gpu_spec_public,
               COUNT(DISTINCT server_id) AS observed_servers,
               SUM(COALESCE(gpu_count, 0)) AS observed_gpu_count,
               SUM(COALESCE(cpu_capacity_cores, 0)) AS observed_cpu_capacity_cores,
               COUNT(*) AS source_rows
        FROM read_parquet(?, hive_partitioning=true)
        GROUP BY 1,2,3,4
    """, [SERVER_GLOB])
    con.execute("COPY layer1_server_hour TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'layer1_server_hour.parquet')])
    con.execute(f"""
        CREATE OR REPLACE TABLE layer1_infrastructure_hour AS
        SELECT CAST(day AS VARCHAR) AS day,
               CAST(hour AS VARCHAR) AS hour,
               COUNT(DISTINCT server_id) AS observed_servers,
               SUM(COALESCE(gpu_count, 0)) AS observed_gpu_count,
               SUM(COALESCE(cpu_capacity_cores, 0)) AS observed_cpu_capacity_cores,
               COUNT(*) AS source_rows
        FROM read_parquet(?, hive_partitioning=true)
        GROUP BY 1,2
    """, [SERVER_GLOB])
    con.execute("COPY layer1_infrastructure_hour TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'layer1_infrastructure_hour.parquet')])
    print(f'Wrote {OUT / "layer1_server_hour.parquet"}')
    print(f'Wrote {OUT / "layer1_infrastructure_hour.parquet"}')
    print(con.execute('SELECT * FROM layer1_infrastructure_hour ORDER BY CAST(day AS INTEGER), hour LIMIT 10').df().to_string(index=False))
finally:
    con.close()
