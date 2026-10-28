# Data dictionary (complete after inspecting actual files)

| Table | Field | Type | Meaning from official schema | Unit | Null rate | Transformation / caveat |
|---|---|---|---|---|---|---|
| server-hourly | `server_id` | string | Anonymized server identifier | n/a | TBD | Stable within release; validate server-hour uniqueness |
| server-hourly | `cluster_id` | string | Anonymized cluster identifier | n/a | TBD | Stable within release |
| server-hourly | `gpu_spec_public` | string | Public GPU model bucket | category | TBD | Models may not be directly interchangeable |
| server-hourly | `gpu_count` | double | GPU count | GPUs | TBD | Observed inventory; not operational availability |
| server-hourly | `cpu_capacity_cores` | double | CPU capacity | cores | TBD | Sum only at validated grain |
| pod-hourly | Add rows from actual schema | | | | | Verify request/use units and denominators |

Do not finalize this dictionary from guessed field names. Use `inspect_parquet_dataset.py` and the official schema, then record the schema version and date inspected.
