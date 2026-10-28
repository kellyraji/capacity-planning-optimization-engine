
from pathlib import Path
import duckdb
import pandas as pd

REQUIRED_COLUMNS = [
    "server_id",
    "cluster_id",
    "gpu_count",
    "cpu_capacity_cores",
]


def validate_schema(frame: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"Required server fields are missing: {missing}")


def build_hourly_capacity_footprint(database_path: Path, anchor="2026-01-01"):
    """
    Aggregate server capacity by trace day and hour using DuckDB.
    Reads the source view without loading all raw records into pandas.
    """
    con = duckdb.connect(str(database_path), read_only=True)

    try:
        tables = con.execute("SHOW TABLES").fetchdf()["name"].tolist()
        if "asi_opensource_server_hourly" not in tables:
            raise ValueError(
                "View/table 'asi_opensource_server_hourly' not found in "
                f"{database_path}. Create the view first."
            )

        result = con.execute("""
            SELECT
                CAST(day AS BIGINT) AS trace_day,
                TRY_CAST(hour AS INTEGER) AS trace_hour,
                SUM(GREATEST(TRY_CAST(gpu_count AS DOUBLE), 0))
                    AS observed_gpu_capacity,
                SUM(GREATEST(TRY_CAST(cpu_capacity_cores AS DOUBLE), 0))
                    AS observed_cpu_capacity,
                COUNT(DISTINCT server_id) AS active_servers,
                COUNT(DISTINCT cluster_id) AS active_clusters
            FROM asi_opensource_server_hourly
            WHERE TRY_CAST(day AS BIGINT) IS NOT NULL
              AND TRY_CAST(hour AS INTEGER) BETWEEN 0 AND 23
            GROUP BY 1, 2
            ORDER BY 1, 2
        """).fetchdf()

        if result.empty:
            raise ValueError("No hourly capacity records were returned.")

        result["trace_timestamp"] = (
            pd.Timestamp(anchor)
            + pd.to_timedelta(result["trace_day"], unit="D")
            + pd.to_timedelta(result["trace_hour"], unit="h")
        )

        return (
            result.set_index("trace_timestamp")
            .sort_index()
        )
    finally:
        con.close()
