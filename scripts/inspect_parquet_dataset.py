"""Inspect Parquet schema and basic file metadata without loading all rows into pandas."""
import argparse
from pathlib import Path
import duckdb

p = argparse.ArgumentParser()
p.add_argument('--path', required=True, help='Glob, e.g. data/RAW/asi_opensource_server_hourly/**/*.parquet')
p.add_argument('--database', default=':memory:', help='DuckDB file path or :memory:')
args = p.parse_args()
con = duckdb.connect(args.database)
path = args.path.replace('\\', '/')
print(f'Input glob: {path}')
try:
    print('Schema:')
    print(con.execute('DESCRIBE SELECT * FROM read_parquet(?, hive_partitioning=true) LIMIT 0', [path]).df().to_string(index=False))
    print('Sample rows:')
    print(con.execute('SELECT * FROM read_parquet(?, hive_partitioning=true) LIMIT 5', [path]).df().to_string(index=False))
    print('Approximate row count (may scan all matching files):')
    print(con.execute('SELECT COUNT(*) AS rows FROM read_parquet(?, hive_partitioning=true)', [path]).df().to_string(index=False))
except Exception as e:
    raise SystemExit(f'Could not inspect dataset. Check path and schema. Details: {e}')
finally:
    con.close()
