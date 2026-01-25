MODEL(
    name core_layer0_base.program_value_streams,
    kind VIEW,
    grain (program_name, program_year),
);

SELECT
    program_name::VARCHAR AS program_name,
    program_year::INTEGER AS program_year,
    avoided_cost::VARCHAR AS avoided_cost,
    avoided_cost_value::FLOAT AS avoided_cost_value,
FROM 
    openbca_input.program_value_streams