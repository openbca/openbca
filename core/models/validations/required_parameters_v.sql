MODEL(
  name core_validations.required_parameters_v,
  kind FULL,
);

SELECT
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) AS count_null_id
    , SUM(CASE WHEN ntg IS NULL THEN 1 ELSE 0 END) AS count_null_ntg
    , SUM(CASE WHEN estimated_useful_life IS NULL THEN 1 ELSE 0 END) AS count_null_estimated_useful_life
    , SUM(CASE WHEN unit_quantity IS NULL THEN 1 ELSE 0 END) AS count_null_unit_quantity
    , SUM(CASE WHEN start_year IS NULL THEN 1 ELSE 0 END) AS count_null_start_year
    , SUM(CASE WHEN start_quarter IS NULL THEN 1 ELSE 0 END) AS count_null_start_quarter
    , SUM(CASE WHEN COALESCE(m.discount_rate, gp.discount_rate) IS NULL THEN 1 ELSE 0 END) AS count_null_discount_rate
FROM
    openbca_input.measures m, openbca_input.global_parameters gp