AUDIT (
  name time_slice_validation_audit,
);

-- This audit checks that start year, start quarter, and EUL align with a fully populated slice
-- in the avoided cost data.
WITH
measure_time_slices AS (
  -- Get all measures with their time slice information
  SELECT
    measure_id,
    avoided_cost_subset,
    start_year,
    start_quarter,
    estimated_useful_life as eul,
    start_year + estimated_useful_life as end_year
  FROM openbca_input.measures
  WHERE start_year IS NOT NULL 
    AND start_quarter IS NOT NULL 
    AND estimated_useful_life IS NOT NULL
    AND avoided_cost_subset IS NOT NULL
),
available_years AS (
  -- Get all available years in the avoided cost data for each avoided_cost_subset
  SELECT
    avoided_cost_subset,
    MIN(year) as min_year,
    MAX(year) as max_year,
    COUNT(DISTINCT year) as year_count,
    MAX(year) - MIN(year) + 1 as year_span
  FROM openbca_core.all_avoided_costs_ts
  WHERE year IS NOT NULL
  GROUP BY avoided_cost_subset
)

-- Return measures where the time slice doesn't align with available avoided cost data
SELECT
  mts.measure_id,
  mts.avoided_cost_subset,
  mts.start_year,
  mts.start_quarter,
  mts.eul,
  mts.end_year,
  ay.min_year,
  ay.max_year,
  ay.year_count,
  ay.year_span,
  CASE
    WHEN ay.min_year IS NULL THEN 'No yearly avoided cost data available for this avoided_cost_subset'
    WHEN mts.start_year < ay.min_year THEN 'Start year is earlier than available avoided cost data'
    WHEN mts.end_year > ay.max_year THEN 'End year (start_year + EUL) exceeds available avoided cost data'
    WHEN ay.year_count < ay.year_span THEN 'Gaps in yearly avoided cost data for this time period'
    ELSE 'Time slice validation failed for unknown reason'
  END as validation_message
FROM measure_time_slices mts
LEFT JOIN available_years ay
  ON mts.avoided_cost_subset = ay.avoided_cost_subset
WHERE ay.min_year IS NULL  -- No data available
  OR mts.start_year < ay.min_year  -- Start year too early
  OR mts.end_year > ay.max_year  -- End year too late
  OR ay.year_count < ay.year_span  -- Gaps in data