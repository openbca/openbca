MODEL(
    name openbca_input.commodity_load_shape_ts,
    kind FULL,
    grain (commodity, load_shape, hour_of_year),
);
-- TODO replace with the actual source table
SELECT
    CAST(NULL AS STRING) AS commodity,
    CAST(NULL AS INTEGER) AS quarter,
    CAST(NULL AS INTEGER) AS month,
    CAST(NULL AS INTEGER) AS hour_of_year,
    CAST(NULL AS INTEGER) AS hour_of_day,
    CAST(NULL AS STRING) AS load_shape,
    CAST(NULL AS FLOAT) AS value
WHERE 1 = 0
