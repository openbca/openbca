MODEL(
    name core_layer0_base.first_year_avoided_costs_by_id,
    kind VIEW,
);

SELECT
    id::VARCHAR AS id,
    year::INT AS year,
    value_stream::VARCHAR AS value_stream,
    gross_dollar_value::FLOAT AS gross_dollar_value,
FROM 
    openbca_input.first_year_avoided_costs_by_id