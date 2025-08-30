AUDIT (
  name load_shape_mapping_validation_audit,
  description 'This audit checks that load shape mappings in measures exist in the available load shapes.',
);

WITH
measure_load_shapes AS (
  -- Get all load shape mappings from measures
  SELECT DISTINCT
    measure_id,
    'ELECTRICITY' as commodity,
    upper(elec_load_shape_mapping) as load_shape_mapping
  FROM openbca_input.measures
  WHERE elec_load_shape_mapping IS NOT NULL
  UNION ALL
  SELECT DISTINCT
    measure_id,
    'GAS' as commodity,
    upper(gas_load_shape_mapping) as load_shape_mapping
  FROM openbca_input.measures
  WHERE gas_load_shape_mapping IS NOT NULL
),
available_load_shapes AS (
  -- Get all available load shapes from both reference and input sources
  SELECT DISTINCT
    commodity,
    load_shape
  FROM openbca_core.all_commodity_load_shape_ts
)
-- Return measures with load shape mappings that don't exist in available load shapes
SELECT
  measure_id,
  commodity,
  load_shape_mapping,
  'Load shape mapping does not exist in available load shapes' as validation_message
FROM measure_load_shapes
WHERE NOT EXISTS (
  SELECT 1
  FROM available_load_shapes
  WHERE available_load_shapes.commodity = measure_load_shapes.commodity
    AND available_load_shapes.load_shape = measure_load_shapes.load_shape_mapping
)