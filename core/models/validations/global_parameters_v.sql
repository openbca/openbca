MODEL(
  name core_validations.global_parameters_v,
  kind FULL,
);

SELECT
    SUM(CASE WHEN inflation_rate IS NULL THEN 1 ELSE 0 END) AS count_null_inflation_rate
    , SUM(CASE WHEN dollar_year IS NULL THEN 1 ELSE 0 END) AS count_null_dollar_year
    , SUM(CASE WHEN discount_cadence IS NULL THEN 1 ELSE 0 END) AS count_null_discount_cadence
    , SUM(CASE WHEN electric_line_loss IS NULL THEN 1 ELSE 0 END) AS count_null_electric_line_loss
    , SUM(CASE WHEN natural_gas_line_loss IS NULL THEN 1 ELSE 0 END) AS count_null_natural_gas_line_loss
    , SUM(CASE WHEN cost_treatment IS NULL THEN 1 ELSE 0 END) AS count_null_cost_treatment
FROM
    openbca_input.global_parameters