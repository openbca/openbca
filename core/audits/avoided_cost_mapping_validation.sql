AUDIT (
  name avoided_cost_mapping_validation_audit,
);

-- This audit confirms that the utility and region combination (avoided_cost_subset)
-- maps to valid avoided cost time series data.
WITH
measure_avoided_costs AS (
  -- Get all avoided cost subsets from measures
  SELECT DISTINCT
    measure_id,
    avoided_cost_subset
  FROM openbca_input.measures
  WHERE avoided_cost_subset IS NOT NULL
),
available_avoided_costs AS (
  -- Get all available avoided cost subsets from both reference and input sources
  SELECT DISTINCT
    avoided_cost_subset
  FROM openbca_core.all_avoided_costs_ts
  WHERE avoided_cost_subset IS NOT NULL
)

-- Return measures with avoided cost subsets that don't exist in available avoided costs
SELECT
  measure_id,
  avoided_cost_subset,
  'Avoided cost subset (utility and region combination) does not map to valid avoided cost time series data' as validation_message
FROM measure_avoided_costs
WHERE NOT EXISTS (
  SELECT 1
  FROM available_avoided_costs
  WHERE available_avoided_costs.avoided_cost_subset = measure_avoided_costs.avoided_cost_subset
)