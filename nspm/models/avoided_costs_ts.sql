MODEL (
    name openbca_input.avoided_costs_ts,
    kind FULL,
    grain (
        year,
        month,
        day,
        type_of_day,
        period,
        hour_of_day,
        hour_of_year,
        default_inputs,
        source_sheet
    )
);

SELECT
    CAST(year AS INT) AS year,
    CAST(month AS INT) AS month,
    CAST(day AS INT) AS day,
    CAST(type_of_day AS STRING) AS type_of_day,
    CAST(period AS STRING) AS period,
    CAST(hour_of_day AS INT) AS hour_of_day,
    CAST(hour_of_year AS INT) AS hour_of_year,
    CAST(default_inputs AS FLOAT) AS default_inputs,
    source_sheet
FROM nspm.openbca_input_avoided_costs_ts
