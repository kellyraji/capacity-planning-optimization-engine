-- Run in DuckDB after creating layer1_server_hour and layer2_pod_server_hour.
-- Relative trace time: do not cast day/hour to calendar timestamps.

-- Layer 1 overall range and row count
SELECT MIN(TRY_CAST(day AS INTEGER)) AS min_day,
       MAX(TRY_CAST(day AS INTEGER)) AS max_day,
       COUNT(*) AS aggregate_rows
FROM layer1_server_hour;

-- Layer 1 cluster/model footprint distribution
SELECT cluster_id, gpu_spec_public,
       SUM(observed_gpu_count) AS gpu_count_sum_over_hours,
       MAX(observed_gpu_count) AS peak_observed_gpu_count
FROM layer1_server_hour
GROUP BY 1,2
ORDER BY peak_observed_gpu_count DESC;

-- Check duplicate server-hour grain in source if loaded as a view/table:
-- SELECT day, hour, server_id, COUNT(*) n
-- FROM server_source GROUP BY 1,2,3 HAVING COUNT(*) > 1;

-- IMPORTANT: do not sum server capacity after joining to raw pod rows.
-- Aggregate pod rows to server-hour first, then join and check row counts.
