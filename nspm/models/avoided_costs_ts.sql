MODEL (
    name openbca_input.avoided_costs_ts,
    kind FULL,
    grain (
        commodity,
        avaoided_cost,
        avoided_cost_subset
        year,
        month,
        day,
        type_of_day,
        period,
        hour_of_day,
        hour_of_year,
        value
    )
);

SELECT
    CAST(commodity AS STRING) AS commodity,
    CAST(avoided_cost AS STRING) AS avoided_cost,
    CAST(avoided_cost_subset AS STRING) AS avoided_cost_subset,
    CAST(year AS INT) AS year,
    CAST(month AS INT) AS month,
    CAST(day AS INT) AS day,
    CAST(type_of_day AS STRING) AS type_of_day,
    CAST(period AS STRING) AS period,
    CAST(hour_of_day AS INT) AS hour_of_day,
    CAST(hour_of_year AS INT) AS hour_of_year,
    CAST(value AS FLOAT) AS av_cost_dollar_per_energy_unit
FROM nspm.openbca_input_avoided_costs_ts
