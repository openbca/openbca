MODEL(
    name core_layer0_base.program_value_streams,
    kind VIEW,
    grain (program_name, program_year),
);

SELECT
    program_name::VARCHAR AS program_name,
    program_year::INTEGER AS program_year,
    program_admin_costs_dollar_per_year::FLOAT AS program_admin_costs_dollar_per_year,
    program_incentive_utility_to_customer_dollar_per_year::FLOAT AS program_incentive_utility_to_customer_dollar_per_year,
    program_performance_incentive_govt_to_utility_dollar_per_year::FLOAT AS program_performance_incentive_govt_to_utility_dollar_per_year,
    program_federal_incentive_dollar_per_year::FLOAT AS program_federal_incentive_dollar_per_year
FROM 
    openbca_input.program_value_streams