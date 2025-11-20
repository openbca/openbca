MODEL (
    name openbca_input.global_parameters,
    kind FULL,
);

SELECT
    discount_rate::FLOAT AS discount_rate,
    electric_line_loss::FLOAT AS electric_line_loss,
    natural_gas_line_loss::FLOAT AS natural_gas_line_loss,
    cost_treatment::VARCHAR AS cost_treatment,

FROM nspm.openbca_input_global_parameters