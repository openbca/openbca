MODEL(
  name core_validations.load_shape_v,
  kind FULL,
);

WITH measure_electric_load_shapes AS (
    SELECT
        DISTINCT electric_savings_load_shape AS load_shape
    FROM
        openbca_input.measures
)

, measure_natural_gas_load_shapes AS (
    SELECT
        DISTINCT natural_gas_savings_load_shape AS load_shape
    FROM
        openbca_input.measures
)

, load_shape_electric_load_shapes AS (
    SELECT
        DISTINCT load_shape
    FROM  
        openbca_input.load_shapes_ts  
    WHERE
        UPPER(commodity) = 'ELECTRIC'
)

, load_shape_natural_gas_load_shapes AS (
    SELECT
        DISTINCT load_shape
    FROM  
        openbca_input.load_shapes_ts  
    WHERE
        UPPER(commodity) = 'NATURAL GAS'
)

SELECT 
    DISTINCT
    'ELECTRIC' AS commodity
    , load_shape
FROM 
    measure_electric_load_shapes
WHERE 
    load_shape NOT IN (SELECT load_shape FROM load_shape_electric_load_shapes)

UNION ALL

SELECT 
    DISTINCT 
    'NATURAL GAS' AS commodity
    , load_shape
FROM 
    measure_natural_gas_load_shapes
WHERE 
    load_shape NOT IN (SELECT load_shape FROM load_shape_natural_gas_load_shapes)