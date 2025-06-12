MODEL(
    name openbca_input.avoided_costs_ts,
    kind FULL,
    grain (utility, region, commodity, avoided_cost, year, hour_of_year),
);

-- IMPORTANT NOTE: The time-granularity of the avoided_costs_ts table cannot be lower than the time-granularity of the commodity_load_shape_ts table.
-- For instance, if the commodity_load_shape_ts table is monthly then the avoided_costs_ts table cannot be hourly.

SELECT
    CAST(NULL AS STRING) AS utility,
    CAST(NULL AS STRING) AS region,
    CAST(NULL AS STRING) AS commodity,
    CAST(NULL AS INTEGER) AS year,
    CAST(NULL AS INTEGER) AS quarter,
    CAST(NULL AS INTEGER) AS month,
    CAST(NULL AS INTEGER) AS hour_of_year,
    CAST(NULL AS INTEGER) AS hour_of_day,
    CAST(NULL AS STRING) AS avoided_cost,
    CAST(NULL AS FLOAT) AS value
WHERE 1 = 0
