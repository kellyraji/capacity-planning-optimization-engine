
from pathlib import Path
import pandas as pd

path = Path("clusterdata/PROCESSED/hourly_capacity_footprint.csv")

if not path.exists():
    path = Path("outputs/hourly_capacity_footprint.csv")

if not path.exists():
    raise FileNotFoundError(
        "Could not find hourly_capacity_footprint.csv. "
        "Check your PROCESSED path in cpoe.config."
    )

df = pd.read_csv(path)

print("Columns:", df.columns.tolist())
print("Rows:", len(df))

# Identify and parse the timestamp column.
timestamp_col = (
    "trace_timestamp"
    if "trace_timestamp" in df.columns
    else df.columns[0]
)

raw = df[timestamp_col]
ts = pd.to_datetime(raw, errors="coerce")

print("\nTimestamp column:", timestamp_col)
print("Unparseable timestamps:", int(ts.isna().sum()))

ts = ts.dropna().sort_values()

print("First timestamp:", ts.min())
print("Last timestamp:", ts.max())
print("Duplicate timestamps:", int(ts.duplicated().sum()))

# Check intervals between consecutive timestamps.
intervals = ts.diff().dropna()

print("\nMost common intervals:")
print(intervals.value_counts().head(10))

print("\nExactly one-hour intervals:", int((intervals == pd.Timedelta(hours=1)).sum()))
print("Intervals longer than one hour:", int((intervals > pd.Timedelta(hours=1)).sum()))
print("Intervals shorter than one hour:", int((intervals < pd.Timedelta(hours=1)).sum()))

# Check missing hourly timestamps across the observed range.
if not ts.empty:
    unique_ts = pd.DatetimeIndex(ts.unique()).sort_values()
    expected = pd.date_range(
        start=unique_ts.min(),
        end=unique_ts.max(),
        freq="h",
    )
    missing = expected.difference(unique_ts)

    print("Expected hourly timestamps:", len(expected))
    print("Unique observed timestamps:", len(unique_ts))
    print("Missing hourly timestamps:", len(missing))

    if len(missing):
        print("First missing timestamps:", list(missing[:10]))

    if (
        ts.duplicated().sum() == 0
        and len(missing) == 0
        and (intervals == pd.Timedelta(hours=1)).all()
    ):
        print("\nPASS: timestamps are unique and consecutive hourly.")
    else:
        print("\nCHECK REQUIRED: timestamps are duplicated or irregular.")
