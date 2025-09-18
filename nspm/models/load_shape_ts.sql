MODEL (
    name openbca_input.load_shape_ts,
    kind FULL,
    grain (
        commodity
        year,
        quarter,
        month,
        day,
        hour_of_year
        load_shape,
        value

    )
);

SELECT
    CAST(commodity AS STRING) AS commodity,
    CAST(year AS INT) AS year,
    CAST(quarter AS INT) AS quarter,
    CAST(month AS INT) AS month,
    CAST(day AS INT) AS hour_of_day,
    CAST(hour_of_year AS INT) AS hour_of_year,
    CAST(load_shape AS STRING) AS load_shape,
    CAST(value AS FLOAT) AS load_shape_normalized_fraction
FROM nspm.openbca_input_load_shapes_ts

