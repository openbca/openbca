MODEL(
  name core_validations.load_shape_normalization_v,
  kind FULL,
);

WITH normalized_load_shapes AS (
  SELECT 
  lsts.impact_category
  , lsts.load_shape
  , SUM(lsts.load_shape_value) AS sum_load_shape_value
  FROM openbca_input.load_shapes_ts lsts
  JOIN openbca_input.load_shape_normalization n ON 
  lsts.impact_category = n.impact_category 
  AND 
  lsts.load_shape = n.load_shape
  WHERE 
  n.normalized
  AND lsts.load_shape IN (
  SELECT DISTINCT electric_savings_load_shape FROM openbca_input.measures WHERE electric_savings_load_shape IS NOT NULL  
  UNION ALL 
  SELECT DISTINCT natural_gas_savings_load_shape FROM openbca_input.measures WHERE natural_gas_savings_load_shape IS NOT NULL
  )
  GROUP BY 
  lsts.impact_category
  , lsts.load_shape
  )

  SELECT
  *
  , CASE WHEN ABS(sum_load_shape_value) BETWEEN 0.999 and 1.001 THEN 'PASS' ELSE 'FAIL' END AS passed_normalization_test
  FROM 
  normalized_load_shapes