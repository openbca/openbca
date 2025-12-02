MODEL(
    name core_layer0_base.global_parameters,
    kind VIEW,
);

SELECT
    discount_rate::FLOAT AS discount_rate,
    electric_line_loss::FLOAT AS electric_line_loss,
    natural_gas_line_loss::FLOAT AS natural_gas_line_loss,
    cost_treatment::VARCHAR AS cost_treatment,
FROM openbca_input.global_parameters
