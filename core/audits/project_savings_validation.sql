AUDIT (
  name project_savings_validation_audit,
);

-- This audit checks if the project savings ≠ 1.0 and the sum of the corresponding load shape time series also ≠ 1,
-- and issues a warning in that case.
WITH
measure_savings AS (
  -- Get all measures with their energy savings
  SELECT
    measure_id,
    'ELECTRICITY' as commodity,
    upper(elec_load_shape_mapping) as load_shape_mapping,
    elec_savings_mwh as energy_savings
  FROM openbca_input.measures
  WHERE elec_load_shape_mapping IS NOT NULL AND elec_savings_mwh IS NOT NULL
  
  UNION ALL
  
  SELECT
    measure_id,
    'GAS' as commodity,
    upper(gas_load_shape_mapping) as load_shape_mapping,
    gas_saving_therms as energy_savings
  FROM openbca_input.measures
  WHERE gas_load_shape_mapping IS NOT NULL AND gas_saving_therms IS NOT NULL
),
load_shape_sums AS (
  -- Calculate the sum of load shape normalized fractions for each load shape
  SELECT
    commodity,
    load_shape,
    SUM(load_shape_normalized_fraction) as total_fraction
  FROM openbca_core.all_commodity_load_shape_ts
  GROUP BY commodity, load_shape
)

-- Return measures where energy savings ≠ 1.0 and the sum of the corresponding load shape time series also ≠ 1.0
SELECT
  ms.measure_id,
  ms.commodity,
  ms.load_shape_mapping,
  ms.energy_savings,
  ls.total_fraction,
  'Warning: Project savings ≠ 1.0 and load shape sum ≠ 1.0' as validation_message
FROM measure_savings ms
JOIN load_shape_sums ls
  ON ms.commodity = ls.commodity
  AND ms.load_shape_mapping = ls.load_shape
WHERE ABS(ms.energy_savings - 1.0) > 0.0001  -- Energy savings not equal to 1.0 (with small tolerance)
  AND ABS(ls.total_fraction - 1.0) > 0.0001  -- Load shape sum not equal to 1.0 (with small tolerance)