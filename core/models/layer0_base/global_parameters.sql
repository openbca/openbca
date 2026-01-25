MODEL(
    name core_layer0_base.global_parameters,
    kind VIEW,
);

SELECT
    --real_or_nominal_inputs::VARCHAR AS real_or_nominal_inputs,
    inflation_rate::FLOAT AS inflation_rate,
    dollar_year::INT AS dollar_year,
    discount_rate::FLOAT AS discount_rate,
    discount_cadence::INT AS discount_cadence,
    electric_line_loss::FLOAT AS electric_line_loss,
    natural_gas_line_loss::FLOAT AS natural_gas_line_loss,
    cost_treatment::VARCHAR AS cost_treatment,
FROM 
    openbca_input.global_parameters